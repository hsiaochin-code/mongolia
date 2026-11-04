"""產生論文格式研究架構圖（SVG），並以 Playwright 輸出 PNG / PDF。"""
import pathlib
import subprocess

W, H = 1800, 1060
FONT = "'Times New Roman','Liberation Serif','WenQuanYi Zen Hei',serif"
out = []
a = out.append

def text(x, y, s, size=20, weight="normal", anchor="middle", style="normal"):
    a(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
      f'font-style="{style}" text-anchor="{anchor}">{s}</text>')

def box(x, y, w, h, dash=False, sw=1.6):
    d = ' stroke-dasharray="8,5"' if dash else ""
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#000" stroke-width="{sw}"{d}/>')

def item(x, y, w, h, zh, en):
    box(x, y, w, h)
    text(x + w / 2, y + h / 2 - 4, zh, 21)
    text(x + w / 2, y + h / 2 + 22, en, 16, style="italic")

def arrow(x1, y1, x2, y2, dash=False, sw=2):
    d = ' stroke-dasharray="9,6"' if dash else ""
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" stroke-width="{sw}"{d} marker-end="url(#ah)"/>')

def hyp(x, y, s):
    text(x, y, s, 20, "bold", style="italic")

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
a('<defs><marker id="ah" markerWidth="12" markerHeight="10" refX="11" refY="5" orient="auto">'
  '<path d="M0,0 L12,5 L0,10 z" fill="#000"/></marker></defs>')
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')

# 旅遊歷程階段（頂部時間軸）
TOP = 40
stages = [(40, 640, "旅前階段（Pre-trip）：旅遊誘因"),
          (720, 1060, "旅中階段（During-trip）：旅遊體驗"),
          (1130, 1770, "旅後階段（Post-trip）：記憶延伸與持續消費")]
for x1, x2, s in stages:
    a(f'<rect x="{x1}" y="{TOP}" width="{x2-x1}" height="44" fill="#eee" stroke="#000" stroke-width="1.2"/>')
    text((x1 + x2) / 2, TOP + 29, s, 20, "bold")
arrow(40, TOP + 70, 1770, TOP + 70, sw=1.5)
text(1770, TOP + 96, "旅遊歷程（Tourist Journey）", 16, anchor="end", style="italic")

Y0, Y1 = 170, 830  # 構面框上下界

def construct(x, w, zh, en, items, role, pad=30):
    box(x, Y0, w, Y1 - Y0, sw=2)
    text(x + w / 2, Y0 + 38, zh, 23, "bold")
    text(x + w / 2, Y0 + 66, en, 18, style="italic")
    text(x + w / 2, Y0 + 94, f"〔{role}〕", 17)
    n = len(items)
    ih = 92
    gap = (Y1 - Y0 - 110 - n * ih) / (n + 1)
    pos = []
    for i, (z, e) in enumerate(items):
        yy = Y0 + 100 + gap * (i + 1) + ih * i
        item(x + pad, yy, w - 2 * pad, ih, z, e)
        pos.append((yy, yy + ih))
    return pos

# 前置變數：數位接觸管道
cx, cw = 40, 240
construct(cx, cw, "數位接觸管道", "Digital Touchpoints",
          [("網路資訊", "Online Information"), ("社群媒體", "Social Media"),
           ("電商平台", "E-commerce Platforms")], "前置變數", pad=18)
# S
sx, sw_ = 340, 300
construct(sx, sw_, "食品紀念品刺激", "Stimulus (S)",
          [("吸引力", "Attractiveness"), ("地方特色", "Local Uniqueness"),
           ("文化故事", "Cultural Story"), ("品牌形象", "Brand Image")], "自變數")
# O
ox, ow = 740, 320
op = construct(ox, ow, "旅客心理歷程", "Organism (O)",
               [("真實性感知", "Perceived Authenticity"), ("地方興趣", "Place Interest"),
                ("地方依附", "Place Attachment")], "中介變數")
for (t, b), (t2, _) in zip(op, op[1:]):
    arrow(ox + ow / 2, b, ox + ow / 2, t2 - 2)
# R
rx, rw = 1140, 320
rp = construct(rx, rw, "旅客後續行為", "Response (R)",
               [("分享與推薦", "Sharing &amp; Recommendation"), ("線上回購", "Online Repurchase"),
                ("再訪意圖", "Revisit Intention")], "依變數")
for (t, b), (t2, _) in zip(rp, rp[1:]):
    arrow(rx + rw / 2, b, rx + rw / 2, t2 - 2)

# 結果：後續旅遊行為與地方發展
fx, fw = 1540, 230
box(fx, 350, fw, 300, sw=2)
text(fx + fw / 2, 388, "後續旅遊行為", 22, "bold")
text(fx + fw / 2, 416, "與地方發展", 22, "bold")
text(fx + fw / 2, 442, "(Outcomes)", 16, style="italic")
text(fx + fw / 2, 468, "〔結果變數〕", 17)
for i, s in enumerate(["再次造訪", "多次購買", "品牌忠誠", "地方支持"]):
    text(fx + fw / 2, 508 + i * 38, s, 20)

mid = (Y0 + Y1) / 2
arrow(cx + cw, mid, sx - 2, mid); hyp((cx + cw + sx) / 2, mid - 14, "H1")
arrow(sx + sw_, mid, ox - 2, mid); hyp((sx + sw_ + ox) / 2, mid - 14, "H2")
arrow(ox + ow, mid, rx - 2, mid); hyp((ox + ow + rx) / 2, mid - 14, "H3")
arrow(rx + rw, mid, fx - 2, mid); hyp((rx + rw + fx) / 2, mid - 14, "H4")
# 直接效果（S → R，檢驗中介）
a(f'<path d="M{sx + sw_ / 2},{Y0} L{sx + sw_ / 2},{Y0 - 30} L{rx + rw / 2},{Y0 - 30} L{rx + rw / 2},{Y0 - 2}" '
  'fill="none" stroke="#000" stroke-width="1.6" stroke-dasharray="3,4" marker-end="url(#ah)"/>')
a(f'<rect x="{(sx+rx+rw)/2 - 150}" y="{Y0 - 44}" width="300" height="28" fill="#fff"/>')
text((sx + rx + rw) / 2, Y0 - 23, "H5：直接效果（Direct Effect）", 18, style="italic")

# 回饋（循環）路徑
FB = 900
a(f'<path d="M{rx + rw / 2},{Y1} L{rx + rw / 2},{FB} L{sx + sw_ / 2},{FB} L{sx + sw_ / 2},{Y1 + 2}" '
  'fill="none" stroke="#000" stroke-width="1.6" stroke-dasharray="9,6" marker-end="url(#ah)"/>')
text((sx + rx + rw) / 2, FB - 14,
     "回饋效果：到訪金門、體驗地方文化、現地購買（Visit, Cultural Experience, On-site Purchase）", 18)

# 圖例
lx, ly = 1250, 945
a(f'<line x1="{lx}" y1="{ly}" x2="{lx+50}" y2="{ly}" stroke="#000" stroke-width="2"/>')
text(lx + 60, ly + 6, "直接影響關係", 16, anchor="start")
a(f'<line x1="{lx+200}" y1="{ly}" x2="{lx+250}" y2="{ly}" stroke="#000" stroke-width="1.6" stroke-dasharray="9,6"/>')
text(lx + 260, ly + 6, "間接影響或循環關係", 16, anchor="start")

# 圖名與資料來源（論文格式：圖名置於圖下方）
text(W / 2, 1000, "圖 3-1　研究架構圖", 26, "bold")
text(W / 2, 1036, "資料來源：本研究整理（理論基礎：SOR 理論、旅遊歷程理論、體驗經濟、食品旅遊、真實性理論、地方依附理論）", 17)
a("</svg>")

here = pathlib.Path(__file__).parent
svg = here / "research_framework.svg"
svg.write_text("\n".join(out), encoding="utf-8")
subprocess.run(["node", str(here / "render.js")], check=True)
print("done")
