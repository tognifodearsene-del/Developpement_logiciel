"""Configuration centrale de l'application chargée depuis les variables d'environnement (.env)."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv


# Racine du dépôt (remonte de src/backend/app/config.py vers la racine)
REPO_ROOT = Path(__file__).resolve().parents[3]
# Base SQLite locale utilisée par défaut si PostgreSQL/Docker n'est pas démarré
DEFAULT_SQLITE_PATH = Path(__file__).resolve().parents[1] / "optistack_dev.db"

# Charge le fichier .env à la racine sans écraser les variables déjà définies dans l'OS
load_dotenv(REPO_ROOT / ".env", override=False)


def _as_bool(value: str | None, default: bool) -> bool:
    """Convertit proprement une variable d'environnement texte en booléen."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Paramètres d'exécution immuables pour le backend OptiStack."""

    app_name: str
    app_version: str
    environment: str
    debug: bool
    database_url: str
    sqlalchemy_echo: bool
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    allowed_origins: str
    seed_file_path: Path

    @property
    def cors_origins(self) -> list[str]:
        """Découpe la liste des origines CORS autorisées (séparées par des virgules)."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Retourne une instance unique (mise en cache) de la configuration."""
    return Settings(
        app_name=os.getenv("APP_NAME", "OptiStack API"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=_as_bool(os.getenv("DEBUG"), True),
        database_url=os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"),
        sqlalchemy_echo=_as_bool(os.getenv("SQLALCHEMY_ECHO"), False),
        secret_key=os.getenv("SECRET_KEY", "dev-only-secret-key-change-in-production-32bytes"),
        algorithm=os.getenv("ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        allowed_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"),
        seed_file_path=REPO_ROOT / "data" / "alternatives_seed.json",
    )
