# DeepSeek-R1 客户端使用指南

## 概述

DeepSeek-R1客户端是一个功能完整的LLM客户端封装，专门为DeepSeek-R1推理模型优化。提供异步API调用、自动重试、错误处理、缓存等企业级特性。

## 核心特性

### 1. 异步API调用
- 基于`asyncio`的异步接口
- 支持高并发场景
- 非阻塞I/O操作

### 2. 自动重试机制
- 指数退避策略（exponential backoff）
- 可配置重试次数（默认3次）
- 智能错误分类和处理

### 3. 错误处理
- 细粒度异常分类：
  - `LLMConnectionError`: 连接错误
  - `LLMRateLimitError`: 速率限制
  - `LLMTimeoutError`: 超时错误
  - `LLMException`: 通用错误
- 详细的错误日志

### 4. 响应缓存
- 基于prompt的智能缓存
- 可配置启用/禁用
- 显著提升重复查询性能

### 5. 批量处理
- 并发批量调用
- 可控并发数
- 自动异常处理

### 6. 流式输出
- 实时流式响应
- 适合长文本生成
- 改善用户体验

## 快速开始

### 基础使用

```python
from src.core.llm_client import DeepSeekR1Client

# 创建客户端
client = DeepSeekR1Client()

# 生成文本
response = await client.generate(
    prompt="请介绍岗位JD的重要性",
    max_tokens=200
)
print(response)
```

### JSON格式输出

```python
# 生成JSON格式响应
prompt = """
请解析以下JD：
职位：Python工程师
要求：3年经验

返回JSON格式：
{
    "job_title": "...",
    "experience": "..."
}
"""

response = await client.generate_json(prompt)
print(response)  # 自动解析为dict
```

### 批量处理

```python
# 批量生成
prompts = [
    "什么是岗位JD？",
    "什么是候选人匹配？",
    "什么是职位评估？"
]

responses = await client.batch_generate(
    prompts,
    max_concurrent=3  # 最多3个并发请求
)
```

### 流式输出

```python
# 流式生成
async for chunk in client.generate_stream(
    prompt="详细介绍HR分析系统",
    max_tokens=500
):
    print(chunk, end="", flush=True)
```

## 配置选项

### 环境变量配置

在`.env`文件中配置：

```bash
# DeepSeek API配置
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-reasoner

# 高级配置
LLM_MAX_RETRIES=3
LLM_TIMEOUT=60.0
LLM_ENABLE_CACHE=true
LLM_MAX_CONCURRENT=5
LLM_DEFAULT_TEMPERATURE=0.7
LLM_DEFAULT_MAX_TOKENS=4000
```

### 代码配置

```python
client = DeepSeekR1Client(
    api_key="your_api_key",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-reasoner",
    max_retries=3,
    timeout=60.0,
    enable_cache=True
)
```

## API参考

### DeepSeekR1Client

#### 初始化参数

- `api_key` (str, optional): API密钥
- `base_url` (str, optional): API基础URL
- `model` (str, optional): 模型名称
- `max_retries` (int): 最大重试次数，默认3
- `timeout` (float): 请求超时时间（秒），默认60.0
- `enable_cache` (bool): 是否启用缓存，默认True

#### 主要方法

##### generate()

生成文本响应。

```python
async def generate(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000,
    system_message: Optional[str] = None
) -> str
```

**参数：**
- `prompt`: 用户提示词
- `model`: 模型名称（可选）
- `temperature`: 温度参数（0-1），控制随机性
- `max_tokens`: 最大生成token数
- `system_message`: 系统消息（可选）

**返回：** 生成的文本内容

**异常：** `LLMException`及其子类

##### generate_json()

生成JSON格式响应。

```python
async def generate_json(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000,
    system_message: Optional[str] = None
) -> Dict[str, Any]
```

**返回：** 解析后的JSON对象（dict）

**异常：** `LLMException`, `ValueError`

##### generate_stream()

流式生成文本响应。

```python
async def generate_stream(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000,
    system_message: Optional[str] = None
) -> AsyncGenerator[str, None]
```

**返回：** 异步生成器，逐块返回文本

##### batch_generate()

批量生成文本响应。

```python
async def batch_generate(
    prompts: List[str],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000,
    system_message: Optional[str] = None,
    max_concurrent: int = 5
) -> List[str]
```

**参数：**
- `prompts`: 提示词列表
- `max_concurrent`: 最大并发数

**返回：** 生成的文本列表（顺序与输入一致）

