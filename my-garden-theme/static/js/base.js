/* The site can be mounted under a sub-path (e.g. /digital-garden on Pages). */
export const GARDEN_BASE = new URL("..", import.meta.url).pathname;

/* Inline note icon from the sprite in base.html; returns null when absent. */
export function noteIcon(name) {
  if (!name || !document.getElementById("i-" + name)) return null;
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "note-icon");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", "#i-" + name);
  svg.appendChild(use);
  return svg;
}
