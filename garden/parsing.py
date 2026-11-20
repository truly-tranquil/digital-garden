"""Markdown scanning helpers: front matter, fences, headings, wikilinks and excerpts.

These functions are deliberately format-level; they never look at build state.
"""

import html
import re
from urllib.parse import quote, unquote

from markdown.extensions.toc import slugify as toc_slugify

FRONT = re.compile(r'\A---\s*\n(.*?)\n---\s*\n', re.S)
WIKILINK = re.compile(r'\[\[(.*?)\]\]')
EMBED = re.compile(r'!\[\[([^\]|#]+)(?:#([^\]|]*))?(?:\|[^\]]*)?\]\]')
LINK = re.compile(r'(!?)\[\[(.*?)\]\]')
MDLINK = re.compile(r'(?<!!)\[[^\]]*\]\(((?:[^()\s#]|\([^()\s#]*\))*?\.md)(?:#[^)]*)?\)')
MD_INLINE_LINK = re.compile(
    r'(?P<open>!?\[[^\]]*\]\()(?P<dest><[^>]+>|(?:[^()\s]|\([^()\s]*\))*)'
    r'(?P<title>\s+["\'][^)]*["\'])?(?P<close>\))'
)
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*(\{[^}]*\})?\s*$')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')
FENCE_CLOSE = re.compile(r'^\s*(`{3,}|~{3,})\s*$')
OUTSIDE_CODE_TOKEN = re.compile(r'`[^`\n]*`|<!--|-->|</?(?:pre|code)\b[^>]*>|%%', re.I)
HTML_CODE_TAG = re.compile(r'<(/?)(pre|code)\b[^>]*>', re.I)
BLOCKQUOTE_PREFIX = re.compile(r'^ {0,3}(?:>[ \t]?)+')
OUTSIDE_CODE_BLOCK = re.compile(r'<!--|-->|</?(?:pre|code)\b[^>]*>|%%', re.I)

# Inline syntax that changes what the toc extension sees when it slugifies a
# heading. Keep these in rendered order: links/images first, then HTML, then
# emphasis and escapes.
IMAGE_REF = re.compile(r'!\[[^\]]*\]\[[^\]]*\]')
IMAGE = re.compile(r'!\[[^\]]*\]\([^)]*\)')
LINK_TEXT = re.compile(r'(?<!!)\[([^\]]*)\]\([^)]*\)')
REF_LINK = re.compile(r'\[([^\]]+)\]\[[^\]]*\]')
AUTOLINK = re.compile(r'<((?:[a-z][a-z0-9+.-]*:[^ <>]+)|(?:[^ <>@]+@[^ <>]+))>', re.I)
HTML_TAG = re.compile(r'</?[a-zA-Z][^>]*>')
FOOTNOTE_REF = re.compile(r'\[\^[^\]]+\]')
INLINE_CODE = re.compile(r'`([^`\n]*)`')
UNDERSCORE_STRONG = re.compile(r'(?<![\\\w])__(?=\S)(.+?)(?<=\S)(?<!\\)__(?!\w)')
UNDERSCORE_EM = re.compile(r'(?<![\\\w])_(?=\S)(.+?)(?<=\S)(?<!\\)_(?!\w)')
ESCAPE = re.compile(r'\\([\\`*_{}\[\]()#+\-.!|>~=^])')


def slugify(text):
    return re.sub(r'[^\w]+', '-', str(text).lower()).strip('-')


def heading_slug(text):
    return toc_slugify(str(text), '-')


def unique_anchor(base, used):
    """Pick the anchor id python-markdown's toc extension would pick.

    Empty slugs (CJK headings, for example) become ``_1``, ``_2`` and so on,
    matching ``toc.unique`` instead of collapsing to an empty fragment.
    """
    while not base or base in used:
        match = re.fullmatch(r'(.*)_(\d+)', base)
        if match:
            base = '%s_%d' % (match.group(1), int(match.group(2)) + 1)
        else:
            base = '%s_1' % base
    return base


def _unescape_wikilink(value):
    return re.sub(r'\\([\\|#])', r'\1', value).strip()


def parse_wikilink(value):
    """Split a wikilink body into (target, heading, alias), honouring escapes."""

    def split_unescaped(text, delimiter):
        escaped = False
        for index, character in enumerate(text):
            if character == delimiter and not escaped:
                return text[:index], text[index + 1 :]
            if character == '\\' and not escaped:
                escaped = True
            else:
                escaped = False
        return text, None

    target, alias = split_unescaped(value, '|')
    name, heading = split_unescaped(target, '#')
    return (
        _unescape_wikilink(name),
        _unescape_wikilink(heading) if heading is not None else None,
        _unescape_wikilink(alias) if alias is not None else None,
    )


