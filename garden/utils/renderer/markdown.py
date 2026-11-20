"""Markdown conversion: pymdown extensions and the text-level fixes applied before rendering."""

import posixpath
import re
from urllib.parse import quote, unquote

import markdown

from garden.links import inject_note_icons
from garden.parsing import FENCE, closes_fence, heading_slug

EXTENSIONS = [
    'nl2br',
    'admonition',
    'attr_list',
    'md_in_html',
    'footnotes',
    'def_list',
    'abbr',
    'tables',
    'toc',
    'pymdownx.saneheaders',
    'pymdownx.tasklist',
    'pymdownx.mark',
    'pymdownx.tilde',
    'pymdownx.caret',
    'pymdownx.details',
    'pymdownx.superfences',
    'pymdownx.tabbed',
    'pymdownx.highlight',
    'pymdownx.keys',
]

EXTENSION_CONFIGS = {
    'toc': {
        'toc_depth': '2-4',
        'permalink': '',
    },
    'pymdownx.tasklist': {'custom_checkbox': True},
    'pymdownx.tabbed': {'alternate_style': True},
    'pymdownx.highlight': {'use_pygments': False, 'css_class': 'highlight'},
    'pymdownx.superfences': {},
}

# One Markdown instance per process, reset between notes (extensions carry state).
_MD = markdown.Markdown(extensions=EXTENSIONS, extension_configs=EXTENSION_CONFIGS)

CALLOUT_START = re.compile(r'^> \[!(\w+)\]([+-]?)[ \t]*(.*)$')
LIST_ITEM = re.compile(r'^\s*(?:[-*+]|\d+[.)])\s+')
MD_HREF = re.compile(r'href="((?![a-z][a-z0-9+.-]*:|//|/|#)[^"#]+)\.md(#[^"]*)?"', re.I)


def next_fence(line, fence):
    """Return the open fence marker after ``line`` (None when outside a code fence).

    A fence only closes on the same character, at least as long as the opener, with
    nothing after it, so a ``~~~`` line inside a backtick fence is just code.
    """
    match = FENCE.match(line)
    if match is None:
        return fence
    if fence is None:
        return match.group(1)
    return None if closes_fence(line, fence) else fence


def convert_callouts(text):
    lines = text.split('\n')
    out = []
    fence = None
    i = 0
    while i < len(lines):
        line = lines[i]
        fence = next_fence(line, fence)
        m = None if fence is not None else CALLOUT_START.match(line)
        if not m:
            out.append(line)
            i += 1
            continue

        kind, fold, title = m.groups()
        i += 1
        body = []
        while i < len(lines) and lines[i].startswith('>'):
            body.append(re.sub(r'^> ?', '', lines[i]))
            i += 1

        marker = '!!!' if not fold else ('???' if fold == '-' else '???+')
        title = (title.strip() or kind).replace('"', "'")
        out.append('')
        out.append('%s %s "%s"' % (marker, kind.lower(), title))
        for b in body:
            out.append(('    ' + b) if b.strip() else '')
        out.append('')
    return '\n'.join(out)


def fix_lists(text):
    """Obsidian allows a list right under a paragraph; python-markdown needs a blank line."""
    out, fence, prev = [], None, ''
    for line in text.split('\n'):
        if FENCE.match(line):
            fence = next_fence(line, fence)
        elif (
            fence is None
            and LIST_ITEM.match(line)
            and prev.strip()
            and not LIST_ITEM.match(prev)
            and not prev.startswith((' ', '\t'))
        ):
            out.append('')
        out.append(line)
        prev = line
    return '\n'.join(out)


DOODLE_START = re.compile(r'^\s*:::\s*doodle(?:\s+(.*))?$', re.I)


def convert_doodles(text):
    """Turn ``::: doodle`` blocks into accessible figures with an optional caption.

    The block holds ordinary Markdown (an image, a quote, a short aside); the
    caption is the text after ``doodle``. A doodle without a caption still gets
    a figure, and the inner image's alt text remains the accessible name.
    """
    lines = text.split('\n')
    out: list[str] = []
    fence = None
    i = 0
    while i < len(lines):
        line = lines[i]
        fence = next_fence(line, fence)
        match = None if fence is not None else DOODLE_START.match(line)
        if not match:
            out.append(line)
            i += 1
            continue
        caption = (match.group(1) or '').strip().strip('"').strip("'")
        i += 1
        body = []
        while i < len(lines) and not re.match(r'^\s*:::\s*$', lines[i]):
            body.append(lines[i])
            i += 1
        if i < len(lines):
            i += 1
        out.append('')
        out.append('<figure class="doodle" markdown="1">')
        out.append('')
        out.extend(body)
        out.append('')
        if caption:
            out.append('<figcaption>%s</figcaption>' % caption)
            out.append('')
        out.append('</figure>')
        out.append('')
    return '\n'.join(out)


def resolve_md_links(html_text, src):
    base = posixpath.dirname(src)

    def repl(m):
        target = posixpath.normpath(posixpath.join(base, unquote(m.group(1))))
        fragment = m.group(2) or ''
        if fragment.startswith('#'):
            fragment = '#' + heading_slug(unquote(fragment[1:]))
        return 'href="/%s.html%s"' % (quote(target, safe='/'), fragment)

    return MD_HREF.sub(repl, html_text)


def render_html(text, src):
    """Convert one note body to ``(html, toc_html)`` with every text fix applied."""
    _MD.reset()
    html_body = _MD.convert(convert_doodles(convert_callouts(fix_lists(text))))
    html_body = resolve_md_links(html_body, src)
    html_body = inject_note_icons(html_body, src)
    return html_body, _MD.toc if _MD.toc_tokens else ''
