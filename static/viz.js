/**
 * viz.js — Live Bitcoin mempool coin-age clock
 *
 * Wire drawing is strictly additive:
 *   • On initial connect or block change → clearLines() + drawLines() (representative sample)
 *   • On each new mempool tx  → addWires(new_inputs) appends paths, never repositions old ones
 *   • Labels update on every WebSocket message
 */

'use strict';

// ── Layout constants (match gen_viz.py) ──────────────────────────────────────

const SVG_W = 1320, SVG_H = 900;
const SVG_NS = 'http://www.w3.org/2000/svg';

// Top row: ages 1–10, age 10 leftmost
const BW = 84, BH = 90, TOP_CY = 78;
const TOP_L = 185, TOP_R = 1270;
const TOP_PIT = (TOP_R - TOP_L) / 9;
function topCx(age) { return TOP_L + (10 - age) * TOP_PIT; }

// Left column: 5 age-range blocks
const LC_W = 100, LC_H = 84, LC_CX = 62;
const LC_YS = [215, 320, 425, 530, 672];   // 1000+ pushed down; it's twice as tall
const RANGES      = ['10_20', '20_50', '50_100', '100_1000', '1000_plus'];
const RANGE_LABELS = ['10–20', '20–50', '50–100', '100–1000', '1000+'];

// Mempool block (bottom centre) — 50% bigger than the source blocks
const TW = 300, TH = 300;
const TIP_CX    = SVG_W / 2;
const TIP_CY    = 450;
const TIP_TOP   = TIP_CY - TH / 2;   // 357
const TIP_BOT   = TIP_CY + TH / 2;   // 543
const TIP_LEFT  = TIP_CX - TW / 2;   // 567
const TIP_RIGHT = TIP_CX + TW / 2;   // 753
const SRC_BOT   = TOP_CY + BH / 2;

// Non-mempool arc parameters (not currently used for same-mempool arcs below)
const ARC_MIN = 160, ARC_MAX = 280;
const ARC_V_SCALE = 0.55;

// Same-mempool (unconfirmed) arc parameters — sized so the furthest arc just
// reaches the counter label at x ≈ 1140  (TIP_RIGHT=753, 753+387=1140).
const MEMPOOL_ARC_MIN = 350, MEMPOOL_ARC_MAX = 1000;
const MEMPOOL_ARC_V_SCALE = 0.42;  // flat sweep: mostly rightward, little downward

// Max wires kept in the DOM at once (oldest trimmed when exceeded)
const MAX_WIRES = 800;

// Total lines drawn during initial / block-change representative sample.
// Distributed proportionally across buckets so the wire DENSITY matches the
// relative input counts (a bucket with 2× more inputs draws 2× more lines).
const DRAW_BUDGET = 600;

// ── Colour helpers ────────────────────────────────────────────────────────────

function ageHsl(age, l = 63) {
  return `hsl(${Math.round(((age - 1) / 9) * 220)},88%,${l}%)`;
}
const RANGE_HUES = {
  '10_20': 233, '20_50': 258, '50_100': 282, '100_1000': 308, '1000_plus': 333,
};
function rangeHsl(key, l = 62) { return `hsl(${RANGE_HUES[key]},78%,${l}%)`; }

const SAME_COL    = 'hsl(48,95%,65%)';
const MEMPOOL_COL = '#3b82f6';

// Wire appearance is uniform — the visualisation encodes input COUNT, not value.
// BTC totals are displayed as text labels but do not affect wire rendering.
function lineOpacity() { return 0.55; }
function lineWidth()   { return 1.0; }
function fmtBtc(v) {
  if (v >= 10000) return (v / 1000).toFixed(1) + 'k';
  if (v >= 1000)  return v.toFixed(0);
  if (v >= 1)     return v.toFixed(2);
  return v.toFixed(4);
}
function fmtNum(n) { return (n || 0).toLocaleString(); }

// ── SVG helpers ───────────────────────────────────────────────────────────────

