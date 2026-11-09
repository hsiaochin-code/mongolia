"""產生論文格式研究架構圖（SVG），並以 Playwright 輸出 PNG / PDF。"""
import pathlib
import subprocess

W, H = 1800, 1210
# 中文：標楷體（Windows 開啟 SVG 時優先使用；轉檔環境以教育部全字庫正楷體 TW-Kai 替代）；英文：Times New Roman
FONT = "'Times New Roman','Liberation Serif','DFKai-SB','標楷體','BiauKai','TW-Kai',serif"
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
TOP = 30
stages = [(40, 776, "旅前階段（Pre-trip）", "旅遊誘因"),
          (900, 1304, "旅中階段（During-trip）", "旅遊體驗"),
          (1400, 1770, "旅後階段（Post-trip）", "記憶延伸與持續消費")]
for x1, x2, s, sub in stages:
    a(f'<rect x="{x1}" y="{TOP}" width="{x2-x1}" height="58" fill="#eee" stroke="#000" stroke-width="1.2"/>')
    text((x1 + x2) / 2, TOP + 25, s, 19, "bold")
    text((x1 + x2) / 2, TOP + 49, sub, 17)
text(40, TOP + 89, "旅遊歷程（Tourist Journey）", 16, anchor="start", style="italic")
arrow(260, TOP + 84, 1770, TOP + 84, sw=1.5)

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
cx, cw = 40, 260
construct(cx, cw, "數位接觸管道", "Digital Touchpoints",
          [("網路資訊", "Online Information"), ("社群媒體", "Social Media"),
           ("電商平台", "E-commerce Platforms")], "前置變數", pad=18)
# S
sx, sw_ = 456, 320
construct(sx, sw_, "食品紀念品刺激", "Stimulus (S)",
          [("吸引力", "Attractiveness"), ("地方特色", "Local Uniqueness"),
           ("文化故事", "Cultural Story"), ("品牌形象", "Brand Image")], "自變數")
# O：三個中介變數（序列）
ox, ow = 932, 340
op = construct(ox, ow, "旅客心理歷程", "Organism (O)",
               [("真實性感知", "Perceived Authenticity"), ("地方興趣", "Place Interest"),
                ("地方依附", "Place Attachment")], "中介變數")
ix1, ix2 = ox + 30, ox + ow - 30          # O 內方框左右緣
pa_c = sum(op[0]) / 2                      # 真實性感知中心 y
patt_c = sum(op[2]) / 2                    # 地方依附中心 y
for (t, b), (t2, _), h in zip(op, op[1:], ["H3", "H4"]):
    arrow(ox + ow / 2, b, ox + ow / 2, t2 - 2)
    hyp(ox + ow / 2 + 14, (b + t2) / 2 + 7, h)
    out[-1] = out[-1].replace('text-anchor="middle"', 'text-anchor="start"')
# R：後續行為意圖（單一構面，三個衡量面向）
rx, rw = 1430, 340
rp = construct(rx, rw, "後續行為意圖", "Behavioral Intention (R)",
          [("推薦意圖", "Recommendation Intention"), ("回購意圖", "Online &amp; Repeat Purchase"),
           ("再訪意圖", "Revisit Intention")], "依變數")

mid = (Y0 + Y1) / 2
arrow(cx + cw, mid, sx - 2, mid); hyp((cx + cw + sx) / 2, mid - 14, "H1")
arrow(sx + sw_, pa_c, ix1 - 2, pa_c); hyp((sx + sw_ + ix1) / 2, pa_c - 14, "H2")
# H5、H6 指向 R 構面外框（落在面向方框之間），表示作用於整體構面
r_up = (rp[0][1] + rp[1][0]) / 2
r_dn = (rp[1][1] + rp[2][0]) / 2
arrow(ix2, pa_c, rx - 2, r_up); hyp((ix2 + rx) / 2, (pa_c + r_up) / 2 - 14, "H6")
arrow(ix2, patt_c, rx - 2, r_dn); hyp((ix2 + rx) / 2, (patt_c + r_dn) / 2 - 14, "H5")

