# Bug 修复：model_type 类型问题

## 问题描述

错误信息：
```
❌ 分析失败: 'str' object has no attribute 'value'
```

## 原因分析

在 UI 中，`model_type` 被设置为字符串值：
```python
model_type = st.selectbox(...)[1]  # 返回 "standard", "mercer_ipe" 等字符串
```

但在 `SimpleMCPClient.analyze_jd()` 方法中，代码尝试访问 `model_type.value`：
```python
model_type_str = model_type.value  # ❌ 字符串没有 .value 属性
```

## 解决方案

修改 `SimpleMCPClient.analyze_jd()` 方法，支持两种类型的 `model_type`：

```python
# 处理 model_type（可能是枚举或字符串）
if isinstance(model_type, str):
    model_type_str = model_type
else:
    model_type_str = model_type.value

# 选择评估模型
model = self._evaluator_agent.evaluation_models.get(model_type_str)
```

同时，在创建 `EvaluationResult` 时，确保 `model_type` 是枚举：

```python
# 确保 model_type 是 EvaluationModel 枚举
if isinstance(model_type, str):
    model_type_enum = EvaluationModel(model_type)
else:
    model_type_enum = model_type

evaluation = EvaluationResult(
    ...
    model_type=model_type_enum,
    ...
)
```

## 修复文件

- ✅ `src/mcp/simple_client.py`

## 测试

重启服务后测试：
```bash
# 访问 UI
http://localhost:8501

# 测试 JD 分析功能
# 1. 输入 JD 文本
# 2. 选择评估模型
# 3. 点击"开始分析"
# 4. 应该能正常显示结果
```

## 状态

✅ 已修复并重启服务

---

**修复日期**: 2024年  
**修复人**: Kiro AI Assistant
