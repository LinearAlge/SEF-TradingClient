from __future__ import annotations

from typing import Any, Dict

import asyncio
import inspect

from backend_fastapi.mock_modules.admin_router import quote, trade_rule, trading_day_status


class AdminAdapter:
    def _run(self, result):
        if inspect.iscoroutine(result):
            return asyncio.run(result)
        return result

    def quote(self, stock_code: str) -> Dict[str, Any]:
        return self._run(quote(stock_code))

    def trade_rule(self, stock_code: str) -> Dict[str, Any]:
        return self._run(trade_rule(stock_code))

    def trading_day_status(self) -> Dict[str, Any]:
        return self._run(trading_day_status())
