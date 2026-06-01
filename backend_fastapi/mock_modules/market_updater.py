from __future__ import annotations

import random
from threading import Event, Thread

from backend_fastapi.mock_modules.mock_store import store, now_iso


def _apply_drift(price: float) -> float:
    change = random.random() * 0.008 - 0.004
    next_price = price * (1 + change)
    return round(max(0.01, next_price), 2)


def _update_market() -> None:
    market = store.load_market()
    if not market.get("stocks"):
        return
    updated = []
    for stock in market.get("stocks", []):
        last_price = _apply_drift(float(stock.get("lastPrice", 0)))
        bid = round(last_price * 0.999, 2)
        ask = round(last_price * 1.001, 2)
        volume = int(stock.get("volume", 0)) + random.randint(500, 4000)
        updated.append(
            {
                **stock,
                "lastPrice": last_price,
                "bid": bid,
                "ask": ask,
                "volume": volume,
                "dayHigh": max(stock.get("dayHigh", last_price), last_price),
                "dayLow": min(stock.get("dayLow", last_price), last_price),
                "weekHigh": max(stock.get("weekHigh", last_price), last_price),
                "weekLow": min(stock.get("weekLow", last_price), last_price),
                "monthHigh": max(stock.get("monthHigh", last_price), last_price),
                "monthLow": min(stock.get("monthLow", last_price), last_price),
            }
        )
    market["stocks"] = updated
    market["asOf"] = now_iso()
    store.save_market(market)


def start_market_updater(stop_event: Event | None = None) -> Event:
    if stop_event is None:
        stop_event = Event()

    def loop() -> None:
        while not stop_event.is_set():
            _update_market()
            stop_event.wait(5)

    thread = Thread(target=loop, daemon=True)
    thread.start()
    return stop_event
