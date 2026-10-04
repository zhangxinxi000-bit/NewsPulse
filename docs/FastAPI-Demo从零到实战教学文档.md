# FastAPI Demo · 从零到实战教学文档

> 目标：读完这份文档，你不仅能看懂 demo 里每一行代码，还能把它变成自己的项目实战经验。
> 面向对象：把 FastAPI 当第一门 Web 框架学习的小白，或想系统梳理后端知识的中级开发者。

---

## 0. 怎么读这份文档

这份文档把 demo 拆成 8 层，**按依赖顺序**讲解。建议这样读：

1. **第一遍（30 分钟）**：只读第 1、2 章 + 第 11 章（端到端演练），先建立"这个项目在干嘛"的整体画面，不纠结细节。
2. **第二遍（跟着敲）**：按 3 → 4 → 5 → 6 → 7 → 8 → 9 的顺序，对照文档把每个文件**自己动手敲一遍**（不要复制粘贴，敲完再对照）。
3. **第三遍（变自己的）**：完成第 12 章的"练习作业"，给项目加一个新功能（比如加一个"点赞"模块），你就真正掌握了。

### 重点分级图例（贯穿全文）

每个文件/知识点都标了等级，含义如下：

| 等级 | 含义 | 对待方式 |
| --- | --- | --- |
| 🔴 **必须亲手掌握** | 后端开发的核心概念，面试必问、换项目必用 | 自己敲、能默写、能讲出"为什么" |
| 🟡 **理解设计即可** | 设计意图重要，但实现细节可以靠 AI | 看懂思路，能改参数/配置，实现交给 AI |
| 🟢 **会用就行** | 工程配套内容，不体现核心能力 | 知道是干嘛的、怎么跑，直接让 AI 写 |

> 判断标准：**换个新项目（比如做一个商城）时，这段知识你还得自己写吗？** 得自己写 = 🔴；能描述清楚让 AI 写 = 🟡；根本不用碰 = 🟢。

---

## 1. 项目全景

### 1.1 这个 demo 是什么

一个**新闻资讯 App 的后端 API 服务**（对标今日头条/网易新闻的后台），名字叫"AI 掘金头条"。它提供了：

- 用户系统：注册、登录、改资料、改密码
- 新闻系统：分类浏览、列表分页、详情（带浏览量）、相关推荐
- 用户行为：收藏新闻、浏览历史
- AI 问答：调用通义千问大模型（可选功能）
- 工程能力：Redis 缓存（自动降级）、统一响应格式、全局异常处理、Token 认证

前端可以是 Vue/小程序/App，后端只负责提供 JSON 接口——这就是**前后端分离**架构。整个项目没有界面，用浏览器访问 `http://127.0.0.1:8000/docs` 就能看到交互式接口文档。

### 1.2 技术栈一览（每一项为什么选它）

| 技术 | 作用 | 为什么选它 |
| --- | --- | --- |
| **FastAPI** | Web 框架（处理 HTTP 请求/响应） | 现代 Python 首选：自动生成接口文档、异步性能好、类型提示友好 |
| **Uvicorn** | ASGI 服务器（让 FastAPI 跑起来） | FastAPI 官方推荐；`[standard]` 附带性能优化（uvloop 等） |
| **SQLAlchemy 2.0 + 异步** | ORM（操作数据库） | 不用写原生 SQL，用 Python 对象操作表；异步版本不阻塞事件循环 |
| **aiosqlite** | SQLite 的异步驱动 | 让 SQLite 能被异步访问（开发零配置，免装数据库） |
| **Pydantic** | 数据校验/序列化 | FastAPI 的"心脏"：请求参数自动校验、响应自动转 JSON |
| **email-validator** | 邮箱格式校验 | Pydantic 校验 EmailStr 类型需要它 |
| **bcrypt** | 密码加密 | 公认的安全密码哈希算法，自带加盐 |
| **httpx** | 异步 HTTP 客户端 | 用来调大模型 API（FastAPI 的 TestClient 底层也是它） |
| **redis** | Redis 客户端 | 给热点数据加缓存，减轻数据库压力 |

> 一句话技术栈定位：**FastAPI 管请求、Pydantic 管数据、SQLAlchemy 管数据库、Redis 管性能、bcrypt 管安全**。

### 1.3 目录结构总览

```
fastapi_demo/
├── main.py                  # 入口：装配整个应用
├── requirements.txt         # 依赖清单
├── test_main.http           # 接口手动测试清单
├── .gitignore               # Git 忽略规则
├── app.db                   # SQLite 数据库文件（运行时生成）
├── config/                  # 配置层：数据库、缓存
├── models/                  # 模型层：数据库表结构（ORM）
├── schemas/                 # 校验层：请求/响应数据结构（Pydantic）
├── crud/                    # 业务层：操作数据库的函数
├── routers/                 # 路由层：定义 API 接口
├── utils/                   # 工具层：认证、加密、异常、响应
└── scripts/                 # 脚本：初始化数据、导入数据、测试
```

**为什么这么分层？** 这是业界标准的"分层架构"，核心思想是**关注点分离**：

```
浏览器/前端
    │  HTTP 请求
    ▼
routers（路由层：定义"有什么接口"，只做参数接收和响应组装）
    │
    ▼
crud（业务层：定义"数据怎么存取"，只做数据库操作）
    │
    ▼
models（模型层：定义"数据库长什么样"，表结构）
    │
    ▼
SQLite/MySQL（真实数据）
```

- `schemas` 贯穿请求和响应：**进来时校验数据，出去时规范数据**。
- `utils` 是公共能力：任何一层都可能用到认证、异常、统一响应。
- `config` 是全局配置：数据库连哪、Redis 连哪。

这样分层的好处：加一个新功能（比如点赞），你只需**在对应层各加一个文件/函数**，不动其他层；出了问题也容易定位。

### 1.4 一个请求的完整旅程（拿"获取新闻详情"举例）

```
用户访问 GET /api/news/detail?id=1
  │
  ▼
uvicorn（服务器接收请求）
  │
  ▼
main.py（已挂载路由）→ routers/news.py 的 get_news_detail 被调用
  │
  ▼
FastAPI 先按 schemas 校验参数：id 必须是 int（Query(...) 必填）
  │
  ▼
routers 调 crud/news_cache.py（带缓存）：先查 Redis → 没命中
  │
  ▼
crud/news.py 查数据库（SQLAlchemy ORM → SQL → SQLite）
  │
  ▼
拿到 News 对象 → routers 把它转成 Pydantic（NewsDetailResponse）→ 组装 data
  │
  ▼
utils/response 统一序列化为 JSON：{code:200, message, data}
  │
  ▼
返回给前端
```

**关键理解**：请求是"从上往下"经过各层，响应是"从下往上"返回。每一层只干自己的事。

---

## 2. 动手运行（环境篇）

### 2.1 虚拟环境（.venv）

```bash
python -m venv .venv        # 创建
.venv\Scripts\activate      # Windows 激活（mac/Linux 用 source .venv/bin/activate）
```

**为什么需要虚拟环境？** 每个项目依赖的包版本可能冲突（项目 A 要 fastapi 0.1，项目 B 要 0.2）。虚拟环境给每个项目一个**独立的 Python 包仓库**，互不污染。这是 Python 工程化的第一课，🔴。

### 2.2 requirements.txt（🔴 要会读）

```text
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
aiosqlite
pydantic
email-validator
bcrypt
httpx
redis
```

- `uvicorn[standard]`：方括号是"extra"，表示安装附带推荐扩展（性能优化）。
- `sqlalchemy[asyncio]`：同样道理，附带 `greenlet` 等异步依赖。
- 安装命令：`.venv\Scripts\pip install -r requirements.txt`
- **为什么没写版本号？** 方便装最新版。正式项目一般锁版本（如 `fastapi==0.142.2`）甚至用 `uv.lock`/`poetry.lock` 保证可复现。这一点文档后面"现代视角"会讲。

### 2.3 启动

```bash
.venv\Scripts\uvicorn main:app --reload
```

拆解这条命令：
- `main:app` = 文件 `main.py` 里的变量 `app`。
- `--reload` = 开发模式：改代码自动重启（**只用于开发**，生产禁用）。
- 启动后访问：
  - `http://127.0.0.1:8000/` 健康检查
  - `http://127.0.0.1:8000/docs` **自动生成的接口文档**（FastAPI 最大的卖点之一）

> 🔴 面试常问：`--reload` 为什么不能用于生产？因为每次改动都重启进程，多进程部署时会导致服务中断；生产应该用 `--workers N` 配合反向代理（Nginx）。

### 2.4 app.db 是什么

SQLite 是**文件型数据库**，`app.db` 就是整个数据库（所有表都在里面）。好处：零配置、随项目走；坏处：不适合高并发生产。所以 demo 的配置层留了切换 MySQL 的口子（后面讲）。

---

## 3. 配置层 config/

### 3.1 config/db_conf.py —— 数据库引擎与会话（🔴）

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 数据库连接地址
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./app.db"

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,          # 开发时可改为 True 输出 SQL 日志
    pool_pre_ping=True,  # 连接前检查，避免使用失效连接
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**逐段讲解：**

1. **连接串 `sqlite+aiosqlite:///./app.db`**
   - 格式：`驱动类型+异步驱动://路径`。`sqlite` = 数据库类型，`aiosqlite` = 异步驱动，`./app.db` = 数据库文件路径（相对项目根目录）。
   - 想切 MySQL 只需改成：`mysql+aiomysql://用户名:密码@localhost:3306/news_app?charset=utf8mb4`。**这就是"配置与代码分离"的价值**——换数据库不动业务代码。

2. **`create_async_engine`（引擎）**
   - 引擎是"连接池"的管理者，负责创建/复用数据库连接（连接池避免每次请求都新建连接，性能关键）。
   - `echo=True` 会打印所有 SQL，**调试神器**，开发时强烈建议打开试试。
   - `pool_pre_ping=True`：每次从池里拿连接前先 ping 一下，防止拿到已断开的"僵尸连接"。

3. **`async_sessionmaker`（会话工厂）**
   - 会话（Session）是你"操作数据库"的入口：增删改查都通过它。
   - `expire_on_commit=False`：提交后对象属性不过期。默认 True 时，commit 后再访问对象属性会**触发一次额外查询**，改掉能避免很多坑。

4. **`get_db` 依赖（重点中的重点 🔴🔴）**
   - 这是一个**异步生成器（async generator）**，配合 `yield` 把 session 交给调用方。
   - 每个请求进来 → FastAPI 调用 `get_db` → `yield session`（路由里用）→ 请求结束 → 回到生成器 → `commit`/`rollback`/`close`。
   - **这就是 FastAPI 的"依赖注入（DI）"**：路由不用自己创建/关闭 session，框架帮你管理生命周期。
   - 异常时 `rollback` 保证数据一致性（事务要么全部成功，要么全部回滚）。

