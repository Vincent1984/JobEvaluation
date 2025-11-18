# LLM调用缓存机制

## 概述

LLM调用缓存机制用于减少重复的API调用，提高响应速度并降低成本。系统支持两种缓存后端：

1. **内存缓存（MemoryCache）** - 快速但不持久，适合开发和测试
2. **Redis缓存（RedisCache）** - 持久化且支持分布式，适合生产环境

## 核心特性

### 1. 智能缓存键生成

基于以下参数生成唯一的MD5哈希键：
- 提示词（prompt）
- 模型名称（model）
- 温度参数（temperature）
- 最大token数（max_tokens）
- 系统消息（system_message）

```python
from src.core.llm_cache import LLMCache

cache_key = LLMCache.generate_cache_key(
    prompt="解析以下岗位JD",
    model="deepseek-reasoner",
    temperature=0.7,
    max_tokens=4000,
    system_message="你是一个专业的HR岗位分析专家。"
)
# 返回: "ebb687e2f3fcac285c45e783cadde631"
```

### 2. 多后端支持

#### 内存缓存

```python
from src.core.llm_cache import create_memory_cache
from src.core.llm_client import DeepSeekR1Client

# 创建内存缓存
cache = create_memory_cache()

# 创建带缓存的LLM客户端
client = DeepSeekR1Client(enable_cache=True, cache=cache)
```

**特点：**
- ✅ 快速访问（纳秒级）
- ✅ 零配置
- ✅ 适合开发和测试
- ❌ 不持久化（重启后丢失）
- ❌ 不支持分布式

#### Redis缓存

```python
import redis.asyncio as aioredis
from src.core.llm_cache import create_redis_cache
from src.core.llm_client import DeepSeekR1Client
from src.core.config import settings

# 连接Redis
redis_client = await aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    encoding="utf-8",
    decode_responses=True
)

# 创建Redis缓存
cache = create_redis_cache(
    redis_client,
    key_prefix="llm_cache:",  # 键前缀，用于命名空间隔离
    default_ttl=3600  # 默认过期时间（秒）
)

# 创建带缓存的LLM客户端
client = DeepSeekR1Client(enable_cache=True, cache=cache)
```

**特点：**
- ✅ 持久化存储
- ✅ 支持TTL自动过期
- ✅ 支持分布式部署
- ✅ 适合生产环境
- ❌ 需要Redis服务
- ❌ 略慢于内存缓存（毫秒级）

## 使用方法

### 基本使用

```python
from src.core.llm_client import DeepSeekR1Client

# 创建客户端（默认使用内存缓存）
client = DeepSeekR1Client(enable_cache=True)

# 第一次调用（调用API并缓存）
result1 = await client.generate("解析以下岗位JD")

# 第二次调用相同提示词（从缓存返回，不调用API）
result2 = await client.generate("解析以下岗位JD")
```

### 自定义缓存TTL

```python
# 设置缓存过期时间为30分钟
result = await client.generate(
    "解析以下岗位JD",
    cache_ttl=1800  # 秒
)
```

### 禁用缓存

```python
# 创建不使用缓存的客户端
client = DeepSeekR1Client(enable_cache=False)

# 或者在初始化后禁用
client.enable_cache = False
```

### 缓存管理

```python
# 查看缓存统计
stats = await client.get_cache_stats()
print(stats)
# {
#     "backend": "memory",
#     "size": 10,
#     "hits": 15,
#     "misses": 5,
#     "hit_rate": "75.00%",
#     "enabled": True
# }

# 清空缓存
await client.clear_cache()
```

### get_or_compute模式

```python
from src.core.llm_cache import create_memory_cache

cache = create_memory_cache()

async def expensive_llm_call():
    return await client.generate("复杂的提示词")

# 如果缓存存在则返回缓存，否则执行计算并缓存
result = await cache.get_or_compute(
    cache_key="my_key",
    compute_fn=expensive_llm_call,
    ttl=3600
)
```

## 缓存策略

### 何时使用缓存

✅ **适合缓存的场景：**
- 相同的JD解析请求
- 标准化的评估模板
- 固定的问卷生成
- 重复的质量检查

❌ **不适合缓存的场景：**
- 需要实时数据的请求
- 用户特定的个性化内容
- 频繁变化的提示词
- 需要随机性的生成（高temperature）

