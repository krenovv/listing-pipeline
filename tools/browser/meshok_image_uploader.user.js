// ==UserScript==
// @name         Meshok: Mail/eBay -> загрузка файлов (одна панель)
// @namespace    meshok-lite-filedrop
// @version      4.0.0
// @description  Яндекс.Почта (в т.ч. LITE) и eBay: собирает фото лота и грузит их на Meshok через input[type=file]. На почте 1-е фото уходит последним; на eBay порядок исходный.
// @author       you
// @match        https://mail.yandex.ru/*
// @match        https://mail.yandex.ru/lite/*
// @match        https://mail.yandex.*/*
// @match        https://www.ebay.com/*
// @match        https://ebay.com/*
// @match        https://www.ebay.*/*
// @match        https://ebay.*/*
// @match        https://meshok.net/*
// @match        https://www.meshok.net/*
// @match        https://*.meshok.net/*
// @match        http://meshok.net/*
// @match        http://www.meshok.net/*
// @match        http://*.meshok.net/*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_addValueChangeListener
// @grant        GM_notification
// @grant        GM_xmlhttpRequest
// @connect      yandex.ru
// @connect      yandex.net
// @connect      yandex.com
// @connect      yandex.by
// @connect      yandex.kz
// @connect      mail.yandex.ru
// @connect      *.yandex.ru
// @connect      *.yandex.net
// @connect      i.ebayimg.com
// @run-at       document-idle
// ==/UserScript==

