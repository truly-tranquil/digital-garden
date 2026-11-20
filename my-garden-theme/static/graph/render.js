/* Graph rendering: canvas drawing, the animation loop and view sizing. */

import { MIN_ALPHA, state, isVisible } from "./state.js";
import { step, settle, fit } from "./physics.js";

export function readColors() {
  const cs = getComputedStyle(document.documentElement);
  function v(name, fallback) {
    const value = cs.getPropertyValue(name);
    return value && value.trim() ? value.trim() : fallback;
  }
  state.colors = {
    surface: v("--surface", "#E6DCD1"),
    text: v("--text", "#575279"),
    line: v("--ui-border", "#80798A"),
    faint: v("--border", "#D0CFCE"),
    accentText: v("--accent-text", "#964085"),
    tagBg: v("--tag-bg", "#EBDEDA"),
    seedling: v("--rb-3", "#92C17E"),
    bud: v("--rb-4", "#7BB9B9"),
    evergreen: v("--rb-5", "#5AAEF0"),
    other: v("--rb-7", "#A68BC0"),
    font: getComputedStyle(document.body).fontFamily || "serif"
  };
}

function colorFor(n) {
  return state.colors[n.stage] || state.colors.other;
}

function roundedRect(x, y, w, h, r) {
  state.ctx.beginPath();
  state.ctx.moveTo(x + r, y);
  state.ctx.arcTo(x + w, y, x + w, y + h, r);
  state.ctx.arcTo(x + w, y + h, x, y + h, r);
  state.ctx.arcTo(x, y + h, x, y, r);
  state.ctx.arcTo(x, y, x + w, y, r);
  state.ctx.closePath();
}

export function draw() {
  const ctx = state.ctx;
  ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
  ctx.clearRect(0, 0, state.W, state.H);
  ctx.save();
  ctx.translate(state.view.x, state.view.y);
  ctx.scale(state.view.k, state.view.k);

  const focus = state.hover || (state.drag && state.drag.node) || null;
  let near = null;
  if (focus) {
    near = {};
    near[focus.id] = true;
    focus.nbrs.forEach((m) => { near[m.id] = true; });
  }

  state.edges.forEach((e) => {
    if (!isVisible(e.a) || !isVisible(e.b)) return;
    const lit = focus && (e.a === focus || e.b === focus);
    ctx.globalAlpha = focus && !lit ? 0.1 : 1;
    ctx.beginPath();
    ctx.moveTo(e.a.x, e.a.y);
    ctx.lineTo(e.b.x, e.b.y);
    if (e.kind === "tag") {
      ctx.setLineDash([4, 5]);
      ctx.lineWidth = lit ? 2.5 : 1.6;
      ctx.strokeStyle = lit ? state.colors.accentText : state.colors.faint;
    } else {
      ctx.setLineDash([]);
      ctx.lineWidth = lit ? 3.5 : 2.2;
      ctx.strokeStyle = lit ? state.colors.accentText : state.colors.line;
    }
    ctx.stroke();
  });
  ctx.setLineDash([]);

  let shown = 0;
  state.nodes.forEach((n) => {
    if (isVisible(n)) shown++;
  });

  [true, false].forEach((tagPass) => {
    state.nodes.forEach((n) => {
      if ((n.type === "tag") !== tagPass || !isVisible(n)) return;
      const isFocus = focus === n;
      ctx.globalAlpha = focus && !near[n.id] ? 0.18 : 1;
      const r = n.r + (isFocus ? 2 : 0);
      if (n.type === "tag") {
        roundedRect(n.x - r, n.y - r, r * 2, r * 2, 4);
        ctx.fillStyle = state.colors.tagBg;
        ctx.fill();
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = state.colors.accentText;
        ctx.stroke();
      } else {
        ctx.beginPath();
        ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
        ctx.fillStyle = colorFor(n);
        ctx.fill();
        ctx.lineWidth = isFocus ? 4 : 3;
        ctx.strokeStyle = isFocus ? state.colors.accentText : state.colors.surface;
        ctx.stroke();
      }
    });
  });

  const showAll = shown <= 30 || state.view.k >= 1.6;
  const size = 13 / state.view.k;
  ctx.globalAlpha = 1;
  ctx.font = "600 " + size + "px " + state.colors.font;
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  ctx.lineJoin = "round";
  state.nodes.forEach((n) => {
    if (!isVisible(n)) return;
    const show = focus ? near[n.id] : showAll;
    if (!show) return;
    let label = n.title.toLowerCase();
    if (label.length > 28) label = label.slice(0, 27) + "\u2026";
    const y = n.y + n.r + 4 / state.view.k;
    ctx.lineWidth = 4 / state.view.k;
    ctx.strokeStyle = state.colors.surface;
    ctx.strokeText(label, n.x, y);
    ctx.fillStyle = n.type === "tag" ? state.colors.accentText : state.colors.text;
    ctx.fillText(label, n.x, y);
  });

  ctx.restore();
  ctx.globalAlpha = 1;
}

export function frame() {
  state.raf = 0;
  const active = state.alpha > MIN_ALPHA || state.drag !== null || state.alphaTarget > 0;
  if (active) step();
  draw();
  if (active) state.raf = requestAnimationFrame(frame);
}

export function kick() {
  if (!state.raf) state.raf = requestAnimationFrame(frame);
}

export function reheat(amount) {
  state.alpha = Math.max(state.alpha, amount);
  if (state.reduceMotion) {
    settle(300, true);
    fit();
  }
  kick();
}

export function resize() {
  state.dpr = window.devicePixelRatio || 1;
  state.W = state.stage.clientWidth;
  state.H = state.stage.clientHeight;
  state.canvas.width = Math.max(1, Math.round(state.W * state.dpr));
  state.canvas.height = Math.max(1, Math.round(state.H * state.dpr));
  kick();
}

export function zoomAt(sx, sy, factor) {
  const k = Math.min(4, Math.max(0.1, state.view.k * factor));
  const change = k / state.view.k;
  state.view.x = sx - (sx - state.view.x) * change;
  state.view.y = sy - (sy - state.view.y) * change;
  state.view.k = k;
  kick();
}
