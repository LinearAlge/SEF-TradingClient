from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from backend_fastapi.core.errors import (
    ACCOUNT_INSUFFICIENT_FUNDS,
    ACCOUNT_INSUFFICIENT_POSITION,
    COMMON_BAD_REQUEST,
)
from backend_fastapi.core.response import error_response, success_response
from backend_fastapi.mock_modules.mock_store import build_market_index, calc_market_value, now_iso, now_cn_time, store


router = APIRouter()


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _format_amount(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


@router.post("/auth/login")
async def auth_login(payload: Dict[str, Any]) -> Dict[str, Any]:
    fund_account_id = payload.get("fund_account_id")
    password = payload.get("password")
    if not fund_account_id or not password:
        return error_response(COMMON_BAD_REQUEST.code, "账户或密码不能为空")

    funds = store.load_funds()
    account = "admin" if fund_account_id == "FUND000001" else fund_account_id
    stored_password = funds.get("passwords", {}).get(account, {}).get("trade")
    if not stored_password or stored_password != password:
        return error_response("AUTH_BAD_CREDENTIALS", "交易密码错误")

    record = funds.get("accounts", {}).get(account)
    if not record:
        return error_response("COMMON_NOT_FOUND", "账户不存在")

    data = {
        "verified": True,
        "investor_id": "INV000001",
        "fund_account_id": "FUND000001",
        "security_account_id": "SEC000001",
        "first_login": False,
        "token": "mock-jwt-token",
        "expires_at": now_iso(),
    }
    return success_response(data)


@router.post("/auth/password")
async def change_password(payload: Dict[str, Any]) -> Dict[str, Any]:
    fund_account_id = payload.get("fund_account_id")
    password_type = payload.get("password_type")
    old_password = payload.get("old_password")
    new_password = payload.get("new_password")
    if not fund_account_id or not password_type or not old_password or not new_password:
        return error_response(COMMON_BAD_REQUEST.code, "字段缺失")

    account = "admin" if fund_account_id == "FUND000001" else fund_account_id
    funds = store.load_funds()
    password_map = funds.setdefault("passwords", {}).setdefault(account, {})
    stored_password = password_map.get("trade" if password_type == "TRADE" else "withdraw")
    if stored_password != old_password:
        return error_response("AUTH_BAD_CREDENTIALS", "原密码错误")

    key = "trade" if password_type == "TRADE" else "withdraw"
    password_map[key] = new_password
    store.save_funds(funds)
    return success_response({"updated": True})


@router.get("/fund-accounts/{fund_account_id}")
async def get_fund_account(fund_account_id: str) -> Dict[str, Any]:
    account = "admin" if fund_account_id == "FUND000001" else fund_account_id
    funds = store.load_funds()
    record = funds.get("accounts", {}).get(account)
    if not record:
        return error_response("COMMON_NOT_FOUND", "账户不存在")

    balances = record.get("balances", {})
    available = _decimal(balances.get("available", 0))
    frozen = _decimal(balances.get("frozen", 0))

    market_index = build_market_index()
    market_value = _decimal(calc_market_value(record.get("positions", []), market_index))
    total_amount = available + frozen + market_value

    data = {
        "fund_account_id": fund_account_id,
        "investor_id": "INV000001",
        "bank_card_no": "622202******0001",
        "available_amount": _format_amount(available),
        "frozen_amount": _format_amount(frozen),
        "total_amount": _format_amount(total_amount),
        "status": "NORMAL",
    }
    return success_response(data)


@router.post("/fund-accounts/{fund_account_id}/freeze")
async def freeze_funds(fund_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    amount = payload.get("amount")
    if not amount:
        return error_response(COMMON_BAD_REQUEST.code, "字段缺失")

    account = "admin" if fund_account_id == "FUND000001" else fund_account_id
    funds = store.load_funds()
    record = funds.get("accounts", {}).get(account)
    if not record:
        return error_response("COMMON_NOT_FOUND", "账户不存在")

    balances = record.setdefault("balances", {"available": 0, "frozen": 0})
    available = _decimal(balances.get("available", 0))
    frozen = _decimal(balances.get("frozen", 0))
    amount_value = _decimal(amount)

    if available < amount_value:
        return error_response(ACCOUNT_INSUFFICIENT_FUNDS.code, ACCOUNT_INSUFFICIENT_FUNDS.message)

    balances["available"] = float(available - amount_value)
    balances["frozen"] = float(frozen + amount_value)
    order_id = payload.get("order_id")
    if order_id:
        record.setdefault("frozenFunds", {})[order_id] = str(amount_value)
    record["asOf"] = now_iso()
    store.save_funds(funds)

    data = {
        "freeze_id": f"FRZ-{now_cn_time()}",
        "fund_account_id": fund_account_id,
        "frozen_amount": _format_amount(amount_value),
        "available_amount": _format_amount(_decimal(balances["available"])),
    }
    return success_response(data)


@router.post("/fund-accounts/{fund_account_id}/release")
async def release_funds(fund_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    amount = payload.get("amount")
    if not amount:
        return error_response(COMMON_BAD_REQUEST.code, "字段缺失")

    account = "admin" if fund_account_id == "FUND000001" else fund_account_id
    funds = store.load_funds()
    record = funds.get("accounts", {}).get(account)
    if not record:
        return error_response("COMMON_NOT_FOUND", "账户不存在")

    balances = record.setdefault("balances", {"available": 0, "frozen": 0})
    available = _decimal(balances.get("available", 0))
    frozen = _decimal(balances.get("frozen", 0))
    amount_value = _decimal(amount)

    release_amount = min(amount_value, frozen)
    balances["available"] = float(available + release_amount)
    balances["frozen"] = float(frozen - release_amount)
    order_id = payload.get("order_id")
    if order_id:
        frozen_map = record.setdefault("frozenFunds", {})
        current = Decimal(str(frozen_map.get(order_id, "0")))
        remaining = current - release_amount
        if remaining > 0:
            frozen_map[order_id] = str(remaining)
        else:
            frozen_map.pop(order_id, None)
    record["asOf"] = now_iso()
    store.save_funds(funds)

    return success_response({"released_amount": _format_amount(release_amount)})


@router.post("/fund-accounts/{fund_account_id}/settlements")
async def settle_funds(fund_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    change_type = payload.get("change_type")
    amount = payload.get("amount")
    if not change_type or not amount:
        return error_response(COMMON_BAD_REQUEST.code, "字段缺失")

    account = "admin" if fund_account_id == "FUND000001" else fund_account_id
    funds = store.load_funds()
    record = funds.get("accounts", {}).get(account)
    if not record:
        return error_response("COMMON_NOT_FOUND", "账户不存在")

    balances = record.setdefault("balances", {"available": 0, "frozen": 0})
    available = _decimal(balances.get("available", 0))
    frozen = _decimal(balances.get("frozen", 0))
    amount_value = _decimal(amount)

    if change_type == "DEDUCT":
        remaining = amount_value
        if frozen > 0:
            use_frozen = min(frozen, remaining)
            balances["frozen"] = float(frozen - use_frozen)
            remaining -= use_frozen
        if remaining > 0:
            balances["available"] = float(max(Decimal("0"), available - remaining))
        else:
            balances["available"] = float(available)
        flow_type = "买入成交" if payload.get("reason") == "TRADE_FILLED" else "出金"
        funds.setdefault("cashFlows", []).insert(
            0,
            {
                "id": f"CASH-{now_cn_time()}",
                "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "status": "已完成",
                "account": account,
                "type": flow_type,
                "amount": f"-{amount_value:.2f}",
            },
        )
    elif change_type == "INCREASE":
        balances["available"] = float(available + amount_value)
        flow_type = "卖出成交" if payload.get("reason") == "TRADE_FILLED" else "入金"
        funds.setdefault("cashFlows", []).insert(
            0,
            {
                "id": f"CASH-{now_cn_time()}",
                "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "status": "已完成",
                "account": account,
                "type": flow_type,
                "amount": f"+{amount_value:.2f}",
            },
        )
    elif change_type == "RELEASE":
        release_amount = min(amount_value, frozen)
        balances["available"] = float(available + release_amount)
        balances["frozen"] = float(frozen - release_amount)
    else:
        return error_response(COMMON_BAD_REQUEST.code, "不支持的变更类型")

    record["asOf"] = now_iso()
    store.save_funds(funds)
    return success_response({"status": "OK"})


@router.get("/security-accounts/{security_account_id}/positions")
async def get_positions(security_account_id: str) -> Dict[str, Any]:
    account = "admin" if security_account_id == "SEC000001" else security_account_id
    securities = store.load_securities()
    record = securities.get("accounts", {}).get(account)
    if not record:
        return error_response("COMMON_NOT_FOUND", "账户不存在")

    market_index = build_market_index()
    positions = []
    for item in record.get("positions", []):
        total_quantity = sum(lot.get("shares", 0) for lot in item.get("lots", []))
        total_cost = sum((lot.get("price", 0) or 0) * lot.get("shares", 0) for lot in item.get("lots", []))
        cost_price = total_cost / total_quantity if total_quantity else 0
        symbol = item.get("symbol")
        stock_name = market_index.get(symbol, {}).get("name") if symbol else None
        positions.append(
            {
                "security_account_id": security_account_id,
                "investor_id": "INV000001",
                "stock_code": symbol,
                "stock_name": stock_name,
                "total_quantity": total_quantity,
                "available_quantity": item.get("availableShares", total_quantity),
                "frozen_quantity": item.get("frozenShares", 0),
                "cost_price": str(cost_price),
            }
        )

    return success_response({"security_account_id": security_account_id, "positions": positions})


@router.post("/security-accounts/{security_account_id}/positions/freeze")
async def freeze_positions(security_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    stock_code = payload.get("stock_code")
    quantity = payload.get("quantity")
    if not stock_code or not quantity:
        return error_response(COMMON_BAD_REQUEST.code, "字段缺失")

    account = "admin" if security_account_id == "SEC000001" else security_account_id
    securities = store.load_securities()
    record = securities.get("accounts", {}).get(account)
    if not record:
        return error_response("COMMON_NOT_FOUND", "账户不存在")

    position = next((item for item in record.get("positions", []) if item.get("symbol") == stock_code), None)
    if not position:
        return error_response(ACCOUNT_INSUFFICIENT_POSITION.code, ACCOUNT_INSUFFICIENT_POSITION.message)

    available = int(position.get("availableShares", 0))
    quantity_value = int(quantity)
    if available < quantity_value:
        return error_response(ACCOUNT_INSUFFICIENT_POSITION.code, ACCOUNT_INSUFFICIENT_POSITION.message)

    position["availableShares"] = available - quantity_value
    position["frozenShares"] = int(position.get("frozenShares", 0)) + quantity_value
    order_id = payload.get("order_id")
    if order_id:
        position.setdefault("frozenOrders", {})[order_id] = quantity_value
    store.save_securities(securities)

    return success_response({"frozen_quantity": quantity_value})


@router.post("/security-accounts/{security_account_id}/positions/release")
async def release_positions(security_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    stock_code = payload.get("stock_code")
    quantity = payload.get("quantity")
    if not stock_code or not quantity:
        return error_response(COMMON_BAD_REQUEST.code, "字段缺失")

    account = "admin" if security_account_id == "SEC000001" else security_account_id
    securities = store.load_securities()
    record = securities.get("accounts", {}).get(account)
    if not record:
        return error_response("COMMON_NOT_FOUND", "账户不存在")

    position = next((item for item in record.get("positions", []) if item.get("symbol") == stock_code), None)
    if not position:
        return error_response("COMMON_NOT_FOUND", "持仓不存在")

    quantity_value = int(quantity)
    frozen = int(position.get("frozenShares", 0))
    release_qty = min(quantity_value, frozen)
    position["availableShares"] = int(position.get("availableShares", 0)) + release_qty
    position["frozenShares"] = frozen - release_qty
    order_id = payload.get("order_id")
    if order_id:
        position.setdefault("frozenOrders", {}).pop(order_id, None)
    store.save_securities(securities)

    return success_response({"released_quantity": release_qty})


@router.post("/security-accounts/{security_account_id}/positions/settlements")
async def settle_positions(security_account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    stock_code = payload.get("stock_code")
    change_type = payload.get("change_type")
    quantity = payload.get("quantity")
    if not stock_code or not change_type or not quantity:
        return error_response(COMMON_BAD_REQUEST.code, "字段缺失")

    account = "admin" if security_account_id == "SEC000001" else security_account_id
    securities = store.load_securities()
    record = securities.get("accounts", {}).get(account)
    if not record:
        return error_response("COMMON_NOT_FOUND", "账户不存在")

    quantity_value = int(quantity)
    positions = record.setdefault("positions", [])
    position = next((item for item in positions if item.get("symbol") == stock_code), None)
    if not position:
        position = {"symbol": stock_code, "lots": [], "availableShares": 0, "frozenShares": 0}
        positions.append(position)

    if change_type == "INCREASE":
        position.setdefault("lots", []).append({"price": float(payload.get("price", 0)), "shares": quantity_value})
        position["availableShares"] = int(position.get("availableShares", 0)) + quantity_value
        securities.setdefault("stockFlows", []).insert(
            0,
            {
                "id": f"STOCK-{now_cn_time()}",
                "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "status": "已完成",
                "account": account,
                "type": "买入成交",
                "symbol": stock_code,
                "qty": str(quantity_value),
            },
        )
    elif change_type == "DEDUCT":
        frozen = int(position.get("frozenShares", 0))
        if frozen >= quantity_value:
            position["frozenShares"] = frozen - quantity_value
        else:
            position["availableShares"] = max(0, int(position.get("availableShares", 0)) - quantity_value)
        securities.setdefault("stockFlows", []).insert(
            0,
            {
                "id": f"STOCK-{now_cn_time()}",
                "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "status": "已完成",
                "account": account,
                "type": "卖出成交",
                "symbol": stock_code,
                "qty": str(quantity_value),
            },
        )
    elif change_type == "RELEASE":
        position["frozenShares"] = max(0, int(position.get("frozenShares", 0)) - quantity_value)
        position["availableShares"] = int(position.get("availableShares", 0)) + quantity_value
    else:
        return error_response(COMMON_BAD_REQUEST.code, "不支持的变更类型")

    store.save_securities(securities)
    return success_response({"status": "OK"})


@router.get("/associations/check")
async def check_association(
    fund_account_id: str = Query(...),
    security_account_id: str = Query(...),
    operation_type: str = Query(...),
    investor_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    is_related = fund_account_id == "FUND000001" and security_account_id == "SEC000001"
    allow = is_related
    data = {
        "fund_account_id": fund_account_id,
        "security_account_id": security_account_id,
        "investor_id": investor_id or "INV000001",
        "is_related": is_related,
        "is_unique_valid": is_related,
        "allow_operation": allow,
        "fund_account_status": "NORMAL",
        "security_account_status": "NORMAL",
        "reason": None if allow else "资金账户与证券账户未建立绑定关系",
    }
    return success_response(data)
