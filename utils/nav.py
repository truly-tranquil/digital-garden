TOP_PAGES = ["welcome", "manifesto", "about"]
LAST_PAGE = "forum"
STAGE_FOLDERS = [("seedlings", "seedling"), ("buds", "bud"), ("evergreens", "evergreen")]


def _matches(src, note, name):
    if name == "welcome":
        return src == "index.md"
    return name in {note["title"].lower(), note["_stem"].lower()}


def build_nav(notes):
    visible = [(s, n) for s, n in notes.items() if not n["draft"] and not n["unlisted"]]

    def link(n):
        return {"title": n["title"], "url": "/" + n["url"]}

    used = set()
    nav = []

    for name in TOP_PAGES:
        for src, n in visible:
            if src not in used and _matches(src, n, name):
                nav.append(link(n))
                used.add(src)
                break

    last = None
    for src, n in visible:
        if src not in used and _matches(src, n, LAST_PAGE):
            last = n
            used.add(src)
            break

    rest = sorted(
        (n for s, n in visible if s not in used and n["stage"] and not n["is_index"]),
        key=lambda n: n["title"].lower(),
    )

    for folder_name, stage in STAGE_FOLDERS:
        nav.append({"title": folder_name, "children": [link(n) for n in rest if n["stage"] == stage]})

    tag_map = {}
    for n in rest:
        for t in n["tags"]:
            tag_map.setdefault(t, []).append(n)
    nav.append({
        "title": "by-tag",
        "children": [
            {"title": t, "children": [link(n) for n in tag_map[t]]}
            for t in sorted(tag_map, key=str.lower)
        ],
    })

    if last:
        nav.append(link(last))
    return nav