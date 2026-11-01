// 需要瀏覽器 session 的檢查：489pro 日曆、永澤平八 (hpdsp.net)
// 用法: node browser_checks.js 2027-01-25 2027-01-30   -> stdout 輸出 JSON 陣列
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');

const [, , FROM = '2027-01-25', TO = '2027-01-30'] = process.argv;
const nights = [];
for (let d = new Date(FROM + 'T00:00:00Z'); d <= new Date(TO + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + 1))
  nights.push(d.toISOString().slice(0, 10));
const months = [...new Set(nights.map(n => n.slice(0, 7)))];

const C489 = {
  ginzanso: '仙峡の宿 銀山荘', kosekikan: '本館 古勢起屋', kosekiya: '古勢起屋 別館',
  notoyaryokan: '能登屋旅館', yanadaya: '御宿 やなだ屋', takimikan: '滝と蕎麦の宿 瀧見舘',
};
const out = [];
const push = (inn, night, status, detail, url) => out.push({ inn, night, status, detail, url });

async function check489(browser, client, idx = 0) {
  const inn = C489[client];
  await new Promise(r => setTimeout(r, idx * 2500)); // 錯開，避免 489ban 429/502
  const url = `https://reserve.489ban.net/client/${client}/0/plan/availability/daily`;
  const p = await browser.newPage({ locale: 'ja-JP' });
  try {
    await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await p.waitForTimeout(2500);
    const marks = {};
    for (const ym of months) {
      const [y, m] = ym.split('-').map(Number);
      let r = [0, ''];
      for (let a = 0; a < 4; a++) {
        r = await p.evaluate(async ([y, m]) => {
          const x = await fetch(`./dailycalendar?year=${y}&month=${m}&planType=1&_=${Date.now()}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
          return [x.status, await x.text()];
        }, [y, m]);
        if (r[0] === 200) break;
        await p.waitForTimeout(2000 + 2000 * a);
      }
      if (r[0] !== 200) throw new Error('dailycalendar HTTP ' + r[0]);
      const re = /class=\\?"(20\d\d-\d\d-\d\d)\\?">([\s\S]*?)<\\?\/p>/g; let mm;
      while ((mm = re.exec(r[1]))) {
        const ic = (mm[2].match(/fa-(circle|triangle-exclamation|xmark|minus)/) || [])[1];
        marks[mm[1]] = ic || 'unknown';
      }
    }
    for (const n of nights) {
      const v = marks[n];
      const st = !v ? 'error' : (v === 'circle' || v === 'triangle-exclamation') ? 'available' : v === 'xmark' ? 'full' : v === 'minus' ? 'not_open' : 'error';
      push(inn, n, st, v ? `489pro 日曆: ${v === 'circle' ? '○空室あり' : v === 'triangle-exclamation' ? '△残りわずか' : v === 'xmark' ? '×満室' : v === 'minus' ? '－受付不可' : v}` : '日曆無此日', url);
    }
  } catch (e) {
    for (const n of nights) push(inn, n, 'error', '489pro: ' + e.message.slice(0, 120), url);
  } finally { await p.close().catch(() => {}); }
}

async function checkHeihachi(browser) {
  const inn = '旅館 永澤平八';
  const listUrl = 'https://www.hpdsp.net/heihachi/hw/hwp3100/hww3101.do?yadNo=319755';
  const p = await browser.newPage({ locale: 'ja-JP' });
  const res = {}; // night -> [{plan, val}]
  try {
    await p.goto(listUrl, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await p.waitForTimeout(2500);
    let planUrls = await p.evaluate(() => [...new Set([...document.querySelectorAll('a')].map(a => a.href).filter(h => h.includes('hww3201init')))]);
    planUrls = planUrls.map(u => u.replace(/adultNum=\d+/, 'adultNum=2').replace(/roomCrack=\d+/, 'roomCrack=200000'));
    if (!planUrls.length) throw new Error('找不到方案連結');
    for (const pu of planUrls) {
      await p.goto(pu, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await p.waitForTimeout(2500);
      const pending = new Set(months);
      for (let i = 0; i < 8 && pending.size; i++) {
        const t = await p.evaluate(() => document.body.innerText);
        const m = t.match(/(\d{4})年(\d+)月[\s\S]*?月\s+火\s+水\s+木\s+金\s+土\s+日([\s\S]*?)予約受付は/);
        if (!m) throw new Error('讀不到日曆');
        const ym = `${m[1]}-${String(m[2]).padStart(2, '0')}`;
        if (pending.has(ym)) {
          pending.delete(ym);
          // 解析 "日 值" ; 值可能是 "-", "50,600 他プランを探す", "50,600 残1", 或空白(未販售)
          const toks = m[3].split('\n').map(s => s.trim()).filter(Boolean);
          const days = {};
          for (let k = 0; k < toks.length; k++) {
            if (/^\d{1,2}$/.test(toks[k])) {
              const d = +toks[k]; const nx = toks[k + 1] || '';
              if (nx === '-' || /^[\d,]+$/.test(nx) && !(+nx === d + 1 && nx.length <= 2)) {
                let val = nx; if (/^[\d,]+$/.test(nx) && toks[k + 2] && !/^\d{1,2}$/.test(toks[k + 2])) val += ' ' + toks[k + 2];
                days[d] = val;
              } else days[d] = '';
            }
          }
          for (const n of nights.filter(n => n.startsWith(ym))) {
            (res[n] = res[n] || []).push({ plan: pu.match(/planCd=(\d+)/)?.[1], val: days[+n.slice(8)] ?? '' });
          }
        }
        if (!pending.size) break;
        const links = p.locator('a', { hasText: /^\s*\d+月\s*$/ });
        if (!(await links.count())) throw new Error('無法翻到下個月');
        await links.last().click(); await p.waitForTimeout(2500);
      }
    }
    for (const n of nights) {
      const arr = res[n] || [];
      const av = arr.filter(a => /[\d,]{4,}/.test(a.val));
      const full = arr.filter(a => a.val === '-');
      const st = !arr.length ? 'error' : av.length ? 'available' : full.length ? 'full' : 'not_open';
      const detail = 'hpdsp 方案日曆: ' + arr.map(a => `${a.plan}=${a.val || '空白(未販售)'}`).join(', ') +
        (st === 'not_open' ? '；官網：3か月前の1日から電話受付 0237-28-2137' : '');
      push(inn, n, st, detail, listUrl);
    }
  } catch (e) {
    for (const n of nights) push(inn, n, 'error', 'hpdsp: ' + e.message.slice(0, 120), listUrl);
  } finally { await p.close().catch(() => {}); }
}

(async () => {
  const browser = await chromium.launch();
  const killer = setTimeout(() => { console.log(JSON.stringify(out)); process.exit(0); }, 140000);
  await Promise.all([...Object.keys(C489).map((c, i) => check489(browser, c, i)), checkHeihachi(browser)]);
  clearTimeout(killer);
  console.log(JSON.stringify(out));
  await browser.close();
})();
