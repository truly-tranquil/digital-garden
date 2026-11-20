import functools
import http.server
import json
import os
import posixpath
import re
import shutil
import sys
import tempfile

import yaml

from garden.garden_state import referenced_media
from garden.notes import is_listed
from garden.output import listed_tag_slugs, write_site_files
from garden.utils import garden
from garden.utils.assets import (
    OG_IMAGE_HEIGHT,
    OG_IMAGE_WIDTH,
    copy_referenced_media,
    copy_static_assets,
)
from garden.utils.graph import build_graph, with_base
from garden.utils.images import responsive_images
from garden.utils.nav import build_nav
from garden.utils.renderer import render_404, render_graph, render_page


def copy_theme_static(theme_dir="my-garden-theme", dist_dir="dist"):
    static_dir = os.path.join(theme_dir, "static")
    if not os.path.exists(static_dir):
        return
    for root, _, files in os.walk(static_dir):
        for file in files:
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(src_file, static_dir)
            dist_file = os.path.join(dist_dir, rel_path)
            os.makedirs(os.path.dirname(dist_file), exist_ok=True)
            shutil.copy2(src_file, dist_file)


_ATTR_URL = re.compile(r"""(?<![\w-])(href|src)=(['"])(/(?!/)[^'"]*)\2""", re.I)
_SRCSET = re.compile(r"""(?<![\w-])(srcset)=(['"])([^'"]*)\2""", re.I)
_CONTENT = re.compile(r"""(?<![\w-])(content)=(['"])([^""]*)\2""", re.I)
_CONTENT_REFRESH = re.compile(r"""(url=)(/(?!/)[^\s"'>]*)""", re.I)
_CODE_REGION = re.compile(r'(<pre\b[^>]*>.*?</pre>|<code\b[^>]*>.*?</code>)', re.I | re.S)


def _rebase_url(url, base):
    """Prefix a single root-relative URL with ``base``, leaving others alone."""
    if url.startswith("/") and not url.startswith("//"):
        return base + url
    return url


def _rebase_srcset(match, base):
    attr, quote, value = match.group(1), match.group(2), match.group(3)
    parts = []
    for candidate in value.split(","):
        stripped = candidate.strip()
        parts.append(_rebase_url(stripped, base) if stripped else candidate)
    return "%s=%s%s%s" % (attr, quote, ", ".join(parts), quote)


def _rebase_content(match, base):
    attr, quote, value = match.group(1), match.group(2), match.group(3)
    value = _CONTENT_REFRESH.sub(lambda m: m.group(1) + _rebase_url(m.group(2), base), value)
    value = _rebase_url(value, base)
    return "%s=%s%s%s" % (attr, quote, value, quote)


