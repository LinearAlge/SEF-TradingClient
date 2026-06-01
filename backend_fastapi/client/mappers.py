from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def map_funds_to_client(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "available": float(_decimal(data.get("available_amount") or 0)),
        "frozen": float(_decimal(data.get("frozen_amount") or 0)),
        "marketValue": float(_decimal(data.get("market_value") or 0)),
        "totalEquity": float(_decimal(data.get("total_amount") or 0)),
        "updatedAt": data.get("updated_at"),
    }


def map_holdings_to_client(data: Dict[str, Any], quote_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    holdings = []
    total_market_value = Decimal("0")
    for item in data.get("positions", []):
        stock_code = item.get("stock_code")
        quote = quote_map.get(stock_code, {})
        last_price = _decimal(quote.get("latest_price") or 0)
        total_quantity = int(item.get("total_quantity") or 0)
        cost_price = _decimal(item.get("cost_price") or 0)
        market_value = last_price * total_quantity
        pnl_amount = market_value - cost_price * total_quantity
        pnl_rate = (pnl_amount / (cost_price * total_quantity)) if cost_price and total_quantity else Decimal("0")
        total_market_value += market_value
        holdings.append(
            {
                "symbol": stock_code,
                "name": item.get("stock_name") or quote.get("stock_name") or "--",
                "shares": total_quantity,
                "availableShares": int(item.get("available_quantity") or 0),
                "frozenShares": int(item.get("frozen_quantity") or 0),
                "costPrice": float(cost_price),
                "lastPrice": float(last_price),
                "pnlAmount": float(pnl_amount),
                "pnlRate": float(pnl_rate),
            }
        )
    return {"holdings": holdings, "totalMarketValue": float(total_market_value)}


def map_market_list(items: List[Dict[str, Any]], quote_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for item in items:
        stock_code = item.get("stock_code")
        quote = quote_map.get(stock_code, {})
        result.append(
            {
                "symbol": stock_code,
                "name": item.get("stock_name"),
                "lastPrice": float(_decimal(quote.get("latest_price") or 0)),
                "dayHigh": float(_decimal(quote.get("high_price") or 0)),
                "dayLow": float(_decimal(quote.get("low_price") or 0)),
                "bid": float(_decimal(quote.get("best_bid_price") or 0)),
                "ask": float(_decimal(quote.get("best_ask_price") or 0)),
                "volume": int(quote.get("volume") or 0),
            }
        )
    return result


def map_market_detail(stock: Dict[str, Any], quote: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": stock.get("stock_code"),
        "name": stock.get("stock_name"),
        "board": stock.get("board") or "主板",
        "lastPrice": float(_decimal(quote.get("latest_price") or 0)),
        "bid": float(_decimal(quote.get("best_bid_price") or 0)),
        "ask": float(_decimal(quote.get("best_ask_price") or 0)),
        "dayHigh": float(_decimal(quote.get("high_price") or 0)),
        "dayLow": float(_decimal(quote.get("low_price") or 0)),
        "weekHigh": float(_decimal(stock.get("week_high") or quote.get("high_price") or 0)),
        "weekLow": float(_decimal(stock.get("week_low") or quote.get("low_price") or 0)),
        "monthHigh": float(_decimal(stock.get("month_high") or quote.get("high_price") or 0)),
        "monthLow": float(_decimal(stock.get("month_low") or quote.get("low_price") or 0)),
        "volume": int(quote.get("volume") or 0),
        "announcements": stock.get("announcements") or [],
    }


def map_orders_to_client(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for item in items:
        result.append(
            {
                "id": item.get("order_id"),
                "createdAt": item.get("submitted_at"),
                "symbol": item.get("stock_code"),
                "side": "买入" if item.get("side") == "BUY" else "卖出",
                "price": float(_decimal(item.get("order_price") or 0)),
                "quantity": int(item.get("order_quantity") or 0),
                "filledQuantity": int(item.get("filled_quantity") or 0),
                "avgPrice": float(_decimal(item.get("avg_fill_price") or 0)),
                "status": _map_order_status(item.get("status")),
            }
        )
    return result


def _map_order_status(status: str | None) -> str:
    mapping = {
        "ACCEPTED": "未成交",
        "QUEUED": "未成交",
        "PARTIALLY_FILLED": "部分成交",
        "FILLED": "已成交",
        "CANCELLED": "已撤单",
        "EXPIRED": "已过期",
        "REJECTED": "已拒绝",
    }
    return mapping.get(status or "", status or "未成交")


def map_fills_to_client(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for item in items:
        result.append(
            {
                "id": item.get("trade_id") or item.get("id"),
                "createdAt": item.get("traded_at") or item.get("createdAt"),
                "orderId": item.get("buy_order_id") or item.get("sell_order_id") or item.get("order_id"),
                "symbol": item.get("stock_code") or item.get("symbol"),
                "side": "买入" if item.get("buy_order_id") else "卖出",
                "price": float(_decimal(item.get("trade_price") or item.get("price") or 0)),
                "quantity": int(item.get("trade_quantity") or item.get("quantity") or 0),
            }
        )
    return result
