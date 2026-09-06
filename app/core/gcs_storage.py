"""
Google Cloud Storage wrapper.
Used to store uploaded scripts / production documents and generated
artifacts (agent reports, simulation traces, forensics reports).

Falls back to local-disk storage under ./local_storage when GCS
credentials/bucket are not configured, so uploads still work offline.
"""
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from app.config import get_settings

logger = logging.getLogger("cineverse.gcs")
_settings = get_settings()

LOCAL_FALLBACK_DIR = Path("local_storage")


class GCSStorage:
    def __init__(self):
        self.bucket_name = _settings.gcs_bucket_name
        self.enabled = bool(_settings.gcp_project_id and _settings.google_application_credentials
                             and os.path.exists(_settings.google_application_credentials))
        self._client = None
        self._bucket = None
        if self.enabled:
            try:
                from google.cloud import storage
                self._client = storage.Client(project=_settings.gcp_project_id)
                self._bucket = self._client.bucket(self.bucket_name)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not init GCS client, using local fallback: %s", exc)
                self.enabled = False
        if not self.enabled:
            LOCAL_FALLBACK_DIR.mkdir(exist_ok=True)

    def upload_bytes(self, data: bytes, filename: str, folder: str = "uploads") -> str:
        key = f"{folder}/{uuid.uuid4().hex}_{filename}"
        if self.enabled:
            blob = self._bucket.blob(key)
            blob.upload_from_string(data)
            return f"gs://{self.bucket_name}/{key}"

        local_path = LOCAL_FALLBACK_DIR / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
        return str(local_path)

    def download_bytes(self, uri: str) -> Optional[bytes]:
        if uri.startswith("gs://") and self.enabled:
            _, _, rest = uri.partition("gs://")
            bucket_name, _, key = rest.partition("/")
            blob = self._client.bucket(bucket_name).blob(key)
            return blob.download_as_bytes()

        path = Path(uri)
        if path.exists():
            return path.read_bytes()
        return None

    def list_artifacts(self, folder: str = "artifacts") -> list[str]:
        if self.enabled:
            return [b.name for b in self._client.list_blobs(self.bucket_name, prefix=folder)]
        folder_path = LOCAL_FALLBACK_DIR / folder
        if not folder_path.exists():
            return []
        return [str(p) for p in folder_path.rglob("*") if p.is_file()]