> 🔴 你要能讲清楚：什么是连接池、什么是依赖注入、为什么用 `yield` 而不是直接返回 session（因为要保证请求结束后的清理）。

### 3.2 config/cache_conf.py —— Redis 封装与自动降级（🟡）

```python
import json
from typing import Any

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 缓存过期时间（秒）
EXPIRE_CATEGORIES = 7200    # 分类、配置：2 小时
EXPIRE_NEWS_LIST = 1800     # 新闻列表：30 分钟
EXPIRE_NEWS_DETAIL = 300    # 新闻详情：5 分钟
EXPIRE_RELATED_NEWS = 1800  # 相关推荐：30 分钟

_redis_client = None
_redis_disabled = False

def get_redis_client():
    global _redis_client, _redis_disabled
    if _redis_disabled:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        import redis.asyncio as redis
        _redis_client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=2,
        )
        return _redis_client
    except Exception as e:
        _redis_disabled = True
        print(f"[cache] Redis 客户端创建失败，已禁用缓存，直查数据库：{e}")
        return None

def _mark_disabled():
    global _redis_disabled
    _redis_disabled = True

async def get_cache(key: str):
    client = get_redis_client()
    if client is None:
        return None
    try:
        return await client.get(key)
    except Exception as e:
        _mark_disabled()
        print(f"[cache] 获取缓存失败，已禁用缓存：{e}")
        return None

async def get_json_cache(key: str):
    data = await get_cache(key)
    if not data:
        return None
    try:
        return json.loads(data)
    except Exception as e:
        print(f"[cache] JSON 解析失败：{e}")
        return None

async def set_cache(key: str, value: Any, expire: int = 3600):
    client = get_redis_client()
    if client is None:
        return False
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await client.setex(key, expire, value)
        return True
    except Exception as e:
        _mark_disabled()
        print(f"[cache] 设置缓存失败，已禁用缓存：{e}")
        return False

async def delete_cache(key: str):
    client = get_redis_client()
    if client is None:
        return False
    try:
        await client.delete(key)
        return True
    except Exception as e:
        _mark_disabled()
        print(f"[cache] 删除缓存失败，已禁用缓存：{e}")
        return False

async def delete_cache_by_pattern(pattern: str):
    client = get_redis_client()
    if client is None:
        return False
    try:
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
        return True
    except Exception as e:
        _mark_disabled()
        print(f"[cache] 批量删除缓存失败，已禁用缓存：{e}")
        return False
```

**这段代码的设计精髓（🟡 理解意图即可，细节让 AI 写）：**

1. **为什么要缓存？** 新闻列表/详情是高频读取、低频修改的数据。每次都查数据库浪费 IO。Redis 是内存数据库，读它比读磁盘快一个数量级。

2. **过期时间为什么不同？** 分类几乎不变 → 缓存 2 小时；新闻详情浏览量随时在变 → 只缓存 5 分钟。**数据越稳定，缓存越久**。同时时间错开，避免所有 key 同时过期造成"缓存雪崩"（大批请求同时打穿到数据库）。

3. **自动降级（这个 demo 最值得学的工程细节之一）**
   - `socket_connect_timeout=1, socket_timeout=2`：连不上 Redis 时**快速失败**，而不是无限等待。这是之前修过的一个真实 bug：没有超时配置时，Redis 未启动会让请求永久挂起。
   - `_redis_disabled`：一旦失败就记下来，**本轮进程内不再尝试连 Redis**——否则每个请求都要等 1-2 秒超时，业务就废了。
   - 所有方法都 try/except 兜底：Redis 挂了 → 读返回 None → 上层直接查数据库 → 业务照常。这叫**优雅降级（fail-safe）**。

4. **`setex` 一条命令同时设值和过期时间**；`decode_responses=True` 让 Redis 返回 str 而不是 bytes；JSON 用 `ensure_ascii=False` 保证中文不变成 `\uXXXX`。

> 面试常问：缓存穿透（查不存在的数据，每次都打到库）怎么解决？缓存雪崩？缓存击穿？——这个 demo 只做了"雪崩防护（过期时间错开）+ 降级"，穿透/击穿是你可以继续补的方向（文档末尾"进阶方向"有提示）。

---

## 4. 模型层 models/ —— 数据库表长什么样

**先搞懂两个概念（🔴）：**

1. **ORM 是什么**：Object-Relational Mapping（对象关系映射）。把"数据库表"映射成"Python 类"，把"一行数据"映射成"一个对象"。你操作 `User` 对象，SQLAlchemy 帮你翻译成 `INSERT INTO user ...` 这样的 SQL。**好处：不用写 SQL、类型安全、改表结构改 Python 代码即可。**

2. **Mapped 语法（SQLAlchemy 2.0 风格）**
   ```python
   id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
   ```
   - `Mapped[int]`：声明"这个属性是 int 类型"（类型提示，写代码时有自动补全）。
   - `mapped_column(...)`：定义数据库列的具体属性（主键、长度、默认值...）。
   - `Optional[str]` = 可空（数据库 NULL）；`String(50)` = 长度 50 的字符串。

### 4.1 models/base.py —— 公共基类（🟡）

```python
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )
```

- `DeclarativeBase`：所有模型类的"祖宗"。所有模型继承它，SQLAlchemy 就知道"这些类是表"。
- `created_at / updated_at`：**所有表自动拥有**的公共字段（基类定义了，子类不用重复写）。
  - `default=datetime.now`：插入时自动填当前时间。
  - `onupdate=datetime.now`：更新时自动改成当前时间。**这是数据库层的"审计字段"**，任何一行数据都能知道"什么时候建的、最后什么时候改的"。
- 这就是"继承"在工程上的经典用法：把公共逻辑提到基类，避免 7 张表重复 14 次定义。

### 4.2 models/users.py —— 用户与令牌（🔴）

```python
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="加密密码")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="头像URL")
    gender: Mapped[str] = mapped_column(String(10), default="unknown", nullable=False, comment="性别 male/female/unknown")
    bio: Mapped[Optional[str]] = mapped_column(String(200), comment="个人简介")
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, comment="手机号")

    tokens: Mapped[list["UserToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class UserToken(Base):
    __tablename__ = "user_token"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="令牌ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True, comment="用户ID")
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False, comment="令牌值")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")

    user: Mapped["User"] = relationship(back_populates="tokens")

    def __repr__(self):
        return f"<UserToken(user_id={self.user_id}, expires_at={self.expires_at})>"
```

**逐段讲解：**

1. **`hashed_password` 不是 `password`** —— 数据库里**永远不存明文密码**，只存 bcrypt 哈希（第 7 章讲）。看到这个命名你就知道：这是安全意识。

2. **`unique=True` 的威力**：数据库层面保证用户名/邮箱/手机号不重复，比在代码里 if 判断更可靠（并发时两个请求同时注册同名用户，代码判断会漏，唯一索引兜底）。面试会问"唯一性为什么用数据库约束而不是应用层判断"。

3. **`index=True`**：给经常查询的字段建索引（登录查 username、按 token 查用户）。没索引时是全表扫描，数据多了会慢。

4. **`ForeignKey("user.id")`（外键）**：UserToken.user_id 引用 User.id。数据库层保证"不能给不存在的用户发 token"。**外键 = 表之间的"引用关系"声明**。

5. **`relationship`（ORM 关系）**
   - `tokens` 让你能通过 `user.tokens` 直接拿到这个用户的所有 token（SQLAlchemy 自动帮你 join 查询）。
   - `back_populates` 是双向关联：User.tokens 和 UserToken.user 互相指向。
   - `cascade="all, delete-orphan"`：删掉用户时，它的 token 自动删（级联删除），避免留孤儿数据。
   - 🔴 理解：**外键是数据库层面的约束，relationship 是 Python 层面的便捷导航**，两个都要写。

6. **`__repr__`**：调试时打印对象看到的友好格式（否则看到 `<User object at 0x...>`）。

> 设计要点：**认证 Token 存数据库表**而不是纯内存，是为了**服务重启后用户登录态不丢**，而且能随时"踢掉"某个 token（删记录即可）。这是"可控"的设计——比无状态方案（JWT）更难被滥用（JWT 发出去就收不回了）。两种方案的取舍见第 12 章。

### 4.3 models/news.py —— 分类与新闻（🔴）

```python
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Category(Base):
    __tablename__ = "news_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class News(Base):
    __tablename__ = "news"

    __table_args__ = (
        Index("fk_news_category_idx", "category_id"),
        Index("idx_publish_time", "publish_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="新闻简介")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图片URL")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(ForeignKey("news_category.id"), nullable=False, comment="分类ID")
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="浏览量")
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="发布时间")

    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"
```

1. **为什么 `content` 用 `Text`，标题用 `String(255)`？** 新闻正文可以很长，用可变长的大文本类型；标题长度固定限制（255）。**字段类型/长度 = 第一道数据约束**。
2. **为什么 `category_id` 存"数字 id"而不是存"分类名字符串"？**
   - 避免冗余：分类改名，新闻不用动。
   - 避免歧义：字符串拼写错误会创造新"分类"。
   - 这是**数据库三范式**的核心思想：消除冗余、用主键关联。🔴 面试必问。
3. **`__table_args__` 里的联合索引**：按分类查新闻（WHERE category_id=?）、按时间排序（ORDER BY publish_time DESC）是高频查询，所以建索引。**索引 = 空间换时间**，字段越常被 WHERE/ORDER BY/JOIN，越该建索引。
4. **`views` 默认 0**：浏览量从 0 开始累计，接口里每次访问 +1。

### 4.4 models/favorite.py 与 models/history.py —— 关系表（🔴 掌握"多对多"思想）

```python
# favorite.py
class Favorite(Base):
    __tablename__ = "favorite"
    __table_args__ = (UniqueConstraint("user_id", "news_id", name="uq_user_news"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True, comment="用户ID")
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, index=True, comment="新闻ID")
```

```python
# history.py
class History(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="历史记录ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True, comment="用户ID")
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, index=True, comment="新闻ID")
```

**这是"多对多关系"的标准建模**：一个用户 ↔ 多条新闻。中间表（也叫关联表）每行 = "谁收藏了哪条新闻"。

- **Favorite 的 `UniqueConstraint("user_id","news_id")`**：同一个用户不能重复收藏同一新闻。**唯一约束（联合唯一）**是数据库层保证的防重，比代码 if 判断可靠。
- **为什么加 `id` 主键而不直接用 (user_id, news_id) 当主键？** 便于后续扩展（比如收藏加备注字段），也符合常规习惯。
- **Favorite 和 History 结构几乎一样，为什么不合成一张表？** 语义不同：收藏是"主动持久行为"，历史是"浏览足迹"。分开维护各自的接口和规则（比如历史支持删单条、收藏支持清空）。**表设计先按业务语义划分，别为了"省事"硬合**。

### 4.5 models/related_news.py 与 ai_chat.py —— 补充表（🟡）

