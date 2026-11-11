# Digital Garden

A personal digital garden built with Zensical and a custom garden preprocessing step.

## Local development

Use Python 3.12 or newer, then install the pinned dependencies:

```powershell
python -m pip install -r requirements.txt
python garden_build.py serve
```

The preview watches the source files and refreshes the generated Zensical input when they change.
If port 8000 is in use, choose another preview address with
`python garden_build.py serve --dev-addr 127.0.0.1:8001`. For a direct MkDocs preview,
`python -m mkdocs serve` is also supported.
The unlisted reference sheet is available only in the local Zensical preview at
`http://127.0.0.1:8000/digital-garden/for-my-reference/reference-page/`. Zensical excludes it from production builds;
do not deploy a raw MkDocs build if you want to keep it private, because MkDocs still builds unlisted files.
Static hosting does not provide access control for files that are included in a deployed build.

## Validation

```powershell
python -m unittest discover -s tests -v
node --test tests/garden-pages.test.js tests/garden-search.test.js
python garden_build.py build
```

Zensical does not support MkDocs hooks, so `garden_build.py` expands garden-specific links, builds navigation and metadata, and writes the generated feed, graph, redirects, and JSON indexes around the Zensical build. Keep `mkdocs.yml` as the shared configuration; use the wrapper commands above when building with Zensical. MkDocs remains available for local preview and hook-based builds.

Pull requests run the same tests and build, then check internal links and run a Lighthouse accessibility audit. Changes merged to `main` are uploaded as a GitHub Pages artifact and deployed through GitHub Actions. Set the repository's Pages publishing source to **GitHub Actions** in Settings → Pages.

## Content

Write notes as Markdown files under `docs/`. The reference page documents note front matter, links, embeds, formatting, and garden-specific features; it is unlisted and excluded from production Zensical builds. The note template is kept out of the published site.

When a published note moves or is renamed, add its old path to the note's `aliases` front matter; the build hook creates redirect pages for those aliases.
