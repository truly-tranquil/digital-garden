# Digital Garden

A personal garden of notes that grow through reading, learning, making, and revision.

- **Visit the garden:** [truly-tranquil.github.io/digital-garden](https://truly-tranquil.github.io/digital-garden/)
- **Read the [garden manifesto](https://truly-tranquil.github.io/digital-garden/manifesto/)** for the purpose and principles behind the notes.
- **Browse the [manifesto source](docs/manifesto.md)** or return to this [project README](https://github.com/truly-tranquil/digital-garden#digital-garden).

## How it works

Notes and site content live in `docs/`. The public site is built with Zensical by
`garden_build.py`, which prepares garden links, metadata, navigation, and generated
indexes before building. GitHub Actions runs the tests and build, then deploys successful
changes from `main` to GitHub Pages.

## Run locally

Use Python 3.12 or newer and Node.js for the JavaScript tests. From the repository root,
install the pinned Python dependencies and start the garden preview:

```powershell
python -m pip install -r requirements.txt
python garden_build.py serve
```

Open `http://127.0.0.1:8000/digital-garden/`. If that port is in use, choose another:

```powershell
python garden_build.py serve --dev-addr 127.0.0.1:8001
```

The Zensical wrapper is the production build path. Unlisted content is not access-controlled;
never put private or sensitive material in this repository.

## Validate changes

```powershell
python -m unittest discover -s tests -v
node --test tests/garden-pages.test.js tests/garden-search.test.js
python garden_build.py build
```

Pull requests also run internal-link and Lighthouse accessibility checks. To publish,
set the repository's Pages source to **GitHub Actions** in Settings → Pages; pushes to
`main` trigger the deployment workflow.

## Tend the garden

Add Markdown notes under `docs/seedlings/`, `docs/buds/`, or `docs/evergreens/` as they
develop. Use `draft: true` in front matter to keep an unfinished note out of the public
site. The unlisted reference page at `docs/for-my-reference/reference-page.md` documents
note front matter, links, embeds, and formatting.

When renaming a published note, add its previous path to the note's `aliases` front
matter so the build can create a redirect.

For questions about what belongs here or how the garden is meant to grow, start with the
[manifesto](https://truly-tranquil.github.io/digital-garden/manifesto/).

## Governance

This repository is a personal garden, but it has light governance to keep the build
and content consistent.

- **Code of governance**: read [`CODEOWNERS`](.github/CODEOWNERS) and
  [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to contribute and who reviews changes.
- **Issue templates**: use the templates in `.github/ISSUE_TEMPLATE/` for bug reports,
  feature requests, and documentation improvements.
- **Content policy**: this is not a verified source of factual information. We welcome
  respectful disagreement and discussion, but the garden is not a space for hatred.

---

## License

This project is private and not published under an open-source license. Use of this
repository is governed by the terms set by the maintainers.