```python
# related_news.py：相关新闻关联表（推荐系统）
class RelatedNews(Base):
    __tablename__ = "related_news"
    __table_args__ = (UniqueConstraint("news_id", "related_news_id", name="news_related_unique"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, index=True)
    related_news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), nullable=False, index=True)
```

```python
# ai_chat.py：AI 聊天记录表
class AiChat(Base):
    __tablename__ = "ai_chat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id"), nullable=True, index=True, comment="用户ID（可空，匿名问答不记录归属）"
    )
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="用户消息")
    response: Mapped[str] = mapped_column(Text, nullable=False, comment="AI回复")
```

- `related_news`：**自己引用自己**的外键（两个列都指向 news.id），表示"新闻 A 关联新闻 B"。这是课程数据库里的"静态推荐"方案；demo 里这张表目前是空的，相关推荐逻辑会**自动回退**到"同分类热门"动态计算（见 6.2）。
- `ai_chat.user_id` 为什么可空？AI 问答允许匿名使用（不强制登录），所以记录归属是可选的。**字段可空性 = 业务规则的数据库表达**。
- 注意 `related_news` 没有继承 `Base` 的 created_at？——它继承了（`from models.base import Base`），只是没显式写出来。所有模型的 `created_at/updated_at` 都由基类自动提供。

### 4.6 models/__init__.py —— 汇总导出（🟢）

```python
from models.ai_chat import AiChat
from models.base import Base
from models.favorite import Favorite
from models.history import History
from models.news import Category, News
from models.related_news import RelatedNews
from models.users import User, UserToken

__all__ = ["Base", "User", "UserToken", "Category", "News", "RelatedNews", "Favorite", "History", "AiChat"]
```

**为什么要有这个文件？** 让 `from models import Base, User, News` 一次导入所有模型。更重要的是：`Base.metadata.create_all` 需要**所有模型类都被 import 过**才会建对应的表——这个文件保证"import models 一次 = 所有表都注册"。没经验的人经常踩这个坑：新加了一个模型文件却忘了在这里导入，结果表没建出来。

> 🟡 记住一个工程原则：**包（文件夹）的 `__init__.py` 是包的"门面"**，决定外部怎么用这个包。好的门面 = 外部一行 import 就能用到全部能力。

---

## 5. 校验层 schemas/ —— 请求与响应的"模具"

**先搞懂 Pydantic（🔴）：**

- Pydantic 是一个**数据校验库**。你定义一个类描述"数据长什么样"（字段名+类型+规则），它自动做两件事：
  1. **进来时校验**：请求体不符合规则（比如邮箱格式错、密码太短）→ 自动返回 422 错误，不用你写一行 if。
  2. **出去时序列化**：把 Python 对象/ORM 对象转成 JSON 前的标准结构。
- 每个 schema 就是一个"模具"：**读（请求）模型**定义"客户端必须给什么"；**写（响应）模型**定义"我们返回什么"。

### 5.1 schemas/base.py（🟡）

```python
from typing import Any
from pydantic import BaseModel

class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None
```

统一的响应结构声明。`Any = None` 表示 data 可以是任何东西。实际响应由 `utils/response.py` 生成，这个类更像"接口文档注释"——告诉读者整个 API 的响应长什么样。**模式**：`{code, message, data}` 是前后端约定好的"信封"，前端拿到先看 code 再取 data。

### 5.2 schemas/users.py（🔴 重点看校验规则怎么写）

```python
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(description="邮箱")
    password: str = Field(min_length=6, max_length=100, description="密码")
    nickname: Optional[str] = Field(default=None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(default=None, max_length=255, description="头像URL")
    gender: Optional[Literal["male", "female", "unknown"]] = Field(default=None, description="性别")
    bio: Optional[str] = Field(default=None, max_length=200, description="个人简介")
    phone: Optional[str] = Field(default=None, max_length=20, pattern=r"^\+?\d{5,20}$", description="手机号")


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(default=None, max_length=50, description="昵称")
    bio: Optional[str] = Field(default=None, max_length=200, description="个人简介")
    avatar: Optional[str] = Field(default=None, max_length=255, description="头像URL")
    gender: Optional[Literal["male", "female", "unknown"]] = Field(default=None, description="性别")
    phone: Optional[str] = Field(default=None, max_length=20, pattern=r"^\+?\d{5,20}$", description="手机号")


class UserChangePassword(BaseModel):
    old_password: str = Field(min_length=6, max_length=100, description="原密码")
    new_password: str = Field(min_length=6, max_length=100, description="新密码")


class UserInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None


class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse
```

**逐段讲解：**

1. **`Field(...)` 声明规则**：`min_length=2` = 至少 2 个字符；`EmailStr` = 必须是合法邮箱（配合 email-validator 包）；`pattern=r"^\+?\d{5,20}$"` = 手机号正则（5-20 位数字，可带 + 号）。
   - **校验规则写在"数据入口"**：非法输入在进入业务逻辑前就被拦下，路由里就不用写一堆 if。
   - 这正是 Pydantic 最大的价值：**声明式校验**——你"声明"规则，框架执行。

2. **为什么拆成 UserCreate / UserUpdate / UserInfoResponse 三个类？**
   - `UserCreate`：注册时的输入（必填 username/email/password）。
   - `UserUpdate`：改资料时的输入（全可选，因为用户可能只改一项）。
   - `UserInfoResponse`：返回给前端的用户信息——注意它**不含 password**，也**不含 hashed_password**！**响应模型 = 隐私边界**：只暴露该暴露的字段。如果把 User ORM 直接返回，密码哈希就泄露出去了。🔴 这个安全意识必须刻进脑子里。

3. **`ConfigDict(from_attributes=True)` 是干嘛的？**
   - 默认 Pydantic 只能从字典创建对象。加上这个配置，就能直接从 **ORM 对象**创建（`UserInfoResponse.model_validate(user)` 其中 user 是 User 实例）。
   - 一句话：**让 Pydantic 能"读取"ORM 对象的属性**。这是 schemas 和 models 之间的"桥"。

4. **`Optional[str] = None`**：字段可以缺省。请求时没传 nickname → 自动填 None，不会报错。

5. **`UserAuthResponse` 组合了 token + user_info**：登录/注册接口一次返回两样东西。**schema 可以嵌套 schema**，这是"响应组装"的基础。

### 5.3 schemas/news.py（🟡 重点是"列表 vs 详情"的载荷设计）

```python
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    sort_order: int


class NewsItemBase(BaseModel):
    """新闻列表项（不含正文，减小列表载荷）。"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int
    views: int
    publish_time: Optional[datetime] = None


class RelatedNewsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    views: int


class NewsDetailResponse(BaseModel):
    """新闻详情响应（含正文）。"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str] = None
    content: str
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int
    views: int
    publish_time: Optional[datetime] = None


class NewsListData(BaseModel):
    list: List[NewsItemBase]
    total: int
    has_more: bool
```

**设计精髓（这是真实的工程经验）：**

- **列表（NewsItemBase）不含 `content`（正文）**，只有标题、简介、封面、浏览量。为什么？列表页同时展示几十条新闻，如果每条都带几千字正文，**响应体巨大、浪费带宽**。详情页才需要完整正文（NewsDetailResponse 才有 `content`）。
- **这就是"按需返回字段"**：不同场景给不同大小的数据。看似小事，在大流量下是实打实的性能优化。
- `RelatedNewsResponse` 是更精简的"推荐卡片"（连分类都不要了）。
- `NewsListData` 定义分页三件套：`list / total / hasMore`——前端拿 total 显示"共 N 条"，拿 hasMore 判断"还有没有下一页"。

### 5.4 schemas/favorite.py、history.py、ai.py（🟢🟡）

```python
# favorite.py
class FavoriteAddRequest(BaseModel):
    news_id: int = Field(gt=0, description="新闻ID")   # gt=0：必须大于 0

class FavoriteResponse(BaseModel):
    id: int
    news: NewsItemBase    # 复用新闻的 schema！
```

```python
# history.py —— 结构同 favorite
class HistoryAddRequest(BaseModel):
    news_id: int = Field(gt=0, description="新闻ID")

class HistoryResponse(BaseModel):
    id: int
    news: NewsItemBase
```

```python
# ai.py
class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000, description="用户问题")

class ChatHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    message: str
    response: str
    created_at: Optional[datetime] = None
```

- `Field(gt=0)`：新闻 ID 必须是正整数（>0）。**边界校验**：防止传 `news_id=-1` 这种脏数据。
- `FavoriteResponse` 里 **复用 `NewsItemBase`**：收藏列表返回"收藏记录 + 新闻摘要"。**schema 复用 = 避免重复定义**，也是分层的好处。
- 这就是"响应模型"的组装技巧：嵌套组合出前端需要的完整结构。

---

## 6. 业务层 crud/ —— "操作数据库的函数库"

**crud = Create Read Update Delete**。这一层放所有**直接操作数据库**的函数。为什么单独一层？因为：
1. 路由层保持"薄"——只管接收参数、调用、返回。
2. 多个接口复用同一个 crud 函数（比如收藏和新闻详情都查新闻）。
3. 换数据库/加缓存时只改这一层。

### 6.1 crud/users.py —— 用户业务（🔴）

```python
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserCreate, UserUpdate
from utils.security import get_hash_password, verify_password

TOKEN_EXPIRE_DAYS = 7


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    return await db.get(User, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_hash_password(user_in.password),
        nickname=user_in.nickname,
        avatar=user_in.avatar,
        gender=user_in.gender or "unknown",
        bio=user_in.bio,
        phone=user_in.phone,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def create_token(db: AsyncSession, user_id: int) -> str:
    token = secrets.token_hex(32)
    expires_at = datetime.now() + timedelta(days=TOKEN_EXPIRE_DAYS)
    db.add(UserToken(user_id=user_id, token=token, expires_at=expires_at))
    await db.commit()
    return token


async def get_user_by_token(db: AsyncSession, token: str) -> Optional[User]:
    stmt = (
        select(User)
        .join(UserToken, UserToken.user_id == User.id)
        .where(UserToken.token == token, UserToken.expires_at > datetime.now())
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user: User, user_in: UserUpdate) -> User:
    data = user_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        if value is not None:
            setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str) -> bool:
    if not verify_password(old_password, user.hashed_password):
        return False
    user.hashed_password = get_hash_password(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True
```

**逐段讲解（这段是你最该吃透的业务代码）：**

1. **查询的三板斧**：`select(Model).where(条件)` → `await db.execute(stmt)` → `result.scalar_one_or_none()`。
   - `scalar_one_or_none()`：取"唯一一行"，没有返回 None，有多行会**报错**（帮你在开发期发现 SQL 写错）。对照：`scalars().all()` 取所有行，`scalar_one()` 必须恰好一行。
   - `db.get(User, user_id)`：按主键查，最简写法。

