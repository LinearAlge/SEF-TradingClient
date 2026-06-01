from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend_fastapi.core.config import DATA_DIR


@dataclass
class MockStore:
    data_dir: Path

    def _read_json(self, filename: str, default: Any) -> Any:
        path = self.data_dir / filename
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return default

    def _write_json(self, filename: str, payload: Any) -> None:
        path = self.data_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_funds(self) -> Dict[str, Any]:
        return self._read_json("mock-funds-db.json", {"accounts": {}, "cashFlows": [], "passwords": {}})

    def save_funds(self, data: Dict[str, Any]) -> None:
        self._write_json("mock-funds-db.json", data)

    def load_securities(self) -> Dict[str, Any]:
        return self._read_json("mock-securities-db.json", {"accounts": {}, "stockFlows": []})

    def save_securities(self, data: Dict[str, Any]) -> None:
        self._write_json("mock-securities-db.json", data)

    def load_trade(self) -> Dict[str, Any]:
        return self._read_json("mock-exchange-db.json", {"accounts": {}, "orders": [], "fills": []})

    def save_trade(self, data: Dict[str, Any]) -> None:
        self._write_json("mock-exchange-db.json", data)

    def load_market(self) -> Dict[str, Any]:
        return self._read_json("mock-market-db.json", {"asOf": "", "stocks": []})

    def save_market(self, data: Dict[str, Any]) -> None:
        self._write_json("mock-market-db.json", data)


store = MockStore(DATA_DIR)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def now_cn_time() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def build_market_index() -> Dict[str, Dict[str, Any]]:
    market = store.load_market()
    index: Dict[str, Dict[str, Any]] = {}
    for item in market.get("stocks", []):
        if "symbol" in item:
            index[item["symbol"]] = item
    return index


def pick_stock(stock_code: str) -> Optional[Dict[str, Any]]:
    market = store.load_market()
    for item in market.get("stocks", []):
        if item.get("symbol") == stock_code:
            return item
    return None


def calc_market_value(positions: List[Dict[str, Any]], market_index: Dict[str, Dict[str, Any]]) -> float:
    total = 0.0
    for position in positions:
        symbol = position.get("symbol")
        lots = position.get("lots", [])
        shares = sum(lot.get("shares", 0) for lot in lots)
        last_price = float(market_index.get(symbol, {}).get("lastPrice") or position.get("lastPrice") or 0)
        total += shares * last_price
    return total


def ensure_fund_record(account: str) -> Dict[str, Any]:
    data = store.load_funds()
    record = data.setdefault("accounts", {}).setdefault(
        account,
        {
            "fundAccountId": "FUND000001",
            "currency": "CNY",
            "phone": "13800000000",
            "idNumber": "110101199001011234",
            "balances": {"available": 200000, "frozen": 0},
            "positions": [],
        },
    )
    return record


def ensure_security_record(account: str) -> Dict[str, Any]:
    data = store.load_securities()
    record = data.setdefault("accounts", {}).setdefault(
        account,
        {
            "securitiesAccountId": "SEC000001",
            "positions": [],
        },
    )
    return record


def ensure_trade_record(account: str) -> Dict[str, Any]:
    data = store.load_trade()
    record = data.setdefault("accounts", {}).setdefault(account, {"account": account})
    return record


__all__ = [
    "store",
    "now_iso",
    "now_cn_time",
    "build_market_index",
    "pick_stock",
    "calc_market_value",
    "ensure_fund_record",
    "ensure_security_record",
    "ensure_trade_record",
]
