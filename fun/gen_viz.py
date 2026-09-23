#!/usr/bin/env python3
"""
Generate coin_age_viz.html.

Top row:     10 source blocks (ages 1–10, oldest left → newest right).
Left column: 5 age-range blocks (10–20, 20–50, 50–100, 100–1000, 1000+).
Bottom centre: tip block.
Same-block spends: bezier quarter-circles from tip's right edge around to tip's bottom edge.
"""

import json, collections, random, math, os

random.seed(42)
DIR = os.path.dirname(os.path.abspath(__file__))

data       = json.load(open(f"{DIR}/coin_age_968282.json"))
TIP_HEIGHT = data["meta"]["block_height"]

# ── collect data -----------------------------------------------------------

by_age = collections.defaultdict(list)
for r in data["inputs"]:
    a = r.get("age_blocks")
    if a is not None and 0 <= a <= 10:
        by_age[a].append(r)

by_age_txs = {}
for age in range(11):
    txs = {}
    for r in by_age[age]:
        txs.setdefault(r["spending_txid"], 0.0)
        txs[r["spending_txid"]] += r.get("value_btc") or 0.0
    by_age_txs[age] = txs

INF = 10_000_000
# The first range bumps its lower bound to 11 so age-10 inputs (already in the
# top row) aren't double-counted. All other range boundaries stay as-is.
RANGES = [(10, 20), (20, 50), (50, 100), (100, 1000), (1000, INF)]
range_rows = {}
range_txs  = {}
for rng in RANGES:
    lo, hi = rng
    lo_actual = lo + 1 if lo == 10 else lo   # skip age 10 (shown individually above)
    rows = [r for r in data["inputs"]
            if r.get("age_blocks") is not None and lo_actual <= r["age_blocks"] < hi]
    range_rows[rng] = rows
    txs = {}
    for r in rows:
        txs.setdefault(r["spending_txid"], 0.0)
        txs[r["spending_txid"]] += r.get("value_btc") or 0.0
    range_txs[rng] = txs

# ── layout -----------------------------------------------------------------

SVG_W, SVG_H = 1320, 900

# Top row: ages 1–10 (age 10 leftmost, age 1 rightmost)
BW, BH  = 84, 90
TOP_CY  = 78
TOP_L   = 185
TOP_R   = 1270
TOP_PIT = (TOP_R - TOP_L) / 9

def top_cx(age):
    return TOP_L + (10 - age) * TOP_PIT

# Left column: 5 range blocks — lowered so their wires start below the
# dense zone occupied by the age-10 block's wires (which begin at y≈123).
LC_W, LC_H = 100, 84
LC_CX  = 62
LC_YS  = [215, 320, 425, 530, 635]   # 105px pitch, ~21px gap; first block clears age-10 wire zone

# Tip block — moved up and enlarged to spread arriving wires
TW, TH   = 124, 124
TIP_CX   = SVG_W / 2
TIP_CY   = 480
TIP_TOP  = TIP_CY - TH / 2
TIP_BOT  = TIP_CY + TH / 2
TIP_LEFT = TIP_CX - TW / 2
TIP_RIGHT= TIP_CX + TW / 2

# Same-block arc radius range (pixels the arc bulges past the corner)
ARC_MIN, ARC_MAX = 180, 280

MAX_TOP   = 55
MAX_RANGE = 45
MAX_SAME  = 50   # same-block quarter-circle curves

# ── colour helpers ---------------------------------------------------------

def age_hsl(age, l=63):
    hue = int((age - 1) / 9 * 220)
    return f"hsl({hue},88%,{l}%)"

RANGE_HUES = {(10,20): 233, (20,50): 258, (50,100): 282, (100,1000): 308, (1000,INF): 333}
def range_hsl(rng, l=62):
    return f"hsl({RANGE_HUES[rng]},78%,{l}%)"

SAME_COL = "hsl(48,95%,65%)"    # gold — visually distinct from age gradient

