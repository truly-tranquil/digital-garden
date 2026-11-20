import { GARDEN_BASE } from "./base.js";

/* Index bar: sidebar, random note, TOC drawer and the active site-map item. */

export function initNav() {
  const container = document.getElementById("garden-container");
  const toggle = document.getElementById("sidebar-toggle");
  const random = document.getElementById("random-note");

  if (container && toggle) {
    toggle.addEventListener("click", () => {
      let open;
      if (window.matchMedia("(max-width: 800px)").matches) {
        open = container.classList.toggle("sidebar-open");
      } else {
        open = container.classList.toggle("sidebar-collapsed") === false;
      }
      toggle.setAttribute("aria-expanded", open);
    });
  }

  if (random) {
    let cachedNotes = null;
    random.addEventListener("click", () => {
      const fetchPromise = cachedNotes
        ? Promise.resolve(cachedNotes)
        : fetch(GARDEN_BASE + "search-index.json")
            .then((r) => r.json())
            .then((data) => {
              cachedNotes = data;
              return data;
            });

      fetchPromise
        .then((notes) => {
          const randomPool = notes.filter((n) => n.listed && n.random !== false);
          const here = window.location.pathname;
          const others = randomPool.filter((n) => n.url !== here);
          const pool = others.length ? others : randomPool;
          if (pool.length) {
            window.location.href = pool[Math.floor(Math.random() * pool.length)].url;
          }
        })
        .catch(() => {});
    });
  }

  const tocContainer = document.getElementById("garden-container");
  const tab = document.getElementById("toc-toggle");
  if (tocContainer && tab) {
    tab.addEventListener("click", () => {
      let open;
      if (window.matchMedia("(max-width: 1099px)").matches) {
        open = tocContainer.classList.toggle("toc-open");
      } else {
        open = tocContainer.classList.toggle("toc-collapsed") === false;
      }
      tab.setAttribute("aria-expanded", open);
    });

    const links = [...document.querySelectorAll(".toc-panel a")];
    const heads = links.map((a) => {
      return document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1)));
    });

    function spy() {
      let current = -1;
      heads.forEach((h, i) => {
        if (h && h.getBoundingClientRect().top < 120) current = i;
      });
      links.forEach((a, i) => { a.classList.toggle("current", i === current); });
    }

    window.addEventListener("scroll", spy, { passive: true });
    spy();

    links.forEach((a) => {
      a.addEventListener("click", () => {
        if (window.matchMedia("(max-width: 1099px)").matches) {
          tocContainer.classList.remove("toc-open");
          tab.setAttribute("aria-expanded", "false");
        }
      });
    });
  }

  const path = decodeURIComponent(window.location.pathname);
  const activePath = path.slice(-1) === "/" ? path + "index.html" : path;

  document.querySelectorAll("#site-map a").forEach((a) => {
    const href = decodeURIComponent(new URL(a.href).pathname);
    if (href !== activePath) return;
    a.classList.add("active");
    a.setAttribute("aria-current", "page");
    let p = a.parentElement;
    while (p && p.id !== "site-map") {
      if (p.tagName === "DETAILS") p.open = true;
      p = p.parentElement;
    }
  });
}
