# Backend Architecture

## 1. 设计原则

- 前端只依赖统一网关 `/api/client/*`
- 客户端组只维护“客户端自有数据”
- 资金、持仓、委托、成交、行情等权威数据属于外部系统
- mock 服务仅用于独立开发与联调前测试
- 联调阶段通过替换 adapters 实现或 base URL，不改前端

## 2. 统一后端结构

```
frontend (Vue)
  -> src/services/clientApi.ts
  -> /api/client/* (FastAPI unified)
     -> ClientService (业务编排)
     -> Adapters (account/trade/info/admin)
     -> mock_modules/* (本地模拟)
```

- 统一后端入口：`backend_fastapi/main.py`
- 客户端路由：`backend_fastapi/client/router.py`
- 业务编排：`backend_fastapi/client/service.py`
- 领域映射：`backend_fastapi/client/mappers.py`

## 3. 数据归属与替换点

| 数据类型 | 当前实现位置 | 当前存储 | 正式归属 | 本组是否维护 | 联调替换方式 |
| --- | --- | --- | --- | --- | --- |
| 登录认证 | CLIENT 模块 | SQLite | 客户端组 | 是 | 维持不变 |
| 安全证书 | SQLite + IndexedDB | SQLite + IndexedDB | 客户端组 | 是 | 维持不变 |
| 登录记录 | CLIENT 模块 | SQLite | 客户端组 | 是 | 维持不变 |
| 客户端申请 | CLIENT 模块 | SQLite | 客户端组 | 是 | 维持不变 |
| 价格提醒 | CLIENT 模块 | SQLite | 客户端组 | 是 | 维持不变 |
| 通知消息 | CLIENT 模块 | SQLite | 客户端组 | 是 | 维持不变 |
| 自选股/偏好 | CLIENT 模块 | SQLite | 客户端组 | 是 | 维持不变 |
| 资金余额 | mock account | JSON | ACCOUNT | 否 | 替换 AccountAdapter |
| 冻结/释放资金 | mock account | JSON | ACCOUNT | 否 | 替换 AccountAdapter |
| 资金流水 | mock account | JSON | ACCOUNT | 否 | 替换 AccountAdapter |
| 持仓 | mock account | JSON | ACCOUNT | 否 | 替换 AccountAdapter |
| 冻结/释放持仓 | mock account | JSON | ACCOUNT | 否 | 替换 AccountAdapter |
| 证券流水 | mock account | JSON | ACCOUNT | 否 | 替换 AccountAdapter |
| 委托 | mock trade | JSON | TRADE | 否 | 替换 TradeAdapter |
| 成交回报 | mock trade | JSON | TRADE | 否 | 替换 TradeAdapter |
| 行情 | mock info | JSON | INFO | 否 | 替换 InfoAdapter |
| 公告 | mock info | JSON | INFO | 否 | 替换 InfoAdapter |
| 涨跌停规则 | mock admin | JSON | ADMIN | 否 | 替换 AdminAdapter |
| 交易日状态 | mock admin | JSON | ADMIN | 否 | 替换 AdminAdapter |

## 4. SQLite 数据库说明

- 路径：backend_fastapi/client/client.sqlite
- 初始化：backend_fastapi/client/database.py
- 表结构：
  - client_users：账户与密码、首次登录标记
  - client_certificates：证书公钥
  - client_login_records：登录记录
  - client_applications：客户端申请记录
  - client_alerts：价格提醒
  - client_notifications：通知消息
  - client_preferences：偏好配置
  - client_watchlist：自选股
- 重置方式：运行 `reset-client-db.cmd` 删除 SQLite 文件

说明：SQLite 仅存客户端自有数据，不应存储资金、持仓、委托、成交等权威数据。

## 5. Mock 服务说明

### Mock Account Router

- 入口：backend_fastapi/mock_modules/account_router.py
- 数据源：backend_fastapi/mock_modules/data/mock-funds-db.json
- 模拟：资金账户与证券账户系统
- 主要接口：
  - GET /api/v1/account/fund-accounts/{fund_account_id}
  - POST /api/v1/account/fund-accounts/{fund_account_id}/freeze
  - POST /api/v1/account/fund-accounts/{fund_account_id}/release
  - POST /api/v1/account/fund-accounts/{fund_account_id}/settlements
  - GET /api/v1/account/security-accounts/{security_account_id}/positions
  - POST /api/v1/account/security-accounts/{security_account_id}/positions/freeze
  - POST /api/v1/account/security-accounts/{security_account_id}/positions/release
  - POST /api/v1/account/security-accounts/{security_account_id}/positions/settlements
  - GET /api/v1/account/associations/check

### Mock Trade Router

- 入口：backend_fastapi/mock_modules/trade_router.py
- 数据源：backend_fastapi/mock_modules/data/mock-exchange-db.json
- 模拟：中央交易系统
- 主要接口：
  - POST /api/v1/trade/orders
  - GET /api/v1/trade/orders
  - POST /api/v1/trade/orders/{order_id}/cancel
  - GET /api/v1/trade/fills
  - GET /api/v1/trade/market/{stock_code}
  - WebSocket /api/v1/trade/ws/orders

### Mock Info Router

- 入口：backend_fastapi/mock_modules/info_router.py
- 数据源：backend_fastapi/mock_modules/data/mock-market-db.json
- 模拟：信息发布系统
- 主要接口：
  - GET /api/v1/info/stocks
  - GET /api/v1/info/stocks/{stock_code}/quote

### Mock Admin Router

- 入口：backend_fastapi/mock_modules/admin_router.py
- 数据源：backend_fastapi/mock_modules/data/mock-market-db.json
- 模拟：交易系统管理
- 主要接口：
  - GET /api/v1/admin/stocks/{stock_code}/rule
  - GET /api/v1/admin/stocks/{stock_code}/quote
  - GET /api/v1/admin/trading-day/status

## 6. Adapter 设计说明

- AccountAdapter：资金/证券系统接口封装，联调替换到 ACCOUNT 服务
- TradeAdapter：撮合系统接口封装，联调替换到 TRADE 服务
- InfoAdapter：行情系统接口封装，联调替换到 INFO 服务
- AdminAdapter：管理系统接口封装，联调替换到 ADMIN 服务

替换原则：保持网关接口不变，仅替换 adapters 的实现或 base URL。

## 7. 与 V2 接口的一致性说明

- mock 接口返回格式为 `{success, code, message, data}`，与 V2 约定一致。
- 统一网关输出 `{ok, code, message, data}` 以保持当前前端兼容。
- 网关内的字段映射位于 `backend_fastapi/client/mappers.py`，确保前端字段稳定。
