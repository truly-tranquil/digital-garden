"""Note discovery: parse front matter, build the note registry and link graph."""

import functools
import os
import posixpath
from datetime import datetime
from typing import Any
from urllib.parse import unquote

import yaml

from garden.dates import git_dates_for_files, validated_date
from garden.icons import ICON_NAMES
from garden.garden_state import (
    backlinks,
    lookup,
    media_lookup,
    notes,
    outgoing,
    referenced_media,
    warn,
    warnings,
)
from garden.links import link_context
from garden.parsing import (
    FRONT,
    MDLINK,
    WIKILINK,
    excerpt,
    flatten,
    heading_map,
    outside_code,
    parse_wikilink,
    slugify,
    title_from_body,
)

STAGE_BY_FOLDER = {'seedlings': 'seedling', 'buds': 'bud', 'evergreens': 'evergreen'}
STAGE_INDEX = {folder + '/index.md': stage for folder, stage in STAGE_BY_FOLDER.items()}
TAG_PAGE = 'by-tag/index.md'

def is_listed(note):
    """True for notes that appear in indexes, the feed and the graph."""
    return (
        not note["is_index"]
        and bool(note.get("stage"))
        and not note.get("unlisted", False)
        and not note.get("draft", False)
        and not note.get("archived", False)
    )


def is_public(note):
    return not note.get('unlisted', False) and not note.get('draft', False)


def collect_links(text, wikilinks, mdlinks):
    """Collect wikilink and markdown-link targets from one text segment."""
    wikilinks.extend(
        match.group(1)
        for match in WIKILINK.finditer(text)
        if match.start() == 0 or text[match.start() - 1] != '!'
    )
    mdlinks.extend(MDLINK.findall(text))
    return text


