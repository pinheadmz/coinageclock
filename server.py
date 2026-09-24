#!/usr/bin/env python3
"""
Live Bitcoin mempool coin-age dashboard server.

Reads ~/.bitcoin/.cookie for RPC auth.
Connects to Bitcoin Core RPC on 127.0.0.1:8332.
Subscribes to ZMQ hashblock + hashtx on tcp://127.0.0.1:21000.
Serves the coin-age clock at http://0.0.0.0:8080.
"""

import asyncio
import base64
import hashlib
import io
import logging
import pathlib
import struct
from dataclasses import dataclass, field

import aiohttp
from aiohttp import web
import zmq
import zmq.asyncio

log = logging.getLogger("mempool")

# ── Cookie auth ──────────────────────────────────────────────────────────────

def read_cookie(path="~/.bitcoin/.cookie") -> dict:
    """Return an Authorization header dict for Bitcoin Core cookie auth."""
    p = pathlib.Path(path).expanduser()
    encoded = base64.b64encode(p.read_text().strip().encode()).decode()
    return {"Authorization": f"Basic {encoded}"}

# ── Bitcoin RPC client ───────────────────────────────────────────────────────

class BitcoinRPC:
    def __init__(self, session: aiohttp.ClientSession, auth_headers: dict,
                 url: str = "http://127.0.0.1:8332/"):
        self._session = session
        self._auth_headers = auth_headers
        self._url = url
        self._id = 0

    async def call(self, method: str, params: list = None):
        self._id += 1
        payload = {"jsonrpc": "2.0", "id": self._id,
                   "method": method, "params": params or []}
        async with self._session.post(self._url, json=payload,
                                      headers=self._auth_headers) as resp:
            data = await resp.json(content_type=None)
        if data.get("error"):
            raise RuntimeError(f"RPC {method}: {data['error']}")
        return data["result"]

    async def getblockcount(self) -> int:
        return await self.call("getblockcount")

    async def getrawmempool(self, verbose: bool = False):
        return await self.call("getrawmempool", [verbose])

    async def getrawtransaction(self, txid: str):
        return await self.call("getrawtransaction", [txid, True])

    async def gettxout(self, txid: str, vout: int, include_mempool: bool = True):
        return await self.call("gettxout", [txid, vout, include_mempool])

    async def getblockhash(self, height: int) -> str:
        return await self.call("getblockhash", [height])

    async def getblock(self, blockhash: str, verbosity: int = 1):
        return await self.call("getblock", [blockhash, verbosity])

# ── Coin-age bucketing ───────────────────────────────────────────────────────

ALL_BUCKETS = (
    ["mempool"]
    + [str(i) for i in range(1, 11)]
    + ["10_20", "20_50", "50_100", "100_1000", "1000_plus"]
)

def age_to_bucket(confs: int) -> str:
    if confs <= 10:    return str(confs)
    if confs <= 20:    return "10_20"
    if confs <= 50:    return "20_50"
    if confs <= 100:   return "50_100"
    if confs <= 1000:  return "100_1000"
    return "1000_plus"

# ── Mempool state ────────────────────────────────────────────────────────────

def _empty_buckets():
    return {k: {"inputs": 0, "btc": 0.0, "txs": 0} for k in ALL_BUCKETS}

