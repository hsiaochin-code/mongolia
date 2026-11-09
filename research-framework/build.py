"""產生正式論文用研究架構圖：SVG（16 cm 寬，可直接插入 Word）、PNG、PDF，另輸出可編輯的 PPTX。

設計原則（正式論文格式）：
- 以實際版面尺寸設計：1 px = 0.01 cm，全圖寬 16 cm，插入 Word 後字級約 10 pt，與內文比例一致。
- 只畫構面與研究假設路徑；圖名、資料來源、中介路徑說明等文字放在 Word 的圖說，
  以便用「插入標號」自動編號並產生圖目錄。
- 黑白單色、線條粗細一致；中文標楷體、英數 Times New Roman。
"""
import json
import pathlib
import subprocess

W, H = 1600, 730          # 1 px = 0.01 cm → 16 cm × 7.3 cm
CM = 0.01
FONT = "'Times New Roman','Liberation Serif','DFKai-SB','標楷體','BiauKai','TW-Kai',serif"

FS_TITLE, FS_SUB, FS_ITEM, FS_HYP, FS_STAGE = 38, 32, 35, 34, 34   # ≈10.8 / 9 / 10 / 9.6 / 9.6 pt
SW_BOX, SW_ITEM, SW_ARROW = 3.5, 2.5, 3                             # ≈1 / 0.7 / 0.85 pt

out, prims = [], []
a, P = out.append, prims.append


def text(x, y, s, size, bold=False, italic=False, anchor="middle", record=True):
    a(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{"bold" if bold else "normal"}" '
      f'font-style="{"italic" if italic else "normal"}" text-anchor="{anchor}">{s}</text>')
    if record:
        P(dict(t="text", x=x, y=y, s=s, size=size, bold=bold, italic=italic, anchor=anchor))


def box(x, y, w, h, sw, dash=False, lines=None):
    d = ' stroke-dasharray="14,9"' if dash else ""
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#000" stroke-width="{sw}"{d}/>')
    P(dict(t="rect", x=x, y=y, w=w, h=h, sw=sw, dash=dash, lines=lines or []))


def path(pts, sw=SW_ARROW, head=True):
    d = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(pts))
    mk = ' marker-end="url(#ah)"' if head else ""
    a(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{sw}"{mk}/>')
    P(dict(t="path", pts=pts, sw=sw, head=head))


def hyp(x, y, s, anchor="middle"):
    text(x, y, s, FS_HYP, bold=True, italic=True, anchor=anchor)


a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * CM}cm" height="{H * CM}cm" '
  f'viewBox="0 0 {W} {H}" font-family="{FONT}">')
a('<defs><marker id="ah" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto">'
  '<path d="M0,0 L10,4 L0,8 z" fill="#000"/></marker></defs>')
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')

# ---- 版面 ----
Y0, Y1 = 80, 620                    # 構面框上下緣
HEAD = 112                          # 構面標題區高度
IH = 72                             # 面向方框高度
cols = {                            # x, 寬度
    "D": (10, 290),
    "S": (410, 320),
    "O": (840, 320),
    "R": (1270, 320),
}


def construct(key, name, role, items, dash=False, pad=22):
    x, w = cols[key]
    box(x, Y0, w, Y1 - Y0, SW_BOX, dash=dash)
    text(x + w / 2, Y0 + 46, name, FS_TITLE, bold=True)
    text(x + w / 2, Y0 + 88, role, FS_SUB)
    top, bot = Y0 + HEAD, Y1 - 22
    gap = (bot - top - len(items) * IH) / (len(items) + 1)
    pos = []
    for i, s in enumerate(items):
        y = top + gap * (i + 1) + IH * i
        box(x + pad, y, w - 2 * pad, IH, SW_ITEM, lines=[dict(s=s, size=FS_ITEM)])
        text(x + w / 2, y + IH / 2 + FS_ITEM * 0.36, s, FS_ITEM, record=False)
        pos.append((y, y + IH))
    return pos


