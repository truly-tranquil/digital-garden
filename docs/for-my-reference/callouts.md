---
title: "callouts"
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

## pull quotes

a quote lifted out of the flow: centred, oversized, italicised and capped by a large opening quotation mark.

```html
<blockquote class="pull">a quotation, centred and oversized</blockquote>
```

<blockquote class="pull">diction is done with the tip of the tongue on the teeth</blockquote>

## callouts

obsidian-style callouts. add `-` after the type to make it collapsed, or `+` to make it foldable but open. text after the type becomes the title. these eight types show the eight callout colors, in order.

<pre><code>&gt; [!danger]- red, collapsed by default
&gt; the body of the callout
&gt; &nbsp;
&gt; [!warning] orange
&gt; the body of the callout
&gt; &nbsp;
&gt; [!tip] yellow
&gt; the body of the callout
&gt; &nbsp;
&gt; [!success] green
&gt; the body of the callout
&gt; &nbsp;
&gt; [!abstract] turquoise
&gt; the body of the callout
&gt; &nbsp;
&gt; [!note] blue
&gt; the body of the callout
&gt; &nbsp;
&gt; [!question]+ indigo, foldable and open by default
&gt; the body of the callout
&gt; &nbsp;
&gt; [!quote] purple
&gt; the body of the callout
&gt; &nbsp;</code></pre>

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

> [!question]+ indigo, foldable and open by default
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

## seed packets

an unplanted thought: a dashed-border box with a sprout marker, for ideas that have nowhere to grow yet. write it as a div with `class="seed-packet"` and the `markdown` attribute.

```html
<div class="seed-packet" markdown>

an unplanted thought that deserves to be grown

</div>
```

<div class="seed-packet" markdown>

diction is done with the tip of the tongue on the teeth

</div>
