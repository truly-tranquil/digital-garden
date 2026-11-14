import os
import re
import json
import shutil
import yaml
from utils import garden
from utils.nav import build_nav
from utils.assets import copy_static_assets
from utils.renderer import render_page


def build_garden():
    with open('.garden-zensical.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    docs_dir = config['paths']['source']
    dist_dir = config['paths']['output']
    os.makedirs(dist_dir, exist_ok=True)
    base = os.environ.get("GARDEN_BASE_PATH", "").rstrip("/")

    notes = garden.load(docs_dir)
    nav_notes = build_nav(notes)
    search_entries = []

    for src, note in notes.items():
        if note['draft']:
            continue

        html_out = render_page(
            note, garden.markdown_for(src), src, garden.context_for(src),
            config, nav_notes=nav_notes,
        )
        html_out = re.sub(
            r'(href|src)="/(?!/)',
            lambda m: m.group(1) + '="' + base + '/',
            html_out,
        )
        out_path = os.path.join(dist_dir, src[:-3] + '.html')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_out)

        if not note['unlisted']:
            search_entries.append({
                "title": note['title'],
                "url": base + "/" + note['url'],
                "stage": note['stage'] or "",
                "tags": note['tags'],
                "listed": garden.is_listed(note),
                "text": note['_body'][:2000],
            })

    copy_static_assets(f"{docs_dir}/assets", f"{dist_dir}/assets")
    shutil.copy2("my-garden-theme/static/garden.css", os.path.join(dist_dir, "garden.css"))
    shutil.copy2("my-garden-theme/static/garden.js", os.path.join(dist_dir, "garden.js"))
    with open(os.path.join(dist_dir, "search-index.json"), "w", encoding="utf-8") as f:
        json.dump(search_entries, f)

    print(f"Garden build complete! Dist generated at '{dist_dir}'.")


if __name__ == "__main__":
    build_garden()