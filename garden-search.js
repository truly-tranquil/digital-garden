(function () {
  var indexPromise = null;
  var notesPromise = null;

  function loadIndex() {
    if (!indexPromise) {
      indexPromise = fetch(base_url + '/search/search_index.json')
        .then(function (r) { return r.json(); })
        .then(function (d) { return d.docs || []; })
        .catch(function () { return []; });
    }
    return indexPromise;
  }

  function loadNotes() {
    if (!notesPromise) {
      notesPromise = fetch(base_url + '/notes.json')
        .then(function (r) { return r.json(); })
        .catch(function () { return []; });
    }
    return notesPromise;
  }

  function strip(html) {
    var d = document.createElement('div');
    d.innerHTML = html;
    return d.textContent || '';
  }

  // search words match page text; words starting with # filter by tag
  function search(q, limit) {
    q = q.trim().toLowerCase();
    if (!q) return Promise.resolve([]);
    var words = q.split(/\s+/);
    var tagWords = words.filter(function (w) { return w.length > 1 && w.charAt(0) === '#'; })
      .map(function (w) { return w.slice(1); });
    var textWords = words.filter(function (w) { return w.charAt(0) !== '#'; });
    if (!tagWords.length && !textWords.length) return Promise.resolve([]);

    return Promise.all([
      textWords.length ? loadIndex() : Promise.resolve([]),
      tagWords.length ? loadNotes() : Promise.resolve([])
    ]).then(function (res) {
      var docs = res[0], notes = res[1], hits = [];

      docs.forEach(function (doc) {
        var title = (doc.title || '').toLowerCase();
        var text = strip(doc.text || '').toLowerCase();
        var score = 0;
        for (var i = 0; i < textWords.length; i++) {
          var w = textWords[i], inTitle = title.indexOf(w) !== -1, inText = text.indexOf(w) !== -1;
          if (!inTitle && !inText) { score = 0; break; }
          score += (inTitle ? 10 : 0) + (inText ? 1 : 0);
        }
        if (!score) return;
        if (doc.location.indexOf('#') === -1) score += 3; // prefer whole pages over sections
        var plain = strip(doc.text || '');
        var at = plain.toLowerCase().indexOf(textWords[0]);
        var snip = at === -1 ? plain.slice(0, 90) : plain.slice(Math.max(0, at - 30), at + 70);
        hits.push({ title: strip(doc.title || ''), url: doc.location, snippet: snip.trim(), score: score });
      });
      hits.sort(function (a, b) { return b.score - a.score; });

      if (tagWords.length) {
        var tagged = {};
        notes.forEach(function (n) {
          var mine = (n.tags || []).map(function (t) { return t.toLowerCase(); });
          if (!n.is_index && tagWords.every(function (t) { return mine.indexOf(t) !== -1; })) tagged[n.url] = n;
        });
        if (textWords.length) {
          hits = hits.filter(function (h) { return tagged[h.url.split('#')[0]]; });
        } else {
          hits = Object.keys(tagged).map(function (u) {
            return { title: tagged[u].title, url: u, snippet: tagged[u].excerpt || '', score: 0 };
          }).sort(function (a, b) { return a.title.toLowerCase().localeCompare(b.title.toLowerCase()); });
        }
      }

      hits.forEach(function (h) { h.terms = textWords; });
      return limit ? hits.slice(0, limit) : hits;
    });
  }

  // put text in an element, wrapping the search terms in <mark>
  function mark(el, text, terms) {
    el.textContent = '';
    var list = (terms || []).filter(Boolean).map(function (t) { return t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); });
    if (!list.length) { el.textContent = text; return; }
    var re = new RegExp('(' + list.join('|') + ')', 'gi');
    text.split(re).forEach(function (part, i) {
      if (i % 2 === 1) {
        var m = document.createElement('mark');
        m.textContent = part;
        el.appendChild(m);
      } else if (part) {
        el.appendChild(document.createTextNode(part));
      }
    });
  }

  window.gardenSearch = search;
  window.gardenMark = mark;

  // dropdown wiring
  var input = document.getElementById('mkdocs-search-query');
  var dd = document.getElementById('search-dd');
  var status = document.getElementById('search-status');
  if (!input || !dd) return;
  var sel = -1, timer = null;

  function say(text) {
    if (status) status.textContent = text;
  }

  function openList() {
    dd.hidden = false;
    input.setAttribute('aria-expanded', 'true');
  }

  function closeList() {
    dd.hidden = true;
    input.setAttribute('aria-expanded', 'false');
    input.removeAttribute('aria-activedescendant');
    sel = -1;
  }

  function choose(items, index) {
    sel = index;
    items.forEach(function (a, i) {
      a.classList.toggle('sel', i === sel);
      a.setAttribute('aria-selected', i === sel ? 'true' : 'false');
    });
    if (items[sel]) input.setAttribute('aria-activedescendant', items[sel].id);
    else input.removeAttribute('aria-activedescendant');
  }

  function render(hits) {
    dd.innerHTML = '';
    sel = -1;
    input.removeAttribute('aria-activedescendant');
    if (!hits.length) {
      var none = document.createElement('div');
      none.className = 'none';
      none.setAttribute('role', 'option');
      none.setAttribute('aria-disabled', 'true');
      none.textContent = 'nothing found. press enter to see the full search page.';
      dd.appendChild(none);
      say('nothing found');
    } else {
      say(hits.length + (hits.length === 1 ? ' suggestion' : ' suggestions') + ', use the up and down arrow keys to browse');
    }
    hits.forEach(function (h, i) {
      var a = document.createElement('a');
      a.href = base_url + '/' + h.url;
      a.id = 'search-opt-' + i;
      a.setAttribute('role', 'option');
      a.setAttribute('aria-selected', 'false');
      var s = document.createElement('strong'); mark(s, h.title, h.terms);
      var m = document.createElement('small'); mark(m, h.snippet, h.terms);
      a.appendChild(s); a.appendChild(m);
      dd.appendChild(a);
    });
    openList();
  }

  input.addEventListener('input', function () {
    clearTimeout(timer);
    var v = input.value;
    if (!v.trim()) { closeList(); say(''); return; }
    timer = setTimeout(function () { search(v, 5).then(render); }, 120);
  });

  input.addEventListener('keydown', function (e) {
    var items = Array.prototype.slice.call(dd.querySelectorAll('a'));
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      if (!items.length || dd.hidden) return;
      e.preventDefault();
      choose(items, (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length);
    } else if (e.key === 'Enter' && sel >= 0 && items[sel]) {
      e.preventDefault();
      location.href = items[sel].href;
    } else if (e.key === 'Escape') {
      closeList();
    }
  });

  document.addEventListener('click', function (e) {
    if (!dd.contains(e.target) && e.target !== input) closeList();
  });
})();