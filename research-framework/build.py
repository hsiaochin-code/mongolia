"""產生論文格式研究架構圖（SVG），並以 Playwright 輸出 PNG / PDF，另輸出可編輯的 PPTX。"""
import pathlib
import json
import subprocess

W, H = 1800, 1210
# 中文：標楷體（Windows 開啟 SVG 時優先使用；轉檔環境以教育部全字庫正楷體 TW-Kai 替代）；英文：Times New Roman
FONT = "'Times New Roman','Liberation Serif','DFKai-SB','標楷體','BiauKai','TW-Kai',serif"
out = []
a = out.append
prims = []  # 給 build_pptx.js 使用的可編輯圖元（座標單位同 SVG 像素）
P = prims.append

def text(x, y, s, size=20, weight="normal", anchor="middle", style="normal", record=True):
    a(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
      f'font-style="{style}" text-anchor="{anchor}">{s}</text>')
    if record:
        P(dict(t="text", x=x, y=y, s=s.replace("&amp;", "&"), size=size,
               bold=weight == "bold", italic=style == "italic", anchor=anchor))

def box(x, y, w, h, dash=False, sw=1.6, fill="#fff", stroke=True, lines=None):
    d = ' stroke-dasharray="8,5"' if dash else ""
    st = f'stroke="#000" stroke-width="{sw}"' if stroke else 'stroke="none"'
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {st}{d}/>')
    P(dict(t="rect", x=x, y=y, w=w, h=h, sw=sw if stroke else 0, fill=fill, lines=lines or []))

def item(x, y, w, h, zh, en):
    box(x, y, w, h, lines=[dict(s=zh, size=21), dict(s=en.replace("&amp;", "&"), size=16, italic=True)])
    text(x + w / 2, y + h / 2 - 4, zh, 21, record=False)
    text(x + w / 2, y + h / 2 + 22, en, 16, style="italic", record=False)

def path(pts, sw=2, dash=None, head=True):
    """折線；dash: None / "dot" / "dash"；head: 最後一段加箭頭"""
    da = {"dot": ' stroke-dasharray="3,4"', "dash": ' stroke-dasharray="9,6"'}.get(dash, "")
    mk = ' marker-end="url(#ah)"' if head else ""
    d = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(pts))
    a(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{sw}"{da}{mk}/>')
    P(dict(t="path", pts=pts, sw=sw, dash=dash, head=head))

def arrow(x1, y1, x2, y2, sw=2, dash=None):
    path([(x1, y1), (x2, y2)], sw, dash)

def hyp(x, y, s, anchor="middle", italic=True):
    text(x, y, s, 20, "bold", anchor=anchor, style="italic" if italic else "normal")

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
    box(x1, TOP, x2 - x1, 58, sw=1.2, fill="#eee",
        lines=[dict(s=s, size=19, bold=True), dict(s=sub, size=17)])
    text((x1 + x2) / 2, TOP + 25, s, 19, "bold", record=False)
    text((x1 + x2) / 2, TOP + 49, sub, 17, record=False)
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
    hyp(ox + ow / 2 + 14, (b + t2) / 2 + 7, h, anchor="start")
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
path([(sx + sw_ / 2, Y0), (sx + sw_ / 2, Y0 - 30), (rx + rw / 2, Y0 - 30), (rx + rw / 2, Y0 - 2)], 1.2, "dot")
box((sx + rx + rw) / 2 - 230, Y0 - 44, 460, 28, stroke=False)
text((sx + rx + rw) / 2, Y0 - 23, "直接效果（中介檢驗用，不列假設）", 18)

# H7：中介效果以大括號標示於 O 構面下方（不另畫路徑）
by, bh, br = Y1 + 10, 24, 12
xm, x1, x2 = ox + ow / 2, ox + 6, ox + ow - 6
a(f'<path d="M{x1},{by} Q{x1},{by + bh / 2} {x1 + br},{by + bh / 2} L{xm - br},{by + bh / 2} '
  f'Q{xm},{by + bh / 2} {xm},{by + bh} Q{xm},{by + bh / 2} {xm + br},{by + bh / 2} '
  f'L{x2 - br},{by + bh / 2} Q{x2},{by + bh / 2} {x2},{by}" fill="none" stroke="#000" stroke-width="1.6"/>')
P(dict(t="brace", x=x1, y=by, w=x2 - x1, h=bh, sw=1.6))
hyp(xm, by + bh + 28, "H7a、H7b：中介效果", italic=False)

# 回饋（循環）路徑：概念說明，不列入檢驗
FB = 960
path([(rx + rw / 2, Y1), (rx + rw / 2, FB), (sx + sw_ / 2, FB), (sx + sw_ / 2, Y1 + 2)], 1.6, "dash")
text((sx + rx + rw) / 2, FB - 14,
     "回饋效果（概念說明，不列入檢驗）：到訪金門、體驗地方文化、現地購買", 18)

# 圖例
lx, ly = 40, 1010
path([(lx, ly), (lx + 50, ly)], 2, head=False)
text(lx + 60, ly + 6, "研究假設路徑", 16, anchor="start")
path([(lx + 200, ly), (lx + 250, ly)], 1.2, "dot", head=False)
text(lx + 260, ly + 6, "直接效果（不列假設）", 16, anchor="start")
path([(lx + 440, ly), (lx + 490, ly)], 1.6, "dash", head=False)
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
(here / "framework_prims.json").write_text(json.dumps(dict(W=W, H=H, prims=prims), ensure_ascii=False), encoding="utf-8")
subprocess.run(["node", str(here / "render.js")], check=True)
# 可編輯的 PowerPoint 版（需要 pptxgenjs、jszip：在此資料夾執行 npm install）
if subprocess.run(["node", str(here / "build_pptx.js")]).returncode:
    print("PPTX 未產生：請先在 research-framework 資料夾執行 npm install")
print("done")
