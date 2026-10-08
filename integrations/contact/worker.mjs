// No secrets or message bodies are logged. The public site remains on GitHub Pages.
const ORIGIN = 'https://pageatelier.jp';
const OWNER = 'yue.sadamatsu@gmail.com';
const FROM = 'Page Atelier <contact@pageatelier.jp>';
const POLICY = '2026-10-08-resend';
const MAX_BYTES = 48000;
const UUID = /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
const json = (value, status = 200) => Response.json(value, {status, headers: {'Cache-Control': 'no-store'}});
const fail = (code, status) => json({success: false, code}, status);
export const RECEIPT = `お問い合わせありがとうございます。
ご相談内容を受け付けました。内容を確認のうえ、担当者からご連絡します。

追加のご希望は、このメールにご返信ください。
※このメールは受付の自動返信です。契約・お支払いは発生していません。

お心当たりのない場合は、このメールを破棄してください。

サイト工房｜Page Atelier
https://pageatelier.jp/
お問い合わせ：${OWNER}`;

export function validate(input) {
  if (!input || !UUID.test(input.request_id || '')) throw Error('invalid');
  const limits = {name: 100, email: 254, industry: 100, message: 6000, site_plan: 6000,
    acquisition: 300, privacy_consent: 160, privacy_policy_version: 40, privacy_consent_at: 40};
  const data = {};
  for (const [key, max] of Object.entries(limits)) {
    if (typeof input[key] !== 'string' || input[key].length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(input[key])) throw Error('invalid');
    data[key] = input[key].trim();
  }
  if (!data.name || /[\r\n]/.test(data.name) || !/^[^\s<>(),;:"\\]+@[^\s<>(),;:"\\]+\.[^\s<>(),;:"\\]+$/.test(data.email)) throw Error('invalid');
  if (data.privacy_policy_version !== POLICY || !data.privacy_consent.startsWith('個人情報の取扱い') || !data.privacy_consent.includes('同意済み') || !Number.isFinite(Date.parse(data.privacy_consent_at))) throw Error('invalid');
  if (input._honey || typeof input.turnstile_token !== 'string' || input.turnstile_token.length > 2048) throw Error('invalid');
  return {data, id: input.request_id, token: input.turnstile_token};
}
async function digest(value) {
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  return [...new Uint8Array(bytes)].map(x => x.toString(16).padStart(2, '0')).join('');
}
async function readLimited(request) {
  if (Number(request.headers.get('Content-Length')) > MAX_BYTES) throw Error('size');
  const reader = request.body?.getReader();
  if (!reader) throw Error('invalid');
  const chunks = []; let size = 0;
  while (true) {
    const {done, value} = await reader.read(); if (done) break;
    size += value.byteLength;
    if (size > MAX_BYTES) {await reader.cancel(); throw Error('size');}
    chunks.push(value);
  }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) {bytes.set(chunk, offset); offset += chunk.byteLength;}
  return JSON.parse(new TextDecoder('utf-8', {fatal:true}).decode(bytes));
}
export function messages(data, id) {
  const labels = {name:'お名前', email:'返信先', industry:'業種', message:'相談内容', site_plan:'サイト構成', acquisition:'流入元', privacy_consent:'同意', privacy_policy_version:'説明の版', privacy_consent_at:'送信者の同意日時'};
  const body = '受付番号：' + id + '\n\n' + Object.entries(labels).map(([key, label]) => label + '：\n' + data[key]).join('\n\n');
  return [
    {from:FROM, to:[OWNER], reply_to:data.email, subject:'【Page Atelier】無料相談を受け付けました', text:body},
    // Do not reflect unverified visitor input/links or their inquiry into the receipt.
    {from:FROM, to:[data.email], reply_to:OWNER, subject:'【Page Atelier】お問い合わせを受け付けました', text:RECEIPT + '\n\n受付番号：' + id}
  ];
}
export default {
  async fetch(request, env) {
    if (new URL(request.url).pathname !== '/contact') return fail('not_found',404);
    if (request.headers.get('Origin') !== ORIGIN) return fail('origin',403);
    const respond = response => {
      const headers = new Headers(response.headers);
      headers.set('Access-Control-Allow-Origin', ORIGIN); headers.set('Vary','Origin');
      headers.set('Access-Control-Allow-Methods','POST, OPTIONS');
      headers.set('Access-Control-Allow-Headers','Content-Type');
      return new Response(response.body,{status:response.status,headers});
    };
    if (request.method === 'OPTIONS') return respond(new Response(null,{status:204}));
    if (request.method !== 'POST') return respond(fail('method',405));
    if (!env.RESEND_API_KEY || !env.TURNSTILE_SECRET_KEY || !env.INQUIRIES || !env.QUOTA || !env.CONTACT_RATE) return respond(fail('unavailable',503));
    if (!request.headers.get('Content-Type')?.startsWith('application/json')) return respond(fail('content_type',415));
    try {
      // This binding provides a local edge limit, not a global daily spend limit.
      const ip = request.headers.get('CF-Connecting-IP');
      if (!ip || !(await env.CONTACT_RATE.limit({key:ip})).success) return respond(fail('rate_limit',429));
      let input;
      try {input = await readLimited(request); validate(input);} catch (e) {return respond(fail('invalid',e.message === 'size' ? 413 : 400));}
      const stub = env.INQUIRIES.get(env.INQUIRIES.idFromName(input.request_id));
      return respond(await stub.fetch(new Request('https://internal/contact',{method:'POST',body:JSON.stringify(input)})));
    } catch {return respond(fail('unavailable',503));}
  }
};

export class Inquiry {
  constructor(ctx, env) {this.ctx=ctx; this.env=env;}
  async alarm() {await this.ctx.storage.deleteAll();}
  async fetch(request) {
    // Serialize the whole delivery attempt, including concurrent retries, per request ID.
    return this.ctx.blockConcurrencyWhile(async () => {
      let parsed;
      try {parsed=validate(await request.json());} catch {return fail('invalid',400);}
      const {data,id,token}=parsed;
      const hash=await digest(JSON.stringify(data));
      let record=await this.ctx.storage.get('record');
      if (record && record.hash !== hash) return fail('id_conflict',409);
      if (record?.status === 'sent') return json({success:true,receipt:'accepted',request_id:id});
      // Resend deduplicates for 24h; never replay an uncertain attempt after that window.
      if (record && Date.now()-record.at > 23*3600000) return fail('manual_review',409);
      if (!record) {
        if (Math.abs(Date.now()-Date.parse(data.privacy_consent_at))>15*60000) return fail('manual_review',409);
        if (!token) return fail('challenge',400);
        let verified;
        try {
          const response=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{
            method:'POST',headers:{'Content-Type':'application/json'},signal:AbortSignal.timeout(7000),
            body:JSON.stringify({secret:this.env.TURNSTILE_SECRET_KEY,response:token,idempotency_key:id})});
          if (!response.ok) return fail('challenge',400);
          verified=await response.json();
        } catch {return fail('challenge',400);}
        if (verified.success !== true || verified.hostname !== 'pageatelier.jp' || verified.action !== 'contact') return fail('challenge',400);
        record={hash,at:Date.now(),status:'pending'};
        // If storage fails here, do not send any email.
        await this.ctx.storage.setAlarm(Date.now()+30*86400000);
        await this.ctx.storage.put('record',record);
      }
      const quota=this.env.QUOTA.get(this.env.QUOTA.idFromName('contact-global'));
      const quotaResponse=await quota.fetch(new Request('https://internal/quota',{method:'POST',body:JSON.stringify({emailHash:await digest(data.email.toLowerCase()),id})}));
      if (!quotaResponse.ok) return fail('rate_limit',429);
      try {
        const response=await fetch('https://api.resend.com/emails/batch',{
          method:'POST',signal:AbortSignal.timeout(10000),headers:{Authorization:'Bearer '+this.env.RESEND_API_KEY,'Content-Type':'application/json','Idempotency-Key':'pageatelier-contact-v1-'+id},
          body:JSON.stringify(messages(data,id))});
        if (!response.ok) return fail('delivery_pending',503);
        const result=await response.json();
        if (!Array.isArray(result.data) || result.data.length!==2 || result.data.some(x=>typeof x.id!=='string'||!x.id)) return fail('delivery_pending',503);
        await this.ctx.storage.put('record',{...record,status:'sent',ids:result.data.map(x=>x.id)});
        return json({success:true,receipt:'accepted',request_id:id});
      } catch {return fail('delivery_pending',503);}
    });
  }
}
export class ContactQuota {
  constructor(ctx) {this.ctx=ctx;}
  async alarm() {await this.ctx.storage.deleteAll();}
  async fetch(request) {
    return this.ctx.blockConcurrencyWhile(async () => {
      const {emailHash,id}=await request.json();
      if (!/^[a-f0-9]{64}$/.test(emailHash) || !UUID.test(id||'')) return fail('invalid',400);
      const day=new Date().toISOString().slice(0,10);
      let state=await this.ctx.storage.get('daily');
      if (state?.day!==day) state={day,total:0,emails:{},ids:{}};
      if (state.ids[id]) return json({success:true});
      // Global cap: 40 distinct attempted batches/day (UTC), including older retries.
      if (state.total>=40 || (state.emails[emailHash]||0)>=3) return fail('rate_limit',429);
      state.total++;state.ids[id]=true;state.emails[emailHash]=(state.emails[emailHash]||0)+1;
      await this.ctx.storage.setAlarm(Date.now()+2*86400000);
      await this.ctx.storage.put('daily',state);
      return json({success:true});
    });
  }
}
