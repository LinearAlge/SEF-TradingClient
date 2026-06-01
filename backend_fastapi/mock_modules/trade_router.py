from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from backend_fastapi.core.errors import (
    COMMON_BAD_REQUEST,
    COMMON_NOT_FOUND,
    TRADE_E01,
    TRADE_E02,
    TRADE_E03,
    TRADE_E04,
    TRADE_E05,
    TRADE_E06,
    TRADE_E07,
)
from backend_fastapi.core.response import error_response, success_response
from backend_fastapi.mock_modules.mock_store import build_market_index, now_iso, now_cn_time, pick_stock, store


router = APIRouter()


class OrderWsManager:
    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self._connections:
            self._connections.remove(ws)

    async def broadcast(self, payload: dict) -> None:
        for ws in list(self._connections):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(ws)


ws_manager = OrderWsManager()


def _required_fields(payload: Dict[str, Any], fields: List[str]) -> bool:
    return all(payload.get(item) not in (None, "") for item in fields)


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _format_amount(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def _resolve_order_status(order: Dict[str, Any]) -> str:
    status = order.get("status")
    if status:
        return status
    return "QUEUED"


def _map_status_to_client(status: str) -> str:
    mapping = {
        "ACCEPTED": "未成交",
        "QUEUED": "未成交",
        "PARTIALLY_FILLED": "部分成交",
        "FILLED": "已成交",
        "CANCELLED": "已撤单",
        "EXPIRED": "已过期",
        "REJECTED": "已拒绝",
    }
    return mapping.get(status, status)


def _map_side_to_client(side: str) -> str:
    return "买入" if side == "BUY" else "卖出"


def _map_side_from_client(side: str) -> str:
    return "BUY" if side == "买入" else "SELL"


@router.post("/orders")
async def submit_order(payload: Dict[str, Any]) -> Dict[str, Any]:
    required = [
        "client_order_id",
        "investor_id",
        "fund_account_id",
        "security_account_id",
        "stock_code",
        "side",
        "order_price",
        "order_quantity",
        "submitted_at",
    ]
    if not _required_fields(payload, required):
        return error_response(TRADE_E01.code, TRADE_E01.message)

    stock_code = payload.get("stock_code")
    side = payload.get("side")
    if side not in ("BUY", "SELL"):
        return error_response(TRADE_E04.code, TRADE_E04.message)

    stock = pick_stock(stock_code)
    if not stock:
        return error_response(TRADE_E02.code, TRADE_E02.message)

    if stock.get("status") in ("PAUSED", "CLOSED"):
        return error_response(TRADE_E03.code, TRADE_E03.message)

    price = _decimal(payload.get("order_price"))
    quantity = int(payload.get("order_quantity"))
    if price <= 0:
        return error_response(TRADE_E05.code, TRADE_E05.message)
    if quantity <= 0:
        return error_response(TRADE_E06.code, TRADE_E06.message)

    limit_up = _decimal(stock.get("limitUp") or stock.get("limit_up_price") or stock.get("lastPrice") or 0) * _decimal("1.1")
    limit_down = _decimal(stock.get("limitDown") or stock.get("limit_down_price") or stock.get("lastPrice") or 0) * _decimal("0.9")
    if price > limit_up or price < limit_down:
        return error_response(TRADE_E05.code, TRADE_E05.message)

    trade = store.load_trade()
    order_id = f"ORD-{now_cn_time()}"
    order = {
        "order_id": order_id,
        "investor_id": payload.get("investor_id"),
        "fund_account_id": payload.get("fund_account_id"),
        "security_account_id": payload.get("security_account_id"),
        "stock_code": stock_code,
        "side": side,
        "order_price": _format_amount(price),
        "order_quantity": quantity,
        "filled_quantity": 0,
        "remaining_quantity": quantity,
        "avg_fill_price": None,
        "status": "QUEUED",
        "submitted_at": payload.get("submitted_at"),
    }

    trade.setdefault("orders", []).insert(0, order)

    fills: List[Dict[str, Any]] = []
    market_index = build_market_index()
    market = market_index.get(stock_code)
    if market:
        match_price = Decimal(str(market.get("ask") or market.get("lastPrice") or price))
        should_fill = price >= match_price if side == "BUY" else price <= match_price
        if should_fill:
            fill_qty = min(quantity, 500) if quantity > 500 else quantity
            fill_price = match_price
            fill = {
                "trade_id": f"TRD-{now_cn_time()}",
                "stock_code": stock_code,
                "buy_order_id": order_id if side == "BUY" else None,
                "sell_order_id": order_id if side == "SELL" else None,
                "trade_price": _format_amount(fill_price),
                "trade_quantity": fill_qty,
                "traded_at": now_iso(),
                "investor_id": payload.get("investor_id"),
            }
            fills.append(fill)
            order["filled_quantity"] = fill_qty
            order["remaining_quantity"] = quantity - fill_qty
            order["avg_fill_price"] = _format_amount(fill_price)
            order["status"] = "FILLED" if fill_qty == quantity else "PARTIALLY_FILLED"
            trade.setdefault("fills", []).insert(0, fill)

    store.save_trade(trade)

    await ws_manager.broadcast({
        "type": "order.accepted",
        "event_id": f"EVT-{now_cn_time()}",
        "sent_at": now_iso(),
        "data": {
            "order_id": order_id,
            "stock_code": stock_code,
            "side": side,
            "order_status": order.get("status"),
            "filled_quantity": order.get("filled_quantity"),
            "remaining_quantity": order.get("remaining_quantity"),
        },
    })
    if fills:
        fill = fills[0]
        await ws_manager.broadcast({
            "type": "order.filled" if order.get("status") == "FILLED" else "order.partially_filled",
            "event_id": f"EVT-{now_cn_time()}",
            "sent_at": now_iso(),
            "data": {
                "order_id": order_id,
                "stock_code": stock_code,
                "side": side,
                "trade_id": fill.get("trade_id"),
                "trade_price": fill.get("trade_price"),
                "trade_quantity": fill.get("trade_quantity"),
                "filled_quantity": order.get("filled_quantity"),
                "remaining_quantity": order.get("remaining_quantity"),
                "order_status": order.get("status"),
                "traded_at": fill.get("traded_at"),
            },
        })

    return success_response({"order_id": order_id, "status": "ACCEPTED", "accepted_at": now_iso()})


@router.get("/orders")
async def list_orders(
    investor_id: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
) -> Dict[str, Any]:
    trade = store.load_trade()
    items = trade.get("orders", [])
    if investor_id:
        items = [item for item in items if item.get("investor_id") == investor_id]
    start = (page - 1) * page_size
    end = start + page_size
    return success_response({"items": items[start:end], "page": page, "page_size": page_size, "total": len(items)})


@router.get("/orders/{order_id}")
async def get_order(order_id: str) -> Dict[str, Any]:
    trade = store.load_trade()
    order = next((item for item in trade.get("orders", []) if item.get("order_id") == order_id), None)
    if not order:
        return error_response(COMMON_NOT_FOUND.code, COMMON_NOT_FOUND.message)
    return success_response(order)


@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    trade = store.load_trade()
    order = next((item for item in trade.get("orders", []) if item.get("order_id") == order_id), None)
    if not order:
        return error_response(COMMON_NOT_FOUND.code, COMMON_NOT_FOUND.message)

    status = _resolve_order_status(order)
    if status not in ("QUEUED", "PARTIALLY_FILLED"):
        return error_response(TRADE_E07.code, TRADE_E07.message)

    remaining = int(order.get("remaining_quantity") or 0)
    stock_code = order.get("stock_code")
    order["status"] = "CANCELLED"

    store.save_trade(trade)

    await ws_manager.broadcast({
        "type": "order.cancelled",
        "event_id": f"EVT-{now_cn_time()}",
        "sent_at": now_iso(),
        "data": {
            "order_id": order_id,
            "stock_code": order.get("stock_code"),
            "side": order.get("side"),
            "order_status": "CANCELLED",
            "filled_quantity": order.get("filled_quantity"),
            "remaining_quantity": order.get("remaining_quantity"),
        },
    })

    released = None
    if order.get("side") == "BUY":
        released = {
            "released_resource_type": "FUND",
            "released_amount": _format_amount(_decimal(order.get("order_price")) * remaining),
            "released_quantity": None,
            "stock_code": stock_code,
        }
    else:
        released = {
            "released_resource_type": "SECURITY",
            "released_amount": None,
            "released_quantity": remaining,
            "stock_code": stock_code,
        }

    data = {
        "order_id": order_id,
        "status": "CANCELLED",
        "cancelled_quantity": remaining,
        **released,
    }
    return success_response(data)


@router.websocket("/ws/orders")
async def order_ws(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            message = await ws.receive_text()
            if message:
                try:
                    payload = json.loads(message)
                except Exception:
                    payload = None
                if isinstance(payload, dict) and payload.get("type") == "ping":
                    await ws.send_json({"type": "pong", "sent_at": now_iso()})
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)


@router.get("/fills")
async def list_fills(investor_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    trade = store.load_trade()
    items = trade.get("fills", [])
    if investor_id:
        items = [item for item in items if item.get("investor_id") == investor_id]
    return success_response({"items": items})


@router.get("/market/{stock_code}")
async def get_market(stock_code: str) -> Dict[str, Any]:
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
