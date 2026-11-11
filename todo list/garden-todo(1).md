# garden improvement list, ordered by file

Items marked **[you]** are your requests. Everything else came from my review. Within each file, your requests come first. Finished items are checked or removed as we go (done so far: the quill cursor, all of main.css, all of main.html except the privacy item, and unlisted handling).

Files in order: `main.css`, `main.html`, `hooks.py`, `garden-search.js`, `garden-mermaid.js`, `home.html`, `search.html`, `404.html`, `reference-page.md`, `index.md`, `mkdocs.yml`, `requirements.txt`, `deploy.yml`, new files.

---

## 1. main.css

### Your requests

- [x] **[you] Style and random buttons: new location.** Location will be the left header. the site logo that links to the home page will go on the header right, to the right of the search bar. See the options under main.html. Once chosen, restyle here:
  - Remove them from `.header-right`, and keep `.header-right` as search only.
  - Add styles for the new home (for example a `.sidebar-tools` row at the bottom of the left sidebar).
  - The shared button rule (`#sidebar-toggle, #mode-toggle, #random-note, ...`) still applies, so a move shouldn't need new button styling.
- [x] User entry: make the webpage full width by default and only have this change when either the index or table of contents is open.
- [x] User entry: make the red slightly more vibrant and the orange slightly less so in the darkmode variant.

---

## 2. main.html

- [x] **[you] Move the style (dark mode) and random buttons.** Keep the `data-random` attribute and the `#mode-toggle` id so the existing scripts keep working, and keep both as real `<button>`s with the same accessible labels.
- [ ] Privacy and supply chain. Both parts need a decision from you:
  - Google Fonts: self-host Newsreader with `font-display: swap`. This needs the font files added to the repo first (see new files), and then the `<link>` tags here come out and an `@font-face` goes in main.css. User's note: I would like to add the files to the repo, just tell me what i need to do on my end and i will.
  - The Google favicon service tells Google which sites you link to. Either drop the favicons on external links, or keep them and accept that. Dropping means removing the last script block here and the `.link-favicon` rule, and updating the reference page's sentence about it. User's note: keep the favicons, i like them.

---

## 3. hooks.py

- [x] **Unlisted flag.** Add `unlisted: true` front matter. Honor it in `notes.json`, the stage and tag indexes, `_related`, and the home widgets. The reference page is `stage: evergreen`, so today it appears everywhere.
- [x] Copy folder-derived stage into `page.meta` (`setdefault('stage', ...)`). Today a note without `stage:` has no badge and `og:type` stays `website`.
- [x] Exclude non-note pages (`manifesto`, `about`) from the "notes in all" total.
- [x] Fence closing: a line like ` ```python ` shouldn't close a ` ``` ` fence. Closers must be bare. Fix in `_outside_code` and `_section`.
- [x] `_outside_code` should also skip `<pre>`, `<code>`, `<!-- -->` and `%% %%`. Then the `&#91;` entity workaround in the reference page can go.
- [x] Run `WIKILINK` and `MDLINK` extraction through `_outside_code` so links inside code don't count as outgoing.
- [x] Title detection: skip fences, strip markdown and attr_list, support `title:` properly. The home page title is currently a raw string with two images.
- [x] `MDLINK`: `unquote()` paths. `_links`: use `urllib.parse.quote`, handle parentheses in filenames.
- [x] Slugs: `heading_slug` can differ from toc's slugify (non-ASCII, duplicate `_1` suffix). Reuse `markdown.extensions.toc.slugify`.
- [x] Respect custom ids (`{ #my-custom-id }`) in `[[note#Heading]]` links by storing a heading to id map in `on_files`.
- [x] Support `[[#Heading]]` same-page links.
- [x] Support `[[a\|b]]` (escaped pipe) in table cells.
- [x] Support `![[img.png|100x200]]`.
- [x] Log warnings (`mkdocs.utils.log`) for broken wikilinks, duplicate stems or titles, and invalid `stage`, `tags` or date values.
- [x] Add a slug fallback key so `[[my note]]` finds `my-note.md`.
- [x] Normalize tag case in `on_files`. `Idea` and `idea` currently make two headings with the same id.
- [x] `_excerpt`:
  - Prefer `description:` front matter.
  - Stop stripping `_ ~ ^ # = >` blindly.
  - Remove HTML comments and callout markers.
  - Cut at a word boundary.
  - Handle 4-backtick fences.
