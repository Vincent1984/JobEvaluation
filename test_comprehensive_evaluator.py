"""测试综合评估器功能"""

import asyncio
import json
from datetime import datetime
from src.agents.evaluator_agent import ComprehensiveEvaluator, StandardEvaluationModel
from src.models.schemas import CategoryTag
from src.core.llm_client import DeepSeekR1Client


async def test_comprehensive_evaluator():
    """测试综合评估器"""
    print("=" * 60)
    print("测试综合评估器功能")
    print("=" * 60)
    
    # 创建模拟的LLM客户端
    class MockLLMClient:
        async def generate_json(self, prompt, temperature=0.3):
            """模拟LLM响应"""
            if "分析以下分类标签" in prompt:
                # 标签分析响应
                return {
                    "has_tags": True,
                    "strategic_importance": "高",
                    "business_value": "高",
                    "skill_scarcity": "中",
                    "market_competition": "高",
                    "development_potential": "高",
                    "risk_level": "中",
                    "impact_summary": "该岗位具有高战略重要性和高业务价值，对企业核心业务有重要影响",
                    "value_adjustment": 8,
                    "core_position_indicator": 0.85
                }
            elif "整合以下三个维度" in prompt:
                # 维度整合响应
                return {
                    "integrated_score": 88,
                    "dimension_synergy": "JD内容质量高，评估模板匹配度好，分类标签显示高战略价值，三个维度协同良好",
                    "key_insights": [
                        "该岗位对企业战略目标实现具有重要影响",
                        "技能要求与市场需求高度匹配",
                        "岗位价值评估结果一致性高"
                    ],
                    "conflicts": [],
                    "recommendations": [
                        "建议作为核心岗位重点培养",
                        "可以适当提高薪资待遇以吸引优秀人才"
                    ]
                }
            elif "评估以下岗位JD的质量" in prompt:
                # 基础评估响应
                return {
                    "dimension_scores": {
                        "完整性": 85,
                        "清晰度": 80,
                        "专业性": 82
                    },
                    "overall_score": 82,
                    "analysis": "JD整体质量良好，信息完整，描述清晰",
                    "issues": [
                        {"type": "缺失信息", "severity": "medium", "description": "建议补充薪资范围"}
                    ]
                }
            return {}
    
    # 创建测试数据
    jd_data = {
        "id": "jd_test_001",
        "job_title": "高级后端工程师",
        "department": "技术部",
        "responsibilities": [
            "负责后端系统架构设计和开发",
            "优化系统性能和稳定性",
            "指导初级工程师"
        ],
        "required_skills": [
            "Python",
            "Django/FastAPI",
            "MySQL/PostgreSQL",
            "Redis"
        ],
        "qualifications": [
            "本科及以上学历",
            "5年以上后端开发经验"
        ]
    }
    
    category_tags = [
        CategoryTag(
            id="tag_001",
            category_id="cat_003",
            name="高战略重要性",
            tag_type="战略重要性",
            description="该岗位对企业战略目标实现具有重要影响，评估时应提高岗位价值评级",
            created_at=datetime.now()
        ),
        CategoryTag(
            id="tag_002",
            category_id="cat_003",
            name="高业务价值",
            tag_type="业务价值",
            description="该岗位直接支撑核心业务，对业务成功至关重要",
            created_at=datetime.now()
        ),
        CategoryTag(
            id="tag_003",
            category_id="cat_003",
            name="高市场竞争度",
            tag_type="市场竞争度",
            description="该岗位在人才市场竞争激烈，需要有竞争力的薪酬",
            created_at=datetime.now()
        )
    ]
    
    # 创建综合评估器
    llm_client = MockLLMClient()
    evaluator = ComprehensiveEvaluator(llm_client)
    evaluation_model = StandardEvaluationModel()
    
    print("\n1. 测试综合评估功能")
    print("-" * 60)
    
    try:
        result = await evaluator.comprehensive_evaluate(
            jd_data,
            evaluation_model,
            category_tags
        )
        
        print(f"✓ 综合评估成功")
        print(f"  - 综合质量分数: {result.get('overall_score', 0)}")
        print(f"  - 企业价值评级: {result.get('company_value', '未知')}")
        print(f"  - 是否核心岗位: {result.get('is_core_position', False)}")
        print(f"  - 维度贡献度: {json.dumps(result.get('dimension_contributions', {}), ensure_ascii=False)}")
        
        # 验证必要字段
        assert "company_value" in result, "缺少company_value字段"
        assert "is_core_position" in result, "缺少is_core_position字段"
        assert "dimension_contributions" in result, "缺少dimension_contributions字段"
        assert "tag_analysis" in result, "缺少tag_analysis字段"
        assert "integrated_analysis" in result, "缺少integrated_analysis字段"
        
        print(f"✓ 所有必要字段都存在")
        
    except Exception as e:
        print(f"✗ 综合评估失败: {e}")
        raise
    
    print("\n2. 测试标签分析功能")
    print("-" * 60)
    
    try:
        tag_analysis = await evaluator._analyze_category_tags(category_tags, jd_data)
        
        print(f"✓ 标签分析成功")
        print(f"  - 战略重要性: {tag_analysis.get('strategic_importance', '未知')}")
        print(f"  - 业务价值: {tag_analysis.get('business_value', '未知')}")
        print(f"  - 技能稀缺性: {tag_analysis.get('skill_scarcity', '未知')}")
        print(f"  - 核心岗位指标: {tag_analysis.get('core_position_indicator', 0)}")
        print(f"  - 价值调整分数: {tag_analysis.get('value_adjustment', 0)}")
        
        assert tag_analysis.get("has_tags") == True, "has_tags应该为True"
        assert "strategic_importance" in tag_analysis, "缺少strategic_importance字段"
        assert "core_position_indicator" in tag_analysis, "缺少core_position_indicator字段"
        
        print(f"✓ 标签分析字段验证通过")
        
    except Exception as e:
        print(f"✗ 标签分析失败: {e}")
        raise
    
    print("\n3. 测试企业价值判断")
    print("-" * 60)
    
    try:
        base_evaluation = {
            "overall_score": 82,
            "dimension_scores": {"完整性": 85, "清晰度": 80, "专业性": 82}
        }
        
        company_value = await evaluator._determine_company_value(
            base_evaluation,
            tag_analysis,
            jd_data
        )
        
        print(f"✓ 企业价值判断成功: {company_value}")
        assert company_value in ["高价值", "中价值", "低价值"], f"企业价值评级无效: {company_value}"
        print(f"✓ 企业价值评级有效")
        
    except Exception as e:
        print(f"✗ 企业价值判断失败: {e}")
        raise
    
    print("\n4. 测试核心岗位判断")
    print("-" * 60)
    
    try:
        is_core = await evaluator._determine_core_position(
            tag_analysis,
            base_evaluation,
            jd_data
        )
        
        print(f"✓ 核心岗位判断成功: {is_core}")
        assert isinstance(is_core, bool), "is_core_position应该是布尔值"
        print(f"✓ 核心岗位判断类型正确")
        
    except Exception as e:
        print(f"✗ 核心岗位判断失败: {e}")
        raise
    
    print("\n5. 测试维度贡献度计算")
    print("-" * 60)
    
    try:
        contributions = evaluator._calculate_dimension_contributions(
            base_evaluation,
            tag_analysis
        )
        
        print(f"✓ 维度贡献度计算成功")
        print(f"  - JD内容: {contributions.get('jd_content', 0)}%")
        print(f"  - 评估模板: {contributions.get('evaluation_template', 0)}%")
        print(f"  - 分类标签: {contributions.get('category_tags', 0)}%")
        
        total = contributions.get('jd_content', 0) + contributions.get('evaluation_template', 0) + contributions.get('category_tags', 0)
        print(f"  - 总计: {total}%")
        
        assert "jd_content" in contributions, "缺少jd_content字段"
        assert "evaluation_template" in contributions, "缺少evaluation_template字段"
        assert "category_tags" in contributions, "缺少category_tags字段"
        
        print(f"✓ 维度贡献度字段验证通过")
        
    except Exception as e:
        print(f"✗ 维度贡献度计算失败: {e}")
        raise
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_comprehensive_evaluator())
