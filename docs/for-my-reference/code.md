---
title: "code"
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
python garden_build.py
python -m http.server 8000 --directory dist
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
