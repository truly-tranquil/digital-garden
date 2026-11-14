import os
import re
import posixpath
from urllib.parse import quote, unquote

import markdown
from pymdownx.superfences import fence_div_format
from jinja2 import Environment, FileSystemLoader

EXTENSIONS = [
    'nl2br', 'admonition', 'attr_list', 'md_in_html', 'footnotes',
    'def_list', 'abbr', 'tables', 'toc',
    'pymdownx.saneheaders', 'pymdownx.tasklist', 'pymdownx.mark',
    'pymdownx.tilde', 'pymdownx.caret', 'pymdownx.details',
    'pymdownx.superfences', 'pymdownx.tabbed', 'pymdownx.highlight',
]

EXTENSION_CONFIGS = {
    'toc': {
        'toc_depth': '2-4',
        'permalink': '¶',
        'permalink_title': 'Link to this section',
    },
    'pymdownx.tasklist': {'custom_checkbox': True},
    'pymdownx.tabbed': {'alternate_style': True},
    'pymdownx.highlight': {'use_pygments': False, 'css_class': 'highlight'},
    'pymdownx.superfences': {
        'custom_fences': [
            {'name': 'mermaid', 'class': 'mermaid', 'format': fence_div_format}
        ]
    },
}

STAGE_FOLDER = {'seedling': 'seedlings', 'bud': 'buds', 'evergreen': 'evergreens'}
CALLOUT_START = re.compile(r'^> \[!(\w+)\]([+-]?)[ \t]*(.*)$')
MD_HREF = re.compile(r'href="((?![a-z][a-z0-9+.-]*:|//|/|#)[^"#]+)\.md(#[^"]*)?"', re.I)


def convert_callouts(text):
    lines = text.split('\n')
    out = []
    in_fence = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith('```') or line.lstrip().startswith('~~~'):
            in_fence = not in_fence
        m = None if in_fence else CALLOUT_START.match(line)
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


def resolve_md_links(html_text, src):
    base = posixpath.dirname(src)

    def repl(m):
        target = posixpath.normpath(posixpath.join(base, unquote(m.group(1))))
        return 'href="/%s.html%s"' % (quote(target, safe='/'), m.group(2) or '')

    return MD_HREF.sub(repl, html_text)


def render_page(note, text, src, ctx, config, theme_dir="my-garden-theme", nav_notes=None):
    md = markdown.Markdown(extensions=EXTENSIONS, extension_configs=EXTENSION_CONFIGS)
    html_body = md.convert(convert_callouts(text))
    html_body = resolve_md_links(html_body, src)
    toc_html = md.toc if md.toc_tokens else ''

    env = Environment(
        loader=FileSystemLoader(os.path.join(theme_dir, 'templates')),
        autoescape=True,
    )
    template = env.get_template('page.html')
    return template.render(
        title=note['title'],
        show_title='<h1' not in html_body,
        stage=note['stage'],
        stage_folder=STAGE_FOLDER.get(note['stage'], ''),
        tags=[{'name': t, 'slug': s} for t, s in zip(note['tags'], note['tag_slugs'])],
        planted=str(note['planted'])[:10] if note['planted'] else '',
        tended=str(note['tended'])[:10] if note['tended'] else '',
        content=html_body,
        toc=toc_html,
        backlinks=ctx['backlinks'],
        outgoing=ctx['outgoing'],
        related=ctx['related'],
        config=config,
        nav_notes=nav_notes or [],
    )