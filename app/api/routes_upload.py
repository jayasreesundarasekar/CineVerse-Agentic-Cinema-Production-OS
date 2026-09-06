"""File storage routes — upload scripts/production documents to GCS
(or local fallback), and list stored artifacts."""
from fastapi import APIRouter, File, Form, UploadFile

from app.core.gcs_storage import GCSStorage
from app.models.schemas import UploadResponse

router = APIRouter(prefix="/storage", tags=["storage"])
storage = GCSStorage()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), folder: str = Form("uploads")):
    data = await file.read()
    uri = storage.upload_bytes(data, file.filename, folder=folder)
    return UploadResponse(filename=file.filename, storage_uri=uri, size_bytes=len(data))


@router.get("/artifacts")
async def list_artifacts(folder: str = "artifacts"):
    return {"folder": folder, "files": storage.list_artifacts(folder=folder)}
