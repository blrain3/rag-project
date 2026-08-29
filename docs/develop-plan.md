# Personal RAG Knowledge Base 开发文档

| 项 | 值 |
|---|---|
| 版本 | 2.0 |
| 更新日期 | 2026-08-26 |
| 项目定位 | 基于 Python + FastAPI + PostgreSQL/pgvector + LLM 的个人知识库 RAG 系统 |
| 部署目标 | 可长期迭代的个人项目，最终开源至 GitHub 并写入简历 |

## 0. 文档说明

本文件是项目唯一的开发计划来源（Single Source of Truth）。每个 Phase 包含：**目标、任务清单、交付物、验收标准**。只有当验收标准全部通过时，该 Phase 才允许标记为完成并进入下一阶段。

---

## 一、项目概述

### 1.1 解决的问题

用户将个人 Markdown / PDF 文档上传至系统，系统自动完成解析、切分、向量化与索引。用户以自然语言提问时，系统检索知识库中最相关的内容，将其作为上下文交给 LLM，生成**带来源引用**的回答。

### 1.2 核心数据流

```text
入库（离线）                          查询（在线）
─────────────────────                ─────────────────────
Document                             Question
   ↓ Parser                             ↓ Query Embedding
纯文本                                  ↓ Vector Search (Top-K)
   ↓ Chunker                            ↓ (Reranker, Phase 8)
Chunks                                  ↓ Build Context
   ↓ Embedding Model                    ↓ Prompt
Vectors                                 ↓ LLM
   ↓                                    ↓ Streaming Answer
PostgreSQL + pgvector                   ↓ Sources / Citation
```

### 1.3 设计原则

1. **不用 LangChain / LlamaIndex（第一阶段）**：本项目以理解 RAG 全链路为目的，Pipeline 手写实现；理解后再评估是否引入框架。
2. **小步提交，每步可验证**：每个 Phase 结束时项目必须处于可运行状态，禁止"写一堆代码再统一调试"。
3. **配置与环境分离**：所有配置经 `app/core/config.py` 集中管理，密钥只存在于 `.env`（已加入 `.gitignore`，永不入库）。

---

## 二、技术栈

### 2.1 第一版（Phase 0–7）

| 组件 | 选型 | 版本 | 说明 |
|---|---|---|---|
| 语言 | Python | 3.11.15 | |
| Web 框架 | FastAPI | 0.141.1 | |
| ASGI Server | Uvicorn | 0.52.4 | |
| 数据校验 | Pydantic | 2.13.4 | |
| 配置管理 | pydantic-settings | 2.15.0 | 读取 .env |
| 数据库 | PostgreSQL | ≥ 14 | |
| 向量扩展 | pgvector | ≥ 0.5 | |
| ORM | SQLAlchemy | 2.x | Phase 2 引入 |
| 迁移 | Alembic | 最新 | Phase 2 引入 |
| Embedding | sentence-transformers（BAAI/bge-m3） | 最新 | Phase 5 引入 |
| LLM | OpenAI 兼容 API | — | Phase 7 引入 |

### 2.2 后续引入（Phase 8+）

Reranker（BGE-reranker）、SSE 流式输出、Redis 缓存、Celery/ARQ 异步任务、S3/R2 对象存储、JWT 认证、Next.js 前端、Docker 部署。

---

## 三、项目结构（目标态）

```text
rag-project/
├── app/
│   ├── main.py               # 应用工厂，挂载路由
│   ├── core/
│   │   └── config.py         # 配置中心（pydantic-settings）
│   ├── api/                  # 路由层：只做参数校验与编排
│   │   ├── health.py
│   │   ├── documents.py
│   │   └── chat.py
│   ├── schemas/              # Pydantic 请求/响应模型
│   ├── models/               # SQLAlchemy ORM 模型
│   ├── services/             # 业务层
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   ├── retrieval_service.py
│   │   └── llm_service.py
│   └── rag/                  # RAG 核心算法
│       ├── chunker.py
│       ├── retriever.py
│       ├── prompt.py
│       └── pipeline.py
├── tests/                    # pytest 测试
├── documents/                # 本地测试文档（不入库）
├── docs/                     # 开发文档
├── .env / .env.example
├── requirements.txt
└── README.md
```