def heading_text(text):
    """Reduce a heading to the plain text python-markdown renders for the toc.

    The toc extension slugifies the rendered heading, so inline Markdown has to
    be reduced to its visible text before the slug is computed. Without this,
    ``## [text](url)`` gets the anchor ``texthttpsexamplecom`` instead of
    ``text`` and deep links to that heading break.
    """

    def wikilink(match):
        target, heading, alias = parse_wikilink(match.group(2))
        if alias:
            return alias
        if match.group(1):
            return ''
        return target + (' › ' + heading if heading else '')

    text = FOOTNOTE_REF.sub('', text)
    text = LINK.sub(wikilink, text)
    text = IMAGE_REF.sub('', text)
    text = IMAGE.sub('', text)
    text = LINK_TEXT.sub(r'\1', text)
    text = REF_LINK.sub(r'\1', text)
    text = AUTOLINK.sub(r'\1', text)
    text = HTML_TAG.sub('', text)
    text = re.sub(r'(?<![\w:/.-]):[a-z0-9][a-z0-9-]*:(?![\w:/-])', ' ', text)
    text = INLINE_CODE.sub(r'\1', text)
    text = UNDERSCORE_STRONG.sub(r'\1', text)
    text = UNDERSCORE_EM.sub(r'\1', text)
    text = ESCAPE.sub(r'\1', text)
    text = html.unescape(text)
    return ' '.join(text.split())


def heading_map(body):
    """Map heading titles and slugs to their anchor ids, skipping code."""
    ids: dict[str, str] = {}
    used: set[str] = set()

    def collect(text):
        for line in text.splitlines():
            match = HEADING.match(line)
            if not match:
                continue
            title = re.sub(r'\s+\{[^}]*\}\s*$', '', match.group(2)).strip()
            attrs = match.group(3) or ''
            custom = re.search(r'#([\w-]+)', attrs)
            plain = heading_text(title)
            base = heading_slug(plain)
            anchor = custom.group(1) if custom else unique_anchor(base, used)
            used.add(anchor)
            ids.setdefault(plain.strip().lower(), anchor)
            ids.setdefault(title.strip().lower(), anchor)
            ids.setdefault(base.lower(), anchor)
        return text

    outside_code(body, collect, inline=False)
    return ids


def quote_path(path):
    return quote(unquote(path), safe='/')


def flatten(value):
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from flatten(item)
    elif value is not None:
        yield str(value).strip().strip('[]').strip()


def escape_brackets(title):
    return title.replace('[', '\\[').replace(']', '\\]')


def closes_fence(line, fence):
    match = FENCE_CLOSE.match(line)
    return bool(match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence))


def title_from_body(body):
    start, end = '\x01', '\x02'
    marked = outside_code(body, lambda text: start + text + end)
    for line in marked.splitlines():
        if start not in line:
            continue
        line = line.replace(start, '').replace(end, '')
        match = HEADING.match(line)
        if not match:
            continue
        heading = re.sub(r'\s+\{[^}]*\}\s*$', '', match.group(2)).strip()
        heading = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', heading)
        heading = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', heading)
        heading = re.sub(r'[*_`~^]', '', heading)
        heading = re.sub(r'<[^>]+>', '', heading)
        return re.sub(r'\s+', ' ', heading).strip()
    return None


def without_first_heading(body, title=None):
    """Drop the first heading, unless it is a real section with a different title.

    When ``title`` is given (the note has a frontmatter title), only a heading
    that repeats that title is removed; a body starting with ``## section``
    keeps its heading.
    """
    start, end = '\x01', '\x02'
    marked = outside_code(body, lambda text: start + text + end)
    lines, removed, checked = [], False, False
    for line in marked.splitlines():
        if not removed and not checked and start in line:
            candidate = line.replace(start, '').replace(end, '')
            match = HEADING.match(candidate)
            if match:
                checked = True
                heading = re.sub(r'\s+\{[^}]*\}\s*$', '', match.group(2)).strip()
                if title is None or heading.casefold() == str(title).casefold():
                    removed = True
                    continue
        lines.append(line.replace(start, '').replace(end, ''))
    return '\n'.join(lines)


