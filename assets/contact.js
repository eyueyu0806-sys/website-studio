/* Optional Resend transport. No provider code loads while contactMode is formsubmit. */
(() => {
  'use strict';
  const config=window.PAGE_ATELIER_CONFIG || {};
  if (config.contactMode !== 'resend') return;
  const form=document.querySelector('#form');
  const status=document.querySelector('#status');
  const storageKey='pageatelier.contact.attempt';
  let token='', widget, initError='', attempt=null;
  const fail=(code,message)=>Object.assign(new Error(message),{contactCode:code});
  try {
    const endpoint=new URL(config.contactEndpoint);
    if (endpoint.protocol!=='https:' || endpoint.pathname!=='/contact' || endpoint.search || endpoint.hash || !config.turnstileSiteKey || config.contactPolicyVersion!=='2026-10-08-resend') throw Error('config');
  } catch {initError='受付の設定を確認中です。メールまたはLINEからご相談ください。';}
  try {attempt=JSON.parse(sessionStorage.getItem(storageKey));} catch { /* Memory-only retry still works. */ }
  if (!attempt || typeof attempt.fingerprint!=='string' || typeof attempt.id!=='string' || typeof attempt.at!=='string') attempt=null;
  const remember=()=>{try {if(attempt) sessionStorage.setItem(storageKey,JSON.stringify(attempt));else sessionStorage.removeItem(storageKey);}catch {}};
  const reset=()=>{token='';if(widget!==undefined && window.turnstile) window.turnstile.reset(widget);};
  window.PageAtelierContact={
    async send(payload,signal) {
      if (initError) throw fail('unavailable',initError);
      const core={...payload}; delete core.privacy_consent_at;
      const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(core)));
      const fingerprint=Array.from(new Uint8Array(bytes),x=>x.toString(16).padStart(2,'0')).join('');
      if (!attempt || attempt.fingerprint!==fingerprint || !attempt.attempted) attempt={fingerprint,id:crypto.randomUUID(),at:payload.privacy_consent_at,attempted:false};
      if (!token && !attempt.attempted) throw fail('challenge','送信前の確認が終わるまで、少しお待ちください。確認が表示されない場合はメールまたはLINEからご相談ください。');
      attempt.attempted=true;remember();
      let result,response;
      try {
        response=await fetch(config.contactEndpoint,{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},signal,
          body:JSON.stringify({...payload,privacy_consent_at:attempt.at,request_id:attempt.id,turnstile_token:token})});
        result=await response.json();
      } finally {reset();}
      if (!response.ok || result.success!==true) {
        const text={
          challenge:'送信前の確認をやり直してから、もう一度お試しください。入力内容は残っています。',
          rate_limit:'受付が混み合っています。少し時間をおくか、メールまたはLINEからご相談ください。入力内容は残っています。',
          invalid:'入力内容の形式・長さを確認してください。入力内容は残っています。',
          id_conflict:'送信結果の確認が必要です。重複送信を避けるため、メールまたはLINEからご連絡ください。入力内容は残っています。',
          manual_review:'前回の送信結果を確認できません。再送せず、メールまたはLINEからご連絡ください。入力内容は残っています。',
          delivery_pending:'送信結果を確認できませんでした。入力内容は残っています。同じ内容で再度お試しいただくと、受付状況を確認します。'
        };
        throw fail(result.code || 'unavailable',text[result.code] || '現在送信できません。入力内容は残っています。メールまたはLINEからご相談ください。');
      }
      attempt=null;remember();
      return result;
    }
  };
  if (!form || initError) return;
  const container=document.createElement('div');container.className='full';container.id='contact-verification';
  form.querySelector('.privacy-consent').after(container);
  // Load only when the form approaches view, not on initial landing.
  const load=()=>{
    const script=document.createElement('script');
    script.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';script.async=true;
    script.onload=()=>{
      try {widget=window.turnstile.render(container,{sitekey:config.turnstileSiteKey,action:'contact',theme:'light',size:'flexible',
        callback:value=>{token=value;},'expired-callback':()=>{token='';},'error-callback':()=>{token='';status.textContent='送信前の確認を読み込めませんでした。メールまたはLINEからご相談ください。';}});}
      catch {initError='送信前の確認を読み込めませんでした。メールまたはLINEからご相談ください。';}
    };
    script.onerror=()=>{initError='送信前の確認を読み込めませんでした。メールまたはLINEからご相談ください。';status.textContent=initError;};
    document.head.append(script);
  };
  if ('IntersectionObserver' in window) {
    const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){observer.disconnect();load();}},{rootMargin:'400px'});observer.observe(form);
  } else load();
})();
