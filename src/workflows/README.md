# 工作流模块

本模块提供JD分析和问卷评估的完整工作流实现，通过MCP协议协调多个Agent完成复杂任务。

## 模块结构

```
src/workflows/
├── __init__.py                    # 模块导出
├── jd_analysis_workflow.py        # JD完整分析工作流
├── questionnaire_workflow.py      # 问卷生成与匹配评估工作流
└── README.md                      # 本文档
```

## 工作流概述

### 1. JD完整分析工作流 (JDAnalysisWorkflow)

实现 **解析 → 评估 → 优化** 的完整流程，通过MCP协调多个Agent：

**流程步骤：**
1. **解析JD** - 通过Parser Agent提取结构化信息
2. **评估质量** - 通过Evaluator Agent评估JD质量
3. **生成优化建议** - 通过Optimizer Agent生成改进建议

**支持的评估模型：**
- `standard` - 标准评估模型
- `mercer_ipe` - 美世国际职位评估法
- `factor_comparison` - 因素比较法

### 2. 问卷生成与匹配评估工作流 (QuestionnaireWorkflow)

实现 **问卷生成 → 回答收集 → 匹配计算** 的流程：

**主要功能：**
- **生成问卷** - 基于JD自动生成评估问卷
- **单个候选人评估** - 评估单个候选人与岗位的匹配度
- **批量候选人评估** - 批量处理多个候选人，提高效率

## 使用示例

### 1. JD完整分析

```python
from src.mcp.server import MCPServer
from src.workflows import JDAnalysisWorkflow

# 初始化MCP服务器
mcp_server = MCPServer(redis_client)

# 创建工作流实例
workflow = JDAnalysisWorkflow(mcp_server)

# 执行完整分析
result = await workflow.execute_full_analysis(
    jd_text="招聘Python后端工程师...",
    evaluation_model="standard",
    custom_template=None,
    timeout=300.0
)

# 结果包含：
# - jd_id: JD唯一标识
# - parsed_data: 解析结果
# - evaluation: 评估结果
# - suggestions: 优化建议
# - workflow_id: 工作流ID
# - status: completed/failed
# - execution_time: 执行时间（秒）

print(f"JD ID: {result['jd_id']}")
print(f"质量分数: {result['evaluation']['quality_score']['overall_score']}")
print(f"优化建议: {result['suggestions']}")
```

### 2. 生成问卷

```python
from src.workflows import QuestionnaireWorkflow

# 创建工作流实例
workflow = QuestionnaireWorkflow(mcp_server)

# 生成问卷
result = await workflow.generate_questionnaire(
    jd_id="jd_123456",
    evaluation_model="mercer_ipe",
    custom_config=None,
    timeout=120.0
)

# 结果包含：
# - questionnaire_id: 问卷ID
# - questionnaire: 问卷详情（题目、选项等）
# - workflow_id: 工作流ID
# - status: completed/failed

print(f"问卷ID: {result['questionnaire_id']}")
print(f"题目数量: {len(result['questionnaire']['questions'])}")
```

### 3. 评估单个候选人

```python
# 评估单个候选人的匹配度
result = await workflow.evaluate_match(
    jd_id="jd_123456",
    questionnaire_id="quest_789",
    responses={
        "q1": "5年",
        "q2": ["Python", "Django", "FastAPI"],
        "q3": 8  # 量表题
    },
    respondent_name="张三",
    timeout=120.0
)

# 结果包含：
# - match_id: 匹配结果ID
# - match_result: 匹配详情
#   - overall_score: 综合匹配度分数 (0-100)
#   - dimension_scores: 各维度得分
#   - strengths: 优势列表
#   - gaps: 差距列表
#   - recommendations: 建议

print(f"匹配度: {result['match_result']['overall_score']}")
print(f"优势: {result['match_result']['strengths']}")
print(f"差距: {result['match_result']['gaps']}")
```

### 4. 批量评估候选人

```python
# 批量评估多个候选人
candidate_responses = [
    {
        "respondent_name": "张三",
        "responses": {"q1": "5年", "q2": ["Python", "Django"], "q3": 8}
    },
    {
        "respondent_name": "李四",
        "responses": {"q1": "3年", "q2": ["Python", "Flask"], "q3": 7}
    },
    {
        "respondent_name": "王五",
        "responses": {"q1": "7年", "q2": ["Python", "FastAPI", "Django"], "q3": 9}
    }
]

result = await workflow.batch_evaluate_candidates(
    jd_id="jd_123456",
    questionnaire_id="quest_789",
    candidate_responses=candidate_responses,
    timeout=300.0
)

# 结果包含：
# - batch_id: 批量任务ID
# - total: 总候选人数
# - successful: 成功评估数
# - failed: 失败数
# - results: 成功的匹配结果列表
# - failed_candidates: 失败的候选人列表

print(f"总计: {result['total']}, 成功: {result['successful']}, 失败: {result['failed']}")

# 按匹配度排序
sorted_results = sorted(
    result['results'],
    key=lambda x: x['match_result']['overall_score'],
    reverse=True
)

for idx, candidate in enumerate(sorted_results, 1):
    print(f"{idx}. {candidate['respondent_name']}: {candidate['match_result']['overall_score']}分")
```

### 5. 查询工作流状态

