"""Shared build state.

The build is a single pass: notes are parsed once, then links, nav, the graph,
the feed and the sitemap all read from these registries. They stay module-level
and are only ever mutated in place so that every importer sees the same objects.
"""

from typing import Any

notes: dict[str, dict[str, Any]] = {}
backlinks: dict[str, list[dict[str, Any]]] = {}
outgoing: dict[str, list[dict[str, Any]]] = {}
lookup: dict[str, str] = {}
media_lookup: dict[str, str] = {}
referenced_media: set[str] = set()
warnings: list[str] = []
trails: list[dict[str, Any]] = []
trail_contexts: dict[str, list[dict[str, Any]]] = {}


def warn(message):
    entry = '[digital-garden] ' + message
    warnings.append(entry)
    print('WARNING:', entry)
