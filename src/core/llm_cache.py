"""LLM调用缓存机制

支持两种缓存策略：
1. 内存缓存（MemoryCache）- 快速但不持久
2. Redis缓存（RedisCache）- 持久化且支持分布式

缓存键生成策略：
- 基于prompt、model、temperature等参数生成唯一哈希
- 使用MD5确保键的一致性和长度可控
"""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import timedelta

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """缓存后端抽象基类"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None表示永不过期
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str):
        """删除缓存"""
        pass
    
    @abstractmethod
    async def clear(self):
        """清空所有缓存"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        pass


class MemoryCache(CacheBackend):
    """内存缓存实现
    
    特点：
    - 快速访问
    - 进程内共享
    - 不持久化（重启后丢失）
    - 适合开发和测试环境
    """
    
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._hits = 0
        self._misses = 0
        logger.info("内存缓存初始化完成")
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        value = self._cache.get(key)
        if value is not None:
            self._hits += 1
            logger.debug(f"缓存命中: {key[:8]}...")
        else:
            self._misses += 1
            logger.debug(f"缓存未命中: {key[:8]}...")
        return value
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        """设置缓存值（内存缓存不支持TTL）"""
        self._cache[key] = value
        logger.debug(f"缓存已保存: {key[:8]}... (size={len(value)})")
    
    async def delete(self, key: str):
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"缓存已删除: {key[:8]}...")
    
    async def clear(self):
        """清空所有缓存"""
        count = len(self._cache)
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info(f"内存缓存已清空: {count}个条目")
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return key in self._cache
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            "backend": "memory",
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "keys_sample": list(self._cache.keys())[:10]
        }


