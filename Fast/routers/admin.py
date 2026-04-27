from fastapi import APIRouter, Depends, Header, HTTPException, status

from Fast.config import get_settings
from Fast.dependencies import get_rag_service
from Fast.schemas import ReindexRequest, ReindexResponse

router = APIRouter()


def verify_admin_key(x_admin_key: str | None = Header(default=None)):
    settings = get_settings()
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_API_KEY is not configured.",
        )
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key.")


@router.post("/index/rebuild", response_model=ReindexResponse, dependencies=[Depends(verify_admin_key)])
def rebuild_index(payload: ReindexRequest, rag_service=Depends(get_rag_service)):
    result = rag_service.rebuild_index(data_dir=payload.data_dir)
    return ReindexResponse(**result)
