#!/usr/bin/env python3
"""銀山溫泉 各旅館官網空房檢查（2 位成人、1 間房、每晚 1 泊）。

用法:
  python3 /root/ginzan-monitor/official.py                 # 預設 2027-01-25 ～ 2027-01-30
  python3 /root/ginzan-monitor/official.py 2027-01-25 2027-01-30

輸出:
  /root/ginzan-monitor/official_last.json  {checked_at, results:[...], hits:[...]}
  /root/ginzan-monitor/official_log.txt    每次 append 一行摘要
status: available | full | not_open | error
全部檢查並行執行，總時限約 170 秒；任何單一網站失敗只記成 error。
"""
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(BASE, 'official_last.json')
OUT_LOG = os.path.join(BASE, 'official_log.txt')
TW = dt.timezone(dt.timedelta(hours=8))
DEADLINE = time.time() + 170

FROM = sys.argv[1] if len(sys.argv) > 1 else '2027-01-25'
TO = sys.argv[2] if len(sys.argv) > 2 else '2027-01-30'
d0, d1 = dt.date.fromisoformat(FROM), dt.date.fromisoformat(TO)
NIGHTS = [d0 + dt.timedelta(days=i) for i in range((d1 - d0).days + 1)]
MONTHS = sorted({(n.year, n.month) for n in NIGHTS})


def R(inn, night, status, detail, url):
    return {'inn': inn, 'night': night.isoformat() if hasattr(night, 'isoformat') else night,
            'status': status, 'detail': detail, 'url': url}


def curl(url, data=None, headers=None, timeout=25):
    """用 curl（走系統代理與 CA），回傳文字。"""
    t = max(5, min(timeout, int(DEADLINE - time.time()) - 5))
    t = min(t, 20)
    cmd = ['curl', '-sS', '-L', '--connect-timeout', '10', '--max-time', str(t), url]
    # 注意：不要加瀏覽器 User-Agent，R-withs 對 Chrome UA 會掛住不回應
    for k, v in (headers or {}).items():
        cmd += ['-H', f'{k}: {v}' if v != '' else f'{k};']
    if data is not None:
        cmd += ['-X', 'POST', '--data-binary', data]
    err = ''
    for attempt in range(3):
        if time.time() > DEADLINE - 10:
            break
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=t + 5)
        except subprocess.TimeoutExpired:
            err = 'timeout'; continue
        if p.returncode == 0:
            return p.stdout.decode('utf-8', 'ignore')
        err = p.stderr.decode('utf-8', 'ignore').strip()[:150] or f'curl rc={p.returncode}'
        time.sleep(1 + attempt)
    raise RuntimeError(err or 'deadline')


def to_text(s):
    s = re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<input[^>]*__VIEWSTATE[^>]*>', '', s)
    t = html.unescape(re.sub(r'<[^>]+>', '\n', s))
    t = re.sub(r'[ \t　]+', ' ', t)
    return re.sub(r'\n\s*\n+', '\n', t)


def safe(fn, inn, url):
    """包裝單一檢查：例外時每晚記成 error。"""
    def run():
        try:
            return fn()
        except Exception as e:  # noqa
            return [R(inn, n, 'error', f'{type(e).__name__}: {str(e)[:150]}', url) for n in NIGHTS]
    return run


# ---------- nj-yoyaku.net（銀山溫泉組合 Web 予約） ----------
NJ = {
    'ginzanso': '仙峡の宿 銀山荘', 'kosekikan': '本館 古勢起屋', 'kosekiya': '古勢起屋 別館',
    'notoya': '能登屋旅館', 'yanadaya': '御宿 やなだ屋', 'takimikan': '滝と蕎麦の宿 瀧見舘',
    'fujiya': '藤屋', 'nagasawa': '旅館 永澤平八', 'itouya': '旅籠 いとうや',
    'kozankaku': '古山閣', 'matsumoto': '旅館 松本', 'showakan': '昭和館',
}


