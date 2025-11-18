"""DeepSeek-R1客户端测试"""

import asyncio
import pytest
from src.core.llm_client import DeepSeekR1Client, LLMException, LLMConnectionError


# 基础功能测试
async def test_basic_generate():
    """测试基础文本生成"""
    client = DeepSeekR1Client()
    
    prompt = "请用一句话介绍什么是HR。"
    response = await client.generate(prompt, max_tokens=100)
    
    print(f"\n基础生成测试:")
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    
    assert response is not None
    assert len(response) > 0
    assert "HR" in response or "人力资源" in response


async def test_json_generate():
    """测试JSON格式生成"""
    client = DeepSeekR1Client()
    
    prompt = """
    请分析以下岗位JD并提取结构化信息。
    
    岗位JD:
    职位：Python后端工程师
    部门：技术部
    职责：负责后端系统开发和维护
    要求：3年以上Python开发经验，熟悉Django/FastAPI
    
    请按照以下JSON格式返回：
    {
        "job_title": "职位名称",
        "department": "部门",
        "responsibilities": ["职责1", "职责2"],
        "requirements": ["要求1", "要求2"]
    }
    """
    
    response = await client.generate_json(prompt, max_tokens=500)
    
    print(f"\nJSON生成测试:")
    print(f"Response: {response}")
    
    assert isinstance(response, dict)
    assert "job_title" in response
    assert "department" in response


async def test_cache():
    """测试缓存功能"""
    client = DeepSeekR1Client(enable_cache=True)
    
    prompt = "什么是岗位JD？"
    
    # 第一次调用
    print("\n缓存测试 - 第一次调用:")
    response1 = await client.generate(prompt, max_tokens=100)
    print(f"Response 1: {response1[:100]}...")
    
    # 第二次调用（应该从缓存返回）
    print("\n缓存测试 - 第二次调用（从缓存）:")
    response2 = await client.generate(prompt, max_tokens=100)
    print(f"Response 2: {response2[:100]}...")
    
    # 验证缓存
    assert response1 == response2
    
    # 检查缓存统计
    stats = client.get_cache_stats()
    print(f"\n缓存统计: {stats}")
    assert stats["enabled"] is True
    assert stats["size"] > 0


async def test_batch_generate():
    """测试批量生成"""
    client = DeepSeekR1Client()
    
    prompts = [
        "什么是岗位JD？用一句话回答。",
        "什么是候选人匹配度？用一句话回答。",
        "什么是职位评估？用一句话回答。"
    ]
    
    print(f"\n批量生成测试 - {len(prompts)}个请求:")
    responses = await client.batch_generate(
        prompts,
        max_tokens=100,
        max_concurrent=2
    )
    
    assert len(responses) == len(prompts)
    
    for i, (prompt, response) in enumerate(zip(prompts, responses), 1):
        print(f"\n请求 {i}:")
        print(f"Prompt: {prompt}")
        print(f"Response: {response[:100]}...")
        assert response is not None
        assert len(response) > 0


async def test_stream_generate():
    """测试流式生成"""
    client = DeepSeekR1Client()
    
    prompt = "请详细介绍岗位JD分析的重要性。"
    
    print(f"\n流式生成测试:")
    print(f"Prompt: {prompt}")
    print("Response (streaming): ", end="")
    
    full_response = ""
    async for chunk in client.generate_stream(prompt, max_tokens=200):
        print(chunk, end="", flush=True)
        full_response += chunk
    
    print()  # 换行
    
    assert len(full_response) > 0


async def test_error_handling():
    """测试错误处理"""
    # 使用无效的API密钥
    client = DeepSeekR1Client(
        api_key="invalid_key",
        max_retries=1
    )
    
    print("\n错误处理测试 - 无效API密钥:")
    
    try:
        await client.generate("测试", max_tokens=10)
        assert False, "应该抛出异常"
    except LLMException as e:
        print(f"捕获到预期的异常: {type(e).__name__}: {e}")
        assert True


async def test_custom_system_message():
    """测试自定义系统消息"""
    client = DeepSeekR1Client()
    
    prompt = "介绍一下你自己。"
    system_message = "你是一个专业的招聘顾问，专注于技术岗位招聘。"
    
    response = await client.generate(
        prompt,
        system_message=system_message,
        max_tokens=150
    )
    
    print(f"\n自定义系统消息测试:")
    print(f"System: {system_message}")
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    
    assert response is not None
    assert len(response) > 0


async def test_temperature_control():
    """测试温度参数控制"""
    client = DeepSeekR1Client()
    
    prompt = "列举3个Python Web框架。"
    
    # 低温度（更确定性）
    print("\n温度控制测试 - 低温度 (0.1):")
    response_low = await client.generate(prompt, temperature=0.1, max_tokens=100)
    print(f"Response: {response_low}")
    
    # 高温度（更随机）
    print("\n温度控制测试 - 高温度 (0.9):")
    response_high = await client.generate(prompt, temperature=0.9, max_tokens=100)
    print(f"Response: {response_high}")
    
    assert response_low is not None
    assert response_high is not None


async def test_reasoning_prompt():
    """测试推理型Prompt（DeepSeek-R1特性）"""
    client = DeepSeekR1Client()
    
    prompt = """
    作为HR专家，请评估以下岗位JD的质量。
    
    <thinking>
    评估步骤：
    1. 检查完整性 - JD是否包含所有必要信息？
    2. 评估清晰度 - 职责和要求是否明确？
    3. 分析专业性 - 语言表达是否专业？
    4. 综合打分 - 基于以上分析给出总分
    </thinking>
    
    岗位JD:
    职位：高级Java工程师
    职责：开发系统
    要求：会Java
    
    请提供详细的评估结果（JSON格式）：
    {
        "completeness_score": 0-100,
        "clarity_score": 0-100,
        "professionalism_score": 0-100,
        "overall_score": 0-100,
        "issues": ["问题1", "问题2"],
        "suggestions": ["建议1", "建议2"]
    }
    """
    
    print("\n推理型Prompt测试:")
    response = await client.generate_json(prompt, max_tokens=1000)
    
    print(f"Response: {response}")
    
    assert isinstance(response, dict)
    if "error" not in response:
        assert "overall_score" in response or "completeness_score" in response


# 运行所有测试
async def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("DeepSeek-R1客户端测试套件")
    print("=" * 80)
    
    tests = [
        ("基础文本生成", test_basic_generate),
        ("JSON格式生成", test_json_generate),
        ("缓存功能", test_cache),
        ("批量生成", test_batch_generate),
        ("流式生成", test_stream_generate),
        ("错误处理", test_error_handling),
        ("自定义系统消息", test_custom_system_message),
        ("温度参数控制", test_temperature_control),
        ("推理型Prompt", test_reasoning_prompt),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n{'=' * 80}")
            print(f"运行测试: {name}")
            print(f"{'=' * 80}")
            await test_func()
            print(f"\n✓ 测试通过: {name}")
            passed += 1
        except Exception as e:
            print(f"\n✗ 测试失败: {name}")
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'=' * 80}")
    print(f"测试总结")
    print(f"{'=' * 80}")
    print(f"通过: {passed}/{len(tests)}")
    print(f"失败: {failed}/{len(tests)}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(run_all_tests())
