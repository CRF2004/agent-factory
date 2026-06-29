# Agent Factory NOW

Last updated: 2026-06-29

## 当前阶段

Phase A/B 后端基础设施已完成，正在搭建前端像素沙盒 UI（Phase C）。

## 当前状态

- Phase A（pgvector / LLM dmxapi / WebSearch Tavily / TaskRunner / 状态机）全部完成
- Phase B（Runtime 真实化 / Tool Registry API / Approval 自动创建）全部完成
- 7 个测试全部通过
- 默认 LLM model: `deepseek-v4-flash-guan`（via dmxapi）
- WebSearch 推荐 Tavily，预留了抽象接口，当前未配置真实 API key 时走 mock
- REPOSITORY_BACKEND=postgres + DMXAPI_API_KEY 即可在真实 PostgreSQL 上运行

## 正在做

前端像素沙盒 UI 搭建：Vite + React + TypeScript + Tailwind CSS + 自建像素设计系统。

## 下一步

1. 前端脚手架：`npm create vite` + 依赖安装
2. 像素设计系统：design tokens + atoms/molecules/organisms 组件库
3. 页面实现：Dashboard → Agent Workspace → Agent Designer → Task Workspace → Memory Workspace → Approval Center
4. 前后端联调

## 未决问题

- Tavily API key 待用户获取
- Web search provider 最终选型待用户调研确认

## 决策记录

- 前端：React + TypeScript + Vite + Tailwind CSS，自建像素设计系统
- ORM：保持 SQLAlchemy + Pydantic
- 队列：MVP 进程内，预留 TaskRunner Protocol
- LLM：dmxapi（OpenAI 兼容），默认 model `deepseek-v4-flash-guan`
- pgvector：第一版接入