### 缓存失效策略

1. **基于TTL的自动过期**（Redis）
   ```python
   cache = create_redis_cache(redis_client, default_ttl=3600)  # 1小时
   ```

2. **手动清除**
   ```python
   await cache.delete(cache_key)  # 删除单个
   await cache.clear()  # 清空所有
   ```

3. **参数变化自动失效**
   - 任何影响输出的参数变化都会生成新的缓存键

## 性能优化

### 缓存命中率优化

1. **标准化提示词**
   ```python
   # 不好：每次都不同
   prompt = f"解析JD，时间：{datetime.now()}"
   
   # 好：标准化格式
   prompt = "解析以下岗位JD"
   ```

2. **固定温度参数**
   ```python
   # 对于确定性任务使用较低的温度
   result = await client.generate(prompt, temperature=0.3)
   ```

3. **使用模板**
   ```python
   # 定义标准模板
   PARSE_TEMPLATE = "请解析以下岗位JD并提取关键信息：\n{jd_text}"
   
   # 使用模板
   prompt = PARSE_TEMPLATE.format(jd_text=jd_text)
   ```

### 内存管理

对于内存缓存，注意控制缓存大小：

```python
# 定期清理旧缓存
import asyncio

async def cache_cleanup_task():
    while True:
        await asyncio.sleep(3600)  # 每小时
        await client.clear_cache()
        logger.info("缓存已清理")
```

## 监控和调试

### 启用详细日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("src.core.llm_cache")
logger.setLevel(logging.DEBUG)
```

### 缓存统计

```python
stats = await client.get_cache_stats()

print(f"缓存后端: {stats['backend']}")
print(f"缓存大小: {stats['size']}")
print(f"命中次数: {stats.get('hits', 'N/A')}")
print(f"未命中次数: {stats.get('misses', 'N/A')}")
print(f"命中率: {stats.get('hit_rate', 'N/A')}")
```

### 检查特定缓存

```python
cache_key = LLMCache.generate_cache_key(...)

# 检查是否存在
exists = await cache.exists(cache_key)

# 获取缓存值
value = await cache.get(cache_key)
```

## 最佳实践

1. **生产环境使用Redis**
   - 持久化保证数据不丢失
   - 支持多实例共享缓存
   - 自动过期管理

2. **合理设置TTL**
   - 短期数据：300-1800秒（5-30分钟）
   - 中期数据：3600-7200秒（1-2小时）
   - 长期数据：86400秒（24小时）

3. **监控缓存命中率**
   - 目标：>70%命中率
   - 低于50%考虑优化提示词标准化

4. **定期清理**
   - 开发环境：每次重启清理
   - 生产环境：根据业务需求定期清理

5. **错误处理**
   ```python
   try:
       result = await client.generate(prompt)
   except Exception as e:
       logger.error(f"LLM调用失败: {e}")
       # 缓存失败不应影响业务逻辑
   ```

## 故障排查

### 缓存未命中

**问题：** 相同的请求没有命中缓存

**排查：**
1. 检查参数是否完全相同（包括空格、换行）
2. 检查temperature等参数是否一致
3. 启用DEBUG日志查看缓存键

```python
import logging
logging.getLogger("src.core.llm_cache").setLevel(logging.DEBUG)
```

### Redis连接失败

**问题：** 无法连接到Redis

**排查：**
1. 检查Redis服务是否运行
   ```bash
   redis-cli ping
   ```

2. 检查配置
   ```python
   from src.core.config import settings
   print(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
   ```

3. 测试连接
   ```python
   import redis.asyncio as aioredis
   redis_client = await aioredis.from_url("redis://localhost:6379")
   await redis_client.ping()
   ```

### 内存占用过高

**问题：** 内存缓存占用过多内存

**解决：**
1. 定期清理缓存
2. 切换到Redis缓存
3. 限制缓存大小（需要自定义实现）

## 示例代码

完整示例请参考：
- `examples/llm_cache_usage.py` - 缓存使用示例
- `test_llm_cache.py` - 单元测试

## 相关文档

- [DeepSeek-R1客户端文档](./README_DEEPSEEK.md)
- [配置管理](./config.py)
- [MCP通讯协议](../mcp/README.md)
