# 🚀 立即开始

## 最快3步启动

### 第1步: 安装 (1分钟)

**Windows用户 - 双击运行:**
```
start.bat
```

**Linux/Mac用户:**
```bash
chmod +x start.sh
./start.sh
```

### 第2步: 配置 (1分钟)

1. 打开 `.env` 文件（自动创建）
2. 填入你的API密钥:

```env
OPENAI_API_KEY=sk-your-key-here
```

**获取API密钥:**
- OpenAI: https://platform.openai.com/api-keys
- DeepSeek: https://platform.deepseek.com/api_keys

### 第3步: 启动 (1分钟)

选择选项 `1` - 启动Streamlit UI

浏览器自动打开: http://localhost:8501

## 🎯 立即体验

1. 点击 **"加载示例JD"** 按钮
2. 点击 **"开始分析"** 按钮  
3. 等待15秒，查看结果！

## 💡 提示

- **首次使用**: 建议先用示例JD测试
- **API成本**: 每次分析约 $0.01-0.05
- **分析时间**: 通常10-30秒
- **最佳效果**: JD文本越详细越好

## 📚 需要帮助？

- 快速指南: [QUICKSTART.md](QUICKSTART.md)
- 详细说明: [USAGE.md](USAGE.md)
- 演示指南: [DEMO.md](DEMO.md)
- 项目总结: [MVP_SUMMARY.md](MVP_SUMMARY.md)

## ⚡ 常见问题

**Q: 没有API密钥怎么办？**
A: 访问 https://platform.openai.com 注册并充值

**Q: 启动失败？**
A: 确保Python版本 >= 3.11，重新运行 `pip install -r requirements.txt`

**Q: 分析失败？**
A: 检查API密钥是否正确，网络是否正常

**Q: 想用国内API？**
A: 使用DeepSeek，修改 `.env`:
```env
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_API_KEY=sk-your-deepseek-key
LLM_MODEL=deepseek-chat
```

## 🎉 开始使用吧！

现在你已经准备好了，开始分析你的第一个JD吧！

---

**遇到问题？** 查看 [USAGE.md](USAGE.md) 获取详细帮助