def line_opacity(btc):
    if btc <= 0: return 0.15
    return min(0.88, max(0.18, 0.18 + 0.14 * math.log10(btc + 1)))

def line_width(btc):
    if btc >= 10_000: return 4.5
    if btc >= 1_000:  return 2.8
    if btc >= 100:    return 1.8
    if btc >= 10:     return 1.2
    return 0.85

def fmt_btc(v):
    if v >= 10_000: return f"{v/1000:.1f}k"
    if v >= 1_000:  return f"{v:,.0f}"
    if v >= 1:      return f"{v:.1f}"
    return f"{v:.4f}"

def sample_txs(txs, n):
    items = sorted(txs.items(), key=lambda x: -x[1])
    top   = items[:5]
    rest  = items[5:]
    tail  = random.sample(rest, min(len(rest), n - len(top))) if rest else []
    return top + tail

# ── SVG elements -----------------------------------------------------------

line_parts  = []
block_parts = []

SRC_BOT = TOP_CY + BH / 2

# ── Top-row flow lines (drop into tip top) ---------------------------------

for age in range(1, 11):
    scx = top_cx(age)
    col = age_hsl(age)
    for _tid, btc in sample_txs(by_age_txs[age], MAX_TOP):
        x1 = scx + random.uniform(-BW/2+4, BW/2-4)
        x2 = TIP_CX + random.uniform(-TW/2+4, TW/2-4)
        y1, y2 = SRC_BOT, TIP_TOP
        vert = y2 - y1
        d = (f"M{x1:.1f},{y1:.1f} "
             f"C{x1:.1f},{y1+vert*0.40:.1f} {x2:.1f},{y1+vert*0.60:.1f} "
             f"{x2:.1f},{y2:.1f}")
        line_parts.append(
            f'<path d="{d}" stroke="{col}" stroke-width="{line_width(btc):.1f}" '
            f'fill="none" opacity="{line_opacity(btc):.2f}"/>')

# ── Left-column flow lines (go right → down into tip) ---------------------

for i, rng in enumerate(RANGES):
    lc_cy = LC_YS[i]
    src_x = LC_CX + LC_W / 2
    col   = range_hsl(rng)
    for _tid, btc in sample_txs(range_txs[rng], MAX_RANGE):
        y1 = lc_cy + random.uniform(-LC_H/2+4, LC_H/2-4)
        x2 = TIP_CX + random.uniform(-TW/2+4, TW/2-4)
        y2 = TIP_CY + random.uniform(-TH/2+4, TH/2-4)
        horiz = x2 - src_x
        cp1x, cp1y = src_x + horiz * 0.50, y1
        cp2x, cp2y = src_x + horiz * 0.50, y2
        d = (f"M{src_x:.1f},{y1:.1f} "
             f"C{cp1x:.1f},{cp1y:.1f} {cp2x:.1f},{cp2y:.1f} "
             f"{x2:.1f},{y2:.1f}")
        line_parts.append(
            f'<path d="{d}" stroke="{col}" stroke-width="{line_width(btc):.1f}" '
            f'fill="none" opacity="{line_opacity(btc):.2f}"/>')

# ── Same-block quarter-circle curves (right edge → bottom edge of tip) ----
# Bezier quarter-circle: exit right → arc around bottom-right corner → enter from below.
# CP1 extends rightward from the start; CP2 extends downward from the end.
# The arc radius (ext) varies slightly per line for visual spread.

same_txs = sample_txs(by_age_txs[0], MAX_SAME)
for _tid, btc in same_txs:
    # start: random point spread across the full right edge
    y1  = TIP_CY + random.uniform(-TH/2+6, TH/2-6)
    # end: random point spread across the full bottom edge
    x2  = TIP_CX + random.uniform(-TW/2+6, TW/2-6)
    ext = random.uniform(ARC_MIN, ARC_MAX)
    op  = line_opacity(btc)
    sw  = line_width(btc)
    # CP1: exit the right edge going right (outward)
    # CP2: arrive at the bottom edge coming from below (outward)
    # Together they trace a quarter-circle arc around the bottom-right corner.
    cp1x, cp1y = TIP_RIGHT + ext, y1
    cp2x, cp2y = x2,              TIP_BOT + ext
    d = (f"M{TIP_RIGHT:.1f},{y1:.1f} "
         f"C{cp1x:.1f},{cp1y:.1f} {cp2x:.1f},{cp2y:.1f} "
         f"{x2:.1f},{TIP_BOT:.1f}")
    line_parts.append(
        f'<path d="{d}" stroke="{SAME_COL}" stroke-width="{sw:.1f}" '
        f'fill="none" opacity="{min(op, 0.55):.2f}"/>')

