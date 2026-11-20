# digital garden

A small digital garden built with a custom Python static site generator. Notes are plain markdown in `docs/`, grown in three stages: **seedlings** (rough), **buds** (developing), **evergreens** (sturdy).

## build and preview

```bash
pip install -r requirements-dev.txt   # runtime dependencies plus ruff and mypy
python garden_build.py                # writes the site to dist/
python garden_build.py serve          # build, then preview at http://localhost:8000
python validate_frontmatter.py        # check front matter and links
python check_site.py dist             # check internal links and assets in the built site
ruff check .                          # lint
ruff format --check .                 # formatting check
mypy garden garden_build.py validate_frontmatter.py check_site.py  # type check
```

Set `GARDEN_BASE_PATH=/digital-garden` when building for GitHub Pages so root-relative links get the repo prefix. Pass the same value to the link checker: `python check_site.py dist --base-path /digital-garden`.

## layout

| path | what it is |
| --- | --- |
| `docs/` | notes. the folder (`seedlings/`, `buds/`, `evergreens/`) sets the stage; `drafts/` is excluded from the build entirely |
| `docs/assets/` | images, fonts, cursor |
| `docs/for-my-reference/` | reference hub (unlisted) and the note template (unlisted) |
| `garden/` | the build system as a package: `garden_state` (shared registries), `parsing`, `links`, `dates`, `notes`, `output`, `page`, `utils/` (`garden.py` loader, nav, graph, renderer, assets) |
| `garden_build.py` | entry point: builds the site into `dist/`, renders notes, the graph, 404, feeds, sitemap, robots.txt, alias redirects |
| `check_site.py` | internal link and asset checker for the built site |
| `validate_frontmatter.py` | front-matter validator |
| `my-garden-theme/` | templates, `tokens.css`, `layout.css`, `content.css`, `components.css`, `wilderness.css`, `print.css`, `garden.js`, `graph.js`, `js/*.js`, `graph/*.js`, `feed.xsl` (feed stylesheet) |
| `garden.yml` | site title, url, source and output folders |
| `pyproject.toml` | ruff lint and format settings |
| `requirements*.txt` | pinned runtime and dev dependencies |

## front matter

`title`, `stage`, `tags`, `planted`, `tended`, `links_to` (or `links to`), `unlisted`, `archived`, `random`, `icon`, `aliases`, `draft`. Dates default to git history: planted from the commit that added the file, tended from the most recent commit (or today when the file has uncommitted changes). `draft: true` keeps a note off the site; anything in `docs/drafts/` is skipped outright. `unlisted: true` keeps it out of the index, graph, feed and random picks. `archived: true` — or simply living in `docs/archive/` — moves it to the archive group in the index. `random: false` keeps the note out of the random pick and note of the day.

## generated pages

The build renders each listed note into `dist/`, plus:

- `/graph.html` — garden graph: canvas visualization of notes and links, with a plain-text fallback list
- `/404.html` — not-found page with a search box and stage suggestions
- `/feed.xml` — Atom 1.0 feed of listed notes
- `/feed.json` — JSON Feed of listed notes
- `/sitemap.xml` — sitemap of listed pages
- `/robots.txt` — robots exclusion file

## navigation

The header has a "nav." button (opens the site compass dialog), a random note button, a theme look switcher, a light/dark toggle, and a search form. The compass dialog has wells for home, manifesto, about, seedlings, buds, and evergreens. The footer links to about. The default look is **dusk** in light mode, which the look switcher names **dawn**; the theme and dark-mode choices are remembered in localStorage.

## note pages

Notes are rendered at their source path, e.g. `docs/seedlings/alpha.md` → `dist/seedlings/alpha.html`. Each note page shows its stage badge, tags, dates, reading time, and body content.

## deploy

`.github/workflows/deploy.yml` builds on every push to `main` and publishes to GitHub Pages. It checks out full git history (`fetch-depth: 0`) so planted and tended dates are right.
