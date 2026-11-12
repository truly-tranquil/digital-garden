"""Garden content processing and generated assets for MkDocs and Zensical."""
import html
import json
import os
import posixpath
import re
import shutil
import subprocess
from datetime import date, datetime
from xml.etree import ElementTree
from urllib.parse import quote, unquote, urljoin

import yaml
from markdown.extensions.toc import slugify as toc_slugify

try:
    from mkdocs.plugins import event_priority
    from mkdocs.utils import log
except ImportError:
    def event_priority(priority):
        return lambda func: func

    class log:
        @staticmethod
        def warning(message):
            print('WARNING:', message)

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
STAGE_BY_FOLDER = {'seedlings': 'seedling', 'buds': 'bud', 'evergreens': 'evergreen'}
STAGE_INDEX = {folder + '/index.md': stage for folder, stage in STAGE_BY_FOLDER.items()}
TAG_PAGE = 'by-tag/index.md'
MAX_EMBED_DEPTH = 2
ATOM_NS = 'http://www.w3.org/2005/Atom'

notes = {}
backlinks = {}
outgoing = {}
lookup = {}
media_lookup = {}
serving = False


def slugify(text):
    return re.sub(r'[^\w]+', '-', str(text).lower()).strip('-')


def heading_slug(text):
    return toc_slugify(str(text), '-')


def _unescape_wikilink(value):
    return re.sub(r'\\([\\|#])', r'\1', value).strip()


def _parse_wikilink(value):
    def split_unescaped(text, delimiter):
        escaped = False
        for index, character in enumerate(text):
            if character == delimiter and not escaped:
                return text[:index], text[index + 1:]
            if character == '\\' and not escaped:
                escaped = True
            else:
                escaped = False
        return text, None

    target, alias = split_unescaped(value, '|')
    name, heading = split_unescaped(target, '#')
    return _unescape_wikilink(name), _unescape_wikilink(heading) if heading is not None else None, _unescape_wikilink(alias) if alias is not None else None


def _heading_map(body):
    ids, counts = {}, {}

    def collect(text):
        for line in text.splitlines():
            match = HEADING.match(line)
            if not match:
                continue
            title = re.sub(r'\s+\{[^}]*\}\s*$', '', match.group(2)).strip()
            attrs = match.group(3) or ''
            custom = re.search(r'#([\w-]+)', attrs)
            base = custom.group(1) if custom else heading_slug(title)
            count = counts.get(base, 0)
            counts[base] = count + 1
            anchor = base if custom or count == 0 else '%s_%d' % (base, count)
            ids.setdefault(title.strip().lower(), anchor)
            ids.setdefault(base.lower(), anchor)
        return text

    _outside_code(body, collect)
    return ids


def _quote_path(path):
    return quote(unquote(path), safe='/')


def _warn(message):
    log.warning('[digital-garden] %s' % message)


def _validated_date(value, key, src):
    if value is None:
        return None
    try:
        date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        _warn('%s has an invalid %s date: %r' % (src, key, value))
    return value


def _link_context(body, target, target_src):
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
                excerpt = _excerpt(line)
                if excerpt:
                    context.append(excerpt)
                    return text
        return text

    _outside_code(body, find)
    return context[0] if context else ''