# ── Top-row blocks ---------------------------------------------------------

for age in range(1, 11):
    scx  = top_cx(age)
    bx   = scx - BW/2
    by   = TOP_CY - BH/2
    col  = age_hsl(age)
    cnt  = len(by_age[age])
    btc  = sum(r.get("value_btc") or 0 for r in by_age[age])
    block_parts += [
        f'<rect x="{bx:.1f}" y="{by:.1f}" width="{BW}" height="{BH}" '
        f'rx="6" fill="#080f1c" stroke="{col}" stroke-width="1.8"/>',
        f'<text x="{scx:.1f}" y="{by+15:.1f}" text-anchor="middle" '
        f'fill="{col}" font-size="9.5" font-family="monospace">#{TIP_HEIGHT-age}</text>',
        f'<text x="{scx:.1f}" y="{by+27:.1f}" text-anchor="middle" '
        f'fill="#253450" font-size="8.5" font-family="monospace">age {age}</text>',
        f'<text x="{scx:.1f}" y="{by+49:.1f}" text-anchor="middle" '
        f'fill="#f1f5f9" font-size="15" font-weight="bold" font-family="monospace">{cnt}</text>',
        f'<text x="{scx:.1f}" y="{by+61:.1f}" text-anchor="middle" '
        f'fill="#1a2c48" font-size="7.5" font-family="monospace">inputs</text>',
        f'<text x="{scx:.1f}" y="{by+76:.1f}" text-anchor="middle" '
        f'fill="{col}" font-size="9" font-family="monospace">{fmt_btc(btc)} ₿</text>',
    ]

# ── Left-column range blocks -----------------------------------------------

for i, rng in enumerate(RANGES):
    lo, hi  = rng
    lc_cy   = LC_YS[i]
    bx      = LC_CX - LC_W/2
    by      = lc_cy - LC_H/2
    col     = range_hsl(rng)
    cnt     = len(range_rows[rng])
    btc     = sum(r.get("value_btc") or 0 for r in range_rows[rng])
    label   = f"{lo}+" if hi == INF else f"{lo}–{hi}"
    block_parts += [
        f'<rect x="{bx:.1f}" y="{by:.1f}" width="{LC_W}" height="{LC_H}" '
        f'rx="6" fill="#080f1c" stroke="{col}" stroke-width="1.8"/>',
        f'<text x="{LC_CX}" y="{by+14:.1f}" text-anchor="middle" '
        f'fill="{col}" font-size="9" font-family="monospace">age {label}</text>',
        f'<text x="{LC_CX}" y="{by+25:.1f}" text-anchor="middle" '
        f'fill="#253450" font-size="7.5" font-family="monospace">blocks</text>',
        f'<text x="{LC_CX}" y="{by+46:.1f}" text-anchor="middle" '
        f'fill="#f1f5f9" font-size="15" font-weight="bold" font-family="monospace">{cnt}</text>',
        f'<text x="{LC_CX}" y="{by+57:.1f}" text-anchor="middle" '
        f'fill="#1a2c48" font-size="7.5" font-family="monospace">inputs</text>',
        f'<text x="{LC_CX}" y="{by+72:.1f}" text-anchor="middle" '
        f'fill="{col}" font-size="9" font-family="monospace">{fmt_btc(btc)} ₿</text>',
    ]

# ── Tip block --------------------------------------------------------------