def excerpt(body):
    lines, fence = [], None
    for line in body.splitlines():
        match = FENCE.match(line)
        if match:
            if fence is None:
                fence = match.group(1)
            elif closes_fence(line, fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    text = '\n'.join(lines)
    text = re.sub(r'<!--.*?-->', ' ', text, flags=re.S)
    text = re.sub(r'<(pre|code)\b[^>]*>.*?</\1\s*>', ' ', text, flags=re.I | re.S)
    text = re.sub(r'%%.*?%%', ' ', text, flags=re.S)
    text = re.sub(r'^#{1,6}\s+.*$', ' ', text, flags=re.M)
    text = re.sub(r'^\s*>\s*\[![\w-]+(?:[-+])?\]\s*', ' ', text, flags=re.M | re.I)
    text = re.sub(r'^\s*>\s?', '', text, flags=re.M)
    text = re.sub(r'!?\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r'(?<![\w:/.-]):[a-z0-9][a-z0-9-]*:(?![\w:/-])', ' ', text)
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'(?<!\w)(?:\*{1,3}|_{1,3}|~~|`+)|(?:\*{1,3}|_{1,3}|~~|`+)(?!\w)', '', text)
    text = re.sub(r'^\s*(?:[-*+]|\d+\.)\s+', '', text, flags=re.M)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > 160:
        shortened = text[:160].rsplit(' ', 1)[0]
        text = (shortened or text[:160]) + '…'
    return text


def outside_code(text, fn, inline=True):
    """Apply fn only outside code, HTML code blocks, comments, and %% spans.

    With ``inline=False``, inline code stays part of the surrounding segment so
    callers that inspect whole lines (heading scanning) see the full line.
    """
    out: list[str] = []
    fence = None
    comment = False
    html_code: list[str] = []
    percent = False
    fence_quoted = False

    def transform(segment):
        if not inline:
            return fn(segment)
        parts = re.split(r'(`[^`\n]*`)', segment)
        return ''.join(p if i % 2 else fn(p) for i, p in enumerate(parts))

    tokens = OUTSIDE_CODE_TOKEN if inline else OUTSIDE_CODE_BLOCK

    for line in text.split('\n'):
        # a fence can sit inside a blockquote ("> ```"); judge it without the "> " prefix
        quoted = BLOCKQUOTE_PREFIX.match(line) is not None
        if fence is not None and fence_quoted and not quoted:
            fence = None  # the blockquote ended, which ends a fence opened inside it
        # inside a plain fence a "> ```" line is just code, so only strip when it can matter
        content = (
            line
            if fence is not None and not fence_quoted
            else BLOCKQUOTE_PREFIX.sub('', line, count=1)
        )
        f = FENCE.match(content)
        if f and not (comment or html_code or percent):
            if fence is None:
                fence, fence_quoted = f.group(1), quoted
            elif closes_fence(content, fence):
                fence = None
            out.append(line)
        elif fence is not None:
            out.append(line)
        else:
            pieces, last = [], 0
            for match in tokens.finditer(line):
                token = match.group()
                protected = comment or html_code or percent
                segment = line[last : match.start()]
                pieces.append(segment if protected else transform(segment))
                pieces.append(token)

                if token == '<!--':
                    comment = True
                elif token == '-->' and comment:
                    comment = False
                elif token == '%%' and not (comment or html_code):
                    percent = not percent
                elif not comment and not percent:
                    tag = HTML_CODE_TAG.fullmatch(token)
                    if tag:
                        closing, name = tag.groups()
                        name = name.lower()
                        if closing:
                            if html_code and html_code[-1] == name:
                                html_code.pop()
                        else:
                            html_code.append(name)
                last = match.end()

            if not (comment or html_code or percent):
                pieces.append(transform(line[last:]))
            else:
                pieces.append(line[last:])
            out.append(''.join(pieces))
    return '\n'.join(out)


def section(body, heading, headings=None):
    """Return (section text, anchor id) for a heading, or (None, None).

    ``headings`` is the body's precomputed heading map (the note's ``_headings``),
    so embeds don't re-derive it per target.
    """
    want = heading_text(heading).strip().lower()
    level, anchor, out, fence = None, None, [], None
    for line in body.split('\n'):
        f = FENCE.match(line)
        m = None
        if f:
            if fence is None:
                fence = f.group(1)
            elif closes_fence(line, fence):
                fence = None
        elif fence is None:
            m = HEADING.match(line)
        if level is None:
            if m:
                title = m.group(2).strip()
                plain = heading_text(title)
                if plain.strip().lower() == want:
                    level = len(m.group(1))
                    if headings is None:
                        headings = heading_map(body)
                    anchor = (
                        headings.get(plain.strip().lower())
                        or headings.get(title.lower())
                        or heading_slug(plain)
                    )
            continue
        if m and len(m.group(1)) <= level:
            break
        out.append(line)
    if level is None:
        return None, None
    return '\n'.join(out), anchor
