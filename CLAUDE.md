# Agent Factory 项目协作约定

## 开发原则

### 1. 每次做出实质性改动后必须提交 commit

以下情况都算"实质性改动"：
- 完成一个功能模块
- 修复一个 bug
- 新建或修改任何源文件
- 更新依赖
- 更新文档或计划文件

每次完成一个逻辑单元的工作后，立即创建 commit，不要积攒大量改动。

### 2. Commit message 规范

- 使用英文描述
- 格式：`type: brief description`
- 类型：`feat`（新功能）、`fix`（修复）、`refactor`（重构）、`docs`（文档）、`chore`（杂项）
- 示例：`feat: add pgvector embedding support`、`fix: task output not persisted`

### 3. 不要修改不相关的文件

- 每个 commit 只包含与当前任务直接相关的改动
- 不要顺手改无关代码

### 4. 保持 `NOW.md` 同步

- 完成实质性工作后，更新 `NOW.md` 的 `Current`、`Next`、`Updated` 字段
- 不要在 `NOW.md` 之外维护多套进度记录

### 5. 敏感信息不进仓库

- API key、数据库密码等使用环境变量
- `.env` 文件已在 `.gitignore` 中排除
- 提交前检查没有硬编码凭据

### 6. 测试先过再 commit

- 提交前运行 `pytest backend/tests/ -v` 确保全部通过
- 新增功能要有对应测试

### 7. 代码风格

- Python：默认不加注释，命名自解释
- TypeScript/React：同样原则，不加冗余注释
- 不要引入将来可能用的抽象，只在需要时添加

### 8. 技术栈约定

- 前端：React + TypeScript + Vite + Tailwind CSS
- 后端：Python FastAPI + SQLAlchemy + Pydantic
- 数据库：PostgreSQL + pgvector
- LLM：dmxapi（OpenAI 兼容）
- 不要随意引入新依赖，确有需要时先确认

### 9. 分支策略

- `main` 分支保护，不直接 force push
- 大改动开 feature 分支
- 日常小改动可以直接在 main 提交
