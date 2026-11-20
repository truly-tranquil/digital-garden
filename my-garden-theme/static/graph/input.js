/* Graph input: pointer drag/pan/pinch, wheel zoom, tag/fit/stage controls, theme and resize wiring. */

import { state, isVisible } from "./state.js";
import { kick, reheat, readColors, resize, zoomAt } from "./render.js";
import { fit } from "./physics.js";

function local(e) {
  const rect = state.canvas.getBoundingClientRect();
  return { x: e.clientX - rect.left, y: e.clientY - rect.top };
}

function pick(sx, sy) {
  const wx = (sx - state.view.x) / state.view.k;
  const wy = (sy - state.view.y) / state.view.k;
  let best = null;
  let bestD = Infinity;
  state.nodes.forEach((n) => {
    if (!isVisible(n)) return;
    const d = Math.sqrt((n.x - wx) * (n.x - wx) + (n.y - wy) * (n.y - wy));
    if (d < n.r + 7 / state.view.k && d < bestD) {
      best = n;
      bestD = d;
    }
  });
  return best;
}

function pointerList() {
  return Object.keys(state.pointers).map((id) => { return state.pointers[id]; });
}

function distance(a, b) {
  return Math.sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y)) || 1;
}

export function initInput() {
  const canvas = state.canvas;

  canvas.addEventListener("pointerdown", (e) => {
    try { canvas.setPointerCapture(e.pointerId); } catch {}
    const p = local(e);
    state.pointers[e.pointerId] = p;
    if (Object.keys(state.pointers).length === 2) {
      const pts = pointerList();
      state.pinch = { d: distance(pts[0], pts[1]) };
      if (state.drag) {
        state.drag.node.fx = null;
        state.drag.node.fy = null;
      }
      state.drag = null;
      state.panning = null;
      state.alphaTarget = 0;
      return;
    }
    const hit = pick(p.x, p.y);
    if (hit) {
      state.drag = { node: hit, sx: p.x, sy: p.y, moved: false };
      hit.fx = hit.x;
      hit.fy = hit.y;
      state.alphaTarget = 0.25;
      state.alpha = Math.max(state.alpha, 0.25);
    } else {
      state.panning = { sx: p.x, sy: p.y, vx: state.view.x, vy: state.view.y, moved: false };
    }
    canvas.style.cursor = "grabbing";
    kick();
  });

  canvas.addEventListener("pointermove", (e) => {
    const p = local(e);
    if (state.pointers[e.pointerId]) state.pointers[e.pointerId] = p;
    if (state.pinch && Object.keys(state.pointers).length >= 2) {
      const pts = pointerList();
      const d = distance(pts[0], pts[1]);
      zoomAt((pts[0].x + pts[1].x) / 2, (pts[0].y + pts[1].y) / 2, d / state.pinch.d);
      state.pinch.d = d;
      return;
    }
    if (state.drag) {
      if (Math.abs(p.x - state.drag.sx) + Math.abs(p.y - state.drag.sy) > 5) state.drag.moved = true;
      state.drag.node.fx = (p.x - state.view.x) / state.view.k;
      state.drag.node.fy = (p.y - state.view.y) / state.view.k;
      kick();
      return;
    }
    if (state.panning) {
      if (Math.abs(p.x - state.panning.sx) + Math.abs(p.y - state.panning.sy) > 5) state.panning.moved = true;
      state.view.x = state.panning.vx + p.x - state.panning.sx;
      state.view.y = state.panning.vy + p.y - state.panning.sy;
      kick();
      return;
    }
    if (e.pointerType === "touch") return;
    const h = pick(p.x, p.y);
    canvas.style.cursor = "url('assets/images/cursor.cur'), auto";
    if (h !== state.hover) {
      state.hover = h;
      kick();
    }
  });

  function release(e) {
    delete state.pointers[e.pointerId];
    if (state.pinch && Object.keys(state.pointers).length < 2) state.pinch = null;
    if (state.drag) {
      const node = state.drag.node;
      const moved = state.drag.moved;
      node.fx = null;
      node.fy = null;
      state.drag = null;
      state.alphaTarget = 0;
      if (!moved) {
        if (e.pointerType !== "touch" || state.selected === node) {
          window.location.href = node.url;
        } else {
          state.selected = node;
          state.hover = node;
        }
      }
    } else if (state.panning && !state.panning.moved && e.pointerType === "touch") {
      state.selected = null;
      state.hover = null;
    }
    state.panning = null;
    canvas.style.cursor = "url('assets/images/cursor.cur'), auto";
    kick();
  }

  canvas.addEventListener("pointerup", release);
  canvas.addEventListener("pointercancel", release);
  canvas.addEventListener("pointerleave", (e) => {
    if (e.pointerType === "touch" || state.drag || state.panning) return;
    canvas.style.cursor = "url('assets/images/cursor.cur'), auto";
    if (state.hover) {
      state.hover = null;
      kick();
    }
  });

  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    const p = local(e);
    zoomAt(p.x, p.y, Math.exp(-e.deltaY * 0.0015));
  }, { passive: false });

  const tagButton = document.getElementById("graph-tags");
  if (tagButton) {
    tagButton.addEventListener("click", () => {
      state.showTags = !state.showTags;
      tagButton.setAttribute("aria-pressed", state.showTags ? "true" : "false");
      reheat(0.5);
    });
  }

  const fitButton = document.getElementById("graph-fit");
  if (fitButton) {
    fitButton.addEventListener("click", () => {
      fit();
      kick();
    });
  }

  document.querySelectorAll("[data-stage]").forEach((chip) => {
    chip.addEventListener("click", () => {
      const name = chip.getAttribute("data-stage");
      state.hiddenStages[name] = !state.hiddenStages[name];
      chip.setAttribute("aria-pressed", state.hiddenStages[name] ? "false" : "true");
      reheat(0.5);
    });
  });

  if (window.MutationObserver) {
    new MutationObserver(() => {
      readColors();
      kick();
    }).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  }

  if (window.ResizeObserver) {
    new ResizeObserver(resize).observe(state.stage);
  } else {
    window.addEventListener("resize", resize);
  }
}