##### batch_generate_json()

批量生成JSON格式响应。

```python
async def batch_generate_json(
    prompts: List[str],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000,
    system_message: Optional[str] = None,
    max_concurrent: int = 5
) -> List[Dict[str, Any]]
```

**返回：** 解析后的JSON对象列表

##### clear_cache()

清空缓存。

```python
def clear_cache()
```

##### get_cache_stats()

获取缓存统计信息。

```python
def get_cache_stats() -> Dict[str, Any]
```

**返回：**
```python
{
    "enabled": bool,
    "size": int,
    "keys": List[str]
}
```

## DeepSeek-R1 推理模型特性

### 推理链Prompt

DeepSeek-R1是推理模型，建议使用`<thinking>`标签引导推理过程：

```python
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
{jd_text}

请提供详细的评估结果。
"""
```

### 结构化输出

要求模型返回JSON格式时，明确指定格式：

```python
prompt = """
请分析以下岗位JD。

岗位JD:
{jd_text}

请返回JSON格式：
{{
    "job_title": "职位名称",
    "department": "部门",
    "responsibilities": ["职责1", "职责2"],
    "requirements": ["要求1", "要求2"]
}}
"""
```

## 性能优化建议

### 1. 使用缓存

对于重复查询，启用缓存可显著提升性能：

```python
client = DeepSeekR1Client(enable_cache=True)
```

### 2. 批量处理

批量处理多个请求比逐个处理更高效：

```python
# 推荐
responses = await client.batch_generate(prompts, max_concurrent=5)

# 不推荐
responses = [await client.generate(p) for p in prompts]
```

### 3. 控制并发数

根据API限制调整并发数：

```python
# 避免触发速率限制
responses = await client.batch_generate(
    prompts,
    max_concurrent=3  # 降低并发数
)
```

### 4. 合理设置max_tokens

根据实际需求设置token数，避免浪费：

```python
# 简短回答
response = await client.generate(prompt, max_tokens=100)

# 详细分析
response = await client.generate(prompt, max_tokens=2000)
```

## 错误处理最佳实践

### 捕获特定异常

```python
from src.core.llm_client import (
    LLMException,
    LLMConnectionError,
    LLMRateLimitError,
    LLMTimeoutError
)

try:
    response = await client.generate(prompt)
except LLMRateLimitError:
    # 速率限制，等待后重试
    await asyncio.sleep(60)
    response = await client.generate(prompt)
except LLMTimeoutError:
    # 超时，使用更短的prompt
    response = await client.generate(shorter_prompt)
except LLMConnectionError:
    # 连接错误，检查网络
    logger.error("无法连接到DeepSeek API")
except LLMException as e:
    # 其他错误
    logger.error(f"LLM调用失败: {e}")
```

### 使用重试机制

客户端内置了自动重试，但你也可以添加额外的重试逻辑：

```python
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
async def robust_generate(prompt: str) -> str:
    return await client.generate(prompt)
```

## 成本控制

### Token使用估算

- 输入Token: 约500-2000 tokens/请求
- 输出Token: 约1000-3000 tokens/请求
- 推理Token: R1模型会产生额外的推理过程token

### 优化建议

1. **缓存常见查询**：相似JD的解析结果可以复用
2. **控制输出长度**：设置合理的`max_tokens`
3. **批量处理**：合并多个小任务
4. **精简Prompt**：去除不必要的描述

## 测试

运行测试套件：

```bash
python test_deepseek_client.py
```

运行示例：

```bash
python examples/deepseek_usage.py
```

## 常见问题

### Q: 如何切换到其他LLM提供商？

A: 修改配置即可：

```python
# 使用OpenAI
client = DeepSeekR1Client(
    api_key="your_openai_key",
    base_url="https://api.openai.com/v1",
    model="gpt-4"
)
```

### Q: 缓存会占用多少内存？

A: 缓存存储在内存中，每个缓存项约几KB。可以定期调用`clear_cache()`清理。

### Q: 如何处理超长文本？

A: 可以分段处理或使用更大的`max_tokens`：

```python
response = await client.generate(
    long_prompt,
    max_tokens=8000  # 增加token限制
)
```

### Q: 支持本地部署吗？

A: 支持。使用vLLM等工具部署后，修改`base_url`即可：

```python
client = DeepSeekR1Client(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)
```

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本
- 支持异步API调用
- 实现自动重试机制
- 添加响应缓存
- 支持批量处理和流式输出
- 完善错误处理

## 许可证

MIT License
