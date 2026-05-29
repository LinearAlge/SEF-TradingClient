# TradingClient

股票交易系统客户端（实验项目子系统）。本项目提供交易客户端前端、客户端统一网关、客户端自有 SQLite，以及用于独立跑通的 mock 外部服务。

## 功能范围

- 登录、首次证书绑定/验证、证书重绑
- 首页工作台
- 行情查询与详情
- 买入/卖出委托与撤单
- 委托成交与回报
- 资产/资金/持仓/流水
- 价格提醒
- 安全设置（修改密码、登录记录）

## 技术栈

- 前端：Vue 3 + Vite + Vue Router + Pinia
- 后端：Node.js (CJS)
- 数据库：SQLite (better-sqlite3)
- Mock 数据：JSON 文件

## 快速启动

1) 安装依赖

```bash
npm install
```

2) 启动网关 + mock 服务

```cmd
.\start-gateway.cmd
```

3) 启动前端

```cmd
npm run dev
```

访问地址：Vite 默认输出（通常 http://localhost:5173）。

## 测试账号

来自 backend/mocks/data/mock-funds-db.json：

- 账号：admin
- 交易密码：123456
- 取款密码：654321
- 手机号：13800000000
- 身份证号：110101199001011234

首次登录会触发证书绑定。
如果下载下来项目的数据库已经做好了首次登录，则你的电脑会由于没有私钥而无法登录。此时用户可以通过重新绑定逻辑来表明自己换设备，或者作为开发者你可以直接删掉数据库并重新开通账户权限。

## 常用脚本

- `npm run dev`：启动前端
- `npm run dev:gateway`：仅启动客户端网关/后端
- `npm run dev:mock:funds`：仅启动资金 mock
- `npm run dev:mock:securities`：仅启动证券 mock
- `npm run dev:mock:exchange`：仅启动撮合 mock
- `npm run dev:mock:market`：仅启动行情 mock
- `start-gateway.cmd`：一键启动网关 + mock 服务
- `stop-gateway.cmd`：停止客户端后端网关 + mock 服务
- `reset-client-db.cmd`：删除客户端 SQLite 数据库 / 重置客户端数据状态（如权限重置、登录状态重置等，用于测试）

## 文档入口

- docs/PROJECT_GUIDE.md
- docs/BACKEND_ARCHITECTURE.md
- docs/API_CONTRACT.md
- docs/TESTING_GUIDE.md
