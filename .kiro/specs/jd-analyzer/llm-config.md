# DeepSeek-R1 配置说明

## 模型选择

本系统使用 **DeepSeek-R1**（推理模型）作为核心LLM引擎。

### 为什么选择DeepSeek-R1？

1. **强大的推理能力**: R1模型专门针对复杂推理任务优化，适合HR分析场景
2. **中文支持优秀**: 对中文岗位JD的理解和分析能力强
3. **成本效益**: 相比GPT-4等模型，性价比更高
4. **本地部署选项**: 支持本地部署，保护数据隐私

## API配置

### 使用DeepSeek API

```python
from openai import AsyncOpenAI

# DeepSeek API配置
client = AsyncOpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com"
)

async def call_deepseek_r1(prompt: str) -> str:
    """调用DeepSeek-R1"""
    response = await client.chat.completions.create(
        model="deepseek-reasoner",  # R1推理模型
        messages=[
            {"role": "system", "content": "你是一个专业的HR岗位分析专家。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )
    return response.choices[0].message.content
```

### 环境变量配置

```bash
# .env文件
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-reasoner
```

## Prompt工程建议

DeepSeek-R1是推理模型，建议使用以下Prompt模式：

### 1. 结构化输出Prompt

```python
STRUCTURED_PROMPT = """
请分析以下岗位JD并提取结构化信息。

<thinking>
首先，我需要：
1. 识别职位的核心信息
2. 提取职责和要求
3. 分类技能要求
</thinking>

岗位JD:
{jd_text}

请按照以下JSON格式返回：
{{
    "job_title": "职位名称",
    "department": "部门",
    ...
}}
"""
```

### 2. 推理链Prompt

```python
REASONING_PROMPT = """
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

### 3. 多步骤推理Prompt

```python
MULTI_STEP_PROMPT = """
请为以下岗位生成评估问卷。

<thinking>
步骤1: 分析岗位的核心能力要求
步骤2: 确定评估维度
步骤3: 为每个维度设计问题
步骤4: 确保问题的区分度
</thinking>

岗位信息:
{jd_data}

评估模型: {evaluation_model}

请生成问卷题目列表。
"""
```

## 性能优化

### 1. 批量调用

```python
async def batch_call_deepseek(prompts: List[str]) -> List[str]:
    """批量调用DeepSeek-R1"""
    tasks = [call_deepseek_r1(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 流式输出

```python
async def stream_deepseek_r1(prompt: str):
    """流式调用DeepSeek-R1"""
    stream = await client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### 3. 缓存策略

```python
import hashlib
from functools import lru_cache

class DeepSeekCache:
    def __init__(self):
        self.cache = {}
    
    def get_cache_key(self, prompt: str) -> str:
        return hashlib.md5(prompt.encode()).hexdigest()
    
    async def call_with_cache(self, prompt: str) -> str:
        cache_key = self.get_cache_key(prompt)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = await call_deepseek_r1(prompt)
        self.cache[cache_key] = result
        return result
```

## 成本控制

### Token使用估算

- 输入Token: 约500-2000 tokens/请求（取决于JD长度）
- 输出Token: 约1000-3000 tokens/请求（取决于任务复杂度）
- 推理Token: R1模型会产生额外的推理过程token

### 成本优化建议

1. **缓存常见查询**: 相似JD的解析结果可以复用
2. **控制输出长度**: 设置合理的max_tokens
3. **批量处理**: 合并多个小任务
4. **异步调用**: 提高并发效率

## 错误处理

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_deepseek_with_retry(prompt: str) -> str:
    """带重试的DeepSeek调用"""
    try:
        return await call_deepseek_r1(prompt)
    except Exception as e:
        print(f"DeepSeek API调用失败: {e}")
        raise
```

## 本地部署选项（可选）

如果需要本地部署DeepSeek-R1：

```bash
# 使用vLLM部署
pip install vllm

# 启动服务
python -m vllm.entrypoints.openai.api_server \
    --model deepseek-ai/DeepSeek-R1 \
    --host 0.0.0.0 \
    --port 8000
```

然后修改配置：

```python
client = AsyncOpenAI(
    api_key="not-needed",
    base_url="http://localhost:8000/v1"
)
```
