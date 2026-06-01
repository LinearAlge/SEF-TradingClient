from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from fastapi import APIRouter

from backend_fastapi.core.errors import TRADE_E02
from backend_fastapi.core.response import error_response, success_response
from backend_fastapi.mock_modules.mock_store import now_iso, pick_stock


router = APIRouter()


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _format_amount(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


@router.get("/stocks/{stock_code}/quote")
async def quote(stock_code: str) -> Dict[str, Any]:
    stock = pick_stock(stock_code)
    if not stock:
        return error_response(TRADE_E02.code, TRADE_E02.message)

    data = {
        "stock_code": stock_code,
        "stock_name": stock.get("name"),
        "latest_price": _format_amount(_decimal(stock.get("lastPrice") or 0)),
        "limit_up_price": _format_amount(_decimal(stock.get("limitUp") or stock.get("lastPrice") or 0) * Decimal("1.1")),
        "limit_down_price": _format_amount(_decimal(stock.get("limitDown") or stock.get("lastPrice") or 0) * Decimal("0.9")),
        "updated_at": now_iso(),
    }
    return success_response(data)


@router.get("/stocks/{stock_code}/rule")
async def trade_rule(stock_code: str) -> Dict[str, Any]:
    stock = pick_stock(stock_code)
    if not stock:
        return error_response(TRADE_E02.code, TRADE_E02.message)

    base_price = _decimal(stock.get("lastPrice") or 0)
    data = {
        "stock_code": stock_code,
        "stock_status": stock.get("status", "OPEN"),
        "limit_up_price": _format_amount(base_price * Decimal("1.1")),
        "limit_down_price": _format_amount(base_price * Decimal("0.9")),
    }
    return success_response(data)


@router.get("/trading-day/status")
async def trading_day_status() -> Dict[str, Any]:
    data = {
        "trade_date": now_iso()[:10],
        "status": "OPEN",
    }
    return success_response(data)
