/* hungyi-tw.net — 行為層
   三件事：語言切換、主題切換、低調的進場過場。
   沒有這個檔案網站仍然完整可讀（預設中文、淺色、全部內容可見）。 */
(function () {
  'use strict';

  var root = document.documentElement;

  function store(key, val) { try { localStorage.setItem(key, val); } catch (e) {} }
  function load(key) { try { return localStorage.getItem(key); } catch (e) { return null; } }

  /* ---------- 語言切換 ---------- */
  var LANGS = { zh: { html: 'zh-Hant-TW', next: 'en', label: 'EN' },
                en: { html: 'en',          next: 'zh', label: '中文' } };

  function currentLang() { return root.getAttribute('data-lang') === 'en' ? 'en' : 'zh'; }

  function applyLang(lang) {
    var cfg = LANGS[lang];
    root.setAttribute('data-lang', lang);
    root.setAttribute('lang', cfg.html);
    var title = root.getAttribute('data-title-' + lang);
    if (title) document.title = title;
    var desc = root.getAttribute('data-desc-' + lang);
    var metaDesc = document.querySelector('meta[name="description"]');
    if (desc && metaDesc) metaDesc.setAttribute('content', desc);
    Array.prototype.forEach.call(document.querySelectorAll('[data-lang-toggle]'), function (btn) {
      btn.textContent = cfg.label;
      btn.setAttribute('data-lang-label', cfg.next === 'zh' ? 'zh' : 'en');
      btn.setAttribute('aria-label', lang === 'zh' ? 'Switch to English' : '切換為中文');
    });
  }

  var savedLang = load('lang');
  if (savedLang !== 'zh' && savedLang !== 'en') {
    // 沒有偏好時，非中文瀏覽器預設英文
    savedLang = /^zh/i.test(navigator.language || '') ? 'zh' : 'en';
  }
  applyLang(savedLang);

  Array.prototype.forEach.call(document.querySelectorAll('[data-lang-toggle]'), function (btn) {
    btn.addEventListener('click', function () {
      var next = LANGS[currentLang()].next;
      applyLang(next);
      store('lang', next);
    });
  });

  /* ---------- 主題切換 ---------- */
  function systemTheme() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function currentTheme() { return root.getAttribute('data-theme') || systemTheme(); }

  Array.prototype.forEach.call(document.querySelectorAll('[data-theme-toggle]'), function (btn) {
    function sync() {
      var next = currentTheme() === 'dark' ? 'LIGHT' : 'DARK';
      btn.textContent = next;
      btn.setAttribute('aria-label', next === 'DARK' ? '切換為深色主題 / Switch to dark theme'
                                                     : '切換為淺色主題 / Switch to light theme');
    }
    sync();
    btn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      store('theme', next);
      sync();
    });
  });

  /* ---------- 進場過場 ---------- */
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var targets = document.querySelectorAll('.reveal');

  if (reduced || !('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add('is-in'); });
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      var el = entry.target;
      var delay = (parseInt(el.getAttribute('data-reveal-index'), 10) || 0) % 3 * 60;
      setTimeout(function () { el.classList.add('is-in'); }, delay);
      observer.unobserve(el);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

  Array.prototype.forEach.call(targets, function (el, i) {
    if (!el.hasAttribute('data-reveal-index')) el.setAttribute('data-reveal-index', String(i));
    observer.observe(el);
  });
})();
