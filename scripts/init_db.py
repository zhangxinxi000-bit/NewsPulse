"""初始化脚本：建表并写入示例数据（分类 + 新闻）。

用法：
    .venv\\Scripts\\python scripts\\init_db.py

说明：
- 幂等：分类表已有数据时跳过写入，不会重复插入。
- 演示数据仅用于本地体验，生产环境请删除本脚本。
"""
import asyncio
import os
import sys

# 保证脚本无论从哪里运行都能导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func, select

from config.db_conf import async_engine, AsyncSessionLocal
from models import Base, Category, News

CATEGORIES = [
    {"name": "科技", "sort_order": 1},
    {"name": "财经", "sort_order": 2},
    {"name": "体育", "sort_order": 3},
    {"name": "娱乐", "sort_order": 4},
    {"name": "国际", "sort_order": 5},
]

# (分类名, 标题, 简介, 内容, 作者, 浏览量)
NEWS_TEMPLATE = [
    ("科技", "FastAPI 实战：异步 Web 框架如何提升 API 性能", "从同步阻塞到异步并发，FastAPI 借助 Python asyncio 让单进程也能支撑高并发请求。", "FastAPI 基于 Starlette 与 Pydantic 构建，天然支持异步路由与依赖注入。本文将演示同步与异步接口的性能差异，并给出从 Flask 迁移到 FastAPI 的路径建议……", "编辑部", 1280),
    ("科技", "大模型应用开发入门：从 API 调用到业务落地", "调用通义千问等大模型 API，为产品快速增加智能问答能力。", "本文以阿里云百炼平台为例，介绍大模型 HTTP 接口的调用方式、参数设计与错误处理，并讨论缓存与成本控制的常见做法……", "AI 编辑部", 860),
    ("财经", "央行发布最新货币政策报告：稳健基调不变", "报告强调保持流动性合理充裕，支持实体经济发展。", "最新一期货币政策执行报告指出，将继续实施稳健的货币政策，综合运用多种货币政策工具，保持流动性合理充裕……", "财经观察", 520),
    ("财经", "A 股三季报收官：科技板块业绩增速领先", "半导体、AI 算力相关公司业绩表现亮眼。", "随着三季报披露完毕，A 股上市公司整体营收保持增长，其中半导体与人工智能算力板块业绩增速显著领先……", "市场分析", 410),
    ("体育", "亚洲杯预选赛：国足主场战平对手", "双方各入一球，晋级形势仍存变数。", "在刚刚结束的亚洲杯预选赛中，中国队主场 1:1 战平对手。主教练在赛后表示球队将全力备战下一场比赛……", "体育前线", 950),
    ("体育", "NBA 新赛季开打：卫冕冠军迎来开门红", "核心球员合砍 60 分，全场压制对手。", "NBA 新赛季揭幕战，卫冕冠军主场 120:105 击败对手，两名核心球员合砍 60 分，展现了强大的统治力……", "篮球频道", 760),
    ("娱乐", "国庆档电影市场火热，票房有望再创新高", "多部影片口碑票房双丰收，带动观影热潮。", "今年国庆档多部影片同时上映，涵盖科幻、动画、喜剧等多种类型，观众观影热情高涨，档期总票房有望突破历史纪录……", "文娱速递", 630),
    ("娱乐", "音乐节巡演官宣：多城连开，预售火爆", "门票开售即售罄，主办方紧急加场。", "知名音乐节品牌宣布开启全国巡演，首批公布的城市门票开售数分钟即告售罄，主办方表示正在协调增加场次……", "音乐现场", 380),
    ("国际", "全球气候大会达成新协议：多国承诺减排目标", "与会各方就阶段性减排路线图达成一致。", "为期两周的气候大会闭幕，与会各国就下一阶段减排目标达成共识，将共同推动清洁能源转型与碳减排行动……", "国际观察", 290),
    ("国际", "国际油价波动加剧，能源市场关注供给变化", "多重因素影响下，国际油价短期震荡。", "受地缘局势与主要产油国政策影响，国际油价近期波动加剧。分析人士预计，短期内能源市场仍将维持高位震荡……", "环球经济", 340),
]


async def init_data():
    # 1. 建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. 写入示例数据（幂等）
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count(Category.id)))
        if result.scalar_one() > 0:
            print("分类表已有数据，跳过示例数据写入。")
            return

        # 写入分类
        categories = []
        for item in CATEGORIES:
            category = Category(name=item["name"], sort_order=item["sort_order"])
            db.add(category)
            categories.append(category)
        await db.flush()

        # 写入新闻
        category_map = {c.name: c.id for c in categories}
        for cat_name, title, desc, content, author, views in NEWS_TEMPLATE:
            db.add(
                News(
                    title=title,
                    description=desc,
                    content=content,
                    author=author,
                    category_id=category_map[cat_name],
                    views=views,
                )
            )

        await db.commit()
        print(f"初始化完成：{len(CATEGORIES)} 个分类，{len(NEWS_TEMPLATE)} 条示例新闻。")


if __name__ == "__main__":
    asyncio.run(init_data())