(function(){
  'use strict';

  /* ========== Общие утилиты и хранилище ========== */
  const KEY_QUEUE = 'meshok_queue_lots'; // [{from,title,items:[{url,name,isDownload}]}]
  const KEY_UI = 'meshok_ui_prefs';
  const getUIPrefs = () => GM_getValue(KEY_UI, { bottom: 100, opacity: 0.92 });
  const setUIPrefs = (patch = {}) => {
  const cur = getUIPrefs();
  GM_setValue(KEY_UI, { ...cur, ...patch });
  return getUIPrefs();
};

  const notify=(text,title='Meshok',timeout=2500)=>{ try{ GM_notification({text,title,timeout}); }catch{} };
  const sleep=(ms)=>new Promise(r=>setTimeout(r,ms));
  const lotsGet = ()=> GM_getValue(KEY_QUEUE, []);
  const lotsSet = (arr)=> GM_setValue(KEY_QUEUE, arr||[]);
  const lotsPush= (lot)=> { const q=lotsGet(); q.push(lot); lotsSet(q); };
  const lotsShift=()=> { const q=lotsGet(); if(!q.length) return null; const it=q.shift(); lotsSet(q); return it; };

  const onYandexMail = ()=> location.hostname.includes('mail.yandex');
  const onMeshok     = ()=> location.hostname.includes('meshok');
  const onEbay       = ()=> location.hostname.endsWith('ebay.com') || location.hostname === 'ebay.com';

  /* ========== Яндекс.Почта: сбор вложений ========== */
  const BAD_HOSTS = new Set([
    'upics.yandex.net','avatars.mds.yandex.net','yastatic.net',
    'ssl.gstatic.com','lh3.googleusercontent.com','gstatic.com','gravatar.com'
  ]);

  const looksLikeImageURL = (href)=> {
    href = href || '';
    return (
      /\.(jpe?g|png|webp|gif)(\?.*)?$/i.test(href) ||
      /[?&]filename=.*\.(jpe?g|png|webp|gif)/i.test(href) ||
      /[?&](mime|content_type)=image\//i.test(href) ||
      /\/get-attached\//i.test(href)
    );
  };

  const filenameFrom = (url) => {
    try {
      const u = new URL(url, location.href);
      const fn = u.searchParams.get('filename') || u.pathname.split('/').pop();
      return decodeURIComponent((fn || 'image.jpg').split('?')[0]);
    } catch { return 'image.jpg'; }
  };

  function getMailRoots(){
    const roots = [];
    const selectors = [
      '[data-testid="message-body"]',
      '[data-uid][data-testid*="message"] [data-testid*="body"]',
      '.mail-Message-Body-Content',
      '.message__body',
      '.js-message-body',
      '.message-body',
      '[data-qa="message-attachments"]',
      '.mail-attachments','.b-attachments','.attachments'
    ];
    selectors.forEach(sel => { const el = document.querySelector(sel); if (el) roots.push(el); });
    document.querySelectorAll('iframe').forEach(f=>{ try{ if(f.contentDocument?.body) roots.push(f.contentDocument.body); }catch{} });
    if (!roots.length) roots.push(document.body);
    return roots;
  }

  function collectFromMail(){
    const roots = getMailRoots();
    const imgs = new Set(), links = new Set();

    for (const root of roots){
      root.querySelectorAll('img').forEach(img=>{
        const src = img.currentSrc || img.src || '';
        if (!/^https?:\/\//i.test(src)) return;
        try { const host = new URL(src).hostname; if (BAD_HOSTS.has(host)) return; } catch {}
        imgs.add(src);
      });
      root.querySelectorAll('a[href]').forEach(a=>{
        const href = a.href;
        if (looksLikeImageURL(href)) links.add(href);
      });
    }

    // массив [{url,name,isDownload}]
    const items = [];
    imgs.forEach(u => items.push({url:u, name: filenameFrom(u), isDownload:false}));
    links.forEach(u => items.push({url:u, name: filenameFrom(u), isDownload:true}));

    // уникализируем
    const uniq = [], seen = new Set();
    for (const it of items){ if (seen.has(it.url)) continue; seen.add(it.url); uniq.push(it); }
    return uniq;
  }

  function injectMailButton(){
    if (!onYandexMail()) return;
    if (document.getElementById('meshok-mail-btn')) return;

    const btn = document.createElement('button');
    btn.id='meshok-mail-btn';
    btn.textContent='Собрать фото из письма';
    Object.assign(btn.style,{
      position:'fixed', right:'16px', bottom:'16px', zIndex:2147483647,
      padding:'10px 14px', borderRadius:'10px', border:'none',
      background:'#ffd04d', color:'#000', cursor:'pointer',
      boxShadow:'0 6px 16px rgba(0,0,0,.25)', font:'14px system-ui'
    });
    btn.addEventListener('click', async ()=>{
      btn.disabled=true; const o=btn.textContent; btn.textContent='Собираю…';
      await sleep(200);
      let items = collectFromMail().filter(x=>/\.(jpe?g|png|webp|gif)(\b|$)/i.test(x.name));
      if (!items.length){ btn.textContent='Фото не найдены'; await sleep(1200); btn.textContent=o; btn.disabled=false; return; }

      // ВАЖНО: на почте первое фото кладём ПОСЛЕДНИМ
      if (items.length > 1) items = items.slice(1).concat(items[0]);

      const lot = { from: location.href, title: document.title || 'Lot', items };
      lotsPush(lot);
      notify(`Добавлено в очередь: ${items.length} фото`);
      btn.textContent=`Готово: ${items.length} шт.`; await sleep(1200); btn.textContent=o; btn.disabled=false;
    });
    document.body.appendChild(btn);
  }

  /* ========== eBay: сбор фото галереи лота (только товар) ========== */
  function normalizeEbayUrl(u){
    // предпочитаем максимальный размер, если встречаются s-l140/300/400/960 -> s-l1600
    try{
      return u.replace(/\/s\-l(140|300|400|500|960)\.(webp|jpg|jpeg|png)/i, '/s-l1600.$2');
    }catch{return u;}
  }

  function collectFromEbay(){
    // Берём только картинки из панели товара (PicturePanel), игнор описания
    const nodes = Array.from(document.querySelectorAll('#PicturePanel img[data-zoom-src], #PicturePanel img[data-src], #PicturePanel img[src]'));

    // Собираем в порядке, как в галерее
    const urls = [];
    for (const img of nodes){
      const u = img.getAttribute('data-zoom-src') || img.getAttribute('data-src') || img.getAttribute('src') || '';
      if (!u) continue;
      if (!/i\.ebayimg\.com/i.test(u)) continue; // только хост с изображениями товара
      const full = normalizeEbayUrl(u);
      urls.push(full);
    }

    // Уникализация, формирование items
    const seen = new Set(), items = [];
    for (const url of urls){
      const abs = url;
      if (seen.has(abs)) continue; seen.add(abs);
      const name = abs.split('/').pop().split('?')[0] || 'image.webp';
      items.push({ url: abs, name, isDownload:false });
    }
      const trimmed = items.slice(0, 5);
      if (items.length > 5) {
          try { notify(`eBay: взял первые 5 фото (из ${items.length})`); } catch {}
      }
      return trimmed;

  }

  function injectEbayButton(){
    if (!onEbay()) return;
    if (document.getElementById('meshok-ebay-btn')) return;

    const btn = document.createElement('button');
    btn.id='meshok-ebay-btn';
    btn.textContent='Собрать фото с eBay';
    Object.assign(btn.style,{
      position:'fixed', right:'16px', bottom:'60px', zIndex:2147483647,
      padding:'10px 14px', borderRadius:'10px', border:'none',
      background:'#85d04d', color:'#000', cursor:'pointer',
      boxShadow:'0 6px 16px rgba(0,0,0,.25)', font:'14px system-ui'
    });
    btn.addEventListener('click', async ()=>{
      btn.disabled=true; const o=btn.textContent; btn.textContent='Собираю…';
      await sleep(150);
      const items = collectFromEbay().filter(x=>/\.(jpe?g|png|webp|gif)(\b|$)/i.test(x.name));
      if (!items.length){ btn.textContent='Фото не найдены'; await sleep(1200); btn.textContent=o; btn.disabled=false; return; }

      // На eBay — порядок НЕ меняем!
      const lot = { from: location.href, title: document.title || 'eBay Lot', items };
      lotsPush(lot);
      notify(`Добавлено в очередь: ${items.length} фото (eBay)`);
      btn.textContent=`Готово: ${items.length} шт.`; await sleep(1200); btn.textContent=o; btn.disabled=false;
    });
    document.body.appendChild(btn);
  }

  /* ========== Meshok: загрузка файлов в input[type=file] ========== */
  function setFilesToInput(input, files){
    const dt = new DataTransfer();
    files.forEach(f=>dt.items.add(f));
    input.files = dt.files;
    input.dispatchEvent(new Event('change', {bubbles:true}));
  }

  function fetchBlob(url){
    return new Promise((resolve,reject)=>{
      GM_xmlhttpRequest({
        method:'GET', url, responseType:'blob', withCredentials:true,
        headers:{'Accept':'image/*'},
        onload:(res)=> (res.status>=200 && res.status<300 && res.response) ? resolve(res.response) : reject(new Error('HTTP '+res.status)),
        onerror:()=>reject(new Error('Network error')),
        ontimeout:()=>reject(new Error('Timeout'))
      });
    });
  }

    // Конвертация webp -> jpeg через canvas
    async function webpToJpegBlob(webpBlob, quality = 0.92){
        // Пытаемся через createImageBitmap (быстрее)
        const toBlobFromBitmap = async (bmp) => {
            const canvas = document.createElement('canvas');
            canvas.width = bmp.width; canvas.height = bmp.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(bmp, 0, 0);
            const jpegBlob = await new Promise(res => canvas.toBlob(res, 'image/jpeg', quality));
            return jpegBlob;
        };

        try {
            if ('createImageBitmap' in window) {
                const bmp = await createImageBitmap(webpBlob);
                const out = await toBlobFromBitmap(bmp);
                if (out) return out;
            }
        } catch(e){ /* fallback ниже */ }

        // Фоллбэк через <img>
        const url = URL.createObjectURL(webpBlob);
        try {
            const img = await new Promise((resolve, reject) => {
                const im = new Image();
                im.onload = () => resolve(im);
                im.onerror = reject;
                im.src = url;
            });
            const canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth || img.width;
            canvas.height = img.naturalHeight || img.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            const jpegBlob = await new Promise(res => canvas.toBlob(res, 'image/jpeg', quality));
            return jpegBlob;
        } finally {
            URL.revokeObjectURL(url);
        }
    }

    // Нормализация загруженного blob и имени файла
    async function normalizeBlobAndName(blob, name){
        const isWebp = (blob && blob.type === 'image/webp') || /\.webp$/i.test(name||'');
        if (isWebp){
            const jpeg = await webpToJpegBlob(blob, 0.92);
            const newName = (name || 'image.webp').replace(/\.webp$/i, '.jpg');
            return { blob: jpeg, name: newName, type: 'image/jpeg' };
        }
        // оставляем как есть
        return { blob, name, type: blob?.type || 'image/*' };
    }


  async function fileModeUploadLot(lot){
    const input = document.querySelector('input[type="file"][name="up_pic[]"]') ||
                  document.querySelector('input[type="file"][multiple]');
    if (!input){ alert('Не найден input[type=file] для загрузки.'); return; }

    // Подстраховка: если лот пришел из почты без перестановки — сдвинем (на eBay порядок не трогаем)
    if (/mail\.yandex\./.test(lot.from) && lot.items?.length>1) {
      lot.items = lot.items.slice(1).concat(lot.items[0]);
    }

    const files = [];
    for (const it of lot.items){
      try{
          let blob = await fetchBlob(it.url);
          let name = it.name;
          ({ blob, name } = await normalizeBlobAndName(blob, name)); // конвертируем webp -> jpeg при необходимости
          const type = blob.type || (/\.png$/i.test(name)?'image/png':/\.jpe?g$/i.test(name)?'image/jpeg':'image/*');
          files.push(new File([blob], name, { type }));

      }catch(e){ console.warn('Не скачал', it.url, e); }
    }
    if (!files.length){ alert('Не удалось скачать вложения. Открой письмо/лот заново и собери очередь ещё раз.'); return; }

    setFilesToInput(input, files);
    notify(`Загружено файлов: ${files.length}`, 'Meshok (FILE)');
  }

  /* ========== Панель на Мешке (одна, снизу слева) ========== */
  function injectMeshokPanel(){
    if (!onMeshok()) return;

    // Снесём любые старые ID панелей
    ['meshok-panel3','meshok-autofill-panel','meshok-autofill-panel-old','meshok-autofill-panel-v2']
      .forEach(id => { const el = document.getElementById(id); if (el) el.remove(); });
    if (document.getElementById('meshok-panel3')) return;

    const wrap = document.createElement('div');
    wrap.id = 'meshok-panel3';
    wrap.innerHTML = `
      <div style="position:fixed;left:16px;bottom:100px;z-index:2147483647;
                  display:flex;gap:8px;align-items:center;
                  padding:10px 14px;border-radius:12px;
                  background:rgba(20,20,20,.92);color:#fff;
                  box-shadow:0 6px 16px rgba(0,0,0,.25);
                  font:14px system-ui">
        <button id="btn-file-lot" style="padding:8px 12px;border-radius:8px;border:0;background:#ffd04d;color:#000;cursor:pointer;">
          Залить фото (файлы)
        </button>
        <span id="q-info" style="margin-left:8px;opacity:.9;"></span>
      </div>`;
    document.body.appendChild(wrap);

      const prefs = getUIPrefs();
      const panel = wrap.firstElementChild; // div с кнопкой
      panel.style.bottom = (prefs.bottom || 100) + 'px';
      panel.style.background = `rgba(20,20,20,${prefs.opacity ?? 0.92})`;
      panel.title = 'Alt+↑/↓ — сдвиг панели • Alt+O — прозрачность';


    const $info = wrap.querySelector('#q-info');
    const refresh = ()=>{
      const q = lotsGet();
      const head = q[0]?.items?.length || 0;
      $info.textContent = `Очередь: ${q.length}${head?` | 1-й: ${head} фото`:''}`;
    };
    refresh();

    wrap.querySelector('#btn-file-lot').addEventListener('click', async ()=>{
      const lot = lotsShift();
      if (!lot){ alert('Очередь пуста. Сначала соберите фото в письме/eBay.'); refresh(); return; }
      await fileModeUploadLot(lot);
      refresh();
    });

    GM_addValueChangeListener(KEY_QUEUE, refresh);
  }

    window.addEventListener('keydown', (e) => {
  if (!onMeshok() || !e.altKey) return;
  const panel = document.querySelector('#meshok-panel3 > div');
  if (!panel) return;

  // Alt + ArrowDown / ArrowUp — сдвиг по 20px
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault();
    const prefs = getUIPrefs();
    const delta = (e.key === 'ArrowDown') ? 20 : -20;
    const next = Math.max(0, (prefs.bottom || 100) + delta);
    panel.style.bottom = next + 'px';
    setUIPrefs({ bottom: next });
    return;
  }

  // Alt + O — циклическая прозрачность
  if (e.key.toLowerCase() === 'o') {
    e.preventDefault();
    const steps = [1, 0.85, 0.7, 0.55, 0.4];
    const cur = getUIPrefs().opacity ?? 0.92;
    const idx = steps.findIndex(v => Math.abs(v - cur) < 0.001);
    const next = steps[(idx + 1) % steps.length];
    panel.style.background = `rgba(20,20,20,${next})`;
    setUIPrefs({ opacity: next });
  }
}, true);


  /* ========== init ========== */
  function init(){
    if (onYandexMail()) injectMailButton();
    if (onEbay())       injectEbayButton();
    if (onMeshok())     injectMeshokPanel();
  }
  if (document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded', ()=>setTimeout(init, 200));
  } else {
    setTimeout(init, 200);
  }
  // поддержка SPA/динамики: если панели нет — создать заново
  new MutationObserver(()=>{ if (onMeshok() && !document.getElementById('meshok-panel3')) injectMeshokPanel(); })
    .observe(document.documentElement, {childList:true,subtree:true});
})();
