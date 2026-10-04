# FastAPI Demo · AI掘金头条

基于 **FastAPI + 异步 SQLAlchemy + SQLite** 的新闻系统后端 Demo，包含用户认证、新闻浏览、收藏、浏览历史、Redis 缓存（自动降级）与 AI 问答。

> 📖 **从零到实战教学文档**（逐文件讲解 + 代码为什么这么写 + 学习重点分级）：
> `docs/FastAPI-Demo从零到实战教学文档.md`

## 快速开始

```bash
# 1. 创建并激活虚拟环境（已存在 .venv 可跳过）
python -m venv .venv

# 2. 安装依赖
.venv\Scripts\pip install -r requirements.txt

# 3. 初始化示例数据（分类 + 新闻，幂等可重复执行）
.venv\Scripts\python scripts\init_db.py

# 4. 导入课程项目真实数据（可选，8 分类 + 403 条新闻，覆盖示例数据）
.venv\Scripts\python scripts\import_course_data.py "path\to\database.sql"

# 5. 对齐课程表结构（可选：user 表 gender/phone 字段、related_news/ai_chat 表、admin 测试账号）
.venv\Scripts\python scripts\migrate_db.py

# 6. 启动服务（浏览器访问 http://127.0.0.1:8000/docs 查看交互式文档）
.venv\Scripts\uvicorn main:app --reload
```

内置测试账号（导入课程数据后可用）：**admin / admin123**。

接口自测：`test_main.http`（VS Code REST Client / JetBrains HTTP Client 可直接运行）。

## 功能接口

| 模块 | 接口 | 说明 |
| --- | --- | --- |
| 用户 | POST `/api/user/register` | 注册（bcrypt 加密 + 生成 Token，支持昵称/性别/手机号等） |
| 用户 | POST `/api/user/login` | 登录（Token 7 天有效） |
| 用户 | GET `/api/user/info` | 获取当前用户（需认证） |
| 用户 | PUT `/api/user/update` | 修改昵称/简介/头像/性别/手机号 |
| 用户 | PUT `/api/user/password` | 修改密码 |
| 新闻 | GET `/api/news/categories` | 新闻分类（Redis 缓存） |
| 新闻 | GET `/api/news/list` | 列表（分类筛选 + 分页 total/hasMore，Redis 缓存） |
| 新闻 | GET `/api/news/detail?id=` | 详情（浏览量+1 + 相关推荐，Redis 缓存） |
| 收藏 | GET/POST/DELETE `/api/favorite/...` | 检查/添加/取消/列表/清空（需认证） |
| 历史 | POST/GET/DELETE `/api/history/...` | 添加/列表/删除/清空（需认证） |
| AI | POST `/api/ai/chat` | 通义千问问答（需配置 API Key，登录用户自动记录） |
| AI | GET `/api/ai/history` | 我的问答历史（需认证） |

所有接口统一返回 `{code, message, data}` 结构；错误（401/404/422/500）由全局异常处理器统一格式化。

## 项目结构

```
fastapi_demo/
├── main.py               # 应用入口：CORS、异常注册、路由挂载、启动建表
├── config/
│   ├── db_conf.py        # 异步数据库引擎与会话（默认 SQLite，可切 MySQL）
│   └── cache_conf.py     # Redis 缓存封装（短超时 + 失败自动降级）
├── models/               # ORM 模型：User/UserToken/Category/News/RelatedNews/Favorite/History/AiChat
├── schemas/              # Pydantic 校验模型（读写分离）
├── crud/                 # 数据访问层（含 Cache-Aside 缓存逻辑 news_cache.py、AI 记录 ai.py）
├── routers/              # API 路由：users/news/favorite/history/ai
├── utils/                # 统一响应、bcrypt 加密、Token 认证、全局异常
├── scripts/
│   ├── init_db.py          # 初始化示例数据（5 分类 + 10 新闻）
│   ├── import_course_data.py # 导入课程 database.sql 真实数据（8 分类 + 403 新闻）
│   ├── migrate_db.py       # 对齐课程表结构（gender/phone、related_news/ai_chat、admin 账号）
│   └── smoke_test_api.ps1  # 全流程接口冒烟测试（29 项）
└── test_main.http          # 接口测试清单
```

## 可选配置

- **切换 MySQL**：安装 `aiomysql` 后，修改 `config/db_conf.py` 中的 `ASYNC_DATABASE_URL`。
- **启用 Redis 缓存**：本地安装并启动 Redis（默认 localhost:6379）。Redis 未启动时缓存自动降级为直查数据库，不影响业务。
- **启用 AI 问答**：设置环境变量 `AI_API_KEY`（阿里云百炼 DashScope 的 API Key，模型默认 qwen-plus），或修改 `routers/ai.py` 顶部常量。

## 与课程数据库（database.sql）的对齐情况

| 课程结构 | demo 状态 |
| --- | --- |
| user 表（含 gender/phone） | 已补齐字段，gender 用字符串 + Pydantic 枚举校验，phone 唯一索引 |
| user_token | 已有（7 天有效 Token） |
| news_category / news | 已有（导入 8 分类 + 403 条真实新闻） |
| related_news（静态推荐） | 已建表；表无数据时相关推荐自动回退同分类热门动态计算 |
| favorite / history | 已有（history 的 view_time 用 created_at 承担） |
| ai_chat（聊天记录） | 已建表；登录用户问答自动记录，`GET /api/ai/history` 可查 |

## 冒烟测试

```bash
# 先启动服务，再执行
powershell -ExecutionPolicy Bypass -File scripts\smoke_test_api.ps1
```
