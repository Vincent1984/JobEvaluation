"""MVP功能测试"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from src.services.jd_service import jd_service
from src.models.schemas import EvaluationModel


async def test_jd_analysis():
    """测试JD分析功能"""
    
    print("=" * 60)
    print("🧪 测试岗位JD分析器 MVP")
    print("=" * 60)
    print()
    
    # 测试JD文本
    test_jd = """职位：高级Python后端工程师

部门：技术研发部
地点：北京

岗位职责：
1. 负责公司核心业务系统的后端开发和维护
2. 参与系统架构设计，优化系统性能和稳定性
3. 编写高质量、可维护的代码，进行代码审查

任职要求：
必备技能：
- 3年以上Python开发经验
- 熟练掌握FastAPI、Django等Web框架
- 熟悉MySQL、Redis等数据库

优选技能：
- 有大型互联网项目经验
- 熟悉Docker、Kubernetes容器化技术

学历要求：
- 本科及以上学历，计算机相关专业优先"""
    
    print("📝 测试JD:")
    print(test_jd)
    print()
    print("🔍 开始分析...")
    print()
    
    try:
        # 执行分析
        result = await jd_service.analyze_jd(test_jd, EvaluationModel.STANDARD)
        
        jd = result["jd"]
        evaluation = result["evaluation"]
        
        print("✅ 分析完成！")
        print()
        print("=" * 60)
        print("📊 解析结果")
        print("=" * 60)
        print(f"职位标题: {jd.job_title}")
        print(f"部门: {jd.department or '未指定'}")
        print(f"地点: {jd.location or '未指定'}")
        print()
        
        print("职责描述:")
        for i, resp in enumerate(jd.responsibilities, 1):
            print(f"  {i}. {resp}")
        print()
        
        print("必备技能:")
        for skill in jd.required_skills:
            print(f"  - {skill}")
        print()
        
        print("优选技能:")
        for skill in jd.preferred_skills:
            print(f"  - {skill}")
        print()
        
        print("=" * 60)
        print("⭐ 质量评估")
        print("=" * 60)
        print(f"综合分数: {evaluation.quality_score.overall_score:.1f}/100")
        print(f"完整性: {evaluation.quality_score.completeness:.1f}/100")
        print(f"清晰度: {evaluation.quality_score.clarity:.1f}/100")
        print(f"专业性: {evaluation.quality_score.professionalism:.1f}/100")
        print()
        
        if evaluation.quality_score.issues:
            print("发现的问题:")
            for issue in evaluation.quality_score.issues:
                severity = issue.get("severity", "medium")
                symbol = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🔵"
                print(f"  {symbol} {issue.get('description', '')}")
            print()
        
        print("=" * 60)
        print("💡 优化建议")
        print("=" * 60)
        if evaluation.recommendations:
            for i, rec in enumerate(evaluation.recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("暂无改进建议")
        print()
        
        print("=" * 60)
        print("✅ 测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print()
    print("⚠️  注意: 此测试需要配置有效的API密钥")
    print("请确保 .env 文件中已配置 OPENAI_API_KEY")
    print()
    
    input("按回车键开始测试...")
    print()
    
    # 运行测试
    asyncio.run(test_jd_analysis())


if __name__ == "__main__":
    main()