# ---- 旅遊歷程階段標示（頂端括線） ----
def stage(x1, x2, label):
    text((x1 + x2) / 2, 34, label, FS_STAGE)
    path([(x1, 62), (x1, 50), (x2, 50), (x2, 62)], sw=2, head=False)


stage(cols["D"][0], cols["S"][0] + cols["S"][1], "旅前階段")
stage(cols["O"][0], cols["O"][0] + cols["O"][1], "旅中階段")
stage(cols["R"][0], cols["R"][0] + cols["R"][1], "旅後階段")

# ---- 構面 ----
construct("D", "數位接觸管道", "前置變數", ["網路資訊", "社群媒體", "電商平台"])
construct("S", "食品紀念品刺激", "刺激（S）", ["吸引力", "地方特色", "文化故事", "品牌形象"])
# O 不是單一構面，而是三個中介變數的組合 → 以虛線框表示
op = construct("O", "旅客心理歷程", "有機體（O）", ["真實性感知", "地方興趣", "地方依附"], dash=True)
rp = construct("R", "後續行為意圖", "反應（R）", ["推薦意圖", "回購意圖", "再訪意圖"])

# ---- 研究假設路徑 ----
(dx, dw), (sx, sw), (ox, ow), (rx, rw) = cols["D"], cols["S"], cols["O"], cols["R"]
ix1, ix2, ocx = ox + 22, ox + ow - 22, ox + ow / 2
mid = (Y0 + HEAD + Y1) / 2
pa_c, patt_c = sum(op[0]) / 2, sum(op[2]) / 2
r_up, r_dn = (rp[0][1] + rp[1][0]) / 2, (rp[1][1] + rp[2][0]) / 2

path([(dx + dw, mid), (sx, mid)]);            hyp((dx + dw + sx) / 2, mid - 16, "H1")
path([(sx + sw, pa_c), (ix1, pa_c)]);         hyp((sx + sw + ix1) / 2, pa_c - 16, "H2")
for (t, b), (t2, _), h in zip(op, op[1:], ["H3", "H4"]):
    path([(ocx, b), (ocx, t2)]);              hyp(ocx + 14, (b + t2) / 2 + 12, h, anchor="start")
path([(ix2, pa_c), (rx, r_up)]);              hyp((ix2 + rx) / 2 + 10, (pa_c + r_up) / 2 - 20, "H6")
path([(ix2, patt_c), (rx, r_dn)]);            hyp((ix2 + rx) / 2 + 10, (patt_c + r_dn) / 2 + 46, "H5")

# ---- H7：中介效果（大括號） ----
by, bh, br = Y1 + 12, 26, 14
x1, x2, xm = ox + 8, ox + ow - 8, ox + ow / 2
a(f'<path d="M{x1},{by} Q{x1},{by + bh / 2} {x1 + br},{by + bh / 2} L{xm - br},{by + bh / 2} '
  f'Q{xm},{by + bh / 2} {xm},{by + bh} Q{xm},{by + bh / 2} {xm + br},{by + bh / 2} '
  f'L{x2 - br},{by + bh / 2} Q{x2},{by + bh / 2} {x2},{by}" fill="none" stroke="#000" stroke-width="2.5"/>')
P(dict(t="brace", x=x1, y=by, w=x2 - x1, h=bh, sw=2.5))
text(xm, by + bh + 38, "H7a、H7b（中介效果）", FS_SUB)
a("</svg>")

here = pathlib.Path(__file__).parent
(here / "research_framework.svg").write_text("\n".join(out), encoding="utf-8")
(here / "framework_prims.json").write_text(json.dumps(dict(W=W, H=H, CM=CM, prims=prims), ensure_ascii=False),
                                           encoding="utf-8")
subprocess.run(["node", str(here / "render.js")], check=True)
# 可編輯的 PowerPoint 版（需要 pptxgenjs、jszip：在此資料夾執行 npm install）
if subprocess.run(["node", str(here / "build_pptx.js")]).returncode:
    print("PPTX 未產生：請先在 research-framework 資料夾執行 npm install")
print("done")
