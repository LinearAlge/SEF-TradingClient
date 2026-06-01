from pathlib import Path
out = Path('/mnt/data/交易客户端子系统_设计说明书_优化最终版.md')
content = r'''# 股票交易系统——交易客户端子系统设计说明书

**项目名称：** 股票交易系统  
**子系统名称：** 交易客户端子系统  
**文档类型：** 软件设计说明书  
**版本：** 3.0  
**日期：** 2026-05-31  
**组长：**  
**组员：**  

---

## 目录

1. [文档介绍](#1-文档介绍)  
   1.1 [编写目的](#11-编写目的)  
   1.2 [文档范围](#12-文档范围)  
   1.3 [读者对象](#13-读者对象)  
   1.4 [术语与缩写解释](#14-术语与缩写解释)  
   1.5 [参考资料](#15-参考资料)  
2. [项目介绍](#2-项目介绍)  
   2.1 [项目说明](#21-项目说明)  
   2.2 [项目背景](#22-项目背景)  
   2.3 [需求概述](#23-需求概述)  
   2.4 [条件与限制](#24-条件与限制)  
3. [总体设计](#3-总体设计)  
   3.1 [基本设计概念和流程处理](#31-基本设计概念和流程处理)  
   3.2 [功能 IPO 图](#32-功能-ipo-图)  
   3.3 [系统结构](#33-系统结构)  
   3.4 [技术介绍](#34-技术介绍)  
   3.5 [部署图](#35-部署图)  
   3.6 [类图](#36-类图)  
   3.7 [接口设计](#37-接口设计)  
4. [详细设计](#4-详细设计)  
   4.1 [顺序图](#41-顺序图)  
   4.2 [执行概念](#42-执行概念)  
   4.3 [状态图](#43-状态图)  
5. [用户界面](#5-用户界面)  
6. [数据库设计](#6-数据库设计)  
   6.1 [概念结构设计](#61-概念结构设计)  
   6.2 [逻辑结构设计](#62-逻辑结构设计)  
   6.3 [物理结构设计](#63-物理结构设计)  
   6.4 [系统数据归属与共享](#64-系统数据归属与共享)  
7. [运行设计](#7-运行设计)  
8. [系统出错设计](#8-系统出错设计)  
9. [附录：代码迭代提示词](#9-附录代码迭代提示词)

---

# 1. 文档介绍

## 1.1 编写目的

本文档描述股票交易系统中交易客户端子系统的软件设计方案，目的是：

1. 明确交易客户端子系统的总体架构、模块划分、接口设计、数据设计和运行方式；
2. 作为交易客户端前端、客户端网关、适配层和本地数据模块开发的依据；
3. 作为交易客户端与资金账户、证券账户、中央交易、网上信息发布、交易系统管理等子系统联调的依据；
4. 作为系统测试、课程验收和后续代码迭代的依据。

本设计以课程实验指导书和需求报告中的交易客户端功能要求为边界，保留当前实现中已经形成并验证可行的 **Node.js Client Gateway + SQLite + Vue 前端界面** 方案，同时吸收原设计报告中关于模块化、缓存、接口编排、顺序图、状态图和维护设计的内容，形成最终设计基线。

## 1.2 文档范围

本文档覆盖交易客户端子系统的以下内容：

1. 客户端权限申请、首次登录、普通登录、证书绑定、证书验证与证书重绑；
2. 股票行情查询、股票搜索、股票详情、行情刷新与价格区间展示；
3. 资金账户查询、证券持仓查询、资产汇总、资金流水和证券流水；
4. 买入委托、卖出委托、委托撤销、委托状态管理和成交回报展示；
5. 交易密码、取款密码修改；
6. 价格提醒、自选股、通知、偏好设置等客户端附加功能；
7. Client Gateway、Adapter、缓存、SQLite 数据库和外部接口设计；
8. 用户界面、运行设计、出错处理和维护设计。

## 1.3 读者对象

本文档面向以下人员：

1. 交易客户端前端开发人员；
2. 交易客户端网关与适配层开发人员；
3. 资金账户、证券账户、中央交易、网上信息发布、交易系统管理等其他子系统开发人员；
4. 系统测试人员；
5. 项目管理人员和课程验收人员。

## 1.4 术语与缩写解释

| 缩写、术语及符号 | 解释 |
|---|---|
| CLIENT | 交易客户端子系统，本组负责的子系统 |
| Client Gateway | 客户端统一网关，作为前端访问后端能力的统一入口 |
| Adapter | 外部服务适配器，屏蔽不同子系统接口差异 |
| ACCOUNT | 账户业务相关外部子系统，包括资金账户和证券账户服务 |
| TRADE | 中央交易系统，负责委托、撤单、撮合和成交回报 |
| INFO | 网上信息发布系统，负责行情、股票基本信息和公告 |
| ADMIN | 交易系统管理系统，负责涨跌停、停牌、交易控制等规则 |
| SQLite | 客户端网关本地轻量数据库，用于保存客户端自有数据 |
| IndexedDB | 浏览器本地数据库，用于保存本机证书私钥 |
| JWT / Token | 登录后的会话凭证，用于标识已认证用户 |
| 证书绑定 | 首次登录时生成本机密钥对，并将公钥绑定到账户 |
| 证书验证 | 登录时使用本机私钥对挑战码签名，网关用公钥验签 |
| 冻结资金 | 买入委托提交后，暂时从可用资金中冻结的金额 |
| 冻结持仓 | 卖出委托提交后，暂时从可卖数量中冻结的股票数量 |
| 成交回报 | 中央交易系统返回的成交价格、成交数量和成交状态 |
| IPO 图 | 用输入、处理、输出描述模块加工逻辑的图示工具 |
| 顺序图 | 描述对象之间消息调用时间顺序的 UML 图 |
| 类图 | 描述类、接口及其关系的 UML 静态结构图 |
| 状态图 | 描述对象或流程状态变化的 UML 图 |

## 1.5 参考资料

| 序号 | 文档名称 | 版本 / 说明 |
|---|---|---|
| 1 | 2026 实验大纲 StockTradingSystem | 股票交易系统实验指导书 |
| 2 | 股票交易系统——交易客户端子系统需求说明书 | 1.0 |
| 3 | 股票交易系统——交易客户端子系统原设计报告 | 1.0 |
| 4 | 股票交易系统——交易客户端子系统当前实现设计报告 | 1.1 |
| 5 | TradingClient API Contract | 当前实现 API 参考 |
| 6 | TradingClient Backend Architecture | 当前后端结构参考 |
| 7 | TradingClient Project Guide | 当前项目结构参考 |
| 8 | 系统设计报告实例参考 | 文档组织、图表与章节格式参考 |

---

# 2. 项目介绍

## 2.1 项目说明

| 项目 | 内容 |
|---|---|
| 总体项目名称 | 股票交易系统 |
| 本组负责子系统 | 交易客户端子系统 |
| 任务提出者 | 软件工程课程组 |
| 开发者 | 交易客户端开发小组 |
| 用户群 | 持有资金账户和证券账户的投资者 |
| 间接用户 | 证券经纪商工作人员、系统管理员、其他子系统联调人员 |

股票交易系统包含证券账户业务、资金账户业务、交易客户端、股票中央交易系统、网上信息发布系统、交易系统管理等子系统。交易客户端是投资者直接使用的操作入口，负责向用户展示行情、资金、持仓和交易结果，并将用户的买入、卖出、撤单等操作转化为对其他子系统的标准接口调用。

## 2.2 项目背景

本项目来源于软件工程课程综合实验。实验要求多个小组协作完成完整股票交易系统，各小组分别负责不同业务子系统。交易客户端作为面向投资者的前端交互模块，需要同时连接资金账户系统、证券账户系统、中央交易系统、网上信息发布系统和交易系统管理系统。

由于各外部子系统由不同小组实现，接口细节、开发进度和数据格式存在差异。为降低前端与多个外部系统直接耦合的复杂度，本设计采用 **Vue 前端 + Node.js Client Gateway + Adapter 适配层** 的形式。前端只调用客户端网关；客户端网关根据业务需要调用其他子系统接口，并将外部响应转换为客户端统一数据模型。

## 2.3 需求概述

### 2.3.1 功能需求

| 模块名称 | 功能编号 | 一级功能 | 二级功能 / 说明 | 优先级 |
|---|---|---|---|---|
| 用户认证 | TC001 | 登录客户端 | 账户 + 交易密码登录，首次登录证书认证 | 必须 |
| 用户认证 | TC002 | 修改密码 | 修改交易密码、修改取款密码 | 必须 |
| 信息查询 | TC003 | 查询股票信息 | 最新价、买一卖一、日/周/月高低价、公告 | 必须 |
| 信息查询 | TC004 | 查询持仓信息 | 持仓数量、可卖数量、持有成本、持有损益 | 必须 |
| 信息查询 | TC005 | 查询资金账户 | 可用资金、冻结资金、证券市值、资产总值 | 必须 |
| 交易操作 | TC006 | 发出购买指令 | 参考价提示、资金校验、资金冻结、提交委托 | 必须 |
| 交易操作 | TC007 | 发出出售指令 | 参考价提示、可卖数量校验、持仓冻结、提交委托 | 必须 |
| 交易操作 | TC008 | 撤销指令 | 未成交/部分成交可撤，完全成交不可撤 | 必须 |
| 结果展示 | TC009 | 显示交易结果 | 展示成交回报，刷新资金与持仓 | 必须 |
| 高级功能 | TC010 | 价格提醒 | 设置、查看、暂停、恢复、删除提醒 | 选作 |
| 附加功能 | TC011 | 客户端权限申请 | 未开通客户端权限时提交申请 | 建议实现 |
| 附加功能 | TC012 | 自选股与偏好设置 | 自选股、主题、刷新偏好 | 建议实现 |
| 附加功能 | TC013 | 通知与登录记录 | 通知中心、登录记录查看 | 建议实现 |

### 2.3.2 性能需求

1. 行情价格和报价信息刷新频率不低于每 5 秒一次；
2. 单用户本地操作时，页面主要交互响应时间应小于 1 秒；
3. 查询类接口在正常网络条件下响应时间应小于 2 秒；
4. 委托提交接口在正常网络条件下响应时间应小于 2 秒；
5. 下单、撤单、成交后应及时刷新资金、持仓、委托和成交回报；
6. 系统应支持 Chrome、Edge、Firefox 等主流浏览器；
7. 网关层应具备与多个外部子系统稳定通信和错误隔离的能力。

### 2.3.3 安全需求

1. 用户登录必须校验账户和交易密码；
2. 首次登录必须完成本机证书绑定；
3. 已绑定证书的用户登录时必须进行证书挑战验证；
4. 私钥只保存在浏览器 IndexedDB，不上传服务端；
5. 网关只保存证书公钥和客户端自有信息；
6. 修改交易密码和取款密码必须校验原密码；
7. 买入、卖出、撤单等关键操作必须由网关进行服务端校验；
8. 密码、私钥、Token 等敏感信息不得写入日志；
9. 联调或部署环境应使用 HTTPS / WSS；
10. 外部服务异常时不得泄露内部堆栈信息。

## 2.4 条件与限制

| 类型 | 条件与限制 |
|---|---|
| 前端运行环境 | Chrome、Edge、Firefox 等现代浏览器 |
| 前端技术 | Vue 3、Vite、Vue Router、Pinia 或等价状态管理 |
| 客户端后端 | Node.js Client Gateway |
| 客户端数据库 | SQLite，仅保存客户端自有数据 |
| 外部接口 | 采用与其他小组约定的 ACCOUNT、TRADE、INFO、ADMIN 接口 |
| 本地开发 | 可通过 mock 服务模拟外部系统，但 mock 不是最终业务设计的一部分 |
| 数据归属 | 资金、证券、委托、成交、行情等权威数据归对应子系统 |
| 硬件限制 | 可使用普通 PC 作为本地开发和演示服务器 |
| 网络限制 | 需保证浏览器、客户端网关、外部服务之间网络连通 |

---

# 3. 总体设计

## 3.1 基本设计概念和流程处理

本子系统采用分层架构：

1. **浏览器前端层**：负责用户界面、交互流程、基础输入校验和证书私钥管理；
2. **Client Gateway 层**：负责统一路由、会话管理、业务编排、服务端校验、缓存管理和错误处理；
3. **Adapter 适配层**：负责调用外部 ACCOUNT、TRADE、INFO、ADMIN 等子系统接口；
4. **客户端自有数据库层**：使用 SQLite 存储证书公钥、权限申请、登录记录、提醒、通知、自选股、偏好等客户端自有数据；
5. **外部业务系统层**：资金账户、证券账户、中央交易、网上信息发布、交易系统管理等子系统维护权威业务数据。

处理流程如下：

```mermaid
flowchart LR
    U[投资者] --> FE[Vue 前端页面]
    FE --> API[Client Gateway /api/*]
    API --> AUTH[用户认证与证书服务]
    API --> QUERY[行情/账户查询服务]
    API --> ORDER[交易委托服务]
    API --> RESULT[成交回报服务]
    API --> CLIENTDB[(Client SQLite)]
    AUTH --> CLIENTDB
    QUERY --> ADAPTER[Adapter 适配层]
    ORDER --> ADAPTER
    RESULT --> ADAPTER
    ADAPTER --> ACCOUNT[ACCOUNT 资金/证券账户系统]
    ADAPTER --> TRADE[TRADE 中央交易系统]
    ADAPTER --> INFO[INFO 网上信息发布系统]
    ADAPTER --> ADMIN[ADMIN 交易系统管理系统]
3.1.1 基本业务流程
flowchart TD
    Start([开始]) --> Login[登录/证书验证]
    Login --> Main[进入首页工作台]
    Main --> Quote[查询股票行情]
    Main --> Asset[查询资金和持仓]
    Quote --> Trade[买入/卖出委托]
    Asset --> Trade
    Trade --> Validate[网关侧校验资金/持仓/价格/数量]
    Validate --> Freeze[冻结资金或持仓]
    Freeze --> Submit[提交中央交易系统]
    Submit --> Orders[展示委托状态]
    Orders --> Fill[接收/查询成交回报]
    Fill --> Refresh[刷新资金、持仓、委托、成交]
    Orders --> Cancel[撤单]
    Cancel --> Release[释放未成交部分冻结资源]
    Release --> Refresh
3.2 功能 IPO 图
3.2.1 登录认证
flowchart LR
    IN[输入\n1. 账户/资金账号\n2. 交易密码\n3. 本机证书签名]
    P[处理\n1. 校验客户端权限\n2. 调用账户系统验证密码\n3. 判断首次登录\n4. 绑定或验证证书\n5. 生成会话]
    OUT[输出\n1. 登录成功/失败\n2. apply/enroll/verify 动作\n3. token 与用户信息]
    IN --> P --> OUT
3.2.2 行情查询
flowchart LR
    IN[输入\n1. 股票代码/名称\n2. 板块筛选\n3. 自动刷新触发]
    P[处理\n1. 调用 INFO 行情接口\n2. 写入行情缓存\n3. 补充涨跌停/停牌状态\n4. 组装展示数据]
    OUT[输出\n1. 股票列表\n2. 股票详情\n3. 最新价/买一卖一\n4. 高低价/公告]
    IN --> P --> OUT
3.2.3 账户资产查询
flowchart LR
    IN[输入\n1. 登录账户\n2. 资金查询请求\n3. 持仓查询请求]
    P[处理\n1. 调用资金账户系统\n2. 调用证券账户系统\n3. 调用行情接口取现价\n4. 计算市值/成本/盈亏]
    OUT[输出\n1. 可用资金\n2. 冻结资金\n3. 持仓列表\n4. 资产总值/盈亏]
    IN --> P --> OUT
3.2.4 买入委托
flowchart LR
    IN[输入\n1. 股票代码\n2. 买入价格\n3. 买入数量]
    P[处理\n1. 校验股票和交易状态\n2. 校验涨跌停范围\n3. 校验可用资金\n4. 冻结资金\n5. 提交买入委托]
    OUT[输出\n1. 委托编号\n2. 委托状态\n3. 冻结后资金\n4. 错误提示]
    IN --> P --> OUT
3.2.5 卖出委托
flowchart LR
    IN[输入\n1. 股票代码\n2. 卖出价格\n3. 卖出数量]
    P[处理\n1. 校验股票和交易状态\n2. 校验涨跌停范围\n3. 校验可卖数量\n4. 冻结持仓\n5. 提交卖出委托]
    OUT[输出\n1. 委托编号\n2. 委托状态\n3. 冻结后持仓\n4. 错误提示]
    IN --> P --> OUT
3.2.6 撤销委托
flowchart LR
    IN[输入\n1. 委托编号\n2. 当前账户]
    P[处理\n1. 查询委托状态\n2. 判断是否可撤\n3. 调用中央交易撤单\n4. 释放资金或持仓\n5. 更新委托状态]
    OUT[输出\n1. 撤单成功/失败\n2. 撤销数量\n3. 释放资源结果]
    IN --> P --> OUT
3.2.7 成交回报
flowchart LR
    IN[输入\n1. 成交回报推送/轮询\n2. 委托编号]
    P[处理\n1. 匹配本地委托\n2. 更新成交数量和均价\n3. 触发资金持仓刷新\n4. 生成通知]
    OUT[输出\n1. 完全成交/部分成交\n2. 成交价/成交量\n3. 刷新后的资产]
    IN --> P --> OUT
3.2.8 价格提醒
flowchart LR
    IN[输入\n1. 股票代码\n2. 触发条件\n3. 触发价格]
    P[处理\n1. 保存提醒\n2. 行情刷新时比对价格\n3. 满足条件则触发\n4. 写入通知]
    OUT[输出\n1. 提醒状态\n2. 提醒通知\n3. 触发时间]
    IN --> P --> OUT
3.3 系统结构
3.3.1 系统上下文图
flowchart LR
    Investor[投资者] --> CLIENT[交易客户端子系统]
    CLIENT --> ACCOUNT[ACCOUNT\n资金/证券账户系统]
    CLIENT --> TRADE[TRADE\n中央交易系统]
    CLIENT --> INFO[INFO\n网上信息发布系统]
    CLIENT --> ADMIN[ADMIN\n交易系统管理系统]

    ACCOUNT --> CLIENT
    TRADE --> CLIENT
    INFO --> CLIENT
    ADMIN --> CLIENT
    CLIENT --> Investor
3.3.2 顶层数据流图
flowchart LR
    U[投资者]
    C[交易客户端子系统]
    A[资金/证券账户系统]
    T[中央交易系统]
    I[网上信息发布系统]
    M[交易系统管理系统]

    U -->|登录凭证/查询请求/下单请求/撤单请求/提醒设置| C
    C -->|登录结果/行情信息/资产信息/委托状态/成交回报/提醒通知| U

    C -->|认证请求/资金查询/冻结释放/密码修改| A
    A -->|认证结果/资金数据/持仓数据/流水数据| C

    C -->|买卖委托/撤单请求/成交查询| T
    T -->|委托状态/撮合回报| C

    C -->|股票代码/名称查询| I
    I -->|行情/公告/股票信息| C

    C -->|交易规则查询| M
    M -->|涨跌停/停牌状态| C
3.3.3 0 层模块结构图
graph TD
    CLIENT[交易客户端子系统]

    CLIENT --> P1[1 用户认证与证书管理]
    CLIENT --> P2[2 行情查询与缓存]
    CLIENT --> P3[3 账户资产聚合]
    CLIENT --> P4[4 交易委托编排]
    CLIENT --> P5[5 成交回报同步]
    CLIENT --> P6[6 客户端状态管理]
    CLIENT --> P7[7 安全设置]

    P1 --> DS1[(DS1 会话缓存)]
    P1 --> DS5[(DS5 Client SQLite)]
    P2 --> DS2[(DS2 行情缓存)]
    P3 --> DS3[(DS3 账户快照缓存)]
    P4 --> DS4[(DS4 委托状态缓存)]
    P5 --> DS4
    P6 --> DS5
    P7 --> DS5

    P1 --> ACCOUNT[ACCOUNT]
    P2 --> INFO[INFO]
    P2 --> ADMIN[ADMIN]
    P3 --> ACCOUNT
    P4 --> ACCOUNT
    P4 --> TRADE[TRADE]
    P4 --> ADMIN
    P5 --> TRADE
3.3.4 模块系统结构图
graph TD
    subgraph Presentation[表现层]
        LoginView[登录页]
        DashboardView[首页工作台]
        MarketView[行情中心]
        TradeView[交易下单]
        OrdersView[委托成交]
        AccountView[资产流水]
        AlertsView[价格提醒]
        SettingsView[安全设置]
    end

    subgraph FrontendCore[前端核心层]
        ClientApi[clientApi]
        Store[状态管理 Store]
        CertUtil[证书工具 IndexedDB]
    end

    subgraph Gateway[客户端网关层]
        Router[/api 路由]
        AuthService[AuthService]
        MarketService[MarketService]
        AccountService[AccountService]
        OrderService[OrderService]
        ResultService[ResultService]
        ClientStateService[ClientStateService]
        SettingsService[SettingsService]
    end

    subgraph Cache[缓存与本地数据]
        SessionCache[SessionCache]
        MarketCache[MarketCache]
        AccountCache[AccountCache]
        OrderCache[OrderCache]
        ClientSQLite[(Client SQLite)]
    end

    subgraph Adapter[适配层]
        AccountAdapter[accountAdapter]
        TradeAdapter[tradeAdapter]
        InfoAdapter[infoAdapter]
        AdminAdapter[adminAdapter]
    end

    Presentation --> ClientApi
    ClientApi --> Store
    ClientApi --> Router
    CertUtil --> LoginView

    Router --> AuthService
    Router --> MarketService
    Router --> AccountService
    Router --> OrderService
    Router --> ResultService
    Router --> ClientStateService
    Router --> SettingsService

    AuthService --> SessionCache
    AuthService --> ClientSQLite
    MarketService --> MarketCache
    AccountService --> AccountCache
    OrderService --> OrderCache
    ClientStateService --> ClientSQLite
    SettingsService --> ClientSQLite

    AuthService --> AccountAdapter
    MarketService --> InfoAdapter
    MarketService --> AdminAdapter
    AccountService --> AccountAdapter
    OrderService --> AccountAdapter
    OrderService --> TradeAdapter
    OrderService --> AdminAdapter
    ResultService --> TradeAdapter
3.4 技术介绍
3.4.1 前端技术
系统前端采用 Vue 3 框架构建单页应用。Vue 3 适合组件化页面开发，便于将行情表格、委托单、资产卡片、提醒列表等界面拆分为独立组件。Vite 提供快速开发构建能力。Vue Router 用于页面路由控制，Pinia 或自定义状态管理用于保存登录态、行情数据、资金持仓、委托列表和提醒状态。

3.4.2 客户端网关技术
客户端后端采用 Node.js 编写 Client Gateway。Client Gateway 对前端提供统一 /api/* 接口，并通过 Adapter 层调用外部子系统。采用 Node.js 的原因是当前代码已基于该技术栈形成可运行结构，且网关主要承担接口聚合、字段转换、错误映射和业务编排功能，不承担核心撮合或资金清算等复杂计算任务。

3.4.3 SQLite 数据库
SQLite 用于保存客户端自有数据，包括客户端权限申请、证书公钥、登录记录、价格提醒、通知、自选股和偏好设置。资金、持仓、委托、成交和行情等权威数据不写入 SQLite，而由对应外部系统维护。

3.4.4 适配层技术
Adapter 层负责屏蔽外部子系统差异。联调时如果其他组使用 Python FastAPI、Java Spring Boot 或其他后端框架，只要其提供 HTTP REST 或 WebSocket 接口，Client Gateway 均可通过 Adapter 接入。前端不感知外部接口差异。

3.4.5 缓存设计
缓存	位置	用途
SessionCache	网关内存 / 可选 SQLite	保存当前登录用户会话
MarketCache	网关内存 / 前端 Store	保存最近行情快照，降低重复查询
AccountCache	前端 Store / 网关内存	保存最近资金和持仓快照
OrderCache	前端 Store / 网关内存	保存当前会话委托状态，便于撤单和回报匹配
ClientState	SQLite	保存提醒、通知、自选、偏好等长期客户端状态
3.5 部署图
3.5.1 本地开发部署图
3.5.2 联调部署图
3.6 类图
3.7 接口设计
3.7.1 内部接口
内部接口指交易客户端子系统内部各模块之间的调用接口，不直接暴露给其他小组。

AuthService
方法	输入	输出	说明
login	account, password	LoginAction	登录并返回 apply/enroll/verify/success
enroll	account, publicKey	LoginResult	绑定证书
verify	account, signature	LoginResult	证书挑战验证
rebind	account, password, phone, idNumber	Result	重绑证书
logout	token	Result	清理会话
MarketService
方法	输入	输出	说明
searchStocks	query, board	StockList	股票搜索
getQuote	symbol	StockQuote	单只股票详情
getQuotes	symbols	StockQuote[]	批量报价
refreshWatchingQuotes	symbols	StockQuote[]	刷新关注股票
AccountService
方法	输入	输出	说明
getSummary	account	AccountSummary	资金 + 市值摘要
getFunds	account	FundAccount	查询资金
getHoldings	account	Holding[]	查询持仓
getCashFlows	account	CashFlow[]	查询资金流水
getStockFlows	account	StockFlow[]	查询证券流水
OrderService
方法	输入	输出	说明
submitOrder	OrderRequest	OrderResult	提交买入/卖出委托
cancelOrder	orderId, account	CancelResult	撤单
validateBuyOrder	OrderRequest	ValidateResult	买入校验
validateSellOrder	OrderRequest	ValidateResult	卖出校验
releaseFrozenResource	order	Result	释放冻结资源
ResultService
方法	输入	输出	说明
getFills	account	Fill[]	查询成交回报
syncOrderStatus	account	Result	同步委托状态
handleFill	Fill	Result	处理成交并触发刷新
ClientStateService
方法	输入	输出	说明
createAlert	AlertForm	Alert	新增提醒
updateAlert	id, patch	Alert	更新提醒
deleteAlert	id	Result	删除提醒
listNotifications	account	Notification[]	通知列表
toggleWatchlist	account, symbol	WatchResult	切换自选
updatePreferences	account, data	Result	更新偏好
3.7.2 前端—网关接口
前端只调用 Client Gateway 的统一接口。该接口是交易客户端内部实现接口，不作为与其他小组约定的外部接口。

方法	路径	功能
POST	/api/auth/login	登录，返回登录动作
POST	/api/auth/enroll	证书绑定
POST	/api/auth/verify	证书验证
POST	/api/auth/rebind	证书重绑
GET	/api/auth/me	当前用户
POST	/api/client/applications	客户端权限申请
GET	/api/client/applications	查询申请记录
GET	/api/account/summary	资产摘要
GET	/api/account/funds	资金余额
GET	/api/account/holdings	持仓
GET	/api/account/cash-flows	资金流水
GET	/api/account/stock-flows	证券流水
POST	/api/account/funds/deposit	存款
POST	/api/account/funds/withdraw	取款
POST	/api/account/passwords/trade	修改交易密码
POST	/api/account/passwords/withdraw	修改取款密码
GET	/api/market/stocks	行情列表/搜索
GET	/api/market/quotes	批量报价
GET	/api/trade/orders	委托列表
POST	/api/trade/orders	提交委托
POST	/api/trade/orders/:id/cancel	撤单
GET	/api/trade/fills	成交回报
GET	/api/client/alerts	提醒列表
POST	/api/client/alerts	新增提醒
PATCH	/api/client/alerts/:id	更新提醒
DELETE	/api/client/alerts/:id	删除提醒
GET	/api/client/notifications	通知列表
PATCH	/api/client/notifications/:id/read	标记通知已读
GET	/api/client/watchlist	自选股
POST	/api/client/watchlist/:symbol/toggle	切换自选
GET	/api/client/preferences	偏好
PATCH	/api/client/preferences	更新偏好
GET	/api/client/login-records	登录记录
POST	/api/client/login-records	写入登录记录
3.7.3 外部接口
外部接口指 Client Gateway 调用其他小组子系统的接口。该部分采用原设计报告中与其他小组约定的 /api/v1/* 版本作为最终联调接口，当前代码中的 mock 接口仅作为本地开发替代，不作为最终外部接口。

3.7.3.1 ACCOUNT 账户业务接口
ACCOUNT 包含资金账户与证券账户相关能力。

方法	路径	功能	调用方
POST	/api/v1/account/auth/login	资金账户卡号/账户 + 交易密码认证	AuthService
POST	/api/v1/account/auth/certificate/verify	首次登录安全证书认证	AuthService
POST	/api/v1/account/password/trade	修改交易密码	SettingsService
POST	/api/v1/account/password/withdraw	修改取款密码	SettingsService
GET	/api/v1/account/fund-accounts/{fund_account_id}	查询资金账户余额	AccountService / OrderService
POST	/api/v1/account/fund-accounts/{fund_account_id}/freeze	冻结买入资金	OrderService
POST	/api/v1/account/fund-accounts/{fund_account_id}/release	释放冻结资金	OrderService
POST	/api/v1/account/fund-accounts/{fund_account_id}/deposit	存款	AccountService
POST	/api/v1/account/fund-accounts/{fund_account_id}/withdraw	取款	AccountService
GET	/api/v1/account/fund-accounts/{fund_account_id}/cash-flows	查询资金流水	AccountService
GET	/api/v1/account/security-accounts/{security_account_id}/positions	查询证券持仓	AccountService / OrderService
POST	/api/v1/account/security-accounts/{security_account_id}/positions/freeze	冻结卖出持仓	OrderService
POST	/api/v1/account/security-accounts/{security_account_id}/positions/release	释放冻结持仓	OrderService
GET	/api/v1/account/security-accounts/{security_account_id}/stock-flows	查询证券流水	AccountService
GET	/api/v1/account/associations/check	校验资金账户与证券账户关联关系	AuthService / AccountService
3.7.3.2 TRADE 中央交易系统接口
方法	路径	功能	调用方
POST	/api/v1/trade/orders	提交买入/卖出委托	OrderService
GET	/api/v1/trade/orders	查询当前账户委托列表	OrderService
GET	/api/v1/trade/orders/{order_id}	查询单笔委托状态	OrderService
POST	/api/v1/trade/orders/{order_id}/cancel	撤销委托	OrderService
GET	/api/v1/trade/fills	查询成交回报	ResultService
WS	ws://<trade-host>/api/v1/trade/ws/orders	撮合回报推送	ResultService
GET	/api/v1/trade/market/{symbol}/best-book	查询最优买卖报价	MarketService / OrderService
说明：若中央交易系统暂未提供 WebSocket，客户端可使用 GET /api/v1/trade/fills 周期查询成交回报；若提供 WebSocket，则 ResultService 可切换为实时推送模式。

3.7.3.3 INFO 网上信息发布接口
方法	路径	功能	调用方
GET	/api/v1/info/stocks	股票列表、名称/代码搜索	MarketService
GET	/api/v1/info/stocks/{stock_code}	查询单只股票详情	MarketService
GET	/api/v1/info/stocks/{stock_code}/quote	查询最新行情	MarketService
GET	/api/v1/info/stocks/quotes	批量查询行情	MarketService
GET	/api/v1/info/stocks/{stock_code}/announcements	查询股票公告	MarketService
GET	/api/v1/info/stocks/{stock_code}/stats	查询日/周/月高低价	MarketService
3.7.3.4 ADMIN 交易系统管理接口
方法	路径	功能	调用方
GET	/api/v1/admin/stocks/{stock_code}/limit	查询当日涨跌停价格	OrderService / MarketService
GET	/api/v1/admin/stocks/{stock_code}/status	查询停牌/复牌/交易状态	OrderService
GET	/api/v1/admin/stocks/{stock_code}/rule	查询股票交易规则	OrderService
GET	/api/v1/admin/trading-day/status	查询交易日和开闭市状态	OrderService / MarketService
3.7.3.5 外部接口字段约定
字段	含义
investor_id	投资者编号
fund_account_id	资金账户编号
security_account_id	证券账户编号
stock_code	股票代码
stock_name	股票名称
order_id	委托编号
order_side	BUY / SELL 或 买入 / 卖出
order_price	委托价格
order_quantity	委托数量
filled_quantity	已成交数量
avg_price	成交均价
order_status	委托状态
available_amount	可用资金
frozen_amount	冻结资金
available_shares	可卖数量
frozen_shares	冻结股数
latest_price	最新成交价
best_bid	当前最高买价
best_ask	当前最低卖价
limit_up	涨停价
limit_down	跌停价
suspended	是否停牌
4. 详细设计
4.1 顺序图
4.1.1 用户登录与证书验证
4.1.2 查询行情
4.1.3 查询资金与持仓
4.1.4 发出买入委托
4.1.5 发出卖出委托
4.1.6 撤销委托
4.1.7 成交回报接收
4.1.8 价格提醒
4.2 执行概念
4.2.1 用户认证与证书管理
4.2.1.1 模块概述
用户认证与证书管理模块负责登录、客户端权限判断、首次证书绑定、证书挑战验证、证书重绑和登录记录写入。该模块连接 ACCOUNT 认证接口和 Client SQLite 证书数据。

4.2.1.2 IPO 图
4.2.1.3 功能
登录；

客户端权限申请判断；

首次证书绑定；

证书挑战验证；

证书重绑；

登录记录保存。

4.2.1.4 输入项
名称	标识	类型和格式	输入方式
账户	account	string	外部输入
交易密码	password	string	外部输入
公钥	publicKey	JSON/JWK	浏览器生成
签名	signature	base64 string	浏览器生成
手机号	phone	string	外部输入
身份证号	idNumber	string	外部输入
4.2.1.5 输出项
名称	标识	类型和格式	输出方式
登录动作	action	apply/enroll/verify/success	系统输出
登录结果	ok	boolean	系统输出
用户信息	user	object	系统输出
会话令牌	token	string	系统输出
错误信息	message	string	系统输出
4.2.1.6 设计方法（算法）
BEGIN login(account, password)
  IF account 或 password 为空 THEN
    返回参数错误
  END IF

  IF client_users 中不存在 account THEN
    返回 action=apply
  END IF

  调用 ACCOUNT 登录认证接口
  IF 认证失败 THEN
    写入失败登录记录
    返回交易密码错误
  END IF

  查询 client_certificates
  IF 首次登录或无证书 THEN
    返回 action=enroll
  ELSE
    生成 challenge 并返回 action=verify
  END IF
END
4.2.1.7 流程图
4.2.2 行情查询
4.2.2.1 模块概述
行情查询模块负责按代码、名称和板块查询股票，并展示最新价、买一卖一、日/周/月高低价、公告、涨跌停和交易状态。行情数据主要来自 INFO 系统，交易限制来自 ADMIN 系统。

4.2.2.2 IPO 图
4.2.2.3 功能
查询股票列表；

模糊搜索股票；

查询股票详情；

查询批量报价；

自动刷新行情；

为下单模块提供参考价格和交易限制。

4.2.2.4 输入项
名称	标识	类型和格式	输入方式
股票代码	stock_code	string(6)	外部输入
股票名称	stock_name	string	外部输入
板块	board	string	外部输入
刷新触发	refresh_signal	boolean	系统触发
4.2.2.5 输出项
名称	标识	类型和格式	输出方式
股票列表	stocks	array	系统输出
最新价格	latest_price	decimal	系统输出
买一价	best_bid	decimal	系统输出
卖一价	best_ask	decimal	系统输出
涨停价	limit_up	decimal	系统输出
跌停价	limit_down	decimal	系统输出
公告	announcement	string	系统输出
4.2.2.6 设计方法（算法）
BEGIN searchStocks(query, board)
  调用 INFO /api/v1/info/stocks
  IF 查询失败 THEN
    IF MarketCache 有旧数据 THEN
      返回旧数据并标记 stale
    ELSE
      返回行情服务异常
    END IF
  END IF

  FOR EACH stock IN stocks
    调用 ADMIN 查询涨跌停和交易状态
    合并行情数据与交易限制
  END FOR

  写入 MarketCache
  返回行情展示数据
END
4.2.2.7 流程图
4.2.3 账户资产查询
4.2.3.1 模块概述
账户资产模块负责从 ACCOUNT 系统查询资金和证券持仓，并结合行情价格计算证券市值、总资产、持有成本、持有损益和收益率。

4.2.3.2 IPO 图
4.2.3.3 功能
查询可用资金；

查询冻结资金；

查询证券持仓；

查询资金流水；

查询证券流水；

计算资产总值和持仓损益。

4.2.3.4 输入项
名称	标识	类型和格式	输入方式
账户	account	string	登录态获取
资金账户号	fund_account_id	string	登录态获取
证券账户号	security_account_id	string	登录态获取
4.2.3.5 输出项
名称	标识	类型和格式	输出方式
可用资金	available_amount	decimal	系统输出
冻结资金	frozen_amount	decimal	系统输出
持仓列表	positions	array	系统输出
证券市值	market_value	decimal	系统输出
总资产	total_equity	decimal	系统输出
持有损益	pnl_amount	decimal	系统输出
4.2.3.6 设计方法（算法）
BEGIN getAccountSummary(account)
  并行调用：
    ACCOUNT 查询资金账户
    ACCOUNT 查询证券持仓
    INFO 批量查询持仓股票现价

  IF 任一关键数据查询失败 THEN
    返回数据加载失败
  END IF

  FOR EACH position IN positions
    costPrice = Σ(Pi × Si) / Σ(Si)
    marketValue = latestPrice × shares
    pnlAmount = (latestPrice - costPrice) × shares
    pnlRate = pnlAmount / (costPrice × shares)
  END FOR

  totalEquity = available + frozen + Σ(marketValue)
  返回资产摘要
END
4.2.3.7 流程图
4.2.4 买入委托
4.2.4.1 模块概述
买入委托模块负责接收投资者买入请求，校验股票状态、涨跌停、委托数量和可用资金，冻结资金后向中央交易系统提交委托。

4.2.4.2 IPO 图
4.2.4.3 功能
校验股票是否存在；

校验股票是否停牌；

校验委托价格是否在涨跌停范围内；

校验委托数量是否为 100 的整数倍；

校验可用资金是否充足；

冻结资金；

提交买入委托；

处理提交失败后的冻结资金释放。

4.2.4.4 输入项
名称	标识	类型和格式	输入方式
股票代码	stock_code	string(6)	外部输入
委托价格	order_price	decimal	外部输入
委托数量	order_quantity	int	外部输入
买卖方向	order_side	BUY	系统生成
账户	account	string	登录态获取
4.2.4.5 输出项
名称	标识	类型和格式	输出方式
委托编号	order_id	string	系统输出
委托状态	order_status	enum	系统输出
错误码	code	string	系统输出
错误信息	message	string	系统输出
4.2.4.6 设计方法（算法）
BEGIN submitBuyOrder(req)
  校验股票代码、价格和数量格式
  查询 ADMIN 交易规则
  IF 股票停牌 THEN 返回 TRADE_SUSPENDED
  IF 价格超出涨跌停 THEN 返回 TRADE_PRICE_OUT_OF_RANGE
  IF 数量不是 100 的整数倍 THEN 返回 TRADE_INVALID_QUANTITY

  amount = price × quantity
  查询 ACCOUNT 资金账户
  IF 可用资金 < amount THEN 返回 ACCOUNT_INSUFFICIENT_FUNDS

  调用 ACCOUNT 冻结资金
  IF 冻结失败 THEN 返回 ACCOUNT_FREEZE_FAILED

  调用 TRADE 提交买入委托
  IF 提交失败 THEN
    调用 ACCOUNT 释放冻结资金
    返回 TRADE_SUBMIT_FAILED
  END IF

  返回委托结果
END
4.2.4.7 流程图
4.2.5 卖出委托
4.2.5.1 模块概述
卖出委托模块负责接收投资者卖出请求，校验股票状态、涨跌停、委托数量和可卖数量，冻结持仓后向中央交易系统提交委托。

4.2.5.2 IPO 图
4.2.5.3 功能
校验股票是否存在；

校验股票是否停牌；

校验价格是否在涨跌停范围内；

校验数量是否为 100 的整数倍；

校验可卖数量是否充足；

冻结卖出持仓；

提交卖出委托；

处理提交失败后的持仓释放。

4.2.5.4 输入项
名称	标识	类型和格式	输入方式
股票代码	stock_code	string(6)	外部输入
委托价格	order_price	decimal	外部输入
委托数量	order_quantity	int	外部输入
买卖方向	order_side	SELL	系统生成
账户	account	string	登录态获取
4.2.5.5 输出项
名称	标识	类型和格式	输出方式
委托编号	order_id	string	系统输出
委托状态	order_status	enum	系统输出
错误码	code	string	系统输出
错误信息	message	string	系统输出
4.2.5.6 设计方法（算法）
BEGIN submitSellOrder(req)
  校验股票代码、价格和数量格式
  查询 ADMIN 交易规则
  IF 股票停牌 THEN 返回 TRADE_SUSPENDED
  IF 价格超出涨跌停 THEN 返回 TRADE_PRICE_OUT_OF_RANGE
  IF 数量不是 100 的整数倍 THEN 返回 TRADE_INVALID_QUANTITY

  查询 ACCOUNT 证券持仓
  IF 可卖数量 < order_quantity THEN 返回 ACCOUNT_INSUFFICIENT_POSITION

  调用 ACCOUNT 冻结持仓
  IF 冻结失败 THEN 返回 POSITION_FREEZE_FAILED

  调用 TRADE 提交卖出委托
  IF 提交失败 THEN
    调用 ACCOUNT 释放冻结持仓
    返回 TRADE_SUBMIT_FAILED
  END IF

  返回委托结果
END
4.2.5.7 流程图
4.2.6 撤单
4.2.6.1 模块概述
撤单模块负责撤销尚未完全成交的委托。对于未成交委托，撤销全部剩余数量；对于部分成交委托，只撤销未成交部分；对于完全成交委托，拒绝撤单。

4.2.6.2 IPO 图
4.2.6.3 功能
查询委托状态；

判断是否可撤；

调用中央交易系统撤单；

买入委托释放资金；

卖出委托释放持仓；

刷新委托和资产。

4.2.6.4 输入项
名称	标识	类型和格式	输入方式
委托编号	order_id	string	外部输入
账户	account	string	登录态获取
4.2.6.5 输出项
名称	标识	类型和格式	输出方式
撤单状态	cancel_status	enum	系统输出
撤销数量	cancelled_quantity	int	系统输出
释放金额	released_amount	decimal	系统输出
错误信息	message	string	系统输出
4.2.6.6 设计方法（算法）
BEGIN cancelOrder(orderId, account)
  查询 TRADE 单笔委托状态
  IF 状态为已成交、已撤单、已过期、已拒绝 THEN
    返回不可撤单
  END IF

  调用 TRADE 撤单接口
  IF 撤单失败 THEN
    返回撤单失败原因
  END IF

  计算未成交数量 = 委托数量 - 已成交数量
  IF 买入委托 THEN
    释放未成交数量对应冻结资金
  ELSE IF 卖出委托 THEN
    释放未成交数量对应冻结持仓
  END IF

  返回撤单成功
END
4.2.6.7 流程图
4.2.7 成交回报
4.2.7.1 模块概述
成交回报模块负责查询或接收中央交易系统的成交结果，更新前端委托状态，并触发资金和持仓刷新。

4.2.7.2 IPO 图
4.2.7.3 功能
查询成交回报；

匹配委托；

更新成交数量和成交均价；

区分部分成交和完全成交；

刷新资金和持仓；

生成成交通知。

4.2.7.4 设计方法（算法）
BEGIN syncFills(account)
  调用 TRADE 查询成交回报
  FOR EACH fill IN fills
    匹配对应 order_id
    更新委托已成交数量和均价
    IF 委托全部成交 THEN 状态设为已成交
    ELSE 状态设为部分成交
  END FOR
  调用 AccountService 刷新资金和持仓
  返回成交回报列表
END
4.2.8 价格提醒
4.2.8.1 模块概述
价格提醒模块保存用户自定义提醒规则，并在行情刷新后判断当前价格是否达到触发条件。该功能属于客户端附加功能，数据存储在 SQLite。

4.2.8.2 IPO 图
4.2.8.3 设计方法（算法）
BEGIN checkAlerts(account)
  alerts = 查询监控中的提醒
  FOR EACH alert IN alerts
    quote = 查询股票当前价格
    IF alert.condition == 高于 AND quote.price >= triggerPrice THEN
      更新提醒状态为已触发
      写入通知
    ELSE IF alert.condition == 低于 AND quote.price <= triggerPrice THEN
      更新提醒状态为已触发
      写入通知
    END IF
  END FOR
END
4.3 状态图
4.3.1 用户登录状态图
4.3.2 行情查询状态图
4.3.3 委托状态图
4.3.4 价格提醒状态图
5. 用户界面
5.1 界面总体布局
交易客户端采用单页应用布局：

顶部栏：显示系统名称、登录用户、刷新按钮、退出登录；

左侧导航：工作台、行情中心、交易下单、委托成交、资产流水、价格提醒、安全设置；

主内容区：显示当前页面内容；

全局提示：显示操作成功、错误提示、成交通知和价格提醒。

5.2 登录界面
登录界面包括：

账户输入框；

交易密码输入框；

登录按钮；

客户端权限申请面板；

首次证书绑定提示；

证书验证进度提示；

证书重绑入口。

登录失败时显示具体提示：

未开通客户端权限；

交易密码错误；

证书验证失败；

账户被锁定；

外部认证服务不可用。

5.3 首页工作台
首页工作台用于展示投资者最关心的交易摘要信息：

可用资金；

冻结资金；

证券市值；

总资产；

最新委托；

最新成交；

价格提醒摘要；

行情快照。

5.4 行情中心
行情中心用于股票查询和交易入口跳转：

股票代码/名称搜索；

板块筛选；

股票列表；

股票详情；

最新价、买一价、卖一价；

日/周/月高低价；

涨跌停价；

股票公告；

买入、卖出、设置提醒入口。

5.5 交易下单页面
交易下单页面包括：

买入 / 卖出切换；

股票代码输入；

价格输入；

数量输入；

当前参考价显示；

涨跌停范围提示；

买入时显示预计占用资金；

卖出时显示可卖数量；

委托预览；

提交按钮。

5.6 委托与成交页面
委托与成交页面包括：

委托列表；

状态筛选；

委托详情；

可撤单按钮；

批量撤单；

成交回报列表；

成交均价、成交数量和成交时间展示。

5.7 资产与流水页面
资产与流水页面包括：

资金账户信息；

持仓列表；

持有成本；

当前价格；

持有损益；

资金流水；

证券流水；

存款；

取款。

5.8 价格提醒页面
价格提醒页面包括：

新增提醒；

提醒列表；

当前价格；

触发价格；

条件：高于 / 低于；

状态：监控中 / 已暂停 / 已触发；

暂停、恢复、删除操作。

5.9 安全设置页面
安全设置页面包括：

修改交易密码；

修改取款密码；

登录记录；

证书状态；

证书重绑入口；

偏好设置。

6. 数据库设计
6.1 概念结构设计
客户端数据库只存储客户端自有数据，不存储资金、持仓、委托、成交和行情权威数据。

6.2 逻辑结构设计
client_users(id, account, password, name, phone, id_number, first_login)

client_certificates(id, account, public_key, updated_at)

client_sessions(id, account, token, created_at, expires_at)

client_applications(id, account, type, status, created_at)

client_login_records(id, account, time, method, device, status)

client_alerts(id, account, symbol, condition, trigger_price, current_price, status, last_triggered, created_at, updated_at)

client_notifications(id, account, title, content, read, created_at)

client_watchlist(id, account, symbol)

client_preferences(account, data)
6.3 物理结构设计
表 1：客户端用户表 client_users
编号	属性名	字段名称	数据类型	长度	备注
1	用户编号	id	INTEGER	-	主键，自增
2	账户	account	TEXT	32	唯一，非空
3	密码	password	TEXT	128	mock 阶段使用，正式联调不保存交易密码
4	姓名	name	TEXT	64	可空
5	手机号	phone	TEXT	20	可空
6	身份证号	id_number	TEXT	32	可空
7	首次登录	first_login	INTEGER	1	0/1
表 2：证书表 client_certificates
编号	属性名	字段名称	数据类型	长度	备注
1	证书编号	id	INTEGER	-	主键，自增
2	账户	account	TEXT	32	外键
3	公钥	public_key	TEXT	-	JWK 公钥
4	更新时间	updated_at	TEXT	32	ISO 时间
表 3：客户端申请表 client_applications
编号	属性名	字段名称	数据类型	长度	备注
1	申请编号	id	INTEGER	-	主键，自增
2	账户	account	TEXT	32	非空
3	类型	type	TEXT	32	client-access
4	状态	status	TEXT	32	pending/approved/rejected
5	创建时间	created_at	TEXT	32	ISO 时间
表 4：登录记录表 client_login_records
编号	属性名	字段名称	数据类型	长度	备注
1	记录编号	id	INTEGER	-	主键，自增
2	账户	account	TEXT	32	非空
3	时间	time	TEXT	32	登录时间
4	登录方式	method	TEXT	32	密码/证书
5	设备	device	TEXT	128	浏览器/系统
6	状态	status	TEXT	32	成功/失败
表 5：价格提醒表 client_alerts
编号	属性名	字段名称	数据类型	长度	备注
1	提醒编号	id	INTEGER	-	主键，自增
2	账户	account	TEXT	32	非空
3	股票代码	symbol	TEXT	6	非空
4	条件	condition	TEXT	8	高于/低于
5	触发价	trigger_price	TEXT	32	Decimal 字符串
6	当前价	current_price	TEXT	32	Decimal 字符串
7	状态	status	TEXT	16	监控中/已暂停/已触发
8	触发时间	last_triggered	TEXT	32	可空
9	创建时间	created_at	TEXT	32	ISO 时间
10	更新时间	updated_at	TEXT	32	ISO 时间
表 6：通知表 client_notifications
编号	属性名	字段名称	数据类型	长度	备注
1	通知编号	id	INTEGER	-	主键，自增
2	账户	account	TEXT	32	非空
3	标题	title	TEXT	128	非空
4	内容	content	TEXT	512	非空
5	是否已读	read	INTEGER	1	0/1
6	创建时间	created_at	TEXT	32	ISO 时间
表 7：自选股表 client_watchlist
编号	属性名	字段名称	数据类型	长度	备注
1	编号	id	INTEGER	-	主键，自增
2	账户	account	TEXT	32	非空
3	股票代码	symbol	TEXT	6	非空
表 8：偏好设置表 client_preferences
编号	属性名	字段名称	数据类型	长度	备注
1	账户	account	TEXT	32	主键
2	偏好数据	data	TEXT	-	JSON 字符串
6.4 系统数据归属与共享
数据	权威归属	客户端是否持久化	客户端处理
客户端权限申请	CLIENT	是	SQLite 保存
证书公钥	CLIENT	是	SQLite 保存
证书私钥	浏览器本机	是，本机 IndexedDB	不上传服务端
登录记录	CLIENT	是	SQLite 保存
价格提醒	CLIENT	是	SQLite 保存
自选股/通知/偏好	CLIENT	是	SQLite 保存
资金余额	ACCOUNT	否	查询并展示
冻结资金	ACCOUNT	否	查询并展示
持仓	ACCOUNT	否	查询并展示
可卖数量	ACCOUNT	否	查询并展示
委托	TRADE	否	查询并展示
成交回报	TRADE	否	查询并展示
行情	INFO	否	查询、缓存、展示
涨跌停/停牌状态	ADMIN	否	下单前查询并校验
7. 运行设计
7.1 运行模块组合
本子系统运行时由以下模块组合：

前端 Vue SPA；

Client Gateway；

Client SQLite；

ACCOUNT Adapter；

TRADE Adapter；

INFO Adapter；

ADMIN Adapter；

本地开发时可选的 mock 外部服务。

运行路径为：

用户操作页面
  → 前端 clientApi
  → Client Gateway 路由
  → Service 业务模块
  → Cache / SQLite / Adapter
  → 外部业务系统
  → 返回网关统一数据
  → 前端刷新页面
7.2 运行控制
7.2.1 登录控制
用户访问登录页；

输入账户和交易密码；

网关判断是否已开通权限；

网关调用 ACCOUNT 完成认证；

根据证书状态进入绑定或验证流程；

登录成功后进入首页。

7.2.2 行情查询控制
用户进入行情中心；

前端发起行情查询；

网关查询 INFO 和 ADMIN；

前端展示行情；

系统定时刷新关注股票价格。

7.2.3 资产查询控制
用户进入首页或资产页；

网关并行查询资金、持仓、行情；

网关计算市值、总资产和盈亏；

前端展示资金、持仓和流水。

7.2.4 买入控制
用户输入买入信息；

前端进行基础校验；

网关进行价格、数量、资金校验；

资金账户系统冻结资金；

中央交易系统接收委托；

前端刷新委托与资金状态。

7.2.5 卖出控制
用户输入卖出信息；

前端展示可卖数量；

网关进行价格、数量、可卖数量校验；

证券账户系统冻结持仓；

中央交易系统接收委托；

前端刷新委托与持仓状态。

7.2.6 撤单控制
用户在委托列表点击撤单；

网关查询委托当前状态；

可撤时调用中央交易系统撤单；

根据买入/卖出释放冻结资金或冻结持仓；

前端刷新委托、资金和持仓。

7.2.7 成交回报控制
前端周期查询成交回报，或接收 WebSocket 推送；

网关匹配委托；

网关触发资金和持仓刷新；

前端展示成交通知和最新资产。

7.3 启动与部署
7.3.1 本地开发启动
npm install
启动客户端网关和本地外部服务：

.\start-gateway.cmd
启动前端：

npm run dev
7.3.2 联调部署
联调时保持前端配置不变：

VITE_CLIENT_API_BASE=http://localhost:3010/api
只修改网关侧外部服务地址：

ACCOUNT_SERVICE_BASE_URL=http://account-service-host
TRADE_SERVICE_BASE_URL=http://trade-service-host
INFO_SERVICE_BASE_URL=http://info-service-host
ADMIN_SERVICE_BASE_URL=http://admin-service-host
7.4 测试设计
测试类别	测试内容
登录测试	未开通权限、首次登录、证书绑定、证书验证、证书重绑、密码错误
行情测试	股票搜索、股票详情、刷新失败、无结果、涨跌停展示
资金测试	查询资金、存款、取款、取款密码错误、余额不足
持仓测试	空持仓、有持仓、可卖数量、冻结数量、盈亏计算
买入测试	正常买入、资金不足、价格越界、数量非法、股票停牌
卖出测试	正常卖出、持仓不足、重复卖出、价格越界、股票停牌
撤单测试	未成交撤单、部分成交撤单、已成交撤单失败
成交测试	完全成交、部分成交、成交后资金持仓刷新
提醒测试	新增、暂停、恢复、删除、触发提醒
联调测试	Adapter 替换真实接口后前端页面无需改动
8. 系统出错设计
8.1 出错信息
系统输出信息 / 错误码	含义	处理方法
COMMON_INVALID_ARGUMENT	输入参数不合法	前端提示修改输入
COMMON_UNAUTHORIZED	未登录或会话失效	跳转登录页
COMMON_NOT_FOUND	查询对象不存在	提示未找到
AUTH_BAD_CREDENTIALS	账户或交易密码错误	提示重新输入
AUTH_CERT_REQUIRED	需要绑定证书	进入证书绑定流程
AUTH_CERT_INVALID	证书验证失败	提示重试或重绑
CLIENT_ACCESS_REQUIRED	未开通客户端权限	展示申请面板
ACCOUNT_INSUFFICIENT_FUNDS	可用资金不足	展示当前可用资金
ACCOUNT_INSUFFICIENT_POSITION	可卖数量不足	展示当前可卖数量
ACCOUNT_WITHDRAW_PASSWORD_ERROR	取款密码错误	提示重新输入
TRADE_PRICE_OUT_OF_RANGE	委托价格超出涨跌停	展示涨跌停范围
TRADE_INVALID_QUANTITY	委托数量非法	提示必须为 100 股整数倍
TRADE_SUSPENDED	股票停牌或不可交易	禁止提交
TRADE_ORDER_NOT_CANCELABLE	委托不可撤销	刷新委托状态
TRADE_SUBMIT_FAILED	委托提交失败	提示失败原因并释放冻结资源
EXTERNAL_SERVICE_ERROR	外部子系统异常	展示重试按钮
MARKET_DATA_STALE	行情数据延迟	展示旧数据并标记延迟
DATABASE_ERROR	SQLite 数据库异常	提示系统维护，记录日志
8.2 补救措施
8.2.1 系统恢复
网关崩溃后重启 Client Gateway；

SQLite 异常时根据备份或初始化脚本恢复客户端自有数据；

外部服务不可用时前端展示错误提示，不影响其他页面基本使用；

行情查询失败时可展示上次缓存，并提示数据可能延迟；

下单失败但已冻结资源时，网关必须执行补偿释放。

8.2.2 定时备份
定期备份 SQLite 客户端自有数据；

重要配置文件纳入版本管理；

业务权威数据由对应外部子系统负责备份；

本地开发 mock 数据可通过 seed 文件重置。

8.2.3 人工操作
委托状态异常时，以中央交易系统返回状态为准；

资金或持仓异常时，以 ACCOUNT 系统权威数据为准；

证书异常时允许用户通过重绑流程恢复；

价格提醒异常时可清理并重新创建提醒；

系统维护人员应记录人工修复过程。

8.3 系统维护设计
网关提供 /health 接口用于存活检测；

网关对所有写操作记录 requestId、account、接口路径、耗时和结果；

日志不得记录密码、私钥和完整 token；

Adapter 层统一处理外部服务异常；

下单、撤单、冻结、释放等接口应支持幂等；

前端进行基础输入格式校验，网关进行严格业务校验；

使用参数化 SQL 操作 SQLite，避免注入风险；

定期维护接口文档、部署文档和数据库文档；

核心流程需要单元测试和集成测试；

与其他小组联调时优先在 Adapter 层处理字段和错误码差异。

9. 附录：代码迭代提示词
如需将本文档和当前代码交给 Codex 进行后续迭代，可使用以下提示词：

请以《股票交易系统——交易客户端子系统设计说明书》为最终设计基线，
在保留当前 Vue 3 前端 + Node.js Client Gateway + SQLite + Adapter 架构的前提下，
对当前代码进行增量改造，不要重写为 FastAPI，不要让前端直接调用外部服务。

优先完成以下任务：
1. 保留当前用户界面结构和客户端附加功能，包括登录、证书、首页、行情、下单、委托、资产、提醒、安全设置；
2. 将外部接口适配为设计报告中的 /api/v1/account、/api/v1/trade、/api/v1/info、/api/v1/admin 版本；
3. 保留前端到 Client Gateway 的 /api/* 接口，使前端无需直接适配其他组接口；
4. 在 Adapter 层完成当前 mock 接口与外部约定接口之间的字段映射；
5. 在 POST /api/trade/orders 中补齐服务端校验：股票存在、交易状态、涨跌停、数量 100 整数倍、买入资金、卖出可卖数量；
6. 增加资金冻结/释放逻辑：买入提交前冻结资金，撤单/过期/提交失败释放资金；
7. 增加持仓冻结/释放逻辑：卖出提交前冻结可卖数量，撤单/过期/提交失败释放持仓；
8. 增加 AdminAdapter，用于读取涨跌停和停牌状态；mock 阶段可由行情数据临时模拟；
9. 统一委托状态枚举，内部用 PENDING/PARTIAL/FILLED/CANCELLED/EXPIRED/REJECTED，前端展示中文；
10. 增强错误响应，保留 message，同时增加 code 字段；
11. 保证 SQLite 只保存客户端自有数据，不保存资金、持仓、委托、成交、行情等权威业务数据；
12. 增加必要测试，覆盖登录、买入、卖出、撤单、成交回报、资金冻结、持仓冻结等核心流程。
'''
out.write_text(content, encoding='utf-8')
out