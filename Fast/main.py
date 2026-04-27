from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Fast.config import get_settings
from Fast.dependencies import get_rag_service
from Fast.logging_config import configure_logging
from Fast.routers import admin, health, query, upload

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.skip_startup_init:
        rag_service = get_rag_service()
        rag_service.initialize()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(query.router, prefix=settings.api_prefix, tags=["query"])
app.include_router(admin.router, prefix=settings.api_prefix, tags=["admin"])
app.include_router(upload.router, prefix=settings.api_prefix, tags=["upload"])
