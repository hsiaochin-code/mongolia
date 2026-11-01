// 用法: node /root/trip-plan/tools/page.js "<url>" /path/out.txt [waitMs] [locale]
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async()=>{const [,,url,out,wait='7000',loc='ja-JP']=process.argv;const b=await chromium.launch();
for(let t=0;t<2;t++){const p=await b.newPage({locale:loc,viewport:{width:1300,height:3000}});
 try{const r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:90000});await p.waitForTimeout(+wait);
  const txt=await p.evaluate(()=>document.body.innerText); if(r.status()<500 && txt.length>300){require('fs').writeFileSync(out,txt);console.log('OK',r.status(),txt.length);await b.close();return;}}catch(e){console.log('ERR',e.message.slice(0,120));}
 await p.close();}
require('fs').writeFileSync(out,'FETCH_FAILED');console.log('FAILED');await b.close();})();