- [x] `_related` falls back to recently tended notes when no tags match but still labels them "related". Show fewer, or relabel.
- [x] Exclude index pages as outgoing and backlink targets (the reference page's sample badge links create them).
- [x] Embeds:
  - Rewrite relative links, images and footnotes against the target note's folder.
  - Demote embedded heading levels so they don't pollute the TOC or duplicate ids.
- [x] `_git_dates` runs three subprocesses per note. Do one `git log --name-only` pass into a dict, and skip git when serving.
- [x] Feed and sitemap: generate an Atom feed from `tended`, plus `robots.txt`. main.html already links the feed once `extra: feed: feed.xml` is set in mkdocs.yml.
- [x] Feature ideas: `draft: true`, `aliases:` redirects, backlink context sentences, per-note git history, a local graph view, a "did you mean" data file for the 404 page.
- [x] Add pytest cases for `_links`, `_expand`, `_section`, `_outside_code`.

---

## 4. garden-search.js

- [x] Pre-normalize the index once after loading. Stop parsing HTML with `innerHTML` and lowercasing on every keystroke.
- [x] Group hits by page and keep the best hit, so one page doesn't fill several dropdown slots.
- [x] Match tags by slug. `#book notes` currently splits into tag `book` plus text `notes`.
- [x] Close the dropdown on `focusout`, and ignore stale async results when the input has changed.
- [x] Show an error, not "nothing found", when the index fetch fails.
- [x] If the new orange or blue changes `--accent` usage in `.search-dd`, re-check contrast of the selected row.

---

## 5. garden-mermaid.js

- [x] **[you] Two-way arrow between seedling and bud.** This isn't a bug in this file. The sample diagram in `reference-page.md` literally contains both `seedling --> bud --> evergreen` and `bud --> seedling`. That second line draws the return arrow. Fix it in the reference page (see section 9).
- [x] **[you] Colors follow the palette changes.** The diagram reads `--accent`, `--surface`, `--text` and `--bg` at draw time, so the new blue and orange don't affect it. If you want node colors from the palette, add per-class styles via `themeVariables`.
- [x] Wait for `document.fonts.ready` before the first draw, so nodes are measured with Newsreader, not the fallback.
- [x] Pin the mermaid version exactly (not `@11`) and add an SRI `integrity` hash, or self-host it.
- [x] Redraw on `prefers-color-scheme` changes too, not only the `data-theme` attribute.

---

## 6. home.html

- [x] **[you] Remove the tags widget.**
  - The `.tag-cloud` CSS is already gone, so remove the markup and script together.
  - Delete the `w-tags` section, the `// tags` block in the script (the `counts`/`slugs` code), and the "no tags yet" message.
  - Tags still appear under note titles and on the by-tag page, so nothing else depends on this widget.
  - Check the `.widgets` grid still looks balanced with one widget fewer, since the stats card is full width and note of the day and recently tended are left.
- [x] **[you] Add a clock widget, clearly labeled.**
  - Either use the viewer's local time or fixed Pacific time. Both are fine. My suggestion is the viewer's local time with the zone name shown, because it needs no assumptions, for example `Intl.DateTimeFormat(undefined, { timeStyle: 'medium', timeZoneName: 'short' })`.
  - For Pacific time instead, pass `timeZone: 'America/Los_Angeles'`, which handles PST/PDT switching automatically. Don't hardcode "PST", since it would be wrong for about eight months of the year.
  - Label with a heading in the widget style, such as "the time" or "garden clock", plus the zone in the text so it is never ambiguous.
  - Update with `setInterval` (every second, or every minute if you hide seconds). Don't put `aria-live` on it, or a screen reader will announce every tick. Pause updates when the tab is hidden if you care.
  - Render a sensible static fallback in the markup so no-JS visitors don't see an empty card.
  - The CSS is done and expects this markup inside the widget: `<div class="clock"><time class="clock-time" id="clock-time"></time><span class="clock-date" id="clock-date"></span><span class="clock-zone" id="clock-zone"></span></div>`.
- [x] Render stats and recent notes in Jinja (pass from `on_page_context`). Keep JS only for note-of-the-day. This removes the layout shift and the no-JS blank.
- [x] Respect `unlisted` and non-note pages when counting and listing.
- [x] Add a short "how to read this garden" legend for seedling, bud and evergreen.
- [x] Handle a failed `notes.json` fetch gracefully.

---

## 7. search.html

- [x] Call `gardenMark` so titles and snippets highlight the search terms. The CSS for it already exists.
- [x] Add an `aria-live` result count and put the query in the page title.
- [x] `noindex` (set in main.html).

---

## 8. 404.html

- [x] "Did you mean…?" suggestions: fuzzy-match the requested path against `notes.json`.
- [x] Verify styles load once `site_url` is real. The page builds all asset URLs from `config.site_url`, so the placeholder breaks it.

---

## 9. reference-page.md

- [x] Document `width: full` in the metadata example and bullet list; use it on the reference page.
- [x] Update metadata guidance for tags and the current homepage widgets.
- [x] Document the header location of the style and random buttons.
- [x] Mermaid sample has no unintended backward arrow.
- [x] Show all eight callout colors and types.
- [x] Add a twelve-tab example to show narrow-width scrolling.
- [x] Keep the orange and blue palette labels; neither color was renamed.
- [x] Add `unlisted: true` once the hook supports it.
- [x] Use the UI's "outgoing links" and "backlinks" terminology.
- [x] Add blank lines before the headings after the last footnote and last tab.
- [x] Document the stage legend, `#tag` search, `/` shortcut, random note, dark mode and TOC drawer.
- [x] Sample badge and tag links create outgoing chips to the index pages. Use plain code samples or exclude them.

---

## 10. index.md

- [x] Both decorative title images use `alt=""`.
- [x] Provide a static favicon fallback when `prefers-reduced-motion: reduce` is enabled.

---

## 11. mkdocs.yml

- [x] Configure `og_image` and `feed` in `extra`.
- [x] Replace the placeholder `site_url` with the repository's GitHub Pages URL.
- [x] Add MkDocs validation for anchors, unrecognized links, and omitted files.
- [x] Exclude draft/template paths and `.obsidian/` metadata from the documentation build.
- [x] Set an accessible TOC permalink title and a clearer permalink glyph.
- [x] Enable the selected Markdown enhancements:
  - `nl2br`
  - `pymdownx.saneheaders`
  - `pymdownx.arithmatex` with KaTeX loaded only on pages containing math
- [ ] Optional Markdown enhancements (declined; leave disabled):
  - `mdx_truly_sane_lists` — a third-party extension with configurable nested-list indentation and more predictable line breaks/paragraphs inside lists; could change existing list rendering.
  - Code block titles — display a filename or label above a fenced code block; requires code-fence metadata plus appropriate formatter/template styling.
  - Line highlights (`pymdownx.highlight` with `pymdownx.superfences`) — mark selected lines in fenced code blocks; code syntax highlighting is already enabled.
- [x] Use the existing tested `aliases` front matter/build-hook support for renamed-note redirects; document it in the README.

---

## 12. requirements.txt

- [x] Add the Pygments dependency used for code highlighting.
- [x] Pin direct dependency versions.
- [x] Pin MkDocs to the verified 1.6.1 release, avoiding an unverified major upgrade.

---

## 13. deploy.yml

- [x] Add workflow concurrency, job timeouts, and a pull-request validation job running `mkdocs build --strict`.
- [x] Deploy through a Pages artifact (`upload-pages-artifact` plus `deploy-pages`) instead of force-pushing `gh-pages`.
- [x] Grant the deploy job the `pages: write` and `id-token: write` permissions and include `.nojekyll`.
- [x] Add Lychee internal-link checks and a Lighthouse accessibility audit to pull requests.
- [x] Add weekly Dependabot updates for Actions and pip.

---

## 14. New files

- [x] Add `.gitignore` and a project README; `robots.txt` is generated by the build hook and `gh-deploy` adds `.nojekyll`.
- [x] Add self-hosted Newsreader fonts and include their OFL license.
- [x] Add a 1200×630 social preview image at `docs/assets/og-image.png`.
- [x] Add `tests/test_hooks.py`.
