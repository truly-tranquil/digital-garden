"""Wikilink resolution and note embedding.

Everything here reads the build registries from :mod:`garden_state`; nothing
mutates them.
"""

import html
import posixpath
import re
from urllib.parse import quote, unquote

from garden.garden_state import lookup, media_lookup, notes, referenced_media
from garden.icons import icon_svg
from garden.parsing import (
    EMBED,
    FENCE,
    HEADING,
    LINK,
    MD_INLINE_LINK,
    closes_fence,
    escape_brackets,
    excerpt,
    heading_slug,
    heading_text,
    outside_code,
    parse_wikilink,
    quote_path,
    section,
    slugify,
    without_first_heading,
)

MAX_EMBED_DEPTH = 2

_A_HREF = re.compile(r'<a\b[^>]*?\bhref="([^"]*)"[^>]*>')
_EXTERNAL_URL = re.compile(r'^(?:[a-z][a-z0-9+.-]*:|//)', re.I)
INLINE_ICON = re.compile(r'(?<![\w:/.-]):([a-z0-9][a-z0-9-]*):(?![\w:/-])')


def note_icon_svg(name):
    """Inline ``<svg>`` for a note's registered icon name ('' when unset)."""
    if not name:
        return ''
    return icon_svg(name, 'note-icon')


def inline_icons(text):
    """Turn ``:name:`` into the matching sprite glyph, leaving unknowns alone."""
    return INLINE_ICON.sub(lambda match: icon_svg(match.group(1)) or match.group(0), text)


def link_context(body, target, target_src):
    """First line of ``body`` that mentions ``target``, trimmed to an excerpt."""
    phrases = {
        target['title'].casefold(),
        target['_stem'].casefold(),
        target_src.casefold(),
        posixpath.basename(target_src).casefold(),
    }
    context = []

    def find(text):
        for line in text.splitlines():
            lowered = line.casefold()
            if any(phrase and phrase in lowered for phrase in phrases):
                excerpt_text = excerpt(line)
                if excerpt_text:
                    context.append(excerpt_text)
                    return text
        return text

    outside_code(body, find)
    return context[0] if context else ''


def rewrite_embed_content(body, target, src, prefix):
    """Re-anchor an embedded note so its headings and links stay unique."""
    seen: dict[str, int] = {}
    anchors: dict[str, str] = {}
    lines: list[str] = []
    fence = None
    for line in body.splitlines():
        match = FENCE.match(line)
        if match:
            if fence is None:
                fence = match.group(1)
            elif closes_fence(line, fence):
                fence = None
            lines.append(line)
            continue
        if fence is not None:
            lines.append(line)
            continue
        heading = HEADING.match(line)
        if not heading:
            lines.append(line)
            continue
        title = re.sub(r'\s+\{[^}]*\}\s*$', '', heading.group(2)).strip()
        attrs = heading.group(3) or ''
        custom = re.search(r'#([\w-]+)', attrs)
        base = custom.group(1) if custom else heading_slug(heading_text(title))
        occurrence = seen.get(base, 0)
        seen[base] = occurrence + 1
        anchor = '%s%s%s' % (prefix, base, '-%s' % occurrence if occurrence else '')
        anchors.setdefault(base.lower(), anchor)
        if custom:
            anchors.setdefault(custom.group(1).lower(), anchor)
        level = min(len(heading.group(1)) + 1, 6)
        lines.append('%s %s { #%s }' % ('#' * level, title, anchor))
    body = '\n'.join(lines)

    def rewrite_destination(destination):
        wrapped = destination.startswith('<') and destination.endswith('>')
        raw = destination[1:-1] if wrapped else destination
        if raw.startswith('#'):
            fragment = unquote(raw[1:]).lower()
            return '#' + quote(anchors.get(fragment, raw[1:]), safe='-._~')
        if re.match(r'^(?:[a-z][a-z0-9+.-]*:|//|/)', raw, re.I):
            return destination
        suffix_at = min(
            (index for index in (raw.find('?'), raw.find('#')) if index >= 0), default=len(raw)
        )
        path, suffix = raw[:suffix_at], raw[suffix_at:]
        if not path:
            return destination
        target_path = posixpath.normpath(posixpath.join(posixpath.dirname(target), unquote(path)))
        relative = posixpath.relpath(target_path, posixpath.dirname(src) or '.')
        result = quote_path(relative) + suffix
        return '<%s>' % result if wrapped else result

    def rewrite_markdown_link(match):
        return (
            match.group('open')
            + rewrite_destination(match.group('dest'))
            + (match.group('title') or '')
            + match.group('close')
        )

    body = MD_INLINE_LINK.sub(rewrite_markdown_link, body)

    def rewrite_html_url(match):
        return match.group(1) + rewrite_destination(match.group(2)) + match.group(3)

    body = re.sub(r'(\b(?:href|src)=["\'])([^"\']+)(["\'])', rewrite_html_url, body, flags=re.I)
    body = re.sub(
        r'\[\^([^\]]+)\]',
        lambda match: '[^%s%s]' % (prefix, slugify(match.group(1))),
        body,
    )
    return body