2. **注册流程（create_user）**
   - 密码先 `get_hash_password`（bcrypt）再入库——**明文密码永不落库**。
   - `db.add(user)` 加入会话 → `await db.flush()` **立即执行 SQL 但不提交事务**。为什么要 flush？因为下一步要拿 `user.id`（自增主键要在数据库执行后才知道），而真正"落盘"交给 get_db 依赖最后的 commit。
   - `await db.refresh(user)`：从数据库重新读一遍最新值（拿到 id、created_at 等）。
   - **flush vs commit**：flush 只是发 SQL，commit 才真正提交事务。事务没提交前，其他请求看不到你的数据。

3. **登录校验（authenticate_user）**
   - `verify_password(明文, 哈希)`：bcrypt 重新哈希比对。**永远不要自己设计加密算法**，用成熟库。

4. **Token 生成（create_token）—— 认证的核心**
   - `secrets.token_hex(32)`：生成 64 位十六进制**密码学安全随机数**。为什么不用 `random`？因为 random 可预测，会被撞库攻击。`secrets` 是专门用于安全的模块。🔴 这是安全意识的体现。
   - `timedelta(days=TOKEN_EXPIRE_DAYS)`：7 天后过期。
   - token 存 `user_token` 表：**服务重启登录态不丢**，还能主动失效（删记录）。

5. **按 token 查用户（get_user_by_token）**
   - `join`：把 user 和 user_token 两张表按 user_id 连起来查。
   - 条件 `expires_at > datetime.now()`：**只认未过期的 token**。过期 = 查不到 = 未登录。

6. **部分更新（update_user）—— 经典技巧 🔴**
   - `user_in.model_dump(exclude_unset=True)`：只导出**用户这次传了的字段**（没传的不要）。这是"部分更新"的关键：用户只改昵称，你不能把 phone 也清空。
   - `setattr(user, field, value)`：把新值写回 ORM 对象的属性（ORM 对象变化 = 对应 SQL UPDATE）。
   - 前面 if 排除 None：传了 null 想清空字段？这个实现选择是"null 不更新"（保守）。

7. **改密码（change_password）**
   - 先验证旧密码（防止别人改你密码），再哈希新密码写入。**改密码 = 业务动作，必须校验身份凭证（旧密码）**。

### 6.2 crud/news.py —— 新闻业务（🔴）

```python
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category, News
from models.related_news import RelatedNews


async def get_categories(db, skip: int = 0, limit: int = 100) -> list[Category]:
    stmt = select(Category).order_by(Category.sort_order.asc(), Category.id.asc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_news_list(db, category_id: Optional[int], skip: int = 0, limit: int = 10) -> list[News]:
    stmt = select(News)
    if category_id is not None:
        stmt = stmt.where(News.category_id == category_id)
    stmt = stmt.order_by(News.publish_time.desc(), News.id.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_news_count(db, category_id: Optional[int]) -> int:
    stmt = select(func.count(News.id))
    if category_id is not None:
        stmt = stmt.where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_news_detail(db, news_id: int) -> Optional[News]:
    return await db.get(News, news_id)


async def increase_news_views(db, news_id: int) -> bool:
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_related_news(db, news_id: int, category_id: int, limit: int = 5) -> list[News]:
    # 1. related_news 静态关联表（课程推荐系统方案）
    stmt = (
        select(News)
        .join(RelatedNews, RelatedNews.related_news_id == News.id)
        .where(RelatedNews.news_id == news_id)
        .order_by(News.views.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    related = list(result.scalars().all())
    if related:
        return related

    # 2. 回退方案：同分类下按浏览量和发布时间排序
    stmt = (
        select(News)
        .where(News.category_id == category_id, News.id != news_id)
        .order_by(News.views.desc(), News.publish_time.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
```

**逐段讲解：**

1. **条件拼装**：`get_news_list` 里 `if category_id is not None: stmt = stmt.where(...)`——**动态条件查询**。分类筛选是可选的（不传返回全部），通过"逐步给 stmt 加条件"实现。这是写查询的通用模式。

2. **排序稳定性**：`ORDER BY publish_time DESC, id DESC`——发布时间相同就按 id 倒序。**加第二个排序字段保证结果顺序唯一**，否则同一页数据翻页时会"跳"。

3. **分页（skip/offset + limit）**：`offset(skip).limit(limit)` 跳过 N 条取 M 条。路由层把"页码"换算成"偏移量"（见 8.3）。

4. **`func.count`**：SQL 的 COUNT(*) 聚合。**列表接口要返回 total**（总条数），前端才能算"共几页"。

5. **浏览量 +1（increase_news_views）**：
   ```python
   update(News).where(News.id == news_id).values(views=News.views + 1)
   ```
   - **重点：在数据库里做 `views = views + 1`，而不是先查出来加 1 再写回**。
   - 为什么？并发安全！两个人同时访问，如果"查→加→写"两步，可能都读到 100，写回都是 101（丢一次）。`UPDATE ... SET views = views + 1` 是**原子操作**，数据库内部保证不丢。🔴 这是并发编程的核心考点。

6. **相关推荐的两级策略**：
   - 优先用 `related_news` 表（人工/算法预置的关联，质量高）。
   - 表里没有 → 回退"同分类按热度"（`views DESC, publish_time DESC`）。
   - **这就是"多方案 + 降级回退"的工程思维**：主方案失效时自动走备用方案，而不是报错。

### 6.3 crud/news_cache.py —— 缓存策略（🟡 理解"Cache-Aside"模式）

```python
from fastapi.encoders import jsonable_encoder
from crud import news as news_crud
from schemas.news import NewsDetailResponse, NewsItemBase

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list:"
NEWS_DETAIL_PREFIX = "news:detail:"
RELATED_NEWS_PREFIX = "news:related:"


async def get_categories(db, skip: int = 0, limit: int = 100):
    cached = await get_json_cache(CATEGORIES_KEY)
    if cached:
        return cached
    categories = await news_crud.get_categories(db, skip, limit)
    if categories:
        await set_cache(CATEGORIES_KEY, jsonable_encoder(categories), EXPIRE_CATEGORIES)
    return categories


async def get_news_list(db, category_id: Optional[int], skip: int = 0, limit: int = 10):
    page = skip // limit + 1
    key = _news_list_key(category_id, page, limit)
    cached = await get_json_cache(key)
    if cached:
        return [News(**item) for item in cached]
    news_list = await news_crud.get_news_list(db, category_id, skip, limit)
    if news_list:
        data = [NewsItemBase.model_validate(n).model_dump(mode="json", by_alias=False) for n in news_list]
        await set_cache(key, data, EXPIRE_NEWS_LIST)
    return news_list


def _news_list_key(category_id: Optional[int], page: int, size: int) -> str:
    category_part = category_id if category_id is not None else "all"
    return f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"


async def invalidate_news_list_cache(category_id: Optional[int] = None):
    if category_id is not None:
        await delete_cache_by_pattern(f"{NEWS_LIST_PREFIX}{category_id}:*")
    else:
        await delete_cache_by_pattern(f"{NEWS_LIST_PREFIX}*")


async def get_news_detail(db, news_id: int):
    cached = await get_json_cache(f"{NEWS_DETAIL_PREFIX}{news_id}")
    if cached:
        return News(**cached)
    news = await news_crud.get_news_detail(db, news_id)
    if news:
        detail_data = NewsDetailResponse.model_validate(news).model_dump(mode="json", by_alias=False)
        await set_cache(f"{NEWS_DETAIL_PREFIX}{news_id}", detail_data, EXPIRE_NEWS_DETAIL)
    return news


async def invalidate_news_detail_cache(news_id: int):
    from config.cache_conf import delete_cache
    await delete_cache(f"{NEWS_DETAIL_PREFIX}{news_id}")


async def get_related_news(db, news_id: int, category_id: int, limit: int = 5):
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    cached = await get_json_cache(key)
    if cached:
        return cached
    related = await news_crud.get_related_news(db, news_id, category_id, limit)
    data = [NewsItemBase.model_validate(n).model_dump(mode="json", by_alias=False) for n in related]
    await set_cache(key, data, EXPIRE_RELATED_NEWS)
    return data
```

**这段代码体现的模式叫 Cache-Aside（旁路缓存），是缓存系统的核心范式（🟡 必须理解流程）：**

```
读：查缓存 → 命中？直接返回 → 没命中？查数据库 → 写回缓存 → 返回
写：改数据库 → 删缓存（下次读时重建）
```

1. **key 的设计**：`news_list:1:1:10`（分类1·第1页·每页10条）。**缓存 key 必须能唯一定位一份数据**——分页参数一变，key 就变。这就是为什么"列表"缓存按 (category, page, size) 做 key。

2. **为什么缓存的是 dict 而不是 ORM 对象？** Redis 只能存字符串/JSON。所以流程是 `ORM → Pydantic(model_validate) → dict(model_dump) → JSON → Redis`。`by_alias=False` 保证字段名是 Python 风格（如 `has_more` 而不是 `hasMore`）。

3. **读缓存后还原**：`News(**item)` 用字典直接构造 ORM 对象——**缓存里存的是 News 的全部字段**才能还原（注释特意提醒了这一点）。

4. **失效策略（写时删缓存）**：数据变了，删除对应 key（或按前缀批量删）。下次读取时"查库→重建缓存"。**为什么删而不是更新缓存？** 简单、不会产生"缓存里是旧结构"的问题；更新缓存反而要处理并发写一致性。

5. **缓存一致性（面试必问）**：这里用的是"**先更新数据库，再删缓存**"（Cache-Aside 标准做法）。极端并发下可能有短暂不一致，但 demo 场景可接受；真要强一致，用"延迟双删"或消息队列，那是进阶话题。

### 6.4 crud/favorite.py、history.py、ai.py（🟡）

```python
# favorite.py（收藏）
async def get_favorite(db, user_id, news_id):          # 查单条收藏
    stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def add_favorite(db, user_id, news_id):          # 添加收藏
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.flush()
    await db.refresh(favorite)
    return favorite

async def remove_favorite(db, user_id, news_id) -> bool:
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0                         # 删了几行？0=没删到

async def get_favorite_list(db, user_id, skip=0, limit=20):
    stmt = (
        select(Favorite, News)
        .join(News, News.id == Favorite.news_id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.id.desc())
        .offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.all()   # list[(Favorite, News)]
```

**要点：**

1. **`rowcount > 0` 判断"到底删没删到"**——这是"幂等删除"的写法：删不到就返回 False，路由层据此返回"未收藏"错误。**用返回值传递业务结果**是 crud 层的惯例。

2. **`select(Favorite, News).join(...)` 一次查两张表**：收藏列表要带新闻信息（标题/封面），用 join 一条 SQL 搞定，比"查收藏再逐个查新闻"（N+1 问题）高效。
   - 🔴 **N+1 问题**：循环里逐个查库 = 慢的根源。解决：join 一次性取回。面试高频。