function el(tag, attrs = {}, text = null) {
  const e = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text !== null) e.textContent = text;
  return e;
}
function txt(x, y, content, attrs = {}) {
  return el('text', { x, y, 'text-anchor': 'middle', 'font-family': 'monospace', ...attrs }, content);
}
function rand(lo, hi) { return lo + Math.random() * (hi - lo); }
function bezier(x1, y1, cx1, cy1, cx2, cy2, x2, y2) {
  return `M${x1},${y1} C${cx1},${cy1} ${cx2},${cy2} ${x2},${y2}`;
}

// ── Build static SVG structure ────────────────────────────────────────────────

function buildSVG() {
  const svg = el('svg', {
    viewBox: `0 0 ${SVG_W} ${SVG_H}`,
    id: 'clock-svg',
    style: 'background:#040a14;border-radius:14px;width:100%',
  });

  const defs = el('defs');
  defs.innerHTML = `
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>`;
  svg.appendChild(defs);

  const linesLayer  = el('g', { id: 'lines-layer' });
  const blocksLayer = el('g', { id: 'blocks-layer' });
  svg.appendChild(linesLayer);
  svg.appendChild(blocksLayer);

  // ── Top-row age blocks ──────────────────────────────────────────────────────
  for (let age = 1; age <= 10; age++) {
    const cx = topCx(age);
    const bx = cx - BW / 2, by = TOP_CY - BH / 2;
    const col = ageHsl(age);
    const g = el('g', { id: `blk-age-${age}` });
    g.appendChild(el('rect', { x: bx, y: by, width: BW, height: BH, rx: 6,
      fill: '#080f1c', stroke: col, 'stroke-width': 1.8 }));
    g.appendChild(txt(cx, by + 15, '…',
      { fill: col, 'font-size': 9.5, id: `lbl-age-${age}-height` }));
    g.appendChild(txt(cx, by + 27, `age ${age}`,
      { fill: col, 'font-size': 8.5 }));
    g.appendChild(txt(cx, by + 49, '0',
      { fill: '#f1f5f9', 'font-size': 15, 'font-weight': 'bold',
        id: `lbl-age-${age}-inputs` }));
    g.appendChild(txt(cx, by + 61, 'inputs',
      { fill: col, 'font-size': 7.5 }));
    g.appendChild(txt(cx, by + 76, '—',
      { fill: col, 'font-size': 9, id: `lbl-age-${age}-btc` }));
    blocksLayer.appendChild(g);
  }

  // ── Left-column range blocks ────────────────────────────────────────────────
  for (let i = 0; i < RANGES.length; i++) {
    const key    = RANGES[i], lcy = LC_YS[i];
    const tall   = (i === RANGES.length - 1);   // 1000+ block is twice as tall
    const blockH = tall ? LC_H * 2 : LC_H;
    const bx = LC_CX - LC_W / 2, by = lcy - blockH / 2;
    const col = rangeHsl(key);
    const g = el('g', { id: `blk-range-${key}` });
    g.appendChild(el('rect', { x: bx, y: by, width: LC_W, height: blockH, rx: 6,
      fill: '#080f1c', stroke: col, 'stroke-width': 1.8 }));
    if (tall) {
      // Spread text across the taller block
      g.appendChild(txt(LC_CX, by + 20, `age ${RANGE_LABELS[i]}`, { fill: col, 'font-size': 9 }));
      g.appendChild(txt(LC_CX, by + 32, 'blocks',                  { fill: col, 'font-size': 7.5 }));
      g.appendChild(txt(LC_CX, by + 76, '0',
        { fill: '#f1f5f9', 'font-size': 20, 'font-weight': 'bold', id: `lbl-range-${key}-inputs` }));
      g.appendChild(txt(LC_CX, by + 92,  'inputs', { fill: col, 'font-size': 7.5 }));
      g.appendChild(txt(LC_CX, by + 130, '—',
        { fill: col, 'font-size': 9, id: `lbl-range-${key}-btc` }));
    } else {
      g.appendChild(txt(LC_CX, by + 14, `age ${RANGE_LABELS[i]}`, { fill: col, 'font-size': 9 }));
      g.appendChild(txt(LC_CX, by + 25, 'blocks',                  { fill: col, 'font-size': 7.5 }));
      g.appendChild(txt(LC_CX, by + 46, '0',
        { fill: '#f1f5f9', 'font-size': 15, 'font-weight': 'bold', id: `lbl-range-${key}-inputs` }));
      g.appendChild(txt(LC_CX, by + 57, 'inputs', { fill: col, 'font-size': 7.5 }));
      g.appendChild(txt(LC_CX, by + 72, '—',
        { fill: col, 'font-size': 9, id: `lbl-range-${key}-btc` }));
    }
    blocksLayer.appendChild(g);
  }

  // ── Mempool block (bottom centre) ───────────────────────────────────────────
  {
    const g = el('g', { id: 'blk-mempool' });
    g.appendChild(el('rect', { x: TIP_LEFT, y: TIP_TOP, width: TW, height: TH,
      rx: 10, fill: '#060f22', stroke: MEMPOOL_COL, 'stroke-width': 3,
      filter: 'url(#glow)' }));
    // Distribute text evenly across the 186px-tall block
    g.appendChild(txt(TIP_CX, TIP_TOP + 26, 'MEMPOOL',
      { fill: MEMPOOL_COL, 'font-size': 21 }));
    g.appendChild(txt(TIP_CX, TIP_TOP + 48, '—',
      { fill: '#64748b', 'font-size': 20, id: 'lbl-mempool-txcount' }));
    g.appendChild(txt(TIP_CX, TIP_TOP + 96, '0',
      { fill: '#f8fafc', 'font-size': 34, 'font-weight': 'bold',
        id: 'lbl-mempool-inputs' }));
    g.appendChild(txt(TIP_CX, TIP_TOP + 130, 'inputs',
      { fill: MEMPOOL_COL, 'font-size': 28.5 }));
    g.appendChild(txt(TIP_CX, TIP_TOP + 183, '—',
      { fill: MEMPOOL_COL, 'font-size': 20, id: 'lbl-mempool-btc' }));
    blocksLayer.appendChild(g);
  }

  // ── Unconfirmed-inputs counter ────────────────────────────────────────────────
  // Fixed at the far right of the canvas, vertically centred with the mempool
  // block — clear of the arc sweep which reaches x ≈ TIP_RIGHT + ARC_MAX ≈ 1033.
  const COUNTER_X = 1140;
  blocksLayer.appendChild(txt(COUNTER_X, TIP_CY - 114, '0', {
    fill: '#f8fafc', 'font-size': 24, 'font-weight': 'bold',
    'text-anchor': 'middle', id: 'lbl-same-count',
  }));
  blocksLayer.appendChild(txt(COUNTER_X, TIP_CY - 98, 'unconfirmed', {
    fill: SAME_COL, 'font-size': 9.5, 'text-anchor': 'middle',
  }));
  blocksLayer.appendChild(txt(COUNTER_X, TIP_CY - 86, 'inputs', {
    fill: SAME_COL, 'font-size': 9.5, 'text-anchor': 'middle',
  }));

  blocksLayer.appendChild(txt(SVG_W / 2, SVG_H - 12,
    'each line = 1 spending input  ·  thickness ∝ log(BTC)  ·  red→violet = age 1→1000+  ·  gold = mempool→mempool',
    { fill: '#0f1d30', 'font-size': 10 }));

  document.getElementById('viz-wrap').appendChild(svg);
}

