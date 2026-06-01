# Integration Guide

本文档用于集成方快速接入本项目的统一后端与前端。

## 1. 系统组成

- 前端：Vue 3 + Vite
- 统一后端：FastAPI
- 客户端自有数据：SQLite
- 外部系统：ACCOUNT / TRADE / INFO / ADMIN（当前为 mock）

## 2. 端口与入口

- 统一网关：/api/client/*
- mock 外部服务：/api/v1/account | /api/v1/trade | /api/v1/info | /api/v1/admin
- 健康检查：/health

默认环境变量：

```
VITE_CLIENT_API_BASE=http://localhost:8000/api/client
```

## 3. 接口对接关系

- 前端只访问统一网关 `/api/client/*`
- 统一网关内部通过 adapters 对接外部系统
- 联调阶段替换 adapters 的实现或 base URL

## 4. 运行与启动

1) 安装依赖

```
npm install
pip install fastapi uvicorn pydantic sqlalchemy python-multipart cryptography
```

2) 启动统一后端

```
python -m uvicorn backend_fastapi.main:app --reload --port 8000
```

3) 启动前端

```
npm run dev
```

## 5. 数据与权限

- 客户端自有数据仅保存在 SQLite
- 资金、持仓、委托、成交、行情等权威数据来自外部系统
- 登录返回 `token` 与账户 ID，前端需持久化

## 6. 与 V2 接口的映射策略

- 当前 mock 接口使用 V2 统一响应结构 `{success, code, message, data}`
- 统一网关输出 `{ok, code, message, data}`
- 联调时只需让 adapters 调用真实 V2 接口并做字段映射

## 7. 集成检查清单

- [ ] 确认网关地址与前端环境变量一致
- [ ] 确认 `/health` 可访问
- [ ] 确认登录流程可以返回 `action=enroll` 或 `action=verify`
- [ ] 确认 `token` 存储与过期时间处理正常
- [ ] 确认资金与持仓查询返回字段符合前端显示
- [ ] 确认委托、撤单、成交查询流程完整
- [ ] 确认行情查询可返回最新价与盘口

## 8. 常见集成问题

- 登录失败：确认客户端权限是否已申请或数据是否被重置
- 行情为空：检查 mock-market-db.json 是否有数据
- 委托失败：检查 ACCOUNT/TRADE mock 数据是否一致
