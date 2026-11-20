import { GARDEN_BASE, noteIcon } from "./base.js";

/* Search: "#tag" narrows to tags; plain queries score title, tags, then text. */

export function initSearch() {
  const form = document.getElementById("garden-search-form");
  const input = document.getElementById("search-input");
  const dd = document.getElementById("search-dd");
  const box = document.getElementById("search-listbox");
  const none = document.getElementById("search-none");
  const live = document.getElementById("search-status");
  if (!form || !input || !dd || !box || !live) return;

  let index = null;
  let results = [];
  let selected = -1;

  function load() {
    if (index) return Promise.resolve();
    return fetch(GARDEN_BASE + "search-index.json")
      .then((r) => { return r.json(); })
      .then((data) => { index = data; })
      .catch(() => { index = []; });
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
    if (!q) return [];

    // "#tag" searches tags only
    if (q.charAt(0) === "#") {
      const tag = q.slice(1).trim();
      return index.filter((n) => {
        return (n.tags || []).some((t) => { return t.toLowerCase().indexOf(tag) !== -1; });
      }).slice(0, 8);
    }

    const scored = [];
    index.forEach((n) => {
      const title = (n.title || "").toLowerCase();
      const tags = (n.tags || []).join(" ").toLowerCase();
      const text = (n.text || "").toLowerCase();
      let score = 0;
      if (title.indexOf(q) !== -1) score += 10;
      if (tags.indexOf(q) !== -1) score += 5;
      if (text.indexOf(q) !== -1) score += 1;
      if (score) scored.push({ note: n, score: score });
    });
    scored.sort((a, b) => { return b.score - a.score; });
    return scored.slice(0, 6).map((s) => { return s.note; });
  }

  function setExpanded(open) {
    dd.hidden = !open;
    input.setAttribute("aria-expanded", open ? "true" : "false");
    if (!open) input.setAttribute("aria-activedescendant", "");
  }

  function highlight() {
    const options = box.querySelectorAll('[role="option"]');
    options.forEach((opt, i) => {
      const on = i === selected;
      opt.classList.toggle("sel", on);
      opt.setAttribute("aria-selected", on ? "true" : "false");
    });
    input.setAttribute("aria-activedescendant", selected >= 0 && options[selected] ? options[selected].id : "");
  }

  function render(q) {
    box.textContent = "";
    live.textContent = "";
    none.hidden = true;
    if (!q.trim()) { setExpanded(false); return; }
    const tagSearch = q.trim().charAt(0) === "#";
    if (!results.length) {
      none.hidden = false;
      live.textContent = "nothing found";
      selected = -1;
      setExpanded(true);
      return;
    }
    results.forEach((n, i) => {
      const a = document.createElement("a");
      a.href = n.url;
      a.id = "search-option-" + i;
      a.setAttribute("role", "option");
      a.setAttribute("aria-selected", "false");
      const s = document.createElement("strong");
      const icon = noteIcon(n.icon);
      if (icon) s.appendChild(icon);
      s.appendChild(document.createTextNode(n.title));
      const small = document.createElement("small");
      small.textContent = tagSearch
        ? (n.tags || []).map((t) => { return "#" + t; }).join(" ")
        : snippet(n.text || "", q.trim().toLowerCase());
      a.appendChild(s);
      a.appendChild(small);
      box.appendChild(a);
    });
    selected = -1;
    setExpanded(true);
  }

  input.addEventListener("input", () => {
    load().then(() => {
      results = search(input.value);
      render(input.value);
    });
  });

  input.addEventListener("focus", load);

  input.addEventListener("keydown", (e) => {
    const links = box.querySelectorAll('[role="option"]');
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
      const target = links[selected >= 0 ? selected : 0];
      if (target) window.location.href = target.href;
    } else if (e.key === "Escape") {
      setExpanded(false);
      input.blur();
    }
  });

  document.addEventListener("click", (e) => {
    if (!form.contains(e.target)) setExpanded(false);
  });
}
