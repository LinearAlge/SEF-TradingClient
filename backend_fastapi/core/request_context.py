from __future__ import annotations

from contextvars import ContextVar
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response


_request_id: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    value = _request_id.get()
    return value or "req-" + uuid4().hex


def set_request_id(value: str) -> None:
    _request_id.set(value)


async def request_id_middleware(request: Request, call_next: Callable) -> Response:
    req_id = request.headers.get("X-Request-Id") or "req-" + uuid4().hex
    set_request_id(req_id)
    response = await call_next(request)
    response.headers["X-Request-Id"] = req_id
    return response
