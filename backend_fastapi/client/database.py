from __future__ import annotations

from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend_fastapi.core.config import CLIENT_DB_PATH
from backend_fastapi.client.models import Base


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


_ensure_dir(CLIENT_DB_PATH)
_engine = create_engine(f"sqlite:///{CLIENT_DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def init_db() -> None:
    Base.metadata.create_all(bind=_engine)


def get_session() -> Session:
    return SessionLocal()
