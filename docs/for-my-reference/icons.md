---
title: "icons"
stage: evergreen
tags: []
planted: 2026-11-17
tended: 2026-11-17
links_to: [links, frontmatter]
unlisted: true
archived: false
random: false
icon: sparkle
aliases: []
draft: false
---
every glyph in the garden is an inline svg from a single sprite in the page — no icon site is contacted and no icon font is loaded. **everything on this page is permissive-licensed** (MIT, ISC, Apache-2.0) and free to use, including outside this garden. the source and license ledger lives on [credits](/credits.html#icons).

there is one list. every icon in it:

- works as a note icon via `icon:` front matter (see [[frontmatter]])
- works inline as raw html: `<svg class="icon"><use href="#i-name"></use></svg>`
- works as a hidden collectible — plant one with `<!-- trinket:name -->` and let readers find it
- works as a browser-tab favicon replacement once found (chosen on the menagerie)

## planting and keeping a collectible

a trinket hides inside a note, unannounced, and is found by wandering. plant one anywhere in the markdown body:

    <!-- trinket:acorn -->

to stick one to a spot on the page instead of flowing with the text, add positional properties — any of `top`, `right`, `bottom`, `left`, `rotate`:

    <!-- trinket:butterfly top=3rem right=1rem rotate=-8 -->

notes on the mechanics:

- found names are kept in this browser under `foraging:collection` — nowhere else
- **every icon in the list below can be a collectible**; unknown marker names pass through untouched, so a typo never breaks a build
- the menagerie shelf only shows the icons actually used on the site at build time — anything referenced by the theme, by note front matter, or by a trinket marker. the rest of the list waits until some page reaches for it
- found collectibles can each be worn as this site's browser-tab icon; the choice lives in this browser, and resetting the menagerie also takes the icon off
- a page carries one `?` in its metadata line for every collectible planted on it, which flips to the glyph once found

## the garden icons — the big list

<div class="icon-grid">
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-acorn"></use></svg><code>acorn</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-arrow-square-out"></use></svg><code>arrow-square-out</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-article"></use></svg><code>article</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-asterisk-simple"></use></svg><code>asterisk-simple</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-audio"></use></svg><code>audio</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-bee"></use></svg><code>bee</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-bell"></use></svg><code>bell</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-bird"></use></svg><code>bird</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-book"></use></svg><code>book</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-book-open"></use></svg><code>book-open</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-bookmark"></use></svg><code>bookmark</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-bread"></use></svg><code>bread</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-bug"></use></svg><code>bug</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-butterfly"></use></svg><code>butterfly</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-cactus"></use></svg><code>cactus</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-cake"></use></svg><code>cake</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-calendar"></use></svg><code>calendar</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-camera"></use></svg><code>camera</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-carrot"></use></svg><code>carrot</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-cassette-tape"></use></svg><code>cassette-tape</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-chat"></use></svg><code>chat</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-chat-circle"></use></svg><code>chat-circle</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-check-square"></use></svg><code>check-square</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-clock"></use></svg><code>clock</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-cloud"></use></svg><code>cloud</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-cloud-arrow-up"></use></svg><code>cloud-arrow-up</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-cloud-rain"></use></svg><code>cloud-rain</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-cloud-snow"></use></svg><code>cloud-snow</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-cloud-sun"></use></svg><code>cloud-sun</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-code"></use></svg><code>code</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-coffee"></use></svg><code>coffee</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-compass"></use></svg><code>compass</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-cursor-text"></use></svg><code>cursor-text</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-database"></use></svg><code>database</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-download"></use></svg><code>download</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-drop"></use></svg><code>drop</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-envelope"></use></svg><code>envelope</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-eraser"></use></svg><code>eraser</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-external"></use></svg><code>external</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-feather"></use></svg><code>feather</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-feed"></use></svg><code>feed</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-file-code"></use></svg><code>file-code</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-film-strip"></use></svg><code>film-strip</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-fish"></use></svg><code>fish</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-flower"></use></svg><code>flower</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-flower-lotus"></use></svg><code>flower-lotus</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-flower-tulip"></use></svg><code>flower-tulip</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-game-controller"></use></svg><code>game-controller</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-gear"></use></svg><code>gear</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-git-branch"></use></svg><code>git-branch</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-github-logo"></use></svg><code>github-logo</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-guitar"></use></svg><code>guitar</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-hand"></use></svg><code>hand</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-headphones"></use></svg><code>headphones</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-heart"></use></svg><code>heart</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-highlighter"></use></svg><code>highlighter</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-house"></use></svg><code>house</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-ice-cream"></use></svg><code>ice-cream</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-image"></use></svg><code>image</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-key"></use></svg><code>key</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-ladybug"></use></svg><code>ladybug</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-laptop"></use></svg><code>laptop</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-leaf"></use></svg><code>leaf</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-link"></use></svg><code>link</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-link-simple"></use></svg><code>link-simple</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-list"></use></svg><code>list</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-list-bullets"></use></svg><code>list-bullets</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-magnifying-glass"></use></svg><code>magnifying-glass</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-mail"></use></svg><code>mail</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-map"></use></svg><code>map</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-map-pin"></use></svg><code>map-pin</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-megaphone"></use></svg><code>megaphone</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-microphone"></use></svg><code>microphone</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-monitor"></use></svg><code>monitor</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-moon"></use></svg><code>moon</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-moon-stars"></use></svg><code>moon-stars</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-mountains"></use></svg><code>mountains</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-mushroom"></use></svg><code>mushroom</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-music-notes"></use></svg><code>music-notes</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-newspaper"></use></svg><code>newspaper</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-notebook"></use></svg><code>notebook</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-paper"></use></svg><code>paper</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-paper-plane-right"></use></svg><code>paper-plane-right</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-paw-print"></use></svg><code>paw-print</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-pen"></use></svg><code>pen</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-pen-nib"></use></svg><code>pen-nib</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-pencil"></use></svg><code>pencil</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-photo"></use></svg><code>photo</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-plant"></use></svg><code>plant</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-profile"></use></svg><code>profile</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-quotes"></use></svg><code>quotes</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-rocket"></use></svg><code>rocket</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-scissors"></use></svg><code>scissors</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-seed"></use></svg><code>seed</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-smiley"></use></svg><code>smiley</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-snail"></use></svg><code>snail</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-snowflake"></use></svg><code>snowflake</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-sparkle"></use></svg><code>sparkle</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-star"></use></svg><code>star</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-sun"></use></svg><code>sun</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-sun-dim"></use></svg><code>sun-dim</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-sun-horizon"></use></svg><code>sun-horizon</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-tag"></use></svg><code>tag</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-terminal-window"></use></svg><code>terminal-window</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-tool"></use></svg><code>tool</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-tree"></use></svg><code>tree</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-tree-evergreen"></use></svg><code>tree-evergreen</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-umbrella"></use></svg><code>umbrella</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-upload"></use></svg><code>upload</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-video"></use></svg><code>video</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-vinyl-record"></use></svg><code>vinyl-record</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-waves"></use></svg><code>waves</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-wind"></use></svg><code>wind</code></div>
<div class="icon-cell"><svg class="icon" aria-hidden="true"><use href="#i-wine"></use></svg><code>wine</code></div>
</div>

don't sprinkle raw svg markup through notes for a glyph that exists — reach for the sprite. and don't hand-write `#i-` references with made-up names; the names are the list.
