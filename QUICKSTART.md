# 快速开始指南

## 🚀 5分钟快速启动

### 步骤1: 安装依赖

**Windows用户:**
```bash
# 双击运行
start.bat
```

**Linux/Mac用户:**
```bash
# 添加执行权限
chmod +x start.sh

# 运行
./start.sh
```

**或手动安装:**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤2: 配置API密钥

1. 复制 `.env.example` 为 `.env`
2. 编辑 `.env` 文件，填入你的API密钥：

```env
# OpenAI配置
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# 或使用DeepSeek
# OPENAI_BASE_URL=https://api.deepseek.com/v1
# OPENAI_API_KEY=sk-your-deepseek-key
# LLM_MODEL=deepseek-chat
```

### 步骤3: 启动应用

**方式1: 使用启动脚本（推荐）**
```bash
python run.py
```
然后选择 `1` 启动Streamlit UI

**方式2: 直接启动Streamlit**
```bash
streamlit run src/ui/app.py
```

### 步骤4: 访问应用

打开浏览器访问: **http://localhost:8501**

## 📝 使用示例

### 1. 分析JD

1. 在"JD分析"页面，点击"加载示例JD"按钮
2. 或者粘贴你自己的JD文本
3. 点击"开始分析"按钮
4. 等待AI分析完成（约10-30秒）
5. 查看结果：
   - **解析结果**: 结构化的职位信息
   - **质量评估**: 多维度质量分数
   - **优化建议**: AI生成的改进建议

### 2. 查看历史

点击侧边栏的"历史记录"，查看所有分析过的JD

## 🎯 示例JD

```
职位：高级Python后端工程师

部门：技术研发部
地点：北京

岗位职责：
1. 负责公司核心业务系统的后端开发和维护
2. 参与系统架构设计，优化系统性能和稳定性
3. 编写高质量、可维护的代码，进行代码审查
4. 与产品、前端团队协作，推动项目落地

任职要求：
必备技能：
- 3年以上Python开发经验
- 熟练掌握FastAPI、Django等Web框架
- 熟悉MySQL、Redis等数据库
- 了解微服务架构和RESTful API设计

优选技能：
- 有大型互联网项目经验
- 熟悉Docker、Kubernetes容器化技术
- 了解消息队列（RabbitMQ、Kafka）

学历要求：
- 本科及以上学历，计算机相关专业优先
```

## ⚙️ 配置选项

### 评估模型

在侧边栏可以选择不同的评估模型：
- **标准评估**: 通用质量评估
- **美世国际职位评估法**: 基于影响力、沟通、创新、知识技能四个维度
- **因素比较法**: 基于技能、责任、努力、工作条件等因素

### LLM模型

在 `.env` 文件中可以配置不同的LLM模型：
- `gpt-4`: OpenAI GPT-4（推荐，质量最高）
- `gpt-3.5-turbo`: OpenAI GPT-3.5（更快，成本更低）
- `deepseek-chat`: DeepSeek（国内可用，性价比高）

## 🔧 故障排除

### 问题1: 启动失败

**解决方案:**
1. 确保Python版本 >= 3.11
2. 检查是否正确激活虚拟环境
3. 重新安装依赖: `pip install -r requirements.txt`

### 问题2: API调用失败

**解决方案:**
1. 检查 `.env` 文件中的API密钥是否正确
2. 检查网络连接
3. 确认API余额充足

### 问题3: 分析速度慢

**解决方案:**
1. 使用更快的模型（如 gpt-3.5-turbo）
2. 检查网络连接
3. 考虑使用国内API服务（如DeepSeek）

## 📚 更多功能

当前MVP版本支持：
- ✅ JD解析
- ✅ 质量评估
- ✅ 优化建议
- ✅ 历史记录

即将推出：
- 🔜 候选人匹配
- 🔜 问卷生成
- 🔜 批量处理
- 🔜 报告导出

## 💡 提示

1. **首次使用**: 建议先用示例JD测试
2. **API成本**: 每次分析约消耗 0.01-0.05 USD
3. **分析时间**: 通常需要 10-30 秒
4. **最佳实践**: JD文本越详细，分析结果越准确

## 🆘 获取帮助

如有问题，请查看：
- README.md - 完整文档
- .kiro/specs/jd-analyzer/ - 详细设计文档
- 或联系开发团队
