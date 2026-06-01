from __future__ import annotations

from backend_fastapi.mock_modules.mock_store import store


def seed_defaults() -> None:
    funds = store.load_funds()
    if "admin" not in funds.get("accounts", {}):
        funds["accounts"]["admin"] = {
            "fundAccountId": "FUND000001",
            "currency": "CNY",
            "phone": "13800000000",
            "idNumber": "110101199001011234",
            "balances": {"available": 200000, "frozen": 0},
            "positions": [],
        }
    if "admin" not in funds.get("passwords", {}):
        funds.setdefault("passwords", {})["admin"] = {"trade": "123456", "withdraw": "654321"}
    store.save_funds(funds)

    securities = store.load_securities()
    if "admin" not in securities.get("accounts", {}):
        securities["accounts"]["admin"] = {"securitiesAccountId": "SEC000001", "positions": []}
    store.save_securities(securities)

    trade = store.load_trade()
    trade.setdefault("accounts", {}).setdefault("admin", {"account": "admin"})
    store.save_trade(trade)

    market = store.load_market()
    if not market.get("stocks"):
        market["stocks"] = [
            {
                "symbol": "600001",
                "name": "石英系统",
                "board": "主板",
                "lastPrice": 150.0,
                "bid": 149.8,
                "ask": 150.2,
                "volume": 1000000,
                "dayHigh": 152.0,
                "dayLow": 147.0,
                "weekHigh": 155.0,
                "weekLow": 146.0,
                "monthHigh": 160.0,
                "monthLow": 142.0,
                "announcements": ["发布2026年一季度业绩快报"],
            }
        ]
        market["asOf"] = ""
    store.save_market(market)