def _git_dates_for_files(config, files):
    if serving or not shutil.which('git'):
        return {}
    root = os.path.dirname(os.path.abspath(config['config_file_path']))
    try:
        history = subprocess.run(
            ['git', 'log', '--name-status', '--find-renames', '--format=COMMIT%x09%cs%x09%h%x09%s'],
            cwd=root, capture_output=True, text=True, timeout=60, check=False,
        )
        status = subprocess.run(
            ['git', 'status', '--porcelain', '--untracked-files=all', '-z'],
            cwd=root, capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        _warn('unable to read git note dates: %s' % exc)
        return {}
    if history.returncode:
        _warn('git history lookup failed: %s' % history.stderr.strip())
        return {}
    dates, added, history_by_path = {}, {}, {}
    current_commit = None
    for line in history.stdout.splitlines():
        if line.startswith('COMMIT\t'):
            _, commit_date, commit_hash, subject = line.split('\t', 3)
            current_commit = {
                'date': commit_date,
                'hash': commit_hash,
                'subject': subject,
            }
            continue
        if not current_commit or not line:
            continue
        fields = line.split('\t')
        state = fields[0]
        paths = fields[1:]
        if state.startswith('R') or state.startswith('C'):
            paths = paths[-1:]
        for path in paths:
            path = path.replace('\\', '/')
            dates.setdefault(path, [None, None])[1] = dates.get(path, [None, None])[1] or current_commit['date']
            if state == 'A':
                added[path] = current_commit['date']
            commits = history_by_path.setdefault(path, [])
            if len(commits) < 10:
                commits.append(current_commit.copy())
    for path, planted in added.items():
        dates.setdefault(path, [None, None])[0] = planted
    if status.returncode == 0:
        today = date.today().isoformat()
        pending_original = False
        for entry in status.stdout.split('\0'):
            if pending_original:
                pending_original = False
                continue
            if len(entry) < 4:
                continue
            state, path = entry[:2], entry[3:].replace('\\', '/')
            if 'R' in state or 'C' in state:
                pending_original = True
            dates.setdefault(path, [None, None])[1] = today
    result = {}
    for file in files.documentation_pages():
        path = os.path.relpath(file.abs_src_path, root).replace('\\', '/')
        planted, tended = dates.get(path, (None, None))
        if tended is None and planted is not None:
            tended = planted
        result[file.src_uri] = (planted, tended, history_by_path.get(path, []))
    return result


def _flatten(value):
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _flatten(item)
    elif value is not None:
        yield str(value).strip().strip('[]').strip()


def _esc(title):
    return title.replace('[', '\\[').replace(']', '\\]')


def _is_listed(n):
    return (
        not n['is_index'] and bool(n.get('stage'))
        and not n.get('unlisted', False) and not n.get('draft', False)
    )


def _is_public(n):
    return not n.get('unlisted', False) and not n.get('draft', False)


def _closes_fence(line, fence):
    match = FENCE_CLOSE.match(line)
    return bool(match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence))


def _title_from_body(body):
    start, end = '\x01', '\x02'
    marked = _outside_code(body, lambda text: start + text + end)
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


def _without_first_heading(body):
    start, end = '\x01', '\x02'
    marked = _outside_code(body, lambda text: start + text + end)
    lines, removed = [], False
    for line in marked.splitlines():
        if not removed and start in line:
            candidate = line.replace(start, '').replace(end, '')
            if HEADING.match(candidate):
                removed = True
                continue
        lines.append(line.replace(start, '').replace(end, ''))
    return '\n'.join(lines)


def _excerpt(body):
    lines, fence = [], None
    for line in body.splitlines():
        match = FENCE.match(line)
        if match:
            if fence is None:
                fence = match.group(1)
            elif _closes_fence(line, fence):
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
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'(?<!\w)(?:\*{1,3}|_{1,3}|~~|`+)|(?:\*{1,3}|_{1,3}|~~|`+)(?!\w)', '', text)
    text = re.sub(r'^\s*(?:[-*+]|\d+\.)\s+', '', text, flags=re.M)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > 160:
        shortened = text[:160].rsplit(' ', 1)[0]
        text = (shortened or text[:160]) + '…'
    return text


