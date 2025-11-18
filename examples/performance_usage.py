"""性能优化使用示例

演示如何使用性能优化功能提升系统性能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import logging
from typing import List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_1_llm_optimization():
    """示例1：LLM调用优化"""
    print("\n=== 示例1：LLM调用优化 ===\n")
    
    from src.core.llm_client import DeepSeekR1Client
    from src.core.llm_cache import create_memory_cache
    
    # 创建带缓存的客户端
    client = DeepSeekR1Client(
        enable_cache=True,
        max_concurrent=5  # 限制并发数
    )
    
    # 1. 单次调用（会缓存）
    print("1. 第一次调用（实际请求API）...")
    result1 = await client.generate("分析软件工程师岗位JD")
    print(f"   结果长度: {len(result1)}")
    
    # 2. 相同调用（从缓存返回）
    print("\n2. 第二次相同调用（从缓存返回）...")
    result2 = await client.generate("分析软件工程师岗位JD")
    print(f"   结果长度: {len(result2)}")
    print(f"   结果相同: {result1 == result2}")
    
    # 3. 批量调用（并发控制）
    print("\n3. 批量调用（自动并发控制）...")
    prompts = [
        "分析产品经理岗位",
        "分析数据分析师岗位",
        "分析UI设计师岗位",
    ]
    results = await client.batch_generate(prompts, max_concurrent=2)
    print(f"   处理了 {len(results)} 个请求")
    
    # 4. 查看缓存统计
    print("\n4. 缓存统计:")
    stats = await client.get_cache_stats()
    print(f"   缓存后端: {stats.get('backend')}")
    print(f"   缓存大小: {stats.get('size')}")
    print(f"   命中率: {stats.get('hit_rate', 'N/A')}")


async def example_2_batch_processing():
    """示例2：批量处理优化"""
    print("\n=== 示例2：批量处理优化 ===\n")
    
    from src.core.performance import BatchProcessor
    
    # 创建批量处理器
    processor = BatchProcessor(
        batch_size=5,       # 每批5个
        max_concurrent=3,   # 最多3个并发
        timeout=10.0        # 超时10秒
    )
    
    # 模拟处理项目
    items = list(range(15))
    
    async def process_item(item: int) -> str:
        """处理单个项目"""
        await asyncio.sleep(0.1)  # 模拟处理时间
        return f"processed_{item}"
    
    def on_progress(current: int, total: int):
        """进度回调"""
        print(f"   进度: {current}/{total} ({current/total*100:.1f}%)")
    
    print("开始批量处理...")
    results = await processor.process_batch(
        items,
        process_item,
        on_progress=on_progress
    )
    
    print(f"\n处理完成: {len(results)} 个项目")
    print(f"前3个结果: {results[:3]}")


async def example_3_query_optimization():
    """示例3：查询优化"""
    print("\n=== 示例3：查询优化 ===\n")
    
    from src.core.performance import QueryOptimizer
    
    # 创建查询优化器
    optimizer = QueryOptimizer(cache_ttl=60)
    
    # 模拟数据库查询
    call_count = 0
    
    async def expensive_query():
        """模拟耗时查询"""
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.5)  # 模拟查询延迟
        return {"data": "query_result", "timestamp": call_count}
    
    # 1. 第一次查询（实际执行）
    print("1. 第一次查询（实际执行）...")
    result1 = await optimizer.cached_query("test_query", expensive_query)
    print(f"   结果: {result1}")
    print(f"   查询次数: {call_count}")
    
    # 2. 第二次查询（从缓存返回）
    print("\n2. 第二次查询（从缓存返回）...")
    result2 = await optimizer.cached_query("test_query", expensive_query)
    print(f"   结果: {result2}")
    print(f"   查询次数: {call_count} (未增加)")
    
    # 3. 批量获取
    print("\n3. 批量获取数据...")
    
    async def batch_fetch(ids: List[str]) -> List[dict]:
        """批量获取"""
        await asyncio.sleep(0.1)
        return [{"id": id, "data": f"item_{id}"} for id in ids]
    
    ids = [str(i) for i in range(10)]
    items = await optimizer.batch_fetch(ids, batch_fetch, batch_size=3)
    print(f"   获取了 {len(items)} 个项目")


async def example_4_file_processing():
    """示例4：文件处理优化"""
    print("\n=== 示例4：文件处理优化 ===\n")
    
    from src.core.performance import FileProcessingOptimizer
    
    # 创建文件处理优化器
    optimizer = FileProcessingOptimizer(max_workers=4)
    
    # 模拟文件
    files = [
        {
            "filename": f"file{i}.txt",
            "content": f"这是文件{i}的内容".encode('utf-8')
        }
        for i in range(10)
    ]
    
    async def parse_file(content: bytes, filename: str) -> str:
        """解析文件"""
        await asyncio.sleep(0.1)  # 模拟解析时间
        return content.decode('utf-8')
    
    print("开始并行解析文件...")
    results = await optimizer.parallel_parse(files, parse_file)
    
    successful = sum(1 for r in results if r.get("success"))
    print(f"\n解析完成: {successful}/{len(files)} 个文件成功")
    print(f"第一个文件: {results[0]['filename']} - {results[0]['text']}")


async def example_5_cache_warming():
    """示例5：缓存预热"""
    print("\n=== 示例5：缓存预热 ===\n")
    
    from src.core.performance import CacheWarmer
    from src.core.llm_cache import create_memory_cache
    
    # 创建缓存
    cache = create_memory_cache()
    warmer = CacheWarmer(cache)
    
    # 定义预热项目
    async def compute_category_tree():
        """计算分类树"""
        await asyncio.sleep(0.2)
        return {"tree": "category_data"}
    
    async def compute_templates():
        """计算模板"""
        await asyncio.sleep(0.2)
        return {"templates": ["template1", "template2"]}
    
    items = [
        ("category_tree", compute_category_tree),
        ("templates", compute_templates),
    ]
    
    print("开始缓存预热...")
    await warmer.warm_up(items, ttl=300)
    
    # 验证缓存
    print("\n验证缓存:")
    result1 = await cache.get("category_tree")
    result2 = await cache.get("templates")
    print(f"   category_tree: {'已缓存' if result1 else '未缓存'}")
    print(f"   templates: {'已缓存' if result2 else '未缓存'}")


async def example_6_performance_monitoring():
    """示例6：性能监控"""
    print("\n=== 示例6：性能监控 ===\n")
    
    from src.core.performance import (
        performance_monitor,
        monitor_performance,
        get_performance_report
    )
    
    # 使用装饰器监控函数
    @monitor_performance("test_operation")
    async def monitored_function(duration: float):
        """被监控的函数"""
        await asyncio.sleep(duration)
        return "completed"
    
    # 执行多次
    print("执行被监控的函数...")
    for i in range(5):
        await monitored_function(0.1)
    
    # 获取指标
    print("\n性能指标:")
    metrics = await performance_monitor.get_metrics("test_operation")
    print(f"   总调用次数: {metrics.get('total_calls')}")
    print(f"   平均时间: {metrics.get('avg_time_ms')}ms")
    print(f"   最小时间: {metrics.get('min_time_ms')}ms")
    print(f"   最大时间: {metrics.get('max_time_ms')}ms")
    
    # 获取完整报告
    print("\n完整性能报告:")
    report = await get_performance_report()
    print(f"   监控的操作数: {report['summary']['total_operations']}")
    print(f"   总调用次数: {report['summary']['total_calls']}")


async def example_7_integrated_optimization():
    """示例7：综合优化示例"""
    print("\n=== 示例7：综合优化示例 ===\n")
    
    from src.core.llm_client import DeepSeekR1Client
    from src.core.performance import (
        BatchProcessor,
        QueryOptimizer,
        monitor_performance
    )
    
    # 初始化组件
    llm_client = DeepSeekR1Client(enable_cache=True, max_concurrent=3)
    batch_processor = BatchProcessor(batch_size=5, max_concurrent=3)
    query_optimizer = QueryOptimizer()
    
    @monitor_performance("process_jd")
    async def process_jd(jd_text: str) -> dict:
        """处理单个JD"""
        # 使用LLM分析
        analysis = await llm_client.generate(
            f"分析以下JD：{jd_text[:100]}...",
            cache_ttl=600
        )
        
        # 模拟保存到数据库
        await asyncio.sleep(0.05)
        
        return {
            "jd_text": jd_text,
            "analysis": analysis[:50] + "...",
            "status": "completed"
        }
    
    # 批量处理JD
    jd_texts = [
        f"软件工程师岗位描述 {i}" for i in range(10)
    ]
    
    print("开始批量处理JD...")
    results = await batch_processor.process_batch(
        jd_texts,
        process_jd,
        on_progress=lambda c, t: print(f"   进度: {c}/{t}")
    )
    
    print(f"\n处理完成: {len(results)} 个JD")
    
    # 查看性能指标
    from src.core.performance import performance_monitor
    metrics = await performance_monitor.get_metrics("process_jd")
    print(f"\n性能统计:")
    print(f"   平均处理时间: {metrics.get('avg_time_ms')}ms")
    print(f"   缓存命中率: {metrics.get('cache_hit_rate', 'N/A')}")


async def main():
    """运行所有示例"""
    print("=" * 60)
    print("性能优化使用示例")
    print("=" * 60)
    
    try:
        # 注意：示例1需要实际的API密钥，这里跳过
        # await example_1_llm_optimization()
        print("\n示例1（LLM优化）需要API密钥，已跳过")
        
        await example_2_batch_processing()
        await example_3_query_optimization()
        await example_4_file_processing()
        await example_5_cache_warming()
        await example_6_performance_monitoring()
        
        # 示例7也需要API密钥
        # await example_7_integrated_optimization()
        print("\n示例7（综合优化）需要API密钥，已跳过")
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}", exc_info=True)
    
    print("\n" + "=" * 60)
    print("所有示例执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
