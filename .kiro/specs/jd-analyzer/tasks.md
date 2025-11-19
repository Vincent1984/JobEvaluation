# 实施计划

- [x] 1. 项目基础设施搭建
  - 创建项目目录结构
  - 配置Python虚拟环境和依赖管理（requirements.txt）
  - 配置环境变量文件（.env.example）
  - 设置Git仓库和.gitignore
  - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ] 2. 数据模型和数据库设计
  - [x] 2.1 定义Pydantic数据模型（JobDescription, JobCategory, EvaluationResult, Questionnaire等）
    - 实现所有核心数据模型类
    - 实现JobCategory模型（支持3层级，包含sample_jd_ids字段）
    - 在JobDescription中添加分类字段（category_level1_id, category_level2_id, category_level3_id）
    - 添加数据验证规则（第三层级样本JD数量限制为1-2个）
    - _需求: 1.1, 1.2, 1.3, 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15, 2.1, 2.2, 4.1, 5.1, 5.2_
  
  - [x] 2.1.5 更新数据模型以支持企业和分类标签





    - 在src/models/schemas.py中实现Company模型（id, name, created_at, updated_at）
    - 在src/models/schemas.py中实现CategoryTag模型（id, category_id, name, tag_type, description, created_at）
    - 更新JobCategory模型，添加company_id字段和tags字段（List[CategoryTag]）
    - 更新JobDescription模型，添加category_tags字段（List[CategoryTag]）
    - 更新EvaluationResult模型，添加综合评估字段（overall_score, company_value, is_core_position, dimension_contributions, manual_modifications, is_manually_modified）
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14, 2.29, 2.30, 2.31, 2.32, 2.33_
  
  - [x] 2.2 创建SQLite数据库schema和ORM映射
    - 设计数据库表结构（包括job_categories表，包含sample_jd_ids字段）
    - 实现SQLAlchemy ORM模型
    - 创建数据库初始化脚本
    - 添加分类表的外键关系
    - _需求: 1.1, 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15, 2.1, 4.1, 5.1_
  
-

  - [x] 2.2.5 更新数据库schema以支持企业和分类标签



    - 在src/models/database.py中创建CompanyDB表（id, name, created_at, updated_at）
    - 在src/models/database.py中创建CategoryTagDB表（id, category_id, name, tag_type, description, created_at）
    - 更新JobCategoryDB表，添加company_id外键字段
    - 更新EvaluationResultDB表，添加综合评估字段（overall_score, company_value, is_core_position, dimension_contributions, is_manually_modified, manual_modifications）
    - 创建必要的索引（idx_categories_company, idx_tags_category等）
    - 编写数据库迁移脚本（scripts/migrate_db.py）
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14, 2.29, 2.30, 2.31, 2.32, 2.33_

- [ ] 3. MCP通讯层实现

  - [x] 3.1 实现MCP消息协议（MCPMessage, MCPContext类）






    - 定义消息格式和上下文结构
    - 实现消息序列化和反序列化
    - _需求: 1.1, 2.1, 4.1, 5.1_
  
  - [x] 3.2 实现MCP Server（基于Redis）



    - 配置Redis连接
    - 实现消息发布订阅机制
    - 实现上下文存储和检索
    - _需求: 1.1, 2.1, 4.1, 5.1_
  

  - [x] 3.3 实现MCPAgent基类



    - 实现Agent注册和消息订阅
    - 实现消息处理器注册机制
    - 实现请求-响应模式
    - _需求: 1.1, 2.1, 4.1, 5.1_

- [ ] 4. DeepSeek-R1 LLM集成

  - [x] 4.1 实现DeepSeek-R1客户端封装








    - 配置API连接
    - 实现异步调用接口
    - 添加错误处理和重试机制
    - _需求: 1.1, 1.5, 2.1, 2.6, 2.7, 3.1, 3.2, 3.3, 4.1, 5.1, 5.2, 5.4, 5.6, 5.7_
  



  - [x] 4.2 实现LLM调用缓存机制






    - 实现基于prompt的缓存key生成
    - 实现缓存存储和检索
    - _需求: 1.1, 2.1_

