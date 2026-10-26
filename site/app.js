// Présentation des polices : lit fonts.json (généré par tools/fonts.py site) et construit une section
// par police à partir du modèle #tpl-font. Chaque police est chargée sous un nom interne (« spec-<id> »)
// pour ne pas se mélanger avec les polices de l'interface.
(function () {
  'use strict';

  var root = document.documentElement;
  var status = document.getElementById('status');
  var STATUS_BADGE = { 'bêta': 'gr-badge--beta', 'stable': 'gr-badge--done', 'retirée': 'gr-badge--retired' };
  var LICENSES = { 'OFL-1.1': 'SIL Open Font License 1.1' };

  // ---------- Thème (Parchemin / Crypte) ----------
  (function themeToggle() {
    var sw = document.getElementById('theme-switch');
    var state = sw.querySelector('.gr-toggle__state');
    var sun = sw.querySelector('[data-icon="sun"]'), moon = sw.querySelector('[data-icon="moon"]');
    function render() {
      var dark = root.getAttribute('data-theme') === 'dark';
      sw.setAttribute('aria-checked', dark ? 'true' : 'false');
      state.textContent = dark ? 'Oui' : 'Non';
      sun.hidden = dark; moon.hidden = !dark;
    }
    sw.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      render();
    });
    render();
  })();

  // ---------- Outils ----------
  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function q(scope, sel) { return scope.querySelector(sel); }
  function family(font) { return '"spec-' + font.id + '"'; }
  function codePoint(ch) { return 'U+' + ch.codePointAt(0).toString(16).toUpperCase().padStart(4, '0'); }
  function dateFr(iso) {
    var d = new Date(iso + 'T12:00:00');
    return isNaN(d) ? iso : d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
  }
  function announce(text) { status.textContent = text; setTimeout(function () { status.textContent = ''; }, 2000); }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve, reject) {
      var area = el('textarea', { readonly: '' });
      area.value = text; area.style.position = 'fixed'; area.style.opacity = '0';
      document.body.appendChild(area); area.select();
      var ok = document.execCommand('copy'); area.remove();
      ok ? resolve() : reject();
    });
  }

  function loadFaces(font) {
    return Promise.all(font.styles.map(function (s) {
      var face = new FontFace('spec-' + font.id, 'url("' + s.woff2 + '") format("woff2")', { weight: String(s.weight), display: 'swap' });
      document.fonts.add(face);
      return face.load().catch(function () {});
    }));
  }

  // ---------- Une police ----------
  function renderFont(font, repo) {
    var node = document.getElementById('tpl-font').content.firstElementChild.cloneNode(true);
    var spec = font.specimen;
    var crisp = (spec.crispSizes || []).map(String);
    node.id = font.id;
    node.setAttribute('aria-labelledby', font.id + '-title');

    var name = q(node, '[data-name]');
    name.id = font.id + '-title';
    name.textContent = font.name;
    name.style.fontFamily = family(font) + ', var(--font-display)';

    // Étiquettes : version, statut, licence
    var chips = q(node, '[data-chips]');
    var v = el('li'); v.appendChild(el('span', { 'class': 'gr-badge gr-badge--new' }));
    v.firstChild.appendChild(el('span', { 'class': 'gr-badge__mark', 'aria-hidden': 'true' }, '✦'));
    v.firstChild.appendChild(document.createTextNode('Version ' + font.version));
    chips.appendChild(v);
    if (font.status) {
      var st = el('li'); st.appendChild(el('span', { 'class': 'gr-badge ' + (STATUS_BADGE[font.status] || '') }, font.status));
      chips.appendChild(st);
    }
    (font.tags || []).forEach(function (t) {
      var li = el('li'); li.appendChild(el('span', { 'class': 'gr-chip' }, t)); chips.appendChild(li);
    });

    q(node, '[data-summary]').textContent = font.summary;
    var desc = q(node, '[data-description]');
    if (font.description) desc.textContent = font.description; else desc.remove();

    // Fiche
    var facts = q(node, '[data-facts]');
    function fact(label, value) {
      facts.appendChild(el('dt', {}, label));
      var dd = el('dd'); typeof value === 'string' ? dd.textContent = value : dd.appendChild(value); facts.appendChild(dd);
    }
    fact('Dessin', font.designer);
    if (font.basedOn) {
      var a = el('a', { href: font.basedOn.url }, font.basedOn.name);
      var span = el('span'); span.append('Dérivée de ', a); fact('Origine', span);
    }
    fact('Graisses', font.styles.map(function (s) { return s.name + ' (' + s.weight + ')'; }).join(', '));
    fact('Glyphes', String(Array.from(font.glyphs).length));
    fact('Licence', LICENSES[font.license] || font.license);
    if (font.changelog.length) fact('Mise à jour', dateFr(font.changelog[0].date));
    if (font.usage) fact('Usage', font.usage);

    // Actions
    var actions = q(node, '[data-actions]');
    var dl = el('a', { 'class': 'gr-btn gr-btn--primary', href: font.download, download: '' });
    dl.appendChild(el('span', { 'class': 'gr-btn__star', 'aria-hidden': 'true' }, '✦'));
    dl.appendChild(document.createTextNode('Télécharger la ' + font.version + ' (zip)'));
    dl.appendChild(el('span', { 'class': 'gr-btn__star', 'aria-hidden': 'true' }, '✦'));
    actions.appendChild(dl);
    actions.appendChild(el('a', { 'class': 'gr-btn', href: font.source }, 'Voir les sources'));
    actions.appendChild(el('a', { 'class': 'gr-btn gr-btn--ghost', href: repo + '/releases?q=' + encodeURIComponent(font.id) }, 'Toutes les versions'));

    // Banc d'essai
    var tester = q(node, '[data-tester]');
    var out = q(tester, '[data-out]'), caption = q(tester, '[data-caption]'), value = q(tester, '[data-value]');
    var text = q(tester, '[data-input="text"]'), weight = q(tester, '[data-input="weight"]'), size = q(tester, '[data-input="size"]');
    ['text', 'weight', 'size'].forEach(function (k) {
      var input = q(tester, '[data-input="' + k + '"]'), id = font.id + '-tt-' + k;
      input.id = id; q(tester, '[data-for="' + k + '"]').setAttribute('for', id);
    });
    value.setAttribute('for', size.id);
    text.value = spec.sample || spec.headline || font.name;
    font.styles.forEach(function (s) { weight.appendChild(el('option', { value: s.weight }, s.name)); });
    size.min = spec.minSize || 16; size.max = spec.maxSize || 128; size.value = spec.defaultSize || 64;
    // Sur un écran étroit, on part de la plus petite taille nette (ou de la moitié) pour garder des mots entiers
    if (window.matchMedia('(max-width: 40rem)').matches) size.value = crisp[0] || Math.max(size.min, Math.round(size.value / 2));
    out.style.fontFamily = family(font);
    function renderTester() {
      var isCrisp = crisp.indexOf(size.value) !== -1;
      out.textContent = text.value.trim() || 'Tape un texte';
      out.style.fontWeight = weight.value;
      out.style.fontSize = size.value + 'px';
      value.textContent = size.value + ' px';
      value.classList.toggle('is-crisp', isCrisp);
      size.setAttribute('aria-valuetext', size.value + ' pixels' + (isCrisp ? ', taille nette' : ''));
      caption.textContent = font.name + ' · ' + weight.options[weight.selectedIndex].textContent + ' · ' +
        size.value + ' px' + (isCrisp ? ' ✦ net' : '');
    }
    [text, weight, size].forEach(function (i) { i.addEventListener('input', renderTester); i.addEventListener('change', renderTester); });
    renderTester();

    // Graisses
    var weights = q(node, '[data-weights]');
    if (font.styles.length < 2) q(node, '[data-weights-section]').remove();
    font.styles.forEach(function (s) {
      var li = el('li');
      li.appendChild(el('span', { 'class': 'gr-meta' }, s.name + ' · ' + s.weight));
      var p = el('span', { 'class': 'weights__sample' }, spec.headline || font.name);
      p.style.fontFamily = family(font); p.style.fontWeight = s.weight;
      li.appendChild(p);
      weights.appendChild(li);
    });

    // Glyphes : liste à sélection unique, flèches pour se déplacer
    var chars = Array.from(font.glyphs);
    q(node, '[data-glyphs-title]').textContent = 'Glyphes (' + chars.length + ')';
    var grid = q(node, '[data-glyphs]'), big = q(node, '[data-zoom-char]'), code = q(node, '[data-zoom-code]');
    grid.setAttribute('aria-label', 'Glyphes de ' + font.name);
    grid.style.fontFamily = big.style.fontFamily = family(font);
    var cells = chars.map(function (ch, i) {
      var b = el('button', { type: 'button', 'class': 'glyph', role: 'option', 'aria-selected': 'false',
        'aria-label': ch + ' (' + codePoint(ch) + ')', tabindex: i === 0 ? '0' : '-1' }, ch);
      b.addEventListener('click', function () { select(i, false); });
      grid.appendChild(b);
      return b;
    });
    var current = 0;
    function select(i, focus) {
      cells[current].setAttribute('aria-selected', 'false'); cells[current].tabIndex = -1;
      current = i;
      cells[i].setAttribute('aria-selected', 'true'); cells[i].tabIndex = 0;
      if (focus) cells[i].focus();
      big.textContent = chars[i];
      code.textContent = codePoint(chars[i]);
    }
    grid.addEventListener('keydown', function (e) {
      var cols = Math.max(1, Math.round(grid.clientWidth / cells[0].offsetWidth));
      var to = { ArrowRight: current + 1, ArrowLeft: current - 1, ArrowDown: current + cols, ArrowUp: current - cols,
        Home: 0, End: cells.length - 1 }[e.key];
      if (to === undefined) return;
      e.preventDefault();
      select(Math.min(cells.length - 1, Math.max(0, to)), true);
    });
    var firstLetter = chars.indexOf('A');
    if (cells.length) select(firstLetter > -1 ? firstLetter : 0, false);

    // CSS à copier
    var cssName = font.name.replace(/\s+/g, '');
    var css = font.styles.map(function (s) {
      return '@font-face {\n  font-family: "' + font.name + '";\n  src: url("fonts/' + cssName + '-' + s.name +
        '.woff2") format("woff2");\n  font-weight: ' + s.weight + ';\n  font-style: normal;\n  font-display: swap;\n}';
    }).join('\n') + '\n\nh1, h2, h3 {\n  font-family: "' + font.name + '", Georgia, serif;\n}';
    q(node, '[data-css]').textContent = css;
    var copy = q(node, '[data-copy]'), copyLabel = q(copy, '.gr-code__action-text');
    copy.setAttribute('aria-label', 'Copier le CSS de ' + font.name);
    copy.addEventListener('click', function () {
      copyText(css).then(function () { copyLabel.textContent = 'Copié'; announce('CSS copié.'); },
        function () { announce('Copie impossible : sélectionne le texte à la main.'); });
      setTimeout(function () { copyLabel.textContent = 'Copier'; }, 2000);
    });

    // Historique (accordéon, la dernière version ouverte)
    var history = q(node, '[data-history]');
    var triggers = [];
    font.changelog.forEach(function (release, i) {
      var id = font.id + '-v' + release.version.replace(/\./g, '-');
      var item = el('div', { 'class': 'gr-accordion__item' });
      var h = el('h4', { 'class': 'gr-accordion__heading' });
      var t = el('button', { type: 'button', 'class': 'gr-accordion__trigger', id: id + '-t', 'aria-controls': id + '-p', 'aria-expanded': 'false' });
      t.appendChild(el('span', { 'class': 'gr-accordion__star', 'aria-hidden': 'true' }, '✦'));
      t.appendChild(el('span', { 'class': 'gr-accordion__label' }, 'Version ' + release.version + ' · ' + dateFr(release.date)));
      t.insertAdjacentHTML('beforeend', '<svg class="gr-icon gr-accordion__caret" viewBox="0 0 256 256" aria-hidden="true"><path d="M212.24,100.24l-80,80a6,6,0,0,1-8.48,0l-80-80a6,6,0,0,1,8.48-8.48L128,167.51l75.76-75.75a6,6,0,0,1,8.48,8.48Z"/></svg>');
      h.appendChild(t);
      var panel = el('div', { 'class': 'gr-accordion__panel', id: id + '-p', role: 'region', 'aria-labelledby': id + '-t' });
      var inner = el('div', { 'class': 'gr-accordion__inner changes' });
      release.sections.forEach(function (sec) {
        inner.appendChild(el('h5', {}, { 'Features': 'Nouveautés', 'Bug Fixes': 'Corrections', 'Performance Improvements': 'Performances' }[sec.title] || sec.title));
        var ul = el('ul');
        sec.items.forEach(function (html) { var li = el('li'); li.innerHTML = html; ul.appendChild(li); });
        inner.appendChild(ul);
      });
      if (release.url) {
        var p = el('p', { 'class': 'gr-meta' }); p.appendChild(el('a', { href: release.url }, 'Comparer avec la version précédente'));
        inner.appendChild(p);
      }
      panel.appendChild(inner);
      item.appendChild(h); item.appendChild(panel);
      history.appendChild(item);
      triggers.push(t);
      setOpen(t, i === 0);
    });
    function setOpen(t, open) {
      var panel = document.getElementById(t.getAttribute('aria-controls')) || q(history, '#' + t.getAttribute('aria-controls'));
      t.setAttribute('aria-expanded', open ? 'true' : 'false');
      panel.classList.toggle('is-open', open);
      panel.inert = !open;
    }
    triggers.forEach(function (t) {
      t.addEventListener('click', function () { setOpen(t, t.getAttribute('aria-expanded') !== 'true'); });
    });

    return node;
  }

  function renderIndexCard(font) {
    var li = el('li');
    var a = el('a', { 'class': 'gr-tile', href: '#' + font.id });
    var art = el('span', { 'class': 'gr-tile__art gr-frame', 'aria-hidden': 'true' }, 'Aa');
    art.style.fontFamily = family(font);
    a.appendChild(art);
    a.appendChild(el('span', { 'class': 'gr-tile__name' }, font.name));
    a.appendChild(el('span', { 'class': 'gr-tile__kind' }, 'Version ' + font.version + ' · ' + font.summary));
    li.appendChild(a);
    return li;
  }

  fetch('fonts.json')
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (data) {
      var fonts = data.fonts;
      var nav = document.getElementById('nav'), index = document.getElementById('index'), list = document.getElementById('fonts');
      fonts.forEach(function (font) {
        loadFaces(font);
        var li = el('li'); li.appendChild(el('a', { href: '#' + font.id }, font.name)); nav.appendChild(li);
        index.appendChild(renderIndexCard(font));
        list.appendChild(renderFont(font, data.repo));
      });
      var glyphs = fonts.reduce(function (n, f) { return n + Array.from(f.glyphs).length; }, 0);
      document.getElementById('stats').textContent = fonts.length + (fonts.length > 1 ? ' polices' : ' police') +
        ' · ' + glyphs + ' glyphes au total';
      if (location.hash) { var target = document.getElementById(location.hash.slice(1)); if (target) target.scrollIntoView(); }
    })
    .catch(function () {
      document.getElementById('stats').textContent = 'Impossible de charger la liste des polices. Elles restent disponibles sur GitHub.';
    });
})();
