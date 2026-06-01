from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from backend_fastapi.client.adapters.account_adapter import AccountAdapter
from backend_fastapi.client.adapters.admin_adapter import AdminAdapter
from backend_fastapi.client.adapters.info_adapter import InfoAdapter
from backend_fastapi.client.adapters.trade_adapter import TradeAdapter
from backend_fastapi.client.certificate_service import CertificateService
from backend_fastapi.client.database import get_session, init_db
from backend_fastapi.client.repositories import ClientRepository
from backend_fastapi.client.schemas import (
    AlertRequest,
    AlertUpdateRequest,
    ApplyClientAccessRequest,
    AuthEnrollRequest,
    AuthLoginRequest,
    AuthRebindRequest,
    AuthVerifyRequest,
    DepositRequest,
    LoginRecordRequest,
    OrderRequest,
    PasswordChangeRequest,
    WithdrawRequest,
)
from backend_fastapi.client.service import ClientService
from backend_fastapi.core.response import client_error, client_ok
from backend_fastapi.mock_modules.mock_store import store


router = APIRouter()


def get_service():
    init_db()
    session = get_session()
    repo = ClientRepository(session)
    try:
        service = ClientService(
            repo=repo,
            account_adapter=AccountAdapter(),
            trade_adapter=TradeAdapter(),
            info_adapter=InfoAdapter(),
            admin_adapter=AdminAdapter(),
            certificate_service=CertificateService(),
        )
        yield service
    finally:
        session.close()


@router.post("/auth/login")
def auth_login(payload: AuthLoginRequest, service: ClientService = Depends(get_service)):
    return service.login(payload.account.strip(), payload.password)


@router.post("/auth/enroll")
def auth_enroll(payload: AuthEnrollRequest, service: ClientService = Depends(get_service)):
    return service.enroll(payload.account.strip(), payload.publicKey)


@router.post("/auth/verify")
def auth_verify(payload: AuthVerifyRequest, service: ClientService = Depends(get_service)):
    return service.verify(payload.account.strip(), payload.signature)


@router.post("/auth/rebind")
def auth_rebind(payload: AuthRebindRequest, service: ClientService = Depends(get_service)):
    return service.rebind(payload.account.strip(), payload.password, payload.phone, payload.idNumber)