3. **`order_by(Favorite.id.desc())`**：按收藏时间倒序（id 自增 ≈ 时间顺序）。

```python
# history.py —— 结构几乎同 favorite，多了两个函数
async def get_history_by_id(db, history_id):     # 按 id 查单条（用于"删单条"）
    return await db.get(History, history_id)

async def delete_history(db, history):
    await db.delete(history)                      # ORM 级删除：传对象
    await db.commit()
```

```python
# ai.py —— AI 记录
async def save_chat_record(db, user_id, message, response):
    record = AiChat(user_id=user_id, message=message, response=response)
    db.add(record)
    await db.commit()
    return record

async def get_chat_history(db, user_id, limit=20):
    stmt = (select(AiChat).where(AiChat.user_id == user_id)
            .order_by(AiChat.created_at.desc()).limit(limit))
    result = await db.execute(stmt)
    return list(result.scalars().all())
```

> 🟡 读到这里你会发现：**crud 函数的长相高度重复**（查、增、删、列表）。这很正常——它们就是"表的翻译器"。重点掌握的是：`select/join/where/order_by/offset/limit/rowcount` 这几个词，以及"join 防 N+1"和"返回值传递业务结果"两个思想。

---

## 7. 工具层 utils/ —— 公共能力

### 7.1 utils/response.py —— 统一响应（🔴）

```python
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(message: str = "success", data=None):
    content = {
        "code": 200,
        "message": message,
        "data": data,
    }
    return JSONResponse(content=jsonable_encoder(content))
```

**为什么所有接口都返回 `{code, message, data}` 三件套？**

- **前后端契约**：前端写一套解析逻辑就能处理所有接口（先看 code 判断成败，message 给用户提示，data 取数据）。如果没有统一格式，每个接口字段都不一样，前端要写 N 套解析。
- **`jsonable_encoder`**：把 datetime、ORM 对象、UUID 等非 JSON 原生类型转成可序列化的东西。**没有它，直接 `JSONResponse(content=xxx)` 遇到 datetime 会报错**。
- 所有"成功"的接口都用它；所有"失败"的由全局异常处理器统一格式化（7.4）——**成功失败两条路径都走统一格式**。

### 7.2 utils/security.py —— bcrypt 密码加密（🟡 原理要懂，实现用库）

```python
import bcrypt


def get_hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False
```

**为什么密码要用 bcrypt？（🔴 安全意识）**

- **明文存储的灾难**：数据库一旦泄露，所有用户密码裸奔。真实案例无数（CSDN 600 万明文密码泄露等）。
- **哈希不是加密**：SHA256/MD5 这类"快速哈希"也不行——GPU 每秒能算几十亿次，跑字典攻击很容易。这就是为什么 `utils/security.py` 的注释强调"安全地存储密码"。
- **bcrypt 的特点**：
  1. **加盐（salt）**：`gensalt()` 每次生成随机盐混进哈希。同样的密码，每次哈希结果不同——**防彩虹表**。
  2. **慢**：故意设计得计算慢（约 0.1 秒），让暴力破解成本天文数字。**慢 = 安全**，这正是它和 MD5 的本质区别。
- `verify_password` 里 `encode("utf-8")`：bcrypt 只接受字节串，不接受 str，必须编码。

> 面试常问：什么是加盐？为什么 bcrypt 比 SHA256 更适合存密码？答案都在上面。

### 7.3 utils/auth.py —— Token 认证（🔴🔴 全项目最重要的安全机制）

```python
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import users
from models.users import User


async def get_current_user(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")

    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")

    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的令牌或已经过期的令牌")
    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        return None
    return await users.get_user_by_token(db, token)
```

**这段代码是全项目的"门卫"，必须吃透：**

1. **`Header(alias="Authorization")`**：从 HTTP 请求头取 `Authorization` 字段。前端发请求时带 `Authorization: Bearer <token>`。
   - 为什么叫 Bearer？这是 HTTP 认证的规范格式（RFC 6750），`Bearer` 意思是"持有者令牌"——谁持有这个 token 谁就是本人。

2. **这是一个"依赖（Depends）"而不是普通函数**
   - 路由声明 `user: User = Depends(get_current_user)`，FastAPI 就会**先执行 get_current_user**，拿到 user 才进入路由函数。
   - **认证逻辑零侵入**：想保护哪个接口，加一个参数就行；不想要的接口不加。这就是"依赖注入"的威力——**横切关注点（认证、日志、权限）以声明方式注入**。🔴 面试常问"依赖注入是什么"，这就是活例子。

3. **三个失败分支都返回 401**：
   - 没带 token / 格式不对 → 401
   - token 查不到用户（无效或过期）→ 401
   - 为什么不细分"token 过期"和"token 无效"？**安全考虑**：不告诉攻击者太多信息。
   - 401 vs 403：401 = 未认证（你是谁？）；403 = 已认证但没权限（你不能干这个）。demo 里只用了 401。

4. **`get_current_user_optional`**：不强制登录的"可选认证"——有 token 就返回用户，没有就返回 None。用于"登录用户功能增强、未登录也不拦"的场景（AI 问答记录归属）。

> 🔴 你要能独立画出这个流程：前端带 token → 请求到达路由 → FastAPI 注入执行 get_current_user → 查 user_token 表 → 校验过期 → 返回 user → 路由里用 user.id 干活。

### 7.4 utils/exception.py 与 exception_handlers.py —— 全局异常（🟡 设计思想重要）

```python
# exception.py
class BusinessException(Exception):
    """业务异常：在路由层抛出，由全局异常处理器统一转换为响应。"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
```

```python
# exception_handlers.py
from fastapi import Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from utils.exception import BusinessException


def register_exception_handlers(app):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": str(exc.detail), "data": None},
        )

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return JSONResponse(
            status_code=exc.code,
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        first = errors[0] if errors else {}
        loc = ".".join(str(x) for x in first.get("loc", []) if x != "body")
        message = f"参数校验失败：{loc} {first.get('msg', '')}".strip()
        return JSONResponse(
            status_code=422,
            content={"code": 422, "message": message, "data": errors},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "服务器内部错误，请稍后再试", "data": None},
        )
```

**设计思想（这是"工程健壮性"的核心）：**

1. **问题：FastAPI 默认的错误响应格式**（如 `{"detail": "..."}`）和我们的统一格式 `{code, message, data}` 不一致。前端要解析两种格式，很痛苦。
2. **方案：全局异常处理器**——不管哪里抛异常，都由这里"接住"并**翻译成统一格式**：
   - `HTTPException`（FastAPI 内置，路由里 `raise HTTPException(404, "新闻不存在")`）→ 统一格式。
   - `RequestValidationError`（Pydantic 校验失败自动抛）→ 422 + 提取第一条错误信息（前端好提示用户）。
   - `BusinessException`（自定义业务异常）→ 按 code 返回。
   - `Exception`（**兜底**）→ 500，**绝不把内部错误详情泄露给前端**（防信息泄露，也防攻击者探测）。
3. **路由层从此可以放心抛异常**，不用每个接口写 try/except 处理错误——错误处理集中在一处。这就是"**集中式异常处理**"。
4. 为什么要自定义 `BusinessException`？FastAPI 的 HTTPException 只能带 detail 文本；业务异常想带自己的 code/message，自定义类更灵活。

> 🟡 你可以让 AI 帮你写异常处理器，但"为什么需要统一异常处理"这个思想必须懂——它是大型项目的基础设施。

---

## 8. 路由层 routers/ —— 定义"有什么接口"

**FastAPI 路由的核心语法（🔴 必须滚瓜烂熟）：**

```python
router = APIRouter(prefix="/api/news", tags=["新闻模块"])

@router.get("/list", summary="获取新闻列表")
async def get_news_list(category_id: int, db=Depends(get_db)):
    ...
```

- `APIRouter`：把一组接口打包。`prefix="/api/news"` 统一加前缀（所有接口都带 `/api/news`），`tags` 用来在 /docs 里分组展示。
- `@router.get/post/put/delete("/路径")`：HTTP 方法与路径。
- `summary`：显示在接口文档里的说明。
- 路径参数 vs 查询参数 vs 请求体：
  - `GET /list?categoryId=1` → 查询参数（Query）
  - `GET /delete/{id}` → 路径参数
  - `POST /add` + JSON body → 请求体（body 参数）
- `db=Depends(get_db)`：依赖注入数据库会话。

### 8.1 routers/users.py —— 用户接口（🔴 认证接口怎么写）

```python
from fastapi import APIRouter, Depends, HTTPException

from config.db_conf import get_db
from crud import users as users_crud
from models.users import User
from schemas.users import (
    UserAuthResponse, UserChangePassword, UserCreate,
    UserInfoResponse, UserUpdate,
)
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["用户模块"])


@router.post("/register", summary="用户注册")
async def register(user_data: UserCreate, db=Depends(get_db)):
    # 校验用户名、邮箱是否已存在
    if await users_crud.get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if await users_crud.get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = await users_crud.create_user(db, user_data)
    token = await users_crud.create_token(db, user.id)

    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


@router.post("/login", summary="用户登录")
async def login(user_data: UserCreate, db=Depends(get_db)):
    user = await users_crud.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = await users_crud.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)


@router.get("/info", summary="获取当前用户信息")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/update", summary="修改用户信息")
async def update_user_info(user_data: UserUpdate, user: User = Depends(get_current_user), db=Depends(get_db)):
    user = await users_crud.update_user(db, user, user_data)
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/password", summary="修改用户密码")
async def update_password(password_data: UserChangePassword, user: User = Depends(get_current_user), db=Depends(get_db)):
    ok = await users_crud.change_password(db, user, password_data.old_password, password_data.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="原密码错误")
    return success_response(message="修改密码成功")
```

**逐接口讲解（对照着看，你会看到统一的分层套路）：**

1. **注册接口的三步**：查重（用户名/邮箱）→ 建用户 → 发 token。**查重为什么用两个 if？** 数据库唯一索引是兜底，应用层先查是为了给用户友好的中文提示（"用户名已存在"而不是 500 报错）。**分层防御**：应用层提示友好，数据库层保证绝对正确。

2. **登录接口**：`authenticate_user` 失败 → 401"用户名或密码错误"。注意这里**不区分"用户不存在"还是"密码错误"**——防枚举攻击（攻击者逐个试用户名是否存在）。这是安全最佳实践。

3. **`GET /info` 没有 db 参数**——因为根本不需要操作数据库！user 已经在 get_current_user 里查出来了。**依赖注入帮我们省掉了一次重复查询**。

4. **每个接口的响应都走 `success_response` + Pydantic 序列化**：`UserInfoResponse.model_validate(user)` 把 ORM 对象转成"对外可见"的结构（自动剔除 password 等敏感字段）。

5. **观察"路由层 = 薄薄一层"**：接收参数 → 调 crud → 组装响应。没有复杂逻辑。**逻辑都在 crud 和 schema 里**。这就是分层后的样子。

