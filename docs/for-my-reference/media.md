---
title: "media"
stage: "evergreen"
tags: [reference]
planted: "2026-11-16"
tended: "2026-11-16"
links_to: []
unlisted: true
archived: false
random: false
icon: code
aliases: []
draft: false
---
the syntax first, then how it looks on the site. the sample sentence throughout is: diction is done with the tip of the tongue on the teeth.

## images

<pre><code>![alt text](../assets/images/favicon.ico)
![alt text](../assets/images/favicon.ico){ width="48" }
![alt text](../assets/images/favicon.ico "a hover title")
&nbsp;
or, like in obsidian, by file name from anywhere:
![[favicon.ico]]
![[favicon.ico|48]]</code></pre>

put image files in `docs/assets/`. the path is relative to the note it is written in, so a note in the top level of `docs/` uses `assets/favicon.ico`, and a note inside a folder such as `seedlings/` or `for-my-reference/` needs `../assets/images/favicon.ico`. the wikilink form finds the file by name, so it works from any folder.

at build time every local raster image gets its intrinsic `width` and `height`, so the page reserves the space before the file loads, plus `decoding="async"` and a `loading` hint: the first image on a page loads eagerly, the rest lazily. images wider than 1200px also get a `srcset` of 480px, 960px and 1440px variants generated next to the original. writing `{ width="48" }` yourself skips the added dimensions and leaves the image exactly that size.

a leaf drawn into the page itself, which always works:

![a leaf](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzcyQTU3QiIgZD0iTTEyIDJDNiA2IDQgMTIgNiAxOGMzLTEgNS0zIDYtNiAxIDMgMyA1IDYgNiAyLTYgMC0xMi02LTE2eiIvPjwvc3ZnPg==){ width="48" }

your favicon, which only shows if the path matches where the file really is:

![diction is done with the tip of the tongue on the teeth](../assets/images/favicon.ico){ width="48" }

## embedded notes

an exclamation mark in front of a wikilink pulls another note's content into this one, inside a framed block with a link back to its source. a section name after `#` embeds only that section.

<pre><code>![[note name]]
![[note name#a heading]]</code></pre>

this embeds the section called escaping from the text page:

![[text#escaping]]

embeds go two levels deep. relative links and footnotes inside an embedded note may not work, so keep embedded notes simple.
