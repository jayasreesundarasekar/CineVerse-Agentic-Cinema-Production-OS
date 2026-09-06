"""
Cinema Multiverse — builds the branching universe tree (ORIGINAL ->
UNIVERSE A / UNIVERSE B -> ... -> GREENLIGHT) from the flat `universes`
ClickHouse table so the frontend can render it as a node graph.
"""
from typing import Any

from app.core.clickhouse_client import ClickHouseAnalytics
from app.core.clickhouse_client import analytics as _shared_analytics


def build_tree(project_id: str, analytics: ClickHouseAnalytics | None = None) -> dict[str, Any]:
    analytics = analytics or _shared_analytics
    rows = analytics.query("universes", project_id=project_id, limit=1000)

    nodes_by_id = {row["universe_id"]: {**row, "children": []} for row in rows}
    roots = []
    for row in rows:
        parent_id = row.get("parent_id") or ""
        node = nodes_by_id[row["universe_id"]]
        if parent_id and parent_id in nodes_by_id:
            nodes_by_id[parent_id]["children"].append(node)
        else:
            roots.append(node)

    return {"project_id": project_id, "universe_count": len(rows), "roots": roots}
