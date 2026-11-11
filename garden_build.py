"""Prepare garden content and run Zensical without MkDocs build hooks."""
import argparse
import fnmatch
import json
import os
import posixpath
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

import hooks


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / 'docs'
BUILD_DIR = ROOT / '.garden-build'
GENERATED_DOCS = BUILD_DIR / 'docs'
GENERATED_CONFIG = ROOT / '.garden-zensical.yml'
CONFIG_FILE = ROOT / 'mkdocs.yml'
SITE_DIR = ROOT / 'site'
PREVIEW_DIR = ROOT / '.garden-preview'


class GardenFile:
    def __init__(self, src_uri):
        self.src_uri = src_uri
        self.abs_src_path = str(SOURCE_DIR.joinpath(*src_uri.split('/')))
        self.url = _page_url(src_uri)

    def is_documentation_page(self):
        return self.src_uri.lower().endswith('.md')


class GardenFiles(list):
    def documentation_pages(self):
        return [file for file in self if file.is_documentation_page()]


class GardenPage:
    def __init__(self, file, meta):
        self.file = file
        self.meta = meta


def _page_url(src_uri):
    stem, extension = posixpath.splitext(src_uri)
    if extension.lower() != '.md':
        return src_uri
    if posixpath.basename(stem) == 'index':
        return posixpath.dirname(stem) + ('/' if posixpath.dirname(stem) else '')
    return stem + '/'


def _excluded(src_uri, patterns):
    path = src_uri.strip('/')
    prefixes = [path]
    parts = path.split('/')
    prefixes.extend('/'.join(parts[:index]) + '/' for index in range(1, len(parts)))
    for pattern in patterns:
        normalized = pattern.strip().replace('\\', '/')
        alternatives = [normalized]
        if normalized.startswith('**/'):
            alternatives.append(normalized[3:])
        if any(
            fnmatch.fnmatchcase(candidate, alternative)
            for candidate in prefixes
            for alternative in alternatives
        ):
            return True
    return False


def _source_files(patterns):
    for root, dirs, filenames in os.walk(SOURCE_DIR):
        relative_root = Path(root).relative_to(SOURCE_DIR).as_posix()
        dirs[:] = [
            name for name in dirs
            if not _excluded(
                (relative_root + '/' if relative_root != '.' else '') + name + '/',
                patterns,
            )
        ]
        for filename in filenames:
            path = Path(root, filename)
            src_uri = path.relative_to(SOURCE_DIR).as_posix()
            if not _excluded(src_uri, patterns):
                yield src_uri


def _frontmatter(source):
    match = hooks.FRONT.match(source)
    if not match:
        return {}, source
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError('Front matter must be a mapping')
    return metadata, source[match.end():]


def _nav_paths(items):
    for item in items or []:
        if isinstance(item, dict):
            for title, child in item.items():
                if isinstance(child, str):
                    yield title, child
                elif isinstance(child, list):
                    yield from _nav_paths(child)


def _filter_nav(items):
    filtered = []
    for item in items:
        if not isinstance(item, dict):
            filtered.append(item)
            continue
        title, child = next(iter(item.items()))
        if isinstance(child, str):
            note = hooks.notes.get(child)
            if note and (note['unlisted'] or note['draft']):
                continue
            filtered.append(item)
        elif isinstance(child, list):
            children = _filter_nav(child)
            if children:
                filtered.append({title: children})
    return filtered


def _prepare_nav(nav):
    if not isinstance(nav, list):
        return nav
    existing = {path for _, path in _nav_paths(nav)}
    for section in nav:
        if not isinstance(section, dict):
            continue
        title, children = next(iter(section.items()))
        folder = str(title).lower()
        if folder not in hooks.STAGE_BY_FOLDER or not isinstance(children, list):
            continue
        additional = [
            (note['title'], src)
            for src, note in hooks.notes.items()
            if src.startswith(folder + '/')
            and src not in existing
            and not note['unlisted']
            and not note['draft']
            and not note['is_index']
        ]
        children.extend(
            {title: src}
            for title, src in sorted(additional, key=lambda item: item[0].lower())
        )
    return _filter_nav(nav)


