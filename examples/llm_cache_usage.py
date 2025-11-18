"""LLM缓存使用示例

演示如何使用内存缓存和Redis缓存
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.llm_client import DeepSeekR1Client
from src.core.llm_cache import (
    LLMCache,
    create_memory_cache,
    create_redis_cache
)


async def example_memory_cache():
    """示例1: 使用内存缓存"""
    print("=" * 60)
    print("示例1: 使用内存缓存")
    print("=" * 60)
    
    # 创建带内存缓存的客户端
    cache = create_memory_cache()
    client = DeepSeekR1Client(enable_cache=True, cache=cache)
    
    print("\n第一次调用（将调用API并缓存结果）...")
    prompt = "请用一句话介绍什么是岗位JD"
    
    try:
        result1 = await client.generate(prompt, max_tokens=100)
        print(f"响应: {result1[:100]}...")
    except Exception as e:
        print(f"API调用失败（这是正常的，因为可能没有配置真实API）: {e}")
        # 手动设置缓存用于演示
        cache_key = LLMCache.generate_cache_key(
            prompt=prompt,
            model=client.model,
            temperature=0.7,
            max_tokens=100,
            system_message="你是一个专业的HR岗位分析专家。"
        )
        await cache.set(cache_key, "岗位JD（Job Description）是描述职位职责、要求和期望的文档。")
        print("已设置模拟缓存数据")
    
    print("\n第二次调用相同提示词（将从缓存返回）...")
    try:
        result2 = await client.generate(prompt, max_tokens=100)
        print(f"响应: {result2[:100]}...")
    except Exception as e:
        print(f"错误: {e}")
    
    # 查看缓存统计
    print("\n缓存统计:")
    stats = await client.get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def example_redis_cache():
    """示例2: 使用Redis缓存（需要Redis服务）"""
    print("\n" + "=" * 60)
    print("示例2: 使用Redis缓存")
    print("=" * 60)
    
    try:
        import redis.asyncio as aioredis
        from src.core.config import settings
        
        # 连接Redis
        print(f"\n连接Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        redis_client = await aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            encoding="utf-8",
            decode_responses=True
        )
        
        # 测试连接
        await redis_client.ping()
        print("✓ Redis连接成功")
        
        # 创建Redis缓存
        cache = create_redis_cache(
            redis_client,
            key_prefix="llm_cache:",
            default_ttl=3600  # 1小时过期
        )
        
        # 创建客户端
        client = DeepSeekR1Client(enable_cache=True, cache=cache)
        
        print("\n使用Redis缓存调用LLM...")
        prompt = "什么是岗位评估？"
        
        # 手动设置缓存用于演示
        cache_key = LLMCache.generate_cache_key(
            prompt=prompt,
            model=client.model,
            temperature=0.7,
            max_tokens=100,
            system_message="你是一个专业的HR岗位分析专家。"
        )
        
        await cache.set(
            cache_key,
            "岗位评估是系统地确定岗位相对价值的过程，用于建立公平的薪酬体系。",
            ttl=3600
        )
        print("✓ 已设置Redis缓存")
        
        # 从缓存获取
        result = await cache.get(cache_key)
        print(f"从Redis获取: {result}")
        
        # 查看统计
        print("\nRedis缓存统计:")
        stats = await cache.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 清理
        await redis_client.close()
        print("\n✓ Redis连接已关闭")
        
    except ImportError:
        print("\n⚠ redis.asyncio未安装，跳过Redis示例")
        print("安装: pip install redis")
    except Exception as e:
        print(f"\n⚠ Redis示例失败: {e}")
        print("请确保Redis服务正在运行")


async def example_cache_key_generation():
    """示例3: 缓存键生成"""
    print("\n" + "=" * 60)
    print("示例3: 缓存键生成机制")
    print("=" * 60)
    
    # 相同参数生成相同的键
    print("\n1. 相同参数生成相同的键:")
    key1 = LLMCache.generate_cache_key(
        prompt="解析JD",
        model="deepseek-reasoner",
        temperature=0.7,
        max_tokens=4000
    )
    key2 = LLMCache.generate_cache_key(
        prompt="解析JD",
        model="deepseek-reasoner",
        temperature=0.7,
        max_tokens=4000
    )
    print(f"   键1: {key1}")
    print(f"   键2: {key2}")
    print(f"   相同: {key1 == key2}")
    
    # 不同参数生成不同的键
    print("\n2. 不同提示词生成不同的键:")
    key3 = LLMCache.generate_cache_key(
        prompt="评估JD质量",
        model="deepseek-reasoner",
        temperature=0.7,
        max_tokens=4000
    )
    print(f"   键3: {key3}")
    print(f"   与键1不同: {key1 != key3}")
    
    # 不同温度生成不同的键
    print("\n3. 不同温度生成不同的键:")
    key4 = LLMCache.generate_cache_key(
        prompt="解析JD",
        model="deepseek-reasoner",
        temperature=0.8,  # 不同的温度
        max_tokens=4000
    )
    print(f"   键4: {key4}")
    print(f"   与键1不同: {key1 != key4}")
    
    # 中文支持
    print("\n4. 中文提示词支持:")
    key5 = LLMCache.generate_cache_key(
        prompt="请分析这个岗位JD的质量，包括完整性、清晰度和专业性。",
        model="deepseek-reasoner",
        temperature=0.7,
        max_tokens=4000,
        system_message="你是一个专业的HR岗位分析专家。"
    )
    print(f"   键5: {key5}")
    print(f"   长度: {len(key5)} (MD5固定32字符)")


async def example_get_or_compute():
    """示例4: get_or_compute模式"""
    print("\n" + "=" * 60)
    print("示例4: get_or_compute模式")
    print("=" * 60)
    
    cache = create_memory_cache()
    
    # 模拟一个耗时的计算
    async def expensive_computation():
        print("   执行耗时计算...")
        await asyncio.sleep(0.1)  # 模拟延迟
        return "计算结果"
    
    print("\n第一次调用（执行计算）:")
    result1 = await cache.get_or_compute("compute_key", expensive_computation)
    print(f"   结果: {result1}")
    
    print("\n第二次调用（使用缓存）:")
    result2 = await cache.get_or_compute("compute_key", expensive_computation)
    print(f"   结果: {result2}")
    print("   注意：第二次没有执行计算")


async def example_cache_management():
    """示例5: 缓存管理"""
    print("\n" + "=" * 60)
    print("示例5: 缓存管理")
    print("=" * 60)
    
    cache = create_memory_cache()
    
    # 添加多个缓存项
    print("\n添加缓存项...")
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.set("key3", "value3")
    
    stats = await cache.get_stats()
    print(f"缓存大小: {stats['size']}")
    
    # 检查存在
    print("\n检查键是否存在:")
    print(f"  key1存在: {await cache.exists('key1')}")
    print(f"  key999存在: {await cache.exists('key999')}")
    
    # 删除单个键
    print("\n删除key2...")
    await cache.delete("key2")
    print(f"  key2存在: {await cache.exists('key2')}")
    
    # 清空所有缓存
    print("\n清空所有缓存...")
    await cache.clear()
    stats = await cache.get_stats()
    print(f"缓存大小: {stats['size']}")


async def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("LLM缓存机制使用示例")
    print("=" * 60)
    
    # 运行示例
    await example_cache_key_generation()
    await example_memory_cache()
    await example_get_or_compute()
    await example_cache_management()
    await example_redis_cache()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
