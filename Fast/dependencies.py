from functools import lru_cache

from Fast.config import get_settings
from Fast.services.rag_service import RAGService


@lru_cache
def get_rag_service() -> RAGService:
    settings = get_settings()
    return RAGService(settings)
