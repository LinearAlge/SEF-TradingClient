# API Contract

本文档描述当前前端依赖的统一网关 API，以及 mock 外部服务接口。

## 1. 统一网关 API（前端只调用这一个端口来访问所有后端服务）

Base URL: `VITE_CLIENT_API_BASE`（默认 http://localhost:8000/api/client）

说明：登录后会返回 `token`，前端需保存并在后续请求头加入 `Authorization: Bearer <token>`。

前端只调用统一网关；网关内部再去调用 SQLite 与 mock 外部服务。

### POST /api/auth/login

用途：登录，返回证书流程动作。

Request Body:
```json
{
  "account": "admin",
  "password": "123456"
}
```

Response:
```json
{
  "ok": true,
  "action": "enroll"
}
```

错误响应示例：
```json
{
  "ok": false,
  "message": "未开通客户端权限，请先申请",
  "action": "apply"
}
```

### POST /api/auth/enroll

用途：首次登录绑定证书。

Request Body:
```json
{
  "account": "admin",
  "publicKey": {"kty": "RSA", "n": "...", "e": "AQAB"}
}
```

Response:
```json
{
  "ok": true,
  "token": "mock-token",
  "user": {"name": "admin", "account": "admin"}
}
```

### POST /api/auth/verify

用途：证书挑战验证。

Request Body:
```json
{
  "account": "admin",
  "signature": "base64"
}
```

Response:
```json
{
  "ok": true,
  "token": "mock-token",
  "user": {"name": "admin", "account": "admin"}
}
```

### POST /api/auth/rebind

用途：重绑证书（使用资金账户身份校验）。

Request Body:
```json
{
  "account": "admin",
  "password": "123456",
  "phone": "13800000000",
  "idNumber": "110101199001011234"
}
```

Response:
```json
{
  "ok": true,
  "message": "证书已重置，请重新登录绑定证书",
  "user": {"name": "admin", "account": "admin"}
}
```

### GET /api/auth/me

用途：查询客户端账户信息。

Query:
```
account=admin
```

Response:
```json
{
  "ok": true,
  "user": {"account": "admin", "name": "admin"}
}
```

### POST /api/client/applications

用途：申请客户端权限。

Request Body:
```json
{
  "account": "admin",
  "password": "123456",
  "name": "admin",
  "phone": "13800000000",
  "idNumber": "110101199001011234"
}
```

Response:
```json
{
  "ok": true,
  "status": "approved"
}
```

### GET /api/client/applications

用途：查询申请记录。

Query:
```
account=admin
```

Response:
```json
{
  "ok": true,
  "applications": [
    {
      "id": 1,
      "account": "admin",
      "type": "client-access",
      "status": "approved",
      "created_at": "2026-05-30T04:00:00.000Z"
    }
  ]
}
```

### GET /api/account/summary

用途：资金 + 持仓合并摘要。

Response:
```json
{
  "ok": true,
  "account": "admin",
  "fundAccountId": "CASH-20001",
  "currency": "CNY",
  "available": 200000,
  "frozen": 0,
  "marketValue": 14853,
  "totalEquity": 214853,
  "updatedAt": "2026-05-30T04:19:47.321+08:00"
}
```

### GET /api/account/funds

用途：资金余额（已合并持仓市值）。

Response:
```json
{
  "ok": true,
  "account": "admin",
  "fundAccountId": "CASH-20001",
  "currency": "CNY",
  "available": 200000,
  "frozen": 0,
  "marketValue": 14853,
  "totalEquity": 214853,
  "updatedAt": "2026-05-30T04:19:47.321+08:00"
}
```

### GET /api/account/holdings

用途：持仓。

Response:
```json
{
  "ok": true,
  "account": "admin",
  "securitiesAccountId": "SEC-10001",
  "asOf": "2026-05-30T04:16:18.736+08:00",
  "totalMarketValue": 14853,
  "holdings": [
    {
      "symbol": "600001",
      "name": "石英系统",
      "shares": 200,
      "availableShares": 200,
      "frozenShares": 0,
      "costPrice": 150.04,
      "lastPrice": 148.53,
      "pnlAmount": -302,
      "pnlRate": -0.01
    }
  ]
}
```

