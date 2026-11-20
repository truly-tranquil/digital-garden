"""Check front matter and links in docs/. Run: python validate_frontmatter.py

Errors (exit code 1): invalid YAML, duplicate keys, bad stage or dates, duplicate titles.
Notices (never fail): links to notes that don't exist yet, front matter keys the build ignores.
"""

import os
import sys

import yaml

from garden.garden_state import warnings
from garden.parsing import FRONT
from garden.utils import garden

KNOWN = {
    "title",
    "stage",
    "tags",
    "planted",
    "tended",
    "links_to",
    "links to",
    "aliases",
    "unlisted",
    "archived",
    "random",
    "icon",
    "draft",
}


class _Strict(yaml.SafeLoader):
    pass


def _no_duplicates(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                None, None, "duplicate key %r" % (key,), key_node.start_mark
            )
        seen.add(key)
    return loader.construct_mapping(node, deep)


_Strict.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


def check(docs_dir="docs"):
    garden.load(docs_dir)  # fills garden_state.warnings
    errors: list[str] = []
    notices: list[str] = []
    for warning in warnings:
        (notices if "links to missing" in warning else errors).append(warning)

    for root, _, files in os.walk(docs_dir):
        for name in sorted(files):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, docs_dir).replace("\\", "/")
            if not name.endswith(".md") or garden._excluded(rel):
                continue
            with open(path, encoding="utf-8") as f:
                match = FRONT.match(f.read())
            if not match:
                continue
            try:
                meta = yaml.load(match.group(1), Loader=_Strict) or {}
            except yaml.YAMLError as exc:
                errors.append("%s: %s" % (rel, exc))
                continue
            if isinstance(meta, dict):
                for key in meta:
                    if key not in KNOWN:
                        notices.append(
                            "%s: front matter key %r is not used by the build" % (rel, key)
                        )
    return errors, notices


if __name__ == "__main__":
    errs, notes_ = check(sys.argv[1] if len(sys.argv) > 1 else "docs")
    for n in notes_:
        print("notice:", n)
    for e in errs:
        print("ERROR:", e)
    sys.exit(1 if errs else 0)
