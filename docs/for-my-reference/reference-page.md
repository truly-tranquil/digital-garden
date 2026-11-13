---
stage: evergreen
tags: [reference, formatting, markdown]
planted: 2026-11-10
tended: 2026-11-10
width: full
---

# reference page

every piece of formatting this garden supports. each section shows the syntax first, then how it looks on the site. the sample sentence throughout is: diction is done with the tip of the tongue on the teeth.

<!-- this is a hidden comment. it never shows on the site. -->

## headings

````markdown
# heading 1
## heading 2
### heading 3
#### heading 4
##### heading 5
###### heading 6
````

# heading 1: diction is done with the tip of the tongue on the teeth

## heading 2: diction is done with the tip of the tongue on the teeth

### heading 3: diction is done with the tip of the tongue on the teeth

#### heading 4: diction is done with the tip of the tongue on the teeth

##### heading 5: diction is done with the tip of the tongue on the teeth

###### heading 6: diction is done with the tip of the tongue on the teeth

a custom heading id, so you can link straight to it:

```markdown
### a heading with a custom id { #my-custom-id }
```

### a heading with a custom id { #my-custom-id }

hover over any heading to see its permalink marker.

## emphasis and inline marks

```markdown
**bold** or __bold__
*italic* or _italic_
***bold and italic***
~~strikethrough~~
^^underline^^
==highlight==
H~2~O (subscript)
x^2^ (superscript)
`inline code`
```

**diction is done with the tip of the tongue on the teeth**

*diction is done with the tip of the tongue on the teeth*

***diction is done with the tip of the tongue on the teeth***

~~diction is done with the tip of the tongue on the teeth~~

^^diction is done with the tip of the tongue on the teeth^^

==diction is done with the tip of the tongue on the teeth==

diction is done with the tip of the tongue^1^ on the teeth~2~

`diction is done with the tip of the tongue on the teeth`

a paragraph break is a blank line. a line break inside a paragraph needs a `<br>`:

diction is done with<br>the tip of the tongue<br>on the teeth

## lists

nested items need four spaces of indentation, and a list needs a blank line before it.

```markdown
- unordered item
- another item
    - nested item
        - nested again

1. ordered item
2. another item
    1. nested ordered item
```

- diction is done with the tip of the tongue on the teeth
- the tongue
    - the tip
        - the very edge of the tip
- the teeth

1. diction is done with the tip of the tongue on the teeth
2. the tongue
    1. the tip
    2. the blade
3. the teeth

### task lists

```markdown
- [x] a finished task
- [ ] an unfinished task
```

- [x] diction is done with the tip of the tongue on the teeth
- [ ] diction is done with the tip of the tongue on the teeth
- [ ] a task with a nested step
    - [x] the nested step

## links

square brackets are written with codes in the box below so the garden doesn't turn the examples into real links.

