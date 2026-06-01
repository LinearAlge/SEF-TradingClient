from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend_fastapi.client.models import (
    ClientAlert,
    ClientApplication,
    ClientCertificate,
    ClientLoginRecord,
    ClientNotification,
    ClientPreferences,
    ClientUser,
    ClientWatchlist,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


class ClientRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_user(self, account: str) -> Optional[ClientUser]:
        return self._session.query(ClientUser).filter_by(account=account).first()

    def create_user(self, account: str, password: str, name: str, phone: str, id_number: str) -> ClientUser:
        user = ClientUser(
            account=account,
            password=password,
            name=name,
            phone=phone,
            id_number=id_number,
            first_login=1,
        )
        self._session.add(user)
        self._session.commit()
        return user

    def update_first_login(self, account: str, first_login: bool) -> None:
        self._session.query(ClientUser).filter_by(account=account).update({"first_login": 1 if first_login else 0})
        self._session.commit()

    def update_password(self, account: str, password: str) -> None:
        self._session.query(ClientUser).filter_by(account=account).update({"password": password})
        self._session.commit()

    def get_certificate(self, account: str) -> Optional[ClientCertificate]:
        return self._session.query(ClientCertificate).filter_by(account=account).first()

    def upsert_certificate(self, account: str, public_key: str) -> None:
        record = self.get_certificate(account)
        if record:
            record.public_key = public_key
            record.updated_at = _now_iso()
        else:
            record = ClientCertificate(account=account, public_key=public_key, updated_at=_now_iso())
            self._session.add(record)
        self._session.commit()

    def clear_certificate(self, account: str) -> None:
        self._session.query(ClientCertificate).filter_by(account=account).delete()
        self._session.commit()

    def add_login_record(self, account: str, time: str, method: str, device: str, status: str) -> None:
        record = ClientLoginRecord(account=account, time=time, method=method, device=device, status=status)
        self._session.add(record)
        self._session.commit()

    def list_login_records(self, account: str) -> List[ClientLoginRecord]:
        return (
            self._session.query(ClientLoginRecord).filter_by(account=account).order_by(ClientLoginRecord.id.desc()).all()
        )

    def create_application(self, account: str, type_name: str, status: str) -> None:
        record = ClientApplication(account=account, type=type_name, status=status, created_at=_now_iso())
        self._session.add(record)
        self._session.commit()

    def list_applications(self, account: str) -> List[ClientApplication]:
        return (
            self._session.query(ClientApplication).filter_by(account=account).order_by(ClientApplication.id.desc()).all()
        )

    def list_alerts(self, account: str) -> List[ClientAlert]:
        return (
            self._session.query(ClientAlert).filter_by(account=account).order_by(ClientAlert.id.desc()).all()
        )

    def create_alert(self, account: str, symbol: str, condition: str, trigger_price: str) -> ClientAlert:
        now = _now_iso()
        alert = ClientAlert(
            account=account,
            symbol=symbol,
            condition=condition,
            trigger_price=trigger_price,
            current_price="--",
            status="监控中",
            last_triggered="--",
            created_at=now,
            updated_at=now,
        )
        self._session.add(alert)
        self._session.commit()
        return alert

    def update_alert(self, alert_id: int, patch: Dict[str, Any]) -> Optional[ClientAlert]:
        self._session.query(ClientAlert).filter_by(id=alert_id).update(patch)
        self._session.commit()
        return self._session.query(ClientAlert).filter_by(id=alert_id).first()

    def delete_alert(self, alert_id: int) -> None:
        self._session.query(ClientAlert).filter_by(id=alert_id).delete()
        self._session.commit()

    def list_notifications(self, account: str) -> List[ClientNotification]:
        return (
            self._session.query(ClientNotification)
            .filter_by(account=account)
            .order_by(ClientNotification.id.desc())
            .all()
        )

    def mark_notification_read(self, notification_id: int) -> None:
        self._session.query(ClientNotification).filter_by(id=notification_id).update({"read": 1})
        self._session.commit()

    def get_preferences(self, account: str) -> Optional[ClientPreferences]:
        return self._session.query(ClientPreferences).filter_by(account=account).first()

    def update_preferences(self, account: str, data: Dict[str, Any]) -> None:
        payload = json.dumps(data, ensure_ascii=False)
        record = self.get_preferences(account)
        if record:
            record.data = payload
        else:
            record = ClientPreferences(account=account, data=payload)
            self._session.add(record)
        self._session.commit()

    def list_watchlist(self, account: str) -> List[ClientWatchlist]:
        return (
            self._session.query(ClientWatchlist).filter_by(account=account).order_by(ClientWatchlist.id.desc()).all()
        )

    def toggle_watchlist(self, account: str, symbol: str) -> bool:
        existing = self._session.query(ClientWatchlist).filter_by(account=account, symbol=symbol).first()
        if existing:
            self._session.delete(existing)
            self._session.commit()
            return False
        record = ClientWatchlist(account=account, symbol=symbol)
        self._session.add(record)
        self._session.commit()
        return True