- [x] 5. 核心Agent实现





  - [x] 5.0 实现批量上传Agent（BatchUploadAgent）


    - 实现文件验证逻辑（格式、大小、数量）
    - 实现批量文件处理循环
    - 实现进度通知机制（via MCP）
    - 实现与Parser Agent和Evaluator Agent的协调
    - 实现批量处理上下文管理
    - 实现结果汇总和错误处理
    - _需求: 1.16, 1.17, 1.18, 1.19, 1.20, 1.21, 1.22, 6.1, 6.2, 6.3, 6.8_
  
  - [x] 5.1 实现JD解析Agent（ParserAgent）


    - 实现JD文本解析逻辑
    - 实现自定义字段提取
    - 实现职位自动分类功能（基于3层级分类体系）
    - 实现获取样本JD并用于分类参考的逻辑
    - 实现分类Prompt构建（包含样本JD参考）
    - 实现与DataManagerAgent的通讯
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15_
  
  - [x] 5.2 实现质量评估Agent（EvaluatorAgent）
    - 实现标准评估模型
    - 实现美世国际职位评估法（Mercer IPE）
    - 实现因素比较法
    - 实现质量问题识别
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9_
  
  - [x] 5.2.5 增强EvaluatorAgent以支持综合评估和手动修改





    - 在src/agents/evaluator_agent.py中创建ComprehensiveEvaluator类
    - 实现_analyze_category_tags方法（分析分类标签对评估的影响）
    - 实现_integrate_dimensions方法（整合JD内容、评估模板、分类标签三个维度）
    - 实现_determine_company_value方法（判断企业价值：高价值/中价值/低价值）
    - 实现_determine_core_position方法（判断是否核心岗位）
    - 在EvaluatorAgent中集成ComprehensiveEvaluator，更新handle_evaluate_quality方法
    - 实现handle_update_evaluation方法（支持手动修改评估结果）
    - 实现修改历史记录功能（记录修改时间、修改人、修改内容、原始值）
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14, 2.29, 2.30, 2.31, 2.32, 2.33_
  
  - [x] 5.3 实现优化建议Agent（OptimizerAgent）


    - 实现基于评估结果的建议生成
    - 实现JD改写示例生成
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 5.4 实现问卷生成Agent（QuestionnaireAgent）


    - 实现基于JD的问题生成
    - 实现多种评估模型的问卷适配
    - 实现问题类型生成（单选、多选、量表、开放）
    - _需求: 5.1, 5.2, 5.3, 5.4, 5.5, 5.9_
  
  - [x] 5.5 实现匹配评估Agent（MatcherAgent）


    - 实现问卷回答解析
    - 实现多维度匹配度计算
    - 实现优势和差距分析
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 5.6, 5.7, 5.8, 5.10_
  
  - [x] 5.6 实现数据管理Agent（DataManagerAgent）
    - 实现数据库CRUD操作
    - 实现数据访问接口
    - 实现职位分类的CRUD操作（包含样本JD管理）
    - 实现获取分类树的功能
    - 实现更新JD分类的功能
    - 实现样本JD数量验证（第三层级最多2个）
    - _需求: 1.1, 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15, 2.1, 4.1, 5.1_
  
  - [x] 5.6.5 增强DataManagerAgent以支持企业和标签管理





    - 在src/agents/data_manager_agent.py中实现handle_save_company方法
    - 实现handle_get_company方法
    - 实现handle_get_all_companies方法
    - 实现handle_delete_company方法（级联删除企业下的所有分类和标签）
    - 实现handle_save_category_tag方法（验证仅第三层级分类可添加标签）
    - 实现handle_get_category_tags方法
    - 实现handle_delete_category_tag方法
    - 更新handle_get_jd方法，自动加载关联的分类标签
    - 更新handle_save_evaluation和handle_get_evaluation方法（支持手动修改记录）
    - 实现handle_get_company_categories方法（获取企业的分类树）
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14, 2.29, 2.30, 2.31, 2.32, 2.33_
  
  - [x] 5.7 实现协调Agent（CoordinatorAgent）


    - 实现任务分解和分配逻辑
    - 实现工作流编排
    - 实现Agent间协作协调
    - _需求: 1.1, 2.1, 3.1, 4.1, 5.1_
  
  - [x] 5.8 实现报告生成Agent（ReportAgent）


    - 实现报告数据汇总
    - 实现PDF报告生成
    - 实现可视化图表生成
    - _需求: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 6. 工作流实现




  - [x] 6.1 实现JD完整分析工作流


    - 实现解析→评估→优化的完整流程
    - 实现工作流上下文管理
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 6.2 实现问卷生成与匹配评估工作流


    - 实现问卷生成→回答收集→匹配计算的流程
    - 实现批量候选人评估
    - _需求: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 4.1, 4.2, 4.3, 4.4, 4.5_