def nj_check(slug):
    inn = NJ[slug] + '（nj-yoyaku）'
    out = []
    for y, m in MONTHS:
        url = f'https://www.nj-yoyaku.net/{slug}/plan.aspx?TDT={y}{m:02d}01&NZ=2'
        t = to_text(curl(url))
        mm = re.search(r'(\d{4})年(\d{2})月\n前月.*?土\n(.*?)\n\s*一室当り', t, re.S)
        if not mm or (int(mm.group(1)), int(mm.group(2))) != (y, m):
            raise RuntimeError('讀不到月曆')
        toks = [x.strip() for x in mm.group(3).split('\n')]
        days, i = {}, 0
        while i < len(toks):
            if toks[i].isdigit():
                d = int(toks[i]); v = toks[i + 1] if i + 1 < len(toks) else ''
                if v.isdigit() and int(v) == d + 1:
                    days[d] = ''; i += 1
                else:
                    days[d] = v; i += 2
            else:
                i += 1
        for n in NIGHTS:
            if (n.year, n.month) != (y, m):
                continue
            v = days.get(n.day)
            if v is None:
                st, det = 'error', '月曆無此日'
            elif v == '×':
                st, det = 'full', 'nj-yoyaku 月曆: ×'
            elif v in ('○', '△') or v.isdigit() or v == '※':
                st, det = 'available', f'nj-yoyaku 月曆: {v}' + ('（※ 意義不明，請手動確認）' if v == '※' else '')
            elif v in ('', '-', '－'):
                st, det = 'not_open', f'nj-yoyaku 月曆: {v or "空白"}'
            else:
                st, det = 'error', f'未知符號 {v}'
            out.append(R(inn, n, st, det, f'https://www.nj-yoyaku.net/{slug}/plan.aspx?TDT={n:%Y%m%d}&NZ=2'))
    return out


# ---------- 藤屋 tabichat ----------
def fujiya():
    inn, page = '藤屋', 'https://tabichat.jp/engine/hotels/fujiyaginzan'
    url = (f'https://tabichat.jp/engine/api/v1/hotels/fujiyaginzan/calendar.json?from_date={d0}'
           f'&to_date={d1}&is_one_day_trip=false&adults=2')
    js = json.loads(curl(url))
    if 'rates' not in js:
        raise RuntimeError('回應沒有 rates')
    rates = {r['date']: r for r in js['rates']}
    limit = dt.date.today() + dt.timedelta(days=150)  # 官網：150 日先まで予約可能
    out = []
    for n in NIGHTS:
        r = rates.get(n.isoformat())
        if r:
            out.append(R(inn, n, 'available', f"tabichat: 2名合計 {r.get('price')}", page))
        elif n > limit:
            out.append(R(inn, n, 'not_open', 'tabichat: 超過 150 日販售期', page))
        else:
            out.append(R(inn, n, 'full', 'tabichat: 該日無可訂方案', page))
    return out


# ---------- 昭和館 liberty-service ----------
SHO_SITE, SHO_FAC = 'cc5f559e549f4f2fac443b9673014a37', 'facility-db690034-b45f-46b5-84d1-3f8ba4b8f522'


