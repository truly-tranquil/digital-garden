from garden.garden_state import outgoing
from garden.notes import is_listed


def build_graph(notes, base=""):
    listed = {src: n for src, n in notes.items() if is_listed(n)}
    by_url = {n["url"]: src for src, n in listed.items()}

    nodes = [
        {
            "id": src,
            "type": "note",
            "title": n["title"],
            "url": base + "/" + n["url"],
            "stage": n["stage"],
        }
        for src, n in listed.items()
    ]

    edges = []
    seen = set()
    for src in listed:
        for link in outgoing.get(src, []):
            target = by_url.get(link["url"])
            if not target or target == src:
                continue
            pair = tuple(sorted((src, target)))
            if pair in seen:
                continue
            seen.add(pair)
            edges.append({"source": src, "target": target, "kind": "link"})

    from typing import Any

    tags: dict[str, dict[str, Any]] = {}
    for src, n in listed.items():
        for tag in n["tag_entries"]:
            name, slug = tag["name"], tag["slug"]
            entry = tags.setdefault(slug, {"name": name, "count": 0})
            entry["count"] += 1
            edges.append({"source": src, "target": "tag:" + slug, "kind": "tag"})

    for slug, tag in tags.items():
        nodes.append(
            {
                "id": "tag:" + slug,
                "type": "tag",
                "title": "#" + tag["name"],
                "url": base + "/by-tag/index.html#tag-" + slug,
                "stage": "",
                "count": tag["count"],
            }
        )

    return {"nodes": nodes, "edges": edges}


def with_base(graph, base):
    """Return ``graph`` with every node URL prefixed by ``base`` (for graph.json).

    build_graph runs once with no base; graph.html gets that graph (rebase() adds
    the prefix to the page's links), while graph.json needs the prefixed URLs so
    the canvas can navigate under a sub-path.
    """
    if not base:
        return graph
    return {
        "nodes": [
            dict(n, url=(base + n["url"] if n["url"].startswith("/") else n["url"]))
            for n in graph["nodes"]
        ],
        "edges": graph["edges"],
    }


def graph_text(graph):
    """Plain-text view of build_graph() output for a non-visual alternative.

    Link edges are undirected pairs (deduplicated by build_graph), so each
    note lists every note it is connected to. Tag edges are note -> tag and
    are reported per note. URLs are returned without a base prefix; the
    template relies on rebase() to add it for the rendered page.
    """
    nodes = graph.get("nodes", []) if graph else []
    edges = graph.get("edges", []) if graph else []
    by_id = {n["id"]: n for n in nodes}

    connected: dict[str, list[str]] = {}
    note_tags: dict[str, list[str]] = {}
    for e in edges:
        if e.get("kind") == "link":
            a, b = e["source"], e["target"]
            if a in by_id and b in by_id:
                connected.setdefault(a, []).append(b)
                connected.setdefault(b, []).append(a)
        elif e.get("kind") == "tag":
            note_tags.setdefault(e["source"], []).append(e["target"])

    notes = []
    for n in nodes:
        if n.get("type") != "note":
            continue
        links = [by_id[i] for i in connected.get(n["id"], [])]
        links.sort(key=lambda m: m["title"].casefold())
        tags = [by_id[i] for i in note_tags.get(n["id"], []) if i in by_id]
        tags.sort(key=lambda m: m["title"].casefold())
        notes.append(
            {
                "title": n["title"],
                "url": n["url"],
                "stage": n.get("stage", ""),
                "links": links,
                "tags": tags,
            }
        )
    notes.sort(key=lambda n: n["title"].casefold())

    tags = sorted(
        (n for n in nodes if n.get("type") == "tag"),
        key=lambda n: n["title"].casefold(),
    )
    return {"notes": notes, "tags": tags}
