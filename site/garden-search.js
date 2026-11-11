(function () {
  var indexPromise = null;
  var notesPromise = null;

  function plainText(html) {
    return new DOMParser().parseFromString(String(html || ''), 'text/html').body.textContent || '';
  }

  function slugify(value) {
    return String(value || '').toLowerCase()
      .replace(/[^\p{L}\p{N}_]+/gu, '-')
      .replace(/^-+|-+$/g, '');
  }

  function loadIndex() {
    if (!indexPromise) {
      indexPromise = fetch(base_url + '/search/search_index.json')
        .then(function (response) {
          if (!response.ok) throw new Error('Search index request failed');
          return response.json();
        })
        .then(function (data) {
          if (!data || !Array.isArray(data.docs)) throw new Error('Search index is invalid');
          return data.docs.map(function (doc) {
            var title = plainText(doc.title);
            var text = plainText(doc.text);
            return {
              title: title,
              titleLower: title.toLowerCase(),
              text: text,
              textLower: text.toLowerCase(),
              location: String(doc.location || '')
            };
          });
        });
    }
    return indexPromise;
  }

  function loadNotes() {
    if (!notesPromise) {
      notesPromise = fetch(base_url + '/notes.json')
        .then(function (response) {
          if (!response.ok) throw new Error('Notes index request failed');
          return response.json();
        })
        .then(function (data) {
          if (!Array.isArray(data)) throw new Error('Notes index is invalid');
          return data.map(function (note) {
            return {
              note: note,
              tagSlugs: Array.isArray(note.tag_slugs)
                ? note.tag_slugs
                : (note.tags || []).map(slugify)
            };
          });
        });
    }
    return notesPromise;
  }

  function parseQuery(query) {
    var tagWords = [];
    var text = String(query || '').trim().toLowerCase().replace(
      /(^|\s)#([^\s#][\s\S]*?)(?=\s+#|$)/g,
      function (match, prefix, tag) {
        tagWords.push(slugify(tag));
        return prefix;
      }
    );
    return {
      tagWords: tagWords.filter(Boolean),
      textWords: text.trim().split(/\s+/).filter(Boolean)
    };
  }

  function search(query, limit) {
    var parsed = parseQuery(query);
    var tagWords = parsed.tagWords;
    var textWords = parsed.textWords;
    if (!tagWords.length && !textWords.length) return Promise.resolve([]);

    return Promise.all([
      textWords.length ? loadIndex() : Promise.resolve([]),
      tagWords.length ? loadNotes() : Promise.resolve([])
    ]).then(function (results) {
      var docs = results[0];
      var tagged = Object.create(null);

      if (tagWords.length) {
        results[1].forEach(function (item) {
          var note = item.note;
          if (note.is_index || note.unlisted || note.draft) return;
          if (tagWords.every(function (tag) { return item.tagSlugs.indexOf(tag) !== -1; })) {
            tagged[note.url] = note;
          }
        });
      }

      var bestByPage = Object.create(null);
      docs.forEach(function (doc) {
        var score = 0;
        var matches = -1;
        for (var i = 0; i < textWords.length; i++) {
          var word = textWords[i];
          var inTitle = doc.titleLower.indexOf(word) !== -1;
          var inText = doc.textLower.indexOf(word) !== -1;
          if (!inTitle && !inText) return;
          score += (inTitle ? 10 : 0) + (inText ? 1 : 0);
          if (matches === -1) matches = doc.textLower.indexOf(word);
        }
        if (doc.location.indexOf('#') === -1) score += 3;

        var pageUrl = doc.location.split('#')[0];
        if (tagWords.length && !tagged[pageUrl]) return;

        var previous = bestByPage[pageUrl];
        if (previous && previous.score >= score) return;
        var start = matches === -1 ? 0 : Math.max(0, matches - 30);
        var end = matches === -1 ? 90 : matches + 70;
        bestByPage[pageUrl] = {
          title: doc.title,
          url: doc.location,
          snippet: doc.text.slice(start, end).trim(),
          score: score
        };
      });

      var hits = Object.keys(bestByPage).map(function (url) { return bestByPage[url]; });
      if (tagWords.length && !textWords.length) {
        hits = Object.keys(tagged).map(function (url) {
          return {
            title: tagged[url].title,
            url: url,
            snippet: tagged[url].excerpt || '',
            score: 0
          };
        });
      }
      hits.sort(function (a, b) { return b.score - a.score || a.title.localeCompare(b.title); });
      hits.forEach(function (hit) { hit.terms = textWords; });
      return limit ? hits.slice(0, limit) : hits;
    });
  }

  function mark(el, text, terms) {
    el.textContent = '';
    var list = (terms || []).filter(Boolean).map(function (term) {
      return term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    });
    if (!list.length) { el.textContent = text; return; }
    var re = new RegExp('(' + list.join('|') + ')', 'gi');
    text.split(re).forEach(function (part, i) {
      if (i % 2 === 1) {
        var marked = document.createElement('mark');
        marked.textContent = part;
        el.appendChild(marked);
      } else if (part) {
        el.appendChild(document.createTextNode(part));
      }
    });
  }

  window.gardenSearch = search;
  window.gardenMark = mark;

  var input = document.getElementById('mkdocs-search-query');
  var dd = document.getElementById('search-dd');
  var status = document.getElementById('search-status');
  if (!input || !dd) return;
  var sel = -1, timer = null, requestId = 0;

  function say(text) {
    if (status) status.textContent = text;
  }

  function openList() {
    dd.hidden = false;
    input.setAttribute('aria-expanded', 'true');
  }

  function closeList() {
    requestId++;
    dd.hidden = true;
    input.setAttribute('aria-expanded', 'false');
    input.removeAttribute('aria-activedescendant');
    sel = -1;
  }

  function choose(items, index) {
    sel = index;
    items.forEach(function (anchor, i) {
      anchor.classList.toggle('sel', i === sel);
      anchor.setAttribute('aria-selected', i === sel ? 'true' : 'false');
    });
    if (items[sel]) input.setAttribute('aria-activedescendant', items[sel].id);
    else input.removeAttribute('aria-activedescendant');
  }

  function clearChildren(element) {
    while (element.firstChild) element.removeChild(element.firstChild);
  }

  function render(hits) {
    clearChildren(dd);
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
    hits.forEach(function (hit, i) {
      var anchor = document.createElement('a');
      anchor.href = base_url + '/' + hit.url;
      anchor.id = 'search-opt-' + i;
      anchor.setAttribute('role', 'option');
      anchor.setAttribute('aria-selected', 'false');
      var strong = document.createElement('strong'); mark(strong, hit.title, hit.terms);
      var small = document.createElement('small'); mark(small, hit.snippet, hit.terms);
      anchor.appendChild(strong);
      anchor.appendChild(small);
      dd.appendChild(anchor);
    });
    openList();
  }

  function showError() {
    clearChildren(dd);
    var error = document.createElement('div');
    error.className = 'none';
    error.setAttribute('role', 'option');
    error.setAttribute('aria-disabled', 'true');
    error.textContent = 'search is temporarily unavailable. please try again later.';
    dd.appendChild(error);
    say('search is temporarily unavailable');
    openList();
  }

  input.addEventListener('input', function () {
    clearTimeout(timer);
    var value = input.value;
    var currentRequest = ++requestId;
    if (!value.trim()) { closeList(); say(''); return; }
    timer = setTimeout(function () {
      say('searching');
      search(value, 5).then(function (hits) {
        if (currentRequest === requestId && input.value === value) render(hits);
      }).catch(function () {
        if (currentRequest === requestId && input.value === value) showError();
      });
    }, 120);
  });

  input.addEventListener('keydown', function (event) {
    var items = Array.prototype.slice.call(dd.querySelectorAll('a'));
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      if (!items.length || dd.hidden) return;
      event.preventDefault();
      choose(items, (sel + (event.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length);
    } else if (event.key === 'Enter' && sel >= 0 && items[sel]) {
      event.preventDefault();
      location.href = items[sel].href;
    } else if (event.key === 'Escape') {
      closeList();
    }
  });

  var form = input.form || input.parentNode;
  if (form) {
    form.addEventListener('focusout', function (event) {
      if (event.relatedTarget && form.contains(event.relatedTarget)) return;
      setTimeout(function () {
        if (!form.contains(document.activeElement)) closeList();
      }, 0);
    });
  }

  document.addEventListener('click', function (event) {
    if (!dd.contains(event.target) && event.target !== input) closeList();
  });
})();
