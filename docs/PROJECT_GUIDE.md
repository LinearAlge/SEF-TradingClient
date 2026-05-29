# TradingClient Project Guide

## 1. 背景与目标

本项目是“股票交易系统实验”的客户端部分实现，目标是提供交易客户端前端与客户端自有后端，并以 mock 外部服务完成独立跑通与联调前测试。完整系统应包含：

- 证券账户业务（外部系统）
- 资金账户业务（外部系统）
- 中央交易系统（外部系统）
- 网上信息发布（外部系统）
- 交易系统管理（外部系统）

本项目实际实现内容：

- 客户端申请、首次登录、登录
- 证书绑定/验证/重绑流程
- 首页工作台
- 行情查询与详情
- 买卖委托、撤单、成交回报
- 资产、资金、持仓、资金/证券流水
- 价格提醒（新增/触发/暂停/删除）
- 安全设置（修改交易/取款密码、登录记录、证书状态）

## 2. 整体架构

```
前端 Vue 应用
  ↓
src/services/clientApi.ts
  ↓
客户端网关 backend/client/client-gateway-server.cjs
  ↓
Adapters
  ├─ authAdapter（客户端证书/登录）
  ├─ client-db SQLite（客户端自有数据）
  ├─ mock funds service（资金账户 mock）
  ├─ mock securities service（证券账户 mock）
  ├─ mock exchange service（撮合/委托 mock）
  └─ mock market service（行情 mock）
```

说明：前端只调用统一网关 `VITE_CLIENT_API_BASE`，所有外部系统能力均通过网关 + adapters 模拟。后期联调时只需要替换 adapters 的 base URL 或实现，不需要改前端。

## 3. 前端结构说明

### 目录结构

- src/views：页面级视图
- src/components：通用组件
- src/services：API 封装
- src/composables：Pinia 状态与业务逻辑
- src/router：路由配置
- src/utils：本地证书存储与本地缓存工具
- src/assets：静态资源

### 页面说明

- LoginView：登录、申请权限、证书绑定/验证/重绑
  - API：/api/auth/login | /api/auth/enroll | /api/auth/verify | /api/auth/rebind | /api/client/applications
  - 说明：登录失败仅在 `action=apply` 时展示申请面板
- DashboardView：首页工作台
  - API：/api/account/funds | /api/account/holdings | /api/trade/orders | /api/trade/fills | /api/client/alerts
  - 说明：展示资金、持仓、市值、委托与成交
- MarketView：行情中心
  - API：/api/market/stocks
  - 说明：支持板块/模糊查询，支持跳转买入/卖出/提醒
- TradeView：交易下单
  - API：/api/trade/orders
  - 说明：前端完成基础风控校验，提交后刷新资金/持仓/委托
- OrdersView：委托与成交
  - API：/api/trade/orders | /api/trade/fills | /api/trade/orders/:id/cancel
  - 说明：支持批量撤单
- AccountView：资产与流水
  - API：/api/account/funds | /api/account/holdings | /api/account/cash-flows | /api/account/stock-flows
- AlertsView：价格提醒
  - API：/api/client/alerts
  - 说明：支持新增/暂停/恢复/删除，刷新价格并触发状态
- SettingsView：安全设置
  - API：/api/account/passwords/trade | /api/account/passwords/withdraw | /api/client/login-records
- NotFoundView：404

## 4. 后端结构说明

### 客户端网关

- backend/client/client-gateway-server.cjs
- 对外暴露 `/api/*` 统一接口
- 负责认证流程、将请求转发至各 mock 服务，并对返回数据做必要合并

### 客户端自有数据（SQLite）

- backend/client/client.sqlite
- 数据用途：证书、登录记录、提醒、通知、偏好、自选股等
- 不存放资金、持仓、委托、成交等权威数据

### 外部业务 mock 服务

- backend/mocks/mock-funds-service.cjs
- backend/mocks/mock-securities-service.cjs
- backend/mocks/mock-exchange-service.cjs
- backend/mocks/mock-market-service.cjs

这些服务模拟外部系统，便于独立开发与测试。后期联调时应替换为真实接口。

## 5. 数据流说明

### 5.1 登录与证书验证

1. 前端提交账号/密码 -> /api/auth/login
2. 网关调用资金 mock 校验交易密码
3. 若首次登录或无证书，返回 `action=enroll`
4. 前端生成本机证书，调用 /api/auth/enroll 绑定
5. 若已有证书，返回 `action=verify`，前端签名后调用 /api/auth/verify

### 5.2 申请权限流程

1. 登录返回 `action=apply` 后展示申请面板
2. 前端提交 /api/client/applications
3. 网关校验资金账户存在、手机号一致
4. 通过则写入 client SQLite 并允许登录

### 5.3 行情查询

1. 前端调用 /api/market/stocks
2. 网关转发到 mock market service
3. mock market 每 5 秒更新价格

### 5.4 买入/卖出委托

1. 前端 /api/trade/orders 提交委托
2. mock exchange 撮合，生成订单与成交回报
3. 网关收到 fills，调用 mock funds + mock securities 清算
4. 前端刷新资金/持仓/委托/成交

### 5.5 撤单

1. 前端调用 /api/trade/orders/:id/cancel
2. mock exchange 更新委托状态
3. 前端刷新委托列表与资产

### 5.6 资产/持仓/流水刷新

- /api/account/funds + /api/account/holdings
- /api/account/cash-flows + /api/account/stock-flows
- 网关对 funds + holdings 合并市值与资产总值

### 5.7 提醒流程

1. 新增提醒 /api/client/alerts
2. 提醒列表中刷新行情，满足条件则状态改为已触发
3. 更新提醒 /api/client/alerts/:id
4. 删除提醒 /api/client/alerts/:id

### 5.8 修改密码

- /api/account/passwords/trade
- /api/account/passwords/withdraw
- 修改逻辑由资金 mock 服务处理

## 6. 当前限制与后续替换点

- 行情、资金、证券、撮合均为 mock 数据与逻辑
- 撮合逻辑是简化版，不包含真实撮合优先级与撮合队列
- 资金冻结/解冻逻辑当前仅在成交后调整
- SQLite 仅用于客户端自有数据
- 后期联调时仅需替换 adapters 的 base URL 或实现，不应修改前端页面
