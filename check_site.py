"""Check internal links and assets in a built garden.

Run after ``python garden_build.py``::

    python check_site.py dist
    python check_site.py dist --base-path /digital-garden
"""

import argparse
import os
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

IGNORED_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}


class _ReferenceParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            lower = name.lower()
            if lower in {"href", "src"} and value:
                self.references.append((tag, lower, value))
            if lower == "id" and value:
                self.ids.add(value)
            if lower == "name" and tag == "a" and value:
                self.ids.add(value)


def _normalized_base_path(base_path):
    base_path = (base_path or "").strip().rstrip("/")
    if base_path and not base_path.startswith("/"):
        base_path = "/" + base_path
    return base_path


def _target_for(page_path, url, site_dir, base_path):
    """Return ``(target_path, inside, fragment)`` or ``(None, None, None)``."""
    parsed = urlparse(url)
    if parsed.scheme in IGNORED_SCHEMES or url.startswith("//"):
        return None, None, None
    fragment = unquote(parsed.fragment) if parsed.fragment else None
    if not parsed.path:
        # Fragment-only link (e.g. "#section") — target is the current page.
        if fragment:
            return os.path.abspath(page_path), True, fragment
        return None, None, None
    path = unquote(parsed.path)
    if path.startswith("/"):
        if base_path and (path == base_path or path.startswith(base_path + "/")):
            path = path[len(base_path) :]
        target = os.path.join(site_dir, path.lstrip("/"))
    else:
        target = os.path.join(os.path.dirname(page_path), path)
    target = os.path.abspath(os.path.normpath(target))
    site_root = os.path.abspath(site_dir)
    try:
        inside = os.path.commonpath([site_root, target]) == site_root
    except ValueError:
        inside = False
    if not inside:
        return target, False, fragment
    if os.path.isdir(target):
        target = os.path.join(target, "index.html")
    return target, inside, fragment


def _collect_ids(site_dir):
    """Build a map of absolute file path → set of id attributes for all HTML files."""
    ids_by_file: dict[str, set[str]] = {}
    for root, _, files in os.walk(site_dir):
        for name in sorted(files):
            if not name.endswith(".html"):
                continue
            page = os.path.join(root, name)
            parser = _ReferenceParser()
            with open(page, encoding="utf-8") as stream:
                parser.feed(stream.read())
            ids_by_file[os.path.abspath(page)] = parser.ids
    return ids_by_file


def check_site(site_dir, base_path=""):
    """Return a list of human-readable broken reference messages."""
    site_dir = os.path.abspath(site_dir)
    base_path = _normalized_base_path(base_path)
    if not os.path.isdir(site_dir):
        return ["site directory does not exist: %s" % site_dir]

    ids_by_file = _collect_ids(site_dir)
    errors: list[str] = []
    for root, _, files in os.walk(site_dir):
        for name in sorted(files):
            if not name.endswith(".html"):
                continue
            page = os.path.join(root, name)
            parser = _ReferenceParser()
            with open(page, encoding="utf-8") as stream:
                parser.feed(stream.read())
            page_rel = os.path.relpath(page, site_dir).replace("\\", "/")
            for _, attr, url in parser.references:
                target_path, inside, fragment = _target_for(page, url, site_dir, base_path)
                if target_path is None:
                    continue
                if not inside or not os.path.exists(target_path):
                    errors.append("%s: %s=%r points to a missing file" % (page_rel, attr, url))
                elif fragment and target_path in ids_by_file:
                    if fragment not in ids_by_file[target_path]:
                        errors.append(
                            "%s: %s=%r has a broken fragment #%s" % (page_rel, attr, url, fragment)
                        )
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check internal links and assets in a built garden."
    )
    parser.add_argument(
        "site_dir", nargs="?", default="dist", help="built site directory (default: dist)"
    )
    parser.add_argument(
        "--base-path",
        default=os.environ.get("GARDEN_BASE_PATH", ""),
        help="URL prefix used for a project site, e.g. /digital-garden",
    )
    args = parser.parse_args(argv)

    errors = check_site(args.site_dir, args.base_path)
    for error in errors:
        print("ERROR:", error)
    if errors:
        print("%d broken internal reference(s)." % len(errors))
        return 1
    print("No broken internal links or assets found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
