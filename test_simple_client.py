"""测试 Simple MCP Client"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from src.mcp.simple_client import get_simple_mcp_client
from src.models.schemas import EvaluationModel


async def test_parse_jd():
    """测试 JD 解析"""
    print("=" * 60)
    print("测试 JD 解析")
    print("=" * 60)
    
    client = get_simple_mcp_client()
    
    test_jd = """
职位：高级Python工程师

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
- 本科及以上学历，计算机相关专业优先
"""
    
    try:
        jd = await client.parse_jd(test_jd)
        
        print(f"\n✅ 解析成功！")
        print(f"职位标题: {jd.job_title}")
        print(f"部门: {jd.department}")
        print(f"地点: {jd.location}")
        print(f"\n职责 ({len(jd.responsibilities)} 条):")
        for i, resp in enumerate(jd.responsibilities[:3], 1):
            print(f"  {i}. {resp}")
        print(f"\n必备技能 ({len(jd.required_skills)} 个):")
        for skill in jd.required_skills[:3]:
            print(f"  - {skill}")
        
        return jd
    
    except Exception as e:
        print(f"\n❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_analyze_jd():
    """测试完整分析"""
    print("\n" + "=" * 60)
    print("测试完整分析（解析 + 评估）")
    print("=" * 60)
    
    client = get_simple_mcp_client()
    
    test_jd = """
职位：高级Python工程师

岗位职责：
1. 负责后端开发
2. 优化系统性能

任职要求：
- 3年以上Python经验
- 熟悉FastAPI框架
"""
    
    try:
        result = await client.analyze_jd(test_jd, EvaluationModel.STANDARD)
        
        jd = result["jd"]
        evaluation = result["evaluation"]
        
        print(f"\n✅ 分析成功！")
        print(f"\n【JD 信息】")
        print(f"职位标题: {jd.job_title}")
        print(f"职责数量: {len(jd.responsibilities)}")
        print(f"技能数量: {len(jd.required_skills)}")
        
        print(f"\n【质量评估】")
        print(f"综合分数: {evaluation.quality_score.overall_score:.1f}")
        print(f"完整性: {evaluation.quality_score.completeness:.1f}")
        print(f"清晰度: {evaluation.quality_score.clarity:.1f}")
        print(f"专业性: {evaluation.quality_score.professionalism:.1f}")
        
        if evaluation.recommendations:
            print(f"\n【优化建议】")
            for i, rec in enumerate(evaluation.recommendations[:3], 1):
                print(f"  {i}. {rec}")
        
        return result
    
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主测试函数"""
    print("\n🚀 开始测试 Simple MCP Client\n")
    
    # 测试 1: JD 解析
    jd = await test_parse_jd()
    
    if jd:
        # 测试 2: 完整分析
        result = await test_analyze_jd()
        
        if result:
            print("\n" + "=" * 60)
            print("✅ 所有测试通过！")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️ 分析测试失败")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️ 解析测试失败")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
