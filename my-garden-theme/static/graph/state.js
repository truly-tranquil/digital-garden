/* Shared mutable state for the graph: one live container so every module sees the same values. */

export const REPEL = 420;
export const GRAVITY = 0.035;
export const DAMPING = 0.6;
export const MIN_ALPHA = 0.004;

export const state = {
  nodes: [],
  edges: [],
  showTags: true,
  hiddenStages: {},
  view: { k: 1, x: 0, y: 0 },
  W: 0,
  H: 0,
  dpr: 1,
  alpha: 1,
  alphaTarget: 0,
  hover: null,
  selected: null,
  drag: null,
  panning: null,
  pinch: null,
  pointers: {},
  raf: 0,
  colors: {},
  reduceMotion: !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches),
  stage: null,
  canvas: null,
  ctx: null,
};

export function isVisible(n) {
  if (n.type === "tag") {
    if (!state.showTags) return false;
    for (const m of n.nbrs) {
      if (!state.hiddenStages[m.stage]) return true;
    }
    return false;
  }
  return !state.hiddenStages[n.stage];
}

export function visibleNodes() {
  return state.nodes.filter(isVisible);
}
