const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async()=>{const jobs=JSON.parse(process.argv[2]);const b=await chromium.launch();
 const run=async j=>{for(let t=0;t<2;t++){const p=await b.newPage({locale:'ja-JP'});try{const r=await p.goto(j.url,{waitUntil:'domcontentloaded',timeout:90000});await p.waitForTimeout(7000);
   const txt=await p.evaluate(()=>document.body.innerText); const links=await p.evaluate(()=>[...document.querySelectorAll('a[href]')].map(a=>[a.innerText.trim(),a.href]).filter(x=>x[0])); await p.close(); if(r.status()<400 && txt.length>500){require('fs').writeFileSync(j.out,txt);require('fs').writeFileSync(j.out+'.links.json',JSON.stringify(links));return;} }catch(e){await p.close().catch(()=>{});} }
   require('fs').writeFileSync(j.out,'FETCH_FAILED');};
 for(let i=0;i<jobs.length;i+=4) await Promise.all(jobs.slice(i,i+4).map(run));
 await b.close();})();
