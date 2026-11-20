---
title: "front matter"
stage: evergreen
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

the front matter block at the very top of a note, between two `---` lines, controls how the note is filed, dated and linked. every key is optional; an unknown key is accepted by the build but reported by the validator as a notice, and a duplicate key is an error.

## the keys

```yaml
---
title: a custom title
stage: seedling
tags: [idea, book]
planted: 2026-11-16
tended: 2026-11-16
links_to: [another note, a third note]
unlisted: false
archived: false
random: true
icon: book
aliases: [old-note-name]
draft: false
---
```

| key | what it does |
| :--- | :--- |
| `title` | custom title. without it, the first heading in the note is used. drafts without a title get one humanized from the filename |
| `stage` | `seedling`, `bud` or `evergreen`. notes in `docs/seedlings/`, `docs/buds/` and `docs/evergreens/` infer this from the folder; an invalid value warns and falls back to the folder |
| `tags` | lowercase words shown as pills under the title. each tag links to its section on the by-tag page, and searching with `#tag` finds notes by tag |
| `planted` | ISO date (`YYYY-MM-DD`). when empty, the first commit that touched the file is used |
| `tended` | ISO date. when empty, the last commit that touched the file is used — or today while the file has uncommitted changes. a set `tended` always wins over git history |
| `links_to` | adds outgoing links to other notes by title or filename, even without mentioning them in the text. the spaced variant `links to` is accepted as well |
| `unlisted` | `true` hides the note from the indexes, navigation, feed, graph, random pick, recent list and sitemap. it stays searchable and directly viewable. this page uses it |
| `archived` | `true` moves the note into the archive group in the sidebar, above forum, with the same exclusions as `unlisted` (feed, by-tag, graph, random, recent, sitemap). it stays searchable, viewable and aliasable. notes placed in `docs/archive/` are archived automatically, without the key |
| `random` | `false` keeps the note out of the random button and the note of the day. default is `true` |
| `icon` | one of the icon names listed on the [[icons]] page (all drawn from Phosphor). the glyph marks the note wherever it is referenced: inline links in other notes, the outgoing links chips, backlinks, related notes, the stage and by-tag lists, search results, the note of the day and recently tended. an unknown name warns (an error for the validator) and leaves the note iconless |
| `aliases` | old paths that redirect to this note. useful after renaming a note |
| `draft` | `true` keeps the note out of the built site entirely. drafts folder does the same for every file in it |

## folder inference

placement can replace a key:

- `docs/seedlings/*.md`, `docs/buds/*.md`, `docs/evergreens/*.md` → `stage` from the folder name
- `docs/archive/*.md` → treated as archived, exactly like `archived: true`
- `docs/drafts/*.md` → excluded from the build entirely, like `draft: true`

## dates in practice

- a note you never commit and never write dates for still builds: both dates fall back to today
- a note that is committed but never hand-dated gets git's first/last commit dates
- a hand-written date always beats git history
- recently tended and the feed sort by `tended`

## canonical order

new notes are expected to list the keys in this order; every built note in the garden does:

```yaml
title
stage
tags
planted
tended
links_to
unlisted
archived
random
icon
aliases
draft
```

## checking a note

`python validate_frontmatter.py` re-parses every doc with a strict loader (duplicate keys are errors) and reports: invalid YAML and duplicate keys as errors, unknown keys and links to not-yet-existing notes as notices, bad stages, dates and `icon` values as errors via the build's own warnings. unknown values in date fields are warned about and treated as missing, never fatal.

the annotated skeleton to copy lives at `docs/for-my-reference/note-template.md` (it is deliberately excluded from the build).
