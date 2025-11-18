# Bug 修复：文件上传 403 错误

## 问题描述

在 UI 页面点击"上传岗位JD文件"，上传文件后出现：
```
AxiosError: Request failed with status code 403
```

## 问题分析

### 可能的原因

1. **Streamlit 配置问题**
   - Streamlit 的文件上传大小限制
   - CORS 配置问题

2. **文件大小超限**
   - Streamlit 默认文件上传限制是 200MB
   - 但可能被配置文件修改

3. **Streamlit 内部请求**
   - Streamlit 在处理文件上传时会发送内部请求
   - 可能被某些安全设置阻止

## 解决方案

### 方案 1：配置 Streamlit（推荐）

创建或修改 `.streamlit/config.toml` 文件：

```toml
[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### 方案 2：检查文件大小

确保上传的文件不超过 10MB（代码中的限制）。

### 方案 3：使用文本输入代替

如果文件上传持续有问题，可以：
1. 手动打开文件
2. 复制文件内容
3. 使用"文本输入"方式粘贴

## 实施步骤

### 步骤 1：创建 Streamlit 配置

```bash
# 创建配置目录
mkdir .streamlit

# 创建配置文件
# 使用下面的内容
```

### 步骤 2：配置文件内容

创建 `.streamlit/config.toml`：

```toml
[server]
# 文件上传大小限制（MB）
maxUploadSize = 200

# 禁用 CORS（开发环境）
enableCORS = false

# 禁用 XSRF 保护（开发环境）
enableXsrfProtection = false

# 端口
port = 8501

[browser]
# 禁用使用统计收集
gatherUsageStats = false

[client]
# 显示错误详情
showErrorDetails = true
```

### 步骤 3：重启服务

```bash
# 停止当前的 Streamlit 服务
# Ctrl+C

# 重新启动
streamlit run src/ui/app.py --server.port 8501
```

## 验证

### 测试步骤

1. 重启 Streamlit 服务
2. 访问 http://localhost:8501
3. 选择"文件上传"
4. 上传一个小的测试文件（< 1MB）
5. 点击"开始分析"

### 预期结果

- ✅ 文件成功上传
- ✅ 显示"文件解析成功"
- ✅ 显示分析结果

## 替代方案

如果问题仍然存在，使用以下替代方案：

### 方案 A：使用文本输入

1. 打开 JD 文件
2. 复制全部内容
3. 在 UI 中选择"文本输入"
4. 粘贴内容
5. 点击"开始分析"

### 方案 B：使用批量上传

批量上传功能使用相同的文件解析逻辑，可能不会遇到同样的问题。

### 方案 C：直接使用 Python 脚本

```python
import asyncio
from src.mcp.simple_client import get_simple_mcp_client

async def analyze_file(file_path):
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        jd_text = f.read()
    
    # 分析
    client = get_simple_mcp_client()
    result = await client.analyze_jd(jd_text, "standard")
    
    print(f"职位: {result['jd'].job_title}")
    print(f"质量分数: {result['evaluation'].quality_score.overall_score}")

# 运行
asyncio.run(analyze_file("your_jd_file.txt"))
```

## 调试信息

### 查看 Streamlit 日志

在终端中查看 Streamlit 的输出，寻找更详细的错误信息：

```
2024-xx-xx xx:xx:xx.xxx 
  AxiosError: Request failed with status code 403
  ...
```

### 检查浏览器控制台

1. 打开浏览器开发者工具（F12）
2. 切换到 Console 标签
3. 查看是否有更详细的错误信息
4. 切换到 Network 标签
5. 重新上传文件
6. 查看失败的请求详情

## 常见错误模式

### 错误 1：文件太大

```
File size exceeds maximum allowed size
```

**解决**：减小文件大小或增加 `maxUploadSize` 配置

### 错误 2：CORS 错误

```
Access to XMLHttpRequest has been blocked by CORS policy
```

**解决**：设置 `enableCORS = false`

### 错误 3：XSRF 保护

```
XSRF token mismatch
```

**解决**：设置 `enableXsrfProtection = false`

## 代码检查

当前文件上传代码（`src/ui/app.py`）：

```python
# 文件上传
uploaded_file = st.file_uploader(
    "选择文件",
    type=["txt", "pdf", "docx"],
    help="支持TXT、PDF、DOCX格式，单个文件最大10MB"
)

# 处理文件
if uploaded_file:
    file_content = uploaded_file.read()
    jd_text = file_parser.parse_file(file_content, uploaded_file.name)
```

这段代码：
- ✅ 不调用任何 API
- ✅ 完全在本地处理
- ✅ 使用 Streamlit 内置的文件上传组件

## 推荐配置

### 开发环境配置

`.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false
port = 8501

[browser]
gatherUsageStats = false

[client]
showErrorDetails = true

[logger]
level = "debug"
```

### 生产环境配置

`.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 50
enableCORS = true
enableXsrfProtection = true
port = 8501

[browser]
gatherUsageStats = false

[client]
showErrorDetails = false
```

## 总结

403 错误最可能是 Streamlit 的配置问题。创建 `.streamlit/config.toml` 文件并配置相关选项应该能解决问题。

如果问题仍然存在，请使用文本输入作为替代方案。

---

**文档版本**: 1.0  
**最后更新**: 2024年
