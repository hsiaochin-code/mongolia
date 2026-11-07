import json, re, subprocess, datetime, os, sys
D='/root/ginzan-monitor'; os.makedirs(D+'/raw',exist_ok=True)
NIGHTS=[25,26,27,28,29,30]
KNOWN_OUTSIDE=['虹の館','最上屋','花笠高原荘']   # 不在溫泉街上的住宿
GINZAN=['能登屋','古勢起屋','銀山荘','瀧見館','滝見館','昭和館','永澤平八','永沢平八','藤屋','いとうや','やなだ屋','松本','古山閣','クラノバ','酒田屋','玉ノ湯','ゆさや','遊佐屋','仙峡']

def direct_link(src,name,d,links):
    """回傳該旅館自己的訂房頁（已帶入日期、2 大人）；找不到回 None"""
    for t,h in links:
        if name not in t.split('\n')[0]: continue
        if src=='じゃらん':
            m=re.search(r'jalan\.net/(yad\d+)/',h)
            if m: return f'https://www.jalan.net/{m.group(1)}/plan/?stayYear=2027&stayMonth=1&stayDay={d}&stayCount=1&roomCount=1&adultNum=2'
        else:
            m=re.search(r'/HOTEL/(\d+)/',h) or re.search(r'hotelinfo/plan/(\d+)',h)
            if m: return f'https://hotel.travel.rakuten.co.jp/hotelinfo/plan/{m.group(1)}?f_nen1=2027&f_tuki1=1&f_hi1={d}&f_nen2=2027&f_tuki2=1&f_hi2={d+1}&f_heya_su=1&f_otona_su=2'
    return None
jobs=[]
for d in NIGHTS:
    jobs.append({'url':f'https://www.jalan.net/060000/LRG_060500/SML_060502/?stayYear=2027&stayMonth=1&stayDay={d}&stayCount=1&roomCount=1&adultNum=2','out':f'{D}/raw/jl{d}.txt'})
    jobs.append({'url':f'https://search.travel.rakuten.co.jp/ds/hotellist/Japan-Yamagata-Obanazawa?f_nen1=2027&f_tuki1=1&f_hi1={d}&f_nen2=2027&f_tuki2=1&f_hi2={d+1}&f_heya_su=1&f_otona_su=2','out':f'{D}/raw/rk{d}.txt'})
subprocess.run(['node',D+'/fetch.js',json.dumps(jobs)],timeout=900)
res={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M'),'nights':{},'failed':[],'ginzan_hits':[]}
for d in NIGHTS:
    names=set()
    for src,fn in (('じゃらん',f'{D}/raw/jl{d}.txt'),('楽天',f'{D}/raw/rk{d}.txt')):
        t=open(fn,encoding='utf-8').read()
        if t=='FETCH_FAILED' or ('軒ありました' not in t and '件中' not in t and 'ございません' not in t and '見つかりません' not in t):
            res['failed'].append(f'1/{d} {src}'); continue
        L=[l.strip() for l in t.split('\n') if l.strip()]
        if src=='じゃらん':
            found=[L[i+1] for i,l in enumerate(L) if 'エリア： 山形県' in l and i+1<len(L)]
        else:
            found=[L[i-1] for i,l in enumerate(L) if re.match(r'^\d\.\d\d（\d+件）',l) and i>0]
        try: LK=json.load(open(fn+'.links.json',encoding='utf-8'))
        except Exception: LK=[]
        for n in found:
            names.add((src,n))
            hotel_url=direct_link(src,n,d,LK)
            if not any(k in n for k in KNOWN_OUTSIDE):
                res['ginzan_hits'].append({'night':f'1/{d}','source':src,'name':n,
                   'hotel_url':hotel_url,
                   'url':(f'https://www.jalan.net/060000/LRG_060500/SML_060502/?stayYear=2027&stayMonth=1&stayDay={d}&stayCount=1&roomCount=1&adultNum=2' if src=='じゃらん' else f'https://search.travel.rakuten.co.jp/ds/hotellist/Japan-Yamagata-Obanazawa?f_nen1=2027&f_tuki1=1&f_hi1={d}&f_nen2=2027&f_tuki2=1&f_hi2={d+1}&f_heya_su=1&f_otona_su=2')})
    res['nights'][f'1/{d}']=sorted({n for _,n in names})
json.dump(res,open(D+'/last.json','w'),ensure_ascii=False,indent=1)
with open(D+'/log.txt','a') as f: f.write(json.dumps({'t':res['checked_at'],'hits':len(res['ginzan_hits']),'failed':res['failed']},ensure_ascii=False)+'\n')
print(json.dumps(res,ensure_ascii=False,indent=1))
