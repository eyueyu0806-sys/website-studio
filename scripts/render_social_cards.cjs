/* Optional artwork renderer: use an installed Playwright module and Chromium.
   Runtime publishing uses only Python's standard library and the rendered JPEGs. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const posts = JSON.parse(fs.readFileSync(path.join(root, 'business/marketing/social-posts.json')));
const font = fs.readFileSync(path.join(root, 'assets/fonts/studio-serif.woff')).toString('base64');
const esc = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');

function sheet(post) {
  const c = post.card;
  if (!c || !['notes', 'steps', 'comparison', 'checklist'].includes(c.layout) || c.points.length !== 3) throw new Error('Invalid card: ' + post.id);
  const rows = c.points.map((p, i) => `<div class="point"><span class="num">${String(i+1).padStart(2,'0')}</span><div><h2>${esc(p.label)}</h2><p>${esc(p.text)}</p></div></div>`).join('');
  return `<!doctype html><html lang="ja"><meta charset="utf-8"><style>
  @font-face{font-family:Atelier;src:url(data:font/woff;base64,${font})}*{box-sizing:border-box}
  body{margin:0;background:#fff;color:#111;font-family:"Noto Sans CJK JP",system-ui,sans-serif}
  .sheet{width:1080px;height:1350px;padding:72px 74px;position:relative;overflow:hidden;background:#fff}
  .top{display:flex;align-items:center;justify-content:space-between;font-size:25px;border-bottom:1px solid #b9beb7;padding-bottom:24px}
  .brand{display:flex;align-items:center;gap:18px}.mark{display:block;width:35px;height:35px;position:relative}
  .mark:before,.mark:after{content:'';position:absolute;width:24px;height:24px;border:3px solid #526657}
  .mark:before{top:0;left:0;border-right:0;border-bottom:0}.mark:after{right:0;bottom:0;border-left:0;border-top:0}
  .topic{font-size:25px;color:#526657;letter-spacing:.1em;margin:46px 0 24px}.title-frame{position:relative;padding:25px 0 26px 26px}
  .title-frame:before{content:'';position:absolute;left:0;top:0;width:88px;height:88px;border-top:3px solid #526657;border-left:3px solid #526657}
  h1{font-family:Atelier,serif;font-size:77px;font-weight:500;line-height:1.38;letter-spacing:-.04em;margin:0;white-space:normal}
  .summary{font-size:30px;line-height:1.6;margin:24px 0 38px;color:#5a5a54}
  .points{border-top:1px solid #b9beb7}.point{display:grid;grid-template-columns:64px 1fr;gap:10px;padding:24px 0;border-bottom:1px solid #b9beb7}
  .num{font-size:24px;color:#526657;padding-top:8px;font-variant-numeric:tabular-nums}h2{font-size:40px;font-weight:500;line-height:1.45;margin:0 0 9px}
  .point p{font-size:36px;line-height:1.55;margin:0;color:#45453f}.bottom{position:absolute;bottom:64px;left:74px;right:74px;border-top:1px solid #b9beb7;padding-top:22px;display:flex;justify-content:space-between;font-size:24px;color:#5a5a54}
  .steps .point{border-bottom:0;position:relative;padding:22px 0 22px 12px}.steps .points{border-top:0;border-left:2px solid #526657;padding-left:22px}
  .steps .num{border-top:1px solid #526657}.comparison{background:#F4F4F0}.comparison .points{border:0}.comparison .point{grid-template-columns:1fr 1.8fr;border-top:1px solid #b9beb7;padding:23px 0}
  .comparison .point:last-child{border-bottom:1px solid #b9beb7}.comparison .num{display:none}.comparison .point>div{display:contents}
  .comparison h2{font-size:38px;padding-right:14px}.comparison .point p{padding-left:22px;border-left:1px solid #b9beb7}
  .checklist .points{border-top:0}.checklist .point{grid-template-columns:48px 1fr}.checklist .num{font-size:0;width:25px;height:25px;margin-top:10px;border:2px solid #526657}
  .checklist .title-frame{padding:27px 25px 26px 0}.checklist .title-frame:before{left:auto;right:0;top:auto;bottom:0;border:0;border-bottom:3px solid #526657;border-right:3px solid #526657}
  </style><body><main class="sheet ${esc(c.layout)}"><div class="top"><span class="brand"><i class="mark"></i>サイト工房 / Page Atelier</span><span>制作の手引き ${esc(c.number)}</span></div><p class="topic">${esc(c.topic)}</p><div class="title-frame"><h1>${esc(c.headline).replaceAll('\n','<br>')}</h1></div><p class="summary">${esc(c.summary)}</p><div class="points">${rows}</div><div class="bottom"><span>詳しい手順は、プロフィールから。</span><span>pageatelier.jp ↗</span></div></main></body></html>`;
}

(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', headless:true, args:['--no-sandbox']});
  const page = await browser.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  await page.route('**/*', route => route.abort());
  const report=[];
  try {
    for (const p of posts) {
      await page.setContent(sheet(p));
      await page.evaluate(() => document.fonts.ready);
      const fit = await page.evaluate(() => {
        const points=document.querySelector('.points').getBoundingClientRect();
        const footer=document.querySelector('.bottom').getBoundingClientRect();
        return points.bottom + 35 <= footer.top && [...document.querySelectorAll('h1,h2,.point p,.top,.summary')].every(e => e.scrollWidth <= e.clientWidth+1);
      });
      if(!fit) throw new Error('Card overflow: '+p.id);
      const target=path.join(root,'assets/marketing',p.id+'.jpg');
      await page.screenshot({path:target,type:'jpeg',quality:93});
      report.push({id:p.id,layout:p.card.layout,dimensions:[1080,1350],overflow:false});
    }
    console.log(JSON.stringify(report,null,2));
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1)});
