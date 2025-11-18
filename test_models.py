"""测试数据模型验证规则"""

from src.models.schemas import (
    JobCategory, JobDescription, EvaluationResult, 
    Questionnaire, Question, QuestionnaireResponse,
    MatchResult, CustomTemplate, QualityScore,
    EvaluationModel, QuestionType
)
from datetime import datetime
import sys


def test_job_category_validation():
    """测试JobCategory验证规则"""
    print("测试JobCategory验证规则...")
    
    # 测试1: 第三层级可以有1-2个样本JD
    try:
        cat1 = JobCategory(
            id="cat_001",
            name="后端工程师",
            level=3,
            parent_id="cat_parent",
            sample_jd_ids=["jd_001"]
        )
        print("✓ 第三层级1个样本JD - 通过")
    except Exception as e:
        print(f"✗ 第三层级1个样本JD - 失败: {e}")
        return False
    
    try:
        cat2 = JobCategory(
            id="cat_002",
            name="前端工程师",
            level=3,
            parent_id="cat_parent",
            sample_jd_ids=["jd_001", "jd_002"]
        )
        print("✓ 第三层级2个样本JD - 通过")
    except Exception as e:
        print(f"✗ 第三层级2个样本JD - 失败: {e}")
        return False
    
    # 测试2: 第三层级不能超过2个样本JD
    try:
        cat3 = JobCategory(
            id="cat_003",
            name="测试工程师",
            level=3,
            parent_id="cat_parent",
            sample_jd_ids=["jd_001", "jd_002", "jd_003"]
        )
        print("✗ 第三层级3个样本JD应该失败但通过了")
        return False
    except ValueError as e:
        print(f"✓ 第三层级3个样本JD - 正确拒绝: {e}")
    
    # 测试3: 非第三层级不能有样本JD
    try:
        cat4 = JobCategory(
            id="cat_004",
            name="技术类",
            level=1,
            sample_jd_ids=["jd_001"]
        )
        print("✗ 一级分类有样本JD应该失败但通过了")
        return False
    except ValueError as e:
        print(f"✓ 一级分类不能有样本JD - 正确拒绝: {e}")
    
    # 测试4: 一级分类不能有父级
    try:
        cat5 = JobCategory(
            id="cat_005",
            name="技术类",
            level=1,
            parent_id="should_not_exist"
        )
        print("✗ 一级分类有父级应该失败但通过了")
        return False
    except ValueError as e:
        print(f"✓ 一级分类不能有父级 - 正确拒绝: {e}")
    
    # 测试5: 二三级分类必须有父级
    try:
        cat6 = JobCategory(
            id="cat_006",
            name="研发",
            level=2
        )
        print("✗ 二级分类无父级应该失败但通过了")
        return False
    except ValueError as e:
        print(f"✓ 二级分类必须有父级 - 正确拒绝: {e}")
    
    print("✓ JobCategory所有验证规则测试通过\n")
    return True


def test_job_description_model():
    """测试JobDescription模型"""
    print("测试JobDescription模型...")
    
    try:
        jd = JobDescription(
            id="jd_001",
            job_title="高级Python工程师",
            department="技术部",
            location="北京",
            responsibilities=["开发后端服务", "优化系统性能"],
            required_skills=["Python", "FastAPI", "SQL"],
            preferred_skills=["Docker", "K8s"],
            qualifications=["本科及以上", "3年以上经验"],
            raw_text="招聘高级Python工程师...",
            category_level1_id="cat_tech",
            category_level2_id="cat_dev",
            category_level3_id="cat_backend"
        )
        print(f"✓ JobDescription创建成功: {jd.job_title}")
        print(f"  - 分类: L1={jd.category_level1_id}, L2={jd.category_level2_id}, L3={jd.category_level3_id}")
        print("✓ JobDescription模型测试通过\n")
        return True
    except Exception as e:
        print(f"✗ JobDescription创建失败: {e}\n")
        return False