def showakan():
    inn = '味とまごころの宿 昭和館'
    page = f'https://site.reservation.liberty-service.com/{SHO_SITE}/{SHO_FAC}/search'
    ci = int((d0 - dt.timedelta(days=1)).strftime('%Y%m%d'))
    co = int((d1 + dt.timedelta(days=2)).strftime('%Y%m%d'))
    guests = [{'personAgeTypeId': pid, 'appDateId': ci, 'restIndex': 0, 'roomGroupIndex': 0,
               'persons': 2 if pid == 1769 else 0, 'femalePersons': 1 if pid == 1769 else 0,
               'malePersons': 1 if pid == 1769 else 0} for pid in (1769, 1767, 1766, 1765, 1764, 1763)]
    body = {'checkInDate': ci, 'checkOutDate': co, 'restNumber': 1, 'roomNumber': 1, 'guestsPerRoom': guests,
            'optionItems': [], 'displayCheckInDate': ci, 'displayCheckOutDate': co, 'dayUse': None}
    txt = curl('https://webapi.site.reservation.liberty-service.com/api/booking/search?api-version=1&page=1&size=2000&enabled=true',
               data=json.dumps(body), headers={'content-type': 'application/json-patch+json', 'accept': 'application/json, text/plain, */*',
                                                'x-site-code': SHO_SITE, 'x-facility-code': SHO_FAC, 'accept-language': 'ja',
                                                'time-zone-offset': '0', 'access_code': '', 'referer': 'https://site.reservation.liberty-service.com/'})
    plans = json.loads(txt)
    per = {}
    for pl in plans:
        if '一人' in pl['name'] or 'ひとり' in pl['name']:
            continue  # 單人方案不適用
        for rm in pl.get('rooms', []):
            if 'シングル' in rm['name']:
                continue
            for a in rm.get('appDatePrices', []):
                per.setdefault(a['appDateId'], []).append((pl['name'], rm['name'], a))
    out = []
    for n in NIGHTS:
        rows = per.get(int(n.strftime('%Y%m%d')), [])
        av = [x for x in rows if x[2]['status'].get('isRoomAvailable') and x[2]['status'].get('isAcceptDate') and (x[2].get('remainNumber') or 0) > 0]
        acc = [x for x in rows if x[2]['status'].get('isAcceptDate')]
        if not rows:
            out.append(R(inn, n, 'error', '回應中無此日資料', page))
        elif av:
            det = '; '.join(f"{p[:20]}/{r[:15]} 残{a['remainNumber']} {a.get('totalPrice') or ''}" for p, r, a in av[:4])
            out.append(R(inn, n, 'available', det, page))
        elif acc:
            out.append(R(inn, n, 'full', '受付中但無剩餘房', page))
        else:
            out.append(R(inn, n, 'not_open', 'isAcceptDate=false（網上尚未開放）；電話 0237-28-2151', page))
    return out


# ---------- 松本 R-withs ----------
def matsumoto():
    inn = '旅館 松本'
    base = 'https://matsumoto.rwiths.net/r-withs/'
    lst = curl(base + 'tfi0010a.do?hotelNo=52933&GCode=&vipCode=&f_lang=ja')
    combos = sorted(set(re.findall(r'otona=2&amp;hotelNo=52933&amp;dataPattern=PL&amp;cdHeyaShu=([A-Za-z0-9]+)&amp;planId=(\d+)', lst)))
    if not combos:
        raise RuntimeError('找不到 2 人房型/方案')
    status = {n: [] for n in NIGHTS}

    def one(room, plan, y, m):
        url = (f'{base}tfi0020a.do?calender={y}{m:02d}01&dataPattern=PL&cdHeyaShu={room}&planId={plan}&hotelNo=52933'
               f'&ciDateY={y}&ciDateM={m:02d}&ciDateD=01&coDateY={y}&coDateM={m:02d}&coDateD=02&otona=2'
               '&s1=0&s2=0&y1=0&y2=0&y3=0&y4=0&room=1&f_lang=ja')
        s = curl(url)
        if f'{y}年{m:02d}月' not in s:
            raise RuntimeError('讀不到日曆')
        cells = {}
        for a, b in re.findall(r'<dt>\s*([0-9/]+)\s*</dt>\s*<dd>(.*?)</dd>', s, re.S):
            if '/' not in a:
                cells[int(a)] = re.sub(r'<[^>]+>|\s+', ' ', b).strip()
        return room, plan, y, m, cells

    with ThreadPoolExecutor(max_workers=4) as ex:
        for room, plan, y, m, cells in ex.map(lambda a: one(*a), [(r, p, y, m) for r, p in combos for y, m in MONTHS]):
            for n in NIGHTS:
                if (n.year, n.month) == (y, m):
                    status[n].append((room, plan, cells.get(n.day)))
    out = []
    for n in NIGHTS:
        rows = status[n]
        av = [r for r in rows if r[2] not in (None, '-', '－', '')]
        if any(r[2] is None for r in rows) and not av:
            out.append(R(inn, n, 'error', '日曆缺此日', base + 'tfs0010a.do'))
        elif av:
            out.append(R(inn, n, 'available', '; '.join(f'{r}號室 plan{p}: {v}' for r, p, v in av), base + 'tfs0010a.do'))
        else:
            out.append(R(inn, n, 'full', f'{len(rows)} 個房型×方案皆「－残室なし」（只接受網路預約）', base + 'tfs0010a.do'))
    return out


