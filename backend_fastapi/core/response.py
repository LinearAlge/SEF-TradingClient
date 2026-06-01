from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend_fastapi.core.request_context import get_request_id


def _timestamp() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def success_response(data: Any = None, code: str = "OK", message: str = "success") -> Dict[str, Any]:
    return {
        "success": True,
        "code": code,
        "message": message,
        "data": data,
        "request_id": get_request_id(),
        "timestamp": _timestamp(),
    }


def error_response(code: str, message: str, data: Optional[Any] = None) -> Dict[str, Any]:
    return {
        "success": False,
        "code": code,
        "message": message,
        "data": data,
        "request_id": get_request_id(),
        "timestamp": _timestamp(),
    }


def client_ok(data: Any = None, code: str = "OK", message: str = "success") -> Dict[str, Any]:
    base = {
        "ok": True,
        "code": code,
        "message": message,
    }
    if isinstance(data, dict):
        return {**base, **data}
    return {**base, "data": data}


def client_error(code: str, message: str, data: Optional[Any] = None) -> Dict[str, Any]:
    base = {
        "ok": False,
        "code": code,
        "message": message,
    }
    if isinstance(data, dict):
        return {**base, **data}
    return {**base, "data": data}