def on_files(files, config):
    notes.clear()
    backlinks.clear()
    outgoing.clear()
    lookup.clear()
    media_lookup.clear()
    git_dates = _git_dates_for_files(config, files)

    for f in files.documentation_pages():
        with open(f.abs_src_path, encoding='utf-8') as fh:
            text = fh.read()
        meta, body = {}, text
        m = FRONT.match(text)
        if m:
            try:
                meta = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError as exc:
                _warn('%s has invalid front matter: %s' % (f.src_uri, exc))
                meta = {}
            body = text[m.end():]
        if not isinstance(meta, dict):
            _warn('%s front matter must be a mapping' % f.src_uri)
            meta = {}

        stem = posixpath.splitext(posixpath.basename(f.src_uri))[0]
        folder = posixpath.dirname(f.src_uri)
        title = meta.get('title') or _title_from_body(body)
        if not title:
            title = (posixpath.basename(folder) or 'home') if stem == 'index' else stem

        section = f.src_uri.split('/')[0] if '/' in f.src_uri else 'home'
        planted_git, tended_git, git_history = (
            (None, None, []) if stem == 'index'
            else git_dates.get(f.src_uri, (None, None, []))
        )
        tended = _validated_date(meta.get('tended'), 'tended', f.src_uri) or tended_git or datetime.fromtimestamp(os.path.getmtime(f.abs_src_path)).date()
        planted = _validated_date(meta.get('planted'), 'planted', f.src_uri) or planted_git
        tags = meta.get('tags') or []
        if isinstance(tags, str):
            tags = [tags]
        elif not isinstance(tags, list):
            _warn('%s tags must be a string or list' % f.src_uri)
            tags = []
        normalized_tags, seen_tags = [], set()
        for tag in tags:
            clean_tag = str(tag).strip()
            if clean_tag and clean_tag.casefold() not in seen_tags:
                normalized_tags.append(clean_tag)
                seen_tags.add(clean_tag.casefold())
        tags = normalized_tags
        aliases = meta.get('aliases') or []
        if isinstance(aliases, str):
            aliases = [aliases]
        elif not isinstance(aliases, list):
            _warn('%s aliases must be a string or list' % f.src_uri)
            aliases = []
        stage = meta.get('stage') or STAGE_BY_FOLDER.get(section)
        if meta.get('stage') and (
            not isinstance(meta['stage'], str)
            or meta['stage'] not in {'seedling', 'bud', 'evergreen'}
        ):
            _warn('%s has invalid stage: %r' % (f.src_uri, meta['stage']))
            stage = STAGE_BY_FOLDER.get(section)

        notes[f.src_uri] = {
            'title': str(title),
            'url': f.url,
            'section': section,
            'stage': stage,
            'tags': tags,
            'tag_slugs': [slugify(t) for t in tags],
            'planted': planted,
            'history': git_history,
            'tended': tended,
            'excerpt': _excerpt(str(meta['description'])) if meta.get('description') else _excerpt(body),
            'is_index': stem == 'index',
            'unlisted': meta.get('unlisted') is True,
            'draft': meta.get('draft') is True,
            'aliases': [str(alias) for alias in aliases],
            '_body': body,
            '_stem': stem,
            '_headings': _heading_map(body),
            '_manual': list(_flatten(meta.get('links_to') or meta.get('links to') or [])),
        }

    for field in ('_stem', 'title'):
        values = {}
        for src, note in notes.items():
            if note['is_index']:
                continue
            value = note[field] if field == '_stem' else note['title']
            values.setdefault(str(value).casefold(), []).append(src)
        for value, paths in values.items():
            if len(paths) > 1:
                _warn('duplicate %s %r: %s' % (field.lstrip('_'), value, ', '.join(paths)))

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
        wikilinks, mdlinks = [], []

        def collect_links(text):
            wikilinks.extend(
                match.group(1)
                for match in WIKILINK.finditer(text)
                if match.start() == 0 or text[match.start() - 1] != '!'
            )
            mdlinks.extend(MDLINK.findall(text))
            return text

        _outside_code(n['_body'], collect_links)
        if n['is_index']:
            outgoing[src] = []
            continue
        for raw in wikilinks:
            name, _, _ = _parse_wikilink(raw)
            t = lookup.get(name.lower()) or lookup.get(slugify(name).lower())
            if t:
                targets.add(t)
        for raw in mdlinks:
            t = posixpath.normpath(posixpath.join(posixpath.dirname(src), unquote(raw)))
            if t in notes:
                targets.add(t)
            else:
                _warn('%s links to missing Markdown file %r' % (src, raw))
        for raw in n['_manual']:
            t = lookup.get(raw.lower()) or lookup.get(slugify(raw).lower())
            if t:
                targets.add(t)
            else:
                _warn('%s links to missing note %r in links_to' % (src, raw))
        if not n['is_index']:
            for raw in wikilinks:
                name, _, _ = _parse_wikilink(raw)
                if name and name.lower() not in lookup and slugify(name).lower() not in lookup:
                    _warn('%s links to missing note %r' % (src, name))
        targets = {
            target for target in targets
            if target != src and not notes[target]['is_index'] and _is_public(notes[target])
        }
        outgoing[src] = sorted(
            ({'title': notes[t]['title'], 'url': notes[t]['url']} for t in targets),
            key=lambda x: x['title'].lower(),
        )
        for t in targets:
            if not n.get('unlisted', False) and not n.get('draft', False):
                backlinks.setdefault(t, []).append({
                    'title': n['title'],
                    'url': n['url'],
                    'context': _link_context(n['_body'], notes[t], t),
                })

    for lst in backlinks.values():
        lst.sort(key=lambda b: b['title'].lower())
    remove_file = getattr(files, 'remove', None)
    if callable(remove_file):
        for file in files.documentation_pages():
            if notes.get(file.src_uri, {}).get('draft', False):
                remove_file(file)
    return files


def on_serve(server, config, builder):
    global serving
    serving = True
    return server


