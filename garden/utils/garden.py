import os
import posixpath
import re

import yaml

from garden.garden_state import notes
from garden.links import expand, inline_icons, links
from garden.notes import STAGE_INDEX, TAG_PAGE, populate_garden
from garden.output import stage_index, tag_index
from garden.page import page_context
from garden.parsing import outside_code
from garden.utils.assets import og_image_url

EXCLUDED_DIRS = {"drafts", "templates"}


def _excluded(rel):
    parts = rel.split("/")
    name = parts[-1]
    if any(p in EXCLUDED_DIRS for p in parts[:-1]):
        return True
    if name.startswith("draft-"):
        return True
    return name.endswith(".md") and "template" in name


class GardenFile:
    def __init__(self, docs_dir, rel):
        self.src_uri = rel
        self.abs_src_path = os.path.abspath(os.path.join(docs_dir, rel))
        self._page = rel.endswith(".md")
        self.url = rel[:-3] + ".html" if self._page else rel

    def is_documentation_page(self):
        return self._page


class GardenFiles:
    def __init__(self, items):
        self.items = items

    def __iter__(self):
        return iter(self.items)

    def documentation_pages(self):
        return [f for f in self.items if f.is_documentation_page()]


def load(docs_dir):
    items = []
    for root, dirs, files in os.walk(docs_dir):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in sorted(files):
            rel = os.path.relpath(os.path.join(root, name), docs_dir).replace("\\", "/")
            if not _excluded(rel):
                items.append(GardenFile(docs_dir, rel))
    config = {"config_file_path": os.path.abspath("garden.yml")}
    populate_garden(GardenFiles(items), config)
    return notes


def markdown_for(src):
    text = notes[src]["_body"]
    text = outside_code(text, lambda t: expand(t, src, (src,), 0))
    text = outside_code(text, lambda t: links(t, src))
    text = outside_code(text, inline_icons)
    if src == TAG_PAGE:
        text += tag_index(src)
    if src in STAGE_INDEX:
        if not re.search(r"^#\s", text, re.M):
            text = "# %s\n\n%s" % (posixpath.dirname(src), text.lstrip())
        text += stage_index(src, STAGE_INDEX[src])
    return text


def _get_site_url():
    try:
        with open("garden.yml", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            return cfg.get("site", {}).get("url", "")
    except (OSError, yaml.YAMLError, AttributeError):
        return ""


def context_for(src, config=None):
    site_url = (
        config.get('site', {}).get('url', '')
        if (config and isinstance(config, dict))
        else _get_site_url()
    )
    og_image = og_image_url(config) if isinstance(config, dict) else ''
    # Preserve the full config dict so page_context can read keys like
    # current_status that were attached during the build.
    full_config = dict(config) if isinstance(config, dict) else {}
    full_config.setdefault('site_url', site_url)
    full_config.setdefault('og_image', og_image)
    return page_context(
        {},
        src,
        full_config,
        None,
    )
