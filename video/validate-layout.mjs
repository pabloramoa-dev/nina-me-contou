import puppeteer from 'puppeteer-core';
import {execFileSync} from 'node:child_process';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {writeFileSync} from 'node:fs';
const dir=resolve(process.argv[2]);
const chrome=execFileSync('node',[new URL('./node_modules/hyperframes/bin/hyperframes.mjs',import.meta.url).pathname,'browser','path'],{encoding:'utf8'}).trim().split('\n').at(-1);
const browser=await puppeteer.launch({executablePath:chrome,headless:true,args:['--no-sandbox','--allow-file-access-from-files']});
try {
  const page=await browser.newPage();
  await page.setViewport({width:1080,height:1920,deviceScaleFactor:1});
  await page.goto(pathToFileURL(dir+'/index.html').href,{waitUntil:'load'});
  await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(im=>im.decode()));});
  const result=await page.evaluate(()=>{
    const tl=window.__timelines['nina-hf'],clips=[...document.querySelectorAll('.clip')],errors=[];
    const rect=e=>e.getBoundingClientRect();
    const overlap=(a,b)=>a.left<b.right-.1&&a.right>b.left+.1&&a.top<b.bottom-.1&&a.bottom>b.top+.1;
    let samples=0,imageSamples=0;
    for(const panel of document.querySelectorAll('.panel')){
      const start=+panel.dataset.start,duration=+panel.dataset.duration;
      for(const offset of [.06,.15,.3,.55,1,duration/2,duration-.05]){
        if(offset>=duration)continue;
        const t=start+offset;tl.seek(t,false);samples++;
        for(const el of clips){const a=+el.dataset.start;el.style.visibility=t>=a&&t<a+(+el.dataset.duration)?'visible':'hidden';}
        const caps=[...document.querySelectorAll('.caps')].filter(e=>e.style.visibility==='visible');
        if(caps.length>1)errors.push({t,problem:'duplicate_caption'});
        if(panel.dataset.template==='story_frame_image'){
          const im=panel.querySelector('.art img');imageSamples++;
          if(!im?.naturalWidth)errors.push({t,problem:'missing_image'});
          if(panel.querySelector('.bubble,.note,.wave,.underline'))errors.push({t,problem:'inner_text'});
          if(im){
            if(overlap(rect(im),rect(panel.querySelector('h1 .ink')||panel.querySelector('h1'))))errors.push({t,problem:'image_title_overlap'});
            for(const c of caps)if(overlap(rect(im),rect(c)))errors.push({t,problem:'image_caption_overlap'});
          }
        }
      }
    }
    return {samples,imageSamples,errors};
  });
  writeFileSync(dir+'/layout-check.json',JSON.stringify(result,null,2));
  console.log(JSON.stringify(result));
  if(result.errors.length)process.exitCode=1;
} finally {await browser.close();}