def expand(text, src, stack, depth):
    """Inline ``![[note]]`` embeds, up to MAX_EMBED_DEPTH levels deep."""
    if depth >= MAX_EMBED_DEPTH:
        return text

    embed_count = 0

    def repl(m):
        nonlocal embed_count
        embed_count += 1
        name, section_name = m.group(1).strip(), m.group(2)
        target = lookup.get(name.lower()) or lookup.get(slugify(name).lower())
        if not target or notes[target].get('draft', False):
            return m.group(0)
        if target in stack and not section_name:
            return m.group(0)
        note = notes[target]
        body = note['_body']
        label = note['title']
        anchor = None
        if section_name:
            body, anchor = section(body, section_name, note.get('_headings'))
            if body is None:
                return m.group(0)
            label += ' › ' + section_name.strip()
        else:
            body = without_first_heading(
                body, note['title'] if note.get('title_from_frontmatter') else None
            )
        body = outside_code(body, lambda t: expand(t, target, stack + (target,), depth + 1)).strip()
        body = outside_code(body, lambda t: links(t, target))
        prefix = 'embed-%s-%s-%s-' % (
            slugify(posixpath.splitext(src)[0]),
            slugify(posixpath.splitext(target)[0]),
            embed_count,
        )
        body = rewrite_embed_content(body, target, src, prefix)
        rel = posixpath.relpath(target, posixpath.dirname(src) or '.')
        if anchor:
            rel = quote_path(rel) + '#' + quote(anchor, safe='-._~')
        else:
            rel = quote_path(rel)
        return '\n\n<div class="embed" markdown="1">\n\n**[%s](%s)**\n\n%s\n\n</div>\n\n' % (
            escape_brackets(label),
            rel,
            body,
        )

    return EMBED.sub(repl, text)


def inject_note_icons(html_text, src):
    """Prepend each target note's icon to ``<a>`` links pointing at notes.

    Runs on the final body HTML. Links to other pages (non-notes), external
    URLs, fragments and links from a note to itself are left alone.
    """
    base = posixpath.dirname(src)

    def repl(m):
        href = m.group(1)
        path = href.split('#', 1)[0]
        if not path or _EXTERNAL_URL.match(path):
            return m.group(0)
        if html_text[m.end() : m.end() + 16].lstrip().startswith('<svg'):
            return m.group(0)  # already carries its icon (stage cards, tag lists)
        if path.startswith('/'):
            cand = unquote(path[1:])
        else:
            cand = unquote(posixpath.normpath(posixpath.join(base, path)))
        cand = posixpath.normpath(cand)
        if cand.endswith('.html'):
            cand = cand[:-5] + '.md'
        note = notes.get(cand)
        if not note or cand == src:
            return m.group(0)
        name = note.get('icon')
        if not name:
            return m.group(0)
        return m.group(0) + note_icon_svg(name)

    return _A_HREF.sub(repl, html_text)


def links(text, src):
    """Turn [[wikilinks]] and ![[images]] into normal markdown links."""
    base = posixpath.dirname(src) or '.'

    def repl(m):
        bang = m.group(1)
        name, heading, alias = parse_wikilink(m.group(2))
        key = name.lower()
        if bang:
            media = media_lookup.get(key) or media_lookup.get(posixpath.basename(key))
            if media:
                referenced_media.add(media)
                rel = quote_path(posixpath.relpath(media, base))
                size, alt = '', name
                dimensions = re.fullmatch(r'(\d+)(?:x(\d+))?', alias.strip()) if alias else None
                if dimensions:
                    width, height = dimensions.groups()
                    size = ' { width="%s"%s }' % (width, ' height="%s"' % height if height else '')
                elif alias:
                    alt = alias
                return '![%s](%s)%s' % (alt, rel, size)
        target = src if not name else (lookup.get(key) or lookup.get(slugify(key)))
        if not target or notes[target].get('draft', False):
            return '<span class="broken-link">%s</span>' % html.escape(alias or name)
        rel = quote_path(posixpath.relpath(target, base))
        if heading:
            plain = heading_text(heading)
            target_headings = notes.get(target, {}).get('_headings', {})
            anchor = (
                target_headings.get(plain.strip().lower())
                or target_headings.get(heading.strip().lower())
                or heading_slug(plain)
            )
            rel += '#' + quote(anchor, safe='-._~')
        label = alias or (name + (' › ' + heading.strip() if heading else ''))
        return '[%s](%s)' % (escape_brackets(label), rel)

    return LINK.sub(repl, text)
