#!/usr/bin/env python3
"""
数据库迁移脚本
用于将现有数据库升级到支持企业和分类标签的新schema
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from src.models.database import Base, CompanyDB, CategoryTagDB, JobCategoryDB, EvaluationResultDB
from datetime import datetime
import uuid


def generate_id():
    """生成唯一ID"""
    return str(uuid.uuid4())


def check_table_exists(engine, table_name):
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def check_column_exists(engine, table_name, column_name):
    """检查列是否存在"""
    inspector = inspect(engine)
    if not check_table_exists(engine, table_name):
        return False
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_database(db_path: str = "data/jd_analyzer.db"):
    """执行数据库迁移"""
    
    print(f"开始数据库迁移: {db_path}")
    print("=" * 60)
    
    # 创建数据库引擎
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 步骤1: 创建新表
        print("\n步骤1: 创建新表...")
        
        if not check_table_exists(engine, "companies"):
            print("  - 创建 companies 表")
            CompanyDB.__table__.create(engine)
        else:
            print("  - companies 表已存在，跳过")
        
        if not check_table_exists(engine, "category_tags"):
            print("  - 创建 category_tags 表")
            CategoryTagDB.__table__.create(engine)
        else:
            print("  - category_tags 表已存在，跳过")
        
        # 步骤2: 为现有分类创建默认企业
        print("\n步骤2: 为现有分类创建默认企业...")
        
        if check_table_exists(engine, "job_categories"):
            # 检查是否已有company_id列
            if not check_column_exists(engine, "job_categories", "company_id"):
                print("  - 创建默认企业")
                default_company_id = generate_id()
                default_company = CompanyDB(
                    id=default_company_id,
                    name="默认企业",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(default_company)
                session.commit()
                
                # 添加company_id列到job_categories表
                print("  - 添加 company_id 列到 job_categories 表")
                with engine.connect() as conn:
                    conn.execute(text(
                        f"ALTER TABLE job_categories ADD COLUMN company_id VARCHAR(50) DEFAULT '{default_company_id}'"
                    ))
                    conn.commit()
                
                # 添加updated_at列
                if not check_column_exists(engine, "job_categories", "updated_at"):
                    print("  - 添加 updated_at 列到 job_categories 表")
                    with engine.connect() as conn:
                        conn.execute(text(
                            "ALTER TABLE job_categories ADD COLUMN updated_at DATETIME"
                        ))
                        conn.commit()
                
                print(f"  - 已将所有现有分类关联到默认企业 (ID: {default_company_id})")
            else:
                print("  - company_id 列已存在，跳过")
        
        # 步骤3: 更新evaluation_results表
        print("\n步骤3: 更新 evaluation_results 表...")
        
        if check_table_exists(engine, "evaluation_results"):
            columns_to_add = [
                ("company_value", "VARCHAR(50)"),
                ("is_core_position", "BOOLEAN DEFAULT 0"),
                ("dimension_contributions", "TEXT"),  # JSON存储为TEXT
                ("is_manually_modified", "BOOLEAN DEFAULT 0"),
                ("manual_modifications", "TEXT"),  # JSON存储为TEXT
                ("updated_at", "DATETIME")
            ]
            
            with engine.connect() as conn:
                for col_name, col_type in columns_to_add:
                    if not check_column_exists(engine, "evaluation_results", col_name):
                        print(f"  - 添加 {col_name} 列")
                        conn.execute(text(
                            f"ALTER TABLE evaluation_results ADD COLUMN {col_name} {col_type}"
                        ))
                        conn.commit()
                    else:
                        print(f"  - {col_name} 列已存在，跳过")
        
        # 步骤4: 创建索引
        print("\n步骤4: 创建索引...")
        
        indexes = [
            ("idx_categories_company", "job_categories", "company_id"),
            ("idx_categories_level", "job_categories", "level"),
            ("idx_categories_parent", "job_categories", "parent_id"),
            ("idx_tags_category", "category_tags", "category_id"),
            ("idx_evaluation_jd", "evaluation_results", "jd_id"),
            ("idx_evaluation_company_value", "evaluation_results", "company_value"),
            ("idx_evaluation_core_position", "evaluation_results", "is_core_position"),
        ]
        
        with engine.connect() as conn:
            for idx_name, table_name, column_name in indexes:
                if check_table_exists(engine, table_name):
                    try:
                        conn.execute(text(
                            f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})"
                        ))
                        conn.commit()
                        print(f"  - 创建索引 {idx_name}")
                    except Exception as e:
                        print(f"  - 索引 {idx_name} 创建失败或已存在: {e}")
        
        print("\n" + "=" * 60)
        print("数据库迁移完成！")
        print("\n迁移摘要:")
        print("  ✓ 创建了 companies 表")
        print("  ✓ 创建了 category_tags 表")
        print("  ✓ 更新了 job_categories 表（添加 company_id）")
        print("  ✓ 更新了 evaluation_results 表（添加综合评估字段）")
        print("  ✓ 创建了必要的索引")
        print("\n注意事项:")
        print("  - 所有现有分类已关联到'默认企业'")
        print("  - 可以通过企业管理页面创建新企业")
        print("  - 第三层级分类现在可以添加标签")
        
    except Exception as e:
        print(f"\n错误: 迁移失败 - {e}")
        session.rollback()
        raise
    finally:
        session.close()


def rollback_migration(db_path: str = "data/jd_analyzer.db"):
    """回滚数据库迁移（仅用于开发测试）"""
    
    print(f"警告: 准备回滚数据库迁移: {db_path}")
    print("这将删除新添加的表和列！")
    
    response = input("确认回滚？(yes/no): ")
    if response.lower() != "yes":
        print("已取消回滚")
        return
    
    engine = create_engine(f"sqlite:///{db_path}")
    
    with engine.connect() as conn:
        # 删除新表
        if check_table_exists(engine, "category_tags"):
            conn.execute(text("DROP TABLE category_tags"))
            print("  - 删除 category_tags 表")
        
        if check_table_exists(engine, "companies"):
            conn.execute(text("DROP TABLE companies"))
            print("  - 删除 companies 表")
        
        conn.commit()
    
    print("回滚完成")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库迁移工具")
    parser.add_argument(
        "--db-path",
        default="data/jd_analyzer.db",
        help="数据库文件路径 (默认: data/jd_analyzer.db)"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="回滚迁移（仅用于开发测试）"
    )
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration(args.db_path)
    else:
        migrate_database(args.db_path)