@dataclass
class MempoolState:
    tip_height:  int  = 0
    scanning:    bool = True
    scan_done:   int  = 0
    scan_total:  int  = 0
    generation:       int  = 0    # bumped on every block; lets in-progress scans self-cancel
    known_txids:      set  = field(default_factory=set)
    tx_inputs:        dict = field(default_factory=dict)
    buckets:          dict = field(default_factory=_empty_buckets)
    # Per-block input-age histograms: {age_int: {bucket: count}}
    # age 1 = tip block, age 2 = tip-1, … age 10 = tip-9
    block_histograms: dict = field(default_factory=dict)

    def reset(self):
        """Full wipe — used only on startup if needed."""
        self.known_txids.clear()
        self.tx_inputs.clear()
        self.buckets    = _empty_buckets()
        self.scanning   = True
        self.scan_done  = 0
        self.scan_total = 0
        self.generation += 1

    # ── tx_inputs stores (confs: int, btc: float) per input ──────────────────
    # confs = 0   → unconfirmed parent (mempool spend)
    # confs > 0   → confirmed UTXO, age in blocks

    def _bucket(self, confs: int) -> str:
        return "mempool" if confs == 0 else age_to_bucket(confs)

    def add_tx(self, txid: str, inputs: list) -> bool:
        """inputs: [(confs, btc), …]. Returns True if newly added."""
        if txid in self.tx_inputs:
            return False
        self.known_txids.add(txid)
        self.tx_inputs[txid] = inputs
        tx_counted = False
        for confs, btc in inputs:
            b = self.buckets[self._bucket(confs)]
            b["inputs"] += 1
            b["btc"]    += btc
            if not tx_counted:
                b["txs"] += 1
                tx_counted = True
        return True

    def remove_tx(self, txid: str):
        self.known_txids.discard(txid)
        inputs = self.tx_inputs.pop(txid, None)
        if not inputs:
            return
        tx_counted = False
        for confs, btc in inputs:
            b = self.buckets[self._bucket(confs)]
            b["inputs"] = max(0, b["inputs"] - 1)
            b["btc"]    = max(0.0, b["btc"] - btc)
            if not tx_counted:
                b["txs"] = max(0, b["txs"] - 1)
                tx_counted = True

    def shift_block(self, confirmed: set):
        """
        Efficiently handle a new block without rescanning the entire mempool.

        1. Remove confirmed txids (≈1-2k on mainnet).
        2. For every surviving tx, increment each input's confs by 1.
           Coins cross age-bucket boundaries (e.g. confs 10→11 moves "10"→"10_20")
           correctly because we store exact confirmation counts rather than buckets.
        3. Rebuild the bucket totals in a single O(surviving_inputs) pass.
        """
        for txid in confirmed:
            self.remove_tx(txid)

        # Shift all surviving inputs +1 block and recompute buckets in one pass
        surviving     = self.tx_inputs
        self.tx_inputs = {}
        self.buckets   = _empty_buckets()
        self.known_txids.clear()

        for txid, inputs in surviving.items():
            new_inputs  = []
            tx_counted  = False
            for confs, btc in inputs:
                new_confs = confs + 1 if confs > 0 else 0  # mempool parents stay 0
                new_inputs.append((new_confs, btc))
                b = self.buckets[self._bucket(new_confs)]
                b["inputs"] += 1
                b["btc"]    += btc
                if not tx_counted:
                    b["txs"] += 1
                    tx_counted = True
            self.tx_inputs[txid] = new_inputs
            self.known_txids.add(txid)

    def to_snapshot(self) -> dict:
        return {
            "type":             "state",
            "tip_height":       self.tip_height,
            "mempool_tx_count": len(self.known_txids),
            "scanning":         self.scanning,
            "scan_done":        self.scan_done,
            "scan_total":       self.scan_total,
            "buckets":          {k: dict(v) for k, v in self.buckets.items()},
            "block_histograms": {str(age): h for age, h in self.block_histograms.items()},
        }

    def shift_and_add_histogram(self, new_hist: dict):
        """On every confirmed block: shift ages 1→2, …, 9→10; age 1 = new block."""
        self.block_histograms = {
            age + 1: h for age, h in self.block_histograms.items() if age < 10
        }
        self.block_histograms[1] = new_hist

# ── Raw transaction parsing ───────────────────────────────────────────────────

def _varint(f: io.BytesIO) -> int:
    b = f.read(1)[0]
    if b < 0xfd: return b
    if b == 0xfd: return struct.unpack('<H', f.read(2))[0]
    if b == 0xfe: return struct.unpack('<I', f.read(4))[0]
    return struct.unpack('<Q', f.read(8))[0]

def _varint_bytes(n: int) -> bytes:
    if n < 0xfd: return bytes([n])
    if n < 0x10000: return b'\xfd' + struct.pack('<H', n)
    if n < 0x100000000: return b'\xfe' + struct.pack('<I', n)
    return b'\xff' + struct.pack('<Q', n)

