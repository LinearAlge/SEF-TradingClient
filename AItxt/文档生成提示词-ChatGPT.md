# 交易客户端设计报告生成提示词（ChatGPT 用）

> 说明：ChatGPT 无法读取你的项目文件，请在正文处补充你自己的实现信息（接口、模块、数据表、流程、特殊功能）。

---

## 角色与输出要求

你是一名软件工程文档专家。请根据我提供的“实现信息”生成一份《股票交易系统——交易客户端子系统 设计说明书》。

输出要求：

1. 文档结构必须包含以下章节并保持顺序：
   1) 文档介绍
   2) 项目介绍
   3) 总体设计
   4) 详细设计
   5) 用户界面
   6) 数据库设计
   7) 运行设计
   8) 系统出错设计
2. 文字正式、条理清晰，可直接用于课程提交。
3. 必须包含至少 3 张 Mermaid 图（架构图、顺序图、类图或流程图）。
4. 关键公式用 KaTeX 表达（如持仓成本与损益计算）。
5. 所有接口、模块、数据库表均以“实现信息”为准，不允许编造。
6. 不要提“mock/测试”以外的后端技术，除非我提供。
7. 输出为 Markdown。

---

## 实现信息（请按实际项目填写）

### A. 项目概述
- 项目名称：
- 用户群体：
- 主要功能列表：

### B. 架构与模块
- 前端技术栈：
- 后端/网关技术栈：
- 数据库类型与用途：
- 是否有 mock 服务：
- 主要模块划分：

### C. 接口清单（前端调用的统一网关 API）
- 认证类：
  - POST /auth/login：
  - POST /auth/enroll：
  - POST /auth/verify：
  - POST /auth/rebind：
  - GET /auth/me：
- 账户类：
  - GET /account/summary：
  - GET /account/funds：
  - GET /account/holdings：
  - GET /account/cash-flows：
  - GET /account/stock-flows：
  - POST /account/funds/deposit：
  - POST /account/funds/withdraw：
  - POST /account/passwords/trade：
  - POST /account/passwords/withdraw：
- 交易类：
  - GET /trade/orders：
  - POST /trade/orders：
  - POST /trade/orders/{id}/cancel：
  - GET /trade/fills：
- 行情类：
  - GET /market/stocks：
  - GET /market/quotes：
- 客户端自有数据：
  - GET/POST/PATCH/DELETE /client/alerts：
  - GET/POST /client/login-records：
  - GET/PATCH /client/notifications：
  - GET/POST /client/watchlist：
  - GET/PATCH /client/preferences：
  - GET/POST /client/applications：

### D. 关键业务流程
- 登录与证书绑定流程：
- 行情查询与刷新：
- 买入/卖出委托：
- 撤单处理：
- 成交回报获取：
- 价格提醒触发逻辑：

### E. 数据库设计（真实与客户端自有）
- 数据库类型：
- 表清单与字段：
- 数据归属说明：

### F. UI 页面与功能
- 登录页：
- 首页：
- 行情中心：
- 交易下单：
- 委托成交：
- 资产与流水：
- 提醒管理：
- 安全设置：

### G. 运行与部署
- 启动步骤：
- 端口与服务：
- 依赖项：

### H. 错误处理
- 常见错误码/错误提示：
- 处理办法：
- 恢复策略：

---

## 输出格式模板（必须完整填充）

# 股票交易系统——交易客户端子系统

## 设计说明书

**组长：**
 **组员：**
 **日期：**
 **版本：**

------

## 目录

1. 文档介绍
2. 项目介绍
3. 总体设计
4. 详细设计
5. 用户界面
6. 数据库设计
7. 运行设计
8. 系统出错设计

------

## 1. 文档介绍

### 1.1 编写目的

### 1.2 文档范围

### 1.3 读者对象

### 1.4 术语与缩写解释

### 1.5 参考资料

------

## 2. 项目介绍

### 2.1 项目说明

### 2.2 项目背景

### 2.3 需求概述

#### 2.3.1 功能需求

#### 2.3.2 性能需求

#### 2.3.3 安全需求

### 2.4 条件与限制

------

## 3. 总体设计

### 3.1 基本设计概念和流程处理

### 3.2 功能 IPO 图

### 3.3 系统结构

### 3.4 技术介绍

### 3.5 部署图

### 3.6 类图

### 3.7 接口设计

------

## 4. 详细设计

### 4.1 顺序图

### 4.2 执行概念

------

## 5. 用户界面

------

## 6. 数据库设计

------

## 7. 运行设计

------

## 8. 系统出错设计

