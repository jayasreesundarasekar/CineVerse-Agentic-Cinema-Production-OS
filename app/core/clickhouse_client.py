"""
ClickHouse client for storing/querying:
 - simulation runs (per-agent scores, outcomes)
 - screenplay analysis scores
 - production analytics events (Mission Control feed)
 - character digital twins, budgets, audience projections,
   red-team findings, multiverse universe nodes, and greenlight
   decision provenance (the CREATE/SIMULATE/ANALYZE/PRODUCE/DECIDE
   modules all read/write through this same generic client)

Falls back to an in-memory store when ClickHouse is unreachable or
not configured, so analytics endpoints keep working in mock mode.
"""
import logging
import time
import uuid
from typing import Any

from app.config import get_settings

logger = logging.getLogger("cineverse.clickhouse")
_settings = get_settings()

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS simulation_runs (
        run_id String,
        project_id String,
        agent_name String,
        scenario String,
        score Float64,
        outcome String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (project_id, created_at)
    """,
    """
    CREATE TABLE IF NOT EXISTS screenplay_scores (
        script_id String,
        project_id String,
        dimension String,
        score Float64,
        notes String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (project_id, created_at)
    """,
    """
    CREATE TABLE IF NOT EXISTS mission_control_events (
        event_id String,
        project_id String,
        agent_name String,
        event_type String,
        payload String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY created_at
    """,
    """
    CREATE TABLE IF NOT EXISTS characters (
        character_id String,
        project_id String,
        name String,
        profile_json String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (project_id, created_at)
    """,
    """
    CREATE TABLE IF NOT EXISTS budgets (
        budget_id String,
        project_id String,
        universe_id String,
        line_items_json String,
        total_cost Float64,
        risk_delta String,
        quality_delta String,
        notes String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (project_id, created_at)
    """,
    """
    CREATE TABLE IF NOT EXISTS audience_projections (
        projection_id String,
        project_id String,
        universe_id String,
        segment String,
        appeal_score Float64,
        rationale String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (project_id, created_at)
    """,
    """
    CREATE TABLE IF NOT EXISTS red_team_findings (
        finding_id String,
        project_id String,
        universe_id String,
        severity String,
        issue String,
        recommendation String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (project_id, created_at)
    """,
    """
    CREATE TABLE IF NOT EXISTS universes (
        universe_id String,
        project_id String,
        parent_id String,
        title String,
        summary String,
        story_score Float64,
        audience_score Float64,
        continuity_score Float64,
        budget_score Float64,
        status String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (project_id, created_at)
    """,
    """
    CREATE TABLE IF NOT EXISTS decisions (
        decision_id String,
        project_id String,
        universe_id String,
        verdict String,
        reasoning String,
        source_run_ids String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (project_id, created_at)
    """,
    """
    CREATE TABLE IF NOT EXISTS visual_generations (
        visual_id String,
        project_id String,
        generate_type String,
        prompt String,
        variant_count UInt8,
        storage_uris_json String,
        mock UInt8,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (project_id, created_at)
    """,
]

MEMORY_TABLES = [
    "simulation_runs", "screenplay_scores", "mission_control_events",
    "characters", "budgets", "audience_projections", "red_team_findings",
    "universes", "decisions", "visual_generations",
]


class ClickHouseAnalytics:
    def __init__(self):
        self.enabled = False
        self._client = None
        self._memory: dict[str, list[dict[str, Any]]] = {table: [] for table in MEMORY_TABLES}
        try:
            import clickhouse_connect
            self._client = clickhouse_connect.get_client(
                host=_settings.clickhouse_host,
                port=_settings.clickhouse_port,
                username=_settings.clickhouse_user,
                password=_settings.clickhouse_password,
                database=_settings.clickhouse_database,
            )
            for stmt in SCHEMA_STATEMENTS:
                self._client.command(stmt)
            self.enabled = True
        except Exception as exc:  # noqa: BLE001
            logger.warning("ClickHouse unavailable, using in-memory analytics store: %s", exc)

    def insert(self, table: str, row: dict[str, Any]) -> str:
        row = dict(row)
        row.setdefault("created_at", time.strftime("%Y-%m-%d %H:%M:%S"))
        row_id = (
            row.get("run_id") or row.get("script_id") or row.get("event_id")
            or row.get("character_id") or row.get("budget_id") or row.get("projection_id")
            or row.get("finding_id") or row.get("universe_id") or row.get("decision_id")
            or row.get("visual_id") or uuid.uuid4().hex
        )

        if self.enabled:
            columns = list(row.keys())
            self._client.insert(table, [list(row.values())], column_names=columns)
        else:
            self._memory.setdefault(table, []).append(row)
        return row_id

    def query(self, table: str, project_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        if self.enabled:
            where = f"WHERE project_id = '{project_id}'" if project_id else ""
            result = self._client.query(f"SELECT * FROM {table} {where} ORDER BY created_at DESC LIMIT {limit}")
            return [dict(zip(result.column_names, row)) for row in result.result_rows]

        rows = self._memory.get(table, [])
        if project_id:
            rows = [r for r in rows if r.get("project_id") == project_id]
        return rows[-limit:][::-1]


# Shared singleton. In mock/in-memory mode each ClickHouseAnalytics() instance
# has its own isolated store, so every agent and route MUST import and use
# this shared instance (rather than constructing a new one) for data written
# by one agent to be visible to another agent or to the analytics/studio
# routes. In live-ClickHouse mode this is just a convenience shared client.
analytics = ClickHouseAnalytics()