def test_evaluation_result_model():
    """测试EvaluationResult模型"""
    print("测试EvaluationResult模型...")
    
    try:
        quality_score = QualityScore(
            overall_score=85.0,
            completeness=90.0,
            clarity=80.0,
            professionalism=85.0,
            issues=[
                {"type": "clarity", "severity": "medium", "description": "职责描述不够具体"}
            ]
        )
        
        eval_result = EvaluationResult(
            id="eval_001",
            jd_id="jd_001",
            model_type=EvaluationModel.STANDARD,
            quality_score=quality_score,
            position_value={"影响力": 85.0, "沟通": 75.0},
            recommendations=["建议补充薪资范围", "职责描述可以更具体"]
        )
        print(f"✓ EvaluationResult创建成功: 综合分数={eval_result.quality_score.overall_score}")
        print(f"  - 评估模型: {eval_result.model_type}")
        print(f"  - 建议数量: {len(eval_result.recommendations)}")
        print("✓ EvaluationResult模型测试通过\n")
        return True
    except Exception as e:
        print(f"✗ EvaluationResult创建失败: {e}\n")
        return False


def test_questionnaire_model():
    """测试Questionnaire模型"""
    print("测试Questionnaire模型...")
    
    try:
        question1 = Question(
            id="q_001",
            question_text="您有多少年Python开发经验？",
            question_type=QuestionType.SINGLE_CHOICE,
            options=["1年以下", "1-3年", "3-5年", "5年以上"],
            dimension="技能评估",
            weight=1.0
        )
        
        question2 = Question(
            id="q_002",
            question_text="请描述您最复杂的项目经验",
            question_type=QuestionType.OPEN_ENDED,
            dimension="经验评估",
            weight=0.8
        )
        
        questionnaire = Questionnaire(
            id="quest_001",
            jd_id="jd_001",
            title="高级Python工程师评估问卷",
            description="请如实填写以下问题",
            questions=[question1, question2],
            evaluation_model=EvaluationModel.STANDARD,
            share_link="http://localhost:8501/questionnaire/quest_001"
        )
        print(f"✓ Questionnaire创建成功: {questionnaire.title}")
        print(f"  - 问题数量: {len(questionnaire.questions)}")
        print(f"  - 评估模型: {questionnaire.evaluation_model}")
        print("✓ Questionnaire模型测试通过\n")
        return True
    except Exception as e:
        print(f"✗ Questionnaire创建失败: {e}\n")
        return False


def test_match_result_model():
    """测试MatchResult模型"""
    print("测试MatchResult模型...")
    
    try:
        match_result = MatchResult(
            id="match_001",
            jd_id="jd_001",
            response_id="resp_001",
            overall_score=85.0,
            dimension_scores={"技能匹配": 90.0, "经验匹配": 80.0, "资质匹配": 85.0},
            strengths=["Python经验丰富", "有大型项目经验", "学习能力强"],
            gaps=["缺少K8s经验", "团队管理经验不足"],
            recommendations=["建议学习容器化技术", "可以参与团队管理培训"]
        )
        print(f"✓ MatchResult创建成功: 综合分数={match_result.overall_score}")
        print(f"  - 优势: {len(match_result.strengths)}项")
        print(f"  - 差距: {len(match_result.gaps)}项")
        print(f"  - 建议: {len(match_result.recommendations)}条")
        print("✓ MatchResult模型测试通过\n")
        return True
    except Exception as e:
        print(f"✗ MatchResult创建失败: {e}\n")
        return False


def test_custom_template_model():
    """测试CustomTemplate模型"""
    print("测试CustomTemplate模型...")
    
    try:
        template = CustomTemplate(
            id="tmpl_001",
            name="技术岗位解析模板",
            template_type="parsing",
            config={
                "custom_fields": ["技术栈", "团队规模", "汇报关系"],
                "required_fields": ["技术栈"]
            }
        )
        print(f"✓ CustomTemplate创建成功: {template.name}")
        print(f"  - 模板类型: {template.template_type}")
        print(f"  - 配置项: {len(template.config)}个")
        print("✓ CustomTemplate模型测试通过\n")
        return True
    except Exception as e:
        print(f"✗ CustomTemplate创建失败: {e}\n")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试Pydantic数据模型")
    print("=" * 60 + "\n")
    
    tests = [
        test_job_category_validation,
        test_job_description_model,
        test_evaluation_result_model,
        test_questionnaire_model,
        test_match_result_model,
        test_custom_template_model
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ 测试执行异常: {e}\n")
            results.append(False)
    
    print("=" * 60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    if all(results):
        print("\n✓ 所有数据模型测试通过！")
        return 0
    else:
        print("\n✗ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
