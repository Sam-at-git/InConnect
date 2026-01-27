"""
FastAPI Application Entry Point
迎客通 InConnect Backend
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.database import close_db, init_db
from app.core.exceptions import BusinessException
from app.core.logging import setup_logging
from app.core.performance import PerformanceMiddleware
from app.schemas.common import APIResponse
from app.api.v1 import health, auth, hotels, staff, tickets, webhook, messages, websocket, reports, batch
from app.api.v1 import settings as settings_api
# rules, permissions, audit - Temporarily disabled (missing dependencies)

# Setup logging
setup_logging()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan handler
    Manages startup and shutdown events
    """
    # Startup
    if settings.app_env == "development":
        await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
## 迎客通 InConnect API

客人消息智能路由与工单管理系统

### 主要功能

* **消息管理**: 接收和处理企业微信消息
* **工单系统**: 创建、分配、追踪工单
* **规则引擎**: 智能路由规则配置
* **数据报表**: 工单、员工、消息统计分析
* **权限管理**: 角色和权限矩阵配置
* **审计日志**: 完整的操作审计追踪

### 认证

大多数API需要JWT Bearer Token认证。请在请求头中包含：
```
Authorization: Bearer <your_token>
```

### 响应格式

所有API响应遵循统一格式：
```json
{
  "code": 0,
  "message": "Success",
  "data": {...}
}
```
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan,
    servers=[
        {"url": "http://localhost:8000", "description": "开发环境"},
        {"url": "https://api.inconnect.example.com", "description": "生产环境"},
    ],
    tags=[
        {
            "name": "health",
            "description": "健康检查和服务状态",
        },
        {
            "name": "auth",
            "description": "用户认证和授权",
        },
        {
            "name": "hotels",
            "description": "酒店信息管理",
        },
        {
            "name": "staff",
            "description": "员工信息管理",
        },
        {
            "name": "tickets",
            "description": "工单创建、查询、更新",
        },
        {
            "name": "messages",
            "description": "消息接收和发送",
        },
        {
            "name": "reports",
            "description": "数据统计和报表",
        },
        {
            "name": "rules",
            "description": "路由规则管理和测试",
        },
        {
            "name": "permissions",
            "description": "权限和角色管理",
        },
        {
            "name": "audit",
            "description": "审计日志查询",
        },
    ],
    contact={
        "name": "迎客通技术支持",
        "email": "support@inconnect.com",
    },
    license_info={
        "name": "MIT License",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add performance monitoring middleware
app.add_middleware(PerformanceMiddleware)


# Request ID middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add request ID to response headers"""
    import uuid

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Exception handlers
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """Business exception handler"""
    from app.core.logging import get_logger

    logger = get_logger("app.main")
    logger.warning(
        f"Business exception: {exc.message}",
        extra={"code": exc.code, "path": request.url.path},
    )

    return JSONResponse(
        status_code=200,
        content=APIResponse(code=exc.code, message=exc.message, data=exc.details).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    from app.core.logging import get_logger

    logger = get_logger("app.main")
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"path": request.url.path},
    )

    return JSONResponse(
        status_code=500,
        content=APIResponse(code=5000, message="Internal server error").model_dump(),
    )


# Include routers
app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["health"])
app.include_router(auth.router, prefix=settings.api_v1_prefix, tags=["auth"])
app.include_router(hotels.router, prefix="/api/v1/hotels", tags=["hotels"])
app.include_router(staff.router, prefix="/api/v1/staff", tags=["staff"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["tickets"])
app.include_router(webhook.router, prefix="/api/v1/webhook", tags=["webhook"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(batch.router, prefix="/api/v1/batch", tags=["batch"])
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["settings"])
# app.include_router(rules.router, prefix="/api/v1/rules", tags=["rules"])
# app.include_router(permissions.router, prefix="/api/v1/permissions", tags=["permissions"])
# app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }
