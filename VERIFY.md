# 🔍 启动验证指南

## 验证清单

在首次使用前，请按照以下步骤验证系统是否正确配置。

### ✅ 步骤1: 检查Python版本

```bash
python --version
```

**期望输出**: Python 3.11.0 或更高版本

**如果失败**:
- Windows: 从 https://python.org 下载安装
- Linux: `sudo apt install python3.11`
- Mac: `brew install python@3.11`

### ✅ 步骤2: 检查依赖安装

```bash
pip list | grep -E "streamlit|fastapi|openai|pydantic"
```

**期望输出**: 应该看到这些包

**如果失败**:
```bash
pip install -r requirements.txt
```

### ✅ 步骤3: 检查环境变量

```bash
# Windows
type .env

# Linux/Mac
cat .env
```

**期望内容**:
```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://...
LLM_MODEL=gpt-4
```

**如果失败**:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```
然后编辑 `.env` 填入API密钥

### ✅ 步骤4: 测试API连接

```bash
python test_mvp.py
```

**期望输出**:
- 显示"开始分析..."
- 显示解析结果
- 显示质量评估
- 显示"测试通过！"

**如果失败**:
- 检查API密钥是否正确
- 检查网络连接
- 检查API余额

### ✅ 步骤5: 启动应用

```bash
streamlit run src/ui/app.py
```

**期望结果**:
- 浏览器自动打开
- 显示"岗位JD分析器"标题
- 界面正常显示

**如果失败**:
- 检查端口8501是否被占用
- 尝试指定其他端口: `streamlit run src/ui/app.py --server.port=8502`

### ✅ 步骤6: 测试核心功能

1. **加载示例JD**
   - 点击"加载示例JD"按钮
   - 应该看到示例文本填充

2. **开始分析**
   - 点击"开始分析"按钮
   - 等待15-30秒
   - 应该看到"分析完成！"

3. **查看结果**
   - 切换到"解析结果"标签
   - 应该看到职位信息
   - 切换到"质量评估"标签
   - 应该看到分数
   - 切换到"优化建议"标签
   - 应该看到建议列表

## 🐛 常见问题排查

### 问题1: ModuleNotFoundError

**症状**: 提示找不到某个模块

**解决**:
```bash
pip install -r requirements.txt
```

### 问题2: API Key错误

**症状**: 提示"Invalid API Key"

**解决**:
1. 检查 `.env` 文件中的API密钥
2. 确保没有多余的空格或引号
3. 确认API密钥有效且有余额

### 问题3: 端口被占用

**症状**: 提示"Address already in use"

**解决**:
```bash
# 使用其他端口
streamlit run src/ui/app.py --server.port=8502
```

### 问题4: 网络连接失败

**症状**: 提示"Connection timeout"

**解决**:
1. 检查网络连接
2. 如果在国内，考虑使用DeepSeek:
```env
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_API_KEY=sk-your-deepseek-key
LLM_MODEL=deepseek-chat
```

### 问题5: 分析结果不准确

**症状**: 解析结果不符合预期

**解决**:
1. 使用更强大的模型（gpt-4）
2. 提供更详细的JD文本
3. 检查JD格式是否规范

## 📊 性能基准

### 正常指标
- 启动时间: < 10秒
- 分析时间: 15-30秒
- 内存使用: < 500MB
- CPU使用: < 50%

### 如果超出正常范围
- 检查系统资源
- 关闭其他应用
- 重启应用

## ✅ 验证通过标准

所有以下项目都应该正常:

- [x] Python版本正确
- [x] 依赖包已安装
- [x] 环境变量已配置
- [x] API连接正常
- [x] 应用可以启动
- [x] 界面正常显示
- [x] 示例JD可以加载
- [x] 分析功能正常
- [x] 结果正确显示

## 🎉 验证成功！

如果所有检查都通过，恭喜你！系统已经准备就绪。

### 下一步
1. 阅读 [USAGE.md](USAGE.md) 了解详细使用方法
2. 查看 [DEMO.md](DEMO.md) 准备演示
3. 开始分析你的第一个JD！

## 📞 需要帮助？

如果验证失败:
1. 查看 [USAGE.md](USAGE.md) 的故障排除部分
2. 查看 [QUICKSTART.md](QUICKSTART.md) 重新配置
3. 检查 [README.md](README.md) 的系统要求

---

**验证脚本版本**: v1.0
**最后更新**: 2024-01
