from fastapi import APIRouter, UploadFile, File
import uuid
import os

from app.core.pipeline import DocumentPipeline

router = APIRouter()
pipeline = DocumentPipeline()

@router.post("/extract")
async def extract(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower() or ".png"
    tmp = f"/tmp/{uuid.uuid4().hex}{ext}"
    data = await file.read()
    with open(tmp, "wb") as f:
        f.write(data)
    result = pipeline.run(tmp)
    try:
        os.remove(tmp)
    except Exception:
        pass
    return result

@router.get("/health")
def health():
    return {"status": "ok"}