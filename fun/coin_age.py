#!/usr/bin/env python3
"""
Fetch the most recent block (verbosity=3) and compute the age of every
input coin from vin.prevout.height, which is embedded in the block undo data.

No txindex required. Two RPC calls total: getbestblockhash + getblock.

Caveat: verbosity=3 prevout data is only available for unpruned blocks on the
active chain. The tip block always qualifies.

Usage:
    python3 coin_age.py [--cli "bitcoin-cli -regtest"] [--block <hash|height>]

Output (written to fun/):
    coin_age_<height>.json          full per-input records + metadata
    coin_age_<height>.csv           same as CSV for pandas / spreadsheets
    coin_age_<height>_summary.txt   human-readable stats + distribution
"""

import argparse
import csv
import json
import os
import statistics
import subprocess
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# RPC helpers
# ---------------------------------------------------------------------------

def cli(*args):
    cmd = CLI_ARGS + [str(a) for a in args]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()


def cli_json(*args):
    return json.loads(cli(*args))


# ---------------------------------------------------------------------------
# Block resolution
# ---------------------------------------------------------------------------

def fetch_block(spec):
    """Return getblock verbosity=3 result for a hash, height, or None (tip)."""
    if spec is None or spec == "best":
        h = cli("getbestblockhash")
    elif spec.lstrip("-").isdigit():
        h = cli("getblockhash", spec)
    else:
        h = spec
    return cli_json("getblock", h, 3)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze(block):
    tip_height = block["height"]
    tip_time   = block["time"]

    rows = []
    no_prevout = []   # inputs where undo data was absent (pruned / same-block edge cases)

    for tx in block["tx"]:
        txid = tx["txid"]

        if "coinbase" in tx["vin"][0]:
            continue

        for vin_idx, vin in enumerate(tx["vin"]):
            input_txid = vin["txid"]
            input_vout = vin["vout"]

            prevout = vin.get("prevout")
            if prevout is None:
                # Undo data unavailable (shouldn't happen at tip on non-pruned node)
                no_prevout.append(f"{input_txid}:{input_vout}")
                rows.append({
                    "spending_txid":  txid,
                    "vin_index":      vin_idx,
                    "input_txid":     input_txid,
                    "input_vout":     input_vout,
                    "value_btc":      None,
                    "generated":      None,
                    "created_height": None,
                    "tip_height":     tip_height,
                    "age_blocks":     None,
                    "age_days":       None,
                    "note":           "no-prevout-data",
                })
                continue

            created_height = prevout["height"]
            value_btc      = prevout["value"]
            generated      = prevout["generated"]   # True if spending a coinbase output

            age_blocks = tip_height - created_height
            # Block timestamps aren't perfectly 10 min apart; use tip_time as rough upper bound
            # For precise day count we'd need the creating block's timestamp, but that would
            # require getblockheader — one call per input. Use blocks / 144 as an approximation.
            age_days = round(age_blocks / 144, 4)

            note = "same-block" if age_blocks == 0 else ("coinbase-output" if generated else "")

            rows.append({
                "spending_txid":  txid,
                "vin_index":      vin_idx,
                "input_txid":     input_txid,
                "input_vout":     input_vout,
                "value_btc":      value_btc,
                "generated":      generated,
                "created_height": created_height,
                "tip_height":     tip_height,
                "age_blocks":     age_blocks,
                "age_days":       age_days,
                "note":           note,
            })

    meta = {
        "block_hash":       block["hash"],
        "block_height":     tip_height,
        "block_time_utc":   datetime.fromtimestamp(tip_time, tz=timezone.utc).isoformat(),
        "total_txs":        len(block["tx"]),
        "inputs_analyzed":  len(rows),
        "missing_prevout":  no_prevout,
    }

    return rows, meta


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def summarize(meta, rows):
    valid  = [r for r in rows if r["age_blocks"] is not None]
    ages   = [r["age_blocks"] for r in valid]
    values = [r["value_btc"]  for r in valid if r["value_btc"] is not None]

    lines = [
        "=" * 62,
        f"Block:           {meta['block_height']}  ({meta['block_hash'][:16]}…)",
        f"Time (UTC):      {meta['block_time_utc']}",
        f"Transactions:    {meta['total_txs']}  (coinbase excluded from inputs)",
        f"Inputs analyzed: {meta['inputs_analyzed']}",
        f"Missing prevout: {len(meta['missing_prevout'])}",
        "=" * 62,
        "",
    ]

    if not ages:
        lines.append("No age data to summarize.")
        return "\n".join(lines)

    lines += [
        "Coin age (blocks):",
        f"  min:     {min(ages):>12,}",
        f"  median:  {statistics.median(ages):>12,.1f}",
        f"  mean:    {statistics.mean(ages):>12,.1f}",
        f"  max:     {max(ages):>12,}",
    ]
    if len(ages) > 1:
        lines.append(f"  stdev:   {statistics.stdev(ages):>12,.1f}")
    lines.append("")

    buckets = [
        ("same block (0 blocks)",     lambda a: a == 0),
        ("< 1 day  (< 144 blk)",      lambda a: 0 < a < 144),
        ("1 day – 1 week",            lambda a: 144  <= a < 1_008),
        ("1 week – 1 month",          lambda a: 1_008 <= a < 4_320),
        ("1 month – 6 months",        lambda a: 4_320 <= a < 25_920),
        ("6 months – 1 year",         lambda a: 25_920 <= a < 52_560),
        ("> 1 year",                  lambda a: a >= 52_560),
    ]
    lines.append("Distribution:")
    for label, fn in buckets:
        count = sum(1 for a in ages if fn(a))
        pct   = 100 * count / len(ages) if ages else 0
        bar   = "#" * int(pct / 2)
        lines.append(f"  {label:<30} {count:>5}  ({pct:5.1f}%)  {bar}")

    if values:
        lines += [
            "",
            f"Total input value:  {sum(values):.8f} BTC  ({len(values)} inputs)",
            f"  smallest input:   {min(values):.8f} BTC",
            f"  largest input:    {max(values):.8f} BTC",
        ]

    coinbase_spends = sum(1 for r in valid if r.get("generated"))
    if coinbase_spends:
        lines.append(f"\nInputs spending coinbase outputs: {coinbase_spends}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cli",   default="bitcoin-cli",
                   help="bitcoin-cli invocation, e.g. 'bitcoin-cli -regtest'")
    p.add_argument("--block", default=None,
                   help="block hash, height, or 'best' (default: best/tip)")
    args = p.parse_args()

    CLI_ARGS = args.cli.split()

    print("Fetching block (verbosity=3)…")
    block = fetch_block(args.block)
    print(f"  height {block['height']}  {block['hash'][:16]}…  ({len(block['tx'])} txs)")

    print("Analyzing inputs…")
    rows, meta = analyze(block)
    print(f"  {meta['inputs_analyzed']} inputs  |  {len(meta['missing_prevout'])} missing prevout")

    base    = os.path.join(SCRIPT_DIR, f"coin_age_{block['height']}")
    j_path  = base + ".json"
    c_path  = base + ".csv"
    s_path  = base + "_summary.txt"

    with open(j_path, "w") as f:
        json.dump({"meta": meta, "inputs": rows}, f, indent=2)

    if rows:
        with open(c_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)

    summary = summarize(meta, rows)
    with open(s_path, "w") as f:
        f.write(summary + "\n")

    print()
    print(summary)
    print(f"\nJSON:    {j_path}")
    print(f"CSV:     {c_path}")
    print(f"Summary: {s_path}")
