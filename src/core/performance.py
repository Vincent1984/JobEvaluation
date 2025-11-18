"""性能优化模块

提供以下优化功能：
1. LLM调用优化 - 批量处理、并发控制、智能缓存
2. 数据库查询优化 - 连接池、批量操作、查询缓存
3. 文件处理优化 - 并行解析、流式处理
4. 缓存策略优化 - 多级缓存、预热、失效策略
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable, TypeVar, Coroutine
from functools import wraps
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class PerformanceMetrics:
    """性能指标"""
    operation_name: str
    total_calls: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    errors: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update(self, execution_time: float, error: bool = False, cache_hit: bool = False):
        """更新指标"""
        self.total_calls += 1
        if not error:
            self.total_time += execution_time
            self.avg_time = self.total_time / (self.total_calls - self.errors)
            self.min_time = min(self.min_time, execution_time)
            self.max_time = max(self.max_time, execution_time)
        else:
            self.errors += 1
        
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        cache_total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / cache_total * 100) if cache_total > 0 else 0
        
        return {
            "operation": self.operation_name,
            "total_calls": self.total_calls,
            "avg_time_ms": round(self.avg_time * 1000, 2),
            "min_time_ms": round(self.min_time * 1000, 2) if self.min_time != float('inf') else 0,
            "max_time_ms": round(self.max_time * 1000, 2),
            "errors": self.errors,
            "error_rate": f"{(self.errors / self.total_calls * 100):.2f}%" if self.total_calls > 0 else "0%",
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": f"{hit_rate:.2f}%",
            "last_updated": self.last_updated.isoformat()
        }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = defaultdict(
            lambda: PerformanceMetrics(operation_name="unknown")
        )
        self._lock = asyncio.Lock()
    
    async def record(
        self,
        operation: str,
        execution_time: float,
        error: bool = False,
        cache_hit: bool = False
    ):
        """记录性能指标"""
        async with self._lock:
            if operation not in self.metrics:
                self.metrics[operation] = PerformanceMetrics(operation_name=operation)
            self.metrics[operation].update(execution_time, error, cache_hit)
    
    async def get_metrics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """获取性能指标"""
        async with self._lock:
            if operation:
                metric = self.metrics.get(operation)
                return metric.to_dict() if metric else {}
            else:
                return {
                    op: metric.to_dict()
                    for op, metric in self.metrics.items()
                }
    
    async def reset(self, operation: Optional[str] = None):
        """重置指标"""
        async with self._lock:
            if operation:
                if operation in self.metrics:
                    del self.metrics[operation]
            else:
                self.metrics.clear()


# 全局性能监控器
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: str):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            error = False
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise
            finally:
                execution_time = time.time() - start_time
                await performance_monitor.record(
                    operation=operation_name,
                    execution_time=execution_time,
                    error=error
                )
        return wrapper
    return decorator


class BatchProcessor:
    """批量处理器 - 优化批量操作性能"""
    
    def __init__(
        self,
        batch_size: int = 10,
        max_concurrent: int = 5,
        timeout: float = 60.0
    ):
        """初始化批量处理器
        
        Args:
            batch_size: 批次大小
            max_concurrent: 最大并发数
            timeout: 超时时间（秒）
        """
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(
        self,
        items: List[T],
        process_fn: Callable[[T], Coroutine[Any, Any, Any]],
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> List[Any]:
        """批量处理项目
        
        Args:
            items: 待处理项目列表
            process_fn: 处理函数（异步）
            on_progress: 进度回调函数
            
        Returns:
            处理结果列表
        """
        results = []
        total = len(items)
        
        async def process_with_semaphore(item: T, index: int) -> Any:
            async with self.semaphore:
                try:
                    result = await asyncio.wait_for(
                        process_fn(item),
                        timeout=self.timeout
                    )
                    if on_progress:
                        on_progress(index + 1, total)
                    return result
                except asyncio.TimeoutError:
                    logger.error(f"处理超时: item {index}")
                    return {"error": "timeout", "index": index}
                except Exception as e:
                    logger.error(f"处理失败: item {index}, error: {e}")
                    return {"error": str(e), "index": index}
        
        # 分批处理
        for batch_start in range(0, total, self.batch_size):
            batch_end = min(batch_start + self.batch_size, total)
            batch = items[batch_start:batch_end]
            
            logger.info(f"处理批次: {batch_start}-{batch_end}/{total}")
            
            # 并发处理当前批次
            batch_tasks = [
                process_with_semaphore(item, batch_start + i)
                for i, item in enumerate(batch)
            ]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
        
        return results


class QueryOptimizer:
    """数据库查询优化器"""
    
    def __init__(self, cache_ttl: int = 300):
        """初始化查询优化器
        
        Args:
            cache_ttl: 查询缓存过期时间（秒）
        """
        self.cache_ttl = cache_ttl
        self._query_cache: Dict[str, tuple[Any, datetime]] = {}
        self._lock = asyncio.Lock()
    
    async def cached_query(
        self,
        cache_key: str,
        query_fn: Callable[[], Coroutine[Any, Any, T]],
        ttl: Optional[int] = None
    ) -> T:
        """缓存查询结果
        
        Args:
            cache_key: 缓存键
            query_fn: 查询函数
            ttl: 缓存过期时间（秒）
            
        Returns:
            查询结果
        """
        ttl = ttl or self.cache_ttl
        
        async with self._lock:
            # 检查缓存
            if cache_key in self._query_cache:
                result, cached_at = self._query_cache[cache_key]
                if datetime.now() - cached_at < timedelta(seconds=ttl):
                    logger.debug(f"查询缓存命中: {cache_key}")
                    return result
        
        # 执行查询
        result = await query_fn()
        
        # 保存到缓存
        async with self._lock:
            self._query_cache[cache_key] = (result, datetime.now())
        
        logger.debug(f"查询结果已缓存: {cache_key}")
        return result
    
    async def clear_cache(self, pattern: Optional[str] = None):
        """清空查询缓存
        
        Args:
            pattern: 缓存键模式（支持通配符*）
        """
        async with self._lock:
            if pattern:
                keys_to_delete = [
                    key for key in self._query_cache.keys()
                    if pattern.replace('*', '') in key
                ]
                for key in keys_to_delete:
                    del self._query_cache[key]
                logger.info(f"清空查询缓存: {len(keys_to_delete)}个条目")
            else:
                count = len(self._query_cache)
                self._query_cache.clear()
                logger.info(f"清空所有查询缓存: {count}个条目")
    
    async def batch_fetch(
        self,
        ids: List[str],
        fetch_fn: Callable[[List[str]], Coroutine[Any, Any, List[T]]],
        batch_size: int = 100
    ) -> List[T]:
        """批量获取数据（优化N+1查询问题）
        
        Args:
            ids: ID列表
            fetch_fn: 批量获取函数
            batch_size: 批次大小
            
        Returns:
            数据列表
        """
        results = []
        
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_results = await fetch_fn(batch_ids)
            results.extend(batch_results)
        
        logger.info(f"批量获取完成: {len(ids)}个ID, {len(results)}个结果")
        return results


class FileProcessingOptimizer:
    """文件处理优化器"""
    
    def __init__(self, max_workers: int = 4):
        """初始化文件处理优化器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def parallel_parse(
        self,
        files: List[Dict[str, Any]],
        parse_fn: Callable[[bytes, str], Coroutine[Any, Any, str]]
    ) -> List[Dict[str, Any]]:
        """并行解析文件
        
        Args:
            files: 文件列表 [{"filename": str, "content": bytes}, ...]
            parse_fn: 解析函数
            
        Returns:
            解析结果列表
        """
        async def parse_with_semaphore(file_info: Dict[str, Any]) -> Dict[str, Any]:
            async with self.semaphore:
                try:
                    start_time = time.time()
                    text = await parse_fn(
                        file_info["content"],
                        file_info["filename"]
                    )
                    parse_time = time.time() - start_time
                    
                    return {
                        "filename": file_info["filename"],
                        "text": text,
                        "success": True,
                        "parse_time": parse_time
                    }
                except Exception as e:
                    logger.error(f"文件解析失败: {file_info['filename']}, {e}")
                    return {
                        "filename": file_info["filename"],
                        "error": str(e),
                        "success": False
                    }
        
        logger.info(f"开始并行解析: {len(files)}个文件, {self.max_workers}个工作线程")
        
        tasks = [parse_with_semaphore(file_info) for file_info in files]
        results = await asyncio.gather(*tasks)
        
        successful = sum(1 for r in results if r.get("success"))
        logger.info(f"并行解析完成: {successful}/{len(files)}个成功")
        
        return results


