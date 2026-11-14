var GARDEN_BASE = (function () {
  var s = document.querySelector('script[src$="garden.js"]');
  return s ? new URL(s.src).pathname.replace(/garden\.js$/, "") : "/";
})();

(function () {
  var root = document.documentElement;
  var btn = document.getElementById("mode-toggle");

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (btn) {
      btn.textContent = theme === "dark" ? "\u2600\uFE0E" : "\u263E\uFE0E";
      btn.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
      btn.setAttribute("aria-pressed", theme === "dark");
    }
  }

  var saved = null;
  try { saved = localStorage.getItem("theme"); } catch (e) {}
  var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  setTheme(saved || (prefersDark ? "dark" : "light"));

  if (btn) {
    btn.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      setTheme(next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  }
})();

(function () {
  var form = document.getElementById("mkdocs-search-form");
  var input = document.getElementById("search-input");
  var dd = document.getElementById("search-dd");
  if (!form || !input || !dd) return;

  var index = null;
  var results = [];
  var selected = -1;

  function load() {
    if (index) return Promise.resolve();
    return fetch(GARDEN_BASE + "search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; })
      .catch(function () { index = []; });
  }

  function snippet(text, q) {
    var flat = text.replace(/\s+/g, " ");
    var i = flat.toLowerCase().indexOf(q);
    if (i === -1) return flat.slice(0, 70);
    var start = Math.max(0, i - 25);
    return (start > 0 ? "\u2026" : "") + flat.slice(start, start + 80);
  }

  function search(q) {
    q = q.trim().toLowerCase();
    if (!q) return [];
    var scored = [];
    index.forEach(function (n) {
      var title = (n.title || "").toLowerCase();
      var tags = (n.tags || []).join(" ").toLowerCase();
      var text = (n.text || "").toLowerCase();
      var score = 0;
      if (title.indexOf(q) !== -1) score += 10;
      if (tags.indexOf(q) !== -1) score += 5;
      if (text.indexOf(q) !== -1) score += 1;
      if (score) scored.push({ note: n, score: score });
    });
    scored.sort(function (a, b) { return b.score - a.score; });
    return scored.slice(0, 6).map(function (s) { return s.note; });
  }

  function highlight() {
    var links = dd.querySelectorAll("a");
    links.forEach(function (a, i) { a.classList.toggle("sel", i === selected); });
  }

  function render(q) {
    dd.textContent = "";
    if (!q.trim()) { dd.hidden = true; return; }
    if (!results.length) {
      var none = document.createElement("div");
      none.className = "none";
      none.textContent = "nothing found";
      dd.appendChild(none);
    } else {
      results.forEach(function (n) {
        var a = document.createElement("a");
        a.href = n.url;
        var s = document.createElement("strong");
        s.textContent = n.title;
        var small = document.createElement("small");
        small.textContent = snippet(n.text || "", q.trim().toLowerCase());
        a.appendChild(s);
        a.appendChild(small);
        dd.appendChild(a);
      });
    }
    selected = -1;
    dd.hidden = false;
  }

  input.addEventListener("input", function () {
    load().then(function () {
      results = search(input.value);
      render(input.value);
    });
  });

  input.addEventListener("focus", load);

  input.addEventListener("keydown", function (e) {
    var links = dd.querySelectorAll("a");
    if (e.key === "ArrowDown" && links.length) {
      e.preventDefault();
      selected = (selected + 1) % links.length;
      highlight();
    } else if (e.key === "ArrowUp" && links.length) {
      e.preventDefault();
      selected = (selected - 1 + links.length) % links.length;
      highlight();
    } else if (e.key === "Enter") {
      e.preventDefault();
      var target = links[selected >= 0 ? selected : 0];
      if (target) window.location.href = target.href;
    } else if (e.key === "Escape") {
      dd.hidden = true;
      input.blur();
    }
  });

  document.addEventListener("click", function (e) {
    if (!form.contains(e.target)) dd.hidden = true;
  });
})();

(function () {
  var container = document.getElementById("garden-container");
  var toggle = document.getElementById("sidebar-toggle");
  var random = document.getElementById("random-note");

  if (container && toggle) {
    toggle.addEventListener("click", function () {
      var open;
      if (window.matchMedia("(max-width: 800px)").matches) {
        open = container.classList.toggle("sidebar-open");
      } else {
        open = container.classList.toggle("sidebar-collapsed") === false;
      }
      toggle.setAttribute("aria-expanded", open);
    });
  }

  if (random) {
    random.addEventListener("click", function () {
      fetch(GARDEN_BASE + "search-index.json")
        .then(function (r) { return r.json(); })
        .then(function (notes) {
          var listed = notes.filter(function (n) { return n.listed; });
          var here = window.location.pathname;
          var others = listed.filter(function (n) { return n.url !== here; });
          var pool = others.length ? others : listed;
          if (pool.length) {
            window.location.href = pool[Math.floor(Math.random() * pool.length)].url;
          }
        });
    });
  }
})();

(function () {
  var container = document.getElementById("garden-container");
  var tab = document.getElementById("toc-toggle");
  if (!container || !tab) return;

  tab.addEventListener("click", function () {
    var open;
    if (window.matchMedia("(max-width: 1099px)").matches) {
      open = container.classList.toggle("toc-open");
    } else {
      open = container.classList.toggle("toc-collapsed") === false;
    }
    tab.setAttribute("aria-expanded", open);
  });

  var links = Array.prototype.slice.call(document.querySelectorAll(".toc-panel a"));
  var heads = links.map(function (a) {
    return document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1)));
  });

  function spy() {
    var current = -1;
    heads.forEach(function (h, i) {
      if (h && h.getBoundingClientRect().top < 120) current = i;
    });
    links.forEach(function (a, i) { a.classList.toggle("current", i === current); });
  }

  window.addEventListener("scroll", spy, { passive: true });
  spy();

  links.forEach(function (a) {
    a.addEventListener("click", function () {
      if (window.matchMedia("(max-width: 1099px)").matches) {
        container.classList.remove("toc-open");
        tab.setAttribute("aria-expanded", "false");
      }
    });
  });
})();

