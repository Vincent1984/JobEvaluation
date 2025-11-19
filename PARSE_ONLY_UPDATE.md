# JD 解析流程更新 - 只解析不评估

## 更新说明

根据您的反馈，我已经修改了 JD 解析流程，使其符合两步式工作流程的设计理念：

**第一步（JD 解析）**：只解析 JD，提取结构化信息，不进行评估  
**第二步（JD 评估）**：选择分类、评估模板，进行综合评估

## 修改内容

### 文件: `src/ui/app.py`

#### 1. API 调用修改

**修改前**:
```python
# 调用 /jd/analyze 端点（解析 + 评估）
response = api_request(
    "POST",
    "/jd/analyze",
    json={
        "jd_text": jd_text,
        "model_type": model_type  # ❌ 第一步不应该需要评估模型
    }
)
```

**修改后**:
```python
# 只调用 /jd/parse 端点（只解析）
response = api_request(
    "POST",
    "/jd/parse",  # ✅ 只解析，不评估
    json={
        "jd_text": jd_text,
        "custom_fields": {}  # ✅ 只需要解析模板配置
    }
)
```

#### 2. 数据处理修改

**修改前**:
```python
# 处理解析和评估结果
jd_data = data.get("jd", {})
eval_data = data.get("evaluation", {})  # ❌ 第一步不应该有评估

jd = JobDescription(**jd_data)
evaluation = EvaluationResult(**eval_data)  # ❌ 不需要

# 保存 JD 和评估
st.session_state.analysis_history.append({
    "jd": jd,
    "evaluation": evaluation,  # ❌ 不需要
    "timestamp": jd.created_at
})
```

**修改后**:
```python
# 只处理解析结果
jd_data = response.get("data", {})

jd = JobDescription(**jd_data)

# 只保存 JD，不保存评估
st.session_state.analysis_history.append({
    "jd": jd,
    "evaluation": None,  # ✅ 第一步不进行评估
    "timestamp": jd.created_at
})
```

#### 3. UI 显示修改

**修改前**:
```python
# 显示三个标签页：解析结果、质量评估、优化建议
tab1, tab2, tab3 = st.tabs(["📊 解析结果", "⭐ 质量评估", "💡 优化建议"])

with tab1:
    # 显示解析结果
    ...

with tab2:
    # 显示评估结果 ❌ 第一步不应该有
    ...

with tab3:
    # 显示优化建议 ❌ 第一步不应该有
    ...
```

**修改后**:
```python
# 只显示解析结果
st.subheader("📊 解析结果")

# 显示职位标题、部门、地点
col1, col2, col3 = st.columns(3)
...

# 显示职责、技能、资格
...

# 提示用户进入第二步
st.success("✅ JD 解析完成并已保存！")
st.info("💡 下一步：前往'⭐ JD评估（第二步）'页面进行评估、选择分类和评估模板")
```

#### 4. 提示信息修改

**修改前**:
```python
with st.spinner("🤖 AI正在分析中..."):  # ❌ "分析"包含评估
    ...
st.success("✅ 分析完成！")  # ❌ 不准确
```

**修改后**:
```python
with st.spinner("🤖 AI正在解析中..."):  # ✅ 只是解析
    ...
st.success("✅ 解析完成！JD 已保存")  # ✅ 准确
st.info("💡 提示：前往'JD评估（第二步）'页面进行评估和分类")
```

## 工作流程

### 新的两步式流程

```
第一步：JD 解析与保存
├─ 输入：解析模板 + JD 文本
├─ 处理：AI 根据模板提取结构化信息
├─ 输出：JobDescription 对象
└─ 保存：存储到 session_state

第二步：JD 评估与分析
├─ 输入：已保存的 JD + 评估模板 + 职位分类
├─ 处理：AI 综合三个维度进行评估
│  ├─ JD 内容
│  ├─ 评估模板
│  └─ 分类标签
├─ 输出：EvaluationResult 对象
└─ 显示：评估结果、企业价值、核心岗位判断
```

## API 端点使用

### 第一步使用的端点

**POST /jd/parse**
- 功能：只解析 JD，提取结构化信息
- 输入：
  - `jd_text`: JD 文本
  - `custom_fields`: 自定义字段配置（可选）
