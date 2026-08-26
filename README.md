# Personal RAG Knowledge Base

基于 FastAPI + PostgreSQL/pgvector + LLM 的个人知识库 RAG 系统。开发计划见 [docs/develop-plan.md](docs/develop-plan.md)。

## 快速开始

```bash
# 1. 创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. 配置环境变量
copy .env.example .env   # 填入你的 LLM_API_KEY 等

# 3. 启动开发服务器
.venv\Scripts\python -m uvicorn app.main:app --reload
```

- API 文档（Swagger）：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health

## 当前进度

- [x] Phase 0 工程基线
- [x] Phase 1 FastAPI 骨架
- [ ] Phase 2 PostgreSQL + pgvector
- [ ] Phase 3–10 见开发文档
