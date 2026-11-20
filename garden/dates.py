"""Note dates: front-matter validation and git-derived dates."""

import os
import shutil
import subprocess
from datetime import date

from garden.garden_state import warn


def validated_date(value, key, src):
    """Return ``value`` if it parses as an ISO date, else warn and return None."""
    if value is None:
        return None
    try:
        date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        warn('%s has an invalid %s date: %r' % (src, key, value))
        return None
    return value


def relative_day(value, today=None):
    """Human relative label for an ISO date ('today', 'yesterday', '3 days ago').

    Falls back to the absolute date when the day is in the future or over a
    month old. ``today`` is injectable for tests.
    """
    try:
        day = date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return str(value)
    if today is None:
        today = date.today()
    delta = (today - day).days
    if delta < 0 or delta > 30:
        return day.isoformat()
    if delta == 0:
        return 'today'
    if delta == 1:
        return 'yesterday'
    return '%d days ago' % delta


def git_dates_for_files(config, files):
    """Map source paths to (planted, tended) from git history."""
    if not shutil.which('git'):
        return {}
    config_path = config.get('config_file_path', 'garden.yml')
    root = os.path.dirname(os.path.abspath(config_path))
    if not os.path.exists(os.path.join(root, '.git')):
        return {}
    try:
        log = subprocess.run(
            ['git', 'log', '--name-status', '--find-renames', '--format=COMMIT%x09%cs'],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        status = subprocess.run(
            ['git', 'status', '--porcelain', '--untracked-files=all', '-z'],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        warn('unable to read git note dates: %s' % exc)
        return {}
    if log.returncode:
        warn('git history lookup failed: %s' % log.stderr.strip())
        return {}

    dates: dict[str, list[str | None]] = {}
    added: dict[str, str] = {}
    current_date = None
    for line in log.stdout.splitlines():
        if line.startswith('COMMIT\t'):
            current_date = line.split('\t')[1]
            continue
        if not current_date or not line:
            continue
        fields = line.split('\t')
        state = fields[0]
        paths = fields[1:]
        if state.startswith(('R', 'C')):
            paths = paths[-1:]
        for path in paths:
            path = path.replace('\\', '/')
            dates.setdefault(path, [None, None])[1] = (
                dates.get(path, [None, None])[1] or current_date
            )
            if state == 'A':
                added[path] = current_date
    for path, planted in added.items():
        dates.setdefault(path, [None, None])[0] = planted
    if status.returncode == 0:
        today = date.today().isoformat()
        pending_original = False
        for entry in status.stdout.split('\0'):
            if pending_original:
                pending_original = False
                continue
            if len(entry) < 4:
                continue
            state, path = entry[:2], entry[3:].replace('\\', '/')
            if 'R' in state or 'C' in state:
                pending_original = True
            dates.setdefault(path, [None, None])[1] = today
    result: dict[str, tuple[str | None, str | None]] = {}
    for file in files.documentation_pages():
        path = os.path.relpath(file.abs_src_path, root).replace('\\', '/')
        pair = dates.get(path)
        note_planted: str | None = pair[0] if pair else None
        tended = pair[1] if pair else None
        if tended is None and note_planted is not None:
            tended = note_planted
        result[file.src_uri] = (note_planted, tended)
    return result