def parse_raw_tx(raw: bytes):
    """
    Parse a raw Bitcoin transaction (segwit-aware).
    Returns (txid_hex, vin_list) where vin_list is [(prev_txid_hex, vout), ...].
    Coinbase inputs are represented as (None, None) and should be filtered out.
    """
    f = io.BytesIO(raw)
    version_b = f.read(4)

    # Segwit marker check
    marker = f.read(1)
    segwit = marker == b'\x00'
    if segwit:
        f.read(1)  # flag byte
    else:
        f.seek(-1, 1)  # put back non-marker byte

    # Inputs
    n_in = _varint(f)
    vin = []
    vin_serial = b''
    for _ in range(n_in):
        prev_hash = f.read(32)          # little-endian txid
        prev_idx  = f.read(4)
        slen      = _varint(f)
        script    = f.read(slen)
        seq       = f.read(4)
        vin_serial += prev_hash + prev_idx + _varint_bytes(slen) + script + seq

        if prev_hash == b'\x00' * 32:   # coinbase
            vin.append((None, None))
        else:
            vin.append((prev_hash[::-1].hex(), struct.unpack('<I', prev_idx)[0]))

    # Outputs
    n_out = _varint(f)
    out_serial = b''
    for _ in range(n_out):
        value  = f.read(8)
        slen   = _varint(f)
        script = f.read(slen)
        out_serial += value + _varint_bytes(slen) + script

    # Skip witness data (segwit only) — not included in txid hash
    if segwit:
        for _ in range(n_in):
            stack_items = _varint(f)
            for _ in range(stack_items):
                item_len = _varint(f)
                f.read(item_len)

    locktime_b = f.read(4)

    # txid = double-SHA256 of the non-witness serialisation
    nowitness = (version_b +
                 _varint_bytes(n_in) + vin_serial +
                 _varint_bytes(n_out) + out_serial +
                 locktime_b)
    txid = hashlib.sha256(hashlib.sha256(nowitness).digest()).digest()[::-1].hex()

    return txid, vin

# ── UTXO age lookup (shared by initial scan and live ZMQ path) ────────────────

async def classify_vin(vin: list, rpc: BitcoinRPC,
                       state: MempoolState) -> list:
    """
    Returns [(confs, btc), …] — stores exact confirmation counts, not bucket strings.
    confs=0 means the parent UTXO is itself unconfirmed (CPFP / mempool-to-mempool).
    Storing exact confs lets shift_block() correctly move coins across bucket
    boundaries (e.g. confs 10→11 crosses from "10" into "10_20") without re-fetching.
    """
    inputs = []
    for in_txid, in_vout in vin:
        if in_txid is None:
            continue

        # Pass 1: confirmed UTXO
        try:
            utxo = await rpc.gettxout(in_txid, in_vout, include_mempool=False)
        except Exception as exc:
            log.debug("gettxout %s:%d: %s", in_txid[:16], in_vout, exc)
            utxo = None

        if utxo is not None:
            inputs.append((utxo.get("confirmations", 1), utxo.get("value", 0.0)))
            continue

        # Pass 2: CPFP — parent is in the mempool
        if in_txid in state.known_txids:
            try:
                utxo = await rpc.gettxout(in_txid, in_vout, include_mempool=True)
            except Exception:
                utxo = None
            inputs.append((0, utxo.get("value", 0.0) if utxo else 0.0))
        else:
            log.debug("UTXO not found %s:%d", in_txid[:16], in_vout)

    return inputs

async def classify_tx(txid: str, rpc: BitcoinRPC,
                      state: MempoolState) -> list:
    """Fetch tx via RPC then classify its inputs. Used by the initial scan."""
    try:
        tx = await rpc.getrawtransaction(txid)
    except Exception as exc:
        # Tx may have been confirmed while the slow initial scan was still running.
        log.debug("getrawtransaction %s: %s", txid[:16], exc)
        return []
    vin = [(v["txid"], v["vout"]) if "txid" in v else (None, None)
           for v in tx.get("vin", [])]
    return await classify_vin(vin, rpc, state)

# ── Block histogram computation ──────────────────────────────────────────────

def compute_block_histogram(block: dict) -> dict:
    """
    Compute input-age histogram for a verbosity=3 block dict.
    Uses prevout.height from the block undo data — no txindex required.
    age = block_height - prevout.height; age 0 → "mempool" (same-block spend).
    """
    H = block["height"]
    histogram: dict = {}
    for tx in block.get("tx", []):
        for vin in tx.get("vin", []):
            if "coinbase" in vin:
                continue
            prevout = vin.get("prevout")
            if prevout is None:
                continue          # undo data absent (pruned)
            age = H - prevout["height"]
            bucket = "mempool" if age == 0 else age_to_bucket(age)
            histogram[bucket] = histogram.get(bucket, 0) + 1
    return histogram


async def precompute_block_histograms(rpc: BitcoinRPC, state: MempoolState):
    """
    Fetch and compute input-age histograms for the last 10 confirmed blocks
    so the histogram display is populated immediately on page load.
    """
    log.info("Pre-computing block histograms (verbosity=3)…")
    for age in range(1, 11):
        block_height = state.tip_height - age + 1
        try:
            blockhash = await rpc.getblockhash(block_height)
            block     = await rpc.getblock(blockhash, 3)
            hist      = compute_block_histogram(block)
            state.block_histograms[age] = hist
            log.info("  #%d (age %d): %d inputs", block_height, age,
                     sum(hist.values()))
        except Exception as exc:
            log.warning("  #%d (age %d): %s", block_height, age, exc)
    log.info("Block histogram pre-computation done.")


