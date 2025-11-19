# API 端点修复说明

## 问题描述
在"JD评估（第二步）"页面尝试获取已保存的 JD 列表时，出现 404 错误：
```
API请求失败: 404 Client Error: Not Found for url: http://localhost:8000/api/v1/jd/list
```

## 问题原因
UI 代码中使用了一个尚未实现的 API 端点 `GET /jd/list`。

## 临时解决方案

### 使用 session_state 存储 JD 数据

**位置**: `src/ui/app.py` 第 867-885 行

**修复前**:
```python
try:
    jds_response = api_request("GET", "/jd/list")
    saved_jds = jds_response.get("data", []) if jds_response.get("success") else []
except:
    saved_jds = []
```

**修复后**:
```python
# 暂时从 session_state 获取已保存的 JD
# TODO: 实现 API 端点 GET /jd/list 后替换此逻辑
if "analysis_history" in st.session_state and st.session_state.analysis_history:
    saved_jds = []
    for record in st.session_state.analysis_history:
        jd = record.get("jd")
        if jd:
            jd_dict = {
                "id": jd.id,
                "job_title": jd.job_title,
                "department": jd.department,
                "location": jd.location,
                "created_at": jd.created_at.isoformat() if hasattr(jd.created_at, 'isoformat') else str(jd.created_at),
                "category_level3_id": getattr(jd, 'category_level3_id', None),
                "evaluation_status": record.get("evaluation") is not None
            }
            saved_jds.append(jd_dict)
else:
    saved_jds = []
```

## 工作原理

### 1. 数据来源
现在从 Streamlit 的 `session_state` 中获取已保存的 JD，而不是从 API。

### 2. 数据转换
将 `JobDescription` 对象转换为字典格式，包含以下字段：
- `id`: JD 唯一标识符
- `job_title`: 职位标题
- `department`: 部门
- `location`: 地点
- `created_at`: 创建时间
- `category_level3_id`: 第三层级分类 ID
- `evaluation_status`: 是否已评估

### 3. 数据流程

```
JD 解析（第一步）
    ↓
保存到 session_state.analysis_history
    ↓
JD 评估（第二步）
    ↓
从 session_state 读取 JD 列表
    ↓
显示在评估页面
```

## 限制和注意事项

### 1. 数据持久性
- ⚠️ **session_state 数据不持久化**：刷新页面或重启应用后，数据会丢失
- ⚠️ **仅在当前会话有效**：不同浏览器标签页之间不共享数据

### 2. 适用场景
这个临时方案适用于：
- ✅ 开发和测试阶段
- ✅ 演示和原型验证
- ✅ 单用户单会话使用

不适用于：
- ❌ 生产环境
- ❌ 多用户协作
- ❌ 需要数据持久化的场景

## 长期解决方案

### 需要实现的 API 端点

#### 1. GET /jd/list
获取所有已保存的 JD 列表

**请求**:
```http
GET /api/v1/jd/list
```

**查询参数**:
- `skip` (可选): 跳过的记录数，默认 0
- `limit` (可选): 返回的记录数，默认 100
- `search` (可选): 搜索关键词（职位标题）
- `status` (可选): 筛选状态（evaluated/not_evaluated）

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": "jd_123",
      "job_title": "高级Python工程师",
      "department": "技术研发部",
      "location": "北京",
      "created_at": "2025-01-20T10:30:00",
      "category_level1_id": "cat1_001",
      "category_level2_id": "cat2_001",
      "category_level3_id": "cat3_001",
      "evaluation_status": true
    }
  ],
  "total": 1
}
```

#### 2. GET /jd/{jd_id}
获取单个 JD 的详细信息

**请求**:
```http
GET /api/v1/jd/{jd_id}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": "jd_123",
    "job_title": "高级Python工程师",
    "department": "技术研发部",
    "location": "北京",
    "responsibilities": ["职责1", "职责2"],
    "required_skills": ["技能1", "技能2"],
    "preferred_skills": ["技能3"],
    "qualifications": ["资格1"],
    "raw_text": "原始JD文本...",
    "category_level1_id": "cat1_001",
    "category_level2_id": "cat2_001",
    "category_level3_id": "cat3_001",
    "category_tags": [...],
    "created_at": "2025-01-20T10:30:00",
    "updated_at": "2025-01-20T10:30:00"
  }
}
```

#### 3. POST /jd/{jd_id}/evaluate
提交 JD 评估请求

**请求**:
```http
POST /api/v1/jd/{jd_id}/evaluate
Content-Type: application/json