### 8.2 routers/news.py —— 新闻接口（🔴 分页与查询参数）

```python
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from config.db_conf import get_db
from crud import news as news_crud
from crud import news_cache
from schemas.news import NewsDetailResponse, NewsItemBase

router = APIRouter(prefix="/api/news", tags=["新闻模块"])


@router.get("/categories", summary="获取新闻分类")
async def get_categories(skip: int = 0, limit: int = Query(100, le=200), db=Depends(get_db)):
    categories = await news_cache.get_categories(db, skip, limit)
    return {"code": 200, "message": "获取新闻分类成功", "data": categories}


@router.get("/list", summary="获取新闻列表（支持分类筛选与分页）")
async def get_news_list(
    category_id: Optional[int] = Query(default=None, alias="categoryId", description="分类ID，不传则返回全部"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize", description="每页数量"),
    db=Depends(get_db),
):
    offset = (page - 1) * page_size
    news_list = await news_cache.get_news_list(db, category_id, offset, page_size)
    total = await news_crud.get_news_count(db, category_id)

    data = {
        "list": [NewsItemBase.model_validate(n) for n in news_list],
        "total": total,
        "hasMore": (offset + len(news_list)) < total,
    }
    return {"code": 200, "message": "获取新闻列表成功", "data": data}


@router.get("/detail", summary="获取新闻详情（浏览量+1，返回相关推荐）")
async def get_news_detail(news_id: int = Query(..., alias="id"), db=Depends(get_db)):
    news = await news_cache.get_news_detail(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")

    await news_crud.increase_news_views(db, news.id)
    await news_cache.invalidate_news_detail_cache(news.id)

    related_news = await news_cache.get_related_news(db, news.id, news.category_id)
    news_detail = NewsDetailResponse.model_validate(news)

    data = news_detail.model_dump(mode="json")
    data["relatedNews"] = related_news
    return {"code": 200, "message": "获取新闻详情成功", "data": data}
```

**逐段讲解：**

1. **`Query(alias="categoryId")` 是什么？**
   - 前端传参名是 `categoryId`（驼峰，前端习惯），Python 变量名是 `category_id`（下划线，Python 习惯）。`alias` 就是**对外参数名与内部变量名的桥梁**。
   - 同理 `pageSize` → `page_size`。这是前后端命名风格不一致的标准解法。

2. **Query 的校验参数**：`ge=1` 页码至少 1；`le=100` 每页最多 100；`Query(...)` 三个点 = **必填**（detail 的 id）。
   - **参数边界在这里声明**，不用在函数里写 if 判断。又是"声明式校验"。

3. **分页换算：`offset = (page - 1) * page_size`**
   - 用户说"第 2 页、每页 10 条"→ 数据库说"跳过 10 条取 10 条"。
   - `hasMore = (offset + len(news_list)) < total`：当前已取到 offset+len 条，还没到 total 就是还有下一页。**这个布尔值前端直接用来判断"加载更多"按钮显不显示**。

4. **为什么 categories/list 走缓存层（news_cache），detail 混合用？**
   - 读多写少的 → 缓存（list/categories）。
   - detail 每次要"浏览量+1"（写操作）→ 先读缓存拿数据，再写库 +1，再删缓存（下次重新缓存新浏览量）。
   - **读写策略因业务而异**，这是缓存设计的实战感。

5. **`data["relatedNews"] = related_news`**：Pydantic 序列化后再手动挂一个额外字段。如果字段多，应该把 relatedNews 也加进 schema；这里只有一处，手动加更简单。**工程上叫"按需扩展响应"**。

### 8.3 routers/favorite.py 与 history.py —— 用户行为接口（🟡 套路完全一致）

```python
# favorite.py（收藏）
router = APIRouter(prefix="/api/favorite", tags=["收藏模块"])


@router.get("/check", summary="检查新闻收藏状态")
async def check_favorite(news_id: int = Query(..., alias="newsId"),
                         user: User = Depends(get_current_user), db=Depends(get_db)):
    favorite = await favorite_crud.get_favorite(db, user.id, news_id)
    return success_response(message="查询成功", data={"isFavorite": favorite is not None})


@router.post("/add", summary="添加收藏")
async def add_favorite(body: FavoriteAddRequest,
                       user: User = Depends(get_current_user), db=Depends(get_db)):
    news = await news_crud.get_news_detail(db, body.news_id)
    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")
    if await favorite_crud.get_favorite(db, user.id, body.news_id):
        raise HTTPException(status_code=400, detail="该新闻已在收藏中")
    await favorite_crud.add_favorite(db, user.id, body.news_id)
    return success_response(message="收藏成功")


@router.delete("/remove", summary="取消收藏")
async def remove_favorite(news_id: int = Query(..., alias="newsId"),
                          user: User = Depends(get_current_user), db=Depends(get_db)):
    ok = await favorite_crud.remove_favorite(db, user.id, news_id)
    if not ok:
        raise HTTPException(status_code=400, detail="该新闻未收藏")
    return success_response(message="取消收藏成功")


@router.get("/list", summary="获取收藏列表")
async def get_favorite_list(page: int = Query(1, ge=1),
                            page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
                            user: User = Depends(get_current_user), db=Depends(get_db)):
    offset = (page - 1) * page_size
    rows = await favorite_crud.get_favorite_list(db, user.id, offset, page_size)
    total = await favorite_crud.get_favorite_count(db, user.id)
    data = {
        "list": [FavoriteResponse(id=fav.id, news=NewsItemBase.model_validate(news)) for fav, news in rows],
        "total": total,
        "hasMore": (offset + len(rows)) < total,
    }
    return success_response(message="获取收藏列表成功", data=data)


@router.delete("/clear", summary="清空收藏")
async def clear_favorites(user: User = Depends(get_current_user), db=Depends(get_db)):
    await favorite_crud.clear_favorites(db, user.id)
    return success_response(message="清空收藏成功")
```

**这个文件里藏着一个必须掌握的模式：`user: User = Depends(get_current_user)`**

- 每个需要登录的接口都带这个参数 → FastAPI 自动认证 → 拿到 `user` → 用 `user.id` 做数据归属。
- **这是"接口级权限控制"的标准写法**：收藏/历史都是"我的数据"，一律用 `user.id` 过滤——**你永远只能操作自己的收藏**。数据归属检查放在查询条件里，天然防越权。🔴 面试必问"如何防止水平越权"：答案就是这个。

**错误状态码的选择（🟡 体会一下）：**

- 收藏不存在的新闻 → **404**（资源不存在）
- 重复收藏 → **400**（业务冲突）
- 取消一个没收藏的 → **400**
- 没登录访问 → **401**（get_current_user 抛的）
- **状态码 = 语义**：404 资源、400 业务规则、401 认证、403 权限。选对状态码是 API 设计的基本功。

```python
# history.py —— 几乎同款，只多一个"删除单条"
@router.delete("/delete/{history_id}", summary="删除单条浏览历史")
async def delete_history(history_id: int, user: User = Depends(get_current_user), db=Depends(get_db)):
    history = await history_crud.get_history_by_id(db, history_id)
    if not history or history.user_id != user.id:
        raise HTTPException(status_code=404, detail="记录不存在")
    await history_crud.delete_history(db, history)
    return success_response(message="删除成功")
```

- **这里用了路径参数 `/{history_id}`**：DELETE /api/history/delete/3。
- **`history.user_id != user.id` 的越权检查**：别人不能删你的历史——即使用户传了别人的记录 id，也返回 404（**故意装不存在**，不透露"这条记录存在但属于别人"）。

### 8.4 routers/ai.py —— AI 问答接口（🟡）

```python
"""AI 问答模块：调用阿里云百炼（DashScope）兼容模式的通义千问大模型。"""
import os
from typing import Optional

import httpx

from fastapi import APIRouter, Depends

from config.db_conf import get_db
from crud import ai as ai_crud
from models.users import User
from schemas.ai import ChatHistoryItem, ChatRequest
from utils.auth import get_current_user, get_current_user_optional
from utils.response import success_response

router = APIRouter(prefix="/api/ai", tags=["AI问答"])

AI_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "qwen-plus")


@router.post("/chat", summary="AI 问答（通义千问）")
async def chat(body: ChatRequest,
               user: Optional[User] = Depends(get_current_user_optional),
               db=Depends(get_db)):
    if not AI_API_KEY:
        return success_response(message="AI 问答未启用",
            data={"answer": "AI 问答功能需要配置大模型 API Key：请在环境变量 AI_API_KEY 中设置..."})

    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": body.question}],
        "stream": False,
    }
    headers = {"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(AI_ENDPOINT, json=payload, headers=headers)
            resp.raise_for_status()
            answer = resp.json()["choices"][0]["message"]["content"]
            await ai_crud.save_chat_record(db, user.id if user else None, body.question, answer)
            return success_response(message="AI 回答成功", data={"answer": answer})
    except httpx.HTTPStatusError as e:
        return success_response(message="AI 服务调用失败",
            data={"answer": f"大模型接口返回错误（HTTP {e.response.status_code}），请检查 API Key 是否有效。"})
    except Exception as e:
        return success_response(message="AI 服务调用失败",
            data={"answer": f"调用大模型时发生错误：{e}"})


@router.get("/history", summary="AI 问答历史（需登录）")
async def chat_history(limit: int = 20,
                       user: User = Depends(get_current_user),
                       db=Depends(get_db)):
    records = await ai_crud.get_chat_history(db, user.id, limit=min(limit, 100))
    data = [ChatHistoryItem.model_validate(r) for r in records]
    return success_response(message="获取问答历史成功", data=data)
```

**要点：**

1. **`os.getenv("AI_API_KEY", "")`**：从环境变量读配置——**密钥绝不写死在代码里**（否则 git 一提交就泄密了）。这是 12 要素原则（配置进环境）。
2. **调大模型 = 一次普通 HTTP POST**：`httpx.AsyncClient` 异步发请求，`timeout=60`（大模型慢，要给足超时）。
3. **`get_current_user_optional`**：AI 问答不强制登录（体验好），但登录了就把记录归属到你名下。**可选认证**的典型场景。
4. **错误降级**：API Key 没配 → 返回"未启用"提示；调用失败 → 返回友好错误。**外部服务（大模型）挂了，业务不能挂**——和 Redis 降级同一个思想。
5. **AI 问答的协议是 OpenAI 兼容格式**：`{"model": ..., "messages": [{"role","content"}]}`。会了这个，接任何大模型（通义、DeepSeek、GLM、GPT）都一样。

---

## 9. 入口 main.py —— 组装一切（🔴）

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.db_conf import async_engine
from models import Base
from routers import ai, favorite, history, news, users
from utils.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="FastAPI Demo · AI掘金头条",
    description="基于 FastAPI + SQLAlchemy 异步 ORM 的新闻系统 Demo：用户认证、新闻浏览、收藏、浏览历史、Redis 缓存、AI 问答。",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(news.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai.router)


