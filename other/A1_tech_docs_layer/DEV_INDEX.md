# DEV_INDEX — 项目开发索引

> **版本**：v2.0 | **更新**：2026-06-07

---

## 文档索引

| 文档 | 路径 | 用途 |
|------|------|------|
| 需求说明书 | [需求说明书.md](需求说明书.md) | 业务需求与验收标准 |
| 系统架构 | [系统架构.md](系统架构.md) | 技术栈与模块结构 |
| 数据设计 | [数据设计.md](数据设计.md) | 数据库表结构与字段 |
| 接口设计 | [接口设计.md](接口设计.md) | API 端点规范 |
| 实现方案 | [实现方案.md](实现方案.md) | 各模块实现要点 |
| 任务分解 | [任务分解.md](任务分解.md) | 任务进度与待办 |
| 开发说明书 | [开发说明书.md](开发说明书.md) | 环境配置与调试 |
| 前端方案设计 | [前端方案设计.md](前端方案设计.md) | 前端架构与函数清单 |
| 代码审查报告 | [代码审查报告_2026-06-07.md](代码审查报告_2026-06-07.md) | 最新代码审查结果 |

## 代码索引

| 模块 | 路径 | 说明 |
|------|------|------|
| 入口 | `app/main.py` | FastAPI 入口 + 生命周期 |
| 配置 | `app/core/config.py` | 全局配置 |
| 数据库 | `app/core/database.py` | MySQL 操作 |
| 路由工厂 | `app/core/router_factory.py` | 配置驱动路由 |
| 调度器 | `app/core/scheduler.py` | 定时采集 |
| 爬虫 | `app/crawler/` | 数据采集 |
| 清洗 | `app/cleaner/` | 数据清洗 |
| 通用统计 | `app/services/base_stats.py` | 基础统计 |
| 高级统计 | `app/services/advanced_stats.py` | scatter/lln/std |
| 前端 | `frontend/` | 静态页面 |

## 归档索引

旧版本文档已归档至：
- `other/A4_archive/2026-06-07/A1_tech_docs_layer/` — A1 层旧版
- `other/A4_archive/2026-06-07/A2_tests/` — 旧测试文件
- `other/A4_archive/2026-06-07/A3_scratch/` — 旧草稿文档
- `other/A4_archive/重构方案_Phase11_randomness/` — Phase 11 重构文档

## 当前状态

- **Phase**：12（完成）
- **需求完成度**：F-01 ~ F-17 全部 ✅
- **代码行数**：后端 ~47KB，前端 ~98KB
- **测试覆盖**：手动测试（无自动化）
