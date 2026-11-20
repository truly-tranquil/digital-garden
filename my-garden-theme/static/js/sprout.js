/* The header sprout: grows in on load, click or press enter/space to watch it grow again. */

export function initSprout() {
  const sprout = document.querySelector(".brand-sprout");
  if (!sprout) return;

  function replay() {
    sprout.classList.remove("sprout-play");
    // force a style flush so the animation classes start over
    void sprout.getBoundingClientRect();
    sprout.classList.add("sprout-play");
  }

  // grow in on load
  sprout.classList.add("sprout-play");

  sprout.addEventListener("click", replay);
  sprout.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    e.preventDefault();
    replay();
  });
}