# ── Initial mempool scan ──────────────────────────────────────────────────────

async def initial_scan(rpc: BitcoinRPC, state: MempoolState, broadcast_fn):
    gen = state.generation   # snapshot — if this changes, a new block arrived
    log.info("Starting mempool scan (generation %d)…", gen)
    try:
        raw = await rpc.getrawmempool(verbose=True)
    except Exception as exc:
        log.error("getrawmempool failed: %s", exc)
        state.scanning = False
        await broadcast_fn()
        return

    if state.generation != gen:
        log.info("Scan %d superseded before it started", gen)
        return

    # Register all txids first so mempool-spend detection works from the start.
    state.known_txids = set(raw)
    state.scan_total  = len(raw)
    log.info("Mempool contains %d transactions", state.scan_total)

    # Topological order: process txs with no unconfirmed parents first.
    no_deps  = [t for t, v in raw.items() if not v.get("depends")]
    has_deps = [t for t, v in raw.items() if     v.get("depends")]
    ordered  = no_deps + has_deps

    BATCH = 20
    for i, txid in enumerate(ordered):
        if state.generation != gen:
            log.info("Scan %d cancelled at %d/%d", gen, i, state.scan_total)
            return
        # Skip txids already in tx_inputs (processed by ZMQ or shift_block already ran)
        if txid in state.tx_inputs:
            state.scan_done = i + 1
            continue
        # Skip txids removed by shift_block (confirmed in a block mid-scan)
        if txid not in state.known_txids:
            state.scan_done = i + 1
            continue
        inputs = await classify_tx(txid, rpc, state)
        state.add_tx(txid, inputs)
        state.scan_done = i + 1
        if (i + 1) % BATCH == 0:
            await broadcast_fn()
            await asyncio.sleep(0)

    if state.generation != gen:
        log.info("Scan %d cancelled at completion", gen)
        return

    state.scanning  = False
    state.scan_done = state.scan_total
    await broadcast_fn()
    log.info("Scan %d complete.", gen)

# ── ZMQ listener ──────────────────────────────────────────────────────────────

async def _handle_new_tx(txid: str, vin_or_none, rpc: BitcoinRPC,
                         state: MempoolState):
    """
    Classify and broadcast a new mempool tx.
    vin_or_none: pre-parsed vin list (from rawtx) or None (fetch via RPC for hashtx).
    Returns True if a new tx was added and broadcast.
    """
    # tx_inputs (not known_txids) for dedup: known_txids is pre-loaded by the
    # initial scan, so buffered ZMQ events for existing txs would all be skipped.
    # tx_inputs only contains txids we have actually classified.
    if txid in state.tx_inputs:
        return False

    if vin_or_none is not None:
        inputs = await classify_vin(vin_or_none, rpc, state)
    else:
        inputs = await classify_tx(txid, rpc, state)   # fetches via getrawtransaction

    if not state.add_tx(txid, inputs):
        return False  # scan beat us to it

    log.debug("+tx  total=%d  inputs=%d  buckets=%s",
             len(state.known_txids), len(inputs),
             sorted({"mempool" if c == 0 else age_to_bucket(c) for c, _ in inputs})
             or ["coinbase"])
    await broadcast_tx(state, inputs)
    return True