@router.get("/auth/me")
def auth_me(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    user = service.repo.get_user(account)
    if not user:
        return client_error("COMMON_NOT_FOUND", "账户不存在")
    return client_ok({"user": {"account": user.account, "name": user.name}})


@router.post("/client/applications")
def apply_access(payload: ApplyClientAccessRequest, service: ClientService = Depends(get_service)):
    return service.apply_access(
        payload.account.strip(),
        payload.password,
        payload.name or payload.account.strip(),
        payload.phone,
        payload.idNumber,
    )


@router.get("/client/applications")
def list_applications(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    applications = service.repo.list_applications(account)
    items = [
        {
            "id": item.id,
            "account": item.account,
            "type": item.type,
            "status": item.status,
            "createdAt": item.created_at,
        }
        for item in applications
    ]
    return client_ok({"applications": items})


@router.get("/account/summary")
def account_summary(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.account_summary(account)


@router.get("/account/funds")
def account_funds(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.funds(account)


@router.get("/account/holdings")
def account_holdings(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.holdings(account)


@router.get("/account/cash-flows")
def account_cash_flows(account: str = Query("admin")):
    funds = store.load_funds()
    flows = [item for item in funds.get("cashFlows", []) if item.get("account") == account]
    return client_ok({"cashFlows": flows})


@router.get("/account/stock-flows")
def account_stock_flows(account: str = Query("admin")):
    securities = store.load_securities()
    flows = [item for item in securities.get("stockFlows", []) if item.get("account") == account]
    return client_ok({"stockFlows": flows})


@router.post("/account/funds/deposit")
def deposit(payload: DepositRequest, service: ClientService = Depends(get_service)):
    account = service.resolve_account(payload.account)
    return service.deposit(account, payload.amount)


@router.post("/account/funds/withdraw")
def withdraw(payload: WithdrawRequest, service: ClientService = Depends(get_service)):
    account = service.resolve_account(payload.account)
    return service.withdraw(account, payload.amount, payload.password)


@router.post("/account/passwords/trade")
def change_trade_password(payload: PasswordChangeRequest, service: ClientService = Depends(get_service)):
    account = service.resolve_account(payload.account)
    return service.change_trade_password(account, payload.currentPassword, payload.nextPassword)


@router.post("/account/passwords/withdraw")
def change_withdraw_password(payload: PasswordChangeRequest, service: ClientService = Depends(get_service)):
    account = service.resolve_account(payload.account)
    return service.change_withdraw_password(account, payload.currentPassword, payload.nextPassword)


@router.get("/market/stocks")
def market_stocks(
    query: str | None = Query(None),
    board: str | None = Query(None),
    symbol: str | None = Query(None),
    service: ClientService = Depends(get_service),
):
    if symbol:
        return service.market_stock_detail(symbol)
    return service.market_stocks(query, board)


@router.get("/market/quotes")
def market_quotes(symbols: str | None = Query(None), service: ClientService = Depends(get_service)):
    response = service.market_stocks(None)
    if not response.get("ok"):
        return response
    stocks = response.get("stocks", [])
    if symbols:
        target = {item.strip() for item in symbols.split(",") if item.strip()}
        stocks = [item for item in stocks if item.get("symbol") in target]
    return client_ok({"stocks": stocks, "asOf": response.get("asOf")})


@router.get("/trade/orders")
def list_orders(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.list_orders(account)


@router.post("/trade/orders")
def place_order(payload: OrderRequest, service: ClientService = Depends(get_service)):
    account = service.resolve_account(payload.account)
    return service.place_order(account, payload.dict())


@router.post("/trade/orders/{order_id}/cancel")
def cancel_order(order_id: str, service: ClientService = Depends(get_service), account: str = Query("admin")):
    return service.cancel_order(order_id, account)


@router.get("/trade/fills")
def list_fills(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.list_fills(account)


@router.get("/client/alerts")
def list_alerts(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.list_alerts(account)


@router.post("/client/alerts")
def create_alert(payload: AlertRequest, service: ClientService = Depends(get_service)):
    account = service.resolve_account(payload.account)
    return service.create_alert(account, payload.symbol, payload.condition, payload.triggerPrice)


@router.patch("/client/alerts/{alert_id}")
def update_alert(alert_id: int, payload: AlertUpdateRequest, service: ClientService = Depends(get_service)):
    account = service.resolve_account(payload.account)
    return service.update_alert(account, alert_id, payload.dict(exclude_unset=True))


@router.delete("/client/alerts/{alert_id}")
def delete_alert(alert_id: int, service: ClientService = Depends(get_service)):
    return service.delete_alert(alert_id)


@router.get("/client/notifications")
def list_notifications(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.list_notifications(account)


@router.patch("/client/notifications/{notification_id}/read")
def mark_notification(notification_id: int, service: ClientService = Depends(get_service)):
    return service.mark_notification_read(notification_id)


@router.get("/client/watchlist")
def list_watchlist(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.list_watchlist(account)


@router.post("/client/watchlist/{symbol}/toggle")
def toggle_watchlist(symbol: str, account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.toggle_watchlist(account, symbol)


@router.get("/client/preferences")
def get_preferences(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.get_preferences(account)


@router.patch("/client/preferences")
def update_preferences(payload: dict, service: ClientService = Depends(get_service)):
    account = service.resolve_account(payload.get("account"))
    return service.update_preferences(account, payload)


@router.get("/client/login-records")
def list_login_records(account: str = Query("admin"), service: ClientService = Depends(get_service)):
    return service.list_login_records(account)


@router.post("/client/login-records")
def add_login_record(payload: LoginRecordRequest, service: ClientService = Depends(get_service)):
    account = service.resolve_account(payload.account)
    return service.add_login_record(account, payload.dict(exclude_unset=True))
