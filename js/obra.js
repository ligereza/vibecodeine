/*! obra.js — render dedicated detail page (obra.html?id=...) */
(() => {
  'use strict';
  const esc = (s='') => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  const buildEmbed = (url) => {
    if (!url) return '';
    const yt = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/))([\w-]{6,})/);
    if (yt) return `<iframe src="https://www.youtube.com/embed/${yt[1]}" title="Video" loading="lazy" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`;
    const vm = url.match(/vimeo\.com\/(\d+)/);
    if (vm) return `<iframe src="https://player.vimeo.com/video/${vm[1]}" title="Video" loading="lazy" allow="autoplay; fullscreen" allowfullscreen></iframe>`;
    return `<video controls preload="metadata" playsinline><source src="${esc(url)}" type="video/mp4"></video>`;
  };

  async function init() {
    const id = new URLSearchParams(location.search).get('id');
    const root = document.getElementById('obra');
    if (!root) return;
    if (!id) { root.innerHTML = '<p class="empty" style="grid-column:1/-1;">Falta el parámetro ?id=</p>'; return; }
    let works;
    try { works = await (await fetch('data/works.json', { cache: 'no-cache' })).json(); }
    catch { root.innerHTML = '<p class="empty" style="grid-column:1/-1;">Archivo no disponible.</p>'; return; }

    const w = works.find(x => x.id === id);
    if (!w) { root.innerHTML = '<p class="empty" style="grid-column:1/-1;">Obra no encontrada.</p>'; return; }

    document.title = `${w.title} · ISKVW`;
    const m = (sel, val) => document.querySelector(sel)?.setAttribute('content', val);
    m('meta[name="description"]', w.description || '');
    m('meta[property="og:title"]', `${w.title} · ISKVW`);
    m('meta[property="og:description"]', w.description || '');
    m('meta[property="og:image"]', w.image || w.src || '');
    m('meta[name="twitter:image"]', w.image || w.src || '');

    const gallery = (Array.isArray(w.gallery) && w.gallery.length) ? w.gallery : [w.image || w.src].filter(Boolean);
    const isVid = w.mediaType === 'video' && w.src && /\.(mp4|webm|ogg)$/i.test(w.src);
    const cover = isVid
      ? `<video controls preload="metadata" playsinline poster="${esc(w.poster||'')}"><source src="${esc(w.src)}" type="video/mp4"></video>`
      : `<img id="cover-img" src="${esc(gallery[0])}" alt="${esc(w.title)}">`;
    const thumbs = gallery.length > 1
      ? `<div class="obra-thumbs">${gallery.map((g,i) => `<img class="${i===0?'active':''}" data-full="${esc(g)}" src="${esc(g)}" alt="">`).join('')}</div>`
      : '';
    const videoEmb = (w.video && !isVid) ? `<div class="lb-video">${buildEmbed(w.video)}</div>` : '';

    root.innerHTML = `
      <div>
        <div class="obra-cover">${cover}</div>
        ${thumbs}
      </div>
      <aside class="obra-data">
        <span class="obra-cat">${esc(w.category||'')} ${w.placeholder ? '· [WIP]' : ''}</span>
        <h1 class="obra-title">${esc(w.title)}</h1>
        <p class="obra-tech">${esc(w.technique || '')}${w.year ? ` · ${esc(w.year)}` : ''}</p>
        <p class="obra-desc">${esc(w.descriptionLong || w.description || '')}</p>
        ${videoEmb}
        <a href="index.html" class="obra-back">← Volver al archivo</a>
      </aside>`;

    root.querySelectorAll('.obra-thumbs img').forEach(t => {
      t.addEventListener('click', () => {
        const main = document.getElementById('cover-img');
        if (!main) return;
        main.style.opacity = '0';
        setTimeout(() => { main.src = t.dataset.full; main.style.opacity = '1'; }, 180);
        root.querySelectorAll('.obra-thumbs img').forEach(x => x.classList.remove('active'));
        t.classList.add('active');
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