def _garden_metadata(src_uri, page):
    note = hooks.notes[src_uri]
    context = hooks.on_page_context({}, page, {}, None)
    page.meta.update({
        'title': note['title'],
        'garden_tag_slugs': note['tag_slugs'],
        'garden_outgoing': context['outgoing'],
        'garden_backlinks': context['backlinks'],
        'garden_related': context['related'],
        'garden_history': context['history'],
        'garden_description': context['description'],
        'garden_stage_stats': context['garden_stage_stats'],
        'garden_note_total': context['garden_note_total'],
        'garden_recent': [
            {
                'title': note['title'],
                'url': note['url'],
                'tended': str(note['tended'])[:10],
            }
            for note in context['garden_recent']
        ],
        'garden_section': note['section'],
        'garden_homepage': src_uri == 'index.md',
    })


def _copy_sources(files, transformed):
    if GENERATED_DOCS.exists():
        shutil.rmtree(GENERATED_DOCS)
    GENERATED_DOCS.mkdir(parents=True)
    for file in files:
        source = Path(file.abs_src_path)
        target = GENERATED_DOCS.joinpath(*file.src_uri.split('/'))
        if file.is_documentation_page():
            if file.src_uri not in transformed:
                continue
            metadata, body = transformed[file.src_uri]
            target.parent.mkdir(parents=True, exist_ok=True)
            serialized = yaml.safe_dump(
                metadata,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
            )
            target.write_text('---\n' + serialized + '---\n\n' + body, encoding='utf-8')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def prepare(serving=False):
    with CONFIG_FILE.open(encoding='utf-8') as stream:
        config = yaml.safe_load(stream)
    patterns = [
        line.strip()
        for line in str(config.get('exclude_docs', '')).splitlines()
        if line.strip()
    ]
    files = GardenFiles(GardenFile(src) for src in _source_files(patterns))
    hooks.serving = serving
    hooks.on_files(files, {'config_file_path': str(CONFIG_FILE)})

    transformed = {}
    for file in files.documentation_pages():
        source = Path(file.abs_src_path).read_text(encoding='utf-8')
        metadata, body = _frontmatter(source)
        page = GardenPage(file, metadata)
        body = hooks.on_page_markdown(body, page, config, files)
        _garden_metadata(file.src_uri, page)
        transformed[file.src_uri] = (metadata, body)

    _copy_sources(files, transformed)
    generated_config = dict(config)
    generated_config['docs_dir'] = GENERATED_DOCS.relative_to(ROOT).as_posix()
    site_dir = PREVIEW_DIR if serving else SITE_DIR
    generated_config['site_dir'] = site_dir.relative_to(ROOT).as_posix()
    generated_config['nav'] = _prepare_nav(config.get('nav'))
    generated_config['draft_docs'] = '\n'.join(
        '/' + src for src, note in hooks.notes.items() if note.get('unlisted', False)
    )
    theme = dict(generated_config.get('theme') or {})
    theme.pop('name', None)
    theme.pop('static_templates', None)
    generated_config['theme'] = theme
    generated_config.pop('hooks', None)
    with GENERATED_CONFIG.open('w', encoding='utf-8', newline='\n') as stream:
        yaml.safe_dump(generated_config, stream, sort_keys=False, allow_unicode=True)
    return config


def _write_generated_assets(config, output_dir=None):
    output_dir = output_dir or SITE_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    hooks.on_post_build({
        'site_dir': str(output_dir),
        'site_name': config['site_name'],
        'site_url': config['site_url'],
    })
    _write_search_index(output_dir)


