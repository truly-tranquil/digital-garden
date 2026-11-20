/* The well-trodden path: the stones you've stepped on this visit, kept for the session. */

const STORE = "garden:trail";
const LIMIT = 14;

function read() {
  try {
    const raw = JSON.parse(sessionStorage.getItem(STORE) || "[]");
    return Array.isArray(raw) ? raw : [];
  } catch {
    return [];
  }
}

function write(stones) {
  try {
    sessionStorage.setItem(STORE, JSON.stringify(stones));
  } catch { /* private mode */ }
}

function currentTitle() {
  const h1 = document.querySelector(".garden-article h1, h1");
  if (!h1) return document.title.trim().replace(/\s+/g, " ").slice(0, 60);
  const clone = h1.cloneNode(true);
  // drop heading-anchor decorations like "¶" so the stone shows the real title
  clone.querySelectorAll(".headerlink, script, style").forEach((n) => { n.remove(); });
  return clone.textContent.trim().replace(/\s+/g, " ").slice(0, 60);
}

export function initTrail() {
  const host = document.getElementById("path-trail");
  if (!host) return;

  const here = { h: window.location.pathname, t: currentTitle() };
  const stones = read();
  const last = stones[stones.length - 1];
  if (!last || last.h !== here.h) {
    stones.push(here);
    while (stones.length > LIMIT) stones.shift();
    write(stones);
  }

  host.innerHTML = "";
  const label = document.createElement("span");
  label.className = "path-trail-label";
  label.textContent = "your path:";
  host.appendChild(label);

  const ol = document.createElement("ol");
  stones.forEach((stone, i) => {
    const li = document.createElement("li");
    li.style.display = "contents";
    if (i > 0) {
      const pebble = document.createElement("span");
      pebble.className = "path-pebble";
      pebble.setAttribute("aria-hidden", "true");
      pebble.textContent = "···";
      li.appendChild(pebble);
    }
    const a = document.createElement("a");
    a.className = "path-stone";
    a.href = stone.h;
    a.textContent = stone.t;
    if (i === stones.length - 1) a.setAttribute("aria-current", "page");
    li.appendChild(a);
    ol.appendChild(li);
  });
  host.appendChild(ol);
}