async def zmq_listener(state: MempoolState, rpc: BitcoinRPC,
                       zmq_url: str = "tcp://127.0.0.1:21001"):
    ctx  = zmq.asyncio.Context()
    sock = ctx.socket(zmq.SUB)
    sock.connect(zmq_url)
    # Subscribe to both variants — whichever the node is configured to publish.
    # rawtx  → full serialised tx bytes; we parse the vin inline (no extra RPC).
    # hashtx → just the 32-byte txid hash; we fetch the tx via getrawtransaction.
    sock.subscribe(b"rawtx")
    sock.subscribe(b"hashtx")
    sock.subscribe(b"hashblock")
    log.info("ZMQ connected to %s (topics: rawtx, hashtx, hashblock)", zmq_url)

    while True:
        parts = await sock.recv_multipart()
        topic = parts[0]
        body  = parts[1]

        if topic == b"rawtx":
            try:
                txid, vin = parse_raw_tx(body)
            except Exception as exc:
                log.warning("parse_raw_tx failed: %s", exc)
                continue
            await _handle_new_tx(txid, vin, rpc, state)

        elif topic == b"hashtx":
            # Body is the 32-byte txid in internal byte order — reverse for display.
            txid = body[::-1].hex()
            await _handle_new_tx(txid, None, rpc, state)

        elif topic == b"hashblock":
            # hashblock ZMQ sends the hash already in display (big-endian) byte
            # order — the notifier reverses bytes before publishing, unlike hashtx
            # which sends in internal (little-endian) order.
            blkhash = body.hex()
            log.info("New block: %s…", blkhash[:16])
            try:
                state.tip_height = await rpc.getblockcount()

                # Block histogram from undo data (verbosity=3)
                block    = await rpc.getblock(blkhash, 3)
                new_hist = compute_block_histogram(block)
                state.shift_and_add_histogram(new_hist)

                # Identify confirmed txids, then shift in-place — no rescan needed
                new_txids = set(await rpc.getrawmempool(verbose=False))
                confirmed = state.known_txids - new_txids
                state.shift_block(confirmed)
                log.info("Block %d: %d confirmed removed, %d surviving, "
                         "%d histogram inputs",
                         state.tip_height, len(confirmed),
                         len(state.tx_inputs), sum(new_hist.values()))
            except Exception as exc:
                log.error("block handler: %s", exc)

            await broadcast_block(state)

# ── WebSocket management ───────────────────────────────────────────────────────

_clients: set = set()

async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse(heartbeat=30)
    await ws.prepare(request)
    _clients.add(ws)
    log.info("WS client connected (%d total)", len(_clients))
    state: MempoolState = request.app["state"]
    try:
        await ws.send_json(state.to_snapshot())
        async for _ in ws:
            pass  # no client→server messages needed
    finally:
        _clients.discard(ws)
        log.info("WS client disconnected (%d total)", len(_clients))
    return ws

async def _send_all(msg: dict):
    if not _clients:
        return
    await asyncio.gather(
        *(ws.send_json(msg) for ws in list(_clients)),
        return_exceptions=True,
    )

async def broadcast_all(state: MempoolState):
    await _send_all(state.to_snapshot())

async def broadcast_tx(state: MempoolState, inputs: list):
    """Broadcast state + per-input wire hints (converts stored confs → bucket for client)."""
    msg = state.to_snapshot()
    msg["new_inputs"] = [
        {"bucket": "mempool" if c == 0 else age_to_bucket(c), "btc": btc}
        for c, btc in inputs
    ]
    await _send_all(msg)

async def broadcast_block(state: MempoolState):
    """Broadcast a state snapshot flagged as a block change (includes block_histograms)."""
    msg = state.to_snapshot()
    msg["block_change"] = True
    await _send_all(msg)

# ── Periodic heartbeat (catches clients that connect during quiet periods) ────

async def heartbeat_loop(app: web.Application):
    while True:
        await asyncio.sleep(2.0)
        if _clients:
            await broadcast_all(app["state"])

# ── App lifecycle ──────────────────────────────────────────────────────────────

async def on_startup(app: web.Application):
    auth_headers = read_cookie()
    # Persistent keep-alive connections to the local node — avoids TCP handshake
    # overhead on every RPC call (critical during the initial mempool scan).
    connector = aiohttp.TCPConnector(limit=8, keepalive_timeout=30.0)
    session   = aiohttp.ClientSession(connector=connector)
    rpc       = BitcoinRPC(session, auth_headers)
    state     = MempoolState()

    app["session"] = session
    app["rpc"]     = rpc
    app["state"]   = state

    state.tip_height = await rpc.getblockcount()
    log.info("Tip height: %d", state.tip_height)

    # Pre-compute histograms for the last 10 blocks before opening to connections
    await precompute_block_histograms(rpc, state)

    asyncio.create_task(zmq_listener(state, rpc))
    asyncio.create_task(heartbeat_loop(app))
    asyncio.create_task(initial_scan(rpc, state,
                                     lambda: broadcast_all(app["state"])))

async def on_cleanup(app: web.Application):
    if "session" in app:
        await app["session"].close()

# ── Routing + entry point ─────────────────────────────────────────────────────

def build_app() -> web.Application:
    app = web.Application()
    static_dir = pathlib.Path(__file__).parent / "static"
    app.router.add_get("/ws", ws_handler)
    app.router.add_get("/", lambda r: web.FileResponse(static_dir / "index.html"))
    app.router.add_static("/static", static_dir, show_index=False)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
    )
    web.run_app(build_app(), host="0.0.0.0", port=8080)
