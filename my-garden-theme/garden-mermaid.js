(function () {
  var blocks = document.querySelectorAll('pre.mermaid');
  if (!blocks.length) return;

  var nodes = [];
  blocks.forEach(function (pre) {
    var code = pre.querySelector('code');
    var div = document.createElement('div');
    div.className = 'mermaid';
    div.dataset.source = (code || pre).textContent;
    div.textContent = div.dataset.source;
    pre.replaceWith(div);
    nodes.push(div);
  });

  function css(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function draw(mermaid) {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'base',
      themeVariables: {
        fontFamily: 'Newsreader, Georgia, serif',
        background: css('--bg'),
        primaryColor: css('--rb-5'),
        primaryTextColor: css('--on-folder'),
        primaryBorderColor: css('--accent'),
        lineColor: css('--text'),
        secondaryColor: css('--rb-1'),
        secondaryTextColor: css('--on-folder'),
        tertiaryColor: css('--rb-0'),
        tertiaryTextColor: css('--on-folder')
      }
    });
    nodes.forEach(function (n) {
      n.removeAttribute('data-processed');
      n.textContent = n.dataset.source;
    });
    mermaid.run({ nodes: nodes });
  }

  var redrawTimer = null;
  var fontsReady = Promise.resolve();
  function scheduleDraw(mermaid) {
    clearTimeout(redrawTimer);
    redrawTimer = setTimeout(function () {
      fontsReady.then(function () { draw(mermaid); });
    }, 0);
  }

  var script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/mermaid@12.3.0/dist/mermaid.min.js';
  script.integrity = 'sha384-HHW54r639fK42Ip0coGF3mz8oSiGn0eEoWNTLs75X7H63pLSDBa0Tqs0RwGmLlXE';
  script.crossOrigin = 'anonymous';
  script.onload = function () {
    fontsReady = document.fonts && document.fonts.ready
      ? document.fonts.ready
      : Promise.resolve();
    scheduleDraw(window.mermaid);
    new MutationObserver(function () { scheduleDraw(window.mermaid); })
      .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    var systemTheme = matchMedia('(prefers-color-scheme: dark)');
    systemTheme.addEventListener('change', function () {
      scheduleDraw(window.mermaid);
    });
  };
  document.head.appendChild(script);
})();