-

- [x] 7. FastAPI后端实现



  - [x] 7.1 实现JD分析相关API端点


    - POST /api/v1/jd/analyze - 完整JD分析
    - POST /api/v1/jd/parse - 仅解析JD
    - GET /api/v1/jd/{jd_id} - 获取JD详情
    - GET /api/v1/jd/{jd_id}/evaluation - 获取评估结果
    - PUT /api/v1/jd/{jd_id}/category - 手动更新JD分类
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.12, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 7.1.5 实现职位分类管理API端点


    - POST /api/v1/categories - 创建职位分类（支持添加样本JD）
    - GET /api/v1/categories - 列出职位分类
    - GET /api/v1/categories/tree - 获取分类树
    - PUT /api/v1/categories/{id} - 更新分类
    - PUT /api/v1/categories/{id}/samples - 更新样本JD
    - DELETE /api/v1/categories/{id} - 删除分类
    - _需求: 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15_
  
  - [x] 7.1.6 实现企业管理API端点





    - 在src/api/routers/中创建companies.py路由文件
    - 实现POST /api/v1/companies端点（创建企业）
    - 实现GET /api/v1/companies端点（列出所有企业）
    - 实现GET /api/v1/companies/{company_id}端点（获取企业详情）
    - 实现PUT /api/v1/companies/{company_id}端点（更新企业名称）
    - 实现DELETE /api/v1/companies/{company_id}端点（删除企业，带确认提示）
    - 实现GET /api/v1/companies/{company_id}/categories端点（列出企业的分类）
    - 实现GET /api/v1/companies/{company_id}/categories/tree端点（获取企业的分类树）
    - 在src/api/main.py中注册companies路由
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_
  
  - [x] 7.1.7 实现分类标签管理API端点




  - [ ] 7.1.7 实现分类标签管理API端点
    - 在src/api/routers/categories.py中实现POST /api/v1/categories/{category_id}/tags端点（为第三层级分类添加标签）
    - 实现GET /api/v1/categories/{category_id}/tags端点（获取分类的所有标签）
    - 在src/api/routers/中创建tags.py路由文件
    - 实现PUT /api/v1/tags/{tag_id}端点（更新标签）
    - 实现DELETE /api/v1/tags/{tag_id}端点（删除标签）
    - 在src/api/main.py中注册tags路由
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14_
  
-

  - [x] 7.1.8 实现评估结果手动修改API端点


    - 在src/api/routers/jd.py中实现PUT /api/v1/jd/{jd_id}/evaluation端点
    - 支持修改overall_score、company_value、is_core_position字段
    - 实现修改原因记录（reason参数）
    - 实现修改历史查询（返回manual_modifications数组）
    - 标识哪些结果是系统生成的，哪些是手动修改的（is_manually_modified字段）
    - _需求: 2.29, 2.30, 2.31, 2.32, 2.33_
  
  - [x] 7.2 实现问卷相关API端点


    - POST /api/v1/questionnaire/generate - 生成问卷
    - GET /api/v1/questionnaire/{id} - 获取问卷
    - POST /api/v1/questionnaire/{id}/submit - 提交问卷
    - _需求: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10_
  
  - [x] 7.3 实现匹配评估相关API端点


    - GET /api/v1/match/{id} - 获取匹配结果
    - GET /api/v1/match/{id}/report - 下载报告
    - GET /api/v1/jd/{jd_id}/matches - 列出所有匹配
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 7.4 实现模板管理API端点


    - POST /api/v1/templates - 创建模板
    - GET /api/v1/templates - 列出模板
    - PUT /api/v1/templates/{id} - 更新模板
    - DELETE /api/v1/templates/{id} - 删除模板
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 7.5 实现文件上传和批量处理API端点


    - POST /api/v1/jd/upload - 单个文件上传并分析
    - POST /api/v1/jd/batch-upload - 批量文件上传（最多20个）
    - GET /api/v1/batch/status/{batch_id} - 查询批量处理状态
    - GET /api/v1/batch/results/{batch_id} - 获取批量处理结果
    - POST /api/v1/batch/analyze - 批量分析JD文本
    - POST /api/v1/batch/match - 批量匹配候选人
    - _需求: 1.16, 1.17, 1.18, 1.19, 1.20, 1.21, 1.22, 6.1, 6.2, 6.3, 6.4, 6.5, 6.8_