def rebase(html_text, base):
    """Prefix root-relative URLs with the base path (for project sites).

    Handles ``href``/``src`` (single- or double-quoted), comma-separated
    ``srcset`` candidates and ``content=`` URLs (e.g. ``og:image`` or
    ``<meta http-equiv="refresh" content="0; url=/...">``). External and
    protocol-relative URLs are left untouched.
    """
    base = (base or "").rstrip("/")
    if not base:
        return html_text

    def rewrite(chunk):
        chunk = _ATTR_URL.sub(
            lambda m: "%s=%s%s%s" % (m.group(1), m.group(2), base + m.group(3), m.group(2)),
            chunk,
        )
        chunk = _SRCSET.sub(lambda m: _rebase_srcset(m, base), chunk)
        return _CONTENT.sub(lambda m: _rebase_content(m, base), chunk)

    parts = _CODE_REGION.split(html_text)
    for index in range(0, len(parts), 2):
        parts[index] = rewrite(parts[index])
    return "".join(parts)


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def build_garden(dist_dir=None):
    with open("garden.yml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    docs_dir = config["paths"]["source"]
    dist_dir = dist_dir or config["paths"]["output"]
    config.setdefault("og_image_width", OG_IMAGE_WIDTH)
    config.setdefault("og_image_height", OG_IMAGE_HEIGHT)
    target_dir = os.path.abspath(dist_dir)
    parent_dir = os.path.dirname(target_dir) or "."
    os.makedirs(parent_dir, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix="garden_dist_", dir=parent_dir)
    try:
        base = os.environ.get("GARDEN_BASE_PATH", "").rstrip("/")

        notes = garden.load(docs_dir)

        nav_notes = build_nav(notes)
        tag_slugs = listed_tag_slugs()
        index_dirs = {
            posixpath.dirname(s) for s, n in notes.items() if n["is_index"] and posixpath.dirname(s)
        }

        for src, note in notes.items():
            if note["draft"]:
                continue

            html_out = render_page(
                note,
                garden.markdown_for(src),
                src,
                garden.context_for(src, config),
                config,
                nav_notes=nav_notes,
                index_dirs=index_dirs,
                tag_slugs=tag_slugs,
            )
            html_out = responsive_images(html_out, src, docs_dir, temp_dir)
            write(os.path.join(temp_dir, src[:-3] + ".html"), rebase(html_out, base))

        # --- Copy static assets ---
        copy_static_assets(f"{docs_dir}/assets", f"{temp_dir}/assets")
        copy_referenced_media(docs_dir, temp_dir, referenced_media)
        copy_theme_static("my-garden-theme", temp_dir)

        # --- Graph ---
        graph = build_graph(notes, "")
        write(
            os.path.join(temp_dir, "graph.json"),
            json.dumps(with_base(graph, base), ensure_ascii=False),
        )
        write(
            os.path.join(temp_dir, "graph.html"),
            rebase(render_graph(config, nav_notes=nav_notes, graph=graph), base),
        )

        # --- Search Index ---
        search_entries = []
        for src, n in notes.items():
            if n.get("draft"):
                continue
            # URL should be rebased with base prefix
            url = _rebase_url("/" + src[:-3] + ".html", base)
            search_entries.append(
                {
                    "title": n.get("title", ""),
                    "url": url,
                    "stage": n.get("stage"),
                    "tags": n.get("tags") or [],
                    "excerpt": n.get("excerpt", ""),
                    "text": n.get("_body", ""),
                    "listed": is_listed(n),
                    "random": n.get("random", True),
                    "icon": n.get("icon"),
                }
            )
        write(
            os.path.join(temp_dir, "search-index.json"),
            json.dumps(search_entries, ensure_ascii=False, indent=2),
        )

        write(
            os.path.join(temp_dir, "404.html"),
            rebase(render_404(config, nav_notes=nav_notes), base),
        )

        # --- sitemap.xml, robots.txt and alias redirects ---
        site = config["site"]
        author = site.get("author") or {}
        write_site_files(
            {
                "site_url": site["url"],
                "site_name": site["title"],
                "site_author": author.get("name", ""),
                "site_author_url": author.get("url", ""),
                "site_dir": temp_dir,
            }
        )

        # backup and replace
        backup_dir = None
        if os.path.exists(target_dir):
            backup_dir = tempfile.mkdtemp(prefix="garden_backup_", dir=parent_dir)
            os.rmdir(backup_dir)
            try:
                os.replace(target_dir, backup_dir)
            except OSError:
                shutil.rmtree(target_dir, ignore_errors=True)
                backup_dir = None

        try:
            os.replace(temp_dir, target_dir)
        except OSError:
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, ignore_errors=True)
            shutil.move(temp_dir, target_dir)

        if backup_dir and os.path.exists(backup_dir):
            shutil.rmtree(backup_dir, ignore_errors=True)
    except Exception:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise

    print(f"Garden build complete! Dist generated at '{dist_dir}'.")
    return dist_dir


if __name__ == "__main__":
    out = build_garden()
    if "serve" in sys.argv[1:]:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=out)
        print("Serving at http://localhost:8000 (ctrl+c to stop)")
        try:
            http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler).serve_forever()
        except KeyboardInterrupt:
            pass
