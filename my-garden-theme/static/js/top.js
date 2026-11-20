/* Back-to-top button and the "/" search shortcut. */

export function initTop() {
  const top = document.getElementById("to-top");
  if (top) {
    const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const update = () => { top.hidden = window.scrollY < 600; };
    window.addEventListener("scroll", update, { passive: true });
    update();
    top.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" });
    });
  }

  const search = document.getElementById("search-input");
  document.addEventListener("keydown", (e) => {
    if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey || !search) return;
    const target = e.target;
    const tag = target && target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (target && target.isContentEditable)) {
      return;
    }
    e.preventDefault();
    search.focus();
    search.select();
  });
}
