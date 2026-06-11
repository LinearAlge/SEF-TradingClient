# 自动化测试指南（pytest 版）

## 环境要求

- Python 3.11+
- pip

## 安装

```bash
# 安装后端依赖
pip install fastapi uvicorn pydantic sqlalchemy python-multipart cryptography

# 安装测试依赖
pip install pytest httpx
# 或
pip install -r requirements-test.txt
```

## 启动后端

```bash
python -m uvicorn backend_fastapi.main:app --port 8000
```

访问 `http://localhost:8000/health` → `{"service":"client-unified","status":"UP"}` 表示启动成功。

## 运行测试

```bash
# 全部测试（52 个用例）
pytest tests_pytest/ -v

# 或使用 npm 脚本
npm test

# 单个模块
pytest tests_pytest/test_auth.py -v
pytest tests_pytest/test_trade.py -v

# 报告模式（含失败详情）
npm run test:watch
```

## 测试文件与功能对照

| 文件 | 功能 | 用例数 |
|------|------|--------|
| test_auth.py | 功能1：登录与证书 | 9 |
| test_account.py | 功能2/3/9：持仓/资金/改密 | 12 |
| test_trade.py | 功能4/5/6/7：买入/卖出/撤单/结果 | 17 |
| test_market.py | 功能8：行情查询 | 12 |
| test_alerts.py | 功能10：价格提醒 | 7 |
| **合计** | | **52** |

## 测试架构

```
pytest → httpx → HTTP API (localhost:8000)
                   /api/client/*          (客户端 API)
                   /api/v1/account/*      (Mock 资金服务)
                   /api/v1/trade/*        (Mock 撮合服务)
                   /api/v1/info/*         (Mock 行情服务)
                   /api/v1/admin/*        (Mock 管理服务)
```

测试直接调用客户端 API（`/api/client/*`），不经过浏览器。

## 测试账号

| 字段 | 值 |
|------|-----|
| 账号 | admin |
| 交易密码 | 123456 |
| 取款密码 | 654321 |
| 手机号 | 13800000000 |
| 身份证号 | 110101199001011234 |
| 资金账户ID | FUND000001 |
| 证券账户ID | SEC000001 |

## 常见问题

- **后端无法启动**：检查 Python 版本 ≥ 3.11，确认 `pip install fastapi uvicorn` 成功
- **测试连接超时**：确认后端运行在 8000 端口，`curl http://localhost:8000/health`
- **撤单测试失败**：市场数据动态更新，跌停价会变。价格过低会触发 TRADE_E05
- **重置测试数据**：运行 `reset-trade-data.cmd`