# ---------- 宿探し.com（古山閣・クラノバ / いとうや） ----------
YS = {'0046353751453': '古山閣（含クラノバ新館）', '4116550506152': '旅籠 いとうや'}


def yado_sagashi(yid):
    inn = YS[yid]
    idx = f'https://www.yado-sagashi.net/yoyaku/plan/index2.jsp?beg&all&yid={yid}'
    s = curl(idx)
    plans = sorted(set(re.findall(r"open2\('" + yid + r"',(\d+),", s)))
    if not plans:
        if 'お探しのプランは見つかりませんでした' in s:
            return [R(inn, n, 'not_open', '網上無任何方案（只能電話 0237-28-2025）' if 'いとうや' in inn else '網上無任何方案', idx) for n in NIGHTS]
        raise RuntimeError('讀不到方案清單')
    names = {}
    cal = {n: [] for n in NIGHTS}
    for p in plans:
        for y, m in MONTHS:
            url = f'https://www.yado-sagashi.net/yoyaku/plan/plcal.jsp?y={yid}&p={p}&pe=2&in={y}/{m:02d}/01&cmfrm=1'
            t = re.sub(r'\s+', ' ', to_text(curl(url)))
            mm = re.search(rf'{y}年 ?0?{m}月 日 月 火 水 木 金 土 (.*?) 日付', t)
            if not mm:
                raise RuntimeError(f'plan {p} 讀不到日曆')
            cells = dict((int(d), (price, mark)) for d, price, mark in
                         re.findall(r'(?:^| )(\d{1,2}) (-+|[\d,]+円) (×|-+|\d+|○|△)', mm.group(1)))
            for n in NIGHTS:
                if (n.year, n.month) == (y, m):
                    cal[n].append((p, cells.get(n.day)))
    out = []
    for n in NIGHTS:
        rows = cal[n]
        av = [(p, c) for p, c in rows if c and re.fullmatch(r'\d+|○|△', c[1])]
        if av:
            out.append(R(inn, n, 'available', '; '.join(f'plan{p}: 1人{c[0]} 残{c[1]}' for p, c in av), idx))
        elif any(c is None for _, c in rows):
            out.append(R(inn, n, 'error', '日曆缺此日', idx))
        elif any(c[1] == '×' for _, c in rows):
            out.append(R(inn, n, 'full', f'{len(rows)} 方案: ' + ', '.join(f'{p}={c[1]}' for p, c in rows), idx))
        else:
            out.append(R(inn, n, 'not_open', '所有方案「-」部屋提供なし', idx))
    return out


# ---------- 瀏覽器檢查（489pro、永澤平八） ----------
def browser_checks():
    t = int(DEADLINE - time.time()) - 5
    p = subprocess.run(['node', os.path.join(BASE, 'browser_checks.js'), FROM, TO],
                       capture_output=True, timeout=max(30, t))
    line = [l for l in p.stdout.decode('utf-8', 'ignore').splitlines() if l.startswith('[')]
    if not line:
        raise RuntimeError('browser_checks.js 無輸出: ' + p.stderr.decode('utf-8', 'ignore')[-200:])
    return json.loads(line[-1])