@app.get("/", summary="服务健康检查")
async def root():
    return {"message": "FastAPI Demo is running", "docs": "/docs"}
```

**逐段讲解：**

1. **`lifespan`（应用生命周期）**：启动时执行（建表），关闭时执行清理（yield 后面的代码）。
   - `Base.metadata.create_all`：**根据所有模型自动建表**（表不存在才建，已存在不动）。
   - 🔴 注意：这是 demo 做法，**生产环境要用迁移工具 Alembic**（改表结构时能平滑升级、不丢数据）。文档末尾"进阶方向"会讲。

2. **`register_exception_handlers(app)`**：把 7.4 的全局异常处理器挂到 app 上——**一条语句启用全局错误处理**。

3. **CORS（跨域）**：
   - 为什么需要？前端（比如 Vue 跑在 `localhost:5173`）和后端（`localhost:8000`）**不同端口 = 不同源**，浏览器默认禁止跨源请求。CORS 中间件告诉浏览器"允许来自哪里的请求"。
   - `allow_origins=["*"]`：允许所有来源。**开发方便，生产必须改成具体域名**（否则任何人网页都能调你的接口，容易被滥用）。
   - 🔴 面试常问"什么是跨域、怎么解决"：答案就是 CORS 中间件 + 白名单。

4. **`app.include_router(...)`**：把各模块路由"装"进应用。**每加一个新功能模块，main.py 加一行**。

5. **`/` 健康检查接口**：运维/监控用来探测"服务活着吗"。简单但必不可少。

---

## 10. 脚本与测试 scripts/ + test_main.http

### 10.1 scripts/init_db.py —— 初始化示例数据（🟢）

```python
"""初始化脚本：建表并写入示例数据（分类 + 新闻）。"""
import asyncio
import os
import sys

# 保证脚本无论从哪里运行都能导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func, select

from config.db_conf import async_engine, AsyncSessionLocal
from models import Base, Category, News

CATEGORIES = [...]
NEWS_TEMPLATE = [...]   # (分类名, 标题, 简介, 内容, 作者, 浏览量)


async def init_data():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count(Category.id)))
        if result.scalar_one() > 0:
            print("分类表已有数据，跳过示例数据写入。")
            return   # 幂等：已有数据就不重复写

        # 写入分类 → flush 拿 id → 写新闻（通过分类名映射 id）
        ...
```

**三个知识点（看懂即可）：**

1. **`sys.path.insert(0, ...)` 是干什么的？** 直接 `python scripts/init_db.py` 运行时，Python 的模块搜索路径是 `scripts/` 目录，找不到 `config`、`models` 这些**项目根目录的包**。这行把项目根目录加进搜索路径——**脚本能 import 项目代码的关键**。新写脚本时直接抄这行。
2. **幂等（idempotent）**：`if 分类已有数据: return`——重复执行不会写重复数据。**所有初始化脚本都应该幂等**，否则误执行一次就把数据搞坏了。
3. **为什么要"先 flush 分类拿 id，再写新闻"？** 新闻需要分类 id 外键，所以先把分类插进去拿到自增 id，再通过 `category_map = {c.name: c.id}` 把新闻的 category_id 填上。

### 10.2 scripts/import_course_data.py —— 导入课程真实数据（🟢）

```python
"""导入课程项目的真实数据（database.sql）到本地 SQLite 数据库。"""
import re
import csv
import io

CITE_PATTERN = re.compile(r":cite\[\d+\]")   # 清理从网页复制带入的 :cite[1] 标记

def parse_row(line: str):
    """解析一行元组：('a', 'b', 1, 'c,d'), —— 用 csv 模块处理引号与逗号。"""
    ...

def extract_inserts(sql_text: str):
    """提取 INSERT INTO 块，返回 {表名: [(列名, 行列表), ...]}。
    注意：同一张表可能有多个 INSERT 块且列顺序不同，必须按块分别保存列名。
    """
    ...

async def import_data(sql_path: str):
    # 解析 → 清空新闻相关表 → 写分类 → 写新闻 → 校验数量
    ...
```

**这个脚本是"数据搬运"的实用范例**，核心技巧：

1. **解析 MySQL 的 SQL 文件**：用正则抓 `INSERT INTO` 块，用 `csv.reader(quotechar="'")` 解析每行元组（能正确处理字符串里的逗号和引号）。
2. **踩过的坑**（真实教训）：同一个表有多个 INSERT 块且**列顺序不同**，如果只用一个列名列表去解析，数据会错位。修复：按块独立保存列名。→ 提醒你：**解析异构数据时，永远先检查"每一块的格式是否一致"**。
3. 清空相关表再写入：`delete(Favorite)` → `delete(History)` → `delete(News)` → `delete(Category)`。注意顺序——先删有外键的子表，再删父表，否则外键约束会报错。**删数据也讲究顺序**。
4. 这脚本是"把课程数据搬进 demo"的一次性工具，不是核心能力。理解思路即可，**写这类脚本直接让 AI 干**。

### 10.3 scripts/migrate_db.py —— 表结构迁移（🟡）

```python
"""数据库迁移脚本：把 demo 表结构对齐课程 database.sql（幂等，可重复执行）。"""

async def column_exists(conn, table: str, column: str) -> bool:
    result = await conn.execute(text(f"PRAGMA table_info({table})"))
    cols = [row[1] for row in result.fetchall()]
    return column in cols

async def migrate():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)   # 建新表（related_news / ai_chat）

    async with async_engine.begin() as conn:
        if not await column_exists(conn, "user", "gender"):
            await conn.execute(text("ALTER TABLE user ADD COLUMN gender VARCHAR(10) NOT NULL DEFAULT 'unknown'"))
        ...
```

**这里展示了"给已有数据库加列"的正确姿势（🟡 要懂原理）：**

1. **`Base.metadata.create_all` 只建"新表"**——已有表加了新列，它不会自动加（这是 create_all 的局限，也是需要迁移脚本的原因）。
2. **`ALTER TABLE ... ADD COLUMN`**：SQLite 加列。`PRAGMA table_info(user)` 查表结构 → 判断列是否存在 → 不存在才加。**幂等迁移**：每次都检查，不会重复加列报错。
3. **真实生产会用 Alembic**（自动生成迁移脚本、支持回滚），demo 手写是为了教学简单。理解"为什么需要迁移"比记住命令更重要。

### 10.4 scripts/smoke_test_api.ps1 —— 接口冒烟测试（🟢）

```powershell
$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:8000"
$pass = 0; $fail = 0

function Check([string]$name, [bool]$ok) {
    if ($ok) { $script:pass++; Write-Host "  [OK] $name" }
    else { $script:fail++; Write-Host "  [FAIL] $name" }
}

# 注册（用户已存在则登录，保证幂等可重复跑）
try {
    $r = Invoke-RestMethod -Uri "$base/api/user/register" -Method Post -ContentType "application/json" -Body '{"username":"demo_user",...}'
    $token = $r.data.token
} catch {
    $r = Invoke-RestMethod -Uri "$base/api/user/login" ...
}
...
Write-Host "RESULT: $pass passed, $fail failed"
```

**为什么要有冒烟测试？（🟡 思想重要）**

- 改完代码（比如今天对齐课程表结构），怎么知道**没把旧功能改坏**？一个个接口手动试太慢。
- 冒烟测试 = 把"核心流程的关键检查"写成脚本，一键跑完，输出 OK/FAIL。
- 它测的是**真实 HTTP 层**（启动服务 → 发请求 → 验响应），比单元测试更接近用户视角。
- 注意：**冒烟测试不是正式测试**。真正的项目会用 pytest + TestClient 写自动化单测/集成测（见进阶方向）。

> 🟢 这个脚本你只要会"启动服务后运行它、看 OK/FAIL"就够了。让 AI 帮你扩充测试用例。

### 10.5 test_main.http（🟢）

```http
### 用户注册
POST http://127.0.0.1:8000/api/user/register
Content-Type: application/json

{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secret123"
}

### 获取当前用户信息（需认证）
GET http://127.0.0.1:8000/api/user/info
Authorization: Bearer {{token}}
```

- VS Code 安装 REST Client 插件后，这个文件里每个 `###` 之间的请求块都可以**一键发送**，免去 Postman。
- `{{token}}` 是变量：先跑登录请求拿到 token，在设置里替换。
- 它的价值：**把"手动测试清单"存进代码库**——新人接手项目，打开这个文件就知道有哪些接口、怎么调。

### 10.6 .gitignore（🟢）

```text
.venv/
venv/
__pycache__/
*.pyc
.vscode/
*.db
*.bak
*.log
.idea/
```

- 告诉 Git"这些文件不提交"：虚拟环境（几百 MB）、缓存、数据库、日志、IDE 配置。
- **`*.db` 不提交数据库文件**：数据是运行时生成的，不该进代码库（也避免把测试数据泄露出去）。
- `*.bak` 是备份文件（比如旧库备份 app.db.bak）。**提交代码前先想清楚：这个文件是"代码"还是"运行时产物"？**

### 10.7 其他小文件（🟢）

**各目录的 `__init__.py`（除了 models 的）都是空文件**——它们的作用只有一个：**让该目录成为 Python 包**。没有这些文件，`from config import db_conf` 这类导入会失败（Python 3.3+ 的隐式命名空间包虽可部分替代，但显式 `__init__.py` 仍是惯例）。给 `__init__.py` 写导出内容（像 models 那样）则是"包门面"的进阶用法。

**scripts/list_news.py —— 查看数据库里新闻数据的小工具**

```python
"""查询数据库中的新闻数据（临时验证用）。"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func, select
from config.db_conf import AsyncSessionLocal
from models import Category, News

async def main():
    async with AsyncSessionLocal() as db:
        total = (await db.execute(select(func.count(News.id)))).scalar_one()
        cat_count = (await db.execute(select(func.count(Category.id)))).scalar_one()
        print(f"分类数: {cat_count}, 新闻总数: {total}")
        # LEFT JOIN 统计每个分类的新闻数
        rows = (await db.execute(
            select(Category.name, func.count(News.id))
            .join(News, News.category_id == Category.id, isouter=True)
            .group_by(Category.id).order_by(Category.sort_order)
        )).all()
        ...
```

- 一个实用小脚本：跑一下就知道库里有多少分类、多少新闻、分布如何。
- 新知识点：`isouter=True` = LEFT JOIN（左连接）——即使某个分类没有新闻也能统计出 0，而不是丢行。
- 这类"验证/调试用的一次性脚本"属于 🟢，写完用完可留可删。

**README.md —— 项目的"说明书"**：记录快速开始、接口清单、配置说明、与课程数据的对齐情况。**写 README 是工程习惯**：让任何人（包括三个月后的你自己）拿到项目就能跑起来。

---

## 11. 端到端演练：一个用户的完整旅程（🔴 综合检验）

