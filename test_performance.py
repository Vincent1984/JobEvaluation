"""性能优化测试"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

from src.core.performance import (
    PerformanceMonitor,
    PerformanceMetrics,
    BatchProcessor,
    QueryOptimizer,
    FileProcessingOptimizer,
    CacheWarmer,
    LLMCallOptimizer,
    monitor_performance,
    get_performance_report
)


class TestPerformanceMetrics:
    """测试性能指标"""
    
    def test_metrics_initialization(self):
        """测试指标初始化"""
        metrics = PerformanceMetrics(operation_name="test_op")
        
        assert metrics.operation_name == "test_op"
        assert metrics.total_calls == 0
        assert metrics.total_time == 0.0
        assert metrics.errors == 0
    
    def test_metrics_update(self):
        """测试指标更新"""
        metrics = PerformanceMetrics(operation_name="test_op")
        
        # 更新成功调用
        metrics.update(execution_time=0.5, error=False)
        assert metrics.total_calls == 1
        assert metrics.total_time == 0.5
        assert metrics.avg_time == 0.5
        assert metrics.min_time == 0.5
        assert metrics.max_time == 0.5
        
        # 更新另一次调用
        metrics.update(execution_time=1.0, error=False)
        assert metrics.total_calls == 2
        assert metrics.avg_time == 0.75
        assert metrics.min_time == 0.5
        assert metrics.max_time == 1.0
        
        # 更新错误调用
        metrics.update(execution_time=0.0, error=True)
        assert metrics.total_calls == 3
        assert metrics.errors == 1
    
    def test_metrics_to_dict(self):
        """测试指标转换为字典"""
        metrics = PerformanceMetrics(operation_name="test_op")
        metrics.update(0.5, cache_hit=True)
        metrics.update(1.0, cache_hit=False)
        
        result = metrics.to_dict()
        
        assert result["operation"] == "test_op"
        assert result["total_calls"] == 2
        assert result["cache_hits"] == 1
        assert result["cache_misses"] == 1
        assert "50.00%" in result["cache_hit_rate"]


class TestPerformanceMonitor:
    """测试性能监控器"""
    
    @pytest.mark.asyncio
    async def test_record_metrics(self):
        """测试记录指标"""
        monitor = PerformanceMonitor()
        
        await monitor.record("test_op", 0.5, error=False)
        await monitor.record("test_op", 1.0, error=False)
        
        metrics = await monitor.get_metrics("test_op")
        
        assert metrics["total_calls"] == 2
        assert metrics["avg_time_ms"] == 750.0
    
    @pytest.mark.asyncio
    async def test_get_all_metrics(self):
        """测试获取所有指标"""
        monitor = PerformanceMonitor()
        
        await monitor.record("op1", 0.5)
        await monitor.record("op2", 1.0)
        
        all_metrics = await monitor.get_metrics()
        
        assert "op1" in all_metrics
        assert "op2" in all_metrics
        assert len(all_metrics) == 2
    
    @pytest.mark.asyncio
    async def test_reset_metrics(self):
        """测试重置指标"""
        monitor = PerformanceMonitor()
        
        await monitor.record("test_op", 0.5)
        await monitor.reset("test_op")
        
        metrics = await monitor.get_metrics("test_op")
        assert metrics == {}


class TestMonitorPerformanceDecorator:
    """测试性能监控装饰器"""
    
    @pytest.mark.asyncio
    async def test_decorator_records_metrics(self):
        """测试装饰器记录指标"""
        monitor = PerformanceMonitor()
        
        @monitor_performance("test_function")
        async def test_func():
            await asyncio.sleep(0.1)
            return "result"
        
        result = await test_func()
        
        assert result == "result"
        
        # 等待指标记录完成
        await asyncio.sleep(0.1)
        
        from src.core.performance import performance_monitor
        metrics = await performance_monitor.get_metrics("test_function")
        
        assert metrics["total_calls"] >= 1


class TestBatchProcessor:
    """测试批量处理器"""
    
    @pytest.mark.asyncio
    async def test_process_batch(self):
        """测试批量处理"""
        processor = BatchProcessor(batch_size=5, max_concurrent=2)
        
        items = list(range(10))
        
        async def process_item(item):
            await asyncio.sleep(0.01)
            return item * 2
        
        results = await processor.process_batch(items, process_item)
        
        assert len(results) == 10
        assert results[0] == 0
        assert results[5] == 10
    
    @pytest.mark.asyncio
    async def test_process_batch_with_progress(self):
        """测试带进度回调的批量处理"""
        processor = BatchProcessor(batch_size=3, max_concurrent=2)
        
        items = list(range(6))
        progress_calls = []
        
        def on_progress(current, total):
            progress_calls.append((current, total))
        
        async def process_item(item):
            await asyncio.sleep(0.01)
            return item
        
        results = await processor.process_batch(
            items,
            process_item,
            on_progress=on_progress
        )
        
        assert len(results) == 6
        assert len(progress_calls) == 6
        assert progress_calls[-1] == (6, 6)
    
    @pytest.mark.asyncio
    async def test_process_batch_with_errors(self):
        """测试批量处理错误处理"""
        processor = BatchProcessor(batch_size=5, max_concurrent=2)
        
        items = list(range(5))
        
        async def process_item(item):
            if item == 2:
                raise ValueError("Test error")
            return item * 2
        
        results = await processor.process_batch(items, process_item)
        
        assert len(results) == 5
        assert results[0] == 0
        assert "error" in results[2]


class TestQueryOptimizer:
    """测试查询优化器"""
    
    @pytest.mark.asyncio
    async def test_cached_query(self):
        """测试缓存查询"""
        optimizer = QueryOptimizer(cache_ttl=60)
        
        call_count = 0
        
        async def query_fn():
            nonlocal call_count
            call_count += 1
            return "result"
        
        # 第一次调用
        result1 = await optimizer.cached_query("test_key", query_fn)
        assert result1 == "result"
        assert call_count == 1
        
        # 第二次调用（应该从缓存返回）
        result2 = await optimizer.cached_query("test_key", query_fn)
        assert result2 == "result"
        assert call_count == 1  # 没有增加
    
    @pytest.mark.asyncio
    async def test_clear_cache(self):
        """测试清空缓存"""
        optimizer = QueryOptimizer()
        
        async def query_fn():
            return "result"
        
        await optimizer.cached_query("test_key", query_fn)
        await optimizer.clear_cache()
        
        # 清空后再次调用应该重新执行
        call_count = 0
        
        async def query_fn2():
            nonlocal call_count
            call_count += 1
            return "result"
        
        await optimizer.cached_query("test_key", query_fn2)
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_batch_fetch(self):
        """测试批量获取"""
        optimizer = QueryOptimizer()
        
        async def fetch_fn(ids):
            return [f"item_{id}" for id in ids]
        
        ids = [str(i) for i in range(10)]
        results = await optimizer.batch_fetch(ids, fetch_fn, batch_size=3)
        
        assert len(results) == 10
        assert results[0] == "item_0"
        assert results[9] == "item_9"


class TestFileProcessingOptimizer:
    """测试文件处理优化器"""
    
    @pytest.mark.asyncio
    async def test_parallel_parse(self):
        """测试并行解析"""
        optimizer = FileProcessingOptimizer(max_workers=2)
        
        files = [
            {"filename": f"file{i}.txt", "content": f"content{i}".encode()}
            for i in range(5)
        ]
        
        async def parse_fn(content, filename):
            await asyncio.sleep(0.01)
            return content.decode()
        
        results = await optimizer.parallel_parse(files, parse_fn)
        
        assert len(results) == 5
        assert all(r["success"] for r in results)
        assert results[0]["text"] == "content0"
    
    @pytest.mark.asyncio
    async def test_parallel_parse_with_errors(self):
        """测试并行解析错误处理"""
        optimizer = FileProcessingOptimizer(max_workers=2)
        
        files = [
            {"filename": "file1.txt", "content": b"content1"},
            {"filename": "file2.txt", "content": b"content2"},
        ]
        
        async def parse_fn(content, filename):
            if filename == "file2.txt":
                raise ValueError("Parse error")
            return content.decode()
        
        results = await optimizer.parallel_parse(files, parse_fn)
        
        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert "error" in results[1]


class TestCacheWarmer:
    """测试缓存预热器"""
    
    @pytest.mark.asyncio
    async def test_warm_up(self):
        """测试缓存预热"""
        # 创建模拟缓存
        cache = Mock()
        cache.exists = AsyncMock(return_value=False)
        cache.set = AsyncMock()
        
        warmer = CacheWarmer(cache)
        
        async def compute_fn():
            return "computed_value"
        
        items = [
            ("key1", compute_fn),
            ("key2", compute_fn),
        ]
        
        await warmer.warm_up(items)
        
        assert cache.set.call_count == 2
    
    @pytest.mark.asyncio
    async def test_warm_up_skip_existing(self):
        """测试跳过已存在的缓存"""
        cache = Mock()
        cache.exists = AsyncMock(return_value=True)
        cache.set = AsyncMock()
        
        warmer = CacheWarmer(cache)
        
        async def compute_fn():
            return "computed_value"
        
        items = [("key1", compute_fn)]
        
        await warmer.warm_up(items)
        
        # 不应该调用set
        assert cache.set.call_count == 0


class TestLLMCallOptimizer:
    """测试LLM调用优化器"""
    
    @pytest.mark.asyncio
    async def test_generate_with_concurrency_control(self):
        """测试并发控制的生成"""
        llm_client = Mock()
        llm_client.generate = AsyncMock(return_value="response")
        
        optimizer = LLMCallOptimizer(llm_client, max_concurrent=2)
        
        result = await optimizer.generate("test prompt")
        
        assert result == "response"
        assert llm_client.generate.called
    
    @pytest.mark.asyncio
    async def test_batch_generate(self):
        """测试批量生成"""
        llm_client = Mock()
        llm_client.batch_generate = AsyncMock(
            return_value=["response1", "response2"]
        )
        
        optimizer = LLMCallOptimizer(llm_client, max_concurrent=2)
        
        prompts = ["prompt1", "prompt2"]
        results = await optimizer.batch_generate(prompts)
        
        assert len(results) == 2
        assert llm_client.batch_generate.called


class TestPerformanceReport:
    """测试性能报告"""
    
    @pytest.mark.asyncio
    async def test_get_performance_report(self):
        """测试获取性能报告"""
        from src.core.performance import performance_monitor
        
        # 重置监控器
        await performance_monitor.reset()
        
        # 记录一些指标
        await performance_monitor.record("op1", 0.5)
        await performance_monitor.record("op2", 1.0)
        
        report = await get_performance_report()
        
        assert "timestamp" in report
        assert "metrics" in report
        assert "summary" in report
        assert report["summary"]["total_operations"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
