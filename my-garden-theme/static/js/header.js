/* Measure the sticky header so the side panels and anchor targets can start below it. */

export function initHeader() {
  const header = document.querySelector(".garden-header");
  if (!header) return;
  const root = document.documentElement;

  function measure() {
    root.style.setProperty("--header-h", header.offsetHeight + "px");
  }

  measure();
  if (typeof ResizeObserver === "function") {
    new ResizeObserver(measure).observe(header);
  } else {
    window.addEventListener("resize", measure, { passive: true });
  }
}
