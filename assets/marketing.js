(() => {
  'use strict';
  const config = window.PAGE_ATELIER_CONFIG || {};
  const validId = config.ga4Enabled !== false && /^G-[A-Z0-9]{5,20}$/.test(config.ga4MeasurementId || '');
  const sources = new Set(['instagram', 'google', 'line', 'journal', 'referral']);
  const media = new Set(['social', 'cpc', 'article', 'referral']);
  const campaigns = new Set(['builders_launch', 'builders_guide', 'studio_launch', 'studio_guide']);
  const key = 'pageatelier.analytics.consent';
  const contextKey = 'pageatelier.inquiry.context';
  const version = config.consentVersion || '2026-10-07';
  const events = new Set(['page_view', 'industry_selected', 'builder_step', 'site_plan_created', 'consultation_opened', 'line_click', 'generate_lead', 'contact_error']);
  let consent = 'unset';
  let loaded = false;
  let panel;
  const protectedBrowser = navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true;
  const read = (storage, name) => { try { return JSON.parse(window[storage].getItem(name)); } catch { return null; } };
  const write = (storage, name, value) => { try { window[storage].setItem(name, JSON.stringify(value)); } catch { /* Private browsing must still work. */ } };
  const safePath = () => location.pathname.replace(/[^a-zA-Z0-9/_\-.]/g, '').slice(0, 180);
  const cleanLocation = () => location.origin + safePath();
  const query = new URLSearchParams(location.search);
  const incoming = { source: sources.has(query.get('utm_source')) ? query.get('utm_source') : '', medium: media.has(query.get('utm_medium')) ? query.get('utm_medium') : '', campaign: campaigns.has(query.get('utm_campaign')) ? query.get('utm_campaign') : '' };
  // Only fixed campaign labels and known pages. No full referrer, URL query, names or form contents.
  if (incoming.source) write('sessionStorage', contextKey, { ...incoming, landing: safePath(), at: Date.now() });
  const previous = read('sessionStorage', contextKey);
  const context = previous && Date.now() - previous.at < 24 * 60 * 60 * 1000 ? previous : null;
  function attribution() {
    if (!context || !sources.has(context.source)) return '直接アクセス・流入元未確認';
    return [context.source, media.has(context.medium) ? context.medium : '', campaigns.has(context.campaign) ? context.campaign : '', /^\/[a-zA-Z0-9/_\-.]{0,180}$/.test(context.landing || '') ? context.landing : ''].filter(Boolean).join(' / ');
  }
  const stored = read('localStorage', key);
  if (stored && stored.version === version && Date.now() - stored.at < 180 * 86400000 && ['granted', 'denied'].includes(stored.value)) consent = stored.value;
  if (protectedBrowser) consent = 'denied';
  function track(name, params = {}) {
    if (!events.has(name) || !validId || consent !== 'granted' || protectedBrowser || !loaded || typeof window.gtag !== 'function') return;
    const safe = {};
    if (['realestate', 'beauty', 'food', 'builder', 'pro', 'ec', 'other'].includes(params.industry)) safe.industry = params.industry;
    if (['inquiry', 'reserve', 'sell', 'trust', 'recruit', 'service'].includes(params.purpose)) safe.purpose = params.purpose;
    if ([1, 2, 3].includes(params.step)) safe.step = params.step;
    if (['form', 'line'].includes(params.method)) safe.method = params.method;
    if (['network', 'timeout'].includes(params.reason)) safe.reason = params.reason;
    if (context && sources.has(context.source)) safe.campaign_source = context.source;
    window.gtag('event', name, { ...safe, page_location: cleanLocation(), page_referrer: '', page_title: document.title });
  }
  function scrubLocation() {
    // Google's automatic events may inspect location independently of page_location.
    // Retain only the same fixed routing/campaign values already accepted by the site.
    const clean = new URLSearchParams();
    if (['realestate', 'beauty', 'food', 'builder', 'pro', 'ec', 'other'].includes(query.get('industry'))) clean.set('industry', query.get('industry'));
    if (['inquiry', 'reserve', 'sell', 'trust', 'recruit', 'service'].includes(query.get('purpose'))) clean.set('purpose', query.get('purpose'));
    if (incoming.source) clean.set('utm_source', incoming.source);
    if (incoming.medium) clean.set('utm_medium', incoming.medium);
    if (incoming.campaign) clean.set('utm_campaign', incoming.campaign);
    const hash = /^#[a-zA-Z0-9_-]{1,64}$/.test(location.hash) && document.getElementById(location.hash.slice(1)) ? location.hash : '';
    const target = location.pathname + (clean.size ? '?' + clean.toString() : '') + hash;
    try { history.replaceState(history.state, '', target); return true; }
    catch { return false; } // Do not load analytics if the URL cannot be made safe.
  }
  function load() {
    if (!validId || consent !== 'granted' || protectedBrowser || loaded) return;
    if (!scrubLocation()) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
    window.gtag('js', new Date());
    window.gtag('config', config.ga4MeasurementId, { send_page_view: false, page_location: cleanLocation(), page_referrer: '', allow_google_signals: false, allow_ad_personalization_signals: false });
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(config.ga4MeasurementId);
    document.head.append(script);
    track('page_view');
  }
  function forgetCookies() {
    // GA may set host/domain cookies. Remove accessible GA cookies when withdrawing.
    document.cookie.split(';').map(x => x.trim().split('=')[0]).filter(x => /^_ga(?:_|$)|^_gid$|^_gat/.test(x)).forEach(name => {
      [null, location.hostname, '.' + location.hostname].forEach(domain => {
        document.cookie = name + '=; Max-Age=0; path=/; SameSite=Lax' + (domain ? '; domain=' + domain : '');
      });
    });
  }
  function choose(value) {
    consent = value;
    write('localStorage', key, { version, value, at: Date.now() });
    if (value === 'denied') {
      window['ga-disable-' + config.ga4MeasurementId] = true;
      if (window.gtag) window.gtag('consent', 'update', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
      forgetCookies();
    } else {
      window['ga-disable-' + config.ga4MeasurementId] = false;
      if (window.gtag) window.gtag('consent', 'update', { analytics_storage: 'granted' });
      load();
    }
    panel.hidden = true;
    document.querySelector('[data-analytics-settings]')?.focus({ preventScroll: true });
  }
  function setup() {
    document.addEventListener('click', e => {
      const a = e.target.closest('a');
      if (!a) return;
      if (a.matches('[data-line]') || a.href.startsWith('https://lin.ee/')) track('line_click', { method: 'line' });
    });
    if (!validId) return;
    const style = document.createElement('style');
    style.textContent = '.atelier-consent{position:fixed;inset:auto 16px 16px;z-index:10000;max-width:720px;margin:auto;padding:22px;background:#fff;border:1px solid #526657;color:#111;font:14px/1.7 system-ui,sans-serif}.atelier-consent[hidden]{display:none}.atelier-consent p{margin:0 0 14px}.atelier-consent-actions{display:flex;flex-wrap:wrap;gap:12px}.atelier-consent button{padding:10px 16px;border:1px solid #526657;background:#fff;color:#111;font:inherit;cursor:pointer}.atelier-consent button:focus-visible{outline:2px solid #526657;outline-offset:3px}.atelier-consent button[data-choice="granted"]{background:#526657;color:#fff}.atelier-settings{border:0;background:none;color:inherit;font:inherit;text-decoration:underline;text-underline-offset:4px;cursor:pointer}';
    document.head.append(style);
    panel = document.createElement('aside');
    panel.className = 'atelier-consent';
    panel.setAttribute('aria-label', 'アクセス解析の設定');
    panel.innerHTML = '<p>サイトの改善のため、同意した場合のみGoogle Analyticsで閲覧・ボタン操作を計測します。相談内容やメールアドレスは送りません。<a href="/privacy.html#cookies-title">詳細</a></p><div class="atelier-consent-actions"><button type="button" data-choice="denied">同意しない</button><button type="button" data-choice="granted">解析に同意する</button><button type="button" data-choice="later">後で決める</button></div>';
    panel.hidden = consent !== 'unset';
    panel.addEventListener('click', e => {
      const value = e.target.closest('[data-choice]')?.dataset.choice;
      if (value === 'later') panel.hidden = true;
      else if (value && !protectedBrowser) choose(value);
    });
    document.body.append(panel);
    const settings = document.createElement('button');
    settings.type = 'button'; settings.className = 'atelier-settings'; settings.dataset.analyticsSettings = '';
    settings.textContent = '解析の設定';
    settings.addEventListener('click', () => { panel.hidden = false; panel.querySelector('button').focus(); });
    (document.querySelector('footer nav:last-child') || document.querySelector('footer') || document.body).append(settings);
    if (!protectedBrowser) load();
    else { panel.hidden = true; settings.textContent = '解析停止中（ブラウザ設定）'; settings.disabled = true; }
  }
  window.PageAtelier = Object.freeze({ track, attribution });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setup, { once: true });
  else setup();
})();
