import { GARDEN_BASE, noteIcon } from "./base.js";

/* Search: lazy load on first focus, title/tag/body scoring, top 6, #tag support. */

export function initSearch() {
  const form = document.getElementById("garden-search-form");
  const input = document.getElementById("search-input");
  if (!form || !input) return;

  let index = null;
  let selected = -1;

  // Create dropdown if not present
  let dd = document.getElementById("search-dd");
  if (!dd) {
    dd = document.createElement("div");
    dd.id = "search-dd";
    dd.className = "search-dd";
    dd.hidden = true;
    form.appendChild(dd);
  }

  function load() {
    if (index) return Promise.resolve(index);
    return fetch(GARDEN_BASE + "search-index.json")
      .then((r) => r.json())
      .then((data) => { index = data; return data; })
      .catch(() => { index = []; return []; });
  }

  function snippet(text, q) {
    const flat = text.replace(/\s+/g, " ");
    const i = flat.toLowerCase().indexOf(q);
    if (i === -1) return flat.slice(0, 70);
    const start = Math.max(0, i - 25);
    return (start > 0 ? "…" : "") + flat.slice(start, start + 80);
  }

  function search(q) {
    q = q.trim().toLowerCase();
    if (!q || !index) return [];

    if (q.startsWith("#")) {
      const tag = q.slice(1).trim();
      return index
        .filter((n) => (n.tags || []).some((t) => t.toLowerCase().includes(tag)))
        .slice(0, 6);
    }

    const scored = [];
    const isShort = q.length < 3;
    const wordBoundary = new RegExp("\\b" + q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "i");

    index.forEach((n) => {
      const title = (n.title || "").toLowerCase();
      const tags = (n.tags || []).join(" ").toLowerCase();
      const text = n.text || "";
      let score = 0;

      if (title.includes(q)) score += 10;
      if (tags.includes(q)) score += 5;
      if (isShort ? wordBoundary.test(text) : text.toLowerCase().includes(q)) score += 1;

      if (score > 0) scored.push({ note: n, score });
    });

    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, 6).map((s) => s.note);
  }

  function render(q) {
    const results = search(q);
    dd.innerHTML = "";
    selected = -1;

    if (!q.trim()) {
      dd.hidden = true;
      input.setAttribute("aria-expanded", "false");
      return;
    }

    if (!results.length) {
      dd.innerHTML = '<div class="none">nothing found</div>';
      dd.hidden = false;
      input.setAttribute("aria-expanded", "true");
      return;
    }

    const tagMode = q.trim().startsWith("#");
    results.forEach((n, i) => {
      const a = document.createElement("a");
      a.href = n.url;
      a.id = "search-opt-" + i;
      a.setAttribute("role", "option");

      const strong = document.createElement("strong");
      const icon = noteIcon(n.icon);
      if (icon) strong.appendChild(icon);
      strong.appendChild(document.createTextNode(n.title));

      const small = document.createElement("small");
      small.textContent = tagMode
        ? (n.tags || []).map((t) => "#" + t).join(" ")
        : snippet(n.text || "", q.trim().toLowerCase());

      a.appendChild(strong);
      a.appendChild(small);
      dd.appendChild(a);
    });

    dd.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }

  function highlight() {
    const options = dd.querySelectorAll("a");
    options.forEach((opt, i) => {
      const on = i === selected;
      opt.classList.toggle("sel", on);
      opt.setAttribute("aria-selected", on ? "true" : "false");
    });
    input.setAttribute("aria-activedescendant", selected >= 0 && options[selected] ? options[selected].id : "");
  }

  input.addEventListener("focus", load);
  input.addEventListener("input", () => {
    load().then(() => render(input.value));
  });

  input.addEventListener("keydown", (e) => {
    const options = dd.querySelectorAll("a");
    if (e.key === "ArrowDown" && options.length) {
      e.preventDefault();
      selected = (selected + 1) % options.length;
      highlight();
    } else if (e.key === "ArrowUp" && options.length) {
      e.preventDefault();
      selected = (selected - 1 + options.length) % options.length;
      highlight();
    } else if (e.key === "Enter") {
      const target = options[selected >= 0 ? selected : 0];
      if (target) {
        e.preventDefault();
        window.location.href = target.href;
      }
    } else if (e.key === "Escape") {
      dd.hidden = true;
      input.blur();
    }
  });

  // Global / shortcut to jump to search
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== input && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) {
      e.preventDefault();
      input.focus();
      input.select();
    }
  });

  document.addEventListener("click", (e) => {
    if (!form.contains(e.target)) dd.hidden = true;
  });
}
