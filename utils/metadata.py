import os
import json
import frontmatter
from jsonschema import validate, ValidationError

def parse_markdown_file(file_path, schema_path="frontmatter-schema.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

        metadata = dict(post.metadata)
        content = post.content

        for key, value in metadata.items():
            if hasattr(value, "isoformat"):
                metadata[key] = value.isoformat()

    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        try:
            validate(instance=metadata, schema=schema)
        except ValidationError as e:
            print(f"Validation warning in {file_path}: {e.message}")

    return metadata, content

def build_index(docs_dir="docs", schema_path="frontmatter-schema.json"):
    index = []
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, docs_dir)
                try:
                    meta, _ = parse_markdown_file(full_path, schema_path)
                    index.append({
                        "path": rel_path.replace("\\", "/"),
                        "title": meta.get("title", file[:-3]),
                        "stage": meta.get("stage", "seedling"),
                        "tags": meta.get("tags", []),
                        "date": str(meta.get("date", ""))
                    })
                except Exception as e:
                    print(f"Error reading {full_path}: {e}")
    return index