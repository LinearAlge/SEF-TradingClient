from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class ClientUser(Base):
    __tablename__ = "client_users"

    id = Column(Integer, primary_key=True)
    account = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String)
    phone = Column(String)
    id_number = Column(String)
    first_login = Column(Integer, default=1)


class ClientCertificate(Base):
    __tablename__ = "client_certificates"

    id = Column(Integer, primary_key=True)
    account = Column(String, nullable=False)
    public_key = Column(Text)
    updated_at = Column(String)


class ClientSession(Base):
    __tablename__ = "client_sessions"

    id = Column(Integer, primary_key=True)
    account = Column(String, nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(String)


class ClientLoginRecord(Base):
    __tablename__ = "client_login_records"

    id = Column(Integer, primary_key=True)
    account = Column(String, nullable=False)
    time = Column(String)
    method = Column(String)
    device = Column(String)
    status = Column(String)


class ClientApplication(Base):
    __tablename__ = "client_applications"

    id = Column(Integer, primary_key=True)
    account = Column(String, nullable=False)
    type = Column(String)
    status = Column(String)
    created_at = Column(String)


class ClientAlert(Base):
    __tablename__ = "client_alerts"

    id = Column(Integer, primary_key=True)
    account = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    trigger_price = Column(String, nullable=False)
    current_price = Column(String)
    status = Column(String)
    last_triggered = Column(String)
    created_at = Column(String)
    updated_at = Column(String)


class ClientNotification(Base):
    __tablename__ = "client_notifications"

    id = Column(Integer, primary_key=True)
    account = Column(String, nullable=False)
    title = Column(String)
    content = Column(Text)
    read = Column(Integer, default=0)
    created_at = Column(String)


class ClientPreferences(Base):
    __tablename__ = "client_preferences"

    account = Column(String, primary_key=True)
    data = Column(Text)


class ClientWatchlist(Base):
    __tablename__ = "client_watchlist"

    id = Column(Integer, primary_key=True)
    account = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