// ── Wire drawing ──────────────────────────────────────────────────────────────

function clearLines() {
  const layer = document.getElementById('lines-layer');
  while (layer.firstChild) layer.removeChild(layer.firstChild);
}

/**
 * Create a single SVG path element for one input (bucket + btc value).
 * flash=true: wire starts fully bright then fades to its normal opacity/width.
 * Returns null for unrecognised buckets.
 */
function makeWire(bucket, btc, flash = false) {
  const finalOp = Math.min(lineOpacity(btc), bucket === 'mempool' ? 0.55 : 1);
  const finalSW = lineWidth(btc);
  let d, col;

  if (bucket === 'mempool') {
    const y1    = TIP_CY + rand(-TH / 2 + 6, TH / 2 - 6);
    const x2    = TIP_CX + rand(-TW / 2 + 6, TW / 2 - 6);
    const ext_h = rand(MEMPOOL_ARC_MIN, MEMPOOL_ARC_MAX);
    const ext_v = ext_h * MEMPOOL_ARC_V_SCALE;
    d   = bezier(TIP_RIGHT, y1, TIP_RIGHT + ext_h, y1, x2, TIP_BOT + ext_v, x2, TIP_BOT);
    col = SAME_COL;
  } else {
    const age = parseInt(bucket, 10);

    // String(age) === bucket guards against parseInt("10_20") === 10 which would
    // incorrectly route the "10_20" range bucket into the top-row age branch.
    if (!isNaN(age) && age >= 1 && age <= 10 && String(age) === bucket) {
      const cx = topCx(age);
      const x1 = cx + rand(-BW / 2 + 4, BW / 2 - 4);
      const x2 = TIP_CX + rand(-TW / 2 + 4, TW / 2 - 4);
      const v  = TIP_TOP - SRC_BOT;
      d   = bezier(x1, SRC_BOT, x1, SRC_BOT + v * 0.40, x2, SRC_BOT + v * 0.60, x2, TIP_TOP);
      col = ageHsl(age);
    } else if (RANGES.includes(bucket)) {
      const i      = RANGES.indexOf(bucket);
      const blockH = (i === RANGES.length - 1) ? LC_H * 2 : LC_H;  // 1000+ is twice as tall
      const x1   = LC_CX + LC_W / 2;
      const y1   = LC_YS[i] + rand(-blockH / 2 + 4, blockH / 2 - 4);
      const x2   = TIP_CX + rand(-TW / 2 + 4, TW / 2 - 4);
      const y2   = TIP_CY + rand(-TH / 2 + 4, TH / 2 - 4);
      const midX = x1 + (x2 - x1) * 0.50;
      d   = bezier(x1, y1, midX, y1, midX, y2, x2, y2);
      col = rangeHsl(bucket);
    } else {
      return null;
    }
  }

  const path = el('path', {
    d, stroke: col, fill: 'none',
    'stroke-width': flash ? finalSW * 2.5 : finalSW,
    opacity:        flash ? 1.0            : finalOp,
  });

  if (flash) {
    // Two rAF frames ensures the browser paints the bright state first,
    // then the CSS transition takes over and fades to normal.
    requestAnimationFrame(() => requestAnimationFrame(() => {
      path.style.transition = 'opacity 0.7s ease-out, stroke-width 0.4s ease-out';
      path.style.opacity      = String(finalOp);
      path.style.strokeWidth  = String(finalSW);
    }));
  }

  return path;
}

