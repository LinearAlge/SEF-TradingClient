from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List

from backend_fastapi.client.adapters.account_adapter import AccountAdapter
from backend_fastapi.client.adapters.admin_adapter import AdminAdapter
from backend_fastapi.client.adapters.info_adapter import InfoAdapter
from backend_fastapi.client.adapters.trade_adapter import TradeAdapter
from backend_fastapi.client.certificate_service import CertificateService
from backend_fastapi.client.mappers import (
    map_fills_to_client,
    map_funds_to_client,
    map_holdings_to_client,
    map_market_detail,
    map_market_list,
    map_orders_to_client,
)
from backend_fastapi.client.repositories import ClientRepository
from backend_fastapi.core.cache import session_cache
from backend_fastapi.core.errors import (
    ACCOUNT_INSUFFICIENT_FUNDS,
    ACCOUNT_INSUFFICIENT_POSITION,
    CLIENT_ACCESS_REQUIRED,
    TRADE_E05,
    TRADE_E06,
)
from backend_fastapi.core.response import client_error, client_ok
from backend_fastapi.mock_modules.mock_store import store


@dataclass
class ClientService:
    repo: ClientRepository
    account_adapter: AccountAdapter
    trade_adapter: TradeAdapter
    info_adapter: InfoAdapter
    admin_adapter: AdminAdapter
    certificate_service: CertificateService

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).astimezone().isoformat()

    def _expires_at(self) -> str:
        return (datetime.now(timezone.utc).astimezone() + timedelta(hours=8)).isoformat()

    def resolve_account(self, account: str | None) -> str:
        return account or "admin"

    def resolve_fund_account_id(self, account: str) -> str:
        return "FUND000001" if account == "admin" else account

    def resolve_security_account_id(self, account: str) -> str:
        return "SEC000001" if account == "admin" else account

    def resolve_investor_id(self, account: str) -> str:
        return "INV000001"

    def login(self, account: str, password: str) -> Dict[str, Any]:
        user = self.repo.get_user(account)
        if not user:
            return client_error(CLIENT_ACCESS_REQUIRED.code, CLIENT_ACCESS_REQUIRED.message, {"action": "apply"})

        fund_account_id = self.resolve_fund_account_id(account)
        login_payload = {
            "fund_account_id": fund_account_id,
            "password": password,
            "client_time": self._now_iso(),
        }
        auth_result = self.account_adapter.login(login_payload)
        if not auth_result.get("success"):
            return client_error(auth_result.get("code", "AUTH_BAD_CREDENTIALS"), auth_result.get("message", "登录失败"))

        cert = self.repo.get_certificate(account)
        if not cert or user.first_login:
            return client_ok({
                "action": "enroll",
                "token": "mock-token",
                "investorId": self.resolve_investor_id(account),
                "fundAccountId": self.resolve_fund_account_id(account),
                "securityAccountId": self.resolve_security_account_id(account),
                "expiresAt": self._expires_at(),
            })

        challenge = self._build_challenge(account)
        return client_ok({
            "action": "verify",
            "challenge": challenge,
            "token": "mock-token",
            "investorId": self.resolve_investor_id(account),
            "fundAccountId": self.resolve_fund_account_id(account),
            "securityAccountId": self.resolve_security_account_id(account),
            "expiresAt": self._expires_at(),
        })

    def _build_challenge(self, account: str) -> str:
        key = f"challenge:{account}"
        challenge = f"challenge-{int(datetime.now().timestamp())}"
        session_cache.set(key, challenge, ttl_seconds=600)
        return challenge

    def enroll(self, account: str, public_key: Dict[str, Any]) -> Dict[str, Any]:
        user = self.repo.get_user(account)
        if not user:
            return client_error("COMMON_NOT_FOUND", "账户不存在")

        self.repo.upsert_certificate(account, json_dumps(public_key))
        self.repo.update_first_login(account, False)
        return client_ok({
            "token": "mock-token",
            "user": {"account": user.account, "name": user.name},
            "investorId": self.resolve_investor_id(account),
            "fundAccountId": self.resolve_fund_account_id(account),
            "securityAccountId": self.resolve_security_account_id(account),
            "expiresAt": self._expires_at(),
        })

    def verify(self, account: str, signature: str) -> Dict[str, Any]:
        user = self.repo.get_user(account)
        if not user:
            return client_error("COMMON_NOT_FOUND", "账户不存在")

        cert = self.repo.get_certificate(account)
        if not cert:
            return client_error("AUTH_CERT_REQUIRED", "需要绑定证书")

        challenge = session_cache.get(f"challenge:{account}")
        if not challenge:
            return client_error("COMMON_BAD_REQUEST", "挑战码已失效")

        ok = self.certificate_service.verify_signature(cert.public_key, challenge, signature)
        if not ok:
            return client_error("AUTH_CERT_INVALID", "证书验证失败")

        return client_ok({
            "token": "mock-token",
            "user": {"account": user.account, "name": user.name},
            "investorId": self.resolve_investor_id(account),
            "fundAccountId": self.resolve_fund_account_id(account),
            "securityAccountId": self.resolve_security_account_id(account),
            "expiresAt": self._expires_at(),
        })

    def rebind(self, account: str, password: str, phone: str, id_number: str) -> Dict[str, Any]:
        user = self.repo.get_user(account)
        if not user or user.password != password:
            return client_error("AUTH_BAD_CREDENTIALS", "账号或密码错误")

        if user.phone and user.phone != phone:
            return client_error("COMMON_FORBIDDEN", "身份信息校验失败")

        if user.id_number and user.id_number != id_number:
            return client_error("COMMON_FORBIDDEN", "身份信息校验失败")

        self.repo.clear_certificate(account)
        self.repo.update_first_login(account, True)
        return client_ok({"message": "证书已重置，请重新登录绑定证书"})

    def apply_access(self, account: str, password: str, name: str, phone: str, id_number: str | None) -> Dict[str, Any]:
        if self.repo.get_user(account):
            return client_error("COMMON_CONFLICT", "账户已开通客户端权限")

        fund_account_id = self.resolve_fund_account_id(account)
        profile = self.account_adapter.get_fund_account(fund_account_id)
        if not profile.get("success"):
            return client_error(profile.get("code", "COMMON_NOT_FOUND"), profile.get("message", "账户不存在"))

        funds = store.load_funds()
        record = funds.get("accounts", {}).get(account)
        if record and record.get("phone") and record.get("phone") != phone:
            return client_error("COMMON_FORBIDDEN", "手机号校验失败")

        self.repo.create_user(account=account, password=password, name=name, phone=phone, id_number=id_number or "")
        self.repo.create_application(account, "client-access", "approved")
        return client_ok({"status": "approved"})

    def account_summary(self, account: str) -> Dict[str, Any]:
        fund_account_id = self.resolve_fund_account_id(account)
        security_account_id = self.resolve_security_account_id(account)

        fund_data = self.account_adapter.get_fund_account(fund_account_id)
        if not fund_data.get("success"):
            return client_error(fund_data.get("code", "COMMON_INTERNAL_ERROR"), fund_data.get("message", "查询失败"))

        position_data = self.account_adapter.get_positions(security_account_id)
        quote_map = self._build_quote_map(position_data.get("data", {}).get("positions", []))
        holdings_result = map_holdings_to_client(position_data.get("data", {}), quote_map)

        base_data = fund_data.get("data", {})
        total_amount = (
            float(base_data.get("available_amount", 0))
            + float(base_data.get("frozen_amount", 0))
            + holdings_result.get("totalMarketValue", 0)
        )
        funds_client = map_funds_to_client({
            **base_data,
            "market_value": holdings_result.get("totalMarketValue"),
            "total_amount": total_amount,
            "updated_at": self._now_iso(),
        })

        return client_ok({
            "account": account,
            **funds_client,
        })

    def funds(self, account: str) -> Dict[str, Any]:
        fund_account_id = self.resolve_fund_account_id(account)
        security_account_id = self.resolve_security_account_id(account)
        fund_data = self.account_adapter.get_fund_account(fund_account_id)
        if not fund_data.get("success"):
            return client_error(fund_data.get("code", "COMMON_INTERNAL_ERROR"), fund_data.get("message", "查询失败"))

        position_data = self.account_adapter.get_positions(security_account_id)
        quote_map = self._build_quote_map(position_data.get("data", {}).get("positions", []))
        holdings_result = map_holdings_to_client(position_data.get("data", {}), quote_map)
        base_data = fund_data.get("data", {})
        total_amount = (
            float(base_data.get("available_amount", 0))
            + float(base_data.get("frozen_amount", 0))
            + holdings_result.get("totalMarketValue", 0)
        )

        return client_ok(map_funds_to_client({
            **base_data,
            "market_value": holdings_result.get("totalMarketValue"),
            "total_amount": total_amount,
            "updated_at": self._now_iso(),
        }))

    def holdings(self, account: str) -> Dict[str, Any]:
        security_account_id = self.resolve_security_account_id(account)
        position_data = self.account_adapter.get_positions(security_account_id)
        if not position_data.get("success"):
            return client_error(position_data.get("code", "COMMON_INTERNAL_ERROR"), position_data.get("message", "查询失败"))

        quote_map = self._build_quote_map(position_data.get("data", {}).get("positions", []))
        mapped = map_holdings_to_client(position_data.get("data", {}), quote_map)
        return client_ok({
            "holdings": mapped.get("holdings", []),
            "totalMarketValue": mapped.get("totalMarketValue", 0),
            "asOf": self._now_iso(),
        })

    def market_stocks(self, query: str | None, board: str | None = None) -> Dict[str, Any]:
        stocks_resp = self.info_adapter.search(query)
        if not stocks_resp.get("success"):
            return client_error(stocks_resp.get("code", "COMMON_INTERNAL_ERROR"), stocks_resp.get("message", "查询失败"))

        items = stocks_resp.get("data", {}).get("items", [])
        if board:
            items = [item for item in items if item.get("board") == board]
        quote_map = self._quote_map_from_info(items)
        mapped = map_market_list(items, quote_map)
        return client_ok({"stocks": mapped, "asOf": self._now_iso()})

    def market_stock_detail(self, stock_code: str) -> Dict[str, Any]:
        stocks_resp = self.info_adapter.search(stock_code)
        if not stocks_resp.get("success"):
            return client_error(stocks_resp.get("code", "COMMON_INTERNAL_ERROR"), stocks_resp.get("message", "查询失败"))

        stock_items = stocks_resp.get("data", {}).get("items", [])
        stock = next((item for item in stock_items if item.get("stock_code") == stock_code), None)
        if not stock:
            return client_error("COMMON_NOT_FOUND", "股票不存在")

        quote_resp = self.info_adapter.quote(stock_code)
        if not quote_resp.get("success"):
            return client_error(quote_resp.get("code", "COMMON_INTERNAL_ERROR"), quote_resp.get("message", "查询失败"))

        mapped = map_market_detail(stock, quote_resp.get("data", {}))
        return client_ok({"stock": mapped, "asOf": self._now_iso()})

    def place_order(self, account: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        fund_account_id = self.resolve_fund_account_id(account)
        security_account_id = self.resolve_security_account_id(account)
        investor_id = self.resolve_investor_id(account)
        side = "BUY" if payload.get("side") == "买入" else "SELL"
        price = Decimal(str(payload.get("price")))
        quantity = int(payload.get("quantity"))

        if quantity <= 0:
            return client_error(TRADE_E06.code, TRADE_E06.message)

        association = self.account_adapter.check_association(
            fund_account_id=fund_account_id,
            security_account_id=security_account_id,
            operation_type="BUY_ORDER" if side == "BUY" else "SELL_ORDER",
            investor_id=investor_id,
        )
        if not association.get("success") or not association.get("data", {}).get("allow_operation"):
            return client_error("ACCOUNT_STATUS_BLOCKED", association.get("data", {}).get("reason", "账户校验失败"))

        rule_resp = self.admin_adapter.trade_rule(payload.get("symbol"))
        if not rule_resp.get("success"):
            return client_error(rule_resp.get("code", "COMMON_INTERNAL_ERROR"), rule_resp.get("message", "规则查询失败"))

        rule = rule_resp.get("data", {})
        if rule.get("stock_status") != "OPEN":
            return client_error("TRADE_E03", "股票不可交易")

        limit_up = Decimal(str(rule.get("limit_up_price")))
        limit_down = Decimal(str(rule.get("limit_down_price")))
        if price > limit_up or price < limit_down:
            return client_error(TRADE_E05.code, TRADE_E05.message)

        if side == "BUY":
            amount = price * Decimal(quantity)
            freeze_resp = self.account_adapter.freeze_funds(
                fund_account_id,
                {
                    "order_id": payload.get("client_order_id") or f"CLI-{int(datetime.now().timestamp())}",
                    "amount": str(amount),
                    "reason": "BUY_ORDER",
                    "requested_at": self._now_iso(),
                },
            )
            if not freeze_resp.get("success"):
                return client_error(ACCOUNT_INSUFFICIENT_FUNDS.code, ACCOUNT_INSUFFICIENT_FUNDS.message)
        else:
            freeze_resp = self.account_adapter.freeze_positions(
                security_account_id,
                {
                    "order_id": payload.get("client_order_id") or f"CLI-{int(datetime.now().timestamp())}",
                    "stock_code": payload.get("symbol"),
                    "quantity": quantity,
                    "reason": "SELL_ORDER",
                },
            )
            if not freeze_resp.get("success"):
                return client_error(ACCOUNT_INSUFFICIENT_POSITION.code, ACCOUNT_INSUFFICIENT_POSITION.message)

        client_order_id = payload.get("client_order_id") or f"CLI-{int(datetime.now().timestamp())}"
        trade_payload = {
            "client_order_id": client_order_id,
            "investor_id": investor_id,
            "fund_account_id": fund_account_id,
            "security_account_id": security_account_id,
            "stock_code": payload.get("symbol"),
            "side": side,
            "order_price": str(price),
            "order_quantity": quantity,
            "submitted_at": self._now_iso(),
        }
        trade_resp = self.trade_adapter.submit_order(trade_payload)
        if not trade_resp.get("success"):
            if side == "BUY":
                self.account_adapter.release_funds(
                    fund_account_id,
                    {"order_id": client_order_id, "amount": str(price * Decimal(quantity)), "reason": "CANCELLED"},
                )
            else:
                self.account_adapter.release_positions(
                    security_account_id,
                    {
                        "order_id": client_order_id,
                        "stock_code": payload.get("symbol"),
                        "quantity": quantity,
                        "reason": "CANCELLED",
                    },
                )
            return client_error(trade_resp.get("code", "TRADE_SUBMIT_FAILED"), trade_resp.get("message", "委托提交失败"))

        fills_resp = self.trade_adapter.list_fills(investor_id)
        fills = fills_resp.get("data", {}).get("items", []) if fills_resp.get("success") else []
        order_id = trade_resp.get("data", {}).get("order_id")
        for fill in fills:
            if order_id and order_id not in (fill.get("buy_order_id"), fill.get("sell_order_id")):
                continue
            fill_price = Decimal(str(fill.get("trade_price")))
            fill_qty = int(fill.get("trade_quantity"))
            amount = fill_price * Decimal(fill_qty)
            if side == "BUY":
                self.account_adapter.settle_funds(fund_account_id, {"change_type": "DEDUCT", "amount": str(amount), "reason": "TRADE_FILLED"})
                self.account_adapter.settle_positions(
                    security_account_id,
                    {
                        "stock_code": payload.get("symbol"),
                        "change_type": "INCREASE",
                        "quantity": fill_qty,
                        "price": str(fill_price),
                        "reason": "TRADE_FILLED",
                    },
                )
                frozen_amount = price * Decimal(fill_qty)
                diff_amount = frozen_amount - amount
                if diff_amount > 0:
                    self.account_adapter.release_funds(
                        fund_account_id,
                        {"order_id": client_order_id, "amount": str(diff_amount), "reason": "PRICE_DIFF"},
                    )
            else:
                self.account_adapter.settle_positions(
                    security_account_id,
                    {
                        "stock_code": payload.get("symbol"),
                        "change_type": "DEDUCT",
                        "quantity": fill_qty,
                        "reason": "TRADE_FILLED",
                    },
                )
                self.account_adapter.settle_funds(fund_account_id, {"change_type": "INCREASE", "amount": str(amount), "reason": "TRADE_FILLED"})

        orders_resp = self.trade_adapter.list_orders(investor_id, page=1, page_size=20)
        orders = orders_resp.get("data", {}).get("items", []) if orders_resp.get("success") else []
        mapped_orders = map_orders_to_client(orders)
        order = next((item for item in mapped_orders if item.get("id") == trade_resp.get("data", {}).get("order_id")), None)
        return client_ok({"order": order, "fills": []})

    def cancel_order(self, order_id: str, account: str) -> Dict[str, Any]:
        cancel_resp = self.trade_adapter.cancel_order(order_id, {"investor_id": self.resolve_investor_id(account), "cancelled_at": self._now_iso()})
        if not cancel_resp.get("success"):
            return client_error(cancel_resp.get("code", "TRADE_E07"), cancel_resp.get("message", "撤单失败"))

        data = cancel_resp.get("data", {})
        released_type = data.get("released_resource_type")
        if released_type == "FUND":
            released_amount = data.get("released_amount")
            if released_amount:
                self.account_adapter.release_funds(
                    self.resolve_fund_account_id(account),
                    {"order_id": order_id, "amount": str(released_amount), "reason": "CANCELLED"},
                )
        elif released_type == "SECURITY":
            released_quantity = data.get("released_quantity")
            stock_code = data.get("stock_code")
            if released_quantity and stock_code:
                self.account_adapter.release_positions(
                    self.resolve_security_account_id(account),
                    {
                        "order_id": order_id,
                        "stock_code": stock_code,
                        "quantity": int(released_quantity),
                        "reason": "CANCELLED",
                    },
                )

        return client_ok({"order": {"id": order_id, "status": "已撤单"}})

    def list_orders(self, account: str) -> Dict[str, Any]:
        investor_id = self.resolve_investor_id(account)
        orders_resp = self.trade_adapter.list_orders(investor_id, page=1, page_size=50)
        if not orders_resp.get("success"):
            return client_error(orders_resp.get("code", "COMMON_INTERNAL_ERROR"), orders_resp.get("message", "查询失败"))
        mapped = map_orders_to_client(orders_resp.get("data", {}).get("items", []))
        return client_ok({"orders": mapped})

    def list_fills(self, account: str) -> Dict[str, Any]:
        fills_resp = self.trade_adapter.list_fills(self.resolve_investor_id(account))
        data = fills_resp.get("data", {}).get("items", []) if fills_resp.get("success") else []
        fills = map_fills_to_client(data)
        return client_ok({"fills": fills})

    def deposit(self, account: str, amount: float) -> Dict[str, Any]:
        funds = store.load_funds()
        record = funds.get("accounts", {}).get(account)
        if not record:
            return client_error("COMMON_NOT_FOUND", "账户不存在")
        balances = record.get("balances", {})
        amount_value = Decimal(str(amount))
        balances["available"] = float(Decimal(str(balances.get("available", 0))) + amount_value)
        funds.setdefault("cashFlows", []).insert(
            0,
            {
                "id": f"CASH-{int(datetime.now().timestamp())}",
                "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "status": "已完成",
                "account": account,
                "type": "入金",
                "amount": f"+{amount_value:.2f}",
            },
        )
        store.save_funds(funds)
        return client_ok({"ok": True})

    def withdraw(self, account: str, amount: float, password: str | None) -> Dict[str, Any]:
        fund_account_id = self.resolve_fund_account_id(account)
        funds = store.load_funds()
        record = funds.get("accounts", {}).get(account)
        if not record:
            return client_error("COMMON_NOT_FOUND", "账户不存在")
        stored = funds.get("passwords", {}).get(account, {}).get("withdraw")
        if stored and password and stored != password:
            return client_error("ACCOUNT_WITHDRAW_PASSWORD_ERROR", "取款密码错误")
        balances = record.get("balances", {})
        available = Decimal(str(balances.get("available", 0)))
        amount_value = Decimal(str(amount))
        if amount_value > available:
            return client_error("ACCOUNT_INSUFFICIENT_FUNDS", "取款金额超过可用资金")
        balances["available"] = float(available - amount_value)
        funds.setdefault("cashFlows", []).insert(
            0,
            {
                "id": f"CASH-{int(datetime.now().timestamp())}",
                "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "status": "已完成",
                "account": account,
                "type": "出金",
                "amount": f"-{amount_value:.2f}",
            },
        )
        store.save_funds(funds)
        return client_ok({"ok": True})

    def change_trade_password(self, account: str, current_password: str, next_password: str) -> Dict[str, Any]:
        fund_account_id = self.resolve_fund_account_id(account)
        resp = self.account_adapter.change_password({
            "fund_account_id": fund_account_id,
            "password_type": "TRADE",
            "old_password": current_password,
            "new_password": next_password,
        })
        if not resp.get("success"):
            return client_error(resp.get("code", "COMMON_INTERNAL_ERROR"), resp.get("message", "修改失败"))
        return client_ok({"ok": True})

    def change_withdraw_password(self, account: str, current_password: str, next_password: str) -> Dict[str, Any]:
        fund_account_id = self.resolve_fund_account_id(account)
        resp = self.account_adapter.change_password({
            "fund_account_id": fund_account_id,
            "password_type": "WITHDRAW",
            "old_password": current_password,
            "new_password": next_password,
        })
        if not resp.get("success"):
            return client_error(resp.get("code", "COMMON_INTERNAL_ERROR"), resp.get("message", "修改失败"))
        return client_ok({"ok": True})

    def list_alerts(self, account: str) -> Dict[str, Any]:
        alerts = [
            {
                "id": item.id,
                "symbol": item.symbol,
                "condition": item.condition,
                "triggerPrice": item.trigger_price,
                "currentPrice": item.current_price,
                "status": item.status,
                "lastTriggered": item.last_triggered,
            }
            for item in self.repo.list_alerts(account)
        ]
        return client_ok({"alerts": alerts})

    def create_alert(self, account: str, symbol: str, condition: str, trigger_price: str) -> Dict[str, Any]:
        alert = self.repo.create_alert(account, symbol, condition, trigger_price)
        return client_ok({
            "alert": {
                "id": alert.id,
                "symbol": alert.symbol,
                "condition": alert.condition,
                "triggerPrice": alert.trigger_price,
                "currentPrice": alert.current_price,
                "status": alert.status,
                "lastTriggered": alert.last_triggered,
            }
        })

    def update_alert(self, account: str, alert_id: int, patch: Dict[str, Any]) -> Dict[str, Any]:
        mapped = {}
        for key, value in patch.items():
            if key == "triggerPrice":
                mapped["trigger_price"] = value
            elif key == "currentPrice":
                mapped["current_price"] = value
            elif key == "lastTriggered":
                mapped["last_triggered"] = value
            else:
                mapped[key] = value
        mapped["updated_at"] = self._now_iso()
        alert = self.repo.update_alert(alert_id, mapped)
        if not alert:
            return client_error("COMMON_NOT_FOUND", "提醒不存在")
        return client_ok({
            "alert": {
                "id": alert.id,
                "symbol": alert.symbol,
                "condition": alert.condition,
                "triggerPrice": alert.trigger_price,
                "currentPrice": alert.current_price,
                "status": alert.status,
                "lastTriggered": alert.last_triggered,
            }
        })

    def delete_alert(self, alert_id: int) -> Dict[str, Any]:
        self.repo.delete_alert(alert_id)
        return client_ok({"ok": True})

    def list_notifications(self, account: str) -> Dict[str, Any]:
        items = [
            {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "read": item.read,
                "created_at": item.created_at,
            }
            for item in self.repo.list_notifications(account)
        ]
        return client_ok({"notifications": items})

    def mark_notification_read(self, notification_id: int) -> Dict[str, Any]:
        self.repo.mark_notification_read(notification_id)
        return client_ok({"ok": True})

    def list_watchlist(self, account: str) -> Dict[str, Any]:
        watchlist = [item.symbol for item in self.repo.list_watchlist(account)]
        return client_ok({"watchlist": watchlist})

    def toggle_watchlist(self, account: str, symbol: str) -> Dict[str, Any]:
        enabled = self.repo.toggle_watchlist(account, symbol)
        return client_ok({"enabled": enabled})

    def get_preferences(self, account: str) -> Dict[str, Any]:
        pref = self.repo.get_preferences(account)
        data = {}
        if pref and pref.data:
            try:
                data = json_loads(pref.data)
            except ValueError:
                data = {}
        return client_ok({"preferences": data})

    def update_preferences(self, account: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = {key: value for key, value in payload.items() if key != "account"}
        self.repo.update_preferences(account, cleaned)
        return client_ok({"ok": True})

    def add_login_record(self, account: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.repo.add_login_record(
            account,
            payload.get("time") or datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            payload.get("method") or "密码登录",
            payload.get("device") or "未知",
            payload.get("status") or "成功",
        )
        return client_ok({"ok": True})

    def list_login_records(self, account: str) -> Dict[str, Any]:
        records = [
            {
                "id": item.id,
                "time": item.time,
                "method": item.method,
                "device": item.device,
                "status": item.status,
            }
            for item in self.repo.list_login_records(account)
        ]
        return client_ok({"records": records})

    def _build_quote_map(self, positions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        quote_map: Dict[str, Dict[str, Any]] = {}
        for item in positions:
            stock_code = item.get("stock_code")
            quote_resp = self.info_adapter.quote(stock_code)
            if quote_resp.get("success"):
                quote_map[stock_code] = quote_resp.get("data", {})
        return quote_map

    def _quote_map_from_info(self, items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        quote_map: Dict[str, Dict[str, Any]] = {}
        for item in items:
            stock_code = item.get("stock_code")
            quote_resp = self.info_adapter.quote(stock_code)
            if quote_resp.get("success"):
                quote_map[stock_code] = quote_resp.get("data", {})
        return quote_map


def json_dumps(payload: Any) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False)


def json_loads(payload: str) -> Any:
    import json

    return json.loads(payload)


