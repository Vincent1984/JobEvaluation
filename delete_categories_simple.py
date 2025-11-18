"""简单的删除职位分类数据脚本"""

import asyncio
from sqlalchemy import select, delete
from src.core.database import AsyncSessionLocal
from src.models.database import JobCategoryDB, JobDescriptionDB


async def main():
    print("=" * 60)
    print("删除职位分类管理数据")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as session:
        # 统计数据
        result = await session.execute(select(JobCategoryDB))
        categories = result.scalars().all()
        print(f"当前职位分类数量: {len(categories)}")
        
        result = await session.execute(
            select(JobDescriptionDB).where(
                (JobDescriptionDB.category_level1_id.isnot(None)) |
                (JobDescriptionDB.category_level2_id.isnot(None)) |
                (JobDescriptionDB.category_level3_id.isnot(None))
            )
        )
        jds = result.scalars().all()
        print(f"有分类的 JD 数量: {len(jds)}")
        print()
        
        if len(categories) == 0 and len(jds) == 0:
            print("✅ 没有需要删除的数据")
            return
        
        # 清除 JD 分类关联
        if len(jds) > 0:
            print(f"清除 {len(jds)} 个 JD 的分类关联...")
            for jd in jds:
                jd.category_level1_id = None
                jd.category_level2_id = None
                jd.category_level3_id = None
            await session.commit()
            print("✓ 完成")
            print()
        
        # 删除分类
        if len(categories) > 0:
            print(f"删除 {len(categories)} 个职位分类...")
            for level in [3, 2, 1]:
                await session.execute(
                    delete(JobCategoryDB).where(JobCategoryDB.level == level)
                )
            await session.commit()
            print("✓ 完成")
            print()
        
        # 验证
        result = await session.execute(select(JobCategoryDB))
        remaining = len(result.scalars().all())
        print(f"剩余职位分类: {remaining}")
        print()
        print("=" * 60)
        print("✅ 删除完成！")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