<pre><code>[a link](https://en.wikipedia.org/wiki/Diction)
&lt;https://en.wikipedia.org/wiki/Diction&gt;
[a link with a hover title](https://en.wikipedia.org/wiki/Diction "diction")
[opens in a new tab](https://en.wikipedia.org/wiki/Diction){ target="_blank" }
[another note in the garden](reference-page.md)
[a heading in another note](reference-page.md#headings)
[jump to a heading on this page](#headings)
&nbsp;
wikilinks, like in obsidian:
[[reference-page]]
[[reference-page|a custom label]]
[[reference-page#headings]]
[[reference-page#headings|a custom label]]</code></pre>

- [diction is done with the tip of the tongue on the teeth](https://en.wikipedia.org/wiki/Diction)
- <https://en.wikipedia.org/wiki/Dental_consonant>
- [diction is done with the tip of the tongue on the teeth](https://en.wikipedia.org/wiki/Diction "a hover title")
- [diction is done with the tip of the tongue on the teeth](https://en.wikipedia.org/wiki/Diction){ target="_blank" }
- [diction is done with the tip of the tongue on the teeth](reference-page.md)
- [diction is done with the tip of the tongue on the teeth](reference-page.md#headings)
- [diction is done with the tip of the tongue on the teeth](#headings)
- [[reference-page]]
- [[reference-page|diction is done with the tip of the tongue on the teeth]]
- [[reference-page#headings]]
- [[reference-page#headings|diction is done with the tip of the tongue on the teeth]]

external links get a small favicon in front of them automatically.

## images

<pre><code>![alt text](../assets/favicon.ico)
![alt text](../assets/favicon.ico){ width="48" }
![alt text](../assets/favicon.ico "a hover title")
&nbsp;
or, like in obsidian, by file name from anywhere:
![[favicon.ico]]
![[favicon.ico|48]]</code></pre>

put image files in `docs/assets/`. the path is relative to the note it is written in, so a note in the top level of `docs/` uses `assets/favicon.ico`, and a note inside a folder such as `seedlings/` or `for-my-reference/` needs `../assets/favicon.ico`. the wikilink form finds the file by name, so it works from any folder.

a leaf drawn into the page itself, which always works:

![a leaf](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzcyQTU3QiIgZD0iTTEyIDJDNiA2IDQgMTIgNiAxOGMzLTEgNS0zIDYtNiAxIDMgMyA1IDYgNiAyLTYgMC0xMi02LTE2eiIvPjwvc3ZnPg==){ width="48" }

your favicon, which only shows if the path matches where the file really is:

![diction is done with the tip of the tongue on the teeth](../assets/favicon.ico){ width="48" }

## outgoing links and backlinks

links between notes are tracked automatically, and this note's own links are not shown to itself. the page labels them **outgoing links** and **backlinks**.

- a note that links to another note shows its destinations under **outgoing links** near the top of the page
- the note being linked to lists the notes that link to it under **backlinks** at the bottom, numbered like footnotes
- this works for wikilinks, normal `.md` links and embeds
- to add a link without writing one in the text, list it in the front matter with `links_to`, shown in the page metadata section below

## embedded notes

an exclamation mark in front of a wikilink pulls another note's content into this one, inside a framed block with a link back to its source. a section name after `#` embeds only that section.

<pre><code>![[note name]]
![[note name#a heading]]</code></pre>

this embeds the section called escaping from further down this page:

![[reference-page#escaping]]

embeds go two levels deep. relative links and footnotes inside an embedded note may not work, so keep embedded notes simple.

## blockquotes

```markdown
> a quote
>
> a second paragraph in the same quote
>
>> a quote inside a quote
```

> diction is done with the tip of the tongue on the teeth
>
> diction is done with the tip of the tongue on the teeth
>
>> diction is done with the tip of the tongue on the teeth

## callouts

obsidian-style callouts. add `-` after the type to make it collapsed, or `+` to make it foldable but open. text after the type becomes the title. these eight types show the eight callout colors, in order.

<pre><code>&gt; [!danger]- red, collapsed by default
&gt; the body of the callout
&nbsp;
&gt; [!warning] orange
&gt; the body of the callout
&nbsp;
&gt; [!tip] yellow
&gt; the body of the callout
&nbsp;
&gt; [!success] green
&gt; the body of the callout
&nbsp;
&gt; [!abstract] turquoise
&gt; the body of the callout
&nbsp;
&gt; [!note] blue
&gt; the body of the callout
&nbsp;
&gt; [!question]+ indigo, foldable and open by default
&gt; the body of the callout
&nbsp;
&gt; [!quote] purple
&gt; the body of the callout
&nbsp;</code></pre>

> [!danger]- red
> diction is done with the tip of the tongue on the teeth

> [!warning] orange
> diction is done with the tip of the tongue on the teeth

> [!tip] yellow
> diction is done with the tip of the tongue on the teeth

> [!success] green
> diction is done with the tip of the tongue on the teeth

> [!abstract] turquoise
> diction is done with the tip of the tongue on the teeth

> [!note] blue
> diction is done with the tip of the tongue on the teeth

> [!question]+ indigo
> diction is done with the tip of the tongue on the teeth

> [!quote] purple
> diction is done with the tip of the tongue on the teeth

> [!question]
> diction is done with the tip of the tongue on the teeth

> [!warning]
> diction is done with the tip of the tongue on the teeth

> [!failure]
> diction is done with the tip of the tongue on the teeth

> [!danger]
> diction is done with the tip of the tongue on the teeth

> [!bug]
> diction is done with the tip of the tongue on the teeth

> [!example]
> diction is done with the tip of the tongue on the teeth

> [!quote]
> diction is done with the tip of the tongue on the teeth

> [!tip] a custom title
> diction is done with the tip of the tongue on the teeth

> [!warning]- collapsed by default
> diction is done with the tip of the tongue on the teeth

> [!question]+ foldable, open by default
> diction is done with the tip of the tongue on the teeth

### native admonitions and collapsible blocks

```markdown
!!! note "a title"
    the body, indented four spaces

??? tip "collapsed by default"
    the body, indented four spaces

???+ example "open by default"
    the body, indented four spaces
```

!!! note "a native admonition"
    diction is done with the tip of the tongue on the teeth

??? tip "collapsible, closed by default"
    diction is done with the tip of the tongue on the teeth

???+ example "collapsible, open by default"
    diction is done with the tip of the tongue on the teeth

## code

````markdown
`inline code`

```python
print("a fenced block with a language")
```

```
a fenced block with no language
```
````

diction is done with the tip of the tongue on the teeth, as `inline code`.

```python
# diction is done with the tip of the tongue on the teeth
@speak_clearly
def say(sentence: str, volume: int = 3) -> str:
    """return the sentence, a little louder."""
    words = [w.upper() for w in sentence.split()]
    if volume > 2 and words:
        return " ".join(words) + "!"
    return sentence

class Tongue(Mouth):
    teeth = None

print(say("diction is done with the tip of the tongue on the teeth", 4.5))
```

```javascript
// diction is done with the tip of the tongue on the teeth
const say = async (sentence, volume = 3) => {
  const words = sentence.split(" ").map((w) => w.toUpperCase());
  if (volume > 2 && words.length) return `${words.join(" ")}!`;
  return sentence;
};
say("diction is done with the tip of the tongue on the teeth");
```

```css
.tongue:hover > .tip {
  color: #DF7386;
  margin: 0 1.5rem;
  transition: all 0.2s ease;
}
```

```html
<!-- diction is done with the tip of the tongue on the teeth -->
<a class="tongue" href="/teeth" id="tip">diction is done with the tip of the tongue on the teeth</a>
```

```yaml
# diction is done with the tip of the tongue on the teeth
sentence: diction is done with the tip of the tongue on the teeth
volume: 3
tags: [speech, diction]
enabled: true
```

```bash
# diction is done with the tip of the tongue on the teeth
echo "diction is done with the tip of the tongue on the teeth" | tr a-z A-Z
python garden_build.py serve
```

```json
{
  "sentence": "diction is done with the tip of the tongue on the teeth",
  "volume": 3,
  "loud": true,
  "teeth": null
}
```

```
a fenced block with no language is plain: diction is done with the tip of the tongue on the teeth
```

## tables

```markdown
| left | center | right |
| :--- | :----: | ----: |
| a    |   b    |     c |
```

| left aligned | centered | right aligned |
| :--- | :---: | ---: |
| diction is done | with the tip of the tongue | on the teeth |
| diction is done | with the tip of the tongue | on the teeth |

## footnotes

```markdown
a sentence with a footnote.[^note]

[^note]: the footnote text, which collects at the bottom of the page.
```

footnote markers and their numbers are colored in rainbow order, repeating after eight. this page uses all eight so every color shows.

diction is done with the tip of the tongue on the teeth.[^tongue] diction is done with the tip of the tongue on the teeth.[^teeth] diction is done with the tip of the tongue on the teeth.[^lips] diction is done with the tip of the tongue on the teeth.[^breath] diction is done with the tip of the tongue on the teeth.[^jaw] diction is done with the tip of the tongue on the teeth.[^palate] diction is done with the tip of the tongue on the teeth.[^throat] diction is done with the tip of the tongue on the teeth.[^voice]
[^tongue]: the tip of the tongue touches the back of the upper teeth for sounds like t and d. this text collects at the bottom of the page.

[^teeth]: diction is done with the tip of the tongue on the teeth.

[^lips]: diction is done with the tip of the tongue on the teeth.

[^breath]: diction is done with the tip of the tongue on the teeth.

[^jaw]: diction is done with the tip of the tongue on the teeth.

[^palate]: diction is done with the tip of the tongue on the teeth.

[^throat]: diction is done with the tip of the tongue on the teeth.

[^voice]: diction is done with the tip of the tongue on the teeth.

## definition lists

```markdown
term
:   its definition, with a colon and three spaces
```

tongue
:   diction is done with the tip of the tongue on the teeth

teeth
:   diction is done with the tip of the tongue on the teeth

## abbreviations

```markdown
the TTT is hoverable.

*[TTT]: tip of the tongue on the teeth
```

diction is done with the TTT. hover over the underlined letters.

*[TTT]: tip of the tongue on the teeth

## tabs

````markdown
=== "first tab"
    the content, indented four spaces

=== "second tab"
    more content
````

the first eight tab labels show all eight rainbow colors; additional tabs continue the cycle. on narrow screens, scroll horizontally through the labels.

=== "first tab"
    diction is done with the tip of the tongue on the teeth

=== "second tab"
    diction is done with the **tip** of the *tongue* on the ==teeth==

=== "third tab"
    - diction is done
    - with the tip of the tongue
    - on the teeth

=== "fourth tab"
    diction is done with the tip of the tongue on the teeth

=== "fifth tab"
    diction is done with the tip of the tongue on the teeth

=== "sixth tab"
    diction is done with the tip of the tongue on the teeth

=== "seventh tab"
    diction is done with the tip of the tongue on the teeth

=== "eighth tab"
    diction is done with the tip of the tongue on the teeth

=== "ninth tab"
    diction is done with the tip of the tongue on the teeth

=== "tenth tab"
    diction is done with the tip of the tongue on the teeth

=== "eleventh tab"
    diction is done with the tip of the tongue on the teeth

=== "twelfth tab"
    diction is done with the tip of the tongue on the teeth

## attribute lists

add classes, ids and attributes to almost any element. the classes below come from this site's stylesheet. a badge takes one of the stage classes to pick its color: `stage-seedling`, `stage-bud` or `stage-evergreen`. wrap a badge or tag in a link to make it clickable.

<pre><code>a paragraph turned into a card.
{: .card }
&nbsp;
&lt;a class="badge stage-seedling" href="../seedlings/"&gt;seedling&lt;/a&gt;
&lt;a class="badge stage-bud" href="../buds/"&gt;bud&lt;/a&gt;
&lt;a class="badge stage-evergreen" href="../evergreens/"&gt;evergreen&lt;/a&gt;
&lt;a class="tag" href="../by-tag/#tag-reference"&gt;#reference&lt;/a&gt;
[a link](https://en.wikipedia.org/wiki/Diction){ target="_blank" }
![alt text](../assets/favicon.ico){ width="48" }</code></pre>

diction is done with the tip of the tongue on the teeth.
{: .card }

<a class="badge stage-seedling" href="../../seedlings/">seedling</a> <a class="badge stage-bud" href="../../buds/">bud</a> <a class="badge stage-evergreen" href="../../evergreens/">evergreen</a> <a class="tag" href="../../by-tag/#tag-reference">#reference</a> <a class="tag" href="../../by-tag/#tag-formatting">#formatting</a>

## raw html

html works anywhere in markdown.

```html
<kbd>Ctrl</kbd> + <kbd>K</kbd>
<mark>highlighted</mark>
<u>underlined</u>
<small>small text</small>
H<sub>2</sub>O and x<sup>2</sup>
<abbr title="tip of the tongue on the teeth">TTT</abbr>
<!-- a hidden comment -->
<details markdown="1">
<summary>a collapsible section</summary>

the contents, which can contain **markdown**.

</details>
```

press <kbd>Ctrl</kbd> + <kbd>K</kbd> and say: diction is done with the tip of the tongue on the teeth

<mark>diction is done with the tip of the tongue on the teeth</mark>

<u>diction is done with the tip of the tongue on the teeth</u>

<small>diction is done with the tip of the tongue on the teeth</small>

diction is done with the tip of the tongue<sup>1</sup> on the teeth<sub>2</sub>

<details markdown="1">
<summary>a collapsible section: diction is done with the tip of the tongue on the teeth</summary>

diction is done with the tip of the tongue on the **teeth**.

</details>

## horizontal rules

```markdown
---
```

diction is done with the tip of the tongue on the teeth

---

diction is done with the tip of the tongue on the teeth

## layout helpers

these use `md_in_html`, so write `markdown` on each div and leave blank lines around the content.

```html
<div class="grid" markdown>

<div class="card" markdown>

**card one**

the content

</div>

<div class="card" markdown>

**card two**

the content

</div>

</div>
```

### grid of cards

<div class="grid" markdown>

<div class="card" markdown>

**card one**

diction is done with the tip of the tongue on the teeth

</div>

<div class="card" markdown>

**card two**

diction is done with the tip of the tongue on the teeth

</div>

<div class="card" markdown>

**card three**

diction is done with the tip of the tongue on the teeth

</div>

</div>

### masonry

```html
<div class="masonry" markdown>
cards of different heights go here
</div>
```

<div class="masonry" markdown>

<div class="card" markdown>

**short card**

diction is done with the tip of the tongue on the teeth

</div>

<div class="card" markdown>

**tall card**

diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth.

</div>

<div class="card" markdown>

**medium card**

diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth.

</div>

<div class="card" markdown>

**another short card**

diction is done with the tip of the tongue on the teeth

</div>

</div>

### text columns

```html
<div class="columns-2" markdown>
text that flows into two columns (use columns-3 for three)
</div>
```

<div class="columns-2" markdown>

diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth.

</div>

## diagrams

mermaid diagrams go in a fenced block with the language `mermaid`. they follow the light and dark theme, and the mermaid library only loads on pages that contain a diagram.

````markdown
```mermaid
graph LR
    seedling --> bud --> evergreen
```
````

```mermaid
graph LR
    seedling --> bud --> evergreen
```

## math

inline math uses single dollar signs, and display math uses double dollar signs. KaTeX is only loaded on pages containing math.

````markdown
The area of a circle is $A = \pi r^2$.

$$
\int_0^1 x^2\,dx = \frac{1}{3}
$$
````

The area of a circle is $A = \pi r^2$.

$$
\int_0^1 x^2\,dx = \frac{1}{3}
$$

## color palette

the eight accent colors side by side, in the order they are used for tabs, footnotes and the numbered backlinks. the sidebar and page accents follow the same order from top to bottom.

<div class="swatches">
<span style="background: var(--rb-0)">1 red</span>
<span style="background: var(--rb-1)">2 orange</span>
<span style="background: var(--rb-2)">3 yellow</span>
<span style="background: var(--rb-3)">4 green</span>
<span style="background: var(--rb-4)">5 turquoise</span>
<span style="background: var(--rb-5)">6 blue</span>
<span style="background: var(--rb-6)">7 indigo</span>
<span style="background: var(--rb-7)">8 purple</span>
</div>

## escaping

a backslash in front of a character shows it literally.

```markdown
\*not italic\*
\# not a heading
```

\*diction\* is done with the tip of the tongue on the teeth

## page metadata

the block at the very top of a note, between two `---` lines, is its front matter.

```yaml
---
title: a custom title (otherwise the first heading is used)
stage: seedling
tags: [idea, book]
planted: 2026-11-10
tended: 2026-11-10
links_to: [another note, a third note]
template: home.html
width: full
# draft: true
# aliases: [old-note-name]
---
```

- `stage` shows a colored badge: `seedling`, `bud` or `evergreen`
- `tags` show as pills under the title and link to their section on the by-tag page; search for notes by tag with `#tag`
- `links_to` adds links to other notes by title or filename, even if the text doesn't link to them
- `planted` records when a note was created, while `tended` shows the last-tended date and sorts the "recently tended" widget
- `template: home.html` is only for your homepage; it enables the stats, note of the day (notes planted on the visitor's local date only), recent notes, clock, stage legend and garden graph widgets
- `width: full` widens the page content; this reference page uses it
- `draft: true` keeps a note out of the built site
- `aliases` creates redirect pages for old note paths

## using the garden

- the homepage's **how to read this garden** widget explains the seedling, bud and evergreen stages
- the **index**, **random** and **style** buttons are at the upper left of the header; style switches between light and dark mode
- the search field is at the upper right. Press `/` outside a text field to focus it. Use `#tag` in a search to find notes with that tag.
- on pages with a table of contents, use the drawer on the right to open or collapse it

## not supported

Code block titles and line highlighting are not configured.