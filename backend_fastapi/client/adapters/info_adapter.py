from __future__ import annotations

from typing import Any, Dict

import asyncio
import inspect

from backend_fastapi.mock_modules.info_router import quote, search_stocks


class InfoAdapter:
    def _run(self, result):
        if inspect.iscoroutine(result):
            return asyncio.run(result)
        return result

    def search(self, keyword: str | None) -> Dict[str, Any]:
        return self._run(search_stocks(keyword=keyword))

    def quote(self, stock_code: str) -> Dict[str, Any]:
        return self._run(quote(stock_code))
