"""Fixtures pytest isolées : base SQLite temporaire par test et client HTTP FastAPI."""

from collections.abc import Generator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Ajoute src/backend au PYTHONPATH pour résoudre "from app..." quel que soit le répertoire d'appel
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import get_settings  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import create_app  # noqa: E402
from app.services.seed import seed_alternatives  # noqa: E402


@pytest.fixture()
def db_session(tmp_path: Path) -> Generator[Session, None, None]:
    """Crée une base SQLite jetable dans tmp_path et y injecte le catalogue de référence."""
    db_file = tmp_path / "test_optistack.db"
    engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        seed_alternatives(session, get_settings().seed_file_path)
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Fournit un TestClient FastAPI branché sur la session SQLite temporaire de test."""
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    # Surcharge la dépendance get_db pour isoler totalement les tests de la base de dev
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
