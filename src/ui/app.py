"""Streamlit主应用 - 岗位JD分析器"""

import streamlit as st
import sys
import os
import asyncio
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.schemas import EvaluationModel

# API基础URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# 页面配置
st.set_page_config(
    page_title="岗位JD分析器",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-header">📋 岗位JD分析器</div>', unsafe_allow_html=True)
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("🧭 功能导航")
    page = st.radio(
        "选择功能",
        [
            "📝 JD分析",
            "📤 批量上传",
            "🗂️ 职位分类管理",
            "📋 问卷管理",
            "🎯 匹配结果",
            "📄 模板管理",
            "📚 历史记录",
            "ℹ️ 关于"
        ]
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ 评估模型")
    model_type = st.selectbox(
        "选择评估模型",
        [
            ("标准评估", EvaluationModel.STANDARD.value),
            ("美世国际职位评估法", EvaluationModel.MERCER_IPE.value),
            ("因素比较法", EvaluationModel.FACTOR_COMPARISON.value)
        ],
        format_func=lambda x: x[0]
    )[1]
    
    st.markdown("---")
    st.markdown("### 📊 系统状态")
    st.success("✅ API服务正常")
    st.info(f"🕐 {datetime.now().strftime('%H:%M:%S')}")


# ==================== 辅助函数 ====================

def api_request(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """发送API请求"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API请求失败: {str(e)}")
        return {"success": False, "error": str(e)}


def format_score_color(score: float) -> str:
    """根据分数返回颜色"""
    if score >= 90:
        return "🟢"
    elif score >= 80:
        return "🟡"
    elif score >= 70:
        return "🟠"
    else:
        return "🔴"


def display_quality_badge(score: float):
    """显示质量徽章"""
    if score >= 90:
        st.success("🌟 优秀 - JD质量很高")
    elif score >= 80:
        st.info("👍 良好 - JD质量不错，有小幅改进空间")
    elif score >= 70:
        st.warning("⚠️ 中等 - JD需要一些改进")
    else:
        st.error("❌ 较差 - JD需要大幅改进")


# ==================== 页面路由 ====================

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
                        from datetime import datetime
                        
                        jd = JobDescription(**jd_data)
                        
                        quality_score = QualityScore(**eval_data.get("quality_score", {}))
                        evaluation = EvaluationResult(
                            **{**eval_data, "quality_score": quality_score}
                        )
                        
                        # 设置 jd_text 用于后续显示
                        jd_text = jd.raw_text
                        
                        st.success(f"✅ 文件 {uploaded_file.name} 分析完成！")
                        
                        # 直接显示结果（跳过后面的分析步骤）
                        result = {"jd": jd, "evaluation": evaluation}
                        
                        # 保存到历史记录（与批量上传保持一致）
                        if "analysis_history" not in st.session_state:
                            st.session_state.analysis_history = []
                        
                        st.session_state.analysis_history.append({
                            "jd": jd,
                            "evaluation": evaluation,
                            "timestamp": jd.created_at
                        })
                        
                    else:
                        error_msg = response.get("error", "未知错误")
                        st.error(f"❌ 文件上传失败: {error_msg}")
                        st.info("💡 提示：请确保 API 服务正在运行（http://localhost:8000）")
                        st.stop()
                    
                except Exception as e:
                    st.error(f"❌ 文件上传失败: {str(e)}")
                    st.info("💡 提示：请确保 API 服务正在运行，或使用'文本输入'方式")
                    st.stop()
        
        # 检查是否已经通过文件上传获得了结果
        if input_method == "📎 文件上传" and uploaded_file and 'result' in locals():
            # 文件上传已经完成分析，直接使用结果
            jd = result["jd"]
            evaluation = result["evaluation"]
        elif jd_text:
            with st.spinner("🤖 AI正在分析中..."):
                try:
                    # 通过API执行分析
                    response = api_request(
                        "POST",
                        "/jd/analyze",
                        json={
                            "jd_text": jd_text,
                            "model_type": model_type
                        }
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
                        
                        st.success("✅ 分析完成！")
                        
                        # 保存到session state（文本输入方式）
                        if "analysis_history" not in st.session_state:
                            st.session_state.analysis_history = []
                        
                        st.session_state.analysis_history.append({
                            "jd": jd,
                            "evaluation": evaluation,
                            "timestamp": jd.created_at
                        })
                    else:
                        error_msg = response.get("error", "未知错误")
                        st.error(f"❌ 分析失败: {error_msg}")
                        st.info("💡 提示：请确保 API 服务正在运行（http://localhost:8000）")
                        st.stop()
                    
                except Exception as e:
                    st.error(f"❌ 分析失败: {str(e)}")
                    st.exception(e)
                    st.stop()
        else:
            st.stop()
        
        # 统一的结果显示逻辑（文件上传和文本输入共享）
        if 'jd' in locals() and 'evaluation' in locals():
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

# 📤 批量上传页面
elif page == "📤 批量上传":
    st.header("📤 批量上传JD文件")
    
    st.info("💡 支持批量上传最多20个JD文件，系统将自动解析并分析每个文件")
    
    # 文件上传
    uploaded_files = st.file_uploader(
        "选择多个JD文件",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True,
        help="支持TXT、PDF、DOCX格式，单个文件最大10MB，总计最多20个文件"
    )
    
    if uploaded_files:
        # 显示文件列表
        st.subheader(f"📋 已选择 {len(uploaded_files)} 个文件")
        
        # 验证文件数量
        if len(uploaded_files) > 20:
            st.error("❌ 文件数量超过限制！最多支持20个文件")
            st.stop()
        
        # 显示文件信息
        file_data = []
        total_size = 0
        for file in uploaded_files:
            size_kb = file.size / 1024
            total_size += file.size
            file_data.append({
                "文件名": file.name,
                "大小": f"{size_kb:.1f} KB",
                "格式": file.name.split('.')[-1].upper()
            })
        
        import pandas as pd
        df = pd.DataFrame(file_data)
        st.dataframe(df, use_container_width=True)
        
        # 显示总大小
        total_size_mb = total_size / (1024 * 1024)
        if total_size_mb > 100:
            st.error(f"❌ 总文件大小超过限制！当前: {total_size_mb:.1f} MB，最大: 100 MB")
            st.stop()
        else:
            st.success(f"✅ 总大小: {total_size_mb:.2f} MB / 100 MB")
        
        # 开始批量处理
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            process_button = st.button("🚀 开始批量处理", type="primary", use_container_width=True)
        
        if process_button:
            st.markdown("---")
            st.subheader("📊 处理进度")
            
            # 初始化结果存储
            if "batch_results" not in st.session_state:
                st.session_state.batch_results = []
            
            st.session_state.batch_results = []
            
            # 进度条
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 结果容器
            results_container = st.container()
            
            success_count = 0
            failed_count = 0
            
            # 处理每个文件
            for idx, file in enumerate(uploaded_files):
                current_progress = (idx) / len(uploaded_files)
                progress_bar.progress(current_progress)
                status_text.text(f"正在处理: {file.name} ({idx + 1}/{len(uploaded_files)})")
                
                try:
                    from src.utils.file_parser import file_parser
                    
                    # 解析文件
                    file_content = file.read()
                    jd_text = file_parser.parse_file(file_content, file.name)
                    
                    # 通过API分析JD
                    response = api_request(
                        "POST",
                        "/jd/analyze",
                        json={
                            "jd_text": jd_text,
                            "model_type": model_type
                        }
                    )
                    
                    if response.get("success"):
                        # 从 API 响应中获取结果
                        data = response.get("data", {})
                        jd_data = data.get("jd", {})
                        eval_data = data.get("evaluation", {})
                        
                        # 重构为对象
                        from src.models.schemas import JobDescription, EvaluationResult, QualityScore
                        
                        jd = JobDescription(**jd_data)
                        quality_score = QualityScore(**eval_data.get("quality_score", {}))
                        evaluation = EvaluationResult(
                            **{**eval_data, "quality_score": quality_score}
                        )
                        
                        # 保存结果
                        st.session_state.batch_results.append({
                            "status": "success",
                            "filename": file.name,
                            "jd": jd,
                            "evaluation": evaluation
                        })
                        
                        success_count += 1
                    else:
                        raise Exception(response.get("error", "API调用失败"))
                    
                except Exception as e:
                    st.session_state.batch_results.append({
                        "status": "failed",
                        "filename": file.name,
                        "error": str(e)
                    })
                    failed_count += 1
            
            # 完成
            progress_bar.progress(1.0)
            status_text.text("✅ 批量处理完成！")
            
            # 显示汇总
            st.markdown("---")
            st.subheader("📈 处理结果汇总")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总数", len(uploaded_files))
            with col2:
                st.metric("成功", success_count, delta=None, delta_color="normal")
            with col3:
                st.metric("失败", failed_count, delta=None, delta_color="inverse")
            
            # 显示详细结果
            st.markdown("---")
            
            # 成功的结果
            if success_count > 0:
                st.subheader("✅ 成功处理的文件")
                
                for result in st.session_state.batch_results:
                    if result["status"] == "success":
                        jd = result["jd"]
                        evaluation = result["evaluation"]
                        score = evaluation.quality_score.overall_score
                        
                        with st.expander(f"📄 {result['filename']} - {jd.job_title} (质量分数: {score:.1f})"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.markdown(f"**职位**: {jd.job_title}")
                                st.markdown(f"**部门**: {jd.department or '未指定'}")
                                st.markdown(f"**地点**: {jd.location or '未指定'}")
                                
                                if jd.responsibilities:
                                    st.markdown("**职责**:")
                                    for resp in jd.responsibilities[:3]:
                                        st.markdown(f"- {resp}")
                                    if len(jd.responsibilities) > 3:
                                        st.markdown(f"- ... 还有 {len(jd.responsibilities) - 3} 条")
                            
                            with col2:
                                st.metric("质量分数", f"{score:.1f}")
                                st.metric("完整性", f"{evaluation.quality_score.completeness:.1f}")
                                st.metric("清晰度", f"{evaluation.quality_score.clarity:.1f}")
                                
                                # 质量等级
                                if score >= 90:
                                    st.success("🌟 优秀")
                                elif score >= 80:
                                    st.info("👍 良好")
                                elif score >= 70:
                                    st.warning("⚠️ 中等")
                                else:
                                    st.error("❌ 较差")
            
            # 失败的结果
            if failed_count > 0:
                st.markdown("---")
                st.subheader("❌ 处理失败的文件")
                
                for result in st.session_state.batch_results:
                    if result["status"] == "failed":
                        with st.expander(f"❌ {result['filename']}"):
                            st.error(f"错误信息: {result['error']}")
                            st.info("💡 建议: 请检查文件格式是否正确，或尝试重新上传")
            
            # 保存到历史记录
            if "analysis_history" not in st.session_state:
                st.session_state.analysis_history = []
            
            for result in st.session_state.batch_results:
                if result["status"] == "success":
                    st.session_state.analysis_history.append({
                        "jd": result["jd"],
                        "evaluation": result["evaluation"],
                        "timestamp": result["jd"].created_at
                    })
    
    else:
        st.info("👆 请选择要上传的JD文件")
        
        # 使用说明
        with st.expander("📖 使用说明"):
            st.markdown("""
            ### 批量上传功能说明
            
            **支持的文件格式：**
            - `.txt` - 纯文本文件
            - `.pdf` - PDF文档
            - `.docx` - Word文档（2007及以上版本）
            
            **限制规则：**
            - 单个文件最大: 10MB
            - 批量上传最多: 20个文件
            - 总大小限制: 100MB
            
            **使用步骤：**
            1. 点击"选择多个JD文件"按钮
            2. 选择要上传的文件（可多选）
            3. 查看文件列表确认无误
            4. 点击"开始批量处理"按钮
            5. 等待处理完成，查看结果
            
            **注意事项：**
            - 系统会自动跳过无法解析的文件
            - 处理时间取决于文件数量和大小
            - 所有成功处理的JD会自动保存到历史记录
            """)

# 🗂️ 职位分类管理页面
elif page == "🗂️ 职位分类管理":
    st.header("🗂️ 职位分类管理")
    
    st.info("💡 管理职位分类体系（最多3层级），为第三层级分类添加样本JD以提高自动分类准确性")
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 分类树")
        
        # 获取分类树
        try:
            response = api_request("GET", "/categories/tree")
            
            if response.get("success"):
                tree_data = response.get("data", [])
                
                if tree_data:
                    # 递归显示分类树
                    def display_tree(nodes: List[Dict], level: int = 1):
                        for node in nodes:
                            indent = "　" * (level - 1)
                            icon = "📁" if level == 1 else ("📂" if level == 2 else "📄")
                            
                            with st.expander(f"{indent}{icon} {node['name']} (L{level})", expanded=(level == 1)):
                                col_a, col_b = st.columns([3, 1])
                                
                                with col_a:
                                    st.markdown(f"**ID**: `{node['id']}`")
                                    if node.get('description'):
                                        st.markdown(f"**描述**: {node['description']}")
                                    
                                    # 显示样本JD（仅第三层级）
                                    if level == 3 and node.get('sample_jd_ids'):
                                        st.markdown(f"**样本JD数量**: {len(node['sample_jd_ids'])}")
                                        for jd_id in node['sample_jd_ids']:
                                            st.markdown(f"- `{jd_id}`")
                                
                                with col_b:
                                    if st.button("✏️ 编辑", key=f"edit_{node['id']}"):
                                        st.session_state.edit_category_id = node['id']
                                        st.session_state.edit_category_data = node
                                        st.rerun()
                                    
                                    if st.button("🗑️ 删除", key=f"del_{node['id']}"):
                                        del_response = api_request("DELETE", f"/categories/{node['id']}")
                                        if del_response.get("success"):
                                            st.success("✅ 删除成功")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {del_response.get('error', '删除失败')}")
                                
                                # 递归显示子分类
                                if node.get('children'):
                                    display_tree(node['children'], level + 1)
                    
                    display_tree(tree_data)
                else:
                    st.info("📝 暂无分类数据，请从右侧创建第一个分类")
                    st.markdown("""
                    **快速开始：**
                    1. 在右侧表单中输入分类名称
                    2. 选择"第1层级"
                    3. 点击"创建分类"按钮
                    """)
            else:
                error_msg = response.get('error', '未知错误')
                st.warning(f"⚠️ 无法获取分类数据: {error_msg}")
                st.info("💡 这可能是因为分类数据已被清空。您可以从右侧创建新的分类。")
        except Exception as e:
            st.error(f"❌ 获取分类树时发生错误: {str(e)}")
            st.info("💡 请检查 API 服务是否正常运行，或从右侧创建新的分类。")
    
    with col2:
        st.subheader("➕ 创建新分类")
        
        with st.form("create_category_form"):
            cat_name = st.text_input("分类名称*", placeholder="例如：技术类")
            cat_level = st.selectbox("层级*", [1, 2, 3], format_func=lambda x: f"第{x}层级")
            
            # 获取可选的父级分类
            parent_id = None
            if cat_level > 1:
                parent_response = api_request("GET", f"/categories?level={cat_level - 1}")
                if parent_response.get("success"):
                    parent_options = parent_response.get("data", [])
                    if parent_options:
                        parent_dict = {p['name']: p['id'] for p in parent_options}
                        parent_name = st.selectbox(
                            f"父级分类（第{cat_level-1}层级）*",
                            list(parent_dict.keys())
                        )
                        parent_id = parent_dict[parent_name]
                    else:
                        st.warning(f"⚠️ 请先创建第{cat_level-1}层级分类")
            
            cat_desc = st.text_area("描述", placeholder="可选")
            
            # 样本JD（仅第三层级）
            sample_jd_ids = []
            if cat_level == 3:
                st.markdown("**样本JD（1-2个）**")
                sample_jd_1 = st.text_input("样本JD ID 1", placeholder="例如：jd_abc123")
                sample_jd_2 = st.text_input("样本JD ID 2", placeholder="可选")
                
                if sample_jd_1:
                    sample_jd_ids.append(sample_jd_1)
                if sample_jd_2:
                    sample_jd_ids.append(sample_jd_2)
            
            submitted = st.form_submit_button("✅ 创建分类", use_container_width=True)
            
            if submitted:
                if not cat_name:
                    st.error("❌ 请输入分类名称")
                elif cat_level > 1 and not parent_id:
                    st.error(f"❌ 请选择父级分类")
                else:
                    create_data = {
                        "name": cat_name,
                        "level": cat_level,
                        "parent_id": parent_id,
                        "description": cat_desc if cat_desc else None,
                        "sample_jd_ids": sample_jd_ids
                    }
                    
                    response = api_request("POST", "/categories", json=create_data)
                    
                    if response.get("success"):
                        st.success("✅ 分类创建成功！")
                        st.rerun()
                    else:
                        st.error(f"❌ {response.get('detail', '创建失败')}")
        
        # 编辑分类
        if "edit_category_id" in st.session_state:
            st.markdown("---")
            st.subheader("✏️ 编辑分类")
            
            cat_data = st.session_state.edit_category_data
            
            with st.form("edit_category_form"):
                new_name = st.text_input("分类名称", value=cat_data['name'])
                new_desc = st.text_area("描述", value=cat_data.get('description', ''))
                
                # 样本JD更新（仅第三层级）
                if cat_data['level'] == 3:
                    st.markdown("**更新样本JD**")
                    current_samples = cat_data.get('sample_jd_ids', [])
                    sample_1 = st.text_input("样本JD ID 1", value=current_samples[0] if len(current_samples) > 0 else "")
                    sample_2 = st.text_input("样本JD ID 2", value=current_samples[1] if len(current_samples) > 1 else "")
                    
                    new_samples = []
                    if sample_1:
                        new_samples.append(sample_1)
                    if sample_2:
                        new_samples.append(sample_2)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    update_btn = st.form_submit_button("💾 保存", use_container_width=True)
                with col_b:
                    cancel_btn = st.form_submit_button("❌ 取消", use_container_width=True)
                
                if update_btn:
                    # 更新基本信息
                    update_data = {
                        "name": new_name,
                        "description": new_desc if new_desc else None
                    }
                    response = api_request("PUT", f"/categories/{cat_data['id']}", json=update_data)
                    
                    # 更新样本JD（如果是第三层级）
                    if cat_data['level'] == 3:
                        sample_response = api_request(
                            "PUT",
                            f"/categories/{cat_data['id']}/samples",
                            json={"sample_jd_ids": new_samples}
                        )
                    
                    if response.get("success"):
                        st.success("✅ 更新成功！")
                        del st.session_state.edit_category_id
                        del st.session_state.edit_category_data
                        st.rerun()
                    else:
                        st.error(f"❌ {response.get('detail', '更新失败')}")
                
                if cancel_btn:
                    del st.session_state.edit_category_id
                    del st.session_state.edit_category_data
                    st.rerun()

# 📋 问卷管理页面
elif page == "📋 问卷管理":
    st.header("📋 问卷生成和管理")
    
    tab1, tab2 = st.tabs(["📝 生成问卷", "📚 问卷列表"])
    
    with tab1:
        st.subheader("📝 生成新问卷")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.form("generate_questionnaire_form"):
                # 选择JD
                st.markdown("**选择岗位JD**")
                jd_id_input = st.text_input("JD ID*", placeholder="例如：jd_abc123")
                
                # 评估模型
                quest_model = st.selectbox(
                    "评估模型*",
                    [
                        ("标准评估", "standard"),
                        ("美世国际职位评估法", "mercer_ipe"),
                        ("因素比较法", "factor_comparison")
                    ],
                    format_func=lambda x: x[0]
                )[1]
                
                # 自定义标题和描述
                quest_title = st.text_input("问卷标题", placeholder="留空则自动生成")
                quest_desc = st.text_area("问卷描述", placeholder="留空则自动生成")
                
                generate_btn = st.form_submit_button("🚀 生成问卷", type="primary", use_container_width=True)
                
                if generate_btn:
                    if not jd_id_input:
                        st.error("❌ 请输入JD ID")
                    else:
                        with st.spinner("🤖 AI正在生成问卷..."):
                            gen_data = {
                                "jd_id": jd_id_input,
                                "evaluation_model": quest_model,
                                "title": quest_title if quest_title else None,
                                "description": quest_desc if quest_desc else None
                            }
                            
                            response = api_request("POST", "/questionnaire/generate", json=gen_data)
                            
                            if response.get("success"):
                                quest_data = response.get("data", {})
                                st.success("✅ 问卷生成成功！")
                                
                                st.markdown("---")
                                st.markdown(f"**问卷ID**: `{quest_data['id']}`")
                                st.markdown(f"**标题**: {quest_data['title']}")
                                st.markdown(f"**描述**: {quest_data['description']}")
                                st.markdown(f"**题目数量**: {len(quest_data['questions'])}")
                                
                                # 分享链接
                                if quest_data.get('share_link'):
                                    st.markdown(f"**分享链接**: {quest_data['share_link']}")
                                    st.code(quest_data['share_link'], language=None)
                                
                                # 显示题目预览
                                with st.expander("📄 查看题目"):
                                    for idx, q in enumerate(quest_data['questions'], 1):
                                        st.markdown(f"**{idx}. {q['question_text']}**")
                                        st.markdown(f"- 类型: {q['question_type']}")
                                        st.markdown(f"- 维度: {q['dimension']}")
                                        if q.get('options'):
                                            st.markdown(f"- 选项: {', '.join(q['options'])}")
                                        st.markdown("---")
                            else:
                                st.error(f"❌ {response.get('detail', '生成失败')}")
        
        with col2:
            st.markdown("### 💡 使用说明")
            st.info("""
            **生成问卷步骤：**
            1. 输入已分析的JD ID
            2. 选择评估模型
            3. 可选：自定义标题和描述
            4. 点击生成按钮
            5. 复制分享链接发送给候选人
            
            **问卷类型：**
            - 单选题：选择一个答案
            - 多选题：选择多个答案
            - 量表题：1-5分评分
            - 开放题：文本回答
            """)
    
    with tab2:
        st.subheader("📚 已生成的问卷")
        
        # 获取问卷列表
        response = api_request("GET", "/questionnaire")
        
        if response.get("success"):
            questionnaires = response.get("data", [])
            
            if questionnaires:
                st.info(f"共有 {len(questionnaires)} 份问卷")
                
                for quest in questionnaires:
                    with st.expander(f"📋 {quest['title']} (ID: {quest['id']})"):
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            st.markdown(f"**JD ID**: `{quest['jd_id']}`")
                            st.markdown(f"**描述**: {quest['description']}")
                            st.markdown(f"**题目数量**: {len(quest['questions'])}")
                            st.markdown(f"**评估模型**: {quest['evaluation_model']}")
                            st.markdown(f"**创建时间**: {quest['created_at']}")
                            
                            if quest.get('share_link'):
                                st.markdown(f"**分享链接**: {quest['share_link']}")
                        
                        with col_b:
                            if st.button("📄 查看详情", key=f"view_{quest['id']}"):
                                st.session_state.view_quest_id = quest['id']
                                st.rerun()
            else:
                st.info("暂无问卷，请先生成问卷")
        else:
            st.error("❌ 获取问卷列表失败")

# 🎯 匹配结果页面
elif page == "🎯 匹配结果":
    st.header("🎯 匹配结果展示")
    
    # 获取所有匹配结果
    response = api_request("GET", "/match")
    
    if response.get("success"):
        matches = response.get("data", [])
        
        if matches:
            st.info(f"共有 {len(matches)} 条匹配记录")
            
            # 按JD分组显示
            jd_groups = {}
            for match in matches:
                jd_id = match['jd_id']
                if jd_id not in jd_groups:
                    jd_groups[jd_id] = []
                jd_groups[jd_id].append(match)
            
            for jd_id, jd_matches in jd_groups.items():
                with st.expander(f"📄 JD: {jd_id} ({len(jd_matches)} 个匹配结果)", expanded=True):
                    # 按匹配度排序
                    jd_matches.sort(key=lambda x: x['overall_score'], reverse=True)
                    
                    # 显示排名列表
                    for idx, match in enumerate(jd_matches, 1):
                        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                        
                        with col1:
                            st.markdown(f"**#{idx}**")
                        
                        with col2:
                            score = match['overall_score']
                            st.markdown(f"{format_score_color(score)} **匹配度**: {score:.1f}分")
                        
                        with col3:
                            st.markdown(f"**ID**: `{match['id']}`")
                        
                        with col4:
                            if st.button("📊 查看详情", key=f"match_{match['id']}"):
                                st.session_state.view_match_id = match['id']
                                st.rerun()
                    
                    st.markdown("---")
            
            # 显示匹配详情
            if "view_match_id" in st.session_state:
                match_id = st.session_state.view_match_id
                detail_response = api_request("GET", f"/match/{match_id}")
                
                if detail_response.get("success"):
                    match_data = detail_response.get("data", {})
                    
                    st.markdown("---")
                    st.subheader(f"📊 匹配详情 - {match_id}")
                    
                    # 综合分数
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("综合匹配度", f"{match_data['overall_score']:.1f}分")
                    with col2:
                        st.metric("JD ID", match_data['jd_id'])
                    with col3:
                        st.metric("创建时间", match_data['created_at'][:10])
                    
                    # 维度得分雷达图
                    if match_data.get('dimension_scores'):
                        st.markdown("#### 📈 各维度得分")
                        
                        # 使用Streamlit的原生图表
                        import plotly.graph_objects as go
                        
                        dimensions = list(match_data['dimension_scores'].keys())
                        scores = list(match_data['dimension_scores'].values())
                        
                        fig = go.Figure(data=go.Scatterpolar(
                            r=scores,
                            theta=dimensions,
                            fill='toself',
                            name='匹配度'
                        ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100]
                                )
                            ),
                            showlegend=False,
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 表格显示
                        df = pd.DataFrame({
                            "维度": dimensions,
                            "得分": [f"{s:.1f}" for s in scores]
                        })
                        st.dataframe(df, use_container_width=True)
                    
                    # 优势和差距
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### ✅ 优势")
                        if match_data.get('strengths'):
                            for strength in match_data['strengths']:
                                st.success(f"✓ {strength}")
                        else:
                            st.info("暂无优势分析")
                    
                    with col2:
                        st.markdown("#### ⚠️ 差距")
                        if match_data.get('gaps'):
                            for gap in match_data['gaps']:
                                st.warning(f"✗ {gap}")
                        else:
                            st.info("暂无差距分析")
                    
                    # 建议
                    st.markdown("#### 💡 改进建议")
                    if match_data.get('recommendations'):
                        for rec in match_data['recommendations']:
                            st.info(f"→ {rec}")
                    else:
                        st.info("暂无改进建议")
                    
                    # 下载报告
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📥 下载HTML报告", use_container_width=True):
                            st.info("HTML报告下载功能开发中...")
                    
                    with col2:
                        if st.button("📥 下载JSON报告", use_container_width=True):
                            st.info("JSON报告下载功能开发中...")
                    
                    with col3:
                        if st.button("❌ 关闭", use_container_width=True):
                            del st.session_state.view_match_id
                            st.rerun()
        else:
            st.info("暂无匹配结果")
    else:
        st.error("❌ 获取匹配结果失败")

# 📄 模板管理页面
elif page == "📄 模板管理":
    st.header("📄 模板管理")
    
    tab1, tab2 = st.tabs(["📚 模板列表", "➕ 创建模板"])
    
    with tab1:
        st.subheader("📚 已有模板")
        
        # 筛选器
        filter_type = st.selectbox(
            "筛选模板类型",
            ["全部", "parsing", "evaluation", "questionnaire"],
            format_func=lambda x: {
                "全部": "全部模板",
                "parsing": "解析模板",
                "evaluation": "评估模板",
                "questionnaire": "问卷模板"
            }.get(x, x)
        )
        
        # 获取模板列表
        endpoint = "/templates" if filter_type == "全部" else f"/templates?template_type={filter_type}"
        response = api_request("GET", endpoint)
        
        if response.get("success"):
            templates = response.get("data", [])
            
            if templates:
                st.info(f"共有 {len(templates)} 个模板")
                
                for tmpl in templates:
                    with st.expander(f"📄 {tmpl['name']} ({tmpl['template_type']})"):
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            st.markdown(f"**ID**: `{tmpl['id']}`")
                            st.markdown(f"**类型**: {tmpl['template_type']}")
                            st.markdown(f"**创建时间**: {tmpl['created_at']}")
                            st.markdown("**配置**:")
                            st.json(tmpl['config'])
                        
                        with col_b:
                            if st.button("✏️ 编辑", key=f"edit_tmpl_{tmpl['id']}"):
                                st.session_state.edit_template_id = tmpl['id']
                                st.session_state.edit_template_data = tmpl
                                st.rerun()
                            
                            if st.button("🗑️ 删除", key=f"del_tmpl_{tmpl['id']}"):
                                del_response = api_request("DELETE", f"/templates/{tmpl['id']}")
                                if del_response.get("success"):
                                    st.success("✅ 删除成功")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {del_response.get('detail', '删除失败')}")
            else:
                st.info("暂无模板")
        else:
            st.error("❌ 获取模板列表失败")
    
    with tab2:
        st.subheader("➕ 创建新模板")
        
        with st.form("create_template_form"):
            tmpl_name = st.text_input("模板名称*", placeholder="例如：技术岗位解析模板")
            tmpl_type = st.selectbox(
                "模板类型*",
                ["parsing", "evaluation", "questionnaire"],
                format_func=lambda x: {
                    "parsing": "解析模板",
                    "evaluation": "评估模板",
                    "questionnaire": "问卷模板"
                }.get(x, x)
            )
            
            st.markdown("**模板配置（JSON格式）**")
            
            # 根据类型提供示例
            if tmpl_type == "parsing":
                default_config = """{
    "custom_fields": [
        "job_title",
        "department",
        "location",
        "responsibilities",
        "required_skills",
        "preferred_skills",
        "qualifications",
        "tech_stack",
        "team_size"
    ]
}"""
            elif tmpl_type == "evaluation":
                default_config = """{
    "dimensions": ["completeness", "clarity", "professionalism"],
    "weights": {
        "completeness": 0.33,
        "clarity": 0.33,
        "professionalism": 0.34
    }
}"""
            else:
                default_config = """{
    "question_count": 10,
    "include_dimensions": ["技能", "经验", "行为", "价值观"]
}"""
            
            tmpl_config = st.text_area(
                "配置内容*",
                value=default_config,
                height=200,
                help="请输入有效的JSON格式配置"
            )
            
            create_btn = st.form_submit_button("✅ 创建模板", type="primary", use_container_width=True)
            
            if create_btn:
                if not tmpl_name or not tmpl_config:
                    st.error("❌ 请填写所有必填字段")
                else:
                    try:
                        import json
                        config_dict = json.loads(tmpl_config)
                        
                        create_data = {
                            "name": tmpl_name,
                            "template_type": tmpl_type,
                            "config": config_dict
                        }
                        
                        response = api_request("POST", "/templates", json=create_data)
                        
                        if response.get("success"):
                            st.success("✅ 模板创建成功！")
                            st.rerun()
                        else:
                            st.error(f"❌ {response.get('detail', '创建失败')}")
                    except json.JSONDecodeError:
                        st.error("❌ 配置格式错误，请输入有效的JSON")

# 📚 历史记录页面
elif page == "📚 历史记录":
    st.header("📚 历史记录")
    
    if "analysis_history" in st.session_state and st.session_state.analysis_history:
        st.info(f"共有 {len(st.session_state.analysis_history)} 条分析记录")
        
        for i, record in enumerate(reversed(st.session_state.analysis_history), 1):
            with st.expander(f"📄 {record['jd'].job_title} - {record['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**职位**: {record['jd'].job_title}")
                    st.markdown(f"**部门**: {record['jd'].department or '未指定'}")
                    st.markdown(f"**地点**: {record['jd'].location or '未指定'}")
                
                with col2:
                    score = record['evaluation'].quality_score.overall_score
                    st.metric("质量分数", f"{score:.1f}")
    else:
        st.info("暂无分析记录")

# ℹ️ 关于页面
elif page == "ℹ️ 关于":
    st.header("ℹ️ 关于")
    
    st.markdown("""
    ### 岗位JD分析器
    
    这是一个基于AI的智能岗位JD分析系统，帮助HR专业人员：
    
    - 🔍 **自动解析**: 快速提取JD中的关键信息
    - 📊 **质量评估**: 多维度评估JD质量
    - 💡 **优化建议**: 提供针对性的改进建议
    - 🎯 **候选人匹配**: 智能评估候选人匹配度（即将推出）
    
    ### 技术架构
    
    - **前端**: Streamlit
    - **后端**: FastAPI + Python
    - **AI引擎**: OpenAI/DeepSeek
    - **架构**: Agentic AI多Agent协作
    
    ### 版本信息
    
    - 版本: v0.1.0 (MVP)
    - 更新日期: 2024-01
    
    ### 使用说明
    
    1. 在"JD分析"页面输入或粘贴岗位JD文本
    2. 选择评估模型（侧边栏）
    3. 点击"开始分析"按钮
    4. 查看解析结果、质量评估和优化建议
    
    ### 反馈与支持
    
    如有问题或建议，请联系开发团队。
    """)

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>岗位JD分析器 v0.1.0 | Powered by AI</div>",
    unsafe_allow_html=True
)