**规则：按 Phase 逐步创建文件，禁止一次性铺满目录。**

---

## 四、开发阶段规划

### Phase 0：工程基线 ✅（2026-08-26 完成）

| 项 | 内容 |
|---|---|
| 目标 | 让仓库达到可长期迭代的工程标准 |
| 任务 | 修正 .gitignore；requirements.txt 锁定版本；.env/.env.example；配置中心；API 分层；健康检查 |
| 交付物 | `app/core/config.py`、`app/api/health.py`、`requirements.txt`、`.gitignore`、`.env.example` |
| 验收 | `GET /` 与 `GET /api/health` 返回 200；`git status` 不再出现 `.venv/` |

> 历史教训：初版 `.gitignore` 写了 `.md`（会忽略全部文档）却没忽略 `.venv/`（4000+ 文件差点入库）。**.gitignore 必须在第一次 commit 前审一遍。**

### Phase 1：FastAPI 骨架 ✅（已完成，随 Phase 0 重构）

验收：`uvicorn app.main:app --reload` 启动正常，Swagger（/docs）可访问。

### Phase 2：PostgreSQL + pgvector ✅（2026-08-29 完成）

| 项 | 内容 |
|---|---|
| 目标 | 建立可迁移的数据库层 |
| 任务 | 安装 PostgreSQL 与 pgvector 扩展；`CREATE EXTENSION vector`；SQLAlchemy 2.0 engine/session；Alembic 初始化；documents 与 document_chunks 两张表的迁移 |
| 交付物 | `app/db/database.py`、`app/models/`、`alembic/`、首个 migration |
| 验收 | `alembic upgrade head` 成功；psql 中 `\d document_chunks` 可见 `vector` 类型列；`/api/health` 的 database 字段变为真实连接状态 |

表结构（实际落地，2026-08-29）：

```text
documents                 document_chunks
───────────────────       ────────────────────────────────
id             UUID PK     id            UUID PK
title          VARCHAR     document_id   UUID FK → documents.id (ON DELETE CASCADE)
source_type    VARCHAR     chunk_index   INTEGER  (uq: document_id+chunk_index)
source_path    TEXT        content       TEXT
content_text   TEXT        token_count   INTEGER
content_hash   VARCHAR(64) embedding     vector(1024)   -- bge-m3，见下
created_at     TIMESTAMPTZ created_at    TIMESTAMPTZ
updated_at     TIMESTAMPTZ
```

> `vector(1024)` 对应 Phase 5 选型 BAAI/bge-m3 的输出维度（1024）。维度常量集中在 `app/models/document.py` 的 `EMBEDDING_DIM`，换模型必须连同迁移与全量重嵌入一起处理，禁止只改常量。

### Phase 3：文档处理（Markdown 优先）

| 项 | 内容 |
|---|---|
| 目标 | `POST /api/documents` 上传 Markdown 并落库 |
| 任务 | 文件上传接口；Markdown 纯文本提取；Document 记录写入 |
| 验收 | 上传 redis.md 后 `GET /api/documents` 可见记录，数据库 content 为纯文本 |

### Phase 4：Chunking

| 项 | 内容 |
|---|---|
| 目标 | 将文档切分为适合 Embedding 的片段 |
| 任务 | Recursive Chunking（chunk_size=500，overlap=100，按 token/字符计）；chunk_index 顺序写入 |
| 交付物 | `app/rag/chunker.py` + 单元测试（不依赖数据库，纯函数测试） |
| 验收 | 单测覆盖：空文本、超长文本、overlap 正确性、边界切分 |

### Phase 5：Embedding

