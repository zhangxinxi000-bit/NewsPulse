"""从外部 SQL 转储文件批量导入新闻数据到本地 SQLite 数据库。

用法：
    .venv\\Scripts\\python scripts\\import_seed_data.py <sql文件路径>

说明：
- 解析 MySQL 版 SQL 转储文件中的 news_category / news 的 INSERT 数据。
- 导入前会清空 news、news_category、favorite、history 四张表（用户表保留）。
- 幂等：可重复执行。
"""
import asyncio
import csv
import io
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete, select, func  # noqa: E402

from config.db_conf import AsyncSessionLocal, async_engine  # noqa: E402
from models import Base, Category, News, Favorite, History  # noqa: E402

# 清理从网页复制带入的引用标记，如 :cite[1]
CITE_PATTERN = re.compile(r":cite\[\d+\]")


def clean_text(text: str) -> str:
    return CITE_PATTERN.sub("", text).strip()


def parse_row(line: str):
    """解析一行元组：('a', 'b', 1, 'c,d'), —— 用 csv 模块处理引号与逗号。"""
    line = line.strip().rstrip(",").rstrip(";").strip()
    if not (line.startswith("(") and line.endswith(")")):
        return None
    inner = line[1:-1]
    try:
        row = next(csv.reader(io.StringIO(inner), quotechar="'", skipinitialspace=True))
    except Exception:
        return None
    return [clean_text(v) if v is not None else None for v in row]


def extract_inserts(sql_text: str):
    """提取 INSERT INTO 块，返回 {表名: [(列名, [(值1, ...), ...]), ...]}。

    注意：同一张表可能有多个 INSERT 块且列顺序不同，必须按块分别保存列名。
    """
    blocks = {}
    pattern = re.compile(
        r"INSERT INTO\s+`?(\w+)`?\s*\(([^)]*)\)\s*VALUES\s*(.*?);",
        re.IGNORECASE | re.DOTALL,
    )
    for m in pattern.finditer(sql_text):
        table = m.group(1)
        columns = [c.strip().strip("`") for c in m.group(2).split(",")]
        values_block = m.group(3)
        rows = []
        for raw_line in values_block.splitlines():
            row = parse_row(raw_line)
            if row:
                rows.append(row)
        blocks.setdefault(table, []).append((columns, rows))
    return blocks


async def import_data(sql_path: str):
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_text = f.read()

    blocks = extract_inserts(sql_text)
    if "news_category" not in blocks or "news" not in blocks:
        print("解析失败：未找到 news_category / news 的 INSERT 数据")
        return

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. 清空新闻相关表（保留用户）
        await db.execute(delete(Favorite))
        await db.execute(delete(History))
        await db.execute(delete(News))
        await db.execute(delete(Category))
        await db.flush()

        # 2. 导入分类（按每个块独立解析）
        cat_blocks = blocks["news_category"]
        categories = []
        for cat_cols, cat_rows in cat_blocks:
            name_idx = cat_cols.index("name") if "name" in cat_cols else 0
            sort_idx = cat_cols.index("sort_order") if "sort_order" in cat_cols else 1
            for row in cat_rows:
                categories.append(
                    Category(name=clean_text(row[name_idx]), sort_order=int(row[sort_idx] or 0))
                )
        db.add_all(categories)
        await db.flush()
        print(f"导入分类 {len(categories)} 个")

        # 3. 导入新闻（每个块独立建列名索引）
        news_blocks = blocks["news"]
        news_objs = []
        skipped = 0
        for news_cols, news_rows in news_blocks:
            idx = {c: i for i, c in enumerate(news_cols)}
            for row in news_rows:
                try:
                    category_id = int(row[idx["category_id"]])
                    publish_time = None
                    if "publish_time" in idx and row[idx["publish_time"]]:
                        publish_time = datetime.fromisoformat(row[idx["publish_time"]])
                    news_objs.append(
                        News(
                            title=clean_text(row[idx["title"]]),
                            description=clean_text(row[idx["description"]]) if "description" in idx else None,
                            content=clean_text(row[idx["content"]]),
                            image=row[idx["image"]] if "image" in idx else None,
                            author=clean_text(row[idx["author"]]) if "author" in idx else None,
                            category_id=category_id,
                            views=int(row[idx["views"]] or 0) if "views" in idx else 0,
                            publish_time=publish_time,
                        )
                    )
                except (ValueError, IndexError) as e:
                    skipped += 1
                    print(f"  跳过异常行: {e} {str(row)[:80]}")
        db.add_all(news_objs)
        await db.commit()
        print(f"导入新闻 {len(news_objs)} 条（跳过 {skipped} 条异常行）")

        # 4. 校验
        total = (await db.execute(select(func.count(News.id)))).scalar_one()
        cat_total = (await db.execute(select(func.count(Category.id)))).scalar_one()
        print(f"校验：分类 {cat_total} 个，新闻 {total} 条")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python scripts/import_seed_data.py <sql文件路径>")
        sys.exit(1)
    asyncio.run(import_data(sys.argv[1]))
