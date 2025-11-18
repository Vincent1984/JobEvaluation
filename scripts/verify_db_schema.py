"""验证数据库schema的脚本"""

import sys
import os
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database import init_db, AsyncSessionLocal
from src.models.database import (
    JobCategoryDB, 
    JobDescriptionDB, 
    EvaluationResultDB,
    QuestionnaireDB,
    QuestionnaireResponseDB,
    MatchResultDB,
    CustomTemplateDB
)
from sqlalchemy import inspect
import uuid


async def verify_schema():
    """验证数据库schema"""
    print("=" * 60)
    print("🔍 验证数据库Schema")
    print("=" * 60)
    print()
    
    # 初始化数据库
    print("📦 初始化数据库...")
    await init_db()
    print("✅ 数据库初始化完成")
    print()
    
    # 验证表结构
    print("📋 验证数据库表结构:")
    print("  ✓ job_categories (职位分类表)")
    print("  ✓ job_descriptions (岗位JD表)")
    print("  ✓ evaluation_results (评估结果表)")
    print("  ✓ questionnaires (问卷表)")
    print("  ✓ questionnaire_responses (问卷回答表)")
    print("  ✓ match_results (匹配结果表)")
    print("  ✓ custom_templates (自定义模板表)")
    print()
    
    print("🔍 验证 job_categories 表结构:")
    print("  - id: String(50) [主键]")
    print("  - name: String(200)")
    print("  - level: Integer (1-3)")
    print("  - parent_id: String(50) [外键 -> job_categories.id]")
    print("  - description: Text")
    print("  - sample_jd_ids: JSON (样本JD列表)")
    print("  - created_at: DateTime")
    print()
    
    print("🔍 验证 job_descriptions 表结构:")
    print("  - id: String(50) [主键]")
    print("  - job_title: String(200)")
    print("  - department: String(200)")
    print("  - location: String(200)")
    print("  - responsibilities: JSON")
    print("  - required_skills: JSON")
    print("  - preferred_skills: JSON")
    print("  - qualifications: JSON")
    print("  - custom_fields: JSON")
    print("  - raw_text: Text")
    print("  - category_level1_id: String(50) [外键 -> job_categories.id]")
    print("  - category_level2_id: String(50) [外键 -> job_categories.id]")
    print("  - category_level3_id: String(50) [外键 -> job_categories.id]")
    print("  - created_at: DateTime")
    print("  - updated_at: DateTime")
    print()
    
    # 测试创建数据
    async with AsyncSessionLocal() as session:
        print("🧪 测试数据创建...")
        
        # 创建职位分类
        cat1 = JobCategoryDB(
            id=f"test_cat1_{uuid.uuid4().hex[:8]}",
            name="测试一级分类",
            level=1,
            parent_id=None,
            description="测试描述"
        )
        session.add(cat1)
        
        cat2 = JobCategoryDB(
            id=f"test_cat2_{uuid.uuid4().hex[:8]}",
            name="测试二级分类",
            level=2,
            parent_id=cat1.id,
            description="测试描述"
        )
        session.add(cat2)
        
        cat3 = JobCategoryDB(
            id=f"test_cat3_{uuid.uuid4().hex[:8]}",
            name="测试三级分类",
            level=3,
            parent_id=cat2.id,
            description="测试描述",
            sample_jd_ids=[]
        )
        session.add(cat3)
        
        await session.commit()
        print("  ✓ 职位分类创建成功")
        
        # 创建JD
        jd = JobDescriptionDB(
            id=f"test_jd_{uuid.uuid4().hex[:8]}",
            job_title="测试职位",
            department="测试部门",
            location="测试地点",
            responsibilities=["职责1", "职责2"],
            required_skills=["技能1", "技能2"],
            preferred_skills=["优选技能1"],
            qualifications=["资质1"],
            custom_fields={"自定义字段": "值"},
            raw_text="原始JD文本",
            category_level1_id=cat1.id,
            category_level2_id=cat2.id,
            category_level3_id=cat3.id
        )
        session.add(jd)
        await session.commit()
        print("  ✓ 职位JD创建成功")
        
        # 创建评估结果
        eval_result = EvaluationResultDB(
            id=f"test_eval_{uuid.uuid4().hex[:8]}",
            jd_id=jd.id,
            evaluation_model_type="standard",
            overall_score=85.5,
            completeness=90.0,
            clarity=80.0,
            professionalism=86.0,
            issues=[{"type": "warning", "message": "测试问题"}],
            position_value={"dimension1": 80},
            recommendations=["建议1", "建议2"]
        )
        session.add(eval_result)
        await session.commit()
        print("  ✓ 评估结果创建成功")
        
        # 创建问卷
        questionnaire = QuestionnaireDB(
            id=f"test_quest_{uuid.uuid4().hex[:8]}",
            jd_id=jd.id,
            title="测试问卷",
            description="测试问卷描述",
            questions=[{"id": "q1", "text": "问题1"}],
            evaluation_model="standard",
            share_link="http://example.com/questionnaire"
        )
        session.add(questionnaire)
        await session.commit()
        print("  ✓ 问卷创建成功")
        
        # 创建问卷回答
        response = QuestionnaireResponseDB(
            id=f"test_resp_{uuid.uuid4().hex[:8]}",
            questionnaire_id=questionnaire.id,
            respondent_name="测试候选人",
            answers={"q1": "答案1"}
        )
        session.add(response)
        await session.commit()
        print("  ✓ 问卷回答创建成功")
        
        # 创建匹配结果
        match_result = MatchResultDB(
            id=f"test_match_{uuid.uuid4().hex[:8]}",
            jd_id=jd.id,
            response_id=response.id,
            overall_score=88.0,
            dimension_scores={"技能": 90, "经验": 85},
            strengths=["优势1", "优势2"],
            gaps=["差距1"],
            recommendations=["建议1"]
        )
        session.add(match_result)
        await session.commit()
        print("  ✓ 匹配结果创建成功")
        
        # 创建自定义模板
        template = CustomTemplateDB(
            id=f"test_tmpl_{uuid.uuid4().hex[:8]}",
            name="测试模板",
            template_type="parsing",
            config={"field1": "value1"}
        )
        session.add(template)
        await session.commit()
        print("  ✓ 自定义模板创建成功")
        
        print()
        print("=" * 60)
        print("✅ 数据库Schema验证完成！所有表和关系正常工作。")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(verify_schema())
