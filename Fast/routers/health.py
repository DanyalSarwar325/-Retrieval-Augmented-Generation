from fastapi import APIRouter, Depends

from Fast.config import get_settings
from Fast.dependencies import get_rag_service
from Fast.schemas import HealthResponse, ReadyResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    settings = get_settings()
    return HealthResponse(status="ok", app_name=settings.app_name, version="0.1.0")


@router.get("/ready", response_model=ReadyResponse)
def readiness_check(rag_service=Depends(get_rag_service)):
    ready, reason = rag_service.readiness()
    return ReadyResponse(ready=ready, reason=reason)
