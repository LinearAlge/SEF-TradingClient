# Backend Architecture

## 1. 设计原则

- 前端只依赖统一网关 `/api/client/*`
- 客户端组只维护“客户端自有数据”
- 资金、持仓、委托、成交、行情等权威数据属于外部系统
- mock 服务仅用于独立开发与联调前测试
- 后期联调通过替换 adapters 的 base URL 或实现，不改前端

## 2. 数据归属表

| 数据类型 | 当前实现位置 | 当前存储 | 正式归属 | 本组是否维护 | 后期替换方式 |
| --- | --- | --- | --- | --- | --- |
| 登录认证 | FastAPI CLIENT 模块 | SQLite | 客户端组 | 是 | 维持不变 |
| 安全证书 | client SQLite + IndexedDB | SQLite + IndexedDB | 客户端组 | 是 | 维持不变 |
| 登录记录 | client SQLite | SQLite | 客户端组 | 是 | 维持不变 |
| 客户端申请 | client SQLite | SQLite | 客户端组 | 是 | 维持不变 |
| 价格提醒 | client SQLite | SQLite | 客户端组 | 是 | 维持不变 |
| 通知消息 | client SQLite | SQLite | 客户端组 | 是 | 维持不变 |
| 自选股/偏好 | client SQLite | SQLite | 客户端组 | 是 | 维持不变 |
| 资金余额 | mock account router | JSON | 资金账户组 | 否 | 替换 account_adapter |
| 冻结资金 | mock account router | JSON | 资金账户组 | 否 | 替换 account_adapter |
| 资金流水 | mock account router | JSON | 资金账户组 | 否 | 替换 account_adapter |
| 持仓 | mock account router | JSON | 证券账户组 | 否 | 替换 account_adapter |
| 可卖数量 | mock account router | JSON | 证券账户组 | 否 | 替换 account_adapter |
| 证券流水 | mock account router | JSON | 证券账户组 | 否 | 替换 account_adapter |
| 委托 | mock trade router | JSON | 中央交易系统 | 否 | 替换 trade_adapter |
| 成交回报 | mock trade router | JSON | 中央交易系统 | 否 | 替换 trade_adapter |
| 行情 | mock info router | JSON | 信息发布系统 | 否 | 替换 info_adapter |
| 公告 | mock info router | JSON | 信息发布系统 | 否 | 替换 info_adapter |
| 涨跌停规则 | mock admin router（简化） | JSON | 交易系统管理 | 否 | 需外部系统提供 |
| 停牌状态 | 当前未发现 | - | 交易系统管理 | 否 | 待补充 |

## 3. SQLite 数据库说明

- 路径：backend_fastapi/client/client.sqlite
- 初始化：backend_fastapi/client/database.py
- 表结构：
  - client_users：账户与密码、首次登录标记
  - client_certificates：证书公钥
  - client_sessions：会话（当前未发现使用）
  - client_login_records：登录记录
  - client_applications：客户端申请记录
  - client_alerts：价格提醒
  - client_notifications：通知消息
  - client_preferences：偏好配置
  - client_watchlist：自选股

- 重置方式：运行 `reset-client-db.cmd` 删除 SQLite 文件

说明：SQLite 仅存客户端自有数据，不应存储资金、持仓、委托、成交等权威数据。

## 4. Mock 服务说明

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

### Mock Trade Router

- 入口：backend_fastapi/mock_modules/trade_router.py
- 数据源：backend_fastapi/mock_modules/data/mock-exchange-db.json
- 模拟：中央交易系统
- 主要接口：
  - POST /api/v1/trade/orders
  - GET /api/v1/trade/orders
  - POST /api/v1/trade/orders/{order_id}/cancel
  - GET /api/v1/trade/fills

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
  - GET /api/v1/admin/trading-day/status

## 5. Adapter 设计说明

- authAdapter：证书绑定/验证逻辑，读写 client SQLite
- fundsAdapter：封装资金系统接口，后期替换真实资金接口地址
- securitiesAdapter：封装证券系统接口，后期替换真实证券接口地址
- exchangeAdapter：封装撮合系统接口，后期替换真实交易所接口地址
- marketAdapter：封装行情系统接口，后期替换真实行情接口地址

替换原则：保持网关接口不变，仅替换 adapters 的实现或 base URL。
