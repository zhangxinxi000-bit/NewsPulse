"""查询数据库中的新闻数据（临时验证用）。"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func, select  # noqa: E402

from config.db_conf import AsyncSessionLocal  # noqa: E402
from models import Category, News  # noqa: E402


async def main():
    async with AsyncSessionLocal() as db:
        total = (await db.execute(select(func.count(News.id)))).scalar_one()
        cat_count = (await db.execute(select(func.count(Category.id)))).scalar_one()
        print(f"分类数: {cat_count}, 新闻总数: {total}")
        print("--- 各分类新闻数 ---")
        rows = (
            await db.execute(
                select(Category.name, func.count(News.id))
                .join(News, News.category_id == Category.id, isouter=True)
                .group_by(Category.id)
                .order_by(Category.sort_order)
            )
        ).all()
        for name, cnt in rows:
            print(f"  {name}: {cnt}")
        print("--- 新闻列表(全部) ---")
        stmt = select(News).order_by(News.id.asc())
        news_list = (await db.execute(stmt)).scalars().all()
        for n in news_list:
            print(f"  [{n.id}] {n.title} (views={n.views})")


if __name__ == "__main__":
    asyncio.run(main())
