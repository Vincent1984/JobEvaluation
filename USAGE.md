# 使用说明

## 📖 完整使用指南

### 1. 环境准备

#### 1.1 系统要求
- Python 3.11 或更高版本
- 8GB+ 内存
- 稳定的网络连接（用于API调用）

#### 1.2 获取API密钥

**选项A: OpenAI (推荐)**
1. 访问 https://platform.openai.com/
2. 注册账号并充值
3. 创建API密钥
4. 复制密钥备用

**选项B: DeepSeek (国内推荐)**
1. 访问 https://platform.deepseek.com/
2. 注册账号
3. 创建API密钥
4. 复制密钥备用

### 2. 安装配置

#### 2.1 克隆或下载项目

```bash
# 如果使用Git
git clone <repository-url>
cd jd-analyzer

# 或直接下载ZIP并解压
```

#### 2.2 安装依赖

**Windows:**
```bash
# 双击 start.bat 会自动安装
# 或手动执行:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
# 运行 start.sh 会自动安装
# 或手动执行:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2.3 配置环境变量

1. 复制环境变量模板:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

2. 编辑 `.env` 文件:

**使用OpenAI:**
```env
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

**使用DeepSeek:**
```env
OPENAI_API_KEY=sk-your-deepseek-key-here
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

### 3. 启动应用

#### 3.1 使用启动脚本（推荐）

**Windows:**
```bash
# 双击 start.bat
# 或在命令行运行:
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

然后选择选项 `1` 启动Streamlit UI

#### 3.2 手动启动

```bash
# 激活虚拟环境
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 启动Streamlit
streamlit run src/ui/app.py
```

#### 3.3 访问应用

浏览器自动打开，或手动访问:
- **Streamlit UI**: http://localhost:8501

### 4. 功能使用

#### 4.1 JD分析

**步骤1: 输入JD**
- 方式A: 直接在文本框中输入或粘贴JD文本
- 方式B: 点击"加载示例JD"按钮使用预设示例

**步骤2: 选择评估模型**
在侧边栏选择评估模型:
- **标准评估**: 适用于所有类型的JD
- **美世国际职位评估法**: 适用于管理和专业岗位
- **因素比较法**: 适用于技术和操作岗位

**步骤3: 开始分析**
点击"开始分析"按钮，等待10-30秒

**步骤4: 查看结果**
- **解析结果**: 查看提取的结构化信息
- **质量评估**: 查看多维度质量分数
- **优化建议**: 查看AI生成的改进建议

#### 4.2 历史记录

点击侧边栏的"历史记录"查看所有分析过的JD:
- 按时间倒序排列
- 点击展开查看详细信息
- 包含职位信息和质量分数

#### 4.3 关于页面

查看系统信息、版本和使用说明

### 5. 高级功能

#### 5.1 自定义评估标准

当前MVP版本使用默认评估标准，未来版本将支持:
- 自定义评估维度
- 调整权重配置
- 创建评估模板

#### 5.2 批量处理

未来版本将支持:
- 批量上传多个JD
- 批量分析和导出
- JD对比功能

#### 5.3 候选人匹配

未来版本将支持:
- 生成评估问卷
- 候选人在线填写
- 自动计算匹配度
- 生成匹配报告

### 6. 最佳实践

#### 6.1 JD编写建议

为获得最佳分析效果，JD应包含:
- ✅ 明确的职位标题
- ✅ 详细的职责描述（3-5条）
- ✅ 清晰的技能要求（必备+优选）
- ✅ 具体的任职资格
- ✅ 工作地点和部门信息

#### 6.2 评估模型选择

- **标准评估**: 日常使用，快速评估
- **美世法**: 高级管理岗位，需要评估影响力
- **因素法**: 技术岗位，需要详细技能评估

#### 6.3 成本控制

- 使用 `gpt-3.5-turbo` 降低成本（约0.01 USD/次）
- 使用 `gpt-4` 提高质量（约0.05 USD/次）
- 使用 DeepSeek 获得性价比（约0.001 USD/次）

### 7. 故障排除

#### 7.1 常见问题

**Q: 启动失败，提示模块未找到**
A: 确保已激活虚拟环境并安装依赖
```bash
pip install -r requirements.txt
```

**Q: API调用失败**
A: 检查以下几点:
1. `.env` 文件中的API密钥是否正确
2. 网络连接是否正常
3. API账户余额是否充足
4. API服务是否可访问

**Q: 分析速度很慢**
A: 可能原因:
1. 网络延迟 - 尝试使用国内API服务
2. 模型选择 - 使用更快的模型（gpt-3.5-turbo）
3. JD文本过长 - 建议控制在2000字以内

**Q: 分析结果不准确**
A: 改进建议:
1. 提供更详细的JD文本
2. 使用更强大的模型（gpt-4）
3. 尝试不同的评估模型

#### 7.2 日志查看

如遇到问题，查看控制台输出的错误信息:
- Streamlit日志: 启动窗口
- Python错误: 红色错误提示

#### 7.3 重置应用

如需重置应用:
```bash
# 删除数据目录
rm -rf data/

# 重新启动应用
python run.py
```

### 8. 性能优化

#### 8.1 提高分析速度

1. **使用更快的模型**:
```env
LLM_MODEL=gpt-3.5-turbo
```

2. **使用国内API**:
```env
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

3. **优化网络连接**:
- 使用稳定的网络
- 考虑使用代理

#### 8.2 降低成本

1. **选择性价比高的模型**:
- DeepSeek: ~$0.001/次
- GPT-3.5: ~$0.01/次
- GPT-4: ~$0.05/次

2. **控制JD长度**:
- 建议1000-2000字
- 避免过长的JD文本

### 9. 数据管理

#### 9.1 数据存储

当前MVP版本使用内存存储:
- 数据保存在应用运行期间
- 重启应用后数据清空
- 未来版本将支持数据库持久化

#### 9.2 数据导出

未来版本将支持:
- 导出分析报告（PDF/Excel）
- 批量导出历史记录
- 数据备份功能

### 10. 更新日志

#### v0.1.0 (MVP) - 2024-01
- ✅ JD解析功能
- ✅ 质量评估（标准/美世法/因素法）
- ✅ 优化建议生成
- ✅ Streamlit UI界面
- ✅ 历史记录查看

#### 即将推出
- 🔜 候选人匹配功能
- 🔜 问卷生成和管理
- 🔜 批量处理
- 🔜 报告导出
- 🔜 数据库持久化
- 🔜 职位分类管理

### 11. 技术支持

如需帮助:
1. 查看 `README.md` - 项目概述
2. 查看 `QUICKSTART.md` - 快速开始
3. 查看 `.kiro/specs/jd-analyzer/` - 详细设计文档
4. 联系开发团队

### 12. 贡献指南

欢迎贡献代码和建议:
1. Fork项目
2. 创建功能分支
3. 提交Pull Request
4. 等待审核

---

**祝使用愉快！** 🎉