- 输出：
  - `JobDescription` 对象

### 第二步使用的端点

**POST /jd/{jd_id}/evaluate**
- 功能：评估已保存的 JD
- 输入：
  - `jd_id`: JD 的唯一标识符
  - `model_type`: 评估模型类型
  - `category_level3_id`: 第三层级分类 ID（可选）
- 输出：
  - `EvaluationResult` 对象

## 优势

### 1. 职责分离
- 第一步专注于解析，快速提取信息
- 第二步专注于评估，深度分析价值

### 2. 灵活性提升
- 可以先批量解析多个 JD
- 然后统一进行评估和分类
- 同一个 JD 可以用不同模板多次评估

### 3. 性能优化
- 解析速度更快（不需要评估）
- 评估可以按需进行
- 减少不必要的 API 调用

### 4. 用户体验改善
- 流程更清晰，步骤更明确
- 用户可以先快速解析，后续再评估
- 符合实际使用场景

## 使用示例

### 场景 1: 单个 JD 处理

```
1. 进入"JD 解析（第一步）"
   - 选择"标准解析模板"
   - 输入 JD 文本
   - 点击"解析并保存"
   - ✅ 查看解析结果（职位、职责、技能等）
   
2. 进入"JD 评估（第二步）"
   - 选择刚才保存的 JD
   - 选择"标准评估"模板
   - 选择职位分类
   - 点击"提交评估"
   - ✅ 查看评估结果（分数、价值、核心岗位）
```

### 场景 2: 批量 JD 处理

```
1. 批量解析（第一步）
   - 解析 JD A
   - 解析 JD B
   - 解析 JD C
   - ✅ 所有 JD 已保存
   
2. 批量评估（第二步）
   - 选择多个 JD
   - 选择评估模板
   - 为每个 JD 选择分类
   - 批量提交评估
   - ✅ 查看汇总结果
```

## 数据流

### 第一步：解析

```
用户输入
  ↓
解析模板 + JD 文本
  ↓
API: POST /jd/parse
  ↓
AI 提取结构化信息
  ↓
JobDescription 对象
  ↓
保存到 session_state
  ↓
显示解析结果
```

### 第二步：评估

```
选择已保存的 JD
  ↓
评估模板 + 职位分类
  ↓
API: POST /jd/{jd_id}/evaluate
  ↓
AI 综合评估（三个维度）
  ↓
EvaluationResult 对象
  ↓
显示评估结果
```

## 测试验证

### 测试步骤

1. **启动 UI**:
   ```bash
   streamlit run src/ui/app.py
   ```

2. **测试第一步（解析）**:
   - 进入"📝 JD解析（第一步）"
   - 输入 JD 文本
   - 点击"解析并保存"
   - ✅ 应该只显示解析结果
   - ✅ 不应该显示评估分数
   - ✅ 应该提示进入第二步

3. **测试第二步（评估）**:
   - 进入"⭐ JD评估（第二步）"
   - 选择刚才保存的 JD
   - 选择评估模板和分类
   - 点击"提交评估"
   - ✅ 应该显示完整的评估结果

### 预期结果

#### 第一步输出

```
📊 解析结果

职位标题: 高级Python工程师
部门: 技术研发部
地点: 北京

职责描述:
1. 负责公司核心业务系统的后端开发和维护
2. 参与系统架构设计，优化系统性能和稳定性

必备技能:
- 3年以上Python开发经验
- 熟练掌握FastAPI、Django等Web框架

任职资格:
- 本科及以上学历，计算机相关专业优先

---
✅ JD 解析完成并已保存！
💡 下一步：前往'⭐ JD评估（第二步）'页面进行评估、选择分类和评估模板
```

#### 第二步输出

```
📊 评估结果

综合质量分数: 85.0
企业价值: 高价值
核心岗位: 是

评估维度贡献度:
- JD内容: 40%
- 评估模板: 30%
- 分类标签: 30%

[详细评估报告...]
```

## 相关文档

- `WORKFLOW_UPDATE.md` - 工作流程更新说明
- `API_500_ERROR_FIX.md` - API 错误修复
- `JD_ANALYSIS_USER_GUIDE.md` - 用户指南

## 更新日期

2025-01-XX

## 状态

✅ 修改完成，等待测试验证
