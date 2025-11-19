"""测试更新后的数据模型"""

import sys
sys.path.insert(0, '.')

from datetime import datetime
from src.models.schemas import (
    Company, 
    CategoryTag, 
    JobCategory, 
    JobDescription, 
    EvaluationResult,
    ManualModification,
    DimensionContribution,
    QualityScore
)

def test_company_model():
    """测试Company模型"""
    company = Company(
        id="comp_001",
        name="测试科技公司"
    )
    assert company.id == "comp_001"
    assert company.name == "测试科技公司"
    assert company.created_at is not None
    assert company.updated_at is not None
    print("✓ Company模型测试通过")

def test_category_tag_model():
    """测试CategoryTag模型"""
    tag = CategoryTag(
        id="tag_001",
        category_id="cat_003",
        name="高战略重要性",
        tag_type="战略重要性",
        description="该岗位对企业战略目标实现具有重要影响"
    )
    assert tag.id == "tag_001"
    assert tag.category_id == "cat_003"
    assert tag.tag_type == "战略重要性"
    print("✓ CategoryTag模型测试通过")

def test_job_category_model():
    """测试JobCategory模型"""
    # 测试第一层级分类
    category_l1 = JobCategory(
        id="cat_001",
        company_id="comp_001",
        name="技术类",
        level=1,
        parent_id=None
    )
    assert category_l1.company_id == "comp_001"
    assert category_l1.level == 1
    assert len(category_l1.tags) == 0
    print("✓ JobCategory第一层级测试通过")
    
    # 测试第三层级分类（带标签）
    tag = CategoryTag(
        id="tag_001",
        category_id="cat_003",
        name="高战略重要性",
        tag_type="战略重要性",
        description="重要岗位"
    )
    
    category_l3 = JobCategory(
        id="cat_003",
        company_id="comp_001",
        name="后端工程师",
        level=3,
        parent_id="cat_002",
        tags=[tag],
        sample_jd_ids=["jd_001"]
    )
    assert category_l3.level == 3
    assert len(category_l3.tags) == 1
    assert category_l3.tags[0].name == "高战略重要性"
    print("✓ JobCategory第三层级（带标签）测试通过")
    
    # 测试验证规则：非第三层级不能有标签
    try:
        invalid_category = JobCategory(
            id="cat_002",
            company_id="comp_001",
            name="研发",
            level=2,
            parent_id="cat_001",
            tags=[tag]  # 第二层级不应该有标签
        )
        print("✗ 验证规则测试失败：应该抛出异常")
    except ValueError as e:
        assert "只有第三层级分类才能添加标签" in str(e)
        print("✓ JobCategory验证规则测试通过")

def test_job_description_model():
    """测试JobDescription模型"""
    tag = CategoryTag(
        id="tag_001",
        category_id="cat_003",
        name="高战略重要性",
        tag_type="战略重要性",
        description="重要岗位"
    )
    
    jd = JobDescription(
        id="jd_001",
        job_title="高级Python工程师",
        raw_text="招聘高级Python工程师...",
        category_level1_id="cat_001",
        category_level2_id="cat_002",
        category_level3_id="cat_003",
        category_tags=[tag]
    )
    assert jd.id == "jd_001"
    assert len(jd.category_tags) == 1
    assert jd.category_tags[0].name == "高战略重要性"
    print("✓ JobDescription模型测试通过")

def test_evaluation_result_model():
    """测试EvaluationResult模型"""
    quality_score = QualityScore(
        overall_score=85.0,
        completeness=90.0,
        clarity=80.0,
        professionalism=85.0
    )
    
    dimension_contrib = DimensionContribution(
        jd_content=40.0,
        evaluation_template=30.0,
        category_tags=30.0
    )
    
    eval_result = EvaluationResult(
        id="eval_001",
        jd_id="jd_001",
        model_type="standard",
        quality_score=quality_score,
        overall_score=85.0,
        company_value="高价值",
        is_core_position=True,
        dimension_contributions=dimension_contrib,
        is_manually_modified=False
    )
    
    assert eval_result.overall_score == 85.0
    assert eval_result.company_value == "高价值"
    assert eval_result.is_core_position == True
    assert eval_result.dimension_contributions.jd_content == 40.0
    assert eval_result.is_manually_modified == False
    assert len(eval_result.manual_modifications) == 0
    print("✓ EvaluationResult模型测试通过")

def test_manual_modification_model():
    """测试ManualModification模型"""
    modification = ManualModification(
        modified_fields={"overall_score": 90.0, "company_value": "高价值"},
        original_values={"overall_score": 85.0, "company_value": "中价值"},
        reason="根据业务需求调整评分"
    )
    
    assert modification.modified_fields["overall_score"] == 90.0
    assert modification.original_values["overall_score"] == 85.0
    assert modification.reason == "根据业务需求调整评分"
    print("✓ ManualModification模型测试通过")

def test_dimension_contribution_model():
    """测试DimensionContribution模型"""
    contrib = DimensionContribution(
        jd_content=40.0,
        evaluation_template=30.0,
        category_tags=30.0
    )
    
    assert contrib.jd_content == 40.0
    assert contrib.evaluation_template == 30.0
    assert contrib.category_tags == 30.0
    print("✓ DimensionContribution模型测试通过")

if __name__ == "__main__":
    print("开始测试更新后的数据模型...\n")
    
    test_company_model()
    test_category_tag_model()
    test_job_category_model()
    test_job_description_model()
    test_evaluation_result_model()
    test_manual_modification_model()
    test_dimension_contribution_model()
    
    print("\n所有测试通过！✓")