tip_total = (sum(r.get("value_btc") or 0 for a in range(11) for r in by_age[a]) +
             sum(sum(r.get("value_btc") or 0 for r in v) for v in range_rows.values()))

block_parts += [
    f'<rect x="{TIP_LEFT:.1f}" y="{TIP_TOP:.1f}" width="{TW}" height="{TH}" '
    f'rx="8" fill="#060f22" stroke="#3b82f6" stroke-width="2.8" filter="url(#glow)"/>',
    f'<text x="{TIP_CX:.1f}" y="{TIP_TOP+19:.1f}" text-anchor="middle" '
    f'fill="#60a5fa" font-size="10" font-family="monospace">#{TIP_HEIGHT}</text>',
    f'<text x="{TIP_CX:.1f}" y="{TIP_TOP+32:.1f}" text-anchor="middle" '
    f'fill="#93c5fd" font-size="9.5" font-family="monospace">TIP  ★</text>',
    f'<text x="{TIP_CX:.1f}" y="{TIP_TOP+57:.1f}" text-anchor="middle" '
    f'fill="#f8fafc" font-size="18" font-weight="bold" font-family="monospace">'
    f'{data["meta"]["inputs_analyzed"]:,}</text>',
    f'<text x="{TIP_CX:.1f}" y="{TIP_TOP+70:.1f}" text-anchor="middle" '
    f'fill="#1e3a5f" font-size="7.5" font-family="monospace">total inputs</text>',
    f'<text x="{TIP_CX:.1f}" y="{TIP_TOP+87:.1f}" text-anchor="middle" '
    f'fill="#3b82f6" font-size="9" font-family="monospace">{fmt_btc(tip_total)} ₿</text>',
    # same-block label — sits to the right of the right edge, mid-height
    f'<text x="{TIP_RIGHT+10:.1f}" y="{TIP_CY-6:.1f}" text-anchor="start" '
    f'fill="{SAME_COL}" font-size="8" font-family="monospace" opacity="0.75">'
    f'{len(by_age[0])} same-</text>',
    f'<text x="{TIP_RIGHT+10:.1f}" y="{TIP_CY+6:.1f}" text-anchor="start" '
    f'fill="{SAME_COL}" font-size="8" font-family="monospace" opacity="0.75">'
    f'block</text>',
]

# ── Assemble SVG ----------------------------------------------------------

svg = f'''\
<svg viewBox="0 0 {SVG_W} {SVG_H}" xmlns="http://www.w3.org/2000/svg"
     style="background:#040a14;border-radius:14px;width:100%">
  <defs>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  {chr(10).join("  "+p for p in line_parts)}
  {chr(10).join("  "+p for p in block_parts)}
  <text x="{SVG_W//2}" y="{SVG_H-12}" text-anchor="middle"
        fill="#0f1d30" font-size="10" font-family="monospace">
    each line = 1 spending tx · thickness ∝ log(BTC) · red→violet = age 1→1000+  · gold = same-block
  </text>
</svg>'''

# ── Summary table ---------------------------------------------------------

def row_age(age):
    rows = by_age[age]
    btc  = sum(r.get("value_btc") or 0 for r in rows)
    col  = age_hsl(age, l=68)
    mbtc = max((r.get("value_btc") or 0 for r in rows), default=0)
    return (f'<tr><td style="color:{col}">−{age}</td>'
            f'<td>#{TIP_HEIGHT-age}</td>'
            f'<td>{len(rows):,}</td><td>{len(by_age_txs[age]):,}</td>'
            f'<td>{fmt_btc(btc)}</td><td>{fmt_btc(mbtc)}</td></tr>')

