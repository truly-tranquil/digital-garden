STAGE_FOLDERS = [("seedlings", "seedling"), ("buds", "bud"), ("evergreens", "evergreen")]


def _matches(src, note, name):
    if name == "welcome":
        return src == "index.md"
    return name in {note["title"].lower(), note["_stem"].lower()}


def build_nav(notes):
    visible = [(s, n) for s, n in notes.items() if not n["draft"] and not n["unlisted"]]
    archived_notes = [n for s, n in visible if n.get("archived")]
    listed = [(s, n) for s, n in visible if not n.get("archived")]

    def link(n):
        return {"title": n["title"], "url": "/" + n["url"]}

    used = set()
    nav = []

    # Top pages in fixed order: home, manifesto, about
    for name in ["welcome", "manifesto", "about"]:
        for src, n in listed:
            if src not in used and _matches(src, n, name):
                nav.append(link(n))
                used.add(src)
                break

    # Then stage folders
    stage_counts = {
        stage: sum(1 for _, n in notes.items() if n.get("stage") == stage and not n.get("archived"))
        for _, stage in STAGE_FOLDERS
    }

    for folder_name, stage in STAGE_FOLDERS:
        children = [link(n) for _, n in listed if n.get("stage") == stage and not n["is_index"]]
        nav.append(
            {
                "title": folder_name,
                "count": stage_counts[stage],
                "stage": stage,
                "children": [
                    {"title": "all %s" % folder_name, "url": "/%s/index.html" % folder_name}
                ]
                + children,
            }
        )

    if archived_notes:
        nav.append(
            {
                "title": "archive",
                "count": len(archived_notes),
                "children": [
                    link(n) for n in sorted(archived_notes, key=lambda n: n["title"].lower())
                ],
            }
        )

    return nav