{
  "model_type": "standard",
  "category_level3_id": "cat3_001"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "overall_score": 85.5,
    "company_value": "高价值",
    "is_core_position": true,
    "dimension_contributions": {
      "jd_content": 40.0,
      "evaluation_template": 30.0,
      "category_tags": 30.0
    },
    ...
  }
}
```

## 实现步骤

### 1. 后端实现
在 `src/api/` 目录下创建或更新路由文件：

```python
# src/api/routes/jd.py

from fastapi import APIRouter, HTTPException
from typing import List, Optional

router = APIRouter(prefix="/jd", tags=["JD"])

@router.get("/list")
async def list_jds(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None
):
    """获取 JD 列表"""
    # 实现逻辑
    pass

@router.get("/{jd_id}")
async def get_jd(jd_id: str):
    """获取单个 JD"""
    # 实现逻辑
    pass

@router.post("/{jd_id}/evaluate")
async def evaluate_jd(jd_id: str, request: EvaluateRequest):
    """评估 JD"""
    # 实现逻辑
    pass
```

### 2. 前端更新
实现 API 端点后，更新 UI 代码：

```python
# 替换临时方案
try:
    jds_response = api_request("GET", "/jd/list")
    saved_jds = jds_response.get("data", []) if jds_response.get("success") else []
except Exception as e:
    st.error(f"获取 JD 列表失败: {str(e)}")
    saved_jds = []
```

### 3. 数据迁移
如果需要保留 session_state 中的数据，可以：
1. 导出为 JSON 文件
2. 通过 API 批量导入到数据库
3. 验证数据完整性

## 测试验证

### 当前临时方案测试

1. **启动应用**:
   ```bash
   streamlit run src/ui/app.py
   ```

2. **测试流程**:
   - 进入"JD解析（第一步）"页面
   - 解析并保存一个 JD
   - 进入"JD评估（第二步）"页面
   - 应该能看到刚才保存的 JD

3. **预期结果**:
   - ✅ 不再出现 404 错误
   - ✅ 能看到已保存的 JD 列表
   - ✅ 可以选择 JD 进行评估

### API 实现后测试

1. **启动 API 服务**:
   ```bash
   python -m src.api.main
   ```

2. **测试 API 端点**:
   ```bash
   # 获取 JD 列表
   curl http://localhost:8000/api/v1/jd/list
   
   # 获取单个 JD
   curl http://localhost:8000/api/v1/jd/{jd_id}
   
   # 提交评估
   curl -X POST http://localhost:8000/api/v1/jd/{jd_id}/evaluate \
     -H "Content-Type: application/json" \
     -d '{"model_type": "standard"}'
   ```

3. **集成测试**:
   - 通过 UI 解析 JD
   - 刷新页面
   - 检查 JD 是否仍然存在
   - 进行评估

## 相关文件

- `src/ui/app.py` - UI 主文件（已修复）
- `src/api/routes/jd.py` - JD 路由（待实现）
- `src/models/schemas.py` - 数据模型
- `src/services/jd_service.py` - JD 服务（待实现）

## 更新日期
2025-01-XX

## 相关文档
- `UI_JD_ANALYSIS_UPDATE_SUMMARY.md` - UI 更新总结
- `KEYERROR_FIX_SUMMARY.md` - KeyError 修复总结
- `TEMPLATE_FILTER_FIX.md` - 模板过滤修复
