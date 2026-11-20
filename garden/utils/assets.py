import os
import shutil

# the image used for og:image / link previews; rename here if it changes
OG_IMAGE_NAME = "m_umar_farooq.jpg"
# its intrinsic size, declared in the social meta tags; a test keeps them in sync
OG_IMAGE_WIDTH = 1200
OG_IMAGE_HEIGHT = 630


def og_image_url(config):
    """Absolute og:image URL for the site, or '' when the asset is missing.

    og:image must be absolute, so the configured site url is joined with the
    asset path inside the source assets folder.
    """
    if not isinstance(config, dict):
        return ""
    site = config.get("site") or {}
    paths = config.get("paths") or {}
    site_url = site.get("url", "")
    src_dir = paths.get("source", "docs")
    if not site_url:
        return ""
    if not os.path.exists(os.path.join(src_dir, "assets", "images", OG_IMAGE_NAME)):
        return ""
    return site_url.rstrip("/") + "/assets/images/" + OG_IMAGE_NAME


def copy_referenced_media(src_dir="docs", dist_dir="dist", media_paths=()):
    """Copy note media that lives outside ``docs/assets`` to the same path in dist."""
    for rel in sorted(media_paths):
        src_file = os.path.join(src_dir, *rel.split("/"))
        if not os.path.exists(src_file):
            continue
        dist_file = os.path.join(dist_dir, *rel.split("/"))
        os.makedirs(os.path.dirname(dist_file), exist_ok=True)
        shutil.copy2(src_file, dist_file)


def copy_static_assets(src_dir="docs/assets", dist_dir="dist/assets"):
    if not os.path.exists(src_dir):
        return False
    os.makedirs(dist_dir, exist_ok=True)
    for root, _, files in os.walk(src_dir):
        for file in files:
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(src_file, src_dir)
            dist_file = os.path.join(dist_dir, rel_path)
            os.makedirs(os.path.dirname(dist_file), exist_ok=True)
            shutil.copy2(src_file, dist_file)
    return True
