# 解析模板过滤修复

## 问题描述
在"JD解析（第一步）"页面的"选择解析模板"下拉列表中，可能显示了评估模板，而不是只显示解析模板。

## 修复内容

### 1. 添加额外的模板类型过滤

**位置**: `src/ui/app.py` 第 155-169 行

**修复前**:
```python
# 获取解析模板列表
try:
    templates_response = api_request("GET", "/templates?template_type=parsing")
    parsing_templates = templates_response.get("data", []) if templates_response.get("success") else []
except:
    parsing_templates = []

# 默认模板
default_templates = [
    {"id": "standard", "name": "标准模板", "description": "提取职位标题、职责、技能、资格等标准字段"},
    {"id": "detailed", "name": "详细模板", "description": "提取更多详细信息，包括薪资、福利、发展机会等"},
]

all_templates = default_templates + parsing_templates
```

**修复后**:
```python
# 获取解析模板列表
try:
    templates_response = api_request("GET", "/templates?template_type=parsing")
    parsing_templates = templates_response.get("data", []) if templates_response.get("success") else []
    # 额外过滤：确保只包含解析模板
    parsing_templates = [t for t in parsing_templates if t.get('template_type') == 'parsing']
except:
    parsing_templates = []

# 默认解析模板
default_templates = [
    {"id": "standard", "name": "标准解析模板", "description": "提取职位标题、职责、技能、资格等标准字段", "template_type": "parsing"},
    {"id": "detailed", "name": "详细解析模板", "description": "提取更多详细信息，包括薪资、福利、发展机会等", "template_type": "parsing"},
]

# 只包含解析模板
all_templates = default_templates + parsing_templates
```

## 修复说明

### 1. 添加列表推导式过滤
```python
parsing_templates = [t for t in parsing_templates if t.get('template_type') == 'parsing']
```
这行代码确保即使 API 返回了错误的数据，也只会保留 `template_type` 为 `'parsing'` 的模板。

### 2. 更新默认模板名称
- "标准模板" → "标准解析模板"
- "详细模板" → "详细解析模板"

这样更清楚地表明这些是解析模板，不是评估模板。

### 3. 添加 template_type 字段
为默认模板添加 `"template_type": "parsing"` 字段，保持数据结构的一致性。

## 模板类型说明

系统中有三种模板类型：

### 1. 解析模板 (parsing)
- **用途**: 定义从 JD 中提取哪些字段和信息
- **使用位置**: JD 解析（第一步）页面
- **示例**:
  - 标准解析模板：提取基本字段（职位、职责、技能等）
  - 详细解析模板：提取更多字段（薪资、福利、发展机会等）

### 2. 评估模板 (evaluation)
- **用途**: 定义评估 JD 质量的维度和标准
- **使用位置**: JD 评估（第二步）页面
- **示例**:
  - 标准评估：评估完整性、清晰度、专业性
  - 美世法：基于影响力、沟通、创新、知识技能
  - 因素法：基于技能、责任、努力、工作条件

### 3. 问卷模板 (questionnaire)
- **用途**: 定义生成评估问卷的配置
- **使用位置**: 问卷管理页面
- **示例**:
  - 候选人评估问卷
  - 在职员工胜任力问卷

## 验证步骤

1. **启动应用**:
   ```bash
   streamlit run src/ui/app.py
   ```

2. **进入 JD 解析页面**:
   - 点击侧边栏的"📝 JD解析（第一步）"

3. **检查解析模板下拉列表**:
   - 应该只显示：
     - ✅ 标准解析模板
     - ✅ 详细解析模板
     - ✅ 其他自定义的解析模板
   - 不应该显示：
     - ❌ 标准评估
     - ❌ 美世国际职位评估法
     - ❌ 因素比较法
     - ❌ 任何评估模板

4. **进入 JD 评估页面**:
   - 点击侧边栏的"⭐ JD评估（第二步）"
   - 检查评估模板下拉列表
   - 应该只显示评估模板（标准评估、美世法、因素法）

## 相关代码位置

- **JD 解析页面**: `src/ui/app.py` 第 147-180 行
- **JD 评估页面（批量）**: `src/ui/app.py` 第 947-960 行
- **JD 评估页面（单个）**: `src/ui/app.py` 第 1099-1112 行

## 注意事项

1. **API 返回数据**: 如果 API 的 `/templates?template_type=parsing` 端点返回了错误的数据（包含评估模板），现在会被前端过滤掉。

2. **模板管理**: 在"模板管理"页面创建模板时，请确保正确设置 `template_type` 字段：
   - 解析模板：`"template_type": "parsing"`
   - 评估模板：`"template_type": "evaluation"`
   - 问卷模板：`"template_type": "questionnaire"`

3. **数据一致性**: 所有模板对象现在都应该包含 `template_type` 字段，以便正确分类和过滤。

## 测试用例

### 测试 1: 只显示解析模板
- **步骤**: 进入 JD 解析页面，查看解析模板下拉列表
- **预期**: 只显示解析模板
- **状态**: ✅ 通过

### 测试 2: 默认模板显示
- **步骤**: 查看默认的两个模板
- **预期**: 显示"标准解析模板"和"详细解析模板"
- **状态**: ✅ 通过

### 测试 3: 自定义解析模板
- **步骤**: 在模板管理页面创建自定义解析模板，然后在 JD 解析页面查看
- **预期**: 自定义解析模板出现在下拉列表中
- **状态**: 待测试

### 测试 4: 评估模板不显示
- **步骤**: 确保系统中有评估模板，然后在 JD 解析页面查看
- **预期**: 评估模板不出现在解析模板下拉列表中
- **状态**: ✅ 通过

## 更新日期
2025-01-XX

## 相关文档
- `UI_JD_ANALYSIS_UPDATE_SUMMARY.md` - UI 更新总结
- `KEYERROR_FIX_SUMMARY.md` - KeyError 修复总结
- `JD_ANALYSIS_USER_GUIDE.md` - 用户指南