现在把所有知识串起来。想象你是前端，用 HTTP 调这个后端：

### 第一步：注册（POST /api/user/register）

```
前端发：{"username":"alice","email":"alice@example.com","password":"secret123"}
```

发生了什么：
1. FastAPI 收到请求 → 校验 body 是否符合 `UserCreate`（类型、长度、邮箱格式）→ 不符合直接 422。
2. `get_db` 依赖打开数据库会话。
3. 路由调 `get_user_by_username` / `get_user_by_email` 查重。
4. `create_user`：bcrypt 哈希密码 → 插入 user 表 → flush 拿到 id。
5. `create_token`：生成 64 位随机 token → 插入 user_token 表 → commit。
6. 返回 `{code:200, data:{token:"...", user_info:{...}}}`。

**前端拿到 token 后存起来（localStorage），后续所有需要登录的请求都带上 `Authorization: Bearer <token>`。**

### 第二步：看新闻（GET /api/news/list）

1. 校验 query 参数（page≥1，pageSize≤100）。
2. `news_cache.get_news_list`：先查 Redis key `news_list:all:1:10` → 没命中 → 查数据库（分页）→ 写回缓存。
3. 同时 `get_news_count` 算总数 → 组装 `{list, total, hasMore}`。
4. 返回。**第二次请求同样的分页，直接命中缓存，数据库零压力。**

### 第三步：点开详情（GET /api/news/detail?id=1）

1. `news_cache.get_news_detail`：查缓存 → 没命中查库。
2. `increase_news_views`：**数据库原子操作**浏览量 +1 → 删掉详情缓存（下次重建，刷新浏览量）。
3. `get_related_news`：查 related_news 表 → 空 → 回退同分类热门 5 条。
4. 返回 `{..., views: 12501, relatedNews: [...]}`。

### 第四步：收藏（POST /api/favorite/add）

1. 请求头带 token → `get_current_user` 认证 → 拿到 user。
2. 检查新闻存在（404）、检查没收藏过（400）。
3. 插入 favorite 表（user_id + news_id，联合唯一兜底防重）。
4. 返回"收藏成功"。**前端再调用 /check 会得到 isFavorite: true。**

### 第五步：浏览历史（POST /api/history/add）→ 查看（GET /api/history/list）

流程同收藏。历史列表用 join 一次查出"历史记录 + 新闻信息"。

### 第六步：AI 问答（POST /api/ai/chat）

1. 没配 API Key → 返回"未启用"提示（业务不挂）。
2. 配了 → httpx 调通义千问 → 拿到回答 → 写入 ai_chat 表（登录用户记录归属）。
3. 之后 GET /api/ai/history 能看到自己的问答记录。

**到这里你其实已经掌握了整个后端的所有核心流程。** 把每一步的"路由→crud→model"链路画一遍，你能独立讲清楚，就说明真的懂了。

---

## 12. 现代视角：哪些必须亲手掌握，哪些交给 AI

### 12.1 总览表（按文件）

| 文件/知识点 | 等级 | 理由 | 建议 |
| --- | --- | --- | --- |
| FastAPI 路由语法（@router.get、Depends、Query） | 🔴 | 所有 Web 项目的地基 | 亲手敲 10 个接口练熟 |
| 依赖注入（get_db、get_current_user） | 🔴 | 框架核心机制，面试必问 | 能讲清"为什么用 yield" |
| Pydantic schema 与校验 | 🔴 | 数据安全第一道门 | 亲手写请求/响应模型 |
| SQLAlchemy 模型与查询 | 🔴 | 换任何项目都要写 | 亲手建表、写 select/join |
| 异步（async/await） | 🔴 | 现代 Python 后端标配 | 理解事件循环，亲手写异步查询 |
| Token 认证流程 | 🔴 | 每个业务系统都有 | 能画出完整链路 |
| 分页 + join 防 N+1 | 🔴 | 高频实战考点 | 会自己写 |
| 缓存 Cache-Aside 与降级 | 🟡 | 思想重要，细节可让 AI 写 | 能讲流程，实现可抄 |
| bcrypt / secrets | 🟡 | 用库即可，但要知道"为什么" | 记住"加盐+慢哈希"原理 |
| 全局异常处理 | 🟡 | 设计思想重要 | 能讲统一格式的好处 |
| 初始化/导入/迁移脚本 | 🟢 | 一次性工具 | 直接让 AI 写，你看效果 |
| 冒烟测试 / .http / .gitignore | 🟢 | 工程配套 | 会用即可 |
| CORS 配置 | 🟡 | 知道"为什么跨域"即可 | 会改 allow_origins |
| Alembic / Docker / pytest（未引入） | 进阶 | 生产必备 | 学完本 demo 再补 |

### 12.2 面试/实战高频考点（从本 demo 提炼）

1. **FastAPI 为什么快？** 异步 + 类型提示 + 自动文档。
2. **依赖注入是什么？** 框架帮你管理"前置工作"（认证、数据库会话），函数只管核心逻辑。
3. **为什么密码用 bcrypt？** 加盐防彩虹表、慢哈希防暴力破解。
4. **Token 方案 vs JWT？** 本 demo 用"token 存表"：可主动失效、可踢人；JWT 无状态、跨服务方便但发出去收不回。面试常问选型，能说出各自优劣即可。
5. **缓存三种问题？** 穿透（查不存在数据）、击穿（热点 key 过期瞬间）、雪崩（大量 key 同时过期）。demo 做了雪崩防护（过期时间错开）+ 降级，穿透/击穿可以继续补。
6. **如何防越权？** 所有查询都带 user.id 过滤 + 删除时校验归属。
7. **异步什么时候用？** IO 密集（网络请求、数据库）用异步；CPU 密集用进程池。本 demo 的 AI 调用就是典型异步场景。
8. **ORM vs 原生 SQL？** 开发效率 ORM 高；复杂查询/性能调优用原生 SQL 或 SQLAlchemy 核心。

### 12.3 把 demo 升级成"真生产"的路线图

1. **换数据库**：SQLite → MySQL/PostgreSQL（改 `db_conf.py` 一行 + 装驱动 + 数据迁移）。
2. **加迁移工具**：引入 Alembic，替代手写 ALTER。
3. **换 JWT**（如果要多服务共享登录态）或用现有 token 方案加刷新机制。
4. **写 pytest 测试**：`TestClient` + 测试数据库，替代冒烟脚本（注意 Python 3.14 下 TestClient 有兼容问题，可用 httpx ASGITransport 替代）。
5. **容器化**：Dockerfile + docker-compose（app + redis + mysql）。
6. **部署**：Nginx 反向代理 + uvicorn 多 worker + systemd。
7. **监控**：日志结构化、接口耗时统计、错误上报（Sentry）。
8. **安全加固**：限流（防刷）、HTTPS、密码策略、审计日志。
9. **加前端**：Vue3 + Vant（课程里有 xwzx-news 前端，可直接对接本后端）。

### 12.4 用 AI 辅助的正确姿势（现代开发者的基本功）

**哪些可以放心交给 AI：**

- 初始化/迁移/测试脚本、.gitignore、Dockerfile、CI 配置——描述清楚需求，AI 一次写好。
- 模板化的 crud 函数（查/增/删/列表）——把 models 定义好，让 AI 按你的风格生成。
- 常规异常处理、响应封装的初稿。
- SQL 优化建议、缓存 key 设计参考。

**哪些必须自己把关（AI 容易出错的地方）：**

- **认证/鉴权逻辑**：必须自己 review 每一行（漏一个接口没加认证就是安全事故）。
- **外键/唯一约束/级联删除**：让 AI 建表要仔细核对关系。
- **事务边界**：哪些操作必须一起成功（如"创建用户+发 token"）。
- **配置与密钥**：确认没有硬编码进代码。
- **性能热点**：join、索引、缓存 key 的合理性。
- **模型返回的字段**：确认没有把敏感字段（密码哈希）暴露出去。

> 核心心法：**AI 是"写得快的初级工程师"，你是"把关的架构师"。** 架构决策（分层、表设计、认证方案、缓存策略）永远是人的活。

---

## 13. 常见问题 FAQ

**Q1：为什么用 SQLite 而不是 MySQL？**
零配置、随项目走，适合学习和小型 demo。切 MySQL 只需改一行连接串 + 装 aiomysql（db_conf.py 注释里有示例）。生产高并发必须上 MySQL/PostgreSQL。

**Q2：`async def` 和普通函数有什么区别？**
async 函数里可以 `await`（等待 IO 时不阻塞事件循环，让其他请求并发处理）。数据库查询、HTTP 调用都是 IO 密集操作，用异步能大幅提升并发能力。**同步函数处理请求是"排队等"，异步是"交替等"**。

**Q3：为什么访问详情要删缓存再重建，不直接更新缓存？**
更新缓存要处理"并发写的一致性"（两个人同时改 views），复杂且容易出错。删缓存是 Cache-Aside 标准做法：下次读时自动重建，简单可靠。代价是删除后第一次读会慢一点。

**Q4：token 过期了怎么办？**
重新登录拿新 token。想做得更顺滑可以加"刷新 token"机制（有效期短的 access token + 长的 refresh token），进阶话题。

**Q5：`Base.metadata.create_all` 能改表结构吗？**
不能。它只建"不存在的表"，**不修改已存在的表**（不加列、不改类型）。改表结构要用迁移脚本（demo 的 migrate_db.py）或 Alembic。

**Q6：为什么列表接口不走 ORM relationship 直接 `news.category`？**
demo 里列表返回的字段里**不需要分类对象**（只有 category_id），避免多余查询。需要时才 join，这是"按需加载"。

**Q7：Redis 没装，项目还能跑吗？**
能。cache_conf 有完整降级：连不上 Redis → 自动标记禁用 → 直查数据库。**这轮设计保证"可选依赖不影响主业务"**——你可以在没有 Redis 的机器上直接跑通整个项目。

**Q8：前端怎么对接这些接口？**
每个接口都有自动文档（/docs），字段、参数、响应结构都写在里面。前端按文档调即可；`Authorization: Bearer <token>` 是登录后统一要带的头。

---

## 写在最后：怎么算"掌握了这个 demo"

给自己打个分（能独立做到才算）：

- [ ] 不看文档，能从头搭一个 FastAPI 项目（venv + 依赖 + main.py + 一个接口）
- [ ] 能说清分层架构：router/crud/model/schema 各管什么
- [ ] 能画出"注册→登录→带 token 访问"的完整链路
- [ ] 能解释 bcrypt、secrets、原子 UPDATE、join 防 N+1
- [ ] 能讲出缓存 Cache-Aside 流程和 Redis 挂了怎么办
- [ ] 能新增一个"点赞"模块：表 → 模型 → schema → crud → 路由 → 冒烟测试，全部自己写

> 做到最后一条，这个 demo 就真正变成你的实战经验了。遇到卡住的地方，带着问题回来翻这份文档，或者直接问我。



