from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from backend_fastapi.core.errors import TRADE_E02
from backend_fastapi.core.response import error_response, success_response
from backend_fastapi.mock_modules.mock_store import now_iso, pick_stock, store


router = APIRouter()


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _format_amount(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


@router.get("/stocks")
async def search_stocks(keyword: Optional[str] = Query(None)) -> Dict[str, Any]:
    market = store.load_market()
    items = market.get("stocks", [])
    if keyword:
        keyword_lower = keyword.lower()
        items = [
            item
            for item in items
            if keyword_lower in str(item.get("symbol", "")).lower()
            or keyword_lower in str(item.get("name", "")).lower()
        ]

    data = {
        "items": [
            {
                "stock_code": item.get("symbol"),
                "stock_name": item.get("name"),
                "board": item.get("board"),
                "announcements": item.get("announcements", []),
            }
            for item in items
        ]
    }
    return success_response(data)


@router.get("/stocks/{stock_code}/quote")
async def quote(stock_code: str) -> Dict[str, Any]:
    stock = pick_stock(stock_code)
    if not stock:
        return error_response(TRADE_E02.code, TRADE_E02.message)

    data = {
        "stock_code": stock_code,
        "stock_name": stock.get("name"),
        "latest_price": _format_amount(_decimal(stock.get("lastPrice") or 0)),
        "open_price": _format_amount(_decimal(stock.get("openPrice") or stock.get("lastPrice") or 0)),
        "high_price": _format_amount(_decimal(stock.get("dayHigh") or 0)),
        "low_price": _format_amount(_decimal(stock.get("dayLow") or 0)),
        "volume": int(stock.get("volume") or 0),
        "turnover": _format_amount(_decimal(stock.get("turnover") or 0)),
        "best_bid_price": _format_amount(_decimal(stock.get("bid") or 0)),
        "best_ask_price": _format_amount(_decimal(stock.get("ask") or 0)),
        "updated_at": now_iso(),
    }
    return success_response(data)