def populate_garden(files, config):
    """Populate the registries in :mod:`garden_state` from the parsed files."""
    notes.clear()
    backlinks.clear()
    outgoing.clear()
    lookup.clear()
    media_lookup.clear()
    referenced_media.clear()
    warnings.clear()
    git_dates = git_dates_for_files(config, files)
    tag_registry: dict[str, dict[str, str]] = {}
    tag_slug_registry: dict[str, str] = {}

    for f in files.documentation_pages():
        with open(f.abs_src_path, encoding='utf-8') as fh:
            text = fh.read()
        meta: dict[str, Any] = {}
        body = text
        m = FRONT.match(text)
        if m:
            try:
                meta = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError as exc:
                warn('%s has invalid front matter: %s' % (f.src_uri, exc))
                meta = {}
            body = text[m.end() :]
        if not isinstance(meta, dict):
            warn('%s front matter must be a mapping' % f.src_uri)
            meta = {}

        stem = posixpath.splitext(posixpath.basename(f.src_uri))[0]
        folder = posixpath.dirname(f.src_uri)
        title = meta.get('title') or title_from_body(body)
        if not title:
            title = (posixpath.basename(folder) or 'home') if stem == 'index' else stem

        section = f.src_uri.split('/')[0] if '/' in f.src_uri else 'home'
        planted_git, tended_git = git_dates.get(f.src_uri, (None, None))
        tended = (
            validated_date(meta.get('tended'), 'tended', f.src_uri)
            or tended_git
            or datetime.fromtimestamp(os.path.getmtime(f.abs_src_path)).date()
        )
        planted = validated_date(meta.get('planted'), 'planted', f.src_uri) or planted_git
        tags = meta.get('tags') or []
        if isinstance(tags, str):
            tags = [tags]
        elif not isinstance(tags, list):
            warn('%s tags must be a string or list' % f.src_uri)
            tags = []
        tag_entries, seen_tag_keys = [], set()
        for tag in tags:
            clean_tag = str(tag).strip()
            if not clean_tag:
                continue
            key = clean_tag.casefold()
            if key in seen_tag_keys:
                continue
            slug = slugify(clean_tag)
            if not slug:
                warn('%s tag %r has no usable slug' % (f.src_uri, clean_tag))
                continue
            entry = tag_registry.get(key)
            if entry is None:
                unique = slug
                suffix = 2
                while unique in tag_slug_registry:
                    unique = '%s-%d' % (slug, suffix)
                    suffix += 1
                entry = {'name': clean_tag, 'slug': unique}
                tag_registry[key] = entry
                tag_slug_registry[unique] = key
            seen_tag_keys.add(key)
            tag_entries.append(entry)
        tags = [entry['name'] for entry in tag_entries]
        aliases = meta.get('aliases') or []
        if isinstance(aliases, str):
            aliases = [aliases]
        elif not isinstance(aliases, list):
            warn('%s aliases must be a string or list' % f.src_uri)
            aliases = []
        stage = meta.get('stage') or STAGE_BY_FOLDER.get(section)
        if meta.get('stage') and (
            not isinstance(meta['stage'], str)
            or meta['stage'] not in {'seedling', 'bud', 'evergreen'}
        ):
            warn('%s has invalid stage: %r' % (f.src_uri, meta['stage']))
            stage = STAGE_BY_FOLDER.get(section)

        icon = meta.get('icon')
        if icon is not None:
            if not (isinstance(icon, str) and icon.strip()):
                warn('%s icon must be a non-empty string' % f.src_uri)
                icon = None
            else:
                icon = icon.strip()
                if icon not in ICON_NAMES:
                    warn(
                        '%s icon %r is not one of: %s'
                        % (f.src_uri, icon, ', '.join(sorted(ICON_NAMES)))
                    )
                    icon = None

        notes[f.src_uri] = {
            'title': str(title),
            'title_from_frontmatter': bool(meta.get('title')),
            'url': f.url,
            'section': section,
            'stage': stage,
            'tags': tags,
            'tag_entries': tag_entries,
            'planted': planted,
            'tended': tended,
            'excerpt': excerpt(body),
            'is_index': stem == 'index',
            'unlisted': meta.get('unlisted') is True,
            'draft': meta.get('draft') is True,
            'archived': meta.get('archived') is True or section == 'archive',
            'random': meta.get('random') is not False,
            'icon': icon,
            'aliases': [str(alias) for alias in aliases],
            '_body': body,
            '_stem': stem,
            '_headings': heading_map(body),
            '_manual': list(flatten(meta.get('links_to') or meta.get('links to') or [])),
        }

    for field in ('_stem', 'title'):
        values: dict[str, list[str]] = {}
        for src, note in notes.items():
            if note['is_index']:
                continue
            value = note[field] if field == '_stem' else note['title']
            values.setdefault(str(value).casefold(), []).append(src)
        for value, paths in values.items():
            if len(paths) > 1:
                warn('duplicate %s %r: %s' % (field.lstrip('_'), value, ', '.join(paths)))

    for f in files:
        if not f.is_documentation_page():
            media_lookup.setdefault(posixpath.basename(f.src_uri).lower(), f.src_uri)
            media_lookup.setdefault(f.src_uri.lower(), f.src_uri)

    for src, n in notes.items():
        for key in (n['title'], n['_stem'], posixpath.splitext(src)[0]):
            lookup.setdefault(key.lower(), src)
            lookup.setdefault(slugify(key).lower(), src)

    for src, n in notes.items():
        targets = set()
        wikilinks: list[str] = []
        mdlinks: list[str] = []
        outside_code(
            n['_body'],
            functools.partial(collect_links, wikilinks=wikilinks, mdlinks=mdlinks),
        )
        if n['is_index']:
            outgoing[src] = []
            continue
        for raw in wikilinks:
            name, _, _ = parse_wikilink(raw)
            t = lookup.get(name.lower()) or lookup.get(slugify(name).lower())
            if t:
                targets.add(t)
        for raw in mdlinks:
            t = posixpath.normpath(posixpath.join(posixpath.dirname(src), unquote(raw)))
            if t in notes:
                targets.add(t)
            else:
                warn('%s links to missing Markdown file %r' % (src, raw))
        for raw in n['_manual']:
            t = lookup.get(raw.lower()) or lookup.get(slugify(raw).lower())
            if t:
                targets.add(t)
            else:
                warn('%s links to missing note %r in links_to' % (src, raw))
        for raw in wikilinks:
            name, _, _ = parse_wikilink(raw)
            if name and name.lower() not in lookup and slugify(name).lower() not in lookup:
                warn('%s links to missing note %r' % (src, name))
        targets = {
            target
            for target in targets
            if target != src and not notes[target]['is_index'] and is_public(notes[target])
        }
        outgoing[src] = sorted(
            (
                {'title': notes[t]['title'], 'url': notes[t]['url'], 'icon': notes[t]['icon']}
                for t in targets
            ),
            key=lambda x: x['title'].lower(),
        )
        for t in targets:
            if not n.get('unlisted', False) and not n.get('draft', False):
                backlinks.setdefault(t, []).append(
                    {
                        'title': n['title'],
                        'url': n['url'],
                        'icon': n['icon'],
                        'stage': n.get('stage') or '',
                        'src': src,
                        'context': link_context(n['_body'], notes[t], t),
                    }
                )

    for lst in backlinks.values():
        lst.sort(key=lambda b: b['title'].lower())
    return files
