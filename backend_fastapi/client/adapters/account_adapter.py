from __future__ import annotations

from typing import Any, Dict

from backend_fastapi.core.response import error_response
import asyncio
import inspect

from backend_fastapi.mock_modules.account_router import (
    auth_login,
    change_password,
    freeze_funds,
    freeze_positions,
    get_fund_account,
    get_positions,
    release_funds,
    release_positions,
    settle_funds,
    settle_positions,
    check_association,
)


class AccountAdapter:
    def _run(self, result):
        if inspect.iscoroutine(result):
            return asyncio.run(result)
        return result

    def login(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(auth_login(payload))

    def change_password(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(change_password(payload))

    def get_fund_account(self, fund_account_id: str) -> Dict[str, Any]:
        return self._run(get_fund_account(fund_account_id))

    def get_positions(self, security_account_id: str) -> Dict[str, Any]:
        return self._run(get_positions(security_account_id))

    def freeze_funds(self, fund_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(freeze_funds(fund_account_id, payload))

    def release_funds(self, fund_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(release_funds(fund_account_id, payload))

    def settle_funds(self, fund_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(settle_funds(fund_account_id, payload))

    def freeze_positions(self, security_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(freeze_positions(security_account_id, payload))

    def release_positions(self, security_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(release_positions(security_account_id, payload))

    def settle_positions(self, security_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._run(settle_positions(security_account_id, payload))

    def check_association(self, fund_account_id: str, security_account_id: str, operation_type: str, investor_id: str) -> Dict[str, Any]:
        return self._run(check_association(
            fund_account_id=fund_account_id,
            security_account_id=security_account_id,
            operation_type=operation_type,
            investor_id=investor_id,
        ))
