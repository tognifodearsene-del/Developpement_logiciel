"""OptiStack FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.routers import alternatives, analysis, auth, inventory, reports
from app.services.seed import seed_alternatives


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize database schema and seed initial benchmark alternatives."""
    settings = get_settings()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_alternatives(db, settings.seed_file_path)
    yield


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/api/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "version": settings.app_version}

    application.include_router(auth.router)
    application.include_router(inventory.router)
    application.include_router(alternatives.router)
    application.include_router(analysis.router)
    application.include_router(reports.router)
    return application


app = create_app()
