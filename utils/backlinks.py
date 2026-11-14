import re
import os

def build_backlink_graph(docs_dir="docs"):
    notes = {}
    wikilink_pattern = re.compile(r'\[\[([^\|\]]+)(?:\|[^\]]+)?\]\]')

    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                note_name = file[:-3]
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                matches = wikilink_pattern.findall(content)
                notes[note_name] = set(matches)

    backlinks = {note: [] for note in notes}
    for source_note, targets in notes.items():
        for target in targets:
            if target in backlinks:
                backlinks[target].append(source_note)

    return {k: sorted(list(v)) for k, v in backlinks.items()}