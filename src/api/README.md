# FastAPI后端API文档

## 概述

岗位JD分析器的FastAPI后端实现，提供完整的RESTful API接口。

## 启动服务

### 方式1：直接运行
```bash
python -m src.api.main
```

### 方式2：使用uvicorn
```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API文档（Swagger UI）: http://localhost:8000/docs
- 替代文档（ReDoc）: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## API端点

### 1. JD分析相关 (`/api/v1/jd`)

#### POST /api/v1/jd/analyze
完整JD分析（解析+评估）

**请求体：**
```json
{
  "jd_text": "招聘高级Python工程师...",
  "model_type": "standard",
  "custom_fields": {}
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "jd": { ... },
    "evaluation": { ... }
  }
}
```

#### POST /api/v1/jd/parse
仅解析JD（不进行评估）

#### GET /api/v1/jd/{jd_id}
获取JD详情

#### GET /api/v1/jd/{jd_id}/evaluation
获取JD的评估结果

#### PUT /api/v1/jd/{jd_id}/category
手动更新JD分类

**请求体：**
```json
{
  "category_level1_id": "cat_tech",
  "category_level2_id": "cat_dev",
  "category_level3_id": "cat_backend"
}
```

#### POST /api/v1/jd/upload
单个文件上传并分析

**表单数据：**
- `file`: JD文件（TXT/PDF/DOCX）
- `model_type`: 评估模型类型（可选）

### 2. 职位分类管理 (`/api/v1/categories`)

#### POST /api/v1/categories
创建职位分类（支持添加样本JD）

**请求体：**
```json
{
  "name": "后端工程师",
  "level": 3,
  "parent_id": "cat_parent_001",
  "description": "负责后端系统开发",
  "sample_jd_ids": ["jd_001", "jd_002"]
}
```

#### GET /api/v1/categories
列出职位分类

**查询参数：**
- `level`: 筛选指定层级（可选）
- `parent_id`: 筛选指定父级的子分类（可选）

#### GET /api/v1/categories/tree
获取分类树（3层级结构）

#### GET /api/v1/categories/{category_id}
获取分类详情

#### PUT /api/v1/categories/{category_id}
更新分类

#### PUT /api/v1/categories/{category_id}/samples
更新样本JD（仅第三层级）

**请求体：**
```json
{
  "sample_jd_ids": ["jd_001", "jd_002"]
}
```

#### DELETE /api/v1/categories/{category_id}
删除分类（如果有子分类则无法删除）

### 3. 问卷管理 (`/api/v1/questionnaire`)

#### POST /api/v1/questionnaire/generate
生成问卷

**请求体：**
```json
{
  "jd_id": "jd_001",
  "evaluation_model": "standard",
  "title": "高级Python工程师评估问卷",
  "description": "请如实填写以下问题"
}
```

#### GET /api/v1/questionnaire/{questionnaire_id}
获取问卷

#### POST /api/v1/questionnaire/{questionnaire_id}/submit
提交问卷

**请求体：**
```json
{
  "respondent_name": "张三",
  "answers": {
    "q_001": "3-5年",
    "q_002": "熟练"
  }
}
```

#### GET /api/v1/questionnaire
列出问卷

**查询参数：**
- `jd_id`: 筛选指定JD的问卷（可选）

### 4. 匹配评估 (`/api/v1/match`)

#### GET /api/v1/match/{match_id}
获取匹配结果

#### GET /api/v1/match/{match_id}/report
下载匹配报告

**查询参数：**
- `format`: 报告格式（pdf/html/json，默认pdf）

#### GET /api/v1/match/jd/{jd_id}/matches
列出指定JD的所有匹配结果

#### GET /api/v1/match
列出所有匹配结果

### 5. 模板管理 (`/api/v1/templates`)

#### POST /api/v1/templates
创建模板

**请求体：**
```json
{
  "name": "技术岗位解析模板",
  "template_type": "parsing",
  "config": {
    "custom_fields": ["技术栈", "团队规模"]
  }
}
```

**模板类型：**
- `parsing`: 解析模板
- `evaluation`: 评估模板
- `questionnaire`: 问卷模板

#### GET /api/v1/templates
列出模板

**查询参数：**
- `template_type`: 筛选指定类型的模板（可选）

#### GET /api/v1/templates/{template_id}
获取模板详情

#### PUT /api/v1/templates/{template_id}
更新模板

#### DELETE /api/v1/templates/{template_id}
删除模板

### 6. 批量处理 (`/api/v1/batch`)

#### POST /api/v1/batch/upload
批量文件上传（最多20个）

**表单数据：**
- `files`: JD文件列表
- `model_type`: 评估模型类型（可选）

**响应：**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_abc123",
    "total_files": 10
  }
}
```

#### GET /api/v1/batch/status/{batch_id}
查询批量处理状态

**响应：**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_abc123",
    "status": "processing",
    "total_files": 10,
    "processed_files": 5,
    "successful_files": 4,
    "failed_files": 1
  }
}
```

#### GET /api/v1/batch/results/{batch_id}
获取批量处理结果

#### POST /api/v1/batch/analyze
批量分析JD文本

**请求体：**
```json
{
  "jd_texts": [
    "招聘Java工程师...",
    "招聘产品经理..."
  ],
  "model_type": "standard"
}
```

#### POST /api/v1/batch/match
批量匹配候选人

**请求体：**
```json
{
  "jd_id": "jd_001",
  "candidate_profiles": [
    {
      "name": "张三",
      "skills": ["Python", "FastAPI"],
      "experience": "3年"
    }
  ]
}
```

## 评估模型类型

- `standard`: 标准评估模型
- `mercer_ipe`: 美世国际职位评估法（IPE）
- `factor_comparison`: 因素比较法

## 错误处理

所有API端点遵循统一的错误响应格式：

```json
{
  "detail": "错误描述信息"
}
```

常见HTTP状态码：
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 测试

运行API测试：

```bash
# 完整测试（需要LLM配置）
python test_api.py

# 简单测试（不需要LLM）
python test_api_simple.py
```

## 注意事项

1. **LLM配置**：需要在`.env`文件中配置DeepSeek API密钥
2. **文件大小限制**：单个文件最大10MB，批量上传总计最大100MB
3. **批量处理限制**：最多20个文件或50个候选人
4. **分类层级**：职位分类最多支持3个层级
5. **样本JD**：只有第三层级分类可以添加样本JD，最多2个

## 开发

### 添加新端点

1. 在`src/api/routers/`目录下创建或编辑路由文件
2. 在`src/api/__init__.py`中注册路由
3. 添加相应的测试用例

### 目录结构

```
src/api/
├── __init__.py          # FastAPI应用初始化
├── main.py              # 服务启动入口
├── README.md            # API文档
└── routers/             # 路由模块
    ├── __init__.py
    ├── jd.py            # JD分析端点
    ├── categories.py    # 职位分类端点
    ├── questionnaire.py # 问卷管理端点
    ├── match.py         # 匹配评估端点
    ├── templates.py     # 模板管理端点
    └── batch.py         # 批量处理端点
```
