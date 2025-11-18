"""数据库初始化脚本"""

import sys
import os
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database import init_db, drop_db, AsyncSessionLocal
from src.models.database import JobCategoryDB
import uuid


async def create_sample_categories():
    """创建示例职位分类"""
    async with AsyncSessionLocal() as db:
        try:
            # 一级分类
            tech_cat = JobCategoryDB(
                id=f"cat_tech_{uuid.uuid4().hex[:8]}",
                name="技术类",
                level=1,
                parent_id=None,
                description="技术相关职位"
            )
            db.add(tech_cat)
            
            business_cat = JobCategoryDB(
                id=f"cat_business_{uuid.uuid4().hex[:8]}",
                name="业务类",
                level=1,
                parent_id=None,
                description="业务相关职位"
            )
            db.add(business_cat)
            
            # 二级分类（技术类）
            dev_cat = JobCategoryDB(
                id=f"cat_dev_{uuid.uuid4().hex[:8]}",
                name="研发",
                level=2,
                parent_id=tech_cat.id,
                description="软件研发相关职位"
            )
            db.add(dev_cat)
            
            ops_cat = JobCategoryDB(
                id=f"cat_ops_{uuid.uuid4().hex[:8]}",
                name="运维",
                level=2,
                parent_id=tech_cat.id,
                description="系统运维相关职位"
            )
            db.add(ops_cat)
            
            # 三级分类（研发）
            backend_cat = JobCategoryDB(
                id=f"cat_backend_{uuid.uuid4().hex[:8]}",
                name="后端工程师",
                level=3,
                parent_id=dev_cat.id,
                description="后端开发工程师",
                sample_jd_ids=[]  # 可以添加样本JD ID
            )
            db.add(backend_cat)
            
            frontend_cat = JobCategoryDB(
                id=f"cat_frontend_{uuid.uuid4().hex[:8]}",
                name="前端工程师",
                level=3,
                parent_id=dev_cat.id,
                description="前端开发工程师",
                sample_jd_ids=[]
            )
            db.add(frontend_cat)
            
            fullstack_cat = JobCategoryDB(
                id=f"cat_fullstack_{uuid.uuid4().hex[:8]}",
                name="全栈工程师",
                level=3,
                parent_id=dev_cat.id,
                description="全栈开发工程师",
                sample_jd_ids=[]
            )
            db.add(fullstack_cat)
            
            await db.commit()
            
            print("✅ 示例职位分类已创建")
            print(f"  - 一级分类: {tech_cat.name}, {business_cat.name}")
            print(f"  - 二级分类: {dev_cat.name}, {ops_cat.name}")
            print(f"  - 三级分类: {backend_cat.name}, {frontend_cat.name}, {fullstack_cat.name}")
        except Exception as e:
            await db.rollback()
            raise e


async def main_async():
    """异步主函数"""
    print("=" * 60)
    print("🗄️  数据库初始化脚本")
    print("=" * 60)
    print()
    
    print("请选择操作:")
    print("1. 初始化数据库（创建表）")
    print("2. 重置数据库（删除并重建所有表）")
    print("3. 创建示例数据")
    print("0. 退出")
    print()
    
    choice = input("请选择 (0-3): ").strip()
    
    if choice == "1":
        print("\n📦 正在初始化数据库...")
        await init_db()
        print("✅ 数据库初始化完成！")
    
    elif choice == "2":
        confirm = input("\n⚠️  警告：此操作将删除所有数据！确认继续？(yes/no): ").strip().lower()
        if confirm == "yes":
            print("\n🗑️  正在删除旧表...")
            await drop_db()
            print("\n📦 正在创建新表...")
            await init_db()
            print("✅ 数据库重置完成！")
        else:
            print("❌ 操作已取消")
    
    elif choice == "3":
        print("\n📝 正在创建示例数据...")
        try:
            await create_sample_categories()
            print("✅ 示例数据创建完成！")
        except Exception as e:
            print(f"❌ 创建示例数据失败: {e}")
    
    elif choice == "0":
        print("👋 再见！")
    
    else:
        print("❌ 无效选择")


def main():
    """主函数入口"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