def row_range(rng):
    lo, hi = rng
    rows   = range_rows[rng]
    btc    = sum(r.get("value_btc") or 0 for r in rows)
    col    = range_hsl(rng, l=68)
    mbtc   = max((r.get("value_btc") or 0 for r in rows), default=0)
    label  = f"{lo}+" if hi == INF else f"{lo}–{hi}"
    blks   = f"#{TIP_HEIGHT-min(hi,TIP_HEIGHT)}–#{TIP_HEIGHT-lo}"
    return (f'<tr><td style="color:{col}">{label}</td>'
            f'<td>{blks}</td>'
            f'<td>{len(rows):,}</td><td>{len(range_txs[rng]):,}</td>'
            f'<td>{fmt_btc(btc)}</td><td>{fmt_btc(mbtc)}</td></tr>')

same_rows = by_age[0]
same_btc  = sum(r.get("value_btc") or 0 for r in same_rows)
same_max  = max((r.get("value_btc") or 0 for r in same_rows), default=0)
same_row  = (f'<tr><td style="color:{SAME_COL}">same block</td>'
             f'<td>#{TIP_HEIGHT}</td>'
             f'<td>{len(same_rows):,}</td><td>{len(by_age_txs[0]):,}</td>'
             f'<td>{fmt_btc(same_btc)}</td><td>{fmt_btc(same_max)}</td></tr>')

divider = "<tr><td colspan='6' style='color:#1a2c48;padding-top:4px'></td></tr>"
rows_html = (same_row + divider +
             "".join(row_age(a) for a in range(1, 11)) + divider +
             "".join(row_range(r) for r in RANGES))

# ── Full HTML -------------------------------------------------------------

html = f'''\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bitcoin Block {TIP_HEIGHT} – Coin Age</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #020810;
    color: #cbd5e1;
    font-family: "Courier New", monospace;
    padding: 28px 32px;
  }}
  h1   {{ color: #e2e8f0; font-size: 17px; letter-spacing: .03em; margin-bottom: 4px; }}
  .sub {{ color: #253450; font-size: 11px; margin-bottom: 24px; }}
  .viz {{ max-width: 1320px; margin: 0 auto 32px; }}
  h2   {{ color: #1e3a5f; font-size: 10px; letter-spacing: .1em;
           text-transform: uppercase; margin-bottom: 10px; }}
  table {{ border-collapse: collapse; font-size: 12px; }}
  th {{
    color: #1e3a5f; font-size: 10px; letter-spacing: .06em;
    text-transform: uppercase; padding: 5px 18px 5px 0;
    border-bottom: 1px solid #080f1e; text-align: right;
  }}
  th:first-child, th:nth-child(2) {{ text-align: left; }}
  td {{
    padding: 5px 18px 5px 0; text-align: right;
    color: #334155; border-bottom: 1px solid #060d1a;
  }}
  td:first-child  {{ text-align: left; font-weight: bold; }}
  td:nth-child(2) {{ text-align: left; color: #0f1d30; }}
  tr:hover td {{ background: #080f1c; }}
  .note {{ color: #0f1d30; font-size: 10px; margin-top: 18px; line-height: 1.7; }}
</style>
</head>
<body>
<h1>Bitcoin Block #{TIP_HEIGHT} — Input Coin Ages</h1>
<p class="sub">
  {data["meta"]["block_time_utc"]} &nbsp;·&nbsp;
  {data["meta"]["inputs_analyzed"]:,} inputs &nbsp;·&nbsp;
  verbosity=3 (no txindex needed)
</p>
<div class="viz">{svg}</div>
<h2>By source block / range</h2>
<table>
  <thead>
    <tr>
      <th>Age (blocks)</th><th>Block(s)</th><th>Inputs</th>
      <th>Unique txs</th><th>Total BTC</th><th>Max input</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
<p class="note">
  Top row: individual ages 10→1. Left column: bucketed ranges for older coins.<br>
  Gold curves (bottom-right of tip): same-block spends — coin created and spent in block #{TIP_HEIGHT}.<br>
  Lines sampled: up to {MAX_TOP} (top row), {MAX_RANGE} (ranges), {MAX_SAME} (same-block).
</p>
</body>
</html>
'''

out = f"{DIR}/coin_age_viz.html"
with open(out, "w") as f:
    f.write(html)
print(f"Written: {out}  ({len(html):,} bytes)")