### GET /api/account/cash-flows

用途：资金流水。

Response:
```json
{
  "ok": true,
  "cashFlows": [
    {"id": "CASH-...", "time": "2026/5/30 04:16:18", "type": "买入成交", "amount": "-14853.00", "status": "已完成"}
  ]
}
```

### GET /api/account/stock-flows

用途：证券流水。

Response:
```json
{
  "ok": true,
  "stockFlows": [
    {"id": "STOCK-...", "time": "2026/5/30 04:16:18", "type": "买入成交", "symbol": "600001", "qty": "100", "status": "已完成"}
  ]
}
```

### POST /api/account/funds/deposit

Request Body:
```json
{"account": "admin", "amount": 10000}
```

Response:
```json
{"ok": true}
```

### POST /api/account/funds/withdraw

Request Body:
```json
{"account": "admin", "amount": 5000, "password": "654321"}
```

Response:
```json
{"ok": true}
```

### POST /api/account/passwords/trade

Request Body:
```json
{"account": "admin", "currentPassword": "123456", "nextPassword": "1234567"}
```

Response:
```json
{"ok": true}
```

### POST /api/account/passwords/withdraw

Request Body:
```json
{"account": "admin", "currentPassword": "654321", "nextPassword": "654322"}
```

Response:
```json
{"ok": true}
```

### POST /api/trade/orders

用途：提交买卖委托。

Request Body:
```json
{
  "account": "admin",
  "symbol": "600001",
  "side": "买入",
  "price": 100.5,
  "quantity": 100,
  "note": ""
}
```

Response:
```json
{
  "ok": true,
  "order": {
    "id": "ORD-...",
    "status": "未成交"
  },
  "fills": []
}
```

### POST /api/trade/orders/:id/cancel

Response:
```json
{
  "ok": true,
  "order": {"id": "ORD-...", "status": "已撤单"}
}
```

### GET /api/trade/orders

Response:
```json
{
  "ok": true,
  "orders": [
    {
      "id": "ORD-...",
      "createdAt": "2026/5/30 04:16:18",
      "symbol": "600001",
      "side": "买入",
      "price": 150,
      "quantity": 100,
      "filledQuantity": 100,
      "avgPrice": 148.42,
      "status": "已成交"
    }
  ]
}
```

### GET /api/trade/fills

Response:
```json
{
  "ok": true,
  "fills": [
    {
      "id": "FILL-...",
      "createdAt": "2026/5/30 04:16:18",
      "orderId": "ORD-...",
      "symbol": "600001",
      "side": "买入",
      "price": 148.42,
      "quantity": 100
    }
  ]
}
```

### GET /api/market/stocks

Query 示例：
```
query=6000&board=主板
```

Response:
```json
{
  "ok": true,
  "asOf": "2026-05-30T04:19:47.321+08:00",
  "stocks": [
    {"symbol": "600001", "name": "石英系统", "lastPrice": 149.17, "bid": 149.02, "ask": 149.32}
  ]
}
```

### GET /api/market/quotes

Query 示例：
```
symbols=600001,600002
```

Response:
```json
{
  "ok": true,
  "asOf": "2026-05-30T04:19:47.321+08:00",
  "stocks": [
    {"symbol": "600001", "name": "石英系统", "lastPrice": 149.17}
  ]
}
```

### GET /api/client/alerts

Response:
```json
{
  "ok": true,
  "alerts": [
    {
      "id": 1,
      "symbol": "600001",
      "condition": "高于",
      "currentPrice": "149.17",
      "triggerPrice": "150",
      "status": "监控中",
      "lastTriggered": "--"
    }
  ]
}
```

### POST /api/client/alerts

Request Body:
```json
{"symbol": "600001", "condition": "高于", "triggerPrice": "150"}
```

