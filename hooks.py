"""Garden hooks: wikilinks, backlinks, links-to, embedded notes, tag index page, notes.json."""
import html
import json
import os
import posixpath
import re
import shutil
import subprocess
from datetime import date, datetime

import yaml

try:
    from mkdocs.plugins import event_priority
except ImportError:
    def event_priority(priority):
        return lambda func: func

FRONT = re.compile(r'\A---\s*\n(.*?)\n---\s*\n', re.S)
WIKILINK = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]')
EMBED = re.compile(r'!\[\[([^\]|#]+)(?:#([^\]|]*))?(?:\|[^\]]*)?\]\]')
LINK = re.compile(r'(!?)\[\[([^\]|#]+)(?:#([^\]|]*))?(?:\|([^\]]*))?\]\]')
MDLINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)\s#]+\.md)(?:#[^)]*)?\)')
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*(\{[^}]*\})?\s*$')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')
STAGE_BY_FOLDER = {'seedlings': 'seedling', 'buds': 'bud', 'evergreens': 'evergreen'}
STAGE_INDEX = {folder + '/index.md': stage for folder, stage in STAGE_BY_FOLDER.items()}
TAG_PAGE = 'by-tag/index.md'
MAX_EMBED_DEPTH = 2

notes = {}
backlinks = {}
outgoing = {}
lookup = {}
media_lookup = {}


def slugify(text):
    return re.sub(r'[^\w]+', '-', str(text).lower()).strip('-')


def heading_slug(text):
    text = re.sub(r'[^\w\s-]', '', str(text)).strip().lower()
    return re.sub(r'[-\s]+', '-', text)


def _flatten(value):
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _flatten(item)
    elif value is not None:
        yield str(value).strip().strip('[]').strip()


def _esc(title):
    return title.replace('[', '\\[').replace(']', '\\]')


