/* Entry point: loads graph.json, lays out the nodes, then hands off to the physics/render/input modules. */

import { state } from "./graph/state.js";
import { settle, fit } from "./graph/physics.js";
import { readColors, resize, kick } from "./graph/render.js";
import { initInput } from "./graph/input.js";

/* Modules cannot use document.currentScript, so derive the base path from the module URL. */
const base = new URL(".", import.meta.url).pathname;

const stage = document.getElementById("graph-stage");
const canvas = document.getElementById("graph-canvas");
const status = document.getElementById("graph-status");

function init(data) {
  const byId = {};
  const degree = {};
  data.edges.forEach((e) => {
    degree[e.source] = (degree[e.source] || 0) + 1;
    degree[e.target] = (degree[e.target] || 0) + 1;
  });

  state.nodes = data.nodes.map((n, i) => {
    const angle = i * 2.399963;
    const radius = 18 * Math.sqrt(i + 1);
    const deg = degree[n.id] || 0;
    const node = {
      id: n.id,
      type: n.type,
      title: n.title,
      url: n.url,
      stage: n.stage,
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      vx: 0,
      vy: 0,
      fx: null,
      fy: null,
      nbrs: [],
      r: n.type === "tag" ? 6 + Math.min(7, Math.sqrt(n.count || 1) * 1.5) : 6 + Math.min(9, Math.sqrt(deg) * 2.4)
    };
    byId[n.id] = node;
    return node;
  });

  state.edges = [];
  data.edges.forEach((e) => {
    const a = byId[e.source];
    const b = byId[e.target];
    if (!a || !b) return;
    state.edges.push({ a: a, b: b, kind: e.kind });
    a.nbrs.push(b);
    b.nbrs.push(a);
  });

  if (!state.nodes.length) {
    status.textContent = "no notes to graph yet.";
    return;
  }

  status.hidden = true;
  settle(state.nodes.length > 600 ? 60 : 220, false);
  if (state.reduceMotion) settle(300, true);
  fit();
  kick();
}

if (stage && canvas) {
  state.stage = stage;
  state.canvas = canvas;
  state.ctx = canvas.getContext("2d");

  initInput();
  readColors();
  resize();

  fetch(base + "graph.json")
    .then((r) => {
      if (!r.ok) throw new Error("graph.json missing");
      return r.json();
    })
    .then(init)
    .catch(() => {
      status.textContent = "the graph couldn't load.";
    });
}
