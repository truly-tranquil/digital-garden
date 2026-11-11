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
        primaryColor: css('--surface'),
        primaryTextColor: css('--text'),
        primaryBorderColor: css('--accent'),
        lineColor: css('--text'),
        secondaryColor: css('--bg'),
        tertiaryColor: css('--surface')
      }
    });
    nodes.forEach(function (n) {
      n.removeAttribute('data-processed');
      n.textContent = n.dataset.source;
    });
    mermaid.run({ nodes: nodes });
  }

  var script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js';
  script.onload = function () {
    draw(window.mermaid);
    new MutationObserver(function () { draw(window.mermaid); })
      .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  };
  document.head.appendChild(script);
})();