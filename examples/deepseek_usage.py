"""DeepSeek-R1客户端使用示例"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.llm_client import DeepSeekR1Client


async def example_basic_usage():
    """示例1: 基础使用"""
    print("\n" + "=" * 80)
    print("示例1: 基础文本生成")
    print("=" * 80)
    
    client = DeepSeekR1Client()
    
    prompt = "请简要介绍岗位JD（Job Description）的重要性。"
    response = await client.generate(prompt, max_tokens=200)
    
    print(f"Prompt: {prompt}")
    print(f"\nResponse:\n{response}")


async def example_json_parsing():
    """示例2: JSON格式解析"""
    print("\n" + "=" * 80)
    print("示例2: 解析岗位JD为JSON格式")
    print("=" * 80)
    
    client = DeepSeekR1Client()
    
    jd_text = """
    职位名称：高级Python后端工程师
    所属部门：技术研发部
    工作地点：北京
    
    岗位职责：
    1. 负责公司核心业务系统的后端开发和维护
    2. 参与系统架构设计和技术方案评审
    3. 优化系统性能，提升用户体验
    
    任职要求：
    1. 本科及以上学历，计算机相关专业
    2. 5年以上Python开发经验
    3. 精通Django或FastAPI框架
    4. 熟悉MySQL、Redis等数据库
    5. 具有良好的团队协作能力
    """
    
    prompt = f"""
    请解析以下岗位JD，提取结构化信息。
    
    岗位JD:
    {jd_text}
    
    请返回JSON格式：
    {{
        "job_title": "职位名称",
        "department": "部门",
        "location": "工作地点",
        "responsibilities": ["职责1", "职责2", ...],
        "requirements": ["要求1", "要求2", ...]
    }}
    """
    
    response = await client.generate_json(prompt, max_tokens=800)
    
    print(f"原始JD:\n{jd_text}")
    print(f"\n解析结果:")
    import json
    print(json.dumps(response, ensure_ascii=False, indent=2))


async def example_quality_evaluation():
    """示例3: JD质量评估"""
    print("\n" + "=" * 80)
    print("示例3: 评估岗位JD质量")
    print("=" * 80)
    
    client = DeepSeekR1Client()
    
    jd_text = """
    职位：工程师
    要求：会编程
    """
    
    prompt = f"""
    作为HR专家，请评估以下岗位JD的质量。
    
    <thinking>
    评估维度：
    1. 完整性：是否包含职位名称、职责、要求等基本信息
    2. 清晰度：描述是否明确具体
    3. 专业性：语言表达是否专业规范
    </thinking>
    
    岗位JD:
    {jd_text}
    
    请返回JSON格式的评估结果：
    {{
        "overall_score": 0-100,
        "completeness": 0-100,
        "clarity": 0-100,
        "professionalism": 0-100,
        "issues": ["问题1", "问题2"],
        "suggestions": ["建议1", "建议2"]
    }}
    """
    
    response = await client.generate_json(prompt, max_tokens=1000)
    
    print(f"待评估JD:\n{jd_text}")
    print(f"\n评估结果:")
    import json
    print(json.dumps(response, ensure_ascii=False, indent=2))


async def example_batch_processing():
    """示例4: 批量处理多个JD"""
    print("\n" + "=" * 80)
    print("示例4: 批量处理多个岗位JD")
    print("=" * 80)
    
    client = DeepSeekR1Client()
    
    jds = [
        "职位：Python工程师，要求3年经验",
        "职位：Java架构师，要求5年以上经验，精通Spring",
        "职位：前端开发，熟悉React和Vue"
    ]
    
    prompts = [
        f"请提取以下JD的职位名称和核心要求（一句话）：{jd}"
        for jd in jds
    ]
    
    print(f"批量处理 {len(jds)} 个JD...")
    responses = await client.batch_generate(
        prompts,
        max_tokens=100,
        max_concurrent=3
    )
    
    for i, (jd, response) in enumerate(zip(jds, responses), 1):
        print(f"\nJD {i}: {jd}")
        print(f"分析: {response}")


async def example_streaming():
    """示例5: 流式输出"""
    print("\n" + "=" * 80)
    print("示例5: 流式生成优化建议")
    print("=" * 80)
    
    client = DeepSeekR1Client()
    
    prompt = """
    请为以下简单的岗位JD提供详细的优化建议：
    
    职位：开发工程师
    要求：会编程
    
    请从完整性、清晰度、吸引力等方面提供具体的改进建议。
    """
    
    print("生成中（流式输出）：\n")
    async for chunk in client.generate_stream(prompt, max_tokens=500):
        print(chunk, end="", flush=True)
    print("\n")


async def example_with_cache():
    """示例6: 使用缓存"""
    print("\n" + "=" * 80)
    print("示例6: 缓存功能演示")
    print("=" * 80)
    
    client = DeepSeekR1Client(enable_cache=True)
    
    prompt = "什么是岗位JD？请用一句话回答。"
    
    # 第一次调用
    print("第一次调用（从API）...")
    import time
    start = time.time()
    response1 = await client.generate(prompt, max_tokens=100)
    time1 = time.time() - start
    print(f"响应: {response1}")
    print(f"耗时: {time1:.2f}秒")
    
    # 第二次调用（从缓存）
    print("\n第二次调用（从缓存）...")
    start = time.time()
    response2 = await client.generate(prompt, max_tokens=100)
    time2 = time.time() - start
    print(f"响应: {response2}")
    print(f"耗时: {time2:.2f}秒")
    
    print(f"\n缓存加速: {time1/time2:.1f}x")
    
    # 缓存统计
    stats = client.get_cache_stats()
    print(f"缓存统计: {stats['size']} 条记录")


async def example_error_handling():
    """示例7: 错误处理"""
    print("\n" + "=" * 80)
    print("示例7: 错误处理和重试机制")
    print("=" * 80)
    
    from src.core.llm_client import LLMException
    
    # 正常调用
    client = DeepSeekR1Client(max_retries=2)
    
    try:
        print("尝试正常调用...")
        response = await client.generate(
            "测试错误处理",
            max_tokens=50
        )
        print(f"成功: {response[:100]}...")
    except LLMException as e:
        print(f"捕获异常: {type(e).__name__}: {e}")


async def main():
    """运行所有示例"""
    print("=" * 80)
    print("DeepSeek-R1客户端使用示例")
    print("=" * 80)
    
    examples = [
        example_basic_usage,
        example_json_parsing,
        example_quality_evaluation,
        example_batch_processing,
        example_streaming,
        example_with_cache,
        example_error_handling,
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"\n示例执行出错: {e}")
            import traceback
            traceback.print_exc()
        
        # 暂停一下
        await asyncio.sleep(1)
    
    print("\n" + "=" * 80)
    print("所有示例执行完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