# 直接效果（S → R，中介檢驗用，不列假設）
a(f'<path d="M{sx + sw_ / 2},{Y0} L{sx + sw_ / 2},{Y0 - 30} L{rx + rw / 2},{Y0 - 30} L{rx + rw / 2},{Y0 - 2}" '
  'fill="none" stroke="#000" stroke-width="1.2" stroke-dasharray="3,4" marker-end="url(#ah)"/>')
a(f'<rect x="{(sx+rx+rw)/2 - 230}" y="{Y0 - 44}" width="460" height="28" fill="#fff"/>')
text((sx + rx + rw) / 2, Y0 - 23, "直接效果（中介檢驗用，不列假設）", 18)

# H7：中介效果以大括號標示於 O 構面下方（不另畫路徑）
by, bh, br = Y1 + 10, 24, 12
xm, x1, x2 = ox + ow / 2, ox + 6, ox + ow - 6
a(f'<path d="M{x1},{by} Q{x1},{by + bh / 2} {x1 + br},{by + bh / 2} L{xm - br},{by + bh / 2} '
  f'Q{xm},{by + bh / 2} {xm},{by + bh} Q{xm},{by + bh / 2} {xm + br},{by + bh / 2} '
  f'L{x2 - br},{by + bh / 2} Q{x2},{by + bh / 2} {x2},{by}" fill="none" stroke="#000" stroke-width="1.6"/>')
hyp(xm, by + bh + 28, "H7a、H7b：中介效果")
out[-1] = out[-1].replace('font-style="italic"', 'font-style="normal"')

# 回饋（循環）路徑：概念說明，不列入檢驗
FB = 960
a(f'<path d="M{rx + rw / 2},{Y1} L{rx + rw / 2},{FB} L{sx + sw_ / 2},{FB} L{sx + sw_ / 2},{Y1 + 2}" '
  'fill="none" stroke="#000" stroke-width="1.6" stroke-dasharray="9,6" marker-end="url(#ah)"/>')
text((sx + rx + rw) / 2, FB - 14,
     "回饋效果（概念說明，不列入檢驗）：到訪金門、體驗地方文化、現地購買", 18)

# 圖例
lx, ly = 40, 1010
a(f'<line x1="{lx}" y1="{ly}" x2="{lx+50}" y2="{ly}" stroke="#000" stroke-width="2"/>')
text(lx + 60, ly + 6, "研究假設路徑", 16, anchor="start")
a(f'<line x1="{lx+200}" y1="{ly}" x2="{lx+250}" y2="{ly}" stroke="#000" stroke-width="1.2" stroke-dasharray="3,4"/>')
text(lx + 260, ly + 6, "直接效果（不列假設）", 16, anchor="start")
a(f'<line x1="{lx+440}" y1="{ly}" x2="{lx+490}" y2="{ly}" stroke="#000" stroke-width="1.6" stroke-dasharray="9,6"/>')
text(lx + 500, ly + 6, "循環關係（概念說明）", 16, anchor="start")

# 中介假設註記
text(40, 1052, "註：H7a 中介路徑：食品紀念品刺激 → 真實性感知 → 後續行為意圖（H2 × H6）", 17, anchor="start")
text(40, 1080, "　　H7b 序列中介路徑：食品紀念品刺激 → 真實性感知 → 地方興趣 → 地方依附 → 後續行為意圖（H2 × H3 × H4 × H5）", 17, anchor="start")

# 圖名與資料來源（論文格式：圖名置於圖下方）
text(W / 2, 1146, "圖 3-1　研究架構圖", 26, "bold")
text(W / 2, 1182, "資料來源：本研究整理（理論基礎：SOR 理論、旅遊歷程理論、體驗經濟、食品旅遊、真實性理論、地方依附理論）", 17)
a("</svg>")

here = pathlib.Path(__file__).parent
svg = here / "research_framework.svg"
svg.write_text("\n".join(out), encoding="utf-8")
subprocess.run(["node", str(here / "render.js")], check=True)
print("done")