def _excerpt(body):
    text = re.sub(r'```.*?```', '', body, flags=re.S)
    text = re.sub(r'^#+\s.*$', '', text, flags=re.M)
    text = re.sub(r'!?\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'[*_`>=~^#]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:160] + ('…' if len(text) > 160 else '')


def _git_dates(config, path):
    """(planted, tended) from git history. a file with uncommitted changes counts as tended today."""
    if not shutil.which('git'):
        return None, None
    root = os.path.dirname(os.path.abspath(config['config_file_path']))
    rel = os.path.relpath(path, root)

    def run(*args):
        try:
            out = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True, timeout=20)
        except Exception:
            return ''
        return out.stdout.strip() if out.returncode == 0 else ''

    if run('status', '--porcelain', '--', rel):
        tended = date.today().isoformat()
    else:
        tended = run('log', '-1', '--format=%cs', '--', rel)
    first = run('log', '--follow', '--diff-filter=A', '--format=%cs', '--', rel).splitlines()
    planted = first[-1] if first else tended
    return planted or None, tended or None


def on_files(files, config):
    notes.clear()
    backlinks.clear()
    outgoing.clear()
    lookup.clear()
    media_lookup.clear()

    for f in files.documentation_pages():
        with open(f.abs_src_path, encoding='utf-8') as fh:
            text = fh.read()
        meta, body = {}, text
        m = FRONT.match(text)
        if m:
            try:
                meta = yaml.safe_load(m.group(1)) or {}
            except Exception:
                meta = {}
            body = text[m.end():]

        stem = posixpath.splitext(posixpath.basename(f.src_uri))[0]
        folder = posixpath.dirname(f.src_uri)
        h1 = re.search(r'^#\s+(.+)$', body, re.M)
        title = meta.get('title') or (h1.group(1).strip() if h1 else None)
        if not title:
            title = (posixpath.basename(folder) or 'home') if stem == 'index' else stem

        section = f.src_uri.split('/')[0] if '/' in f.src_uri else 'home'
        planted_git, tended_git = (None, None) if stem == 'index' else _git_dates(config, f.abs_src_path)
        tended = meta.get('tended') or tended_git or datetime.fromtimestamp(os.path.getmtime(f.abs_src_path)).date()
        planted = meta.get('planted') or planted_git
        tags = meta.get('tags') or []
        if isinstance(tags, str):
            tags = [tags]
        tags = [str(t) for t in tags]

        notes[f.src_uri] = {
            'title': str(title),
            'url': f.url,
            'section': section,
            'stage': meta.get('stage') or STAGE_BY_FOLDER.get(section),
            'tags': tags,
            'tag_slugs': [slugify(t) for t in tags],
            'planted': planted,
            'tended': tended,
            'excerpt': _excerpt(body),
            'is_index': stem == 'index',
            '_body': body,
            '_stem': stem,
            '_manual': list(_flatten(meta.get('links_to') or meta.get('links to') or [])),
        }

    for f in files:
        if not f.is_documentation_page():
            media_lookup.setdefault(posixpath.basename(f.src_uri).lower(), f.src_uri)
            media_lookup.setdefault(f.src_uri.lower(), f.src_uri)

    for src, n in notes.items():
        for key in (n['title'], n['_stem'], posixpath.splitext(src)[0]):
            lookup.setdefault(key.lower(), src)

    for src, n in notes.items():
        targets = set()
        for raw in WIKILINK.findall(n['_body']):
            t = lookup.get(raw.strip().lower())
            if t:
                targets.add(t)
        for raw in MDLINK.findall(n['_body']):
            t = posixpath.normpath(posixpath.join(posixpath.dirname(src), raw))
            if t in notes:
                targets.add(t)
        for raw in n['_manual']:
            t = lookup.get(raw.lower())
            if t:
                targets.add(t)
        targets.discard(src)
        outgoing[src] = sorted(
            ({'title': notes[t]['title'], 'url': notes[t]['url']} for t in targets),
            key=lambda x: x['title'].lower(),
        )
        for t in targets:
            backlinks.setdefault(t, []).append({'title': n['title'], 'url': n['url']})

    for lst in backlinks.values():
        lst.sort(key=lambda b: b['title'].lower())
    return files


def _outside_code(text, fn):
    """Apply fn only to text that is not inside fenced code or inline code."""
    out, fence = [], None
    for line in text.split('\n'):
        f = FENCE.match(line)
        if f:
            if fence is None:
                fence = f.group(1)
            elif f.group(1)[0] == fence[0] and len(f.group(1)) >= len(fence):
                fence = None
            out.append(line)
        elif fence is not None:
            out.append(line)
        else:
            parts = re.split(r'(`[^`\n]*`)', line)
            out.append(''.join(p if i % 2 else fn(p) for i, p in enumerate(parts)))
    return '\n'.join(out)


def _section(body, heading):
    """Return (section text, anchor id) for a heading, or (None, None)."""
    want = heading.strip().lower()
    level, anchor, out, fence = None, None, [], None
    for line in body.split('\n'):
        f = FENCE.match(line)
        m = None
        if f:
            if fence is None:
                fence = f.group(1)
            elif f.group(1)[0] == fence[0] and len(f.group(1)) >= len(fence):
                fence = None
        elif fence is None:
            m = HEADING.match(line)
        if level is None:
            if m and m.group(2).strip().lower() == want:
                level = len(m.group(1))
                custom = re.search(r'#([\w-]+)', m.group(3) or '')
                anchor = custom.group(1) if custom else heading_slug(m.group(2))
            continue
        if m and len(m.group(1)) <= level:
            break
        out.append(line)
    if level is None:
        return None, None
    return '\n'.join(out), anchor


def _expand(text, src, stack, depth):
    if depth >= MAX_EMBED_DEPTH:
        return text

    def repl(m):
        name, section = m.group(1).strip(), m.group(2)
        target = lookup.get(name.lower())
        if not target:
            return m.group(0)
        if target in stack and not section:
            return m.group(0)
        body = notes[target]['_body']
        label = notes[target]['title']
        anchor = None
        if section:
            body, anchor = _section(body, section)
            if body is None:
                return m.group(0)
            label += ' › ' + section.strip()
        else:
            body = re.sub(r'^#\s+.+\n?', '', body, count=1, flags=re.M)
        body = _outside_code(body, lambda t: _expand(t, target, stack + (target,), depth + 1)).strip()
        rel = posixpath.relpath(target, posixpath.dirname(src) or '.')
        if anchor:
            rel += '#' + anchor
        return '\n\n<div class="embed" markdown="1">\n\n**[%s](%s)**\n\n%s\n\n</div>\n\n' % (_esc(label), rel, body)

    return EMBED.sub(repl, text)


def _links(text, src):
    """Turn [[wikilinks]] and ![[images]] into normal markdown links."""
    base = posixpath.dirname(src) or '.'

    def repl(m):
        bang, name, heading, alias = m.group(1), m.group(2).strip(), m.group(3), m.group(4)
        key = name.lower()
        if bang:
            media = media_lookup.get(key) or media_lookup.get(posixpath.basename(key))
            if media:
                rel = posixpath.relpath(media, base).replace(' ', '%20')
                size, alt = '', name
                if alias and alias.strip().isdigit():
                    size = '{ width="%s" }' % alias.strip()
                elif alias:
                    alt = alias
                return '![%s](%s)%s' % (alt, rel, size)
        target = lookup.get(key)
        if not target:
            return '<span class="broken-link">%s</span>' % html.escape(alias or name)
        rel = posixpath.relpath(target, base).replace(' ', '%20')
        if heading:
            rel += '#' + heading_slug(heading)
        label = alias or (name + (' › ' + heading.strip() if heading else ''))
        return '[%s](%s)' % (_esc(label), rel)

    return LINK.sub(repl, text)


def _tag_index(src):
    by_tag = {}
    for n_src, n in notes.items():
        if n['is_index']:
            continue
        for t in n['tags']:
            by_tag.setdefault(t, []).append((n['title'], n_src))
    if not by_tag:
        return '\n\n*no tagged notes yet. add `tags: [name]` to a note.*\n'
    out = ['\n\n']
    for tag in sorted(by_tag, key=str.lower):
        out.append('## %s { #tag-%s }\n\n' % (tag, slugify(tag)))
        for title, n_src in sorted(by_tag[tag], key=lambda x: x[0].lower()):
            rel = posixpath.relpath(n_src, posixpath.dirname(src) or '.')
            out.append('- [%s](%s)\n' % (_esc(title), rel))
        out.append('\n')
    return ''.join(out)


def on_nav(nav, config, files):
    """add every note in a stage folder to its sidebar section automatically."""
    for section in nav.items:
        folder = str(getattr(section, 'title', '')).lower()
        if not getattr(section, 'is_section', False) or folder not in STAGE_BY_FOLDER:
            continue
        have = {c.file.src_uri for c in section.children if getattr(c, 'is_page', False)}
        extra = [
            f for f in files.documentation_pages()
            if f.src_uri.startswith(folder + '/') and f.src_uri not in have and f.page is not None
        ]
        extra.sort(key=lambda f: notes.get(f.src_uri, {}).get('title', f.src_uri).lower())
        for f in extra:
            f.page.parent = section
            section.children.append(f.page)
    return nav


def _stage_index(src, stage):
    items = sorted(
        ((n['title'], s, n['excerpt']) for s, n in notes.items() if n['stage'] == stage and not n['is_index']),
        key=lambda x: x[0].lower(),
    )
    if not items:
        return '\n\n*nothing planted here yet.*\n'
    out = ['\n\n']
    for title, s, excerpt in items:
        rel = posixpath.relpath(s, posixpath.dirname(src) or '.')
        line = '- [%s](%s)' % (_esc(title), rel)
        if excerpt:
            line += ' \u2014 ' + html.escape(excerpt).replace('[', '\\[').replace(']', '\\]')
        out.append(line + '\n')
    return ''.join(out)


def _related(src, limit=3):
    me = notes[src]
    mine = {t.lower() for t in me['tags']}
    others = [n for s, n in notes.items() if s != src and not n['is_index'] and n['stage']]
    scored = []
    for n in others:
        count = len(mine & {t.lower() for t in n['tags']})
        if count:
            scored.append((count, str(n['tended']), n))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    picks = [x[2] for x in scored[:limit]]
    if len(picks) < limit:
        chosen = {id(n) for n in picks}
        rest = sorted((n for n in others if id(n) not in chosen), key=lambda n: str(n['tended']), reverse=True)
        picks += rest[:limit - len(picks)]
    return [{'title': n['title'], 'url': n['url']} for n in picks]


@event_priority(100)
def on_page_markdown(markdown, page, config, files):
    src = page.file.src_uri
    markdown = _outside_code(markdown, lambda t: _expand(t, src, (src,), 0))
    markdown = _outside_code(markdown, lambda t: _links(t, src))
    if src == TAG_PAGE:
        markdown += _tag_index(src)
    if src in STAGE_INDEX:
        if not re.search(r'^#\s', markdown, re.M):
            markdown = '# %s\n\n%s' % (posixpath.dirname(src), markdown.lstrip())
        markdown += _stage_index(src, STAGE_INDEX[src])
    n = notes.get(src)
    if n and not n['is_index']:
        page.meta.setdefault('tended', str(n['tended'])[:10])
        if n['planted']:
            page.meta.setdefault('planted', str(n['planted'])[:10])
    return markdown


def on_page_context(context, page, config, nav):
    src = page.file.src_uri
    n = notes.get(src)
    is_note = bool(n and not n['is_index'])
    context['backlinks'] = backlinks.get(src, [])
    context['outgoing'] = outgoing.get(src, [])
    context['slug'] = slugify
    context['description'] = n['excerpt'] if is_note else ''
    context['related'] = _related(src) if is_note else []
    return context


def _json_default(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    return str(o)


def on_post_build(config):
    out = [{k: v for k, v in n.items() if not k.startswith('_')} for n in notes.values()]
    with open(os.path.join(config['site_dir'], 'notes.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, default=_json_default, ensure_ascii=False)