def _write_preview_assets(config, output_dir=None):
    output_dir = output_dir or SITE_DIR
    GENERATED_DOCS.mkdir(parents=True, exist_ok=True)
    hooks.on_post_build({
        'site_dir': str(GENERATED_DOCS),
        'site_name': config['site_name'],
        'site_url': config['site_url'],
    })
    source = output_dir / 'search' / 'search_index.json'
    target = GENERATED_DOCS / 'search' / 'search_index.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _write_search_index(output_dir=None):
    output_dir = output_dir or SITE_DIR
    source = output_dir / 'search.json'
    if not source.is_file():
        raise RuntimeError('Zensical did not generate search.json')
    data = json.loads(source.read_text(encoding='utf-8'))
    items = data.get('items') if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise RuntimeError('Zensical search.json has an unsupported format')

    hidden_urls = {
        note['url']
        for note in hooks.notes.values()
        if note['url'] and (note['unlisted'] or note['draft'])
    }
    visible_items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        location = str(item.get('location') or '')
        page_url = location.split('#', 1)[0]
        if any(page_url == url or page_url.startswith(url) for url in hidden_urls):
            continue
        visible_items.append(item)
    data['items'] = visible_items
    source.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    docs = [
        {
            'title': str(item.get('title') or ''),
            'text': str(item.get('text') or ''),
            'location': str(item.get('location') or ''),
        }
        for item in visible_items
    ]
    target = output_dir / 'search' / 'search_index.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({'docs': docs}, ensure_ascii=False),
        encoding='utf-8',
    )


def _zensical_command(action):
    return [
        sys.executable,
        '-m',
        'zensical',
        action,
        '--config-file',
        str(GENERATED_CONFIG),
    ]


def build():
    config = prepare()
    subprocess.run(_zensical_command('build') + ['--strict'], cwd=ROOT, check=True)
    _write_generated_assets(config)


def _snapshot():
    snapshot = {}
    for folder in (SOURCE_DIR, ROOT / 'my-garden-theme'):
        for path in folder.rglob('*'):
            if path.is_file():
                stat = path.stat()
                snapshot[path] = (stat.st_mtime_ns, stat.st_size)
    snapshot[CONFIG_FILE] = (
        CONFIG_FILE.stat().st_mtime_ns,
        CONFIG_FILE.stat().st_size,
    )
    return snapshot


def serve(dev_addr='localhost:8000'):
    config = prepare(serving=True)
    subprocess.run(_zensical_command('build'), cwd=ROOT, check=True)
    _write_generated_assets(config, PREVIEW_DIR)
    _write_preview_assets(config, PREVIEW_DIR)
    process = subprocess.Popen(
        _zensical_command('serve') + ['--dev-addr', dev_addr],
        cwd=ROOT,
    )
    search_path = SITE_DIR / 'search.json'
    deadline = time.monotonic() + 10
    while not search_path.exists():
        if process.poll() is not None:
            return process.wait()
        if time.monotonic() >= deadline:
            process.terminate()
            process.wait()
            raise RuntimeError('Zensical preview did not create site/search.json')
        time.sleep(0.1)
    search_mtime = search_path.stat().st_mtime_ns
    snapshot = _snapshot()
    try:
        while process.poll() is None:
            time.sleep(0.5)
            current = _snapshot()
            if current != snapshot:
                config = prepare(serving=True)
                _write_generated_assets(config, PREVIEW_DIR)
                _write_preview_assets(config, PREVIEW_DIR)
                snapshot = current
            if search_path.exists():
                current_search_mtime = search_path.stat().st_mtime_ns
                if current_search_mtime != search_mtime:
                    _write_search_index()
                    search_mtime = current_search_mtime
    except KeyboardInterrupt:
        process.terminate()
        return process.wait()
    return process.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('build', 'serve'))
    parser.add_argument(
        '--dev-addr',
        default='localhost:8000',
        help='preview address for serve (default: localhost:8000)',
    )
    args = parser.parse_args()
    try:
        if args.action == 'build':
            build()
            return 0
        return serve(args.dev_addr)
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as exc:
        print('Garden build failed: %s' % exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
