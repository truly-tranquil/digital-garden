/* The trail map: a signposted overlay of where the paths lead. Toggle with "m". */

export function initMap() {
  const toggle = document.getElementById("trailmap-toggle");
  const map = document.getElementById("trailmap");
  const close = document.getElementById("trailmap-close");
  if (!toggle || !map || !close) return;

  const open = () => {
    map.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
    close.focus();
  };
  const hide = () => {
    if (map.hidden) return;
    map.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    toggle.focus();
  };
  const toggleMap = () => {
    if (map.hidden) open();
    else hide();
  };

  toggle.setAttribute("aria-expanded", "false");
  toggle.addEventListener("click", toggleMap);
  close.addEventListener("click", hide);
  // click on the dim backdrop (not the panel) closes the map
  map.addEventListener("click", (e) => {
    if (e.target === map) hide();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !map.hidden) {
      hide();
      return;
    }
    if (e.key !== "m" && e.key !== "M") return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const t = e.target;
    const tag = t && t.tagName ? t.tagName.toLowerCase() : "";
    if (tag === "input" || tag === "textarea" || tag === "select" || (t && t.isContentEditable)) return;
    e.preventDefault();
    toggleMap();
  });
}