/**
 * Append wires for a list of {bucket, btc} inputs.
 * Each wire starts bright (flash=true) and fades to its normal colour.
 * Trims oldest wires once the layer exceeds MAX_WIRES.
 */
function addWires(inputs) {
  if (!inputs || inputs.length === 0) return;
  const layer = document.getElementById('lines-layer');
  for (const { bucket, btc } of inputs) {
    const path = makeWire(bucket, btc, true);   // flash = true for live wires
    if (path) layer.appendChild(path);
  }
  while (layer.childNodes.length > MAX_WIRES) {
    layer.removeChild(layer.firstChild);
  }
}

/**
 * Draw a proportionally-sampled set of wires from the full bucket state.
 * Each bucket's line count is proportional to its share of total inputs, so
 * the visual density matches the relative distribution shown in the labels.
 * Used on initial connect and after each block confirmation.
 */
function drawLines(data) {
  const bkts = data.buckets || {};
  const keys = [
    ...Array.from({ length: 10 }, (_, i) => String(i + 1)),
    ...RANGES,
    'mempool',
  ];

  const totalInputs = keys.reduce((s, k) => s + (bkts[k]?.inputs || 0), 0);
  if (totalInputs === 0) return;

  // sqrt-proportional allocation: compresses the dynamic range so small
  // buckets (e.g. 300 inputs out of 20 000 total) still get enough lines to
  // be visible, while large buckets still dominate. Minimum 8 lines per
  // non-empty bucket regardless.
  const MIN_LINES  = 8;
  const sqrtTotal  = keys.reduce((s, k) => s + Math.sqrt(bkts[k]?.inputs || 0), 0);
  const frag = document.createDocumentFragment();

  for (const key of keys) {
    const b = bkts[key];
    if (!b || b.inputs === 0) continue;
    const n   = Math.max(MIN_LINES, Math.round(DRAW_BUDGET * Math.sqrt(b.inputs) / sqrtTotal));
    const avg = b.btc / b.inputs;
    for (let i = 0; i < n; i++) {
      const path = makeWire(key, avg * rand(0.5, 1.8));
      if (path) frag.appendChild(path);
    }
  }

  document.getElementById('lines-layer').appendChild(frag);
}

