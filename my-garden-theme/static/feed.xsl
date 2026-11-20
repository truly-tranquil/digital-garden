<?xml version="1.0" encoding="utf-8"?>
<!-- Atom feed stylesheet: renders feed.xml as a readable page instead of raw XML.
     A neutral, mid-tone palette of its own so it reads the same regardless of
     the reader's mode. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atom="http://www.w3.org/2005/Atom">
  <xsl:output method="html" encoding="utf-8" indent="yes"/>

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <title><xsl:value-of select="atom:feed/atom:title"/> - rss feed</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <meta name="color-scheme" content="light"/>
        <style>
          /* A feed reader page, not the garden: one neutral mid-tone palette that
             reads the same in any light. No site look, no dark-mode swap. */
          :root {
            color-scheme: light;
            --bg: #E7E2D9;
            --surface: #DCD6CA;
            --text: #3E3B34;
            --accent-text: #6E5A3E;
            --border: #C3BCAD;
          }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            background: var(--bg);
            color: var(--text);
            font-family: 'Newsreader', Georgia, 'Times New Roman', serif;
            font-size: 1.1rem;
            line-height: 1.6;
          }
          main {
            max-width: 46rem;
            margin: 0 auto;
            padding: 2.5rem 1.5rem 4rem;
          }
          h1 {
            margin: 0 0 0.25rem;
            font-size: 2rem;
            letter-spacing: -0.02em;
          }
          h1 a { color: var(--accent-text); text-decoration: none; }
          .lede { margin: 0 0 1.5rem; opacity: 0.8; font-size: 0.95rem; }
          .lede code {
            font-family: ui-monospace, 'Cascadia Code', Menlo, Consolas, monospace;
            font-size: 0.85em;
            background: var(--surface);
            padding: 0.1em 0.4em;
            border-radius: 6px;
          }
          ol { margin: 0; padding: 0; list-style: none; }
          li {
            padding: 0.9rem 0;
            border-top: 2px solid var(--border);
          }
          h2 { margin: 0 0 0.15rem; font-size: 1.2rem; }
          h2 a { color: var(--accent-text); text-decoration: none; }
          h2 a:hover, h1 a:hover { text-decoration: underline; text-underline-offset: 3px; }
          .when {
            margin: 0 0 0.35rem;
            font-family: ui-monospace, 'Cascadia Code', Menlo, Consolas, monospace;
            font-size: 0.78rem;
            opacity: 0.72;
          }
          .summary { margin: 0; font-size: 0.95rem; opacity: 0.88; }
          footer {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 2px solid var(--border);
            font-size: 0.85rem;
            opacity: 0.75;
          }
        </style>
      </head>
      <body>
        <main>
          <h1><a href="./"><xsl:value-of select="atom:feed/atom:title"/></a></h1>
          <p class="lede">
            rss feed &#183; updated <xsl:value-of select="atom:feed/atom:updated"/> &#183; subscribe with any feed reader to <code>feed.xml</code>
          </p>
          <ol>
            <xsl:for-each select="atom:feed/atom:entry">
              <li>
                <h2><a href="{atom:link/@href}"><xsl:value-of select="atom:title"/></a></h2>
                <p class="when"><xsl:value-of select="atom:updated"/></p>
                <p class="summary"><xsl:value-of select="atom:summary"/></p>
              </li>
            </xsl:for-each>
          </ol>
          <footer>
            <a href="./">back to the garden</a>
          </footer>
        </main>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
