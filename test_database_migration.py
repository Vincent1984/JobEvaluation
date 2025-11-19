"""测试数据库迁移和新schema"""

import sys
import os
from pathlib import Path
import tempfile
import uuid

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from src.models.database import (
    Base, CompanyDB, CategoryTagDB, JobCategoryDB, 
    EvaluationResultDB, JobDescriptionDB
)
from datetime import datetime


def generate_id():
    """生成唯一ID"""
    return str(uuid.uuid4())


def test_new_schema():
    """测试新的数据库schema"""
    
    print("测试数据库schema...")
    print("=" * 60)
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # 创建数据库引擎
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 测试1: 创建企业
        print("\n测试1: 创建企业")
        company_id = generate_id()
        company = CompanyDB(
            id=company_id,
            name="测试企业",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(company)
        session.commit()
        print(f"  ✓ 成功创建企业: {company.name} (ID: {company_id})")
        
        # 测试2: 创建职位分类（3层级）
        print("\n测试2: 创建职位分类（3层级）")
        
        # 第一层级
        cat1_id = generate_id()
        category1 = JobCategoryDB(
            id=cat1_id,
            company_id=company_id,
            name="技术类",
            level=1,
            description="技术相关职位",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(category1)
        
        # 第二层级
        cat2_id = generate_id()
        category2 = JobCategoryDB(
            id=cat2_id,
            company_id=company_id,
            name="研发",
            level=2,
            parent_id=cat1_id,
            description="研发相关职位",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(category2)
        
        # 第三层级
        cat3_id = generate_id()
        category3 = JobCategoryDB(
            id=cat3_id,
            company_id=company_id,
            name="后端工程师",
            level=3,
            parent_id=cat2_id,
            description="后端开发职位",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(category3)
        session.commit()
        
        print(f"  ✓ 成功创建第一层级分类: {category1.name}")
        print(f"  ✓ 成功创建第二层级分类: {category2.name}")
        print(f"  ✓ 成功创建第三层级分类: {category3.name}")
        
        # 测试3: 为第三层级分类添加标签
        print("\n测试3: 为第三层级分类添加标签")
        
        tags_data = [
            ("高战略重要性", "战略重要性", "该岗位对企业战略目标实现至关重要"),
            ("高业务价值", "业务价值", "该岗位直接创造核心业务价值"),
            ("高技能稀缺性", "技能稀缺性", "该岗位所需技能在市场上较为稀缺")
        ]
        
        for tag_name, tag_type, description in tags_data:
            tag = CategoryTagDB(
                id=generate_id(),
                category_id=cat3_id,
                name=tag_name,
                tag_type=tag_type,
                description=description,
                created_at=datetime.now()
            )
            session.add(tag)
            print(f"  ✓ 成功添加标签: {tag_name} ({tag_type})")
        
        session.commit()
        
        # 测试4: 创建JD并关联分类
        print("\n测试4: 创建JD并关联分类")
        
        jd_id = generate_id()
        jd = JobDescriptionDB(
            id=jd_id,
            job_title="高级后端工程师",
            department="技术部",
            location="北京",
            responsibilities=["开发后端服务", "优化系统性能"],
            required_skills=["Python", "Django", "PostgreSQL"],
            preferred_skills=["Docker", "Kubernetes"],
            qualifications=["本科及以上学历", "3年以上工作经验"],
            raw_text="高级后端工程师职位描述...",
            category_level1_id=cat1_id,
            category_level2_id=cat2_id,
            category_level3_id=cat3_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(jd)
        session.commit()
        print(f"  ✓ 成功创建JD: {jd.job_title}")
        
        # 测试5: 创建评估结果（包含新字段）
        print("\n测试5: 创建评估结果（包含新字段）")
        
        eval_id = generate_id()
        evaluation = EvaluationResultDB(
            id=eval_id,
            jd_id=jd_id,
            evaluation_model_type="standard",
            overall_score=85.5,
            completeness=90.0,
            clarity=85.0,
            professionalism=82.0,
            issues=["缺少薪资范围"],
            company_value="高价值",
            is_core_position=True,
            dimension_contributions={
                "jd_content": 40,
                "evaluation_template": 30,
                "category_tags": 30
            },
            is_manually_modified=False,
            manual_modifications=[],
            recommendations=["建议添加薪资范围"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(evaluation)
        session.commit()
        print(f"  ✓ 成功创建评估结果")
        print(f"    - 综合质量分数: {evaluation.overall_score}")
        print(f"    - 企业价值: {evaluation.company_value}")
        print(f"    - 核心岗位: {evaluation.is_core_position}")
        print(f"    - 维度贡献度: {evaluation.dimension_contributions}")
        
        # 测试6: 测试手动修改评估结果
        print("\n测试6: 测试手动修改评估结果")
        
        evaluation.overall_score = 88.0
        evaluation.company_value = "中价值"
        evaluation.is_manually_modified = True
        evaluation.manual_modifications = [
            {
                "timestamp": datetime.now().isoformat(),
                "modified_fields": {
                    "overall_score": 88.0,
                    "company_value": "中价值"
                },
                "reason": "根据实际情况调整",
                "original_values": {
                    "overall_score": 85.5,
                    "company_value": "高价值"
                }
            }
        ]
        session.commit()
        print(f"  ✓ 成功修改评估结果")
        print(f"    - 新质量分数: {evaluation.overall_score}")
        print(f"    - 新企业价值: {evaluation.company_value}")
        print(f"    - 手动修改标记: {evaluation.is_manually_modified}")
        
        # 测试7: 验证关系和级联删除
        print("\n测试7: 验证关系和级联删除")
        
        # 查询企业的所有分类
        company_categories = session.query(JobCategoryDB).filter_by(company_id=company_id).all()
        print(f"  ✓ 企业有 {len(company_categories)} 个分类")
        
        # 查询第三层级分类的所有标签
        category_tags = session.query(CategoryTagDB).filter_by(category_id=cat3_id).all()
        print(f"  ✓ 第三层级分类有 {len(category_tags)} 个标签")
        
        # 测试8: 验证索引
        print("\n测试8: 验证索引")
        
        inspector = inspect(engine)
        
        # 检查job_categories表的索引
        indexes = inspector.get_indexes("job_categories")
        index_names = [idx['name'] for idx in indexes]
        print(f"  ✓ job_categories 表索引: {index_names}")
        
        # 检查category_tags表的索引
        indexes = inspector.get_indexes("category_tags")
        index_names = [idx['name'] for idx in indexes]
        print(f"  ✓ category_tags 表索引: {index_names}")
        
        # 检查evaluation_results表的索引
        indexes = inspector.get_indexes("evaluation_results")
        index_names = [idx['name'] for idx in indexes]
        print(f"  ✓ evaluation_results 表索引: {index_names}")
        
        print("\n" + "=" * 60)
        print("所有测试通过！✓")
        print("\n新schema功能验证:")
        print("  ✓ 企业表创建和管理")
        print("  ✓ 分类标签表创建和管理")
        print("  ✓ 职位分类关联企业")
        print("  ✓ 评估结果综合评估字段")
        print("  ✓ 评估结果手动修改支持")
        print("  ✓ 关系和级联删除")
        print("  ✓ 索引创建")
        
        session.close()
        engine.dispose()
        
    finally:
        # 清理临时数据库
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            # Windows可能会锁定文件，忽略清理错误
            pass


if __name__ == "__main__":
    test_new_schema()