def _outside_code(text, fn):
    """Apply fn only outside code, HTML code blocks, comments, and %% spans."""
    out, fence, comment, html_code, percent = [], None, False, [], False

    def transform(segment):
        parts = re.split(r'(`[^`\n]*`)', segment)
        return ''.join(p if i % 2 else fn(p) for i, p in enumerate(parts))

    for line in text.split('\n'):
        f = FENCE.match(line)
        if f and not (comment or html_code or percent):
            if fence is None:
                fence = f.group(1)
            elif _closes_fence(line, fence):
                fence = None
            out.append(line)
        elif fence is not None:
            out.append(line)
        else:
            pieces, last = [], 0
            for match in OUTSIDE_CODE_TOKEN.finditer(line):
                token = match.group()
                protected = comment or html_code or percent
                segment = line[last:match.start()]
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
            elif _closes_fence(line, fence):
                fence = None
        elif fence is None:
            m = HEADING.match(line)
        if level is None:
            if m and m.group(2).strip().lower() == want:
                level = len(m.group(1))
                anchor = _heading_map(body).get(m.group(2).strip().lower(), heading_slug(m.group(2)))
            continue
        if m and len(m.group(1)) <= level:
            break
        out.append(line)
    if level is None:
        return None, None
    return '\n'.join(out), anchor


def _rewrite_embed_content(body, target, src, prefix):
    seen = {}
    anchors = {}
    lines, fence = [], None
    for line in body.splitlines():
        match = FENCE.match(line)
        if match:
            if fence is None:
                fence = match.group(1)
            elif _closes_fence(line, fence):
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
        base = custom.group(1) if custom else heading_slug(title)
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
        suffix_at = min((index for index in (raw.find('?'), raw.find('#')) if index >= 0), default=len(raw))
        path, suffix = raw[:suffix_at], raw[suffix_at:]
        if not path:
            return destination
        target_path = posixpath.normpath(posixpath.join(posixpath.dirname(target), unquote(path)))
        relative = posixpath.relpath(target_path, posixpath.dirname(src) or '.')
        result = _quote_path(relative) + suffix
        return '<%s>' % result if wrapped else result

    def rewrite_markdown_link(match):
        return (match.group('open') + rewrite_destination(match.group('dest'))
                + (match.group('title') or '') + match.group('close'))

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


def _expand(text, src, stack, depth):
    if depth >= MAX_EMBED_DEPTH:
        return text

    embed_count = 0

    def repl(m):
        nonlocal embed_count
        embed_count += 1
        name, section = m.group(1).strip(), m.group(2)
        target = lookup.get(name.lower()) or lookup.get(slugify(name).lower())
        if not target or notes[target].get('draft', False):
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
            body = _without_first_heading(body)
        body = _outside_code(body, lambda t: _expand(t, target, stack + (target,), depth + 1)).strip()
        body = _outside_code(body, lambda t: _links(t, target))
        prefix = 'embed-%s-%s-%s-' % (
            slugify(posixpath.splitext(src)[0]),
            slugify(posixpath.splitext(target)[0]),
            embed_count,
        )
        body = _rewrite_embed_content(body, target, src, prefix)
        rel = posixpath.relpath(target, posixpath.dirname(src) or '.')
        if anchor:
            rel = _quote_path(rel) + '#' + quote(anchor, safe='-._~')
        else:
            rel = _quote_path(rel)
        return '\n\n<div class="embed" markdown="1">\n\n**[%s](%s)**\n\n%s\n\n</div>\n\n' % (_esc(label), rel, body)

    return EMBED.sub(repl, text)


def _links(text, src):
    """Turn [[wikilinks]] and ![[images]] into normal markdown links."""
    base = posixpath.dirname(src) or '.'

    def repl(m):
        bang = m.group(1)
        name, heading, alias = _parse_wikilink(m.group(2))
        key = name.lower()
        if bang:
            media = media_lookup.get(key) or media_lookup.get(posixpath.basename(key))
            if media:
                rel = _quote_path(posixpath.relpath(media, base))
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
        rel = _quote_path(posixpath.relpath(target, base))
        if heading:
            rel += '#' + quote(notes.get(target, {}).get('_headings', {}).get(heading.strip().lower(), heading_slug(heading)), safe='-._~')
        label = alias or (name + (' › ' + heading.strip() if heading else ''))
        return '[%s](%s)' % (_esc(label), rel)

    return LINK.sub(repl, text)


