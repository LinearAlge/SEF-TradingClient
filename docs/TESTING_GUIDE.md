# Testing Guide

## 1. 环境要求

- Python: 3.11+
- npm: 随 Node 安装
- SQLite: SQLAlchemy + SQLite
- 操作系统：Windows 已验证

## 2. 安装依赖

```bash
npm install
pip install fastapi uvicorn pydantic sqlalchemy python-multipart cryptography
```

## 3. 环境变量

`.env` 当前包含：

```
VITE_CLIENT_API_BASE=http://localhost:8000/api/client
API_PROFILE=local_unified
ENABLE_TRADE_WS=false
```

说明：前端只需 `VITE_CLIENT_API_BASE`。

## 4. 启动步骤

1. 安装依赖
2. 启动统一后端

```bash
python -m uvicorn backend_fastapi.main:app --reload --port 8000
```

3. 启动前端

```cmd
npm run dev
```

访问地址：Vite 默认输出（通常 http://localhost:5173）。

## 5. 测试账号

当前 mock 资金账户（来自 backend_fastapi/mock_modules/data/mock-funds-db.json）：

- 账号：admin
- 交易密码：123456
- 取款密码：654321
- 手机号：13800000000
- 身份证号：110101199001011234

注意：首次登录会要求绑定证书。

## 6. 业务测试流程

### 登录与证书

1. 打开登录页，输入账号与交易密码
2. 首次登录会触发证书绑定
3. 证书验证通过后进入首页
4. 重绑：在登录页选择“重新绑定证书”，输入手机号与身份证号

### 行情

1. 进入行情中心
2. 搜索股票代码或名称
3. 打开股票详情
4. 从行情跳转到买入/卖出/提醒

### 买入

1. 进入交易页
2. 输入股票代码（自动填充参考价）
3. 输入数量（100 股整数倍）
4. 预览与提交
5. 到“委托成交”确认状态
6. 资产页检查持仓与资金

### 卖出

1. 确保已有持仓
2. 输入卖出数量
3. 提交委托
4. 检查持仓与资金变化

### 撤单

1. 提交未成交委托
2. 到“委托成交”撤单
3. 检查委托状态为已撤单

### 资产页

1. 查看资金概览
2. 查看持仓
3. 查看资金流水与证券流水

### 提醒

1. 新增提醒
2. 刷新价格触发提醒
3. 暂停/恢复/删除提醒

### 安全设置

1. 修改交易密码
2. 修改取款密码
3. 查看登录记录

## 7. 常见问题

- 端口占用：检查是否有占用 8000/5173 的进程
- 前端白屏：检查 FastAPI 后端是否启动
- 登录失败：确认是否已申请客户端权限（第一次登录会要求申请）
- 证书验证失败：清理浏览器 IndexedDB 后重新登录
- 行情无数据：检查 mock market 数据是否存在
- 委托不刷新：确认 WebSocket 已连接，必要时刷新页面
- 委托提交失败：检查 mock exchange 服务是否运行
- SQLite 相关错误：运行 `reset-client-db.cmd` 后重启网关

## 8. 重置测试数据

- 重置客户端 SQLite：

```cmd
.\reset-client-db.cmd
```

- 重置 mock 数据：直接编辑以下 JSON 文件或替换为原始 seed
  - backend_fastapi/mock_modules/data/mock-funds-db.json
  - backend_fastapi/mock_modules/data/mock-securities-db.json
  - backend_fastapi/mock_modules/data/mock-exchange-db.json

重置后重启网关与 mock 服务。
