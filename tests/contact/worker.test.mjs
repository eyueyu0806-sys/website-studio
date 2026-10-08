import test from 'node:test';
import assert from 'node:assert/strict';
import worker,{Inquiry,ContactQuota,messages,validate,RECEIPT} from '../../integrations/contact/worker.mjs';
const id='5b751b02-d891-4a08-ae47-3cd37ff965d7';
const data=()=>({request_id:id,name:'相談テスト',email:'visitor@example.com',industry:'美容室',message:'相談の本文',site_plan:'屋号：テスト\nページ構成：TOP / メニュー',acquisition:'instagram / social / studio_launch',privacy_consent:'個人情報の取扱いと情報提供に同意済み',privacy_policy_version:'2026-10-08-resend',privacy_consent_at:new Date().toISOString(),turnstile_token:'test-token',_honey:''});
function context(){
 const values=new Map();let tail=Promise.resolve();
 return {values,storage:{setAlarm:async()=>{},deleteAll:async()=>values.clear(),get:async k=>structuredClone(values.get(k)),put:async(k,v)=>{values.set(k,structuredClone(v));}},blockConcurrencyWhile(fn){const next=tail.then(fn);tail=next.catch(()=>{});return next;}};
}
function setup(t,send){
 const old=globalThis.fetch,calls=[];
 globalThis.fetch=async(url,options)=>{
  calls.push({url,options});
  if(url.includes('siteverify'))return Response.json({success:true,hostname:'pageatelier.jp',action:'contact'});
  return send ? send(url,options) : Response.json({data:[{id:'owner-email'},{id:'receipt-email'}]});
 };
 t.after(()=>{globalThis.fetch=old;});
 const quota=new ContactQuota(context());
 const env={RESEND_API_KEY:'synthetic-key',TURNSTILE_SECRET_KEY:'synthetic-secret',QUOTA:{idFromName:n=>n,get:()=>quota}};
 const ctx=context(),object=new Inquiry(ctx,env);
 return {calls,ctx,env,object,request:(d=data())=>new Request('https://internal/contact',{method:'POST',body:JSON.stringify(d)})};
}
test('owner receives inquiry and plan; receipt is fixed and replies go to owner',()=>{
 const p=data();p.message='untrusted https://attacker.example';
 const batch=messages(validate(p).data,id);
 assert.deepEqual(batch[0].to,['yue.sadamatsu@gmail.com']);assert.equal(batch[0].reply_to,p.email);
 assert.match(batch[0].text,/ページ構成：TOP/);
 assert.deepEqual(batch[1].to,[p.email]);assert.equal(batch[1].reply_to,'yue.sadamatsu@gmail.com');
 assert.equal(batch[1].text,RECEIPT+'\n\n受付番号：'+id);assert(!batch[1].text.includes('attacker'));
 assert.equal(batch[1].from,'Page Atelier <contact@pageatelier.jp>');
});
test('validation rejects header injection, oversized fields, honeypot and missing consent',()=>{
 for(const patch of [{email:'visitor@example.com\r\nBcc: victim@example.com'},{name:'a\r\nb'},{message:'x'.repeat(6001)},{privacy_consent:''},{_honey:'bot'},{privacy_policy_version:'old'},{request_id:'bad'}])assert.throws(()=>validate({...data(),...patch}));
});
test('Origin and payload checks fail before contacting email service',async t=>{
 const f=setup(t);const env={...f.env,CONTACT_RATE:{limit:async()=>({success:true})},INQUIRIES:{idFromName:n=>n,get:()=>f.object}};
 const req=(origin,body)=>new Request('https://worker.example/contact',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json','CF-Connecting-IP':'192.0.2.1'},body});
 assert.equal((await worker.fetch(req('https://attacker.example',JSON.stringify(data())),env)).status,403);
 assert.equal((await worker.fetch(req('https://pageatelier.jp','x'.repeat(48001)),env)).status,413);
 assert.equal(f.calls.length,0);
 const valid=await worker.fetch(req('https://pageatelier.jp',JSON.stringify(data())),env);
 assert.equal(valid.headers.get('Access-Control-Allow-Origin'),'https://pageatelier.jp');assert.equal(valid.status,200);
});
test('invalid challenge hostname/action cannot send a batch',async t=>{
 const f=setup(t);globalThis.fetch=async()=>Response.json({success:true,hostname:'other.example',action:'contact'});
 const response=await f.object.fetch(f.request());assert.equal(response.status,400);assert.equal(f.ctx.values.size,0);
});
test('concurrent identical submissions send exactly one batch',async t=>{
 const f=setup(t);const d=data();
 const responses=await Promise.all([f.object.fetch(f.request(d)),f.object.fetch(f.request(d))]);
 assert(responses.every(r=>r.status===200));assert.equal(f.calls.filter(c=>c.url.includes('/emails/batch')).length,1);
 assert.equal(f.ctx.values.get('record').status,'sent');
});
test('lost response retries exact batch with identical provider idempotency key',async t=>{
 let count=0;const f=setup(t,()=>{if(++count===1)throw Error('network after acceptance');return Response.json({data:[{id:'a'},{id:'b'}]});});
 const d=data();assert.equal((await f.object.fetch(f.request(d))).status,503);
 assert.equal((await f.object.fetch(f.request({...d,turnstile_token:''}))).status,200);
 const calls=f.calls.filter(c=>c.url.includes('/emails/batch'));
 assert.equal(calls.length,2);assert.equal(calls[0].options.headers['Idempotency-Key'],calls[1].options.headers['Idempotency-Key']);assert.equal(calls[0].options.body,calls[1].options.body);
 assert.equal(f.calls.filter(c=>c.url.includes('siteverify')).length,1);
});
test('changed payload with same ID and expired uncertain attempts never resend',async t=>{
 const f=setup(t,()=>{throw Error('lost');});const d=data();await f.object.fetch(f.request(d));
 assert.equal((await f.object.fetch(f.request({...d,message:'changed'}))).status,409);
 const r=f.ctx.values.get('record');r.at=Date.now()-24*3600000;
 assert.equal((await f.object.fetch(f.request(d))).status,409);assert.equal(f.calls.filter(c=>c.url.includes('/emails/batch')).length,1);
});
test('persistent reservation failure prevents email side effects',async t=>{
 const f=setup(t);f.ctx.storage.put=async()=>{throw Error('storage failed');};
 await assert.rejects(f.object.fetch(f.request()));assert.equal(f.calls.filter(c=>c.url.includes('/emails/batch')).length,0);
});
test('incomplete provider result stays pending instead of claiming success',async t=>{
 const f=setup(t,()=>Response.json({data:[{id:'only-one'}]}));
 assert.equal((await f.object.fetch(f.request())).status,503);assert.equal(f.ctx.values.get('record').status,'pending');
});
test('global quota caps 40 batches and repeated IDs do not consume more slots',async()=>{
 const quota=new ContactQuota(context());
 const make=(i,email=i)=>new Request('https://internal/quota',{method:'POST',body:JSON.stringify({id:`00000000-0000-4000-8000-${String(i).padStart(12,'0')}`,emailHash:String(email).padStart(64,'0')})});
 for(let i=0;i<40;i++)assert.equal((await quota.fetch(make(i))).status,200);
 assert.equal((await quota.fetch(make(1))).status,200);assert.equal((await quota.fetch(make(40))).status,429);
 const limited=new ContactQuota(context());for(let i=0;i<3;i++)assert.equal((await limited.fetch(make(i,0))).status,200);
 assert.equal((await limited.fetch(make(4,0))).status,429);
});

test('receipt ledger expires, and an old attempt cannot become a fresh send',async t=>{
 const f=setup(t);const d=data();await f.object.fetch(f.request(d));
 await f.object.alarm();assert.equal(f.ctx.values.size,0);
 d.privacy_consent_at=new Date(Date.now()-31*86400000).toISOString();
 assert.equal((await f.object.fetch(f.request(d))).status,409);
 assert.equal(f.calls.filter(c=>c.url.includes('/emails/batch')).length,1);
});
