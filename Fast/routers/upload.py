import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from Fast.config import get_settings
from Fast.schemas import UploadResponse
from Fast.dependencies import get_rag_service
from Fast.services.supabase_client import get_supabase_client

router = APIRouter()


@router.post("/upload/pdf", response_model=UploadResponse)
def upload_pdf(
    file: UploadFile = File(...),
    rag_service=Depends(get_rag_service),
) -> UploadResponse:
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase is not configured. Set SUPABASE_URL and SUPABASE_KEY.",
        )

    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF uploads are supported.")

    data = file.file.read()
    size_bytes = len(data)
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_mb} MB limit.",
        )

    supabase = get_supabase_client()

    safe_name = (file.filename or "document.pdf").replace("/", "_").replace("\\", "_")
    object_path = f"{settings.supabase_upload_prefix}/{uuid.uuid4()}-{safe_name}"

    upload_result = supabase.storage.from_(settings.supabase_bucket).upload(
        object_path,
        data,
        file_options={"content-type": file.content_type},
    )

    if getattr(upload_result, "error", None):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Storage upload failed: {upload_result.error}",
        )

    public_url: Optional[str] = None
    if settings.supabase_public_bucket:
        public_url = supabase.storage.from_(settings.supabase_bucket).get_public_url(object_path)

    now = datetime.now(timezone.utc).isoformat()
    insert_payload = {
        "filename": safe_name,
        "storage_path": object_path,
        "content_type": file.content_type,
        "size_bytes": size_bytes,
        "uploaded_at": now,
        "public_url": public_url,
    }

    db_result = supabase.table(settings.supabase_table).insert(insert_payload).execute()
    if getattr(db_result, "error", None):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Metadata insert failed: {db_result.error}",
        )

    record = None
    if getattr(db_result, "data", None):
        record = db_result.data[0]

    try:
        rag_service.ingest_pdf_bytes(
            data=data,
            filename=safe_name,
            storage_path=object_path,
            public_url=public_url,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding failed: {exc}",
        )

    return UploadResponse(
        id=(record.get("id") if record else None),
        filename=safe_name,
        storage_path=object_path,
        public_url=public_url,
        size_bytes=size_bytes,
        content_type=file.content_type,
        uploaded_at=now,
    )
