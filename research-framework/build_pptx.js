// 讀取 build.py 產生的 framework_prims.json，輸出可編輯的 PowerPoint 架構圖（原生圖形與文字方塊）
const pptxgen = require('pptxgenjs');
const JSZip = require('jszip');
const fs = require('fs'), path = require('path');

const { W, H, CM, prims } = JSON.parse(fs.readFileSync(path.join(__dirname, 'framework_prims.json'), 'utf8'));
const k = CM / 2.54;                // 像素 → 英吋（1 px = 0.01 cm）
const pt = px => +(px * k * 72).toFixed(1);   // 像素 → 點
const LATIN = 'Times New Roman', EA = '標楷體';

const pres = new pptxgen();
pres.defineLayout({ name: 'FIG', width: +(W * k).toFixed(3), height: +(H * k).toFixed(3) });
pres.layout = 'FIG';
pres.title = '研究架構圖';
const slide = pres.addSlide();
slide.background = { color: 'FFFFFF' };

// 粗估字串寬度（中日文全形約 1 字高，半形約 0.55 字高）
const textW = (s, size) => [...s].reduce((w, ch) => w + (ch.charCodeAt(0) > 0x2e80 ? size : size * 0.55), 0);

for (const p of prims) {
  if (p.t === 'rect') {
    const opts = {
      shape: pres.shapes.RECTANGLE, x: p.x * k, y: p.y * k, w: p.w * k, h: p.h * k,
      fill: { color: 'FFFFFF' },
      line: { color: '000000', width: pt(p.sw), ...(p.dash ? { dashType: 'dash' } : {}) },
      align: 'center', valign: 'middle', margin: 0, fontFace: LATIN, color: '000000',
    };
    if (p.lines.length) {
      slide.addText(p.lines.map((l, i) => ({
        text: l.s,
        options: { fontSize: pt(l.size), bold: !!l.bold, italic: !!l.italic, breakLine: i < p.lines.length - 1 },
      })), opts);
    } else {
      slide.addShape(pres.shapes.RECTANGLE, opts);
    }
  } else if (p.t === 'text') {
    const w = textW(p.s, p.size) * 1.08 + 12, h = p.size * 1.5;
    const x = p.anchor === 'start' ? p.x - 2 : p.x - w / 2;
    const y = p.y - p.size * 0.35 - h / 2;
    slide.addText(p.s, {
      x: x * k, y: y * k, w: w * k, h: h * k, margin: 0, isTextBox: true,
      align: p.anchor === 'start' ? 'left' : 'center', valign: 'middle',
      fontFace: LATIN, fontSize: pt(p.size), bold: p.bold, italic: p.italic, color: '000000',
    });
  } else if (p.t === 'path') {
    const segs = p.pts.slice(1).map((q, i) => [p.pts[i], q]);
    segs.forEach(([[x1, y1], [x2, y2]], i) => {
      const line = { color: '000000', width: pt(p.sw) };
      if (p.head && i === segs.length - 1) line.endArrowType = 'triangle';
      slide.addShape(pres.shapes.LINE, {
        x: Math.min(x1, x2) * k, y: Math.min(y1, y2) * k,
        w: Math.abs(x2 - x1) * k, h: Math.abs(y2 - y1) * k,
        flipH: x2 < x1, flipV: y2 < y1, line,
      });
    });
  } else if (p.t === 'brace') {
    // 右大括號旋轉 90°：開口朝上、尖端朝下
    const cx = p.x + p.w / 2, cy = p.y + p.h / 2;
    slide.addShape(pres.shapes.RIGHT_BRACE, {
      x: (cx - p.h / 2) * k, y: (cy - p.w / 2) * k, w: p.h * k, h: p.w * k, rotate: 90,
      line: { color: '000000', width: pt(p.sw) },
    });
  }
}

(async () => {
  // pptxgenjs 會把同一字型寫進 latin 與 ea；改成中文用標楷體、英數用 Times New Roman
  const buf = await pres.write({ outputType: 'nodebuffer' });
  const zip = await JSZip.loadAsync(buf);
  const f = 'ppt/slides/slide1.xml';
  let xml = await zip.file(f).async('string');
  xml = xml.replace(new RegExp(`<a:ea typeface="${LATIN}"`, 'g'), `<a:ea typeface="${EA}"`)
    .replace(/(<a:ea typeface="標楷體" pitchFamily="\d+") charset="-122"/g, '$1 charset="-120"');  // Big5
  zip.file(f, xml);
  // 只複製檔案、不寫入資料夾項目，避免雲端硬碟開啟失敗
  const clean = new JSZip();
  for (const n of Object.keys(zip.files).filter(n => !zip.files[n].dir)) {
    clean.file(n, await zip.file(n).async('nodebuffer'), { createFolders: false });
  }
  const out = path.join(__dirname, 'research_framework.pptx');
  fs.writeFileSync(out, await clean.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }));
  console.log('wrote', out);
})();
