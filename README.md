# TradingClient

股票交易系统客户端（实验项目子系统）。本项目提供交易客户端前端与统一 FastAPI 后端，包含 CLIENT 模块与本地 mock 外部服务。

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
- 后端：Python 3.11+ + FastAPI
- 数据库：SQLite (SQLAlchemy)
- Mock 数据：JSON 文件

## 快速启动

1) 安装依赖

```bash
npm install
```

2) 启动统一后端

```bash
pip install fastapi uvicorn pydantic sqlalchemy python-multipart cryptography
python -m uvicorn backend_fastapi.main:app --reload --port 8000
```

3) 启动前端

```cmd
npm run dev
```

访问地址：Vite 默认输出（通常 http://localhost:5173）。

## 测试账号

来自 backend_fastapi/mock_modules/data/mock-funds-db.json：

- 账号：admin
- 交易密码：123456
- 取款密码：654321
- 手机号：13800000000
- 身份证号：110101199001011234

首次登录会触发证书绑定。
如果下载下来项目的数据库已经做好了首次登录，则你的电脑会由于没有私钥而无法登录。此时用户可以通过重新绑定逻辑来表明自己换设备，或者作为开发者你可以直接删掉数据库并重新开通账户权限。

## 常用脚本

- `npm run dev`：启动前端
- `npm run dev:backend`：启动 FastAPI 后端
- `npm run dev:unified`：同时启动前端 + FastAPI 后端
- `start-unified.cmd`：一键启动 FastAPI + 前端（Windows）
- `stop-unified.cmd`：停止本地 FastAPI + 前端（Windows）
- `reset-client-db.cmd`：删除客户端 SQLite 数据库 / 重置客户端数据状态（如权限重置、登录状态重置等，用于测试）

## 文档入口

- docs/PROJECT_GUIDE.md
- docs/BACKEND_ARCHITECTURE.md
- docs/API_CONTRACT.md
- docs/TESTING_GUIDE.md
