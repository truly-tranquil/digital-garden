/* Graph physics: force simulation tick, settle loop and view fitting. No DOM access here. */

import { REPEL, GRAVITY, DAMPING, MIN_ALPHA, state, isVisible, visibleNodes } from "./state.js";

export function step() {
  const vis = visibleNodes();
  const n = vis.length;
  let i;
  let j;

  for (i = 0; i < n; i++) {
    const a = vis[i];
    for (j = i + 1; j < n; j++) {
      const b = vis[j];
      let dx = b.x - a.x;
      let dy = b.y - a.y;
      let d2 = dx * dx + dy * dy;
      if (d2 > 160000) continue;
      if (d2 < 1) {
        dx = Math.random() - 0.5;
        dy = Math.random() - 0.5;
        d2 = dx * dx + dy * dy + 0.01;
      }
      const f = (REPEL * state.alpha) / Math.max(d2, 36);
      a.vx -= dx * f;
      a.vy -= dy * f;
      b.vx += dx * f;
      b.vy += dy * f;
    }
  }

  for (i = 0; i < state.edges.length; i++) {
    const e = state.edges[i];
    if (!isVisible(e.a) || !isVisible(e.b)) continue;
    const ex = e.b.x - e.a.x;
    const ey = e.b.y - e.a.y;
    const d = Math.sqrt(ex * ex + ey * ey) || 1;
    const rest = e.kind === "tag" ? 70 : 52;
    const k = e.kind === "tag" ? 0.035 : 0.09;
    const pull = ((d - rest) * k * state.alpha) / d;
    e.a.vx += ex * pull;
    e.a.vy += ey * pull;
    e.b.vx -= ex * pull;
    e.b.vy -= ey * pull;
  }

  for (i = 0; i < n; i++) {
    const p = vis[i];
    p.vx -= p.x * GRAVITY * state.alpha;
    p.vy -= p.y * GRAVITY * state.alpha;
    if (p.fx !== null) {
      p.x = p.fx;
      p.y = p.fy;
      p.vx = 0;
      p.vy = 0;
    } else {
      p.vx *= DAMPING;
      p.vy *= DAMPING;
      p.x += p.vx;
      p.y += p.vy;
    }
  }

  state.alpha += (state.alphaTarget - state.alpha) * 0.0228;
}

export function settle(maxTicks, untilCalm) {
  for (let t = 0; t < maxTicks; t++) {
    step();
    if (untilCalm && state.alpha < MIN_ALPHA) break;
  }
}

export function fit() {
  const vis = visibleNodes();
  if (!vis.length || !state.W || !state.H) return;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  vis.forEach((n) => {
    minX = Math.min(minX, n.x - n.r);
    maxX = Math.max(maxX, n.x + n.r);
    minY = Math.min(minY, n.y - n.r);
    maxY = Math.max(maxY, n.y + n.r + 18);
  });
  const pad = 36;
  const bw = Math.max(maxX - minX, 1);
  const bh = Math.max(maxY - minY, 1);
  const k = Math.min((state.W - pad * 2) / bw, (state.H - pad * 2) / bh, 1.5);
  state.view.k = Math.max(k, 0.1);
  state.view.x = state.W / 2 - ((minX + maxX) / 2) * state.view.k;
  state.view.y = state.H / 2 - ((minY + maxY) / 2) * state.view.k;
}
