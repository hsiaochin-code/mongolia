// 將 research_framework.svg 輸出為 PNG（2x）與 PDF
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const svg = fs.readFileSync(path.join(__dirname, 'research_framework.svg'), 'utf8');
  const [W, H] = [1800, 1210];
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 2 });
  await pg.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  await pg.screenshot({ path: path.join(__dirname, 'research_framework.png') });
  await pg.pdf({ path: path.join(__dirname, 'research_framework.pdf'), width: W + 'px', height: H + 'px', printBackground: true, pageRanges: '1' });
  await b.close();
})();
