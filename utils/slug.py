import re


def slugify(value):
    s = re.sub(r'[^\w\-]+', '-', str(value).strip().lower()).strip('-')
    return s or 'untitled'