```python
# 查询JD分析工作流状态
status = await workflow.get_workflow_status("workflow_id_123")

print(f"状态: {status['status']}")
print(f"当前步骤: {status['step']}")
print(f"JD ID: {status['jd_id']}")

# 查询批量评估状态
status = await workflow.get_workflow_status("batch_id_456")

print(f"总计: {status['total_candidates']}")
print(f"已处理: {status['processed_candidates']}")
print(f"成功: {status['successful_candidates']}")
print(f"失败: {status['failed_candidates']}")
```

## 工作流上下文管理

工作流使用MCP上下文（MCPContext）来管理执行状态和共享数据：

### JD分析工作流上下文

```python
{
    "context_id": "workflow_id",
    "shared_data": {
        "workflow": "jd_analysis",
        "jd_text": "...",
        "evaluation_model": "standard",
        "step": "parsing/evaluation/optimization/completed",
        "status": "running/completed/failed",
        "jd_id": "jd_123",
        "parsed_data": {...},
        "evaluation": {...},
        "result": {...}
    }
}
```

### 问卷工作流上下文

```python
{
    "context_id": "workflow_id",
    "shared_data": {
        "workflow": "questionnaire",
        "workflow_type": "questionnaire_generation/match_evaluation/batch_evaluation",
        "jd_id": "jd_123",
        "questionnaire_id": "quest_456",
        "status": "running/completed/failed",
        # 批量评估特有字段
        "total_candidates": 10,
        "processed_candidates": 5,
        "successful_candidates": 4,
        "failed_candidates": 1
    }
}
```

## 错误处理

工作流内置了完善的错误处理机制：

1. **超时处理** - 每个步骤都有超时限制，防止无限等待
2. **异常捕获** - 捕获并记录所有异常，返回友好的错误信息
3. **状态追踪** - 通过上下文记录工作流状态，便于调试
4. **部分失败处理** - 批量评估中，单个候选人失败不影响其他候选人

## 性能优化

### 1. 并行处理

批量评估时，可以考虑并行处理多个候选人（需要Agent支持）：

```python
# 未来可以实现并行评估
import asyncio

tasks = [
    workflow._evaluate_match_internal(...)
    for candidate in candidates
]

results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 2. 超时配置

根据实际情况调整超时时间：

```python
# 快速分析（降低准确性）
result = await workflow.execute_full_analysis(
    jd_text=text,
    timeout=60.0  # 1分钟
)

# 深度分析（提高准确性）
result = await workflow.execute_full_analysis(
    jd_text=text,
    timeout=600.0  # 10分钟
)
```

### 3. 缓存机制

工作流依赖LLM缓存机制（src/core/llm_cache.py）来提高性能：
- 相同的JD文本会复用解析结果
- 相同的评估请求会复用评估结果

## 日志记录

工作流使用Python标准logging模块记录执行日志：

```python
import logging

# 配置日志级别
logging.basicConfig(level=logging.INFO)

# 查看详细日志
logging.getLogger("src.workflows").setLevel(logging.DEBUG)
```

日志包含：
- 工作流开始/结束
- 每个步骤的执行
- 错误和异常信息
- 执行时间统计

## 与Agent的集成

工作流通过MCP协议与Agent通信：

```
Workflow → MCP Server → Agent
         ← MCP Server ←
```

**消息流程：**
1. 工作流创建MCPMessage
2. 通过MCP Server发送消息
3. Agent接收并处理消息
4. Agent返回响应
5. 工作流接收响应并继续

## 扩展工作流

可以基于现有工作流创建自定义工作流：

```python
from src.workflows import JDAnalysisWorkflow

class CustomJDWorkflow(JDAnalysisWorkflow):
    """自定义JD分析工作流"""
    
    async def execute_full_analysis(self, jd_text: str, **kwargs):
        # 添加预处理步骤
        jd_text = self._preprocess(jd_text)
        
        # 调用父类方法
        result = await super().execute_full_analysis(jd_text, **kwargs)
        
        # 添加后处理步骤
        result = self._postprocess(result)
        
        return result
    
    def _preprocess(self, jd_text: str) -> str:
        # 自定义预处理逻辑
        return jd_text.strip()
    
    def _postprocess(self, result: dict) -> dict:
        # 自定义后处理逻辑
        return result
```

## 测试

工作流测试示例：

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_jd_analysis_workflow():
    # Mock MCP Server
    mcp_server = MagicMock()
    mcp_server.send_message = AsyncMock()
    mcp_server.wait_for_response = AsyncMock(return_value=MagicMock(
        payload={"jd_id": "test_123", "parsed_data": {}}
    ))
    mcp_server.update_context = AsyncMock()
    
    # 创建工作流
    workflow = JDAnalysisWorkflow(mcp_server)
    
    # 执行测试
    result = await workflow.execute_full_analysis(
        jd_text="测试JD文本",
        evaluation_model="standard"
    )
    
    # 验证结果
    assert result["status"] == "completed"
    assert "jd_id" in result
    assert "parsed_data" in result
```

## 相关文档

- [MCP协议文档](../mcp/README.md)
- [Agent实现文档](../agents/README.md)
- [设计文档](../../.kiro/specs/jd-analyzer/design.md)
- [需求文档](../../.kiro/specs/jd-analyzer/requirements.md)
