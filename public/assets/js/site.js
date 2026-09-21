/* Ian 個人網頁 — 行為層
   只做兩件事：主題切換、低調的進場過場。
   沒有這個檔案網站也必須完整可讀。 */
(function () {
  'use strict';

  var root = document.documentElement;
  var STORE_KEY = 'theme';

  /* ---------- 主題切換 ---------- */
  function systemTheme() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark' : 'light';
  }
  function currentTheme() {
    return root.getAttribute('data-theme') || systemTheme();
  }
  function labelFor(theme) {
    return theme === 'dark' ? 'LIGHT' : 'DARK';
  }

  var toggles = document.querySelectorAll('[data-theme-toggle]');
  Array.prototype.forEach.call(toggles, function (btn) {
    function sync() {
      var next = labelFor(currentTheme());
      btn.textContent = next;
      btn.setAttribute('aria-label', next === 'DARK' ? '切換為深色主題' : '切換為淺色主題');
    }
    sync();
    btn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(STORE_KEY, next); } catch (e) { /* 無痕視窗等情況直接略過 */ }
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
      // 同一組最多錯開三個，每個間隔 60ms
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
