from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorCode:
    code: str
    message: str


COMMON_BAD_REQUEST = ErrorCode("COMMON_BAD_REQUEST", "请求格式错误")
COMMON_UNAUTHORIZED = ErrorCode("COMMON_UNAUTHORIZED", "未登录或令牌无效")
COMMON_NOT_FOUND = ErrorCode("COMMON_NOT_FOUND", "资源不存在")
COMMON_CONFLICT = ErrorCode("COMMON_CONFLICT", "资源状态冲突")
COMMON_INTERNAL_ERROR = ErrorCode("COMMON_INTERNAL_ERROR", "服务内部错误")

AUTH_BAD_CREDENTIALS = ErrorCode("AUTH_BAD_CREDENTIALS", "交易密码错误")
AUTH_CERT_REQUIRED = ErrorCode("AUTH_CERT_REQUIRED", "需要绑定证书")
AUTH_CERT_INVALID = ErrorCode("AUTH_CERT_INVALID", "证书验证失败")
CLIENT_ACCESS_REQUIRED = ErrorCode("CLIENT_ACCESS_REQUIRED", "未开通客户端权限，请先申请")

TRADE_E01 = ErrorCode("TRADE_E01", "字段缺失")
TRADE_E02 = ErrorCode("TRADE_E02", "股票不存在")
TRADE_E03 = ErrorCode("TRADE_E03", "股票不可交易")
TRADE_E04 = ErrorCode("TRADE_E04", "买卖方向无效")
TRADE_E05 = ErrorCode("TRADE_E05", "价格非法或超出涨跌停范围")
TRADE_E06 = ErrorCode("TRADE_E06", "数量非法")
TRADE_E07 = ErrorCode("TRADE_E07", "状态不允许撤销")

ACCOUNT_INSUFFICIENT_FUNDS = ErrorCode("ACCOUNT_INSUFFICIENT_FUNDS", "可用资金不足")
ACCOUNT_INSUFFICIENT_POSITION = ErrorCode("ACCOUNT_INSUFFICIENT_POSITION", "可用持仓不足")
ACCOUNT_STATUS_BLOCKED = ErrorCode("ACCOUNT_STATUS_BLOCKED", "账户状态不允许当前操作")

EXTERNAL_SERVICE_ERROR = ErrorCode("EXTERNAL_SERVICE_ERROR", "外部服务异常")
