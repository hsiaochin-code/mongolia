// 將 research_framework.svg 輸出為 PNG（約 600 dpi）與 PDF（實際尺寸 16 cm 寬）
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const { W, H, CM } = JSON.parse(fs.readFileSync(path.join(__dirname, 'framework_prims.json'), 'utf8'));
  const svg = fs.readFileSync(path.join(__dirname, 'research_framework.svg'), 'utf8')
    .replace(/width="[\d.]+cm" height="[\d.]+cm"/, `width="${W}" height="${H}"`);
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 2.4 });
  await pg.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  await pg.screenshot({ path: path.join(__dirname, 'research_framework.png') });
  const cm = v => `${(v * CM).toFixed(2)}cm`;
  await pg.setContent(`<html><head><style>@page{size:${cm(W)} ${cm(H)};margin:0}body{margin:0}
    svg{width:${cm(W)};height:${cm(H)};display:block}</style></head><body>${svg}</body></html>`);
  await pg.pdf({ path: path.join(__dirname, 'research_framework.pdf'), preferCSSPageSize: true, printBackground: true, pageRanges: '1' });
  await b.close();
})();
