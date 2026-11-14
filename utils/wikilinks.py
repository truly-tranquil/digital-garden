import re

def transform_wikilinks(content):
    content = re.sub(r'!\s*\[\[([^\|\]]+)\]\]', r'![\1](\1)', content)
    content = re.sub(r'\[\[([^\|\]]+)\|([^\]]+)\]\]', r'[\2](\1.md)', content)
    content = re.sub(r'\[\[([^\|\]]+)\]\]', r'[\1](\1.md)', content)
    return content

