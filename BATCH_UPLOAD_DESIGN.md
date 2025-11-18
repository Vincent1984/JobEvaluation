# 批量上传岗位JD附件功能 - 设计文档更新

## 更新日期
2024-01-13

## 概述
为岗位JD分析器的Agentic AI架构添加批量上传JD附件文件的设计，通过MCP协议实现Agent间协作处理批量文件上传和解析。

## 架构设计

### 1. 新增Agent：BatchUploadAgent

**职责：**
- 处理批量文件上传请求
- 验证文件格式和大小
- 协调文件解析和JD分析流程
- 管理批量处理进度
- 汇总处理结果

**MCP通讯：**
- 接收来自API的批量上传请求
- 调用Parser Agent进行JD解析
- 调用Evaluator Agent进行质量评估
- 通过MCP发送进度通知
- 更新共享上下文存储处理状态

### 2. 文件解析服务（FileParserService）

**支持格式：**
- `.txt` - 纯文本（支持UTF-8、GBK、GB2312等编码）
- `.pdf` - PDF文档（使用PyPDF2）
- `.docx` - Word 2007+（使用python-docx）
- `.doc` - Word 97-2003（使用textract，可选）

**限制规则：**
- 单个文件最大：10MB
- 批量上传最多：20个文件
- 总大小限制：100MB

**验证机制：**
```python
# 文件级别验证
- 文件大小检查
- 文件格式检查
- 编码识别

# 批量级别验证
- 文件数量检查
- 总大小检查
- 格式分布检查
```

### 3. 批量处理工作流

```
用户上传文件
    ↓
API接收并验证
    ↓
发送到BatchUploadAgent (via MCP)
    ↓
BatchUploadAgent创建批量上下文
    ↓
循环处理每个文件：
    ├─ 解析文件内容
    ├─ 发送进度通知 (via MCP)
    ├─ 调用Parser Agent解析JD (via MCP)
    ├─ 调用Evaluator Agent评估质量 (via MCP)
    ├─ 更新共享上下文
    └─ 记录成功/失败
    ↓
汇总所有结果
    ↓
返回给API
    ↓
展示给用户
```

### 4. MCP消息流

**批量上传消息：**
```json
{
  "message_id": "msg_xxx",
  "sender": "api",
  "receiver": "batch_uploader",
  "message_type": "request",
  "action": "batch_upload",
  "payload": {
    "files": [
      {
        "filename": "jd1.pdf",
        "content": "<bytes>",
        "size": 12345
      }
    ]
  },
  "context_id": "ctx_xxx"
}
```

**进度通知消息：**
```json
{
  "message_id": "msg_yyy",
  "sender": "batch_uploader",
  "receiver": null,
  "message_type": "notification",
  "action": "upload_progress",
  "payload": {
    "current": 3,
    "total": 10,
    "filename": "jd3.pdf",
    "status": "processing"
  },
  "context_id": "ctx_xxx"
}
```

**批量结果响应：**
```json
{
  "message_id": "msg_zzz",
  "sender": "batch_uploader",
  "receiver": "api",
  "message_type": "response",
  "action": "batch_upload",
  "payload": {
    "success": true,
    "total": 10,
    "successful": 8,
    "failed": 2,
    "results": [
      {
        "filename": "jd1.pdf",
        "status": "success",
        "jd_id": "jd_001",
        "jd_title": "高级Python工程师",
        "quality_score": 85.0
      },
      {
        "filename": "jd2.pdf",
        "status": "failed",
        "error": "PDF解析失败"
      }
    ],
    "failed_files": [
      {
        "filename": "jd2.pdf",
        "error": "PDF解析失败"
      }
    ]
  },
  "context_id": "ctx_xxx"
}
```

### 5. 共享上下文结构

```python
MCPContext(
    context_id="ctx_batch_xxx",
    task_id="task_xxx",
    shared_data={
        "total_files": 10,
        "processed_files": 3,
        "successful_files": 2,
        "failed_files": [
            {"filename": "jd2.pdf", "error": "解析失败"}
        ],
        "results": [
            {
                "filename": "jd1.pdf",
                "status": "success",
                "jd_id": "jd_001",
                "jd_title": "高级Python工程师",
                "quality_score": 85.0
            }
        ]
    },
    metadata={
        "workflow": "batch_upload",
        "start_time": 1234567890,
        "user_id": "user_xxx"
    }
)
```

## API设计

### 新增端点

#### 1. 单个文件上传
```http
POST /api/v1/jd/upload
Content-Type: multipart/form-data

Parameters:
- file: UploadFile (required)
- auto_analyze: bool (default: true)

Response:
{
  "jd": {...},
  "evaluation": {...},
  "suggestions": [...]
}
```

#### 2. 批量文件上传
```http
POST /api/v1/jd/batch-upload
Content-Type: multipart/form-data

Parameters:
- files: List[UploadFile] (required, max 20)
- auto_analyze: bool (default: true)

Response:
{
  "success": true,
  "total": 10,
  "successful": 8,
  "failed": 2,
  "results": [...],
  "failed_files": [...]
}
```

#### 3. 批量处理状态查询
```http
GET /api/v1/batch/status/{batch_id}

Response:
{
  "batch_id": "ctx_xxx",
  "total": 10,
  "processed": 5,
  "successful": 4,
  "failed": 1,
  "status": "processing"  // or "completed"
}
```

#### 4. 批量处理结果查询
```http
GET /api/v1/batch/results/{batch_id}

Response:
{
  "batch_id": "ctx_xxx",
  "results": [...],
  "failed_files": [...]
}
```

## 数据模型

### 文件上传记录

```python
class FileUploadRecord(BaseModel):
    """文件上传记录"""
    id: str
    filename: str
    file_size: int
    file_format: str
    upload_time: datetime
    status: str  # pending, processing, success, failed
    jd_id: Optional[str]
    error_message: Optional[str]
    batch_id: Optional[str]
```

### 批量处理记录

```python
class BatchUploadRecord(BaseModel):
    """批量上传记录"""
    batch_id: str
    total_files: int
    successful_files: int
    failed_files: int
    start_time: datetime
    end_time: Optional[datetime]
    status: str  # processing, completed, failed
    user_id: Optional[str]
```

## 错误处理

### 文件级别错误

| 错误类型 | HTTP状态码 | 处理方式 |
|---------|-----------|---------|
| 文件格式不支持 | 400 | 跳过该文件，继续处理其他文件 |
| 文件大小超限 | 400 | 跳过该文件，继续处理其他文件 |
| 文件损坏 | 400 | 跳过该文件，继续处理其他文件 |
| 解析失败 | 500 | 记录错误，继续处理其他文件 |
| LLM调用失败 | 500 | 记录错误，继续处理其他文件 |

### 批量级别错误

| 错误类型 | HTTP状态码 | 处理方式 |
|---------|-----------|---------|
| 文件数量超限 | 400 | 拒绝整个批量请求 |
| 总大小超限 | 400 | 拒绝整个批量请求 |
| 系统资源不足 | 503 | 返回重试提示 |

### 错误响应格式

```json
{
  "error": {
    "code": "FILE_SIZE_EXCEEDED",
    "message": "文件大小超过10MB限制",
    "details": {
      "filename": "large_jd.pdf",
      "size": 15728640,
      "max_size": 10485760
    }
  }
}
```

## 性能优化

### 1. 并行处理
```python
# 使用asyncio并发处理多个文件
async def process_files_parallel(files: List[Dict]) -> List[Dict]:
    tasks = [process_single_file(file) for file in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 2. 流式上传
```python
# 支持大文件流式上传
@app.post("/api/v1/jd/upload-stream")
async def upload_stream(request: Request):
    async for chunk in request.stream():
        # 处理数据块
        pass
```

### 3. 进度缓存
```python
# 使用Redis缓存批量处理进度
await redis.setex(
    f"batch:progress:{batch_id}",
    3600,  # 1小时过期
    json.dumps(progress_data)
)
```

### 4. 文件预处理
```python
# 在上传时进行初步验证
def prevalidate_file(file: UploadFile) -> bool:
    # 检查文件头（magic number）
    # 快速验证文件格式
    pass
```

## 安全考虑

### 1. 文件验证
- 验证文件扩展名
- 验证文件MIME类型
- 检查文件头（magic number）
- 扫描恶意内容

### 2. 资源限制
- 限制单个文件大小
- 限制批量文件数量
- 限制总上传大小
- 限制并发上传数

### 3. 访问控制
- 用户身份验证
- 上传频率限制
- 文件访问权限控制

### 4. 数据隔离
```python
# 每个用户的文件存储在独立目录
user_upload_dir = f"./uploads/{user_id}/{batch_id}/"
```

## 测试策略

### 单元测试
- [ ] FileParserService.parse_txt()
- [ ] FileParserService.parse_pdf()
- [ ] FileParserService.parse_docx()
- [ ] FileParserService.validate_file()
- [ ] FileParserService.validate_batch()
- [ ] BatchUploadAgent.handle_batch_upload()

### 集成测试
- [ ] 单个文件上传端到端流程
- [ ] 批量文件上传端到端流程
- [ ] MCP消息传递测试
- [ ] Agent协作测试

### 性能测试
- [ ] 单个10MB文件上传性能
- [ ] 20个文件批量上传性能
- [ ] 并发批量上传测试
- [ ] 内存使用测试

### 边界测试
- [ ] 上传21个文件（应拒绝）
- [ ] 上传11MB文件（应拒绝）
- [ ] 上传不支持格式（应拒绝）
- [ ] 上传损坏文件（应跳过）
- [ ] 空文件上传（应拒绝）

## 依赖库

### 新增依赖
```txt
PyPDF2==3.0.1          # PDF解析
python-docx==1.1.0     # DOCX解析
textract==1.6.5        # DOC解析（可选）
python-magic==0.4.27   # 文件类型检测
```

### 安装命令
```bash
pip install PyPDF2 python-docx python-magic
# 可选：pip install textract
```

## 部署注意事项

### 1. 文件存储
```bash
# 创建上传目录
mkdir -p ./uploads
chmod 755 ./uploads

# 配置文件清理任务（cron）
0 2 * * * find ./uploads -type f -mtime +7 -delete
```

### 2. 系统资源
- 确保足够的磁盘空间（建议至少10GB）
- 配置合适的内存限制
- 监控CPU使用率

### 3. 日志配置
```python
# 记录批量上传日志
logger.info(f"Batch upload started: {batch_id}, files: {len(files)}")
logger.info(f"Batch upload completed: {batch_id}, success: {success_count}, failed: {failed_count}")
```

## 监控指标

### 关键指标
- 批量上传成功率
- 平均处理时间
- 文件解析成功率
- 各格式文件分布
- 错误类型分布

### 告警规则
- 批量上传失败率 > 20%
- 平均处理时间 > 30秒/文件
- 磁盘使用率 > 80%
- 内存使用率 > 90%

## 后续优化

### 短期（1-2周）
- [ ] 添加文件预览功能
- [ ] 支持拖拽上传
- [ ] 优化进度显示

### 中期（1-2月）
- [ ] 支持更多文件格式（RTF、HTML）
- [ ] 添加OCR识别（图片JD）
- [ ] 支持压缩包上传

### 长期（3-6月）
- [ ] 云存储集成（OSS、S3）
- [ ] 分布式文件处理
- [ ] 智能文件分类

## 总结

批量上传JD附件功能通过引入BatchUploadAgent和FileParserService，完美融入现有的Agentic AI架构。通过MCP协议实现Agent间的协作，确保了系统的可扩展性和可维护性。该功能将显著提升用户体验，减少手动操作，提高工作效率。
