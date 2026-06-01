from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "backend_fastapi" / "mock_modules" / "data"
CLIENT_DB_PATH = ROOT_DIR / "backend_fastapi" / "client" / "client.sqlite"


@dataclass(frozen=True)
class Settings:
    api_profile: str = "local_unified"
    enable_trade_ws: bool = False


settings = Settings()