class RedisCache(CacheBackend):
    """Redis缓存实现
    
    特点：
    - 持久化存储
    - 支持TTL自动过期
    - 支持分布式部署
    - 适合生产环境
    """
    
    def __init__(
        self,
        redis_client,
        key_prefix: str = "llm_cache:",
        default_ttl: int = 3600  # 默认1小时
    ):
        """初始化Redis缓存
        
        Args:
            redis_client: Redis客户端实例
            key_prefix: 键前缀，用于命名空间隔离
            default_ttl: 默认过期时间（秒）
        """
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        logger.info(f"Redis缓存初始化完成: prefix={key_prefix}, ttl={default_ttl}s")
    
    def _make_key(self, key: str) -> str:
        """生成带前缀的完整键"""
        return f"{self.key_prefix}{key}"
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        full_key = self._make_key(key)
        try:
            value = await self.redis.get(full_key)
            if value:
                logger.debug(f"Redis缓存命中: {key[:8]}...")
                return value.decode('utf-8') if isinstance(value, bytes) else value
            else:
                logger.debug(f"Redis缓存未命中: {key[:8]}...")
                return None
        except Exception as e:
            logger.error(f"Redis获取失败: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        """设置缓存值"""
        full_key = self._make_key(key)
        ttl = ttl or self.default_ttl
        
        try:
            await self.redis.set(full_key, value, ex=ttl)
            logger.debug(f"Redis缓存已保存: {key[:8]}... (ttl={ttl}s, size={len(value)})")
        except Exception as e:
            logger.error(f"Redis保存失败: {e}")
    
    async def delete(self, key: str):
        """删除缓存"""
        full_key = self._make_key(key)
        try:
            await self.redis.delete(full_key)
            logger.debug(f"Redis缓存已删除: {key[:8]}...")
        except Exception as e:
            logger.error(f"Redis删除失败: {e}")
    
    async def clear(self):
        """清空所有缓存（仅清空带前缀的键）"""
        try:
            pattern = f"{self.key_prefix}*"
            cursor = 0
            count = 0
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self.redis.delete(*keys)
                    count += len(keys)
                if cursor == 0:
                    break
            
            logger.info(f"Redis缓存已清空: {count}个条目")
        except Exception as e:
            logger.error(f"Redis清空失败: {e}")
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        full_key = self._make_key(key)
        try:
            return await self.redis.exists(full_key) > 0
        except Exception as e:
            logger.error(f"Redis检查存在失败: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            # 统计带前缀的键数量
            pattern = f"{self.key_prefix}*"
            cursor = 0
            count = 0
            sample_keys = []
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                count += len(keys)
                if len(sample_keys) < 10:
                    sample_keys.extend([k.decode('utf-8') if isinstance(k, bytes) else k for k in keys[:10]])
                if cursor == 0:
                    break
            
            # 获取Redis信息
            info = await self.redis.info()
            
            return {
                "backend": "redis",
                "size": count,
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory_human", "unknown"),
                "keys_sample": sample_keys[:10]
            }
        except Exception as e:
            logger.error(f"Redis统计失败: {e}")
            return {
                "backend": "redis",
                "error": str(e)
            }


class LLMCache:
    """LLM缓存管理器
    
    提供统一的缓存接口，支持多种后端实现
    """
    
    def __init__(self, backend: CacheBackend):
        """初始化缓存管理器
        
        Args:
            backend: 缓存后端实现
        """
        self.backend = backend
        logger.info(f"LLM缓存管理器初始化: backend={backend.__class__.__name__}")
    
    @staticmethod
    def generate_cache_key(
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_message: Optional[str] = None
    ) -> str:
        """生成缓存键
        
        基于所有影响输出的参数生成唯一哈希键
        
        Args:
            prompt: 用户提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            system_message: 系统消息
            
        Returns:
            MD5哈希字符串（32字符）
        """
        # 构建缓存键字符串
        cache_components = {
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "system_message": system_message or ""
        }
        
        # 序列化为JSON（确保顺序一致）
        cache_str = json.dumps(cache_components, sort_keys=True, ensure_ascii=False)
        
        # 生成MD5哈希
        cache_key = hashlib.md5(cache_str.encode('utf-8')).hexdigest()
        
        logger.debug(f"生成缓存键: {cache_key} (prompt_len={len(prompt)})")
        return cache_key
    
    async def get(self, cache_key: str) -> Optional[str]:
        """获取缓存结果"""
        return await self.backend.get(cache_key)
    
    async def set(self, cache_key: str, result: str, ttl: Optional[int] = None):
        """保存缓存结果"""
        await self.backend.set(cache_key, result, ttl)
    
    async def delete(self, cache_key: str):
        """删除缓存"""
        await self.backend.delete(cache_key)
    
    async def clear(self):
        """清空所有缓存"""
        await self.backend.clear()
    
    async def exists(self, cache_key: str) -> bool:
        """检查缓存是否存在"""
        return await self.backend.exists(cache_key)
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return await self.backend.get_stats()
    
    async def get_or_compute(
        self,
        cache_key: str,
        compute_fn,
        ttl: Optional[int] = None
    ) -> str:
        """获取缓存或计算新值
        
        如果缓存存在则返回缓存值，否则调用compute_fn计算并缓存
        
        Args:
            cache_key: 缓存键
            compute_fn: 计算函数（async callable）
            ttl: 缓存过期时间
            
        Returns:
            结果值
        """
        # 尝试从缓存获取
        cached_value = await self.get(cache_key)
        if cached_value is not None:
            logger.debug(f"使用缓存结果: {cache_key[:8]}...")
            return cached_value
        
        # 计算新值
        logger.debug(f"计算新值: {cache_key[:8]}...")
        result = await compute_fn()
        
        # 保存到缓存
        await self.set(cache_key, result, ttl)
        
        return result


# 工厂函数
def create_memory_cache() -> LLMCache:
    """创建内存缓存实例"""
    backend = MemoryCache()
    return LLMCache(backend)


def create_redis_cache(
    redis_client,
    key_prefix: str = "llm_cache:",
    default_ttl: int = 3600
) -> LLMCache:
    """创建Redis缓存实例
    
    Args:
        redis_client: Redis客户端
        key_prefix: 键前缀
        default_ttl: 默认过期时间（秒）
    """
    backend = RedisCache(redis_client, key_prefix, default_ttl)
    return LLMCache(backend)
