# API Contract

本文档描述当前统一网关 API（前端唯一调用入口）以及后端内部使用的 mock 外部服务接口。

## 1. 统一网关 API

Base URL: `VITE_CLIENT_API_BASE`（默认 http://localhost:8000/api/client）

说明：登录后返回 `token`，前端保存并在请求头加入 `Authorization: Bearer <token>`。

### 1.1 响应格式约定

统一网关响应以 `ok` 为顶层成功标记，错误时携带 `code` 与 `message`。

成功示例：
```json
{
  "ok": true,
  "code": "OK",
  "message": "success",
  "data": {}
}
```

失败示例：
```json
{
  "ok": false,
  "code": "COMMON_BAD_REQUEST",
  "message": "请求格式错误",
  "data": null
}
```

### 1.2 认证与证书

#### POST /auth/login

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
  "action": "enroll",
  "token": "mock-token",
  "investorId": "INV000001",
  "fundAccountId": "FUND000001",
  "securityAccountId": "SEC000001",
  "expiresAt": "2026-05-30T04:19:47.321+08:00"
}
```

失败示例（未开通权限）：
```json
{
  "ok": false,
  "code": "CLIENT_ACCESS_REQUIRED",
  "message": "未开通客户端权限，请先申请",
  "action": "apply"
}
```

#### POST /auth/enroll

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
  "user": {"name": "admin", "account": "admin"},
  "investorId": "INV000001",
  "fundAccountId": "FUND000001",
  "securityAccountId": "SEC000001",
  "expiresAt": "2026-05-30T04:19:47.321+08:00"
}
```

#### POST /auth/verify

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
  "user": {"name": "admin", "account": "admin"},
  "investorId": "INV000001",
  "fundAccountId": "FUND000001",
  "securityAccountId": "SEC000001",
  "expiresAt": "2026-05-30T04:19:47.321+08:00"
}
```

#### POST /auth/rebind

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
  "message": "证书已重置，请重新登录绑定证书"
}
```

#### GET /auth/me

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

### 1.3 客户端申请

#### POST /client/applications

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

#### GET /client/applications

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
      "createdAt": "2026-05-30T04:00:00.000Z"
    }
  ]
}
```

### 1.4 账户与资产

#### GET /account/summary

用途：资金 + 持仓合并摘要。

Response:
```json
{
  "ok": true,
  "account": "admin",
  "available": 200000,
  "frozen": 0,
  "marketValue": 14853,
  "totalEquity": 214853,
  "updatedAt": "2026-05-30T04:19:47.321+08:00"
}
```

#### GET /account/funds

用途：资金余额（已合并持仓市值）。

Response:
```json
{
  "ok": true,
  "available": 200000,
  "frozen": 0,
  "marketValue": 14853,
  "totalEquity": 214853,
  "updatedAt": "2026-05-30T04:19:47.321+08:00"
}
```

#### GET /account/holdings

用途：持仓。

Response:
```json
{
  "ok": true,
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
  ],
  "totalMarketValue": 14853,
  "asOf": "2026-05-30T04:16:18.736+08:00"
}
```

#### GET /account/cash-flows

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

#### GET /account/stock-flows

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

#### POST /account/funds/deposit

Request Body:
```json
{"account": "admin", "amount": 10000}
```

Response:
```json
{"ok": true}
```

#### POST /account/funds/withdraw

Request Body:
```json
{"account": "admin", "amount": 5000, "password": "654321"}
```

Response:
```json
{"ok": true}
```

#### POST /account/passwords/trade

Request Body:
```json
{"account": "admin", "currentPassword": "123456", "nextPassword": "1234567"}
```

Response:
```json
{"ok": true}
```

#### POST /account/passwords/withdraw

Request Body:
```json
{"account": "admin", "currentPassword": "654321", "nextPassword": "654322"}
```

Response:
```json
{"ok": true}
```

### 1.5 行情

#### GET /market/stocks

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

#### GET /market/quotes

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

### 1.6 委托与成交

#### POST /trade/orders

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

#### POST /trade/orders/{id}/cancel

Response:
```json
{
  "ok": true,
  "order": {"id": "ORD-...", "status": "已撤单"}
}
```

#### GET /trade/orders

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

#### GET /trade/fills

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

### 1.7 提醒与用户数据

#### GET /client/alerts

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

#### POST /client/alerts

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

#### PATCH /client/alerts/{id}

Request Body:
```json
{"status": "已暂停", "currentPrice": "149.17", "lastTriggered": "2026/5/30 04:16:18"}
```

Response:
```json
{"ok": true, "alert": {"id": 1, "status": "已暂停"}}
```

#### DELETE /client/alerts/{id}

Response:
```json
{"ok": true}
```

#### GET /client/notifications

Response:
```json
{"ok": true, "notifications": []}
```

#### PATCH /client/notifications/{id}/read

Response:
```json
{"ok": true}
```

#### GET /client/watchlist

Response:
```json
{"ok": true, "watchlist": ["600001", "600002"]}
```

#### POST /client/watchlist/{symbol}/toggle

Response:
```json
{"ok": true, "enabled": true}
```

#### GET /client/preferences

Response:
```json
{"ok": true, "preferences": {}}
```

#### PATCH /client/preferences

Request Body:
```json
{"theme": "light", "refreshMode": "auto"}
```

Response:
```json
{"ok": true}
```

#### POST /client/login-records

Request Body:
```json
{"account": "admin", "method": "密码登录", "device": "Windows", "status": "成功"}
```

Response:
```json
{"ok": true}
```

#### GET /client/login-records

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

## 3. 字段与状态约定

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

## 4. 与 V2 接口约定的关系

- 当前统一网关是客户端组内部集成层，外部联调时由 adapters 切换到真实 V2 接口。
- `/api/client/*` 保持稳定，便于前端不改动即可接入真实服务。
- mock 接口字段与 V2 统一响应格式已对齐（`success/code/message/data`），网关输出仍使用 `ok` 以匹配当前前端。

## 5. 错误码与响应

网关错误响应包含 `code` 与 `message`，前端按 `ok` 判断失败：
```json
{
  "ok": false,
  "code": "TRADE_E05",
  "message": "价格非法或超出涨跌停范围",
  "data": null
}
```
