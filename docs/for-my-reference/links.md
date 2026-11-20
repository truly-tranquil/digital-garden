---
title: "links"
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

## links

square brackets are written with codes in the box below so the garden doesn't turn the examples into real links.

<pre><code>[a link](https://en.wikipedia.org/wiki/Diction)
&lt;https://en.wikipedia.org/wiki/Diction&gt;
[a link with a hover title](https://en.wikipedia.org/wiki/Diction "diction")
[opens in a new tab](https://en.wikipedia.org/wiki/Diction){ target="_blank" }
[another note in the garden](for_my_reference.md)
[a heading in another note](text.md#headings)
[jump to a heading on this page](#links)
&nbsp;
wikilinks, like in obsidian:
[[for_my_reference]]
[[for_my_reference|a custom label]]
[[text#headings]]
[[text#headings|a custom label]]
[[text#escaping]]</code></pre>

- [diction is done with the tip of the tongue on the teeth](https://en.wikipedia.org/wiki/Diction)
- <https://en.wikipedia.org/wiki/Dental_consonant>
- [diction is done with the tip of the tongue on the teeth](https://en.wikipedia.org/wiki/Diction "a hover title")
- [diction is done with the tip of the tongue on the teeth](https://en.wikipedia.org/wiki/Diction){ target="_blank" }
- [diction is done with the tip of the tongue on the teeth](for_my_reference.md)
- [diction is done with the tip of the tongue on the teeth](text.md#headings)
- [diction is done with the tip of the tongue on the teeth](#links)
- [[for_my_reference]]
- [[for_my_reference|diction is done with the tip of the tongue on the teeth]]
- [[text#headings]]
- [[text#headings|diction is done with the tip of the tongue on the teeth]]

external links get a small icon in front of them automatically (the arrow), and you can pick a different one per link with `data-icon` &mdash; see [external link icons](#external-link-icons).

## external link icons

every external link gets a small icon in front of it, drawn from an inline svg sprite in the page &mdash; no other site is contacted. the default is the arrow. to pick a different one for a specific link, add `data-icon` with the icon's name:

```markdown
[a video about diction](https://www.youtube.com/watch?v=diction){ data-icon="video" }
```

or write the anchor by hand:

```html
<a href="https://www.youtube.com/watch?v=diction" data-icon="video">a video about diction</a>
```

a selection of icons, each linking to wikipedia's diction article (the full name list lives on the [[icons]] page):

- [default arrow](https://en.wikipedia.org/wiki/Diction){ data-icon="external" }
- [article](https://en.wikipedia.org/wiki/Diction){ data-icon="article" }
- [paper](https://en.wikipedia.org/wiki/Diction){ data-icon="paper" }
- [code](https://en.wikipedia.org/wiki/Diction){ data-icon="code" }
- [video](https://en.wikipedia.org/wiki/Diction){ data-icon="video" }
- [audio](https://en.wikipedia.org/wiki/Diction){ data-icon="audio" }
- [book](https://en.wikipedia.org/wiki/Diction){ data-icon="book" }
- [chat](https://en.wikipedia.org/wiki/Diction){ data-icon="chat" }
- [tool](https://en.wikipedia.org/wiki/Diction){ data-icon="tool" }
- [map](https://en.wikipedia.org/wiki/Diction){ data-icon="map" }
- [mail](https://en.wikipedia.org/wiki/Diction){ data-icon="mail" }
- [feed](https://en.wikipedia.org/wiki/Diction){ data-icon="feed" }
- [profile](https://en.wikipedia.org/wiki/Diction){ data-icon="profile" }
- [photo](https://en.wikipedia.org/wiki/Diction){ data-icon="photo" }
- [download](https://en.wikipedia.org/wiki/Diction){ data-icon="download" }

| `data-icon` | pick it for |
| :--- | :--- |
| `external` | the default: a link that leaves the site |
| `article` | essays, blog posts, news stories |
| `paper` | papers, journals, PDFs |
| `code` | source code, documentation, repositories |
| `video` | videos and talks |
| `audio` | podcasts and music |
| `book` | books and other reading |
| `chat` | forums and chat threads |
| `tool` | tools, apps and services |
| `map` | maps and places |
| `mail` | email addresses |
| `feed` | RSS feeds |
| `profile` | personal pages and profiles |
| `photo` | photo galleries and images |
| `download` | files meant to be saved |

an unknown name falls back to the arrow. the icons are `aria-hidden`, so screen readers hear the link text as before. the `data-icon` table above lists the original fifteen; [[icons]] lists every name in the sprite.

## note icons

the same names double as the value of the `icon` front matter key. set it to mark a note — `icon: code` — and the glyph is injected automatically wherever the note is referenced from another page: inline links (wikilinks and `.md` links), the outgoing links chips, the backlinks list at the bottom of the page, related notes, the generated stage and by-tag lists, the search dropdown, the note of the day and the recently tended widget. the note's own page does not show it. an unknown name warns at build time (an error for the validator) and the note renders iconless; a name that passes validation renders everywhere listed here. [[icons]] lists every name.

## inline icons in raw html

the same sprite can be used in raw html anywhere a `markdown` block is allowed: an svg with `class="icon"` and a `<use>` pointing at the sprite id for any of the names on the [[icons]] page.

```html
<svg class="icon"><use href="#i-book"></use></svg>
```

diction is done with the <svg class="icon"><use href="#i-book"></use></svg> tip of the tongue on the <svg class="icon"><use href="#i-map"></use></svg> teeth.

## outgoing links and backlinks

links between notes are tracked automatically, and this note's own links are not shown to itself. the page labels them **outgoing links** and **backlinks**.

- a note that links to another note shows its destinations under **outgoing links** near the top of the page
- the note being linked to lists the notes that link to it under **backlinks** at the bottom, numbered like footnotes
- this works for wikilinks, normal `.md` links and embeds
- to add a link without writing one in the text, list it in the front matter with `links_to`, shown in the page metadata section below
