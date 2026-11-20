---
title: "text"
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

diction is done with the tip of the tongue on the teeth^1^ on the teeth~2~

`diction is done with the tip of the tongue on the teeth`

a paragraph break is a blank line. a line break inside a paragraph needs a `<br>`:

diction is done with<br>the tip of the tongue<br>on the teeth

## abbreviations

```markdown
the TTT is hoverable.

*[TTT]: tip of the tongue on the teeth
```

diction is done with the TTT. hover over the underlined letters.

*[TTT]: tip of the tongue on the teeth

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

## horizontal rules

```markdown
---
```

diction is done with the tip of the tongue on the teeth

---

diction is done with the tip of the tongue on the teeth

## vine dividers

a horizontal rule with a small vine centred on it: write the rule with `class="vine"`.

```html
<hr class="vine">
```

diction is done with the tip of the tongue on the teeth

<hr class="vine">

diction is done with the tip of the tongue on the teeth

## sidenotes

an aside that floats in the right margin on wide screens and stacks full-width on narrow ones. wrap it in a div with `class="sidenote"` and the `markdown` attribute, and leave blank lines around the content.

```html
<div class="sidenote" markdown>

the note, kept close to the sentence it belongs to

</div>
```

<div class="sidenote" markdown>

diction is done with the tip of the tongue on the teeth

</div>

diction is done with the tip of the tongue on the teeth, so the text wraps around the note on wide screens and reads below it on narrow ones. diction is done with the tip of the tongue on the teeth. diction is done with the tip of the tongue on the teeth.

## escaping

a backslash in front of a character shows it literally.

```markdown
\*not italic\*
\# not a heading
```

\*diction\* is done with the tip of the tongue on the teeth
