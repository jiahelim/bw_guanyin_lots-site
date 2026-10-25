/**
* Language toggle (EN / 中文)
* - Elements tagged data-lang="en" or data-lang="zh" are shown only in that language.
* - Language comes from ?lang=en|zh in the URL, else the browser's language (zh-* gives zh), else en, and is kept on internal links.
* - The pill renders into #langToggle if the page has one, otherwise fixed top right below #header.
*/
(function() {
  "use strict";

  var LANGS = ['en', 'zh'];
  var DEFAULT_LANG = 'en';

  // First browser language we support, e.g. zh-CN or zh-TW gives zh
  function browserLang() {
    var prefs = navigator.languages || [navigator.language || ''];
    for (var i = 0; i < prefs.length; i++) {
      var base = String(prefs[i]).toLowerCase().split('-')[0];
      if (LANGS.indexOf(base) !== -1) return base;
    }
    return DEFAULT_LANG;
  }

  var css =
    'html[lang="en"] [data-lang="zh"], html[lang="zh"] [data-lang="en"] { display: none !important; }' +
    '.lang-toggle { display: inline-flex; padding: 3px; margin: 0; list-style: none; border-radius: 50rem; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.15); z-index: 997; }' +
    '.lang-toggle.lang-toggle-fixed { position: fixed; right: 16px; }' +
    '.lang-toggle a { display: block; padding: 4px 14px; border-radius: 50rem; color: #f50057; font-size: 14px; line-height: 1.5; text-decoration: none; }' +
    '.lang-toggle a:hover { color: #f50057; text-decoration: none; }' +
    '.lang-toggle a.active { background: #f50057; color: #fff; }';

  function getLang() {
    var lang = new URLSearchParams(window.location.search).get('lang');
    return LANGS.indexOf(lang) === -1 ? browserLang() : lang;
  }

  function withLang(href, lang) {
    var url = new URL(href, window.location.href);
    url.searchParams.set('lang', lang);
    return url;
  }

  function relative(url) {
    return url.pathname.split('/').pop() + url.search + url.hash;
  }

  // Sets ?lang= on an href as written, so relative paths like ../index1.html survive
  function hrefWithLang(href, lang) {
    var hashAt = href.indexOf('#');
    var hash = hashAt === -1 ? '' : href.slice(hashAt);
    var rest = hashAt === -1 ? href : href.slice(0, hashAt);
    var queryAt = rest.indexOf('?');
    var path = queryAt === -1 ? rest : rest.slice(0, queryAt);
    var params = new URLSearchParams(queryAt === -1 ? '' : rest.slice(queryAt + 1));
    params.set('lang', lang);
    return path + '?' + params.toString() + hash;
  }

  function isInternalPage(a) {
    var href = a.getAttribute('href');
    return href && /\.html(\?|#|$)/.test(href) && a.hostname === window.location.hostname;
  }

  function setLang(lang) {
    document.documentElement.lang = lang;

    var links = document.querySelectorAll('.lang-toggle a');
    for (var i = 0; i < links.length; i++) {
      links[i].classList.toggle('active', links[i].getAttribute('data-set-lang') === lang);
    }

    var anchors = document.querySelectorAll('a[href]');
    for (var j = 0; j < anchors.length; j++) {
      if (isInternalPage(anchors[j])) {
        anchors[j].setAttribute('href', hrefWithLang(anchors[j].getAttribute('href'), lang));
      }
    }

    // Throws on file:// in some browsers; the toggle still works without the URL update
    try {
      history.replaceState(null, '', relative(withLang(window.location.href, lang)));
    } catch (e) {}
  }

  function renderToggle() {
    var toggle = document.createElement('ul');
    toggle.className = 'lang-toggle';
    toggle.innerHTML =
      '<li><a href="#" data-set-lang="en">EN</a></li>' +
      '<li><a href="#" data-set-lang="zh">中文</a></li>';

    toggle.addEventListener('click', function(e) {
      var target = e.target.closest('a[data-set-lang]');
      if (!target) return;
      e.preventDefault();
      setLang(target.getAttribute('data-set-lang'));
    });

    var slot = document.getElementById('langToggle');
    if (slot) {
      slot.appendChild(toggle);
      return;
    }

    toggle.classList.add('lang-toggle-fixed');
    var header = document.getElementById('header');
    toggle.style.top = ((header ? header.offsetHeight : 0) + 12) + 'px';
    document.body.appendChild(toggle);
  }

  // Applied immediately so the other language never flashes on load
  document.documentElement.lang = getLang();
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  document.addEventListener('DOMContentLoaded', function() {
    renderToggle();
    setLang(getLang());
  });

  // For pages that navigate from script: window.location.href = withLang('./lot.html')
  window.withLang = function(href) {
    return hrefWithLang(href, document.documentElement.lang);
  };
})();