class CacheWarmer:
    """缓存预热器"""
    
    def __init__(self, cache):
        """初始化缓存预热器
        
        Args:
            cache: 缓存实例（LLMCache或其他）
        """
        self.cache = cache
    
    async def warm_up(
        self,
        items: List[tuple[str, Callable[[], Coroutine[Any, Any, str]]]],
        ttl: Optional[int] = None
    ):
        """预热缓存
        
        Args:
            items: 预热项目列表 [(cache_key, compute_fn), ...]
            ttl: 缓存过期时间
        """
        logger.info(f"开始缓存预热: {len(items)}个项目")
        
        for cache_key, compute_fn in items:
            try:
                # 检查是否已缓存
                if await self.cache.exists(cache_key):
                    logger.debug(f"缓存已存在，跳过: {cache_key[:8]}...")
                    continue
                
                # 计算并缓存
                result = await compute_fn()
                await self.cache.set(cache_key, result, ttl)
                logger.debug(f"缓存预热完成: {cache_key[:8]}...")
                
            except Exception as e:
                logger.error(f"缓存预热失败: {cache_key[:8]}..., {e}")
        
        logger.info("缓存预热完成")


class LLMCallOptimizer:
    """LLM调用优化器"""
    
    def __init__(
        self,
        llm_client,
        max_concurrent: int = 5,
        enable_batching: bool = True,
        batch_delay: float = 0.1
    ):
        """初始化LLM调用优化器
        
        Args:
            llm_client: LLM客户端
            max_concurrent: 最大并发数
            enable_batching: 是否启用批处理
            batch_delay: 批处理延迟（秒）
        """
        self.llm_client = llm_client
        self.max_concurrent = max_concurrent
        self.enable_batching = enable_batching
        self.batch_delay = batch_delay
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._pending_requests: List[tuple] = []
        self._batch_task: Optional[asyncio.Task] = None
    
    async def generate(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """优化的生成调用
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            生成结果
        """
        async with self.semaphore:
            return await self.llm_client.generate(prompt, **kwargs)
    
    async def batch_generate(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[str]:
        """批量生成（优化版）
        
        Args:
            prompts: 提示词列表
            **kwargs: 其他参数
            
        Returns:
            生成结果列表
        """
        return await self.llm_client.batch_generate(
            prompts,
            max_concurrent=self.max_concurrent,
            **kwargs
        )


# 全局优化器实例
batch_processor = BatchProcessor()
query_optimizer = QueryOptimizer()
file_processing_optimizer = FileProcessingOptimizer()


async def get_performance_report() -> Dict[str, Any]:
    """获取性能报告"""
    metrics = await performance_monitor.get_metrics()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "summary": {
            "total_operations": len(metrics),
            "total_calls": sum(m["total_calls"] for m in metrics.values()),
            "total_errors": sum(m["errors"] for m in metrics.values()),
        }
    }
