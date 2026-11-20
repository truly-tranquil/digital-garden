"""Responsive inline images: intrinsic size, loading hints and srcset variants.

Markdown leaves ``<img>`` tags alone, so a local image renders without its
intrinsic dimensions (the browser cannot reserve space before the file loads)
and large photos ship at full size on every screen. This post-processor fills
both gaps at build time:

* every local raster image gets ``width``/``height`` (unless the author already
  set one), ``decoding="async"`` and a ``loading`` hint;
* images wider than ``LARGE_IMAGE`` get a ``srcset`` of smaller variants that
  are written next to the original in the build output.

Remote, ``data:`` and SVG images are left untouched. Pillow is a build
requirement; without it the tags pass through unchanged.
"""

import os
import posixpath
import re
from urllib.parse import quote, unquote

try:
    from PIL import Image
except ImportError:  # pragma: no cover - Pillow is listed in requirements.txt
    Image = None  # type: ignore[assignment]

IMG_TAG = re.compile(r'<img\b[^>]*>', re.I)
SAVE_FORMATS = {'JPEG', 'PNG', 'WEBP'}

# Variants offered below the intrinsic width; the original is the last candidate.
VARIANT_WIDTHS = (480, 960, 1440)
# Only images this wide are worth resizing and describing in a srcset.
LARGE_IMAGE = 1200
# The content column stays roughly this wide once the sidebar and TOC are open.
SIZES = '(min-width: 1100px) 720px, 100vw'


def _attr(tag, name):
    match = re.search(r'(?<![\w-])%s=(["\'])(.*?)\1' % name, tag, re.I)
    return match.group(2) if match else None


def _add_attrs(tag, attrs):
    stripped = tag.rstrip()
    suffix = ' />' if stripped.endswith('/>') else '>'
    head = stripped[: -len(suffix)]
    added = ''.join(' %s="%s"' % (name, value) for name, value in attrs)
    return head + added + suffix


def _source(src_attr, note_src, docs_dir):
    """Resolve a local ``src`` to ``(absolute path, path under docs)``, or None."""
    if not src_attr or src_attr.startswith(('http://', 'https://', '//', 'data:')):
        return None
    path = unquote(src_attr.split('?', 1)[0].split('#', 1)[0])
    if path.startswith('/'):
        rel = path.lstrip('/')
    else:
        rel = posixpath.normpath(posixpath.join(posixpath.dirname(note_src), path))
    if rel.startswith(('..', '/')):
        return None
    full = os.path.join(docs_dir, *rel.split('/'))
    return (full, rel) if os.path.isfile(full) else None


def _open(path):
    if Image is None:
        return None
    try:
        image = Image.open(path)
        image.load()
    except OSError:
        return None
    return image


def _variant_rel(source_rel, width):
    stem, ext = posixpath.splitext(source_rel)
    return '%s-w%d%s' % (stem, width, ext)


def _write_variant(image, source_rel, width, dist_dir):
    """Write a resized copy into dist and return its path relative to docs."""
    target_rel = _variant_rel(source_rel, width)
    target = os.path.join(dist_dir, *target_rel.split('/'))
    if os.path.exists(target):
        return target_rel
    height = max(1, round(image.height * width / image.width))
    resized = image.resize((width, height), Image.Resampling.LANCZOS)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    fmt = image.format or ''
    if fmt == 'JPEG':
        resized.convert('RGB').save(target, 'JPEG', quality=82, optimize=True, progressive=True)
    elif fmt == 'PNG':
        resized.save(target, 'PNG', optimize=True)
    else:
        resized.save(target, 'WEBP', quality=82, method=4)
    resized.close()
    return target_rel


def _srcset(image, src_attr, source_rel, width, dist_dir):
    candidates = []
    for candidate in VARIANT_WIDTHS:
        if candidate >= width:
            continue
        target_rel = _write_variant(image, source_rel, candidate, dist_dir)
        candidates.append((target_rel, candidate))
    if not candidates:
        return ''
    base = posixpath.dirname(src_attr)
    parts = []
    for target_rel, candidate in candidates:
        name = quote(posixpath.basename(target_rel), safe='')
        parts.append('%s %dw' % (posixpath.join(base, name) if base else name, candidate))
    parts.append('%s %dw' % (src_attr, width))
    return ', '.join(parts)


def responsive_images(html_text, note_src, docs_dir, dist_dir):
    """Add dimensions, loading hints and srcset candidates to local images."""
    first = [True]

    def repl(match):
        tag = match.group(0)
        src = _attr(tag, 'src')
        resolved = _source(src, note_src, docs_dir)
        if resolved is None:
            return tag
        path, source_rel = resolved
        image = _open(path)
        if image is None:
            return tag

        attrs = []
        if _attr(tag, 'width') is None and _attr(tag, 'height') is None:
            attrs += [('width', image.width), ('height', image.height)]
        if _attr(tag, 'loading') is None:
            attrs.append(('loading', 'eager' if first[0] else 'lazy'))
        if _attr(tag, 'decoding') is None:
            attrs.append(('decoding', 'async'))
        first[0] = False

        if (
            image.format in SAVE_FORMATS
            and not getattr(image, 'is_animated', False)
            and image.width > LARGE_IMAGE
            and _attr(tag, 'srcset') is None
        ):
            attrs += [
                ('sizes', SIZES),
                ('srcset', _srcset(image, src, source_rel, image.width, dist_dir)),
            ]

        image.close()
        return _add_attrs(tag, attrs)

    return IMG_TAG.sub(repl, html_text)