// ── Label / table updates ─────────────────────────────────────────────────────

function setTxt(id, val) {
  const e = document.getElementById(id);
  if (e) e.textContent = val;
}

function updateLabels(data) {
  const tip = data.tip_height || 0;
  const bkts = data.buckets || {};

  for (let age = 1; age <= 10; age++) {
    const b = bkts[String(age)] || { inputs: 0, btc: 0 };
    // confirmations=1 means the UTXO is in the tip block (height = tip_height).
    // confirmations=N means height = tip_height - N + 1.
    setTxt(`lbl-age-${age}-height`, `#${tip - age + 1}`);
    setTxt(`lbl-age-${age}-inputs`, fmtNum(b.inputs));
    setTxt(`lbl-age-${age}-btc`,    fmtBtc(b.btc) + ' ₿');
  }

  for (const key of RANGES) {
    const b = bkts[key] || { inputs: 0, btc: 0 };
    setTxt(`lbl-range-${key}-inputs`, fmtNum(b.inputs));
    setTxt(`lbl-range-${key}-btc`,    fmtBtc(b.btc) + ' ₿');
  }

  const totalIn  = Object.values(bkts).reduce((s, b) => s + (b.inputs || 0), 0);
  const totalBtc = Object.values(bkts).reduce((s, b) => s + (b.btc    || 0), 0);
  setTxt('lbl-mempool-txcount', `${fmtNum(data.mempool_tx_count)} txs`);
  setTxt('lbl-mempool-inputs',  fmtNum(totalIn));
  setTxt('lbl-mempool-btc',     fmtBtc(totalBtc) + ' ₿');
  setTxt('lbl-same-count',      fmtNum((bkts['mempool'] || {}).inputs || 0));
}

const TABLE_ORDER = [
  { key: 'mempool',    label: '0', color: SAME_COL },
  ...Array.from({ length: 10 }, (_, i) => ({
    key: String(i + 1), label: `−${i + 1}`, color: ageHsl(i + 1, 68),
  })),
  { key: '10_20',     label: '10–20',     color: rangeHsl('10_20', 68) },
  { key: '20_50',     label: '20–50',     color: rangeHsl('20_50', 68) },
  { key: '50_100',    label: '50–100',    color: rangeHsl('50_100', 68) },
  { key: '100_1000',  label: '100–1000',  color: rangeHsl('100_1000', 68) },
  { key: '1000_plus', label: '1000+',     color: rangeHsl('1000_plus', 68) },
];