(function () {
  var path = decodeURIComponent(window.location.pathname);
  if (path.slice(-1) === "/") path += "index.html";

  document.querySelectorAll("#site-map a").forEach(function (a) {
    var href = decodeURIComponent(new URL(a.href).pathname);
    if (href !== path) return;
    a.classList.add("active");
    a.setAttribute("aria-current", "page");
    var p = a.parentElement;
    while (p && p.id !== "site-map") {
      if (p.tagName === "DETAILS") p.open = true;
      p = p.parentElement;
    }
  });
})();

(function () {
  var diagrams = document.querySelectorAll(".mermaid");
  if (!diagrams.length) return;

  diagrams.forEach(function (d) { d.setAttribute("data-src", d.textContent); });

  function draw() {
    var dark = document.documentElement.getAttribute("data-theme") === "dark";
    mermaid.initialize({ startOnLoad: false, theme: dark ? "dark" : "default" });
    diagrams.forEach(function (d) {
      d.removeAttribute("data-processed");
      d.textContent = d.getAttribute("data-src");
    });
    mermaid.run({ nodes: diagrams });
  }

  var script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js";
  script.onload = draw;
  document.head.appendChild(script);

  var toggle = document.getElementById("mode-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      if (window.mermaid) draw();
    });
  }
})();

(function () {
  var items = document.querySelectorAll(".footnote li");
  items.forEach(function (li, i) {
    var color = "var(--rb-" + (i % 8) + ")";
    li.style.setProperty("--fnc", color);
    document.querySelectorAll('a.footnote-ref[href="#' + li.id + '"]').forEach(function (a) {
      a.style.color = color;
    });
  });
})();

(function () {
  document.querySelectorAll(".backlinks li").forEach(function (li, i) {
    li.style.setProperty("--fnc", "var(--rb-" + (i % 8) + ")");
  });
})();