# ✅ 美世国际职位评估法模板已添加

## 更新内容

在模板管理中添加了两个新的评估模板：

### 1. 美世国际职位评估法模板

**模板 ID**: `tmpl_mercer_ipe`

**模板名称**: 美世国际职位评估法模板

**模板类型**: evaluation

**配置内容**:
```json
{
    "model": "mercer_ipe",
    "dimensions": ["影响力", "沟通", "创新", "知识技能"],
    "weights": {
        "影响力": 0.35,
        "沟通": 0.25,
        "创新": 0.20,
        "知识技能": 0.20
    },
    "description": "美世国际职位评估法（Mercer IPE）是一种国际标准的岗位评估方法，从影响力、沟通、创新和知识技能四个维度评估岗位价值",
    "适用场景": ["职位价值评估", "薪酬体系设计", "组织架构优化", "岗位等级划分"]
}
```

### 2. 因素比较法模板

**模板 ID**: `tmpl_factor_comparison`

**模板名称**: 因素比较法模板

**模板类型**: evaluation

**配置内容**:
```json
{
    "model": "factor_comparison",
    "dimensions": ["技能要求", "责任程度", "努力程度", "工作条件"],
    "weights": {
        "技能要求": 0.30,
        "责任程度": 0.30,
        "努力程度": 0.20,
        "工作条件": 0.20
    },
    "description": "因素比较法是一种基于补偿性因素的岗位评估方法，适合薪酬设计和职位分级",
    "适用场景": ["薪酬设计", "职位分级", "内部公平性分析", "市场对标"]
}
```

## 现有模板列表

系统现在包含以下预设模板：

1. **标准解析模板** (`tmpl_default_parsing`)
   - 类型: parsing
   - 用途: 标准 JD 解析

2. **技术岗位解析模板** (`tmpl_tech_parsing`)
   - 类型: parsing
   - 用途: 技术岗位 JD 解析（包含技术栈、团队规模等）

3. **标准评估模板** (`tmpl_standard_eval`)
   - 类型: evaluation
   - 用途: 通用 JD 质量评估

4. **美世国际职位评估法模板** (`tmpl_mercer_ipe`) - ✨ 新增
   - 类型: evaluation
   - 用途: 岗位价值评估

5. **因素比较法模板** (`tmpl_factor_comparison`) - ✨ 新增
   - 类型: evaluation
   - 用途: 薪酬设计和职位分级

## 如何使用

### 通过 API 获取模板列表

```bash
GET http://localhost:8000/api/v1/templates
```

### 获取美世法模板详情

```bash
GET http://localhost:8000/api/v1/templates/tmpl_mercer_ipe
```

### 在 UI 中使用

1. 访问 http://localhost:8501
2. 进入"模板管理"页面
3. 查看预设模板列表
4. 选择"美世国际职位评估法模板"
5. 查看模板详情和配置

### 使用模板进行评估

虽然模板已添加，但实际评估时直接使用评估模型即可：

```python
# 在 JD 分析时选择美世法
result = await client.analyze_jd(
    jd_text="...",
    model_type="mercer_ipe"
)
```

或在 UI 侧边栏选择"美世国际职位评估法"。

## 模板的作用

模板主要用于：

1. **配置管理**: 保存和管理不同的评估配置
2. **快速应用**: 快速应用预设的评估标准
3. **自定义**: 用户可以基于模板创建自己的配置
4. **文档化**: 记录评估方法的详细信息

## 扩展建议

如果需要添加更多模板，可以在 `init_default_templates()` 函数中添加：

```python
CustomTemplate(
    id="tmpl_custom",
    name="自定义模板名称",
    template_type="evaluation",  # 或 parsing, questionnaire
    config={
        # 模板配置
    },
    created_at=datetime.now()
)
```

## 文件修改

- ✅ `src/api/routers/templates.py` - 添加美世法和因素比较法模板

## 测试

重启服务后测试：

```bash
# 1. 获取所有模板
curl http://localhost:8000/api/v1/templates

# 2. 获取评估类型模板
curl http://localhost:8000/api/v1/templates?template_type=evaluation

# 3. 获取美世法模板详情
curl http://localhost:8000/api/v1/templates/tmpl_mercer_ipe
```

## 状态

✅ 美世国际职位评估法模板已成功添加到系统中！

---

**添加日期**: 2024年  
**添加人**: Kiro AI Assistant
