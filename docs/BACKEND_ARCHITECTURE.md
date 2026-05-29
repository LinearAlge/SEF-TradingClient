# Backend Architecture

## 1. 设计原则

- 前端只依赖统一网关 `/api/*`
- 客户端组只维护“客户端自有数据”
- 资金、持仓、委托、成交、行情等权威数据属于外部系统
- mock 服务仅用于独立开发与联调前测试
- 后期联调通过替换 adapters 的 base URL 或实现，不改前端

## 2. 数据归属表

| 数据类型 | 当前实现位置 | 当前存储 | 正式归属 | 本组是否维护 | 后期替换方式 |
| --- | --- | --- | --- | --- | --- |
| 登录认证 | client gateway + authAdapter | SQLite | 客户端组 | 是 | 维持不变 |
| 安全证书 | client SQLite + IndexedDB | SQLite + IndexedDB | 客户端组 | 是 | 维持不变 |
| 登录记录 | client SQLite | SQLite | 客户端组 | 是 | 维持不变 |
| 客户端申请 | client SQLite | SQLite | 客户端组 | 是 | 维持不变 |
| 价格提醒 | client SQLite | SQLite | 客户端组 | 是 | 维持不变 |
| 通知消息 | client SQLite | SQLite | 客户端组 | 是 | 维持不变 |
| 自选股/偏好 | client SQLite | SQLite | 客户端组 | 是 | 维持不变 |
| 资金余额 | mock funds service | JSON | 资金账户组 | 否 | 替换 fundsAdapter |
| 冻结资金 | mock funds service | JSON | 资金账户组 | 否 | 替换 fundsAdapter |
| 资金流水 | mock funds service | JSON | 资金账户组 | 否 | 替换 fundsAdapter |
| 持仓 | mock securities service | JSON | 证券账户组 | 否 | 替换 securitiesAdapter |
| 可卖数量 | mock securities service | JSON | 证券账户组 | 否 | 替换 securitiesAdapter |
| 证券流水 | mock securities service | JSON | 证券账户组 | 否 | 替换 securitiesAdapter |
| 委托 | mock exchange service | JSON | 中央交易系统 | 否 | 替换 exchangeAdapter |
| 成交回报 | mock exchange service | JSON | 中央交易系统 | 否 | 替换 exchangeAdapter |
| 行情 | mock market service | JSON | 信息发布系统 | 否 | 替换 marketAdapter |
| 公告 | mock market service | JSON | 信息发布系统 | 否 | 替换 marketAdapter |
| 涨跌停规则 | mock market service（简化） | JSON | 交易系统管理 | 否 | 需外部系统提供 |
| 停牌状态 | 当前未发现 | - | 交易系统管理 | 否 | 待补充 |

## 3. SQLite 数据库说明

- 路径：backend/client/client.sqlite
- 初始化：backend/client/client-db.cjs
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

### Mock Funds Service

- 入口：backend/mocks/mock-funds-service.cjs
- 端口：3021
- 数据源：backend/mocks/data/mock-funds-db.json
- 模拟：资金账户系统
- 主要接口：
  - GET /funds
  - GET /cash-flows
  - POST /funds/deposit
  - POST /funds/withdraw
  - POST /passwords/trade
  - POST /passwords/withdraw
  - POST /passwords/trade/verify
  - POST /funds/apply-fill
  - GET /accounts

### Mock Securities Service

- 入口：backend/mocks/mock-securities-service.cjs
- 端口：3022
- 数据源：backend/mocks/data/mock-securities-db.json
- 模拟：证券账户系统
- 主要接口：
  - GET /holdings
  - GET /stock-flows
  - POST /positions/apply-fill

### Mock Exchange Service

- 入口：backend/mocks/mock-exchange-service.cjs
- 端口：3023
- 数据源：backend/mocks/data/mock-exchange-db.json
- 模拟：中央交易系统
- 主要接口：
  - GET /orders
  - POST /orders
  - POST /orders/:id/cancel
  - GET /fills

### Mock Market Service

- 入口：backend/mocks/mock-market-service.cjs
- 端口：3024
- 数据源：backend/mocks/data/mock-market-db.json
- 模拟：信息发布系统
- 主要接口：
  - GET /stocks
- 行情自动更新：5 秒刷新一次

## 5. Adapter 设计说明

- authAdapter：证书绑定/验证逻辑，读写 client SQLite
- fundsAdapter：封装资金系统接口，后期替换真实资金接口地址
- securitiesAdapter：封装证券系统接口，后期替换真实证券接口地址
- exchangeAdapter：封装撮合系统接口，后期替换真实交易所接口地址
- marketAdapter：封装行情系统接口，后期替换真实行情接口地址

替换原则：保持网关接口不变，仅替换 adapters 的实现或 base URL。
