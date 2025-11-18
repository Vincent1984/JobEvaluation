# 📝 JD分析页面
if page == "📝 JD分析":
    st.header("📝 JD分析")
    
    # 输入方式选择
    input_method = st.radio(
        "选择输入方式",
        ["📝 文本输入", "📎 文件上传"],
        horizontal=True
    )
    
    jd_text = ""
    uploaded_file = None
    
    if input_method == "📝 文本输入":
        # 输入区域
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("输入岗位JD")
            jd_text = st.text_area(
                "请输入或粘贴岗位JD文本",
                height=300,
                placeholder="例如：\n\n职位：高级Python工程师\n\n职责：\n1. 负责后端服务开发\n2. 优化系统性能\n...",
                help="支持中文和英文JD"
            )
            
            analyze_button = st.button("🔍 开始分析", type="primary", use_container_width=True)
    
    else:  # 文件上传
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("上传岗位JD文件")
            uploaded_file = st.file_uploader(
                "选择文件",
                type=["txt", "pdf", "docx"],
                help="支持TXT、PDF、DOCX格式，单个文件最大10MB"
            )
            
            if uploaded_file:
                st.info(f"📄 已选择文件: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
            
            analyze_button = st.button("🔍 开始分析", type="primary", use_container_width=True, disabled=not uploaded_file)
    
    with col2:
        st.subheader("快速示例")
        if st.button("📄 加载示例JD", use_container_width=True):
            example_jd = """职位：高级Python后端工程师

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
- 本科及以上学历，计算机相关专业优先"""
            st.session_state.example_jd = example_jd
            st.rerun()
        
        if "example_jd" in st.session_state:
            jd_text = st.session_state.example_jd
            del st.session_state.example_jd
    
    # 分析结果
    if analyze_button:
        jd = None
        evaluation = None
        
        # 处理文件上传（通过 API）
        if input_method == "📎 文件上传" and uploaded_file:
            with st.spinner("📄 正在上传并解析文件..."):
                try:
                    # 准备文件上传
                    files = {
                        'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                    }
                    
                    # 上传到 API 进行解析和分析
                    response = api_request(
                        "POST",
                        f"/jd/upload?model_type={model_type}",
                        files=files
                    )
                    
                    if response.get("success"):
                        # 从 API 响应中获取结果
                        data = response.get("data", {})
                        jd_data = data.get("jd", {})
                        eval_data = data.get("evaluation", {})
                        
                        # 重构为对象（用于后续显示）
                        from src.models.schemas import JobDescription, EvaluationResult, QualityScore
                        
                        jd = JobDescription(**jd_data)
                        quality_score = QualityScore(**eval_data.get("quality_score", {}))
                        evaluation = EvaluationResult(
                            **{**eval_data, "quality_score": quality_score}
                        )
                        
                        st.success(f"✅ 文件 {uploaded_file.name} 分析完成！")
                        
                    else:
                        error_msg = response.get("error", "未知错误")
                        st.error(f"❌ 文件上传失败: {error_msg}")
                        st.info("💡 提示：请确保 API 服务正在运行（http://localhost:8000）")
                        st.stop()
                    
                except Exception as e:
                    st.error(f"❌ 文件上传失败: {str(e)}")
                    st.info("💡 提示：请确保 API 服务正在运行，或使用'文本输入'方式")
                    st.stop()
        
        # 处理文本输入
        elif jd_text:
            with st.spinner("🤖 AI正在分析中..."):
                try:
                    # 执行分析
                    result = run_async(mcp_client.analyze_jd(jd_text, model_type))
                    jd = result["jd"]
                    evaluation = result["evaluation"]
                    st.success("✅ 分析完成！")
                    
                except Exception as e:
                    st.error(f"❌ 分析失败: {str(e)}")
                    st.exception(e)
                    st.stop()
        else:
            st.stop()
        
        # 保存到历史记录（与批量上传保持一致）
        if jd and evaluation:
            if "analysis_history" not in st.session_state:
                st.session_state.analysis_history = []
            
            st.session_state.analysis_history.append({
                "jd": jd,
                "evaluation": evaluation,
                "timestamp": jd.created_at
            })
            
            # 统一的结果显示逻辑（文件上传和文本输入共享）
            st.markdown("---")
            
            # 显示结果
            tab1, tab2, tab3 = st.tabs(["📊 解析结果", "⭐ 质量评估", "💡 优化建议"])
            
            with tab1:
                st.subheader("解析结果")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("职位标题", jd.job_title)
                with col2:
                    st.metric("部门", jd.department or "未指定")
                with col3:
                    st.metric("地点", jd.location or "未指定")
                
                st.markdown("#### 职责描述")
                if jd.responsibilities:
                    for i, resp in enumerate(jd.responsibilities, 1):
                        st.markdown(f"{i}. {resp}")
                else:
                    st.info("未识别到职责描述")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 必备技能")
                    if jd.required_skills:
                        for skill in jd.required_skills:
                            st.markdown(f"- {skill}")
                    else:
                        st.info("未识别到必备技能")
                
                with col2:
                    st.markdown("#### 优选技能")
                    if jd.preferred_skills:
                        for skill in jd.preferred_skills:
                            st.markdown(f"- {skill}")
                    else:
                        st.info("未识别到优选技能")
                
                st.markdown("#### 任职资格")
                if jd.qualifications:
                    for qual in jd.qualifications:
                        st.markdown(f"- {qual}")
                else:
                    st.info("未识别到任职资格")
            
            with tab2:
                st.subheader("质量评估")
                
                # 综合分数
                score = evaluation.quality_score.overall_score
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "综合分数",
                        f"{score:.1f}",
                        delta=None,
                        help="综合质量评分（0-100）"
                    )
                
                with col2:
                    st.metric(
                        "完整性",
                        f"{evaluation.quality_score.completeness:.1f}",
                        help="信息完整程度"
                    )
                
                with col3:
                    st.metric(
                        "清晰度",
                        f"{evaluation.quality_score.clarity:.1f}",
                        help="描述清晰程度"
                    )
                
                with col4:
                    st.metric(
                        "专业性",
                        f"{evaluation.quality_score.professionalism:.1f}",
                        help="表述专业程度"
                    )
                
                # 分数条
                st.progress(score / 100)
                
                # 质量等级
                if score >= 90:
                    st.success("🌟 优秀 - JD质量很高")
                elif score >= 80:
                    st.info("👍 良好 - JD质量不错，有小幅改进空间")
                elif score >= 70:
                    st.warning("⚠️ 中等 - JD需要一些改进")
                else:
                    st.error("❌ 较差 - JD需要大幅改进")
                
                # 质量问题
                if evaluation.quality_score.issues:
                    st.markdown("#### 发现的问题")
                    for issue in evaluation.quality_score.issues:
                        severity = issue.get("severity", "medium")
                        if severity == "high":
                            st.error(f"🔴 {issue.get('description', '')}")
                        elif severity == "medium":
                            st.warning(f"🟡 {issue.get('description', '')}")
                        else:
                            st.info(f"🔵 {issue.get('description', '')}")
            
            with tab3:
                st.subheader("优化建议")
                
                if evaluation.recommendations:
                    st.markdown("#### 改进建议")
                    for i, rec in enumerate(evaluation.recommendations, 1):
                        st.markdown(f"{i}. {rec}")
                else:
                    st.success("✅ 暂无改进建议，JD质量很好！")
