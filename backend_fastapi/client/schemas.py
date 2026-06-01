from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class AuthLoginRequest(BaseModel):
    account: str
    password: str


class AuthEnrollRequest(BaseModel):
    account: str
    publicKey: dict


class AuthVerifyRequest(BaseModel):
    account: str
    signature: str


class AuthRebindRequest(BaseModel):
    account: str
    password: str
    phone: str
    idNumber: str


class ApplyClientAccessRequest(BaseModel):
    account: str
    password: str
    name: Optional[str] = None
    phone: str
    idNumber: Optional[str] = None


class OrderRequest(BaseModel):
    account: Optional[str] = None
    symbol: str
    side: str
    price: float
    quantity: int
    note: Optional[str] = None


class AlertRequest(BaseModel):
    account: Optional[str] = None
    symbol: str
    condition: str
    triggerPrice: str


class AlertUpdateRequest(BaseModel):
    account: Optional[str] = None
    symbol: Optional[str] = None
    condition: Optional[str] = None
    triggerPrice: Optional[str] = None
    currentPrice: Optional[str] = None
    status: Optional[str] = None
    lastTriggered: Optional[str] = None


class DepositRequest(BaseModel):
    account: Optional[str] = None
    amount: float


class WithdrawRequest(BaseModel):
    account: Optional[str] = None
    amount: float
    password: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    account: Optional[str] = None
    currentPassword: str
    nextPassword: str


class LoginRecordRequest(BaseModel):
    account: Optional[str] = None
    time: Optional[str] = None
    method: Optional[str] = None
    device: Optional[str] = None
    status: Optional[str] = None
