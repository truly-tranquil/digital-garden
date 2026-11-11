# Digital Garden

A personal digital garden built with MkDocs, custom theme templates, and build hooks.

## Local development

Use Python 3.12 or newer, then install the pinned dependencies:

```powershell
python -m pip install -r requirements.txt
python -m mkdocs serve
```

## Validation

```powershell
python -m unittest discover -s tests -v
node --test tests/garden-pages.test.js tests/garden-search.test.js
python -m mkdocs build --strict
```

Pull requests run the same tests and build, then check internal links and run a Lighthouse accessibility audit. Changes merged to `main` are uploaded as a GitHub Pages artifact and deployed through GitHub Actions. Set the repository's Pages publishing source to **GitHub Actions** in Settings → Pages.

## Content

Write notes as Markdown files under `docs/`. The [reference page](docs/for-my-reference/reference-page.md) documents note front matter, links, embeds, formatting, and garden-specific features. The note template is kept out of the published site.

When a published note moves or is renamed, add its old path to the note's `aliases` front matter; the build hook creates redirect pages for those aliases.
