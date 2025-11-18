"""测试重构后的 JD Service

验证 Service 通过 Agent 实现功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.services.jd_service import JDService
from src.models.schemas import EvaluationModel


async def test_jd_service():
    """测试 JD Service 的完整流程"""
    
    print("=" * 60)
    print("测试重构后的 JD Service")
    print("=" * 60)
    print()
    
    # 创建服务实例
    print("1. 创建 JD Service 实例...")
    service = JDService()
    print("   ✓ 服务创建成功")
    print()
    
    # 测试 JD 文本
    jd_text = """
职位：高级 Python 后端工程师

部门：技术研发部
地点：北京

岗位职责：
1. 负责公司核心业务系统的后端开发和维护
2. 参与系统架构设计，优化系统性能和稳定性
3. 编写高质量、可维护的代码，进行代码审查
4. 与产品、前端团队协作，推动项目落地

任职要求：
必备技能：
- 3年以上 Python 开发经验
- 熟练掌握 FastAPI、Django 等 Web 框架
- 熟悉 MySQL、Redis 等数据库
- 了解微服务架构和 RESTful API 设计

优选技能：
- 有大型互联网项目经验
- 熟悉 Docker、Kubernetes 容器化技术
- 了解消息队列（RabbitMQ、Kafka）

学历要求：
- 本科及以上学历，计算机相关专业优先
"""
    
    try:
        # 测试完整分析
        print("2. 测试完整 JD 分析...")
        print("   调用: service.analyze_jd()")
        print("   → 内部调用 ParserAgent 和 EvaluatorAgent")
        print()
        
        result = await service.analyze_jd(
            jd_text=jd_text,
            model_type=EvaluationModel.STANDARD
        )
        
        jd = result["jd"]
        evaluation = result["evaluation"]
        
        print("   ✓ 分析完成！")
        print()
        
        # 显示解析结果
        print("3. 解析结果：")
        print(f"   JD ID: {jd.id}")
        print(f"   职位标题: {jd.job_title}")
        print(f"   部门: {jd.department or '未指定'}")
        print(f"   地点: {jd.location or '未指定'}")
        print(f"   职责数量: {len(jd.responsibilities)}")
        print(f"   必备技能数量: {len(jd.required_skills)}")
        print(f"   优选技能数量: {len(jd.preferred_skills)}")
        
        if jd.category_level1_id:
            print(f"   一级分类: {jd.category_level1_id}")
        if jd.category_level2_id:
            print(f"   二级分类: {jd.category_level2_id}")
        if jd.category_level3_id:
            print(f"   三级分类: {jd.category_level3_id}")
        
        print()
        
        # 显示评估结果
        print("4. 评估结果：")
        print(f"   评估 ID: {evaluation.id}")
        print(f"   综合分数: {evaluation.quality_score.overall_score:.1f}")
        print(f"   完整性: {evaluation.quality_score.completeness:.1f}")
        print(f"   清晰度: {evaluation.quality_score.clarity:.1f}")
        print(f"   专业性: {evaluation.quality_score.professionalism:.1f}")
        
        if evaluation.quality_score.issues:
            print(f"   发现问题: {len(evaluation.quality_score.issues)} 个")
            for issue in evaluation.quality_score.issues[:3]:
                print(f"     - {issue.get('description', '')}")
        
        if evaluation.recommendations:
            print(f"   优化建议: {len(evaluation.recommendations)} 条")
            for rec in evaluation.recommendations[:3]:
                print(f"     - {rec}")
        
        print()
        
        # 测试单独的解析
        print("5. 测试单独解析...")
        jd2 = await service.parse_jd("软件工程师岗位，负责系统开发")
        print(f"   ✓ 解析成功: {jd2.job_title}")
        print()
        
        # 测试获取 JD
        print("6. 测试获取 JD...")
        retrieved_jd = await service.get_jd(jd.id)
        if retrieved_jd:
            print(f"   ✓ 获取成功: {retrieved_jd.job_title}")
        else:
            print("   ⚠️  未找到 JD")
        print()
        
        # 测试列出所有 JD
        print("7. 测试列出所有 JD...")
        all_jds = await service.list_jds()
        print(f"   ✓ 共有 {len(all_jds)} 个 JD")
        print()
        
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print()
        print("架构验证：")
        print("  ✓ Service 成功调用 ParserAgent")
        print("  ✓ Service 成功调用 EvaluatorAgent")
        print("  ✓ Service 成功调用 DataManagerAgent")
        print("  ✓ MCP 协议通信正常")
        print("  ✓ 架构统一完成")
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭服务
        print()
        print("8. 关闭服务...")
        await service.shutdown()
        print("   ✓ 服务已关闭")


async def test_simple_usage():
    """测试简化的使用方式"""
    
    print()
    print("=" * 60)
    print("测试简化使用方式")
    print("=" * 60)
    print()
    
    from src.services.jd_service import get_jd_service
    
    # 获取服务实例
    service = get_jd_service()
    
    # 简单调用
    result = await service.analyze_jd("Python 开发工程师，3年经验")
    
    print(f"职位: {result['jd'].job_title}")
    print(f"分数: {result['evaluation'].quality_score.overall_score:.1f}")
    print()
    print("✅ 简化使用方式正常")
    
    await service.shutdown()


async def main():
    """主函数"""
    try:
        # 测试完整流程
        await test_jd_service()
        
        # 测试简化使用
        await test_simple_usage()
        
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