- [x] 8. Streamlit前端实现







  - [x] 8.0 实现批量上传页面

    - 文件上传组件（支持多选，最多20个文件）
    - 文件列表预览（显示文件名、大小、格式）
    - 上传进度条和实时状态更新
    - 批量处理结果汇总展示
    - 成功/失败文件列表展示
    - 每个JD的快速预览（职位标题、质量分数）
    - 错误信息展示和重试功能
    - _需求: 1.16, 1.17, 1.18, 1.19, 1.20, 1.21, 1.22, 6.1, 6.2, 6.3_
  
  - [x] 8.1 实现JD分析页面

    - JD文本输入区域
    - 单个文件上传功能
    - 评估模型选择
    - 分析结果展示（解析结果、质量评分、优化建议）
    - 职位分类展示（3层级）
    - 手动调整分类功能
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.9, 1.10, 1.11, 1.12, 1.16, 1.17, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 8.1.5 实现职位分类管理页面

    - 分类树展示（3层级）
    - 创建分类表单（选择层级和父级）
    - 第三层级分类的样本JD选择功能（1-2个）
    - 样本JD展示和管理
    - 编辑和删除分类功能
    - _需求: 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15_
  -

  - [x] 8.1.6 实现企业管理页面




    - 在src/ui/app.py中添加"企业管理"页面选项
    - 实现企业列表展示（使用st.dataframe或卡片形式）
    - 实现创建企业表单（使用st.form，仅需企业名称输入）
    - 实现企业详情页面（显示企业信息和职位分类体系）
    - 实现编辑企业名称功能（使用st.text_input）
    - 实现删除企业功能（使用st.button，带st.warning确认提示）
    - 实现企业统计信息展示（使用st.metric显示分类数量、JD数量等）
    - 调用API端点：GET /api/v1/companies, POST /api/v1/companies, PUT /api/v1/companies/{id}, DELETE /api/v1/companies/{id}
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_
  
