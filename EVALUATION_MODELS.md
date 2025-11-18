# 评估模型说明

## 概述

系统支持三种职位评估模型，每种模型都有不同的评估维度和权重。

## 已实现的评估模型

### 1. 标准评估模型 (Standard)

**模型 ID**: `standard`

**评估维度**:
- 完整性 (Completeness) - 30%
- 清晰度 (Clarity) - 30%
- 专业性 (Professionalism) - 25%
- 吸引力 (Attractiveness) - 15%

**适用场景**:
- 通用职位评估
- 快速质量检查
- 日常 JD 审核

**特点**:
- 全面评估 JD 质量
- 识别常见问题
- 提供优化建议

---

### 2. 美世国际职位评估法 (Mercer IPE)

**模型 ID**: `mercer_ipe`

**评估维度**:
- 影响力 (Impact) - 35%
- 沟通 (Communication) - 25%
- 创新 (Innovation) - 20%
- 知识技能 (Knowledge & Skills) - 20%

**适用场景**:
- 职位价值评估
- 薪酬体系设计
- 组织架构优化
- 岗位等级划分

**特点**:
- 国际标准评估方法
- 关注岗位对组织的价值
- 适合大中型企业
- 支持跨部门比较

**评估标准**:

#### 影响力 (35%)
- 岗位对组织目标的贡献
- 决策权限和影响范围
- 对业务结果的直接影响
- 管理的资源规模

#### 沟通 (25%)
- 沟通的复杂度和频率
- 内外部沟通要求
- 跨部门协作需求
- 对外代表公司的程度

#### 创新 (20%)
- 问题解决的复杂度
- 创新和改进的要求
- 应对变化的能力
- 战略思维要求

#### 知识技能 (20%)
- 专业知识深度
- 技能广度要求
- 学习和适应能力
- 行业经验要求

---

### 3. 因素比较法 (Factor Comparison)

**模型 ID**: `factor_comparison`

**评估维度**:
- 技能要求 (Skills) - 30%
- 责任程度 (Responsibility) - 30%
- 努力程度 (Effort) - 20%
- 工作条件 (Working Conditions) - 20%

**适用场景**:
- 薪酬设计
- 职位分级
- 内部公平性分析
- 市场对标

**特点**:
- 关注补偿性因素
- 适合薪酬管理
- 量化评估标准
- 支持市场比较

---

## 使用方法

### 在 UI 中使用

1. 打开 JD 分析页面
2. 在侧边栏选择评估模型：
   - 标准评估
   - 美世国际职位评估法
   - 因素比较法
3. 输入或上传 JD
4. 点击"开始分析"

### 在 API 中使用

```python
# 使用标准模型
POST /api/v1/jd/analyze
{
    "jd_text": "...",
    "model_type": "standard"
}

# 使用美世法
POST /api/v1/jd/analyze
{
    "jd_text": "...",
    "model_type": "mercer_ipe"
}

# 使用因素比较法
POST /api/v1/jd/analyze
{
    "jd_text": "...",
    "model_type": "factor_comparison"
}
```

### 在代码中使用

```python
from src.mcp.simple_client import get_simple_mcp_client
from src.models.schemas import EvaluationModel

client = get_simple_mcp_client()

# 使用美世法评估
result = await client.analyze_jd(
    jd_text="...",
    model_type=EvaluationModel.MERCER_IPE
)

# 或使用字符串
result = await client.analyze_jd(
    jd_text="...",
    model_type="mercer_ipe"
)
```

## 评估结果

所有模型都返回统一的结果格式：

```json
{
    "jd": {
        "id": "jd_abc123",
        "job_title": "高级Python工程师",
        "responsibilities": [...],
        "required_skills": [...],
        ...
    },
    "evaluation": {
        "id": "eval_xyz789",
        "jd_id": "jd_abc123",
        "model_type": "mercer_ipe",
        "quality_score": {
            "overall_score": 85.0,
            "completeness": 90.0,
            "clarity": 80.0,
            "professionalism": 85.0,
            "issues": []
        },
        "recommendations": [
            "建议1",
            "建议2"
        ]
    }
}
```

## 模型对比

| 特性 | 标准评估 | 美世法 | 因素比较法 |
|------|---------|--------|-----------|
| 评估重点 | JD质量 | 岗位价值 | 薪酬因素 |
| 适用场景 | 通用 | 组织管理 | 薪酬设计 |
| 复杂度 | 低 | 中 | 中 |
| 国际标准 | ❌ | ✅ | ✅ |
| 薪酬相关 | ❌ | ✅ | ✅ |

## 选择建议

### 使用标准评估，如果你需要：
- ✅ 快速检查 JD 质量
- ✅ 识别常见问题
- ✅ 获取优化建议
- ✅ 日常 JD 审核

### 使用美世法，如果你需要：
- ✅ 评估岗位价值
- ✅ 设计薪酬体系
- ✅ 划分岗位等级
- ✅ 组织架构优化
- ✅ 国际标准评估

### 使用因素比较法，如果你需要：
- ✅ 薪酬设计
- ✅ 内部公平性分析
- ✅ 市场对标
- ✅ 职位分级

## 扩展新模型

如果需要添加新的评估模型：

1. 在 `src/agents/evaluator_agent.py` 中创建新模型类：

```python
class CustomEvaluationModel(EvaluationModelBase):
    """自定义评估模型"""
    
    def __init__(self):
        super().__init__()
        self.dimensions = ["维度1", "维度2"]
        self.weights = {"维度1": 0.6, "维度2": 0.4}
    
    async def evaluate(self, jd_data: Dict, llm_client) -> Dict:
        # 实现评估逻辑
        pass
```

2. 在 EvaluatorAgent 中注册：

```python
self.evaluation_models = {
    "standard": StandardEvaluationModel(),
    "mercer_ipe": MercerIPEModel(),
    "factor_comparison": FactorComparisonModel(),
    "custom": CustomEvaluationModel()  # 新增
}
```

3. 在 `src/models/schemas.py` 中添加枚举：

```python
class EvaluationModel(str, Enum):
    STANDARD = "standard"
    MERCER_IPE = "mercer_ipe"
    FACTOR_COMPARISON = "factor_comparison"
    CUSTOM = "custom"  # 新增
```

## 总结

系统已完整实现三种评估模型，包括美世国际职位评估法。所有模型都可以通过 UI 或 API 使用，支持灵活的评估需求。

---

**文档版本**: 1.0  
**最后更新**: 2024年
