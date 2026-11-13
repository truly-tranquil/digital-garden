# Contributing to the Digital Garden

Thank you for wanting to help tend this garden. Contributions here are welcome,
but the garden is a personal space for honest reflection, and every note should
stay true to its purpose.

## What belongs in this garden

- **Seedlings** – new or developing thoughts worth testing.
- **Buds** – thoughts that have taken shape and are being tended.
- **Evergreens** – stable, reviewed thoughts that have stood the test of time.

If you are unsure whether something belongs, read the
[manifesto](manifesto.md) and the [About page](about.md).

## Adding a note

1. Create a file under `docs/seedlings/`, `docs/buds/`, or `docs/evergreens/`.
2. Use the [`note-template.md`](for-my-reference/note-template.md) as a starting point.
3. Fill in front matter as needed (title, description, stage, tags, planted,
   tended, excerpt, unlisted, draft, aliases).
4. Add the note content. Links should use wikilinks (`[[Note title]]`), which the
   build converts to normal Markdown links.
5. Keep drafts out of the public site by setting `draft: true`.

### Renaming a note

If you rename a published note, add its previous path to the note's `aliases`
front matter so the build creates a redirect.

## Updating the garden structure

- **Stage index pages** (`seedlings/index.md`, `buds/index.md`,
  `evergreens/index.md`) are auto-populated by the build. Do not need to edit
  them manually.
- **Navigation** is defined in `mkdocs.yml`. The build prepares the nav from the
  stage folders, but you can override it there.
- **The reference page** (`docs/for-my-reference/reference-page.md`) documents
  note front matter, links, embeds, and formatting.

## Governance and review

- The `.github/CODEOWNERS` file lists the owners responsible for reviewing
  changes to different areas.
- Pull requests that change garden content, the build pipeline, or the theme
  should be reviewed by at least one owner.
- Keep changes small and focused. Large structural changes should be discussed
  in an issue first.

## Questions

If you are unsure whether something belongs, or how to make a change, open an
issue or start a discussion on the repository.
