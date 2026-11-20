"""Jinja template rendering for pages, the graph and the 404."""

import math
import os
import re
from typing import Any

from jinja2 import Environment, FileSystemLoader

from garden.dates import relative_day
from garden.garden_state import notes
from garden.utils.assets import og_image_url
from garden.utils.graph import graph_text
from garden.utils.renderer.markdown import render_html

STAGE_FOLDER = {'seedling': 'seedlings', 'bud': 'buds', 'evergreen': 'evergreens'}

_TAG = re.compile(r'<[^>]+>')
_WS = re.compile(r'\s+')


def reading_minutes(html_body):
    """Estimated reading time in whole minutes (200 wpm), 0 when there is no text."""
    text = _TAG.sub(' ', html_body)
    words = len(_WS.split(text.strip()))
    return math.ceil(words / 200) if words else 0


_ENVS: dict[str, Environment] = {}


def _env(theme_dir):
    env = _ENVS.get(theme_dir)
    if env is None:
        env = Environment(
            loader=FileSystemLoader(os.path.join(theme_dir, 'templates')),
            autoescape=True,
        )
        _ENVS[theme_dir] = env
    return env


def _seo(config, title, description, url, og_type='website', image=''):
    site = (config.get('site') or {}) if isinstance(config, dict) else {}
    site_url = site.get('url', '').rstrip('/')
    return {
        'title': title,
        'description': description,
        'og_title': title,
        'og_description': description,
        'og_type': og_type,
        'og_image': image or og_image_url(config),
        'canonical_url': '%s/%s' % (site_url, url) if site_url else '',
    }


def render_page(
    note,
    text,
    src,
    ctx,
    config,
    theme_dir="my-garden-theme",
    nav_notes=None,
    index_dirs=(),
    tag_slugs=None,
):
    html_body, toc_html = render_html(text, src)
    is_home = src == 'index.md'
    tags = [
        dict(tag, linked=tag_slugs is None or tag['slug'] in tag_slugs)
        for tag in note['tag_entries']
    ]
    site_cfg = (config.get('site') or {}) if isinstance(config, dict) else {}

    template = _env(theme_dir).get_template('page.html')
    rendered = template.render(
        title=note['title'],
        show_title='<h1' not in html_body,
        description=ctx.get('description', ''),
        og_title=ctx.get('og_title', ''),
        og_description=ctx.get('og_description', ''),
        og_type=ctx.get('og_type', 'website'),
        og_image=ctx.get('og_image', ''),
        canonical_url=ctx.get('canonical_url', ''),
        base_url='',
        page_url=ctx.get('page_url', ''),
        page_src=ctx.get('page_src', ''),
        stage=note['stage'],
        stage_folder=STAGE_FOLDER.get(note['stage'], ''),
        tags=tags,
        planted=str(note['planted'])[:10] if note['planted'] else '',
        tended=str(note['tended'])[:10] if note['tended'] else '',
        tended_rel=relative_day(note['tended']) if note['tended'] else '',
        reading_minutes=reading_minutes(html_body),
        content=html_body,
        toc=toc_html,
        config=config,
        site_cfg=site_cfg,
        nav_notes=nav_notes or [],
        home=is_home,
        stats=ctx.get('garden_stage_stats', []),
        total=ctx.get('garden_note_total', 0),
    )
    # Add a home class to the <article> element when on the home page,
    # so we can center its text independently from other pages.
    if is_home:
        rendered = rendered.replace(
            '<article class="garden-article"',
            '<article class="garden-article home"',
        )
    return rendered


def render_graph(config, theme_dir="my-garden-theme", nav_notes=None, graph=None):
    template = _env(theme_dir).get_template('graph.html')
    site_url = config.get('site', {}).get('url', '')
    site_title = config.get('site', {}).get('title', '')
    site_desc = config.get('site', {}).get('description', '')
    tags_by_slug: dict[str, dict[str, Any]] = {}
    for note in notes.values():
        for tag in note.get('tag_entries') or []:
            entry = tags_by_slug.setdefault(
                tag['slug'], {'name': tag['name'], 'slug': tag['slug'], 'count': 0}
            )
            entry['count'] = int(entry['count']) + 1
    tags = sorted(tags_by_slug.values(), key=lambda item: str(item['name']).casefold())
    return template.render(
        title='garden graph',
        toc='',
        config=config,
        nav_notes=nav_notes or [],
        description=site_desc,
        og_title=f"garden graph - {site_title}",
        og_description=site_desc,
        og_type='website',
        og_image=og_image_url(config),
        canonical_url=f"{site_url.rstrip('/')}/graph.html",
        base_url='',
        graph_view=graph_text(graph),
        graph_tags=tags,
    )


def render_404(config, theme_dir="my-garden-theme", nav_notes=None):
    template = _env(theme_dir).get_template('404.html')
    site_url = config.get('site', {}).get('url', '')
    site_title = config.get('site', {}).get('title', '')
    stages = [
        {'stage': stage, 'label': label, 'url': '/%s/index.html' % folder}
        for stage, folder, label in (
            ('seedling', 'seedlings', 'seedlings'),
            ('bud', 'buds', 'buds'),
            ('evergreen', 'evergreens', 'evergreens'),
        )
    ]
    return template.render(
        title='not found',
        toc='',
        config=config,
        nav_notes=nav_notes or [],
        description='page not found',
        og_title=f"not found - {site_title}",
        og_description='page not found',
        og_type='website',
        og_image=og_image_url(config),
        canonical_url=f"{site_url.rstrip('/')}/404.html",
        base_url='',
        random_stages=stages,
        graph_url='/graph.html',
    )
