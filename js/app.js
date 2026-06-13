/*!
 * ISKVW Archive — app.js v4.0
 * Vanilla controller. No frameworks, no GSAP required.
 * Pages: home (index), 2d, 3d-immersion, obra, about, 404
 */
(() => {
  'use strict';

  // ---------- helpers ----------
  const $  = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const esc = (s = '') => String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  const buildEmbed = (url) => {
    if (!url) return '';
    const yt = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/))([\w-]{6,})/);
    if (yt) return `<iframe src="https://www.youtube.com/embed/${yt[1]}" title="Video" loading="lazy" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`;
    const vm = url.match(/vimeo\.com\/(\d+)/);
    if (vm) return `<iframe src="https://player.vimeo.com/video/${vm[1]}" title="Video" loading="lazy" allow="autoplay; fullscreen" allowfullscreen></iframe>`;
    return `<video controls preload="metadata" playsinline><source src="${esc(url)}" type="video/mp4"></video>`;
  };

  // ---------- state ----------
  const App = {
    page: document.body.dataset.page || 'home',
    works: [],
    filtered: [],
    cat: 'all',
    lastFocus: null,
    trapHandler: null,
  };

  // ---------- preloader (a single italic word, like a magazine cover) ----------
  const PRELOADER_MIN = 1500;
  const PRELOADER_MAX = 3500;
  let preStart = 0;

  function initPreloader() {
    const pre = $('#preloader');
    if (!pre) { document.body.classList.add('is-loaded'); return; }
    preStart = performance.now();

    const word = $('.preloader-word', pre);
    if (word) requestAnimationFrame(() => word.classList.add('show'));

    let p = 0;
    const id = setInterval(() => {
      p += Math.floor(Math.random() * 8) + 4;
      if (p >= 100) { p = 100; clearInterval(id); }
      pre.dataset.p = String(p);
      if (p === 100) {
        const elapsed = performance.now() - preStart;
        const wait = Math.max(450, PRELOADER_MIN - elapsed);
        setTimeout(hidePreloader, wait);
      }
    }, 70);
    setTimeout(hidePreloader, PRELOADER_MAX);
  }

  function hidePreloader() {
    const pre = $('#preloader');
    if (!pre || pre.dataset.gone === '1') return;
    pre.dataset.gone = '1';
    pre.style.transition = 'opacity .9s cubic-bezier(.7,0,.3,1), visibility .9s';
    pre.style.opacity = '0';
    pre.style.visibility = 'hidden';
    document.body.classList.add('is-loaded');
    setTimeout(() => { pre.style.display = 'none'; }, 950);
  }

  // ---------- mobile menu ----------
  function initMenu() {
    const tog = $('#nav-toggle');
    const menu = $('#mobile-nav');
    const back = $('#mobile-nav-backdrop');
    if (!tog || !menu) return;
    const set = (open) => {
      menu.classList.toggle('open', open);
      back && back.classList.toggle('open', open);
      tog.setAttribute('aria-expanded', open);
      document.body.style.overflow = open ? 'hidden' : '';
    };
    tog.addEventListener('click', () => set(!menu.classList.contains('open')));
    back && back.addEventListener('click', () => set(false));
    menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => set(false)));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') set(false); });
  }

  // ---------- reveal ----------
  let observer;
  function initReveal() {
    if (reduced()) {
      $$('.work, .reveal').forEach(el => el.classList.add('is-visible'));
      return;
    }
    observer = new IntersectionObserver((entries) => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          en.target.classList.add('is-visible');
          observer.unobserve(en.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
  }
  function observe(el) { observer ? observer.observe(el) : el.classList.add('is-visible'); }

  // ---------- data ----------
  async function fetchWorks() {
    try {
      const r = await fetch('data/works.json', { cache: 'no-cache' });
      App.works = await r.json();
    } catch (e) {
      console.error('[ISKVW]', e);
      App.works = [];
    }
    if (App.page === '2d') {
      App.works = App.works.filter(w =>
        (w.category && /2d|ilustr|foto|graphic/i.test(w.category)) || w.mediaType === 'image'
      );
    }
    App.filtered = App.works.slice();
  }

  // ---------- gallery (home) ----------
  function renderGallery() {
    const grid = $('#works');
    if (!grid) return;
    grid.innerHTML = '';
    if (!App.filtered.length) {
      grid.innerHTML = '<p class="empty">No hay obras en esta categoría.</p>';
      return;
    }
    const frag = document.createDocumentFragment();
    App.filtered.forEach((w, i) => frag.appendChild(buildCard(w, i)));
    grid.appendChild(frag);
    grid.querySelectorAll('.work').forEach(observe);
  }

  function buildCard(w, i) {
    const art = document.createElement('article');
    art.className = 'work';
    art.tabIndex = 0;
    art.setAttribute('role', 'button');
    art.setAttribute('aria-label', `Abrir detalle: ${w.title}`);

    const isVid = w.mediaType === 'video' && w.src && /\.(mp4|webm|ogg)$/i.test(w.src);
    const img = w.image || w.src || w.poster || '';
    const media = isVid
      ? `<video muted loop playsinline preload="metadata" poster="${esc(w.poster || img)}"><source src="${esc(w.src)}" type="video/mp4"></video>`
      : `<img src="${esc(img)}" alt="${esc(w.title)} — ${esc(w.category || '')}" loading="lazy" decoding="async">`;

    const flag = w.placeholder
      ? '<span class="work-flag is-wip" title="Placeholder, será reemplazada por una obra real">[ WIP ]</span>'
      : (w.year ? `<span class="work-flag">${esc(w.year)}</span>` : '');

    art.innerHTML = `
      <div class="work-frame">
        ${flag}
        ${media}
        <span class="work-cta">Abrir →</span>
      </div>
      <div class="work-meta">
        <div>
          <h3 class="work-title">${esc(w.title)}</h3>
          <p class="work-tech">${esc(w.technique || w.category || '')}</p>
        </div>
        <span class="work-num">${String(i + 1).padStart(2,'0')} / ${String(App.filtered.length).padStart(2,'0')}</span>
      </div>`;

    if (isVid) {
      const v = art.querySelector('video');
      art.addEventListener('mouseenter', () => v.play().catch(()=>{}));
      art.addEventListener('mouseleave', () => { v.pause(); v.currentTime = 0; });
    }
    const open = () => {
      if (w.template === '3d-immersion' && App.page !== '3d') location.href = '3d-immersion.html';
      else openLB(w);
    };
    art.addEventListener('click', open);
    art.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
    });
    return art;
  }

  // ---------- masonry (2d) ----------
  function renderMasonry() {
    const grid = $('#masonry');
    if (!grid) return;
    grid.innerHTML = '';
    if (!App.works.length) { grid.innerHTML = '<p class="empty">Sin entradas.</p>'; return; }
    const frag = document.createDocumentFragment();
    App.works.forEach((w, i) => {
      const art = document.createElement('article');
      art.className = 'work';
      art.tabIndex = 0;
      art.setAttribute('role','button');
      art.setAttribute('aria-label', `Abrir ilustración: ${w.title}`);
      const flag = w.placeholder ? '<span class="work-flag is-wip">[ WIP ]</span>' : '';
      art.innerHTML = `
        <div class="work-frame">
          ${flag}
          <img src="${esc(w.image || w.src)}" alt="${esc(w.title)}" loading="lazy" decoding="async">
          <span class="work-cta">Abrir →</span>
        </div>
        <div class="work-meta">
          <div>
            <h3 class="work-title">${esc(w.title)}</h3>
            <p class="work-tech">${esc(w.technique || '')}</p>
          </div>
          <span class="work-num">${String(i+1).padStart(2,'0')}</span>
        </div>`;
      const open = () => openLB(w);
      art.addEventListener('click', open);
      art.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
      frag.appendChild(art);
    });
    grid.appendChild(frag);
    grid.querySelectorAll('.work').forEach(observe);
  }

  // ---------- filters ----------
  function renderFilters() {
    const nav = $('#filters');
    if (!nav) return;
    const counts = { all: App.works.length };
    App.works.forEach(w => {
      const c = w.category || '—';
      counts[c] = (counts[c] || 0) + 1;
    });
    const cats = Object.keys(counts).filter(c => c !== 'all').sort();
    const btns = [['all','Todas'], ...cats.map(c => [c, c])];
    nav.innerHTML = btns.map(([id,label]) => `
      <button class="filter-btn" data-cat="${esc(id)}" aria-pressed="${id === 'all'}">
        ${esc(label)}<span class="filter-count">${counts[id]||0}</span>
      </button>`).join('');
    nav.querySelectorAll('.filter-btn').forEach(b => {
      b.addEventListener('click', () => {
        nav.querySelectorAll('.filter-btn').forEach(x => x.setAttribute('aria-pressed','false'));
        b.setAttribute('aria-pressed','true');
        applyFilter(b.dataset.cat);
      });
    });
  }
  function applyFilter(cat) {
    App.cat = cat;
    App.filtered = (cat === 'all') ? App.works.slice() : App.works.filter(w => (w.category||'').toLowerCase() === cat.toLowerCase());
    const grid = $('#works');
    if (!grid) return;
    grid.style.transition = 'opacity .25s ease';
    grid.style.opacity = '0';
    setTimeout(() => { renderGallery(); grid.style.opacity = '1'; }, 220);
  }

  // ---------- lightbox ----------
  function openLB(w) {
    const lb = $('#lb');
    const ct = $('#lb-content');
    if (!lb || !ct) return;
    App.lastFocus = document.activeElement;

    const gallery = (Array.isArray(w.gallery) && w.gallery.length) ? w.gallery : [w.image || w.src].filter(Boolean);
    const isVid = w.mediaType === 'video' && w.src && /\.(mp4|webm|ogg)$/i.test(w.src);
    const main = isVid
      ? `<video controls autoplay muted loop playsinline poster="${esc(w.poster||'')}"><source src="${esc(w.src)}" type="video/mp4"></video>`
      : `<img id="lb-main" src="${esc(gallery[0])}" alt="${esc(w.title)}">`;

    const thumbs = (gallery.length > 1)
      ? `<div class="lb-thumbs">${gallery.map((g,i) => `<img class="lb-thumb${i===0?' active':''}" data-full="${esc(g)}" src="${esc(g)}" alt="">`).join('')}</div>`
      : '';

    const tags = (w.tags||[]).map(t => `<span>${esc(t)}</span>`).join('');
    const videoEmb = (w.video && !isVid) ? `<div class="lb-video">${buildEmbed(w.video)}</div>` : '';

    // siblings for prev/next
    const idx = App.filtered.findIndex(x => x.id === w.id);
    const prev = idx > 0 ? App.filtered[idx - 1] : null;
    const next = idx >= 0 && idx < App.filtered.length - 1 ? App.filtered[idx + 1] : null;

    ct.innerHTML = `
      <div class="lb-media">
        <div class="lb-media-main">${main}</div>
        ${thumbs}
      </div>
      <div class="lb-data">
        <span class="lb-cat">${esc(w.category||'')} ${w.placeholder ? '· [WIP]' : ''}</span>
        <h2 class="lb-title">${esc(w.title)}</h2>
        <p class="lb-desc">${esc(w.descriptionLong || w.description || '')}</p>
        ${videoEmb}
        ${tags ? `<div class="lb-tags">${tags}</div>` : ''}
        <dl class="lb-meta">
          ${w.technique ? `<dt>Técnica</dt><dd>${esc(w.technique)}</dd>` : ''}
          ${w.year ? `<dt>Año</dt><dd>${esc(w.year)}</dd>` : ''}
          ${w.id ? `<dt>ID</dt><dd>${esc(w.id)}</dd>` : ''}
        </dl>
        <div class="lb-nav">
          <button data-dir="prev" ${prev?'':'disabled'}>← ${prev ? esc(prev.title) : 'inicio'}</button>
          <button data-dir="next" ${next?'':'disabled'}>${next ? esc(next.title) : 'fin'} →</button>
        </div>
      </div>`;

    ct.querySelectorAll('.lb-thumb').forEach(t => {
      t.addEventListener('click', () => {
        const m = ct.querySelector('#lb-main');
        if (!m) return;
        m.style.opacity = '0';
        setTimeout(() => { m.src = t.dataset.full; m.style.opacity = '1'; }, 180);
        ct.querySelectorAll('.lb-thumb').forEach(x => x.classList.remove('active'));
        t.classList.add('active');
      });
    });

    ct.querySelectorAll('.lb-nav button').forEach(b => {
      b.addEventListener('click', () => {
        const target = b.dataset.dir === 'prev' ? prev : next;
        if (target) openLB(target);
      });
    });

    lb.classList.add('active');
    lb.removeAttribute('aria-hidden');
    document.body.style.overflow = 'hidden';

    if (w.id) {
      const url = new URL(location.href);
      url.searchParams.set('id', w.id);
      history.pushState({ id: w.id }, '', url);
    }
    setupTrap(lb);
    setTimeout(() => $('.lb-close')?.focus(), 80);
  }

  function closeLB() {
    const lb = $('#lb');
    const ct = $('#lb-content');
    if (!lb) return;
    lb.classList.remove('active');
    lb.setAttribute('aria-hidden','true');
    document.body.style.overflow = '';
    if (App.trapHandler) { lb.removeEventListener('keydown', App.trapHandler); App.trapHandler = null; }
    App.lastFocus?.focus?.();
    setTimeout(() => { if (ct) ct.innerHTML = ''; }, 360);
    if (location.search.includes('id=')) {
      const url = new URL(location.href);
      url.searchParams.delete('id');
      history.replaceState({}, '', url.pathname + (url.search || ''));
    }
  }

  function setupTrap(c) {
    const els = c.querySelectorAll('a[href], button, video, input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (!els.length) return;
    const f = els[0], l = els[els.length-1];
    App.trapHandler = (e) => {
      if (e.key !== 'Tab') return;
      if (e.shiftKey && document.activeElement === f) { e.preventDefault(); l.focus(); }
      else if (!e.shiftKey && document.activeElement === l) { e.preventDefault(); f.focus(); }
    };
    c.addEventListener('keydown', App.trapHandler);
  }

  // ---------- listeners ----------
  function initListeners() {
    $('.lb-close')?.addEventListener('click', closeLB);
    const lb = $('#lb');
    lb?.addEventListener('click', e => { if (e.target === lb) closeLB(); });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && lb?.classList.contains('active')) closeLB();
      if (lb?.classList.contains('active')) {
        if (e.key === 'ArrowRight') $('.lb-nav button[data-dir="next"]')?.click();
        if (e.key === 'ArrowLeft')  $('.lb-nav button[data-dir="prev"]')?.click();
      }
    });
    addEventListener('popstate', () => {
      const id = new URL(location.href).searchParams.get('id');
      if (!id && lb?.classList.contains('active')) closeLB();
      else if (id) {
        const w = App.works.find(w => w.id === id);
        if (w) openLB(w);
      }
    });
  }

  function checkDeepLink() {
    const id = new URL(location.href).searchParams.get('id');
    if (!id) return;
    const w = App.works.find(w => w.id === id);
    if (w) setTimeout(() => openLB(w), 700);
  }

  // ---------- boot ----------
  async function boot() {
    initMenu();
    initReveal();
    initListeners();
    initPreloader();

    if (App.page === '3d' || App.page === 'about' || App.page === '404' || App.page === 'obra') {
      $$('.reveal').forEach(observe);
      return;
    }

    await fetchWorks();
    if (App.page === 'home') { renderFilters(); renderGallery(); }
    else if (App.page === '2d') { renderMasonry(); }
    $$('.reveal').forEach(observe);
    checkDeepLink();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  // public hook for n8n / curator
  window.ISKVW = {
    refresh: async () => {
      await fetchWorks();
      App.page === 'home' ? (renderFilters(), renderGallery()) : renderMasonry();
    },
    open: (id) => { const w = App.works.find(w => w.id === id); if (w) openLB(w); },
    close: closeLB,
    state: App,
  };
})();