def _tag_index(src):
    by_tag = {}
    for n_src, n in notes.items():
        if not _is_listed(n):
            continue
        for t in n['tags']:
            by_tag.setdefault(t, []).append((n['title'], n_src))
    if not by_tag:
        return '\n\n*no tagged notes yet. add `tags: [name]` to a note.*\n'
    out = ['\n\n']
    for tag in sorted(by_tag, key=str.lower):
        out.append('## %s { #tag-%s }\n\n' % (tag, slugify(tag)))
        for title, n_src in sorted(by_tag[tag], key=lambda x: x[0].lower()):
            rel = _quote_path(posixpath.relpath(n_src, posixpath.dirname(src) or '.'))
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
            and not notes.get(f.src_uri, {}).get('unlisted', False)
        ]
        extra.sort(key=lambda f: notes.get(f.src_uri, {}).get('title', f.src_uri).lower())
        for f in extra:
            f.page.parent = section
            section.children.append(f.page)

    def remove_unlisted(items):
        visible = []
        for item in items:
            if getattr(item, 'is_page', False) and (
                notes.get(item.file.src_uri, {}).get('unlisted', False)
                or notes.get(item.file.src_uri, {}).get('draft', False)
            ):
                continue
            if getattr(item, 'is_section', False):
                item.children[:] = remove_unlisted(item.children)
                if not item.children:
                    continue
            visible.append(item)
        return visible

    nav.items[:] = remove_unlisted(nav.items)
    return nav


def _stage_index(src, stage):
    items = sorted(
        ((n['title'], s, n['excerpt']) for s, n in notes.items() if n['stage'] == stage and _is_listed(n)),
        key=lambda x: x[0].lower(),
    )
    if not items:
        return '\n\n*nothing planted here yet.*\n'
    out = ['\n\n']
    for title, s, excerpt in items:
        rel = _quote_path(posixpath.relpath(s, posixpath.dirname(src) or '.'))
        line = '- [%s](%s)' % (_esc(title), rel)
        if excerpt:
            line += ' \u2014 ' + html.escape(excerpt).replace('[', '\\[').replace(']', '\\]')
        out.append(line + '\n')
    return ''.join(out)


def _related(src, limit=3):
    me = notes[src]
    mine = {t.lower() for t in me['tags']}
    others = [n for s, n in notes.items() if s != src and _is_listed(n) and n['stage']]
    scored = []
    for n in others:
        count = len(mine & {t.lower() for t in n['tags']})
        if count:
            scored.append((count, str(n['tended']), n))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    picks = [x[2] for x in scored[:limit]]
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
    page.meta['garden_discussion_enabled'] = src not in {'index.md', 'about.md'}
    page.meta.setdefault('garden_section', src.split('/')[0] if '/' in src else 'home')
    if n and not n['is_index']:
        if n['stage']:
            page.meta.setdefault('stage', n['stage'])
        page.meta.setdefault('tended', str(n['tended'])[:10])
        if n['planted']:
            page.meta.setdefault('planted', str(n['planted'])[:10])
    return markdown


def on_page_context(context, page, config, nav):
    src = page.file.src_uri
    n = notes.get(src)
    is_note = bool(n and not n['is_index'])
    listed = [note for note in notes.values() if _is_listed(note)]
    stages = (
        ('seedling', 'seedlings'),
        ('bud', 'buds'),
        ('evergreen', 'evergreens'),
    )
    context['garden_stage_stats'] = [
        {
            'stage': stage,
            'label': label,
            'count': sum(1 for note in listed if note['stage'] == stage),
        }
        for stage, label in stages
    ]
    context['garden_note_total'] = len(listed)
    context['garden_recent'] = sorted(
        listed,
        key=lambda note: str(note['tended']),
        reverse=True,
    )[:6]
    context['backlinks'] = backlinks.get(src, [])
    context['outgoing'] = outgoing.get(src, [])
    context['slug'] = slugify
    context['description'] = n['excerpt'] if is_note else ''
    context['related'] = _related(src) if is_note else []
    context['history'] = n.get('history', []) if is_note else []
    return context


