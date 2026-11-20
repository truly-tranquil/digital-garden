---
title: "lists"
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

## definition lists

```markdown
term
:   its definition, with a colon and three spaces
```

tongue
:   diction is done with the tip of the tongue on the teeth

teeth
:   diction is done with the tip of the tongue on the teeth
