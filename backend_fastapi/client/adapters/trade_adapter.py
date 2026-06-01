from __future__ import annotations

from typing import Any, Dict

import asyncio
import inspect

from backend_fastapi.mock_modules.trade_router import (
    cancel_order,
    get_market,
    get_order,
    list_fills,
    list_orders,
    submit_order,
)


class TradeAdapter:
    def _run(self, result):
        if inspect.iscoroutine(result):
            return asyncio.run(result)
        return result

    def submit_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(submit_order(payload))

    def list_orders(self, investor_id: str, page: int, page_size: int) -> Dict[str, Any]:
        return self._run(list_orders(investor_id=investor_id, page=page, page_size=page_size))

    def get_order(self, order_id: str) -> Dict[str, Any]:
        return self._run(get_order(order_id))

    def cancel_order(self, order_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(cancel_order(order_id, payload))

    def get_market(self, stock_code: str) -> Dict[str, Any]:
        return self._run(get_market(stock_code))

    def list_fills(self, investor_id: str) -> Dict[str, Any]:
        return self._run(list_fills(investor_id=investor_id))