Response:
```json
{
  "ok": true,
  "alert": {
    "id": 1,
    "symbol": "600001",
    "condition": "高于",
    "currentPrice": "--",
    "triggerPrice": "150",
    "status": "监控中",
    "lastTriggered": "--"
  }
}
```

### PATCH /api/client/alerts/:id

Request Body:
```json
{"status": "已暂停", "currentPrice": "149.17", "lastTriggered": "2026/5/30 04:16:18"}
```

Response:
```json
{"ok": true, "alert": {"id": 1, "status": "已暂停"}}
```

### DELETE /api/client/alerts/:id

Response:
```json
{"ok": true}
```

### GET /api/client/notifications

Response:
```json
{"ok": true, "notifications": []}
```

### PATCH /api/client/notifications/:id/read

Response:
```json
{"ok": true}
```

### GET /api/client/watchlist

Response:
```json
{"ok": true, "watchlist": ["600001", "600002"]}
```

### POST /api/client/watchlist/:symbol/toggle

Response:
```json
{"ok": true, "enabled": true}
```

### GET /api/client/preferences

Response:
```json
{"ok": true, "preferences": {}}
```

### PATCH /api/client/preferences

Request Body:
```json
{"theme": "light", "refreshMode": "auto"}
```

Response:
```json
{"ok": true}
```

### POST /api/client/login-records

Request Body:
```json
{"account": "admin", "method": "密码登录", "device": "Windows", "status": "成功"}
```

Response:
```json
{"ok": true}
```

### GET /api/client/login-records

Response:
```json
{
  "ok": true,
  "records": [
    {"id": 1, "time": "2026/5/30 04:16:18", "method": "密码登录", "device": "Windows", "status": "成功"}
  ]
}
```

## 2. Mock 外部服务 API（后端内部调用）

这些接口由 FastAPI CLIENT 模块在后端调用，前端不直接访问。后期联调时由真实外部系统替换。

### Mock Account Router

- GET /api/v1/account/fund-accounts/{fund_account_id}
- POST /api/v1/account/fund-accounts/{fund_account_id}/freeze
- POST /api/v1/account/fund-accounts/{fund_account_id}/release
- POST /api/v1/account/fund-accounts/{fund_account_id}/settlements
- GET /api/v1/account/security-accounts/{security_account_id}/positions
- POST /api/v1/account/security-accounts/{security_account_id}/positions/freeze
- POST /api/v1/account/security-accounts/{security_account_id}/positions/release
- POST /api/v1/account/security-accounts/{security_account_id}/positions/settlements

### Mock Trade Router

- POST /api/v1/trade/orders
- GET /api/v1/trade/orders
- POST /api/v1/trade/orders/{order_id}/cancel
- GET /api/v1/trade/fills

### Mock Info Router

- GET /api/v1/info/stocks
- GET /api/v1/info/stocks/{stock_code}/quote

### Mock Admin Router

- GET /api/v1/admin/stocks/{stock_code}/rule
- GET /api/v1/admin/trading-day/status

## 3. 字段约定

- account：资金账户号
- fundAccountId：资金账户编号
- securitiesAccountId：证券账户编号
- symbol：股票代码
- name：股票名称
- side：买入/卖出
- price：价格
- quantity：数量
- filledQuantity：已成交数量
- avgPrice：成交均价
- status：状态
- available：可用资金
- frozen：冻结资金
- marketValue：证券市值
- totalEquity：资产总值
- availableShares：可卖数量
- frozenShares：冻结数量
- lastPrice：最新价
- bid：买一价
- ask：卖一价

## 4. 状态枚举

- 委托状态：未成交、部分成交、已成交、已撤单、已过期、已拒绝
- 提醒状态：监控中、已暂停、已触发

## 5. 错误格式

当前统一错误格式：
```json
{
  "ok": false,
  "message": "错误信息"
}
```

如需更强规范，建议未来增加 `code` 字段。
