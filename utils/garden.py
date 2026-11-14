import os
import posixpath
import re
from types import SimpleNamespace

import hooks

EXCLUDED_DIRS = {"drafts", "templates"}


def _excluded(rel):
    parts = rel.split("/")
    name = parts[-1]
    if any(p in EXCLUDED_DIRS for p in parts[:-1]):
        return True
    if name.startswith("draft-"):
        return True
    return name.endswith(".md") and "template" in name


class _File:
    def __init__(self, docs_dir, rel):
        self.src_uri = rel
        self.abs_src_path = os.path.abspath(os.path.join(docs_dir, rel))
        self._page = rel.endswith(".md")
        self.url = rel[:-3] + ".html" if self._page else rel

    def is_documentation_page(self):
        return self._page


class _Files:
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
                items.append(_File(docs_dir, rel))
    config = {"config_file_path": os.path.abspath(".garden-zensical.yml")}
    hooks.on_files(_Files(items), config)
    return hooks.notes


def markdown_for(src):
    text = hooks.notes[src]["_body"]
    text = hooks._outside_code(text, lambda t: hooks._expand(t, src, (src,), 0))
    text = hooks._outside_code(text, lambda t: hooks._links(t, src))
    if src == hooks.TAG_PAGE:
        text += hooks._tag_index(src)
    if src in hooks.STAGE_INDEX:
        if not re.search(r"^#\s", text, re.M):
            text = "# %s\n\n%s" % (posixpath.dirname(src), text.lstrip())
        text += hooks._stage_index(src, hooks.STAGE_INDEX[src])
    return text


def context_for(src):
    page = SimpleNamespace(file=SimpleNamespace(src_uri=src))
    return hooks.on_page_context({}, page, {}, None)


def is_listed(note):
    return hooks._is_listed(note)