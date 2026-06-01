# Documentation Index

本文档是本项目文档入口，建议从下列顺序开始阅读。

## 1. 快速上手

- PROJECT_GUIDE.md：项目背景、结构与主要流程
- TESTING_GUIDE.md：安装、启动、测试流程

## 2. 接口与架构

- API_CONTRACT.md：统一网关 API 与 mock 外部服务接口
- BACKEND_ARCHITECTURE.md：统一后端结构、数据归属与替换点

## 3. 集成与二次开发

- INTEGRATION_GUIDE.md：完整项目包集成清单与接入步骤
- DEVELOPMENT_GUIDE.md：二次开发指南、调试与扩展点

## 4. 关键入口

- 前端 API 入口：src/services/clientApi.ts
- 后端入口：backend_fastapi/main.py
- 客户端路由：backend_fastapi/client/router.py
- 业务编排：backend_fastapi/client/service.py
- Mock 数据：backend_fastapi/mock_modules/data/*.json
