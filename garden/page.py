"""Per-page template context: stage, tags, dates, reading time and SEO."""

from datetime import date

from garden.garden_state import notes
from garden.notes import is_listed

# A note left this many days without a tend is considered gone to weed.
WEEDS_AFTER_DAYS = 14
STAGE_ORDER = {'seedling': 0, 'bud': 1, 'evergreen': 2}
STAGE_LABEL = {'seedling': 'seedlings', 'bud': 'buds', 'evergreen': 'evergreens'}


def days_since(value, today):
    """Whole days from an ISO date to ``today``, or None when it won't parse."""
    try:
        day = date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None
    return (today - day).days


def weeds_for(note, today):
    """Return ``{'days': n, 'tended': iso}`` when the note is gone to weed."""
    last_tended = note.get('tended') or note.get('planted')
    if not last_tended:
        return None
    days = days_since(last_tended, today)
    if days is None or days < WEEDS_AFTER_DAYS:
        return None
    return {'days': days, 'tended': str(last_tended)[:10]}


def page_context(context, page, config, nav=None):
    if hasattr(page, 'file') and hasattr(page.file, 'src_uri'):
        src = page.file.src_uri
    elif isinstance(page, str):
        src = page
    else:
        src = getattr(page, 'src', '')
    n = notes.get(src)
    is_note = bool(n and not n['is_index'])
    listed = [(s, note) for s, note in notes.items() if is_listed(note)]
    stages = (
        ('seedling', 'seedlings'),
        ('bud', 'buds'),
        ('evergreen', 'evergreens'),
    )
    context['garden_stage_stats'] = [
        {
            'stage': stage,
            'label': label,
            'count': sum(1 for _, note in listed if note['stage'] == stage),
        }
        for stage, label in stages
    ]
    context['garden_note_total'] = len(listed)
    context['weeds'] = weeds_for(n, date.today()) if is_note and n else None

    description = (n or {}).get('excerpt', '')

    page_url = '' if isinstance(page, str) else getattr(page, 'url', '')
    note_url = (n or {}).get('url', '')
    url = page_url or note_url
    site_url = config.get('site_url', '').rstrip('/') if isinstance(config, dict) else ''
    context.update(
        {
            'description': description,
            'og_title': (n or {}).get('title', ''),
            'og_description': description,
            'og_type': 'article' if is_note else 'website',
            'og_image': config.get('og_image', '') if isinstance(config, dict) else '',
            'canonical_url': f"{site_url}/{url}" if site_url and url else '',
            'page_url': '/' + url if url else '',
            'page_src': src,
        }
    )
    return context
