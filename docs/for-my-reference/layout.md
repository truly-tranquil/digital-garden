---
title: "layout"
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
&lt;a class="badge stage-seedling" href="../seedlings/index.html"&gt;seedling&lt;/a&gt;
&lt;a class="badge stage-bud" href="../buds/index.html"&gt;bud&lt;/a&gt;
&lt;a class="badge stage-evergreen" href="../evergreens/index.html"&gt;evergreen&lt;/a&gt;
&lt;a class="tag" href="../by-tag/index.html#tag-reference"&gt;#reference&lt;/a&gt;
[a link](https://en.wikipedia.org/wiki/Diction){ target="_blank" }
![alt text](../assets/images/favicon.ico){ width="48" }</code></pre>

diction is done with the tip of the tongue on the teeth.
{: .card }

<a class="badge stage-seedling" href="../seedlings/index.html">seedling</a> <a class="badge stage-bud" href="../buds/index.html">bud</a> <a class="badge stage-evergreen" href="../evergreens/index.html">evergreen</a>

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

### cards with icons

put an icon at the start of a card with `card-icon`. the icon is an inline svg from the sprite, written as `<svg class="icon"><use href="#i-name"></use></svg>`; the names are listed on the [[icons]] page. the icon sits to the left of the content, tinted with the page accent.

```html
<div class="card card-icon" markdown>

<svg class="icon"><use href="#i-book"></use></svg>

**the title**

the body of the card

</div>
```

<div class="card card-icon" markdown>

<svg class="icon"><use href="#i-book"></use></svg>

**diction is done with the tip of the tongue on the teeth**

diction is done with the tip of the tongue on the teeth

</div>

### stage-tinted cards

a card can be tinted with the colour of a growth stage: add `stage-seedling`, `stage-bud` or `stage-evergreen` alongside `card`. the tint shows on the top edge bar.

```html
<div class="card stage-seedling" markdown>

a seedling note

</div>
```

<div class="card stage-seedling" markdown>

diction is done with the tip of the tongue on the teeth

</div>

<div class="card stage-bud" markdown>

diction is done with the tip of the tongue on the teeth

</div>

<div class="card stage-evergreen" markdown>

diction is done with the tip of the tongue on the teeth

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
