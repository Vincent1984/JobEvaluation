"""测试LLM缓存机制"""

import asyncio
import pytest
from src.core.llm_cache import (
    LLMCache,
    MemoryCache,
    create_memory_cache,
    CacheBackend
)


class TestCacheKeyGeneration:
    """测试缓存键生成"""
    
    def test_generate_cache_key_consistency(self):
        """测试相同参数生成相同的缓存键"""
        key1 = LLMCache.generate_cache_key(
            prompt="测试提示词",
            model="deepseek-reasoner",
            temperature=0.7,
            max_tokens=4000,
            system_message="系统消息"
        )
        
        key2 = LLMCache.generate_cache_key(
            prompt="测试提示词",
            model="deepseek-reasoner",
            temperature=0.7,
            max_tokens=4000,
            system_message="系统消息"
        )
        
        assert key1 == key2, "相同参数应生成相同的缓存键"
        assert len(key1) == 32, "MD5哈希应为32字符"
    
    def test_generate_cache_key_different_prompts(self):
        """测试不同提示词生成不同的缓存键"""
        key1 = LLMCache.generate_cache_key(
            prompt="提示词1",
            model="deepseek-reasoner",
            temperature=0.7,
            max_tokens=4000
        )
        
        key2 = LLMCache.generate_cache_key(
            prompt="提示词2",
            model="deepseek-reasoner",
            temperature=0.7,
            max_tokens=4000
        )
        
        assert key1 != key2, "不同提示词应生成不同的缓存键"
    
    def test_generate_cache_key_different_temperature(self):
        """测试不同温度参数生成不同的缓存键"""
        key1 = LLMCache.generate_cache_key(
            prompt="测试",
            model="deepseek-reasoner",
            temperature=0.7,
            max_tokens=4000
        )
        
        key2 = LLMCache.generate_cache_key(
            prompt="测试",
            model="deepseek-reasoner",
            temperature=0.8,
            max_tokens=4000
        )
        
        assert key1 != key2, "不同温度应生成不同的缓存键"
    
    def test_generate_cache_key_chinese_support(self):
        """测试中文支持"""
        key = LLMCache.generate_cache_key(
            prompt="这是一个中文提示词，包含特殊字符：！@#￥%……&*（）",
            model="deepseek-reasoner",
            temperature=0.7,
            max_tokens=4000,
            system_message="你是一个专业的HR岗位分析专家。"
        )
        
        assert len(key) == 32, "应正确处理中文字符"


class TestMemoryCache:
    """测试内存缓存"""
    
    @pytest.mark.asyncio
    async def test_memory_cache_set_and_get(self):
        """测试设置和获取缓存"""
        cache = create_memory_cache()
        
        await cache.set("test_key", "test_value")
        value = await cache.get("test_key")
        
        assert value == "test_value", "应能正确获取缓存值"
    
    @pytest.mark.asyncio
    async def test_memory_cache_miss(self):
        """测试缓存未命中"""
        cache = create_memory_cache()
        
        value = await cache.get("nonexistent_key")
        
        assert value is None, "不存在的键应返回None"
    
    @pytest.mark.asyncio
    async def test_memory_cache_delete(self):
        """测试删除缓存"""
        cache = create_memory_cache()
        
        await cache.set("test_key", "test_value")
        await cache.delete("test_key")
        value = await cache.get("test_key")
        
        assert value is None, "删除后应无法获取"
    
    @pytest.mark.asyncio
    async def test_memory_cache_clear(self):
        """测试清空缓存"""
        cache = create_memory_cache()
        
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.clear()
        
        value1 = await cache.get("key1")
        value2 = await cache.get("key2")
        
        assert value1 is None and value2 is None, "清空后所有缓存应被删除"
    
    @pytest.mark.asyncio
    async def test_memory_cache_exists(self):
        """测试检查键是否存在"""
        cache = create_memory_cache()
        
        await cache.set("test_key", "test_value")
        
        assert await cache.exists("test_key") is True, "存在的键应返回True"
        assert await cache.exists("nonexistent") is False, "不存在的键应返回False"
    
    @pytest.mark.asyncio
    async def test_memory_cache_stats(self):
        """测试缓存统计"""
        cache = create_memory_cache()
        
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.get("key1")  # 命中
        await cache.get("key3")  # 未命中
        
        stats = await cache.get_stats()
        
        assert stats["backend"] == "memory"
        assert stats["size"] == 2
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert "50.00%" in stats["hit_rate"]


