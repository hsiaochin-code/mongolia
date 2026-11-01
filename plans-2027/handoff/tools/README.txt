查詢工具（Chromium 已信任代理 CA，不要關 TLS 驗證）：
node /root/trip-plan/tools/page.js "<url>" <輸出.txt> [等待毫秒] [語系]
- じゃらん 地區空房（2 位成人、1 晚）：
  https://www.jalan.net/<縣碼>/LRG_<大區>/SML_<小區>/?stayYear=2027&stayMonth=1&stayDay=<日>&stayCount=1&roomCount=1&adultNum=2
  例：尾花沢・銀山 = /060000/LRG_060500/SML_060502/。結果頁文字有「N 軒ありました」，每間宿名在「エリア： 山形県 > …」的下一行，方案行有「あとN部屋」、合計(税込)。
  地區代碼可用 WebSearch「じゃらん <地名> SML_」或「jalan.net ranking <地名>」找。
- 楽天トラベル 地區空房：
  https://search.travel.rakuten.co.jp/ds/hotellist/<Japan-縣-地區>?f_nen1=2027&f_tuki1=1&f_hi1=<日>&f_nen2=2027&f_tuki2=1&f_hi2=<日+1>&f_heya_su=1&f_otona_su=2
  例：Japan-Yamagata-Obanazawa。結果有「N件中」、「残りN部屋」；「ご利用日に空室のない宿泊施設は表示しておりません」＝只列出有空房的。
- Google 飯店（台幣）：https://www.google.com/travel/search?hl=zh-TW&gl=TW&curr=TWD&q=<地名> hotels Jan 25 2027 to Jan 26 2027 2 adults
- Google Flights 與其他網站可用 WebSearch / WebFetch 交叉確認。部分網站（Trip.com、Skyscanner、Kayak、長榮、虎航）會擋機器人，不要嘗試繞過。