| 项 | 内容 |
|---|---|
| 目标 | Chunk → 向量 → pgvector |
| 任务 | sentence-transformers 加载 bge-m3；批量编码；向量入库 |
| 验收 | 入库后 SQL `SELECT embedding FROM document_chunks LIMIT 1` 返回 1024 维向量 |

### Phase 6：Vector Search

| 项 | 内容 |
|---|---|
| 目标 | 问题 → Top-K 相关 Chunk |
| 任务 | 查询向量化；`<=>`（cosine）相似度排序；Top-K 查询 |
| 验收 | 对 "Redis 支持哪些数据类型" 的检索，redis.md 相关 chunk 排名靠前，不相关文档得分显著更低 |

### Phase 7：RAG Pipeline（第一个完整 RAG）

| 项 | 内容 |
|---|---|
| 目标 | `POST /api/chat` 返回带 sources 的回答 |
| 任务 | 检索 → 构建 Prompt → 调用 LLM → 返回 answer + sources |
| 验收 | 回答内容基于检索资料；sources 正确指向文档与 score |

### Phase 8：Reranker

向量召回 Top-20 → BGE Reranker 精排 → Top-5。验收：构造一个"向量检索排错"的 case，rerank 后排序改善。

### Phase 9：SSE 流式输出 + Citation

LLM token 级流式返回；回答内嵌 `[1]` 引用并附来源定位。验收：前端可逐 token 渲染，引用可点击/可核对。

### Phase 10：Next.js 前端 + Docker 部署

页面：`/`（Chat）、`/knowledge`、`/knowledge/[id]`、`/settings`。交付 docker-compose（app + postgres + pgvector 镜像）。

---

## 五、API 设计（目标态）

```text
GET    /api/health
GET    /api/documents              # 列表
POST   /api/documents              # 上传（multipart）
GET    /api/documents/{id}         # 详情
DELETE /api/documents/{id}         # 删除（级联删 chunk）
POST   /api/documents/{id}/reindex # 重新切分+向量化
POST   /api/chat                   # 问答
GET    /api/conversations          # 后续
```

约定：统一响应结构、HTTP 状态码语义正确（400/404/422/500）、错误经全局 exception handler 返回统一 JSON。

## 六、质量与评估

Phase 7 完成后建立 `tests/eval/questions.json` 测试集（问题 → 期望命中文档），每次改动后跑：

- Retrieval Top-1 / Top-5 命中率
- Answer Faithfulness（是否编造）
- Answer Relevancy（是否答到点上）

**指标不回退是后续所有优化的前提。**

## 七、安全规范

1. `.env` 永不入库；密钥只在 `.env`；示例值放 `.env.example`。
2. 上传文件校验类型与大小，保存路径不可由用户输入直接拼接（防路径穿越）。
3. LLM 输出视为不可信内容，前端渲染需转义。

## 八、Git 规范

- 提交信息：`feat: / fix: / refactor: / test: / docs: / chore:` + 英文描述，一个提交只做一件事。
- 每个 Phase 至少一个提交，禁止最后一次性提交。
- 首个提交前必须确认 `.gitignore` 覆盖 `.venv/`、`.env`、`__pycache__/`。

## 九、风险清单

| 风险 | 缓解措施 |
|---|---|
| Embedding 模型更换导致维度不匹配 | metadata 记录模型名；换模型必须重建索引 |
| bge-m3 本地推理资源占用大 | 允许降级到 bge-small-zh；或改用 API Embedding |
| pgvector 未安装/版本过低 | Phase 2 第一步即验证 `CREATE EXTENSION vector` |
| LLM API Key 泄露 | 只在 .env；定期轮换；仓库历史中检索确认无泄露 |

## 十、简历表述（完成后）

> 基于 FastAPI、PostgreSQL/pgvector 与 LLM 构建个人知识库 RAG 系统，实现文档解析、智能分块、向量化、混合检索、重排序、上下文增强生成、流式输出及来源引用，并通过 SSE 实现实时 AI 对话；建立检索质量评估集，以指标驱动迭代。
