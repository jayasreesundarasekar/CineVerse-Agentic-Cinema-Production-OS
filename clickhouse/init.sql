-- Cineverse ClickHouse schema (also auto-created by app/core/clickhouse_client.py)
CREATE DATABASE IF NOT EXISTS cineverse;

CREATE TABLE IF NOT EXISTS cineverse.simulation_runs (
    run_id String,
    project_id String,
    agent_name String,
    scenario String,
    score Float64,
    outcome String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (project_id, created_at);

CREATE TABLE IF NOT EXISTS cineverse.screenplay_scores (
    script_id String,
    project_id String,
    dimension String,
    score Float64,
    notes String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (project_id, created_at);

CREATE TABLE IF NOT EXISTS cineverse.mission_control_events (
    event_id String,
    project_id String,
    agent_name String,
    event_type String,
    payload String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY created_at;
