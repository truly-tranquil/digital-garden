import re
import posixpath
import yaml
from pathlib import Path

ROOT = Path('docs')
docs = {}
for p in ROOT.rglob('*.md'):
    docs[p.relative_to(ROOT).as_posix()] = p.read_text(encoding='utf-8')


def slugify(t):
    return re.sub(r'[^\w]+', '-', str(t).lower()).strip('-')


lookup = {}
for src, text in docs.items():
    title = None
    m = re.search(r'\A---\s*\n(.*?)\n---\s*\n', text, re.S)
    if m:
        try:
            meta = yaml.safe_load(m.group(1)) or {}
            if isinstance(meta, dict) and meta.get('title'):
                title = meta['title']
        except Exception:
            pass
    if not title:
        title = Path(src).stem
    lookup[title.lower()] = src
    lookup[slugify(title).lower()] = src
    lookup[src.lower()] = src
    stem = Path(src).stem.lower()
    if stem != 'index':
        lookup[stem] = src


WIKI = re.compile(r'!?\[\[([^\]]+)\]\]')
print("=== WIKILINK AUDIT ===")
broken = []
for src, text in docs.items():
    for m in WIKI.finditer(text):
        raw = m.group(1)
        target, _, _ = raw.partition('|')
        target, _, _ = target.partition('#')
        target = target.strip()
        resolved = None
        if target.lower() in lookup:
            resolved = lookup[target.lower()]
        elif slugify(target).lower() in lookup:
            resolved = lookup[slugify(target).lower()]
        status = 'OK  ' if resolved else 'BROKEN'
        if not resolved:
            broken.append((src, raw))
        print(f"{status} {src:55} [[{raw}]] -> {resolved}")
print()
print(f"BROKEN WIKILINKS: {len(broken)}")
for b in broken:
    print("  ", b)

print()
print("=== INTERNAL MARKDOWN LINK AUDIT ([text](path)) ===")
MLINK = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
broken2 = []
for src, text in docs.items():
    for m in MLINK.finditer(text):
        label, dest = m.group(1), m.group(2)
        if dest.startswith('http') or dest.startswith('mailto') or dest.startswith('#'):
            continue
        # strip fragment
        dest_path = dest.split('#')[0]
        # resolve relative to src dir
        cand = (Path(src).parent / dest_path).as_posix()
        norm = posixpath.normpath(cand)
        exists = norm in docs or (ROOT / norm).is_file()
        status = 'OK  ' if exists else 'BROKEN'
        if not exists:
            broken2.append((src, dest, norm))
        print(f"{status} {src:55} [{label}]({dest}) -> {norm}")
print()
print(f"BROKEN INTERNAL LINKS: {len(broken2)}")
for b in broken2:
    print("  ", b)