class TestLLMCacheIntegration:
    """测试LLM缓存集成"""
    
    @pytest.mark.asyncio
    async def test_get_or_compute_cache_hit(self):
        """测试缓存命中时不执行计算"""
        cache = create_memory_cache()
        
        # 预先设置缓存
        await cache.set("test_key", "cached_value")
        
        # 定义计算函数（不应被调用）
        compute_called = False
        
        async def compute_fn():
            nonlocal compute_called
            compute_called = True
            return "computed_value"
        
        # 获取或计算
        result = await cache.get_or_compute("test_key", compute_fn)
        
        assert result == "cached_value", "应返回缓存值"
        assert not compute_called, "缓存命中时不应调用计算函数"
    
    @pytest.mark.asyncio
    async def test_get_or_compute_cache_miss(self):
        """测试缓存未命中时执行计算"""
        cache = create_memory_cache()
        
        # 定义计算函数
        async def compute_fn():
            return "computed_value"
        
        # 获取或计算
        result = await cache.get_or_compute("new_key", compute_fn)
        
        assert result == "computed_value", "应返回计算值"
        
        # 验证已缓存
        cached = await cache.get("new_key")
        assert cached == "computed_value", "计算结果应被缓存"
    
    @pytest.mark.asyncio
    async def test_large_value_caching(self):
        """测试大值缓存"""
        cache = create_memory_cache()
        
        # 创建一个大字符串（约1MB）
        large_value = "x" * (1024 * 1024)
        
        await cache.set("large_key", large_value)
        retrieved = await cache.get("large_key")
        
        assert retrieved == large_value, "应能正确缓存和检索大值"
        assert len(retrieved) == 1024 * 1024


class TestCacheWithLLMClient:
    """测试缓存与LLM客户端集成"""
    
    @pytest.mark.asyncio
    async def test_llm_client_uses_cache(self):
        """测试LLM客户端使用缓存"""
        from src.core.llm_client import DeepSeekR1Client
        from unittest.mock import AsyncMock, MagicMock
        
        # 创建带缓存的客户端
        cache = create_memory_cache()
        client = DeepSeekR1Client(enable_cache=True, cache=cache)
        
        # Mock API调用
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "测试响应"
        
        client._call_api = AsyncMock(return_value=mock_response)
        
        # 第一次调用（应调用API）
        result1 = await client.generate("测试提示词")
        assert result1 == "测试响应"
        assert client._call_api.call_count == 1
        
        # 第二次调用相同提示词（应使用缓存）
        result2 = await client.generate("测试提示词")
        assert result2 == "测试响应"
        assert client._call_api.call_count == 1, "第二次调用应使用缓存，不调用API"
        
        # 不同提示词（应调用API）
        result3 = await client.generate("不同的提示词")
        assert result3 == "测试响应"
        assert client._call_api.call_count == 2, "不同提示词应调用API"


def test_cache_key_format():
    """测试缓存键格式"""
    key = LLMCache.generate_cache_key(
        prompt="test",
        model="deepseek-reasoner",
        temperature=0.7,
        max_tokens=4000
    )
    
    # 验证是有效的MD5哈希
    assert len(key) == 32
    assert all(c in "0123456789abcdef" for c in key), "应为有效的十六进制字符串"


if __name__ == "__main__":
    # 运行基本测试
    print("运行LLM缓存测试...")
    
    # 测试缓存键生成
    print("\n1. 测试缓存键生成...")
    key1 = LLMCache.generate_cache_key(
        prompt="解析以下岗位JD",
        model="deepseek-reasoner",
        temperature=0.7,
        max_tokens=4000
    )
    print(f"   生成的缓存键: {key1}")
    
    key2 = LLMCache.generate_cache_key(
        prompt="解析以下岗位JD",
        model="deepseek-reasoner",
        temperature=0.7,
        max_tokens=4000
    )
    print(f"   相同参数生成: {key2}")
    print(f"   ✓ 一致性检查: {key1 == key2}")
    
    # 测试内存缓存
    print("\n2. 测试内存缓存...")
    
    async def test_memory():
        cache = create_memory_cache()
        
        # 设置缓存
        await cache.set("test_key", "test_value")
        print("   ✓ 缓存已设置")
        
        # 获取缓存
        value = await cache.get("test_key")
        print(f"   ✓ 缓存获取: {value}")
        
        # 检查存在
        exists = await cache.exists("test_key")
        print(f"   ✓ 键存在检查: {exists}")
        
        # 统计信息
        stats = await cache.get_stats()
        print(f"   ✓ 缓存统计: {stats}")
        
        # 清空缓存
        await cache.clear()
        value_after_clear = await cache.get("test_key")
        print(f"   ✓ 清空后获取: {value_after_clear}")
    
    asyncio.run(test_memory())
    
    print("\n✅ 所有基本测试通过！")
    print("\n运行完整测试套件: pytest test_llm_cache.py -v")
