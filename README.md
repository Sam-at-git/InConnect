# 迎客通 InConnect

**中国酒店的前后台一体化客户体验平台**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 项目简介

迎客通 InConnect 是专为中国酒店打造的智能客户服务平台，通过整合企业微信等多渠道消息，实现客人需求的智能路由和工单闭环追踪。

**核心价值：** 将客人响应时间从 15 分钟缩短至 5 分钟以内，提升客户满意度，降低运营成本。

## 核心功能

- **全渠道消息整合** - 企业微信、微信公众号、小程序、OTA 平台消息统一收件箱
- **智能消息路由** - 基于规则和 AI 意图识别，自动分配消息给合适的服务人员
- **工单管理系统** - 自动创建工单、优先级排序、任务分配、闭环追踪
- **实时协作** - WebSocket 实时消息推送，跨部门协作
- **数据分析** - 响应时间、解决率、员工效率等运营指标看板

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 |
| **前端** | React 18, TypeScript, Vite, Ant Design |
| **数据库** | SQLite (开发/单机部署) |
| **容器化** | Docker, Docker Compose |

## 快速开始

### 前置要求

- Python 3.11+ 和 [uv](https://github.com/astral-sh/uv)
- Node.js 18+
- Git

### 方式一：本地开发（推荐）

**后端：**
```bash
cd backend
uv sync                                           # 安装依赖
mkdir -p data                                     # 创建数据目录
uv run alembic upgrade head                       # 运行数据库迁移
SECRET_KEY=dev-secret uv run uvicorn app.main:app --reload --port 8000  # 启动开发服务器
```

**前端：**
```bash
cd frontend
npm install       # 安装依赖
npm run dev       # 启动开发服务器 (端口 3011)
```

**访问服务：**
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 前端管理后台: http://localhost:3011

### 方式二：Docker Compose

```bash
# 克隆项目
git clone <repository-url>
cd InConnect

# 创建数据目录
mkdir -p data

# 启动所有服务
docker-compose up -d

# 访问服务
# - 后端 API: http://localhost:18000
# - 前端管理后台: http://localhost:13011
```

## 项目结构

```
InConnect/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/         # API 路由
│   │   ├── core/           # 核心模块 (认证、异常、安全)
│   │   ├── crud/           # 数据库操作层
│   │   ├── models/         # SQLAlchemy ORM 模型
│   │   ├── schemas/        # Pydantic 请求/响应模型
│   │   ├── services/       # 业务逻辑层
│   │   └── main.py         # 应用入口
│   ├── alembic/            # 数据库迁移
│   └── tests/              # 测试用例
├── frontend/               # React 前端
│   └── src/
│       ├── api/            # API 客户端
│       ├── pages/          # 页面组件
│       ├── components/     # 通用组件
│       └── stores/         # Zustand 状态管理
├── data/                   # SQLite 数据库文件目录
└── docker-compose.yml      # Docker 编排配置
```

## 开发命令

### 后端

```bash
uv run pytest tests/ -v                    # 运行测试
uv run pytest tests/ --cov=app             # 测试覆盖率
uv run ruff check backend/                 # 代码检查
uv run ruff format backend/                # 代码格式化
uv run mypy backend/                       # 类型检查
uv run alembic revision --autogenerate -m "描述"  # 创建迁移
```

### 前端

```bash
npm run build    # 生产构建
npm run lint     # ESLint 检查
npm run preview  # 预览生产构建
```

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| FastAPI | 8000 | 后端 API |
| React | 3011 | 管理后台前端 |

## 环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
# 数据库 (SQLite)
DATABASE_URL=sqlite+aiosqlite:///./data/inconnect.db

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 企业微信 (可选)
WECHAT_CORP_ID=your-corp-id
WECHAT_APP_SECRET=your-app-secret
```

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
