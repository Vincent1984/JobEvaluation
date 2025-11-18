# FastAPI后端快速开始指南

## 快速启动

### 1. 启动API服务器

```bash
# 方式1：使用Python模块
python -m src.api.main

# 方式2：使用uvicorn（推荐开发环境）
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 2. 测试API

```bash
# 运行简单测试（不需要LLM配置）
python test_api_simple.py
```

## 核心功能演示

### 1. 职位分类管理

#### 创建分类层级
```bash
# 创建一级分类
curl -X POST "http://localhost:8000/api/v1/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "技术类",
    "level": 1,
    "description": "技术相关岗位"
  }'

# 创建二级分类（需要parent_id）
curl -X POST "http://localhost:8000/api/v1/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "研发",
    "level": 2,
    "parent_id": "cat_xxx",
    "description": "研发岗位"
  }'

# 创建三级分类（可添加样本JD）
curl -X POST "http://localhost:8000/api/v1/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "后端工程师",
    "level": 3,
    "parent_id": "cat_yyy",
    "sample_jd_ids": ["jd_001", "jd_002"]
  }'
```

#### 查询分类
```bash
# 获取分类树
curl "http://localhost:8000/api/v1/categories/tree"

# 列出所有分类
curl "http://localhost:8000/api/v1/categories"

# 筛选指定层级
curl "http://localhost:8000/api/v1/categories?level=3"
```

### 2. JD分析

#### 解析JD
```bash
curl -X POST "http://localhost:8000/api/v1/jd/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "jd_text": "招聘高级Python工程师\n\n岗位职责：\n1. 负责后端服务开发\n2. 优化系统性能\n\n任职要求：\n- 3年以上Python开发经验\n- 熟悉FastAPI、Django等框架"
  }'
```

#### 完整分析（解析+评估）
```bash
curl -X POST "http://localhost:8000/api/v1/jd/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "jd_text": "招聘前端工程师...",
    "model_type": "standard"
  }'
```

#### 文件上传
```bash
curl -X POST "http://localhost:8000/api/v1/jd/upload" \
  -F "file=@job_description.txt" \
  -F "model_type=standard"
```

### 3. 批量处理

#### 批量上传文件
```bash
curl -X POST "http://localhost:8000/api/v1/batch/upload" \
  -F "files=@jd1.txt" \
  -F "files=@jd2.pdf" \
  -F "files=@jd3.docx" \
  -F "model_type=standard"
```

响应会返回batch_id，用于查询进度：
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_abc123",
    "total_files": 3
  }
}
```

#### 查询批量处理状态
```bash
curl "http://localhost:8000/api/v1/batch/status/batch_abc123"
```

#### 获取批量处理结果
```bash
curl "http://localhost:8000/api/v1/batch/results/batch_abc123"
```

#### 批量分析JD文本
```bash
curl -X POST "http://localhost:8000/api/v1/batch/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "jd_texts": [
      "招聘Java工程师，要求3年经验",
      "招聘产品经理，要求5年经验",
      "招聘UI设计师，要求熟悉Figma"
    ],
    "model_type": "standard"
  }'
```

### 4. 问卷管理

#### 生成问卷
```bash
curl -X POST "http://localhost:8000/api/v1/questionnaire/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "jd_id": "jd_001",
    "evaluation_model": "standard",
    "title": "高级Python工程师评估问卷"
  }'
```

#### 提交问卷
```bash
curl -X POST "http://localhost:8000/api/v1/questionnaire/quest_001/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "respondent_name": "张三",
    "answers": {
      "q_001": "3-5年",
      "q_002": "熟练",
      "q_003": "有"
    }
  }'
```

### 5. 匹配评估

#### 获取匹配结果
```bash
curl "http://localhost:8000/api/v1/match/match_001"
```

#### 下载匹配报告
```bash
# JSON格式
curl "http://localhost:8000/api/v1/match/match_001/report?format=json" -o report.json

# HTML格式
curl "http://localhost:8000/api/v1/match/match_001/report?format=html" -o report.html
```

#### 列出JD的所有匹配
```bash
curl "http://localhost:8000/api/v1/match/jd/jd_001/matches"
```

### 6. 模板管理

#### 创建模板
```bash
curl -X POST "http://localhost:8000/api/v1/templates" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "技术岗位解析模板",
    "template_type": "parsing",
    "config": {
      "custom_fields": ["技术栈", "团队规模", "汇报关系"]
    }
  }'
```

#### 列出模板
```bash
# 所有模板
curl "http://localhost:8000/api/v1/templates"

# 按类型筛选
curl "http://localhost:8000/api/v1/templates?template_type=parsing"
```

## Python客户端示例

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000"

# 1. 创建分类
response = requests.post(
    f"{BASE_URL}/api/v1/categories",
    json={
        "name": "技术类",
        "level": 1,
        "description": "技术相关岗位"
    }
)
category = response.json()
print(f"创建分类: {category['data']['id']}")

# 2. 解析JD
response = requests.post(
    f"{BASE_URL}/api/v1/jd/parse",
    json={
        "jd_text": "招聘高级Python工程师..."
    }
)
jd = response.json()
print(f"解析JD: {jd['data']['job_title']}")

# 3. 生成问卷
response = requests.post(
    f"{BASE_URL}/api/v1/questionnaire/generate",
    json={
        "jd_id": jd['data']['id'],
        "evaluation_model": "standard"
    }
)
questionnaire = response.json()
print(f"生成问卷: {len(questionnaire['data']['questions'])}个问题")

# 4. 批量上传
files = [
    ('files', open('jd1.txt', 'rb')),
    ('files', open('jd2.txt', 'rb'))
]
response = requests.post(
    f"{BASE_URL}/api/v1/batch/upload",
    files=files,
    data={'model_type': 'standard'}
)
batch = response.json()
print(f"批量上传: {batch['data']['batch_id']}")
```

## 常见问题

### Q: 如何配置DeepSeek API？
A: 在`.env`文件中设置：
```
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
```

### Q: 批量上传有什么限制？
A: 
- 最多20个文件
- 单个文件最大10MB
- 总大小最大100MB
- 支持TXT、PDF、DOCX格式

### Q: 如何查看API文档？
A: 启动服务后访问 http://localhost:8000/docs

### Q: 分类层级有什么规则？
A:
- 最多3个层级
- 一级分类不能有父级
- 二级和三级必须指定父级
- 只有第三层级可以添加样本JD（最多2个）

### Q: 如何测试API？
A: 运行 `python test_api_simple.py` 进行基础测试

## 下一步

1. 查看完整API文档：`src/api/README.md`
2. 运行测试：`python test_api_simple.py`
3. 浏览Swagger UI：http://localhost:8000/docs
4. 集成到Streamlit前端

## 技术支持

- API文档：http://localhost:8000/docs
- 项目README：README.md
- 任务文档：.kiro/specs/jd-analyzer/tasks.md