def browser_safe():
    try:
        return browser_checks()
    except Exception as e:
        out = []
        for inn, u in [('仙峡の宿 銀山荘', 'ginzanso'), ('本館 古勢起屋', 'kosekikan'), ('古勢起屋 別館', 'kosekiya'),
                       ('能登屋旅館', 'notoyaryokan'), ('御宿 やなだ屋', 'yanadaya'), ('滝と蕎麦の宿 瀧見舘', 'takimikan')]:
            out += [R(inn, n, 'error', f'browser: {str(e)[:120]}', f'https://reserve.489ban.net/client/{u}/0/plan/availability/daily') for n in NIGHTS]
        out += [R('旅館 永澤平八', n, 'error', f'browser: {str(e)[:120]}', 'https://www.hpdsp.net/heihachi/hw/hwp3100/hww3101.do?yadNo=319755') for n in NIGHTS]
        return out


def main():
    t0 = time.time()
    jobs = [browser_safe,
            safe(fujiya, '藤屋', 'https://tabichat.jp/engine/hotels/fujiyaginzan'),
            safe(showakan, '味とまごころの宿 昭和館', f'https://site.reservation.liberty-service.com/{SHO_SITE}/{SHO_FAC}/search'),
            safe(matsumoto, '旅館 松本', 'https://matsumoto.rwiths.net/r-withs/tfs0010a.do')]
    jobs += [safe(lambda y=y: yado_sagashi(y), YS[y], f'https://www.yado-sagashi.net/yoyaku/plan/index2.jsp?beg&all&yid={y}') for y in YS]
    jobs += [safe(lambda s=s: nj_check(s), NJ[s] + '（nj-yoyaku）', f'https://www.nj-yoyaku.net/{s}/plan.aspx?PID=-1') for s in NJ]
    results = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(j) for j in jobs]
        for f in futs:
            try:
                results += f.result(timeout=max(1, DEADLINE - time.time()))
            except Exception as e:
                results.append(R('（某項檢查）', '-', 'error', f'逾時或失敗: {e}', ''))
    results.sort(key=lambda r: (r['inn'], r['night']))
    hits = [r for r in results if r['status'] == 'available']
    for h in hits:  # 直接訂房連結（帶入日期）
        u, n = h.get('url', ''), h.get('night', '')
        try:
            d = dt.date.fromisoformat(n)
        except Exception:
            d = None
        bu = u
        m = re.search(r'reserve\.489ban\.net/client/([^/]+)/', u) if d else None
        if m:
            bu = f"https://reserve.489ban.net/client/{m.group(1)}/0/plan/search?date={d:%Y}%2F{d:%m}%2F{d:%d}&roomCount=1"
        elif d and 'nj-yoyaku.net' in u:
            bu = re.sub(r'plan\.aspx.*$', f'plan.aspx?TDT={d:%Y%m%d}&NZ=2', u)
        h['book_url'] = bu
    now = dt.datetime.now(TW).strftime('%Y-%m-%d %H:%M:%S +08:00')
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({'checked_at': now, 'range': [FROM, TO], 'results': results, 'hits': hits}, f, ensure_ascii=False, indent=1)
    cnt = {k: sum(r['status'] == k for r in results) for k in ('available', 'full', 'not_open', 'error')}
    hit_s = '; '.join(f"{h['inn']} {h['night']} {h['detail'][:40]}" for h in hits[:10]) or '無'
    line = (f"{now} | {FROM}~{TO} | available={cnt['available']} full={cnt['full']} not_open={cnt['not_open']} "
            f"error={cnt['error']} | {time.time() - t0:.0f}s | hits: {hit_s}")
    with open(OUT_LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    print(line)
    # 以旅館為單位列出狀態
    by = {}
    for r in results:
        by.setdefault(r['inn'], []).append(r['status'])
    for inn, sts in by.items():
        print(f'  {inn}: ' + ' '.join(s[:5] for s in sts))
    return 0


if __name__ == '__main__':
    sys.exit(main())
