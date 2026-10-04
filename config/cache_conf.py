"""Redis 缓存配置与封装。

设计说明：
- 所有缓存操作均做了异常兜底，Redis 未安装或未启动时自动降级
  （读取返回 None → 直接查数据库，写入静默失败），不影响业务。
- 数据越稳定，缓存时间越长；避免所有 key 同时过期导致缓存雪崩。
"""
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
_redis_disabled = False  # 连接失败后置为 True，本轮进程内不再尝试 Redis，避免拖慢业务


def get_redis_client():
    """惰性创建 Redis 客户端，失败返回 None（降级模式）。

    关键设计：
    - socket_connect_timeout / socket_timeout 保证 Redis 不可用时快速失败，不阻塞请求。
    - 首次连接失败后设置 _redis_disabled，后续请求直接跳过 Redis（快速降级）。
    """
    global _redis_client, _redis_disabled
    if _redis_disabled:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        import redis.asyncio as redis

        _redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,          # 将字节解码为字符串
            socket_connect_timeout=1,       # 连接超时 1 秒
            socket_timeout=2,               # 读写超时 2 秒
        )
        return _redis_client
    except Exception as e:
        _redis_disabled = True
        print(f"[cache] Redis 客户端创建失败，已禁用缓存，直查数据库：{e}")
        return None


def _mark_disabled():
    """标记缓存已禁用（连接失败后调用）。"""
    global _redis_disabled
    _redis_disabled = True


# ---------- 读取缓存 ----------
async def get_cache(key: str):
    """读取字符串缓存，不存在或 Redis 不可用返回 None。"""
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
    """读取 JSON 缓存（列表/字典），不存在或 Redis 不可用返回 None。"""
    data = await get_cache(key)
    if not data:
        return None
    try:
        return json.loads(data)
    except Exception as e:
        print(f"[cache] JSON 解析失败：{e}")
        return None


# ---------- 写入缓存 ----------
async def set_cache(key: str, value: Any, expire: int = 3600):
    """写入缓存（setex），成功返回 True，Redis 不可用返回 False。"""
    client = get_redis_client()
    if client is None:
        return False
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)  # 中文正常保存
        await client.setex(key, expire, value)
        return True
    except Exception as e:
        _mark_disabled()
        print(f"[cache] 设置缓存失败，已禁用缓存：{e}")
        return False


# ---------- 删除缓存 ----------
async def delete_cache(key: str):
    """删除指定缓存键。"""
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
    """按模式批量删除缓存（如 news_list:*），用于数据更新后失效相关缓存。"""
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
