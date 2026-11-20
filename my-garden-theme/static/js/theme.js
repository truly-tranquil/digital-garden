/* Theme: localStorage wins, then light (dawn); #mode-toggle mirrors it. */

export function initTheme() {
  const root = document.documentElement;
  const btn = document.getElementById("mode-toggle");

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (btn) {
      btn.textContent = theme === "dark" ? "\u2600\uFE0E" : "\u263E\uFE0E";
      btn.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
      btn.setAttribute("aria-pressed", theme === "dark");
    }
  }

  let saved = null;
  try { saved = localStorage.getItem("theme"); } catch {}
  setTheme(saved || "light");

  if (btn) {
    btn.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      setTheme(next);
      try { localStorage.setItem("theme", next); } catch {}
    });
  }
}
