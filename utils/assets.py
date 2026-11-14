import os
import shutil

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