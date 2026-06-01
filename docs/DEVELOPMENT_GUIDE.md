# Development Guide

本文档面向项目二次开发与维护同学，说明代码运行逻辑与可扩展点。

## 1. 代码结构速览

- 前端入口：src/main.ts
- API 封装：src/services/clientApi.ts
- 业务组合：src/services/tradingApi.ts
- 会话管理：src/services/sessionStore.ts
- 后端入口：backend_fastapi/main.py
- 客户端路由：backend_fastapi/client/router.py
- 业务编排：backend_fastapi/client/service.py
- 模型映射：backend_fastapi/client/mappers.py
- Mock 服务：backend_fastapi/mock_modules/*

## 2. 运行逻辑概述

- 前端请求只发送到统一网关 `/api/client/*`
- 统一网关负责：认证流程、账户/交易/行情/管理的编排
- 外部系统接口通过 adapters 访问，当前指向 mock

## 3. 关键流程说明

### 3.1 登录与证书

- 登录走 `/api/client/auth/login`
- 若无证书或首次登录，返回 `action=enroll`
- 证书验证走 `/api/client/auth/verify`
- 重绑走 `/api/client/auth/rebind`

### 3.2 买卖委托

- 网关先做账户关联校验、涨跌停校验
- 买入先冻结资金、卖出先冻结持仓
- 提交 TRADE 订单后根据成交回报执行结算

### 3.3 撤单

- 调用 TRADE 撤单
- 根据返回释放冻结资金/持仓

## 4. 与 V2 接口对齐的位置

- adapters 是唯一对接外部系统的位置
- 统一网关输出字段稳定，前端不改动
- 字段映射统一放在 `backend_fastapi/client/mappers.py`

## 5. 常用调试方法

- 查看 SQLite 数据：backend_fastapi/client/client.sqlite
- 重置客户端数据：reset-client-db.cmd
- 重置 mock 数据：reset-trade-data.cmd
- Mock 数据文件：backend_fastapi/mock_modules/data/*.json

## 6. 二次开发建议

- 新增字段优先在统一网关扩展，再补充 adapters 映射
- 保持 `ok` 响应格式对前端兼容
- 修改业务流程时同步更新 API_CONTRACT.md 与 PROJECT_GUIDE.md

## 7. 代码扩展点

- 新增外部系统接口：在 adapters 增加调用方法
- 新增页面数据：在 clientApi.ts 增加接口并在 view/composable 中调用
- 新增 mock 数据：更新 mock_modules/data/*.json 与 mock routers
