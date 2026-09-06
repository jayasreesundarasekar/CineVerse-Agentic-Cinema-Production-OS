"""
Central configuration for Cineverse.
All secrets/keys are loaded from environment variables (.env).
MOCK_MODE lets the whole platform run end-to-end with simulated
responses when a given API key is not configured, which is useful
for demos, CI, and local development.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to the project root (parent of app/), not the
# process's current working directory. Without this, `uvicorn
# app.main:app` run from a different directory (or from an IDE / systemd
# unit with a different CWD) silently fails to find .env, every key
# reads back empty, and every client falls back to mock mode even
# though the file is right there on disk.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    app_env: str = "development"
    app_port: int = 8000
    mock_mode: bool = True

    # Gemini — current as of Sept 2026. gemini-2.0-flash and
    # gemini-2.0-flash-preview-image-generation were both shut down by
    # Google on June 1, 2026; gemini-2.5-flash is itself scheduled to
    # retire Oct 16, 2026, so these default to the 3.x generation.
    # Override via .env if Google issues a newer replacement later.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    gemini_image_model: str = "gemini-3.1-flash-image"

    # Google Cloud
    gcp_project_id: str = ""
    gcp_location: str = "us-central1"
    gcs_bucket_name: str = "cineverse-artifacts"
    google_application_credentials: str = ""
    agent_engine_id: str = ""

    # ClickHouse
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "cineverse"

    # Grafana
    grafana_url: str = "http://localhost:3000"
    grafana_api_key: str = ""

    # Optional APIs
    parallel_api_key: str = ""
    youtube_api_key: str = ""
    tmdb_api_key: str = ""
    omdb_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
