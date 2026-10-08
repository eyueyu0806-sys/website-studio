const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const origin=process.env.TEST_ORIGIN || 'http://127.0.0.1:8014';
assert.ok(['127.0.0.1','localhost','[::1]'].includes(new URL(origin).hostname), 'Use a local test server');
const output=process.env.TEST_ARTIFACTS || '/tmp/pageatelier-consultation-check';
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',args:['--no-sandbox']});
 try {for(const width of [1440,1200,390]) {
  const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'}), errors=[], sent=[];
  page.on('pageerror',e=>errors.push(e.message));
  let fail=false;
  await page.route('https://formsubmit.co/**',async r=>{if(r.request().method()==='OPTIONS')return r.fulfill({status:204,headers:{'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'Content-Type'}});sent.push(r.request().postDataJSON());await r.fulfill({status:fail?503:200,contentType:'application/json',headers:{'Access-Control-Allow-Origin':'*'},body:JSON.stringify({success:!fail})})});
  await page.goto(origin+'/',{waitUntil:'networkidle'});
  await page.locator('[data-choice=denied]').click();
  await page.evaluate(()=>scrollTo(0,0));
  await page.locator('.hero').screenshot({path:`${output}/hero-${width}.png`});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  // Every plan carries through to the form, without erasing a visitor's draft.
  await page.locator('#f-body').fill('相談の下書き');
  for(const plan of ['one-page','website','support']){
   await page.locator(`[data-plan="${plan}"]`).click();
   assert.equal(await page.locator('#f-plan').inputValue(),plan);
   assert.equal(await page.locator('#f-body').inputValue(),'相談の下書き');
  }
  await page.locator('#hero-name').fill('添付時の屋号');
  await page.locator('#opt-ind .opt[data-k="beauty"]').click();
  await page.waitForSelector('.step[data-step="2"].is-active');
  await page.locator('#opt-pur .opt[data-k="reserve"]').click();
  await page.waitForSelector('.step[data-step="3"].is-active');
  await page.locator('#b-next').click();await page.waitForSelector('#result.on');
  await page.locator('#r-consult').click();await page.waitForSelector('#attach.on');
  await page.locator('#hero-name').fill('添付後の別の屋号');
  await page.locator('[data-plan="website"]').click();
  await page.locator('#f-name').fill('接続テスト');await page.locator('#f-mail').fill('visitor@example.com');await page.locator('#f-consent').check();
  fail=true;await page.locator('#form button[type=submit]').click();
  await page.waitForFunction(()=>!document.querySelector('#contact-fallback').hidden);
  assert.equal(await page.locator('#f-plan').inputValue(),'website');
  assert.equal(await page.locator('#f-body').inputValue(),'相談の下書き');
  assert.match(sent.at(-1).message,/110,000円/);
  assert.match(sent.at(-1).site_plan,/添付時の屋号/);
  assert.ok(!sent.at(-1).site_plan.includes('添付後の別の屋号'));
  await page.locator('#form').scrollIntoViewIfNeeded();
  await page.screenshot({path:`${output}/form-${width}.png`});
  fail=false;await page.locator('#form button[type=submit]').click();
  await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('お問い合わせを送信しました'));
  assert.equal(await page.locator('#f-plan').inputValue(),'');
  assert.ok(await page.locator('#contact-fallback').isHidden());
  assert.deepEqual(sent.at(-1).site_plan,sent.at(-2).site_plan);
  assert.deepEqual(errors,[]);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  console.log(`PASS ${width}px: all price CTAs, draft retention, frozen builder attachment, selected plan in payload, failure alternatives, successful retry/reset, no JS errors/overflow`);
  await page.close();
 }}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
