"""Configuration du moteur SQLAlchemy et gestion des sessions de base de données."""

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Classe mère commune à tous les modèles ORM SQLAlchemy."""


def _build_engine():
    """Construit le moteur SQLAlchemy compatible PostgreSQL et SQLite."""
    settings = get_settings()
    url = settings.database_url
    # SQLite impose check_same_thread=False pour fonctionner avec les threads FastAPI
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, echo=settings.sqlalchemy_echo, connect_args=connect_args)


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI fournissant une session DB fermée automatiquement après chaque requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