-

  - [x] 8.1.7 实现分类标签管理功能



    - 在src/ui/app.py的职位分类管理页面中，为第三层级分类添加标签管理区域
    - 实现添加标签表单（使用st.form，包含标签名称、类型、描述输入）
    - 实现标签类型下拉选择（使用st.selectbox，选项：战略重要性、业务价值、技能稀缺性、市场竞争度、发展潜力、风险等级）
    - 实现标签列表展示（使用st.expander或st.dataframe显示标签名称、类型、描述）
    - 实现编辑和删除标签功能（使用st.button）
    - 实现标签数量徽章显示（使用st.badge或st.metric）
    - 调用API端点：POST /api/v1/categories/{id}/tags, GET /api/v1/categories/{id}/tags, PUT /api/v1/tags/{id}, DELETE /api/v1/tags/{id}
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14_
  

  - [-] 8.1.8 增强JD评估页面以支持综合评估


    - 在src/ui/app.py的JD分析页面评估结果中，添加三个维度贡献度展示（使用st.columns和st.metric）
    - 展示企业价值评级（使用st.success/info/warning显示高价值/中价值/低价值）
    - 展示核心岗位判断（使用st.checkbox或st.badge显示是/否）
    - 展示分类标签对评估的影响说明（使用st.info或st.expander）
    - 添加手动修改评估结果的功能（使用st.form，包含质量分数、企业价值、核心岗位判断的输入）
    - 添加修改原因输入框（使用st.text_area）
    - 展示修改历史记录（使用st.expander显示manual_modifications数组）
    - 标识哪些结果是系统生成的，哪些是手动修改的（使用st.badge或颜色标识）
    - 调用API端点：PUT /api/v1/jd/{id}/evaluation
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14, 2.29, 2.30, 2.31, 2.32, 2.33_
  
  - [x] 8.2 实现问卷生成和管理页面

    - 选择JD生成问卷
    - 问卷预览和编辑
    - 问卷分享链接生成
    - _需求: 5.1, 5.2, 5.3, 5.4, 5.5, 5.9_
  
  - [x] 8.3 实现问卷填写页面

    - 问卷题目展示
    - 答案收集表单
    - 提交和结果展示
    - _需求: 5.6, 5.7, 5.8, 5.10_
  
  - [x] 8.4 实现匹配结果展示页面

    - 匹配度分数可视化
    - 维度得分雷达图
    - 优势和差距列表
    - 候选人排名列表
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 6.3_
  
  - [x] 8.5 实现模板管理页面

    - 模板列表展示
    - 创建和编辑模板表单
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5_


- [ ] 9. 文件解析和批量处理功能
  - [x] 9.1 实现文件解析服务（FileParserService）







    - 实现TXT文件解析（支持UTF-8、GBK、GB2312等编码）
    - 实现PDF文档解析（使用PyPDF2）
    - 实现DOCX文档解析（使用python-docx）
    - 实现DOC文档解析（使用textract，可选）
    - 实现文件格式自动识别
    - 实现文件验证（大小、格式）
    - 实现批量验证（数量、总大小）
    - _需求: 1.16, 1.17, 1.18, 1.19, 1.20_
  
  - [x] 9.2 添加文件解析依赖库






    - 添加PyPDF2到requirements.txt
    - 添加python-docx到requirements.txt
    - 添加python-magic到requirements.txt（文件类型检测）
    - 可选：添加textract到requirements.txt
    - _需求: 1.16, 1.17_

- [ ] 10. 部署配置

  - [x] 10.1 创建Docker配置



    - 编写Dockerfile
    - 编写docker-compose.yml（包含FastAPI、Redis、Streamlit）
    - _需求: 所有需求_
  
  - [x] 10.2 创建启动脚本




    - 编写Agent启动脚本
    - 编写服务健康检查脚本
    - _需求: 所有需求_
  
  - [x] 10.3 编写部署文档









    - 安装说明
    - 配置说明
    - 使用指南
    - _需求: 所有需求_

- [x] 11. 测试和优化








  - [x] 11.1 编写Agent单元测试











    - 测试每个Agent的核心功能
    - 测试BatchUploadAgent的文件处理逻辑
    - 测试FileParserService的各格式解析
    - 使用Mock LLM进行测试
    - _需求: 所有需求_
  

  - [x] 11.2 编写API集成测试






    - 测试所有API端点
    - 测试文件上传端点（单个和批量）
    - 测试批量处理工作流完整性
    - 测试文件格式验证和错误处理
    - _需求: 所有需求_
  

  - [x] 11.3 编写批量上传功能测试







    - 测试单个文件上传（TXT、PDF、DOCX）
    - 测试批量上传5个文件
    - 测试批量上传20个文件（边界测试）
    - 测试上传超过20个文件（应拒绝）
    - 测试上传不支持格式（应提示错误）
    - 测试上传超大文件（应拒绝）
    - 测试上传损坏文件（应跳过）
    - 测试并发批量上传
    - _需求: 1.16, 1.17, 1.18, 1.19, 1.20, 1.21, 1.22_
  


  - [x] 11.4 性能优化






    - LLM调用优化
    - 缓存策略优化
    - 数据库查询优化
    - 批量文件处理并行化优化
    - 文件解析性能优化
    - _需求: 所有需求_