function updateTable(data) {
  const tbody = document.getElementById('table-body');
  tbody.innerHTML = '';
  const bkts = data.buckets || {};
  for (const row of TABLE_ORDER) {
    const b  = bkts[row.key] || { inputs: 0, btc: 0, txs: 0 };
    const tr = document.createElement('tr');
    tr.innerHTML =
      `<td style="color:${row.color}">${row.label}</td>` +
      `<td>${fmtNum(b.inputs)}</td>` +
      `<td>${fmtNum(b.txs)}</td>` +
      `<td>${fmtBtc(b.btc)}</td>`;
    tbody.appendChild(tr);
  }
}

// ── Status bar ────────────────────────────────────────────────────────────────

let _lastUpdateTime = null;

function setStatus(state) {
  document.getElementById('conn-dot').className   = state;
  document.getElementById('conn-label').textContent =
    ({ live: 'LIVE', scanning: 'SCANNING', '': 'connecting…' }[state] || state);
}

function tickAge() {
  const e = document.getElementById('stat-age');
  if (!e || _lastUpdateTime === null) return;
  e.textContent = `${((Date.now() - _lastUpdateTime) / 1000).toFixed(1)}s ago`;
}

// ── WebSocket logic ───────────────────────────────────────────────────────────

let _ws            = null;
let _reconnDelay   = 1000;
let _tipHeight     = null;    // detect block changes
let _wasScanning   = false;   // detect scan completion → trigger wire redraw

function connect() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  _ws = new WebSocket(`${proto}://${location.host}/ws`);

  _ws.onopen = () => {
    _reconnDelay = 1000;
    setStatus('scanning');
  };

  _ws.onmessage = (ev) => {
    const data = JSON.parse(ev.data);
    if (data.type !== 'state') return;

    _lastUpdateTime = Date.now();
    setStatus(data.scanning ? 'scanning' : 'live');

    // Scan progress
    const wrap = document.getElementById('scan-wrap');
    if (data.scanning && data.scan_total > 0) {
      wrap.classList.add('visible');
      document.getElementById('scan-bar').style.width =
        (data.scan_done / data.scan_total * 100).toFixed(1) + '%';
      document.getElementById('scan-progress').textContent =
        `${fmtNum(data.scan_done)} / ${fmtNum(data.scan_total)}`;
    } else {
      wrap.classList.remove('visible');
    }

    // Stat bar
    document.getElementById('stat-txcount').textContent = fmtNum(data.mempool_tx_count);
    document.getElementById('stat-tip').textContent     = fmtNum(data.tip_height);

    // Labels + table (always)
    updateLabels(data);
    updateTable(data);

    // ── Wire logic ────────────────────────────────────────────────────────────
    const blockChanged    = _tipHeight !== null && data.tip_height !== _tipHeight;
    const firstConnect    = _tipHeight === null;
    const scanJustDone    = _wasScanning && !data.scanning;  // rescan finished → redraw
    _tipHeight    = data.tip_height;
    _wasScanning  = data.scanning;

    if (firstConnect || blockChanged || data.block_change) {
      // Block arrived (or first load): wipe wires; they'll repopulate as scan runs
      clearLines();
    } else if (scanJustDone) {
      // Rescan finished — draw a representative sample of the full mempool
      clearLines();
      drawLines(data);
    } else if (data.new_inputs && data.new_inputs.length > 0) {
      // New tx: append its wires without touching existing ones
      addWires(data.new_inputs);
    }
    // Mid-scan heartbeat: labels already updated above, wires unchanged
  };

  _ws.onclose = () => {
    setStatus('');
    setTimeout(connect, _reconnDelay);
    _reconnDelay = Math.min(_reconnDelay * 2, 30000);
  };

  _ws.onerror = (e) => console.error('WS error', e);
}

// ── Boot ──────────────────────────────────────────────────────────────────────

buildSVG();
connect();
setInterval(tickAge, 100);
