/* The look switcher: bubblegum, meadow, pond, dusk. The light face of dusk is
   called "dawn" — same look, friendlier name. Pre-paint restore lives in
   base.html. */

const LOOKS = ["bubblegum", "meadow", "pond", "dusk"];
const DEFAULT_LOOK = "dusk"; // light mode of dusk is "dawn", the default theme
const LABELS = { bubblegum: "bubblegum", meadow: "meadow", pond: "pond", dusk: "dusk" };

function stored() {
  try { return localStorage.getItem("look"); } catch { return null; }
}

function current() {
  const saved = stored();
  if (saved === "classic") return "bubblegum"; // the look's old name
  return LOOKS.includes(saved) ? saved : DEFAULT_LOOK;
}

function nameFor(look) {
  const theme = document.documentElement.getAttribute("data-theme");
  return look === "dusk" && theme !== "dark" ? "dawn" : LABELS[look];
}

export function initLook() {
  const btn = document.getElementById("look-toggle");
  if (!btn) return;

  function label(look) {
    const name = nameFor(look);
    btn.setAttribute("aria-label", "switch theme — currently " + name);
    btn.title = "theme: " + name + " (click to wander)";
  }

  function apply(look) {
    document.documentElement.setAttribute("data-look", look);
    btn.setAttribute("data-current", look);
    label(look);
    try { localStorage.setItem("look", look); } catch { /* private mode */ }
  }

  apply(current());

  btn.addEventListener("click", () => {
    const next = LOOKS[(LOOKS.indexOf(current()) + 1) % LOOKS.length];
    apply(next);
  });

  // the mode toggle decides whether dusk is called dusk or dawn
  new MutationObserver(() => label(current())).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });
}