def _json_default(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    return str(o)


def _feed_timestamp(value):
    if isinstance(value, datetime):
        return value.isoformat() + ('Z' if value.tzinfo is None else '')
    if isinstance(value, date):
        return value.isoformat() + 'T00:00:00Z'
    try:
        return date.fromisoformat(str(value)[:10]).isoformat() + 'T00:00:00Z'
    except ValueError:
        return datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def _write_feed(config, site_dir):
    ElementTree.register_namespace('', ATOM_NS)
    root = ElementTree.Element('{%s}feed' % ATOM_NS, {'{http://www.w3.org/XML/1998/namespace}lang': 'en'})
    ElementTree.SubElement(root, '{%s}title' % ATOM_NS).text = config['site_name']
    ElementTree.SubElement(root, '{%s}id' % ATOM_NS).text = config['site_url']
    ElementTree.SubElement(root, '{%s}link' % ATOM_NS, {'href': config['site_url']})
    published = [n['tended'] for n in notes.values() if _is_listed(n)]
    updated = max(published, key=lambda value: str(value)) if published else date.today()
    ElementTree.SubElement(root, '{%s}updated' % ATOM_NS).text = _feed_timestamp(updated)
    entries = sorted(
        ((n['tended'], n) for n in notes.values() if _is_listed(n)),
        key=lambda item: str(item[0]),
        reverse=True,
    )
    for _, note in entries:
        url = urljoin(config['site_url'].rstrip('/') + '/', quote(note['url'], safe='/'))
        entry = ElementTree.SubElement(root, '{%s}entry' % ATOM_NS)
        ElementTree.SubElement(entry, '{%s}title' % ATOM_NS).text = note['title']
        ElementTree.SubElement(entry, '{%s}id' % ATOM_NS).text = url
        ElementTree.SubElement(entry, '{%s}link' % ATOM_NS, {'href': url})
        ElementTree.SubElement(entry, '{%s}updated' % ATOM_NS).text = _feed_timestamp(note['tended'])
        ElementTree.SubElement(entry, '{%s}summary' % ATOM_NS, {'type': 'text'}).text = note['excerpt']
    tree = ElementTree.ElementTree(root)
    tree.write(os.path.join(site_dir, 'feed.xml'), encoding='utf-8', xml_declaration=True)


def _write_aliases(config, site_dir):
    base_url = config['site_url'].rstrip('/') + '/'
    for note in notes.values():
        if not _is_listed(note):
            continue
        destination = urljoin(base_url, quote(note['url'], safe='/'))
        for alias in note.get('aliases', []):
            path = alias.strip().replace('\\', '/').strip('/')
            normalized = posixpath.normpath(path)
            if (
                not path or ':' in path or normalized.startswith('/')
                or any(part in {'.', '..'} for part in path.split('/'))
            ):
                _warn('ignoring unsafe alias %r for %s' % (alias, note['title']))
                continue
            relative = normalized + '/index.html' if not normalized.endswith('.html') else normalized
            output = os.path.join(site_dir, *relative.split('/'))
            if os.path.exists(output):
                _warn('alias %r for %s conflicts with an existing page' % (alias, note['title']))
                continue
            os.makedirs(os.path.dirname(output), exist_ok=True)
            safe_destination = html.escape(destination, quote=True)
            page = (
                '<!doctype html><html lang="en"><meta charset="utf-8">'
                '<meta http-equiv="refresh" content="0;url=%s">'
                '<link rel="canonical" href="%s"><title>note moved</title>'
                '<a href="%s">continue to %s</a></html>'
            ) % (safe_destination, safe_destination, safe_destination, html.escape(note['title']))
            with open(output, 'w', encoding='utf-8') as stream:
                stream.write(page)


def _write_graph(site_dir):
    nodes = [
        {'id': src, 'title': note['title'], 'url': note['url'], 'stage': note['stage']}
        for src, note in notes.items()
        if _is_listed(note)
    ]
    by_url = {note['url']: src for src, note in notes.items() if _is_listed(note)}
    edges = []
    for src, links in outgoing.items():
        if src not in notes or not _is_listed(notes[src]):
            continue
        for link in links:
            target = by_url.get(link['url'])
            if target:
                edges.append({'source': src, 'target': target})
    with open(os.path.join(site_dir, 'graph.json'), 'w', encoding='utf-8') as stream:
        json.dump({'nodes': nodes, 'edges': edges}, stream, ensure_ascii=False)

    graph_page = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>garden graph</title>
<script>
(function(){
  var saved=null;
  try{saved=localStorage.getItem('theme');}catch(error){}
  document.documentElement.dataset.theme=saved||(
    matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'
  );
})();
</script>
<style>
:root{color-scheme:light;--bg:#f8f6f1;--surface:#fff;--text:#26252a;--link:#334e80;--border:#c8c4bc;--line:#a8a4ad;--node:#e2c6e7;--node-border:#56466a;--focus:#c34860;--accent:#c87eb9;--on-accent:#262b40;--ui-border:#80798a}
:root[data-theme="dark"]{color-scheme:dark;--bg:#262b40;--surface:#1d2234;--text:#c6ceef;--link:#a0cdf3;--border:#62677e;--line:#8b92b3;--node:#a68bc0;--node-border:#c6ceef;--focus:#e96882;--ui-border:#8b92b3}
*{cursor:url('assets/garden-cursor.svg') 1 1,auto}
body{margin:0;padding:2rem;font:16px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--text);transition:background .2s,color .2s}
a{color:var(--link)}main{max-width:70rem;margin:auto}
button,.graph-button{display:inline-block;font:inherit;font-weight:600;padding:.45rem 1rem;border:3px solid var(--ui-border);border-radius:16px;background:var(--bg);color:var(--text);text-decoration:none;transition:background .15s,border-color .15s}
button:hover,.graph-button:hover{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
.graph-controls{display:flex;align-items:center;justify-content:space-between;gap:1rem}
svg{width:100%;height:auto;min-height:24rem;border:1px solid var(--border);border-radius:1rem;background:var(--surface)}
line{stroke:var(--line);stroke-width:1.5}#arrowhead{fill:var(--line)}
circle{fill:var(--node);stroke:var(--node-border);stroke-width:2}
text{font:14px system-ui,sans-serif;fill:var(--text);text-anchor:middle}a:focus circle{stroke:var(--focus);stroke-width:4}
.empty{padding:1rem;background:var(--surface);border-radius:.75rem}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.discussion-drawer{position:fixed;z-index:5;top:0;right:0;width:min(20rem,85vw);height:100vh;height:100dvh;transform:translateX(100%);transition:transform .3s cubic-bezier(.4,0,.2,1)}
.discussion-drawer.open{transform:translateX(0)}
.discussion-panel{box-sizing:border-box;height:100%;padding:2rem 1rem;overflow-y:auto;background:var(--surface);border-left:1px solid var(--border);overflow-wrap:anywhere}
.discussion-toggle{position:absolute;top:50%;left:-2.5rem;width:2.5rem;height:3.5rem;transform:translateY(-50%);padding:0;border-right:0;border-radius:12px 0 0 12px;cursor:pointer}
</style>
<main><div class="graph-controls"><a class="graph-button" href="./">back to the garden</a><button id="theme-toggle" type="button" aria-pressed="false"><span aria-hidden="true">🎨</span> style<span class="sr-only"> dark mode</span></button></div><h1>garden graph</h1>
<p>Notes are arranged around the circle; arrows show outgoing links.</p>
<p id="status" role="status">loading the garden graph…</p>
<svg id="graph" viewBox="0 0 1000 700" role="group" aria-label="Garden notes and links"></svg></main>
<aside class="discussion-drawer" id="discussion-drawer">
<button class="discussion-toggle" id="discussion-toggle" type="button" aria-expanded="false" aria-controls="discussion-panel" aria-label="discussion" title="discussion"><span aria-hidden="true">💬</span><span class="sr-only">discussion</span></button>
<section class="discussion-panel" id="discussion-panel" aria-labelledby="discussion-heading" aria-hidden="true" inert>
<h2 id="discussion-heading">discussion</h2>
<script src="https://giscus.app/client.js"
        data-repo="truly-tranquil/digital-garden"
        data-repo-id="R_kgDOVpqNfQ"
        data-category-id="DIC_kwDOVpqNfc4DK1EY"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="catppuccin_mocha"
        data-lang="en"
        crossorigin="anonymous"
        async>
</script>
</section>
</aside>
<script>
var discussionDrawer=document.getElementById('discussion-drawer');
var discussionToggle=document.getElementById('discussion-toggle');
var discussionPanel=document.getElementById('discussion-panel');
discussionToggle.addEventListener('click',function(){
  var open=discussionDrawer.classList.toggle('open');
  discussionToggle.setAttribute('aria-expanded',String(open));
  discussionPanel.setAttribute('aria-hidden',String(!open));
  if(open)discussionPanel.removeAttribute('inert');else discussionPanel.setAttribute('inert','');
});
document.addEventListener('keydown',function(event){
  if(event.key!=='Escape'||!discussionDrawer.classList.contains('open'))return;
  discussionDrawer.classList.remove('open');
  discussionToggle.setAttribute('aria-expanded','false');
  discussionPanel.setAttribute('aria-hidden','true');
  discussionPanel.setAttribute('inert','');
  discussionToggle.focus();
});
</script>
<script>
var themeToggle=document.getElementById('theme-toggle');
function setGraphTheme(theme){
  document.documentElement.dataset.theme=theme;
  themeToggle.setAttribute('aria-pressed',String(theme==='dark'));
}
setGraphTheme(document.documentElement.dataset.theme);
themeToggle.addEventListener('click',function(){
  var theme=document.documentElement.dataset.theme==='dark'?'light':'dark';
  setGraphTheme(theme);
  try{localStorage.setItem('theme',theme);}catch(error){}
});
var systemTheme=matchMedia('(prefers-color-scheme: dark)');
systemTheme.addEventListener('change',function(event){
  var saved=null;
  try{saved=localStorage.getItem('theme');}catch(error){}
  if(!saved)setGraphTheme(event.matches?'dark':'light');
});
fetch('graph.json').then(function(response){if(!response.ok)throw new Error('Graph data unavailable');return response.json();})
.then(function(data){
  var svg=document.getElementById('graph'),status=document.getElementById('status'),ns='http://www.w3.org/2000/svg';
  var nodes=data.nodes||[],edges=data.edges||[],positions={};
  if(!nodes.length){status.textContent='No listed notes to graph yet.';return;}
  var defs=document.createElementNS(ns,'defs'),marker=document.createElementNS(ns,'marker'),arrow=document.createElementNS(ns,'path');
  marker.setAttribute('id','arrow');marker.setAttribute('viewBox','0 0 10 10');marker.setAttribute('refX','9');marker.setAttribute('refY','5');
  marker.setAttribute('markerWidth','6');marker.setAttribute('markerHeight','6');marker.setAttribute('orient','auto-start-reverse');
  arrow.setAttribute('id','arrowhead');arrow.setAttribute('d','M 0 0 L 10 5 L 0 10 z');marker.appendChild(arrow);defs.appendChild(marker);svg.appendChild(defs);
  nodes.forEach(function(node,index){
    var angle=(2*Math.PI*index/nodes.length)-Math.PI/2;
    positions[node.id]={x:500+Math.cos(angle)*360,y:350+Math.sin(angle)*260};
  });
  edges.forEach(function(edge){
    var from=positions[edge.source],to=positions[edge.target];if(!from||!to)return;
    var line=document.createElementNS(ns,'line');line.setAttribute('x1',from.x);line.setAttribute('y1',from.y);
    line.setAttribute('x2',to.x);line.setAttribute('y2',to.y);line.setAttribute('marker-end','url(#arrow)');svg.appendChild(line);
  });
  nodes.forEach(function(node){
    var point=positions[node.id],group=document.createElementNS(ns,'g'),link=document.createElementNS(ns,'a');
    link.setAttribute('href',node.url);link.setAttribute('aria-label',node.title);
    var circle=document.createElementNS(ns,'circle');circle.setAttribute('cx',point.x);circle.setAttribute('cy',point.y);circle.setAttribute('r',11);
    var text=document.createElementNS(ns,'text');text.setAttribute('x',point.x);text.setAttribute('y',point.y+30);text.textContent=node.title;
    link.appendChild(circle);link.appendChild(text);group.appendChild(link);svg.appendChild(group);
  });
  status.textContent=nodes.length+' notes · '+edges.length+' links';
}).catch(function(){document.getElementById('status').textContent='The garden graph could not be loaded.';});
</script></html>"""
    with open(os.path.join(site_dir, 'graph.html'), 'w', encoding='utf-8') as stream:
        stream.write(graph_page)


def _write_suggestions(site_dir):
    suggestions = [
        {'title': note['title'], 'url': note['url']}
        for note in notes.values()
        if _is_listed(note)
    ]
    with open(os.path.join(site_dir, 'suggestions.json'), 'w', encoding='utf-8') as stream:
        json.dump(suggestions, stream, ensure_ascii=False)


def on_post_build(config):
    out = [
        {k: v for k, v in n.items() if not k.startswith('_')}
        for n in notes.values()
        if _is_public(n)
    ]
    with open(os.path.join(config['site_dir'], 'notes.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, default=_json_default, ensure_ascii=False)
    _write_feed(config, config['site_dir'])
    _write_aliases(config, config['site_dir'])
    _write_graph(config['site_dir'])
    _write_suggestions(config['site_dir'])
    sitemap = urljoin(config['site_url'].rstrip('/') + '/', 'sitemap.xml')
    with open(os.path.join(config['site_dir'], 'robots.txt'), 'w', encoding='utf-8') as fh:
        fh.write('User-agent: *\nAllow: /\nSitemap: %s\n' % sitemap)