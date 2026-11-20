/* Read aloud: a split button with a small settings menu. Speaks the article
   with speechSynthesis, highlighting the text being read — word by word where
   the browser reports word boundaries, block by block everywhere else. */

export function initReadAloud() {
  const synth = window.speechSynthesis;
  const article = document.querySelector(".garden-article");
  if (!synth || !article || !("SpeechSynthesisUtterance" in window)) return;

  const SETTINGS_KEY = "garden-read-aloud";
  const POSITION_KEY = "garden-read-aloud-position";
  const settings = { voiceURI: "", rate: 1, volume: 1, pitch: 1, highlight: true, resume: true };
  try { Object.assign(settings, JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}")); } catch {}

  function saveSettings() {
    try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings)); } catch {}
  }
  function positions() {
    try { return JSON.parse(localStorage.getItem(POSITION_KEY) || "{}"); } catch { return {}; }
  }
  function savePositions(map) {
    try { localStorage.setItem(POSITION_KEY, JSON.stringify(map)); } catch {}
  }
  const pageKey = () => { return window.location.pathname; };
  function savedIndex() {
    const i = positions()[pageKey()];
    return Number.isInteger(i) ? i : 0;
  }
  function savePosition(i) {
    const map = positions();
    map[pageKey()] = i;
    savePositions(map);
    topBtn.hidden = false;
  }
  function clearPosition() {
    const map = positions();
    delete map[pageKey()];
    savePositions(map);
    topBtn.hidden = true;
  }

  const BLOCK_SEL = "h1, h2, h3, h4, h5, h6, p, li, blockquote, dt, dd, td, th, figcaption";
  const SKIP_SEL = "pre, svg, script, style, [aria-hidden='true'], .copy-btn";

  // speechSynthesis can stall on very long utterances, so split on sentence boundaries
  function splitLong(text) {
    const out = [];
    let rest = text;
    let base = 0;
    while (rest.length > 320) {
      let cut = rest.lastIndexOf(". ", 320);
      if (cut < 120) cut = rest.lastIndexOf(" ", 320);
      if (cut < 120) cut = 320;
      const raw = rest.slice(0, cut + 1);
      const part = raw.trim();
      out.push({ text: part, at: base });
      const next = rest.slice(cut + 1);
      base += cut + 1 + (next.length - next.trimStart().length);
      rest = next.trim();
    }
    if (rest) out.push({ text: rest, at: base });
    return out;
  }

  // one tokenizer for both the spoken string and the word spans, so boundary
  // charIndex values map straight onto live DOM nodes
  function blockChunks(el) {
    const nodes = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        if (node.parentElement.closest(SKIP_SEL)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    let node;
    while ((node = walker.nextNode())) nodes.push(node);
    let text = "";
    const segs = [];
    nodes.forEach((n) => {
      let t = n.nodeValue.replace(/\s+/g, " ");
      if (text === "") t = t.replace(/^ +/, "");
      else if (t.startsWith(" ") && text.endsWith(" ")) t = t.slice(1);
      if (!t) return;
      segs.push({ node: n, start: text.length, end: text.length + t.length });
      text += t;
    });
    return { text, segs };
  }

  // skip blocks nested in other blocks so quoted text is read once
  function topLevelBlocks() {
    return [...article.querySelectorAll(BLOCK_SEL)].filter((el) => { return !el.parentElement.closest(BLOCK_SEL); });
  }

  function buildChunks() {
    const chunks = [];
    topLevelBlocks().forEach((el) => {
      const { text, segs } = blockChunks(el);
      if (!text) return;
      splitLong(text).forEach((part) => {
        chunks.push({ text: part.text, offset: part.at, el, segs, words: null });
      });
    });
    if (!chunks.length) {
      const text = (article.textContent || "").replace(/\s+/g, " ").trim();
      splitLong(text).forEach((part) => {
        chunks.push({ text: part.text, offset: part.at, el: article, segs: null, words: null });
      });
    }
    chunks.forEach((c, i) => { c.i = i; });
    return chunks;
  }

  // wrap each word of the chunk in a span so it can be lit up mid-sentence
  function wrapWords(chunk) {
    const words = [];
    if (!chunk.segs) return words;
    const re = /\S+/g;
    let m;
    while ((m = re.exec(chunk.text))) words.push({ start: m.index, end: m.index + m[0].length, span: null });
    chunk.segs.forEach((seg) => {
      const inside = words.filter((w) => { return w.start + chunk.offset >= seg.start && w.end + chunk.offset <= seg.end && !w.span; });
      if (!inside.length) return;
      let remain = seg.node;
      let consumed = 0;
      for (const w of inside) {
        const ls = w.start + chunk.offset - seg.start - consumed;
        const le = w.end + chunk.offset - seg.start - consumed;
        if (ls < 0 || le > remain.nodeValue.length) break;
        remain.splitText(ls);
        const wordNode = remain.nextSibling;
        wordNode.splitText(le - ls);
        const span = document.createElement("span");
        span.className = "read-aloud-word";
        wordNode.replaceWith(span);
        span.appendChild(wordNode);
        w.span = span;
        remain = wordNode.nextSibling;
        consumed = w.end + chunk.offset - seg.start;
        if (!remain || remain.nodeType !== Node.TEXT_NODE) break;
      }
    });
    return words;
  }

  function unwrapWords() {
    article.querySelectorAll(".read-aloud-word").forEach((span) => {
      span.replaceWith(...span.childNodes);
    });
    article.normalize();
  }

  // voices are provided by the OS/browser; english ones first
  function englishVoices() {
    const all = synth.getVoices() || [];
    const en = all.filter((v) => { return /^en([-_]|$)/i.test(v.lang); });
    return en.length ? en : all.slice(0, 30);
  }

  // speechSynthesis's default voice tends to be the most robotic one, so
  // prefer the natural/neural/online voices the platform ships
  function pickDefault(voices) {
    return (
      voices.find((v) => { return /online|natural|neural/i.test(v.name); }) ||
      voices.find((v) => { return /google/i.test(v.name); }) ||
      voices[0]
    );
  }

  function selectedVoice() {
    const voices = englishVoices();
    if (settings.voiceURI) {
      const match = voices.find((v) => { return v.voiceURI === settings.voiceURI; });
      if (match) return match;
    }
    return pickDefault(voices);
  }

  // dom: split button + settings menu
  const wrap = document.createElement("div");
  wrap.className = "read-aloud-wrap";

  const button = document.createElement("button");
  button.type = "button";
  button.className = "read-aloud-btn";
  button.id = "read-aloud";
  button.setAttribute("aria-keyshortcuts", "Alt+S");

  const caret = document.createElement("button");
  caret.type = "button";
  caret.className = "read-aloud-btn read-aloud-caret";
  caret.textContent = "▾";
  caret.setAttribute("aria-label", "reading settings");
  caret.setAttribute("aria-expanded", "false");
  caret.setAttribute("aria-controls", "read-aloud-menu");

  const menu = document.createElement("div");
  menu.className = "read-aloud-menu";
  menu.id = "read-aloud-menu";
  menu.hidden = true;

  function field(labelText) {
    const label = document.createElement("label");
    label.className = "read-aloud-field";
    const span = document.createElement("span");
    span.textContent = labelText;
    label.append(span);
    menu.append(label);
    return label;
  }

  const voiceSelect = document.createElement("select");
  voiceSelect.className = "read-aloud-voice";
  voiceSelect.setAttribute("aria-label", "read aloud voice");
  field("voice").append(voiceSelect);

  const speedSelect = document.createElement("select");
  speedSelect.className = "read-aloud-speed";
  speedSelect.setAttribute("aria-label", "reading speed");
  [["0.75", "slow"], ["1", "normal"], ["1.25", "fast"], ["1.5", "faster"]].forEach(([value, name]) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = name;
    speedSelect.append(option);
  });
  field("speed").append(speedSelect);

  const volumeRange = document.createElement("input");
  volumeRange.type = "range";
  volumeRange.className = "read-aloud-volume";
  volumeRange.min = "0";
  volumeRange.max = "1";
  volumeRange.step = "0.01";
  volumeRange.setAttribute("aria-label", "reading volume");
  field("volume").append(volumeRange);

  const pitchRange = document.createElement("input");
  pitchRange.type = "range";
  pitchRange.className = "read-aloud-pitch";
  pitchRange.min = "0.5";
  pitchRange.max = "1.5";
  pitchRange.step = "0.05";
  pitchRange.setAttribute("aria-label", "reading pitch");
  field("pitch").append(pitchRange);

  const highlightCheck = document.createElement("input");
  highlightCheck.type = "checkbox";
  highlightCheck.className = "read-aloud-highlight";
  field("highlight while reading").prepend(highlightCheck);

  const resumeCheck = document.createElement("input");
  resumeCheck.type = "checkbox";
  resumeCheck.className = "read-aloud-resume";
  field("continue where you left off").prepend(resumeCheck);

  const topBtn = document.createElement("button");
  topBtn.type = "button";
  topBtn.className = "read-aloud-top";
  topBtn.textContent = "start from the top";
  topBtn.hidden = true;
  menu.append(topBtn);

  const hint = document.createElement("p");
  hint.className = "read-aloud-hint";
  hint.textContent = "alt + s toggles reading";
  menu.append(hint);

  function syncMenu() {
    voiceSelect.value = settings.voiceURI || "";
    speedSelect.value = String(settings.rate);
    volumeRange.value = String(settings.volume);
    pitchRange.value = String(settings.pitch);
    highlightCheck.checked = settings.highlight;
    resumeCheck.checked = settings.resume;
    topBtn.hidden = savedIndex() === 0;
  }

  let active = false;
  let pending = 0;
  let errored = false;
  let currentSpan = null;

  function clearHighlights() {
    article.querySelectorAll(".read-aloud-reading").forEach((el) => { return el.classList.remove("read-aloud-reading"); });
    article.querySelectorAll(".read-aloud-word-current").forEach((el) => { return el.classList.remove("read-aloud-word-current"); });
    currentSpan = null;
  }

  function refreshLabel() {
    if (active) {
      button.textContent = "stop reading";
      button.setAttribute("aria-pressed", "true");
    } else {
      button.textContent = settings.resume && savedIndex() > 0 ? "resume reading" : "read aloud";
      button.setAttribute("aria-pressed", "false");
    }
  }

  function setIdle() {
    active = false;
    refreshLabel();
  }

  function setReading() {
    active = true;
    refreshLabel();
  }

  function stop() {
    pending = 0;
    active = false;
    synth.cancel();
    clearHighlights();
    unwrapWords();
    refreshLabel();
  }

  function start() {
    const chunks = buildChunks();
    if (!chunks.length) return;
    let begin = 0;
    if (settings.resume) {
      const at = savedIndex();
      if (at > 0 && at < chunks.length) begin = at;
    }
    const voice = selectedVoice();
    const speakList = chunks.slice(begin);
    pending = speakList.length;
    errored = false;
    speakList.forEach((chunk) => {
      if (settings.highlight) chunk.words = wrapWords(chunk);
      const utter = new SpeechSynthesisUtterance(chunk.text);
      if (voice) utter.voice = voice;
      utter.rate = settings.rate;
      utter.volume = settings.volume;
      utter.pitch = settings.pitch;
      utter.onstart = () => {
        savePosition(chunk.i);
        if (settings.highlight) {
          chunk.el.classList.add("read-aloud-reading");
          chunk.el.scrollIntoView({ block: "nearest" });
        }
      };
      utter.onboundary = (e) => {
        if (e.name !== "word" || e.charIndex == null || !chunk.words) return;
        const w = chunk.words.find((x) => { return e.charIndex >= x.start && e.charIndex < x.end; });
        if (!w || !w.span || currentSpan === w.span) return;
        if (currentSpan) currentSpan.classList.remove("read-aloud-word-current");
        w.span.classList.add("read-aloud-word-current");
        currentSpan = w.span;
        const r = w.span.getBoundingClientRect();
        if (r.top < 0 || r.bottom > window.innerHeight) w.span.scrollIntoView({ block: "nearest" });
      };
      const done = () => {
        chunk.el.classList.remove("read-aloud-reading");
        pending -= 1;
        if (pending > 0 || !active) return;
        if (errored) {
          unwrapWords();
          setIdle();
        } else {
          finish();
        }
      };
      utter.onend = done;
      utter.onerror = () => { errored = true; done(); };
      synth.speak(utter);
    });
    setReading();
  }

  function finish() {
    clearPosition();
    clearHighlights();
    unwrapWords();
    setIdle();
  }

  button.addEventListener("click", () => {
    if (active || synth.speaking || synth.pending) stop();
    else start();
  });

  // menu open/close
  function setMenu(open) {
    menu.hidden = !open;
    caret.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) voiceSelect.focus();
  }

  caret.addEventListener("click", () => {
    setMenu(menu.hidden);
  });

  document.addEventListener("pointerdown", (e) => {
    if (!menu.hidden && !wrap.contains(e.target)) setMenu(false);
  });

  menu.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      setMenu(false);
      caret.focus();
    }
  });

  // settings: populate, restore, persist
  function renderVoices() {
    const voices = englishVoices();
    if (voices.length < 2) return;
    voiceSelect.innerHTML = "";
    voices.forEach((voice) => {
      const option = document.createElement("option");
      option.value = voice.voiceURI;
      option.textContent = voice.name.replace(/\s+/g, " ").trim();
      voiceSelect.append(option);
    });
    syncMenu();
  }

  renderVoices();
  synth.addEventListener("voiceschanged", renderVoices);

  syncMenu();
  refreshLabel();

  function restart() {
    saveSettings();
    if (active) {
      stop();
      start();
    }
  }

  voiceSelect.addEventListener("change", () => {
    settings.voiceURI = voiceSelect.value;
    restart();
  });
  speedSelect.addEventListener("change", () => {
    settings.rate = Number(speedSelect.value);
    restart();
  });
  volumeRange.addEventListener("input", () => {
    settings.volume = Number(volumeRange.value);
    restart();
  });
  pitchRange.addEventListener("input", () => {
    settings.pitch = Number(pitchRange.value);
    restart();
  });
  highlightCheck.addEventListener("change", () => {
    settings.highlight = highlightCheck.checked;
    saveSettings();
    if (!settings.highlight) { clearHighlights(); unwrapWords(); }
    restart();
  });
  resumeCheck.addEventListener("change", () => {
    settings.resume = resumeCheck.checked;
    saveSettings();
    if (!settings.resume) clearPosition();
    refreshLabel();
  });
  topBtn.addEventListener("click", () => {
    clearPosition();
    refreshLabel();
    if (active) {
      stop();
      start();
    }
  });

  // alt+s toggles reading, but never inside a field or while the palette is open
  document.addEventListener("keydown", (e) => {
    if (e.repeat || !e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key !== "s" && e.key !== "S") return;
    const t = e.target;
    const tag = t && t.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (t && t.isContentEditable)) return;
    const palette = document.getElementById("palette");
    if (palette && !palette.hidden) return;
    e.preventDefault();
    button.click();
  });

  window.addEventListener("pagehide", stop);

  const tools = document.createElement("div");
  tools.className = "page-tools";
  wrap.append(button, caret, menu);
  tools.append(wrap);
  article.before(tools);
}
