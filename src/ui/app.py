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
            "📝 JD解析（第一步）",
            "⭐ JD评估（第二步）",
            "📤 批量上传",
            "🏢 企业管理",
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

# 📝 JD解析页面（第一步）
if page == "📝 JD解析（第一步）":
    st.header("📝 JD解析与保存（第一步）")
    st.info("💡 第一步：使用解析模板自动解析岗位JD并保存，为后续评估做准备")
    
    # 解析模板选择
    st.subheader("1️⃣ 选择解析模板")
    
    # 获取解析模板列表
    try:
        templates_response = api_request("GET", "/templates?template_type=parsing")
        parsing_templates = templates_response.get("data", []) if templates_response.get("success") else []
        # 额外过滤：确保只包含解析模板
        parsing_templates = [t for t in parsing_templates if t.get('template_type') == 'parsing']
    except:
        parsing_templates = []
    
    # 默认解析模板
    default_templates = []
    
    # 只包含解析模板
    all_templates = default_templates + parsing_templates
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_template = st.selectbox(
            "选择解析模板",
            options=all_templates,
            format_func=lambda x: f"{x['name']} - {x.get('description', '无描述')}",
            help="解析模板定义了从JD中提取哪些字段和信息"
        )
    
    with col2:
        if st.button("➕ 创建模板", use_container_width=True):
            st.info("💡 请前往'模板管理'页面创建自定义解析模板")
    
    st.markdown("---")
    
    # 输入方式选择
    st.subheader("2️⃣ 输入岗位JD")
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
            jd_text = st.text_area(
                "请输入或粘贴岗位JD文本",
                height=300,
                placeholder="例如：\n\n职位：高级Python工程师\n\n职责：\n1. 负责后端服务开发\n2. 优化系统性能\n...",
                help="支持中文和英文JD"
            )
        
        with col2:
            st.markdown("**快速示例**")
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
    
    else:  # 文件上传
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "选择文件",
                type=["txt", "pdf", "docx"],
                help="支持TXT、PDF、DOCX格式，单个文件最大10MB"
            )
            
            if uploaded_file:
                st.info(f"📄 已选择文件: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        with col2:
            st.markdown("**支持格式**")
            st.markdown("- 📄 TXT")
            st.markdown("- 📕 PDF")
            st.markdown("- 📘 DOCX")
    
    st.markdown("---")
    
    # 解析按钮
    st.subheader("3️⃣ 解析并保存")
    st.info("💡 职位分类将在第二步（JD评估）中选择，分类标签会影响评估结果")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if input_method == "📝 文本输入":
            analyze_button = st.button("🔍 解析并保存", type="primary", use_container_width=True, disabled=not jd_text)
        else:
            analyze_button = st.button("🔍 解析并保存", type="primary", use_container_width=True, disabled=not uploaded_file)
    
    # 解析结果
    if analyze_button:
        # 处理文件上传
        if input_method == "📎 文件上传" and uploaded_file:
            with st.spinner("📄 正在读取文件..."):
                try:
                    # 使用文件解析工具
                    from src.utils.file_parser import FileParserService
                    
                    file_content = uploaded_file.getvalue()
                    
                    # 验证文件
                    is_valid, error_msg = FileParserService.validate_file(
                        len(file_content), 
                        uploaded_file.name
                    )
                    
                    if not is_valid:
                        st.error(f"❌ {error_msg}")
                        st.stop()
                    
                    # 解析文件内容
                    jd_text = FileParserService.parse_file(file_content, uploaded_file.name)
                    
                    if not jd_text or not jd_text.strip():
                        st.error("❌ 文件内容为空或无法提取文本")
                        st.stop()
                    
                    st.success(f"✅ 文件 {uploaded_file.name} 读取成功")
                    
                except ImportError as e:
                    st.error(f"❌ 缺少必要的库: {str(e)}")
                    st.info("💡 提示：请安装相应的库（如 PyPDF2 或 python-docx）")
                    st.stop()
                except ValueError as e:
                    st.error(f"❌ 文件解析失败: {str(e)}")
                    st.stop()
                except Exception as e:
                    st.error(f"❌ 文件读取失败: {str(e)}")
                    st.stop()
        
        # 统一处理：文本输入和文件上传都使用相同的解析逻辑
        if jd_text:
            with st.spinner("🤖 AI正在解析JD..."):
                try:
                    # 第一步：只解析JD，不进行评估
                    # 评估将在第二步（JD评估页面）进行
                    response = api_request(
                        "POST",
                        "/jd/parse",  # ✅ 只解析，不评估
                        json={
                            "jd_text": jd_text,
                            "custom_fields": {}  # 可以传入自定义字段配置
                        }
                    )
                    
                    if response.get("success"):
                        # 从 API 响应中获取解析结果
                        jd_data = response.get("data", {})
                        
                        # 重构为对象
                        from src.models.schemas import JobDescription
                        
                        try:
                            jd = JobDescription(**jd_data)
                            
                            if input_method == "📎 文件上传":
                                st.success(f"✅ 文件 {uploaded_file.name} 解析完成！JD 已保存")
                            else:
                                st.success("✅ 解析完成！JD 已保存")
                            st.info("💡 下一步：前往'⭐ JD评估（第二步）'页面进行评估、选择分类和评估模板")
                        except Exception as e:
                            st.error(f"❌ 数据解析失败: {str(e)}")
                            st.warning("⚠️ API 返回的数据格式不完整")
                            st.stop()
                        
                        # 保存到session state（只保存JD，不保存评估结果）
                        if "analysis_history" not in st.session_state:
                            st.session_state.analysis_history = []
                        
                        st.session_state.analysis_history.append({
                            "jd": jd,
                            "evaluation": None,  # ✅ 第一步不进行评估
                            "timestamp": jd.created_at
                        })
                    else:
                        error_msg = response.get("error", "未知错误")
                        st.error(f"❌ 解析失败: {error_msg}")
                        st.info("💡 提示：请确保 API 服务正在运行（http://localhost:8000）")
                        st.stop()
                    
                except Exception as e:
                    st.error(f"❌ 解析失败: {str(e)}")
                    st.exception(e)
                    st.stop()
        else:
            st.stop()
        
        # 统一的结果显示逻辑（只显示解析结果）
        if 'jd' in locals():
            st.markdown("---")
            
            # 只显示解析结果，不显示评估
            st.subheader("📊 解析结果")
            
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
            
            # 提示用户进入第二步
            st.markdown("---")
            st.success("✅ JD 解析完成并已保存！")
            st.info("💡 下一步：前往'⭐ JD评估（第二步）'页面进行评估、选择分类和评估模板")

# ⭐ JD评估页面（第二步）
elif page == "⭐ JD评估（第二步）":
    st.header("⭐ JD评估与分析（第二步）")
    st.info("💡 第二步：选择已解析的JD和评估模板进行评估，获得专业的岗位分析结果")
    
    # 获取已保存的JD列表
    st.subheader("1️⃣ 选择要评估的JD")
    
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
    
    if not saved_jds:
        st.warning("⚠️ 暂无已保存的JD，请先前往'JD解析（第一步）'页面解析并保存JD")
        st.markdown("""
        **快速开始：**
        1. 前往'JD解析（第一步）'页面
        2. 输入或上传JD文件
        3. 解析并保存JD
        4. 返回此页面进行评估
        """)
    else:
        # 显示JD列表
        st.info(f"共有 {len(saved_jds)} 个已保存的JD")
        
        # 搜索和筛选
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_keyword = st.text_input("🔍 搜索JD", placeholder="输入职位标题关键词...")
        with col2:
            filter_status = st.selectbox("筛选状态", ["全部", "未评估", "已评估"])
        with col3:
            sort_by = st.selectbox("排序方式", ["最新", "最旧", "职位标题"])
        
        # 过滤JD列表
        filtered_jds = saved_jds
        if search_keyword:
            filtered_jds = [jd for jd in filtered_jds if search_keyword.lower() in jd.get('job_title', '').lower()]
        if filter_status == "未评估":
            filtered_jds = [jd for jd in filtered_jds if not jd.get('evaluation_status')]
        elif filter_status == "已评估":
            filtered_jds = [jd for jd in filtered_jds if jd.get('evaluation_status')]
        
        # 显示JD卡片
        st.markdown("---")
        
        # 检查是否有可用的JD
        if not filtered_jds:
            st.warning("⚠️ 没有符合筛选条件的JD")
            st.info("💡 请调整搜索关键词或筛选条件")
        else:
            # 单个JD评估模式
            batch_mode = st.checkbox("批量评估模式", value=False, help="选择多个JD进行批量评估")
            
            if batch_mode:
                selected_jd_ids = []
                
                for jd in filtered_jds:
                    col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                    
                    with col1:
                        is_selected = st.checkbox("", key=f"select_{jd['id']}", label_visibility="collapsed")
                        if is_selected:
                            selected_jd_ids.append(jd['id'])
                    
                    with col2:
                        st.markdown(f"**{jd['job_title']}**")
                        st.caption(f"部门: {jd.get('department', '未指定')} | 地点: {jd.get('location', '未指定')}")
                    
                    with col3:
                        if jd.get('category_level3_id'):
                            st.markdown("📍 已分类")
                        else:
                            st.markdown("⚠️ 未分类")
                    
                    with col4:
                        if jd.get('evaluation_status'):
                            st.success("✅ 已评估")
                        else:
                            st.info("⏳ 未评估")
                    
                    st.markdown("---")
                
                if selected_jd_ids:
                    st.success(f"已选择 {len(selected_jd_ids)} 个JD")
                    
                    
                    st.markdown("---")
                    st.subheader("3️⃣ 选择职位分类（批量）")
                    st.caption("为所有选中的JD选择相同的职位分类")
                    

                    # 开始批量评估
                    if st.button("🚀 开始批量评估", type="primary", use_container_width=True):
                        st.markdown("---")
                        st.subheader("📊 批量评估进度")
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        batch_results = []
                        
                        for idx, jd_id in enumerate(selected_jd_ids):
                            current_progress = idx / len(selected_jd_ids)
                            progress_bar.progress(current_progress)
                            
                            jd_info = next((jd for jd in filtered_jds if jd['id'] == jd_id), None)
                            status_text.text(f"正在评估: {jd_info['job_title']} ({idx + 1}/{len(selected_jd_ids)})")
                            
                            try:
                                # 调用评估API
                                eval_response = api_request(
                                    "POST",
                                    f"/jd/{jd_id}/evaluate",
                                    json={"model_type": batch_eval_model}
                                )
                                
                                if eval_response.get("success"):
                                    batch_results.append({
                                        "status": "success",
                                        "jd_id": jd_id,
                                        "jd_title": jd_info['job_title'],
                                        "evaluation": eval_response.get("data", {})
                                    })
                                else:
                                    batch_results.append({
                                        "status": "failed",
                                        "jd_id": jd_id,
                                        "jd_title": jd_info['job_title'],
                                        "error": eval_response.get("error", "未知错误")
                                    })
                            except Exception as e:
                                batch_results.append({
                                    "status": "failed",
                                    "jd_id": jd_id,
                                    "jd_title": jd_info['job_title'],
                                    "error": str(e)
                                })
                        
                        progress_bar.progress(1.0)
                        status_text.text("✅ 批量评估完成！")
                        
                        # 显示结果汇总
                        st.markdown("---")
                        st.subheader("📈 评估结果汇总")
                        
                        success_count = sum(1 for r in batch_results if r['status'] == 'success')
                        failed_count = len(batch_results) - success_count
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("总数", len(batch_results))
                        with col2:
                            st.metric("成功", success_count)
                        with col3:
                            st.metric("失败", failed_count)
                        
                        # 显示详细结果
                        if success_count > 0:
                            st.markdown("---")
                            st.subheader("✅ 评估成功的JD")
                            
                            # 统计分析
                            high_value_count = sum(1 for r in batch_results if r['status'] == 'success' and r['evaluation'].get('company_value') == '高价值')
                            core_position_count = sum(1 for r in batch_results if r['status'] == 'success' and r['evaluation'].get('is_core_position'))
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("高价值岗位", high_value_count, help="企业价值评级为'高价值'的岗位数量")
                            with col2:
                                st.metric("核心岗位", core_position_count, help="被判断为核心岗位的数量")
                            
                            # 详细列表
                            for result in batch_results:
                                if result['status'] == 'success':
                                    eval_data = result['evaluation']
                                    
                                    with st.expander(f"📄 {result['jd_title']} - 综合分数: {eval_data.get('overall_score', 0):.1f}"):
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            st.metric("综合质量分数", f"{eval_data.get('overall_score', 0):.1f}")
                                            st.metric("企业价值", eval_data.get('company_value', '未知'))
                                        
                                        with col2:
                                            st.metric("核心岗位", "是" if eval_data.get('is_core_position') else "否")
                                            
                                            # 查看详情按钮
                                            if st.button("📋 查看完整报告", key=f"view_{result['jd_id']}", use_container_width=True):
                                                st.session_state.view_evaluation_jd_id = result['jd_id']
                                                st.rerun()
                        
                        if failed_count > 0:
                            st.markdown("---")
                            st.subheader("❌ 评估失败的JD")
                            
                            for result in batch_results:
                                if result['status'] == 'failed':
                                    with st.expander(f"❌ {result['jd_title']}"):
                                        st.error(f"错误信息: {result['error']}")
            selected_jd = st.selectbox(
                "选择JD",
                options=filtered_jds,
                format_func=lambda x: f"{x['job_title']} - {x.get('department', '未指定')} ({x.get('created_at', '')[:10]})",
                help="选择要评估的JD"
            )
            
            if selected_jd:
                # 显示JD详情
                with st.expander("📋 查看JD详情", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**职位**: {selected_jd['job_title']}")
                    with col2:
                        st.markdown(f"**部门**: {selected_jd.get('department', '未指定')}")
                    with col3:
                        st.markdown(f"**地点**: {selected_jd.get('location', '未指定')}")
                    
                    if selected_jd.get('responsibilities'):
                        st.markdown("**职责**:")
                        for resp in selected_jd['responsibilities'][:3]:
                            st.markdown(f"- {resp}")
                
                st.markdown("---")
                
                # 评估设置
                st.subheader("2️⃣ 评估设置")
                
                # 评估模板选择
                eval_model = st.selectbox(
                    "选择评估模板",
                    [
                        ("标准评估", EvaluationModel.STANDARD.value),
                        ("美世国际职位评估法", EvaluationModel.MERCER_IPE.value),
                        ("因素比较法", EvaluationModel.FACTOR_COMPARISON.value)
                    ],
                    format_func=lambda x: x[0],
                    help="选择评估框架和标准"
                )[1]
                
                # 显示评估模板说明
                if eval_model == EvaluationModel.MERCER_IPE.value:
                    st.info("📊 美世国际职位评估法：基于影响力、沟通、创新、知识技能四个维度评估岗位价值")
                elif eval_model == EvaluationModel.FACTOR_COMPARISON.value:
                    st.info("📊 因素比较法：基于技能要求、责任程度、努力程度、工作条件等因素评估岗位")
                else:
                    st.info("📊 标准评估：评估JD的完整性、清晰度和专业性")
                
                st.markdown("---")
                
                # 职位分类选择
                st.subheader("3️⃣ 选择职位分类")
                st.caption("为JD选择合适的职位分类，分类标签将影响评估结果")
                
                # 检查JD是否已有分类
                has_category = selected_jd.get('category_level3_id') is not None
                
                if has_category:
                    st.success(f"✅ 该JD已有分类")
                    
                    # 显示当前分类
                    try:
                        cat_response = api_request("GET", f"/categories/{selected_jd['category_level3_id']}")
                        if cat_response.get("success"):
                            category = cat_response.get("data", {})
                            st.info(f"📍 当前分类: {category.get('full_path', '')}")
                    except:
                        pass
                    
                    change_category = st.checkbox("更改分类", value=False)
                else:
                    st.warning("⚠️ 该JD尚未分类，请选择职位分类")
                    change_category = True
                
                # 显示分类选择器
                show_category_selector = change_category or not has_category
                
                if show_category_selector:
                    # 企业选择
                    try:
                        companies_response = api_request("GET", "/companies")
                        companies = companies_response.get("data", []) if companies_response.get("success") else []
                    except:
                        companies = []
                    
                    if not companies:
                        st.error("⚠️ 暂无企业数据")
                        st.markdown("""
                        **请先完成以下步骤：**
                        1. 前往 '🏢 企业管理' 页面
                        2. 创建企业
                        3. 为企业创建职位分类（三层级）
                        4. 为分类添加标签
                        5. 返回此页面进行评估
                        """)
                    else:
                        selected_company = st.selectbox(
                            "选择企业",
                            options=companies,
                            format_func=lambda x: x['name']
                        )
                        
                        if selected_company:
                            # 获取分类树
                            try:
                                tree_response = api_request("GET", f"/companies/{selected_company['id']}/categories/tree")
                                if tree_response.get("success"):
                                    tree_data = tree_response.get("data", {})
                                    category_tree = tree_data.get("category_tree", [])
                                    
                                    if category_tree:
                                        # 三层级级联选择器
                                        col1, col2, col3 = st.columns(3)
                                        
                                        with col1:
                                            level1_options = category_tree
                                            selected_level1 = st.selectbox(
                                                "第一层级（大类）",
                                                options=[None] + level1_options,
                                                format_func=lambda x: "请选择..." if x is None else x['name']
                                            )
                                        
                                        with col2:
                                            if selected_level1:
                                                level2_options = selected_level1.get('children', [])
                                                selected_level2 = st.selectbox(
                                                    "第二层级（中类）",
                                                    options=[None] + level2_options,
                                                    format_func=lambda x: "请选择..." if x is None else x['name']
                                                )
                                            else:
                                                st.selectbox("第二层级（中类）", options=["请先选择第一层级"], disabled=True)
                                                selected_level2 = None
                                        
                                        with col3:
                                            if selected_level2:
                                                level3_options = selected_level2.get('children', [])
                                                selected_level3 = st.selectbox(
                                                    "第三层级（小类）",
                                                    options=[None] + level3_options,
                                                    format_func=lambda x: "请选择..." if x is None else x['name']
                                                )
                                            else:
                                                st.selectbox("第三层级（小类）", options=["请先选择第二层级"], disabled=True)
                                                selected_level3 = None
                                        
                                        # 显示分类路径
                                        if selected_level1:
                                            path_parts = [selected_level1['name']]
                                            if selected_level2:
                                                path_parts.append(selected_level2['name'])
                                            if selected_level3:
                                                path_parts.append(selected_level3['name'])
                                            
                                            st.info(f"📍 分类路径: {' → '.join(path_parts)}")
                                        
                                        # 显示第三层级的标签
                                        if selected_level3:
                                            st.markdown("---")
                                            st.markdown("#### 🏷️ 分类标签预览")
                                            st.caption("以下标签将影响该岗位的评估结果")
                                            
                                            try:
                                                tags_response = api_request("GET", f"/categories/{selected_level3['id']}/tags")
                                                if tags_response.get("success"):
                                                    tags = tags_response.get("data", [])
                                                    
                                                    if tags:
                                                        # 按标签类型分组显示
                                                        tag_types = {}
                                                        for tag in tags:
                                                            tag_type = tag.get('tag_type', '其他')
                                                            if tag_type not in tag_types:
                                                                tag_types[tag_type] = []
                                                            tag_types[tag_type].append(tag)
                                                        
                                                        # 显示标签统计
                                                        st.info(f"📊 共有 {len(tags)} 个标签，分为 {len(tag_types)} 个类型")
                                                        
                                                        # 按类型展示标签
                                                        for tag_type, type_tags in tag_types.items():
                                                            with st.expander(f"📁 {tag_type} ({len(type_tags)} 个标签)", expanded=True):
                                                                for tag in type_tags:
                                                                    col1, col2 = st.columns([1, 3])
                                                                    with col1:
                                                                        st.markdown(f"**🏷️ {tag.get('name', '未命名')}**")
                                                                    with col2:
                                                                        st.caption(tag.get('description', '无描述'))
                                                                    st.markdown("---")
                                                    else:
                                                        st.info("💡 该分类暂无标签，评估将仅基于JD内容和评估模板")
                                            except Exception as e:
                                                st.warning(f"⚠️ 无法获取标签信息: {str(e)}")
                                    else:
                                        st.warning("⚠️ 该企业暂无职位分类")
                                        st.markdown("""
                                        **请先完成以下步骤：**
                                        1. 前往 '🏢 企业管理' 页面
                                        2. 选择该企业
                                        3. 创建三层级职位分类
                                        4. 返回此页面进行评估
                                        """)
                            except Exception as e:
                                st.error(f"❌ 无法获取分类树: {str(e)}")
                                st.info("💡 请确保API服务正常运行")
                
                st.markdown("---")
                
                # 检查是否可以提交评估
                can_evaluate = False
                selected_category_id = None
                
                if has_category and not change_category:
                    # 使用现有分类
                    can_evaluate = True
                    selected_category_id = selected_jd.get('category_level3_id')
                elif 'selected_level3' in locals() and selected_level3:
                    # 选择了新分类
                    can_evaluate = True
                    selected_category_id = selected_level3['id']
                
                # 提交评估
                if not can_evaluate:
                    st.warning("⚠️ 请先选择职位分类后再提交评估")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    evaluate_button = st.button(
                        "⭐ 提交评估", 
                        type="primary", 
                        use_container_width=True,
                        disabled=not can_evaluate
                    )
                
                if evaluate_button and can_evaluate:
                    with st.spinner("🤖 AI正在评估中..."):
                        try:
                            # 准备评估请求
                            eval_payload = {
                                "model_type": eval_model,
                                "category_level3_id": selected_category_id
                            }
                            
                            # 调用评估API
                            eval_response = api_request(
                                "POST",
                                f"/jd/{selected_jd['id']}/evaluate",
                                json=eval_payload
                            )
                            
                            if eval_response.get("success"):
                                st.success("✅ 评估完成！")
                                
                                # 显示评估结果
                                eval_data = eval_response.get("data", {})
                                
                                st.markdown("---")
                                st.subheader("📊 评估结果")
                                
                                # 综合评估结果
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("综合质量分数", f"{eval_data.get('overall_score', 0):.1f}")
                                
                                with col2:
                                    company_value = eval_data.get('company_value', '未知')
                                    if company_value == "高价值":
                                        st.success(f"🏢 企业价值: **{company_value}**")
                                    elif company_value == "中价值":
                                        st.info(f"🏢 企业价值: **{company_value}**")
                                    else:
                                        st.warning(f"🏢 企业价值: **{company_value}**")
                                
                                with col3:
                                    is_core = eval_data.get('is_core_position', False)
                                    if is_core:
                                        st.success("🎯 **核心岗位**")
                                    else:
                                        st.info("🎯 **非核心岗位**")
                                
                                # 显示选中的分类信息
                                if 'selected_level3' in locals() and selected_level3:
                                    st.markdown("---")
                                    st.markdown("### 📍 职位分类")
                                    
                                    # 显示分类路径
                                    if 'selected_level1' in locals() and 'selected_level2' in locals():
                                        path_parts = [selected_level1['name'], selected_level2['name'], selected_level3['name']]
                                        st.info(f"分类路径: {' → '.join(path_parts)}")
                                    
                                    # 显示应用的标签
                                    try:
                                        tags_response = api_request("GET", f"/categories/{selected_level3['id']}/tags")
                                        if tags_response.get("success"):
                                            tags = tags_response.get("data", [])
                                            if tags:
                                                st.markdown("#### 🏷️ 应用的分类标签")
                                                st.caption(f"共 {len(tags)} 个标签影响了评估结果")
                                                
                                                # 按类型分组显示
                                                tag_types = {}
                                                for tag in tags:
                                                    tag_type = tag.get('tag_type', '其他')
                                                    if tag_type not in tag_types:
                                                        tag_types[tag_type] = []
                                                    tag_types[tag_type].append(tag)
                                                
                                                for tag_type, type_tags in tag_types.items():
                                                    with st.expander(f"📁 {tag_type} ({len(type_tags)} 个)", expanded=False):
                                                        for tag in type_tags:
                                                            st.markdown(f"**🏷️ {tag.get('name')}**: {tag.get('description', '无描述')}")
                                    except:
                                        pass
                                
                                # 三个维度贡献度
                                if eval_data.get('dimension_contributions'):
                                    st.markdown("---")
                                    st.markdown("### 📈 评估维度贡献度")
                                    st.caption("展示JD内容、评估模板和分类标签对最终评估结果的贡献比例")
                                    
                                    contrib = eval_data['dimension_contributions']
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("📝 JD内容", f"{contrib.get('jd_content', 0):.1f}%")
                                    with col2:
                                        st.metric("📋 评估模板", f"{contrib.get('evaluation_template', 0):.1f}%")
                                    with col3:
                                        st.metric("🏷️ 分类标签", f"{contrib.get('category_tags', 0):.1f}%")
                                
                                # 查看完整报告
                                st.markdown("---")
                                if st.button("📋 查看完整评估报告", use_container_width=True):
                                    st.session_state.view_evaluation_jd_id = selected_jd['id']
                                    st.rerun()
                            
                            else:
                                st.error(f"❌ 评估失败: {eval_response.get('error', '未知错误')}")
                        
                        except Exception as e:
                            st.error(f"❌ 评估失败: {str(e)}")

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

# 🏢 企业管理页面
elif page == "🏢 企业管理":
    st.header("🏢 企业管理")
    
    st.info("💡 管理企业信息，每个企业拥有独立的职位分类体系")
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 企业列表")
        
        # 获取企业列表
        try:
            response = api_request("GET", "/companies")
            
            if response.get("success"):
                companies = response.get("data", [])
                
                if companies:
                    st.info(f"共有 {len(companies)} 家企业")
                    
                    # 显示企业卡片
                    for company in companies:
                        with st.expander(f"🏢 {company.get('name', '未命名企业')}", expanded=False):
                            col_a, col_b = st.columns([3, 1])
                            
                            with col_a:
                                st.markdown(f"**企业ID**: `{company.get('id', 'N/A')}`")
                                st.markdown(f"**创建时间**: {company.get('created_at', 'N/A')[:19]}")
                                st.markdown(f"**更新时间**: {company.get('updated_at', 'N/A')[:19]}")
                                
                                # 获取企业统计信息
                                try:
                                    cat_response = api_request("GET", f"/companies/{company['id']}/categories")
                                    if cat_response.get("success"):
                                        categories_count = cat_response.get("total", 0)
                                        
                                        # 显示统计信息
                                        st.markdown("---")
                                        st.markdown("**统计信息**")
                                        
                                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                                        with metric_col1:
                                            st.metric("职位分类", f"{categories_count}")
                                        with metric_col2:
                                            st.metric("JD数量", "0")  # TODO: 实现JD统计
                                        with metric_col3:
                                            st.metric("标签数量", "0")  # TODO: 实现标签统计
                                except Exception as e:
                                    st.warning(f"无法获取统计信息: {str(e)}")
                            
                            with col_b:
                                # 查看详情按钮
                                company_id = company.get('id', '')
                                if company_id and st.button("📋 查看详情", key=f"view_{company_id}", use_container_width=True):
                                    st.session_state.view_company_id = company_id
                                    st.rerun()
                                
                                # 编辑按钮
                                if company_id and st.button("✏️ 编辑", key=f"edit_{company_id}", use_container_width=True):
                                    st.session_state.edit_company_id = company_id
                                    st.session_state.edit_company_data = company
                                    st.rerun()
                                
                                # 删除按钮
                                if company_id and st.button("🗑️ 删除", key=f"del_{company_id}", use_container_width=True):
                                    st.session_state.delete_company_id = company_id
                                    st.session_state.delete_company_name = company.get('name', '未命名企业')
                                    st.rerun()
                    
                    # 显示企业详情
                    if "view_company_id" in st.session_state:
                        st.markdown("---")
                        st.subheader("📋 企业详情")
                        
                        company_id = st.session_state.view_company_id
                        
                        # 获取企业信息
                        detail_response = api_request("GET", f"/companies/{company_id}")
                        if detail_response.get("success"):
                            company_detail = detail_response.get("data", {})
                            
                            st.markdown(f"### 🏢 {company_detail['name']}")
                            st.markdown(f"**企业ID**: `{company_detail['id']}`")
                            st.markdown(f"**创建时间**: {company_detail['created_at'][:19]}")
                            st.markdown(f"**更新时间**: {company_detail['updated_at'][:19]}")
                            
                            # 获取企业的分类树
                            st.markdown("---")
                            st.markdown("#### 📊 职位分类体系")
                            
                            tree_response = api_request("GET", f"/companies/{company_id}/categories/tree")
                            if tree_response.get("success"):
                                tree_data = tree_response.get("data", {})
                                category_tree = tree_data.get("category_tree", [])
                                
                                if category_tree:
                                    # 递归显示分类树
                                    def display_company_tree(nodes: List[Dict], level: int = 1):
                                        for node in nodes:
                                            indent = "　" * (level - 1)
                                            icon = "📁" if level == 1 else ("📂" if level == 2 else "📄")
                                            
                                            st.markdown(f"{indent}{icon} **{node.get('name', '未命名')}** (L{level})")
                                            
                                            if node.get('description'):
                                                st.markdown(f"{indent}　　_{node['description']}_")
                                            
                                            # 显示样本JD（仅第三层级）
                                            if level == 3 and node.get('sample_jd_ids'):
                                                st.markdown(f"{indent}　　样本JD: {len(node['sample_jd_ids'])} 个")
                                            
                                            # 递归显示子分类
                                            if node.get('children'):
                                                display_company_tree(node['children'], level + 1)
                                    
                                    display_company_tree(category_tree)
                                else:
                                    st.info("该企业暂无职位分类")
                            else:
                                st.warning("无法获取分类树")
                            
                            # 关闭按钮
                            if st.button("❌ 关闭详情", use_container_width=True):
                                del st.session_state.view_company_id
                                st.rerun()
                    
                    # 编辑企业
                    if "edit_company_id" in st.session_state:
                        st.markdown("---")
                        st.subheader("✏️ 编辑企业")
                        
                        company_data = st.session_state.edit_company_data
                        
                        with st.form("edit_company_form"):
                            new_name = st.text_input("企业名称*", value=company_data['name'])
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                update_btn = st.form_submit_button("💾 保存", use_container_width=True, type="primary")
                            with col_b:
                                cancel_btn = st.form_submit_button("❌ 取消", use_container_width=True)
                            
                            if update_btn:
                                if not new_name:
                                    st.error("❌ 请输入企业名称")
                                else:
                                    update_response = api_request(
                                        "PUT",
                                        f"/companies/{company_data['id']}",
                                        json={"name": new_name}
                                    )
                                    
                                    if update_response.get("success"):
                                        st.success("✅ 企业更新成功！")
                                        del st.session_state.edit_company_id
                                        del st.session_state.edit_company_data
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {update_response.get('detail', '更新失败')}")
                            
                            if cancel_btn:
                                del st.session_state.edit_company_id
                                del st.session_state.edit_company_data
                                st.rerun()
                    
                    # 删除企业确认
                    if "delete_company_id" in st.session_state:
                        st.markdown("---")
                        st.subheader("⚠️ 删除企业确认")
                        
                        company_id = st.session_state.delete_company_id
                        company_name = st.session_state.delete_company_name
                        
                        # 先调用不带confirm的删除，获取警告信息
                        check_response = api_request("DELETE", f"/companies/{company_id}?confirm=false")
                        
                        if check_response.get("confirm_required"):
                            warning_msg = check_response.get("warning", "")
                            categories_count = check_response.get("data", {}).get("categories_count", 0)
                            
                            st.warning(f"⚠️ {warning_msg}")
                            st.error(f"🚨 您即将删除企业 **{company_name}**，这将同时删除该企业下的 **{categories_count}** 个职位分类及其所有标签！")
                            st.markdown("**此操作不可撤销，请谨慎操作！**")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("🗑️ 确认删除", use_container_width=True, type="primary"):
                                    # 执行删除
                                    delete_response = api_request("DELETE", f"/companies/{company_id}?confirm=true")
                                    
                                    if delete_response.get("success"):
                                        st.success(f"✅ {delete_response.get('message', '删除成功')}")
                                        del st.session_state.delete_company_id
                                        del st.session_state.delete_company_name
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {delete_response.get('detail', '删除失败')}")
                            
                            with col_b:
                                if st.button("❌ 取消", use_container_width=True):
                                    del st.session_state.delete_company_id
                                    del st.session_state.delete_company_name
                                    st.rerun()
                        else:
                            # 直接删除（没有关联数据）
                            delete_response = api_request("DELETE", f"/companies/{company_id}?confirm=true")
                            
                            if delete_response.get("success"):
                                st.success("✅ 企业删除成功！")
                                del st.session_state.delete_company_id
                                del st.session_state.delete_company_name
                                st.rerun()
                            else:
                                st.error(f"❌ {delete_response.get('detail', '删除失败')}")
                
                else:
                    st.info("📝 暂无企业数据，请从右侧创建第一家企业")
                    st.markdown("""
                    **快速开始：**
                    1. 在右侧表单中输入企业名称
                    2. 点击"创建企业"按钮
                    3. 为企业创建职位分类体系
                    """)
            else:
                error_msg = response.get('error', '未知错误')
                st.warning(f"⚠️ 无法获取企业数据: {error_msg}")
                st.info("💡 请检查 API 服务是否正常运行")
        except Exception as e:
            st.error(f"❌ 获取企业列表时发生错误: {str(e)}")
            st.info("💡 请检查 API 服务是否正常运行（http://localhost:8000）")
    
    with col2:
        st.subheader("➕ 创建新企业")
        
        with st.form("create_company_form"):
            company_name = st.text_input(
                "企业名称*",
                placeholder="例如：科技有限公司",
                help="输入企业的完整名称"
            )
            
            st.markdown("---")
            st.markdown("**说明**")
            st.info("""
            创建企业后，您可以：
            - 为企业建立独立的职位分类体系
            - 管理企业的岗位JD
            - 查看企业的统计信息
            """)
            
            submitted = st.form_submit_button("✅ 创建企业", use_container_width=True, type="primary")
            
            if submitted:
                if not company_name:
                    st.error("❌ 请输入企业名称")
                else:
                    create_response = api_request(
                        "POST",
                        "/companies",
                        json={"name": company_name}
                    )
                    
                    if create_response.get("success"):
                        st.success("✅ 企业创建成功！")
                        created_company = create_response.get("data", {})
                        st.markdown(f"**企业ID**: `{created_company.get('id')}`")
                        st.markdown(f"**企业名称**: {created_company.get('name')}")
                        st.info("💡 您现在可以在左侧查看企业详情，或前往'职位分类管理'页面为企业创建分类体系")
                        st.rerun()
                    else:
                        st.error(f"❌ {create_response.get('detail', '创建失败')}")
        
        # 使用说明
        st.markdown("---")
        st.markdown("### 💡 使用说明")
        with st.expander("查看详细说明"):
            st.markdown("""
            ### 企业管理功能说明
            
            **功能概述：**
            - 创建和管理企业信息
            - 每个企业拥有独立的职位分类体系
            - 查看企业统计信息（分类数量、JD数量等）
            
            **操作步骤：**
            1. **创建企业**：在右侧表单输入企业名称并提交
            2. **查看详情**：点击企业卡片中的"查看详情"按钮
            3. **编辑企业**：点击"编辑"按钮修改企业名称
            4. **删除企业**：点击"删除"按钮（需确认）
            
            **注意事项：**
            - 删除企业将同时删除该企业下的所有职位分类和标签
            - 删除操作不可撤销，请谨慎操作
            - 建议先查看企业详情，了解关联数据后再删除
            
            **下一步：**
            - 创建企业后，前往"职位分类管理"页面
            - 为企业建立职位分类体系（最多3层级）
            - 为第三层级分类添加标签和样本JD
            """)

# 🗂️ 职位分类管理页面
elif page == "🗂️ 职位分类管理":
    st.header("🗂️ 职位分类管理")
    
    st.info("💡 管理职位分类体系（最多3层级），为第三层级分类添加样本JD和标签以提高自动分类准确性")
    
    # 企业选择器
    st.markdown("### 🏢 选择企业")
    
    # 获取所有企业
    companies_response = api_request("GET", "/companies")
    
    if companies_response.get("success"):
        companies = companies_response.get("data", [])
        
        if companies:
            # 创建企业选择下拉框
            company_options = {f"{c['name']} ({c['id']})": c['id'] for c in companies}
            
            selected_company_display = st.selectbox(
                "选择要管理的企业",
                list(company_options.keys()),
                key="selected_company_for_categories"
            )
            
            selected_company_id = company_options[selected_company_display]
            
            # 显示选中的企业信息
            selected_company = next((c for c in companies if c['id'] == selected_company_id), None)
            if selected_company:
                col_info1, col_info2 = st.columns([3, 1])
                with col_info1:
                    st.success(f"✅ 当前管理企业: **{selected_company['name']}**")
                with col_info2:
                    st.info(f"ID: `{selected_company['id']}`")
            
            st.markdown("---")
        else:
            st.warning("⚠️ 暂无企业数据")
            st.info("💡 请先前往'企业管理'页面创建企业")
            st.stop()
    else:
        st.error("❌ 无法获取企业列表")
        st.info("💡 请检查 API 服务是否正常运行")
        st.stop()
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 分类树")
        
        # 显示成功消息（如果有）
        if 'tag_success_message' in st.session_state:
            st.success(st.session_state.tag_success_message)
            del st.session_state.tag_success_message
        
        # 获取该企业的分类树
        try:
            response = api_request("GET", f"/companies/{selected_company_id}/categories/tree")
            
            if response.get("success"):
                data = response.get("data", {})
                # API返回的数据结构是 {"company": {...}, "category_tree": [...]}
                tree_data = data.get("category_tree", []) if isinstance(data, dict) else []
                
                if tree_data:
                    # 扁平化显示分类树（避免expander嵌套）
                    def flatten_tree(nodes: List[Dict], level: int = 1, result: List = None):
                        """将树形结构扁平化为列表"""
                        if result is None:
                            result = []
                        
                        for node in nodes:
                            # 添加当前节点
                            result.append({
                                'node': node,
                                'level': level
                            })
                            
                            # 递归处理子节点
                            if node.get('children'):
                                flatten_tree(node['children'], level + 1, result)
                        
                        return result
                    
                    # 扁平化分类树
                    flat_categories = flatten_tree(tree_data)
                    
                    # 去重：确保每个分类ID只出现一次
                    seen_ids = set()
                    unique_categories = []
                    for item in flat_categories:
                        if item['node']['id'] not in seen_ids:
                            seen_ids.add(item['node']['id'])
                            unique_categories.append(item)
                    
                    # 标记是否已经显示了添加标签表单
                    form_displayed = False
                    
                    # 显示扁平化的分类列表
                    for item in unique_categories:
                        node = item['node']
                        level = item['level']
                        
                        indent = "　" * (level - 1)
                        icon = "📁" if level == 1 else ("📂" if level == 2 else "📄")
                        
                        # 获取标签（仅第三层级）
                        tags = []
                        if level == 3:
                            try:
                                tags_response = api_request("GET", f"/categories/{node['id']}/tags")
                                if tags_response.get("success"):
                                    tags = tags_response.get("data", [])
                            except:
                                pass
                        
                        # 显示标签信息
                        tag_info = ""
                        if level == 3 and tags:
                            tag_names = [t['name'] for t in tags[:2]]  # 最多显示2个标签名
                            tag_info = f" | 🏷️ {', '.join(tag_names)}"
                            if len(tags) > 2:
                                tag_info += f" +{len(tags)-2}"
                        
                        # 使用expander实现折叠（不嵌套）
                        node_name = node.get('name', '未命名')
                        node_id = node.get('id', '')
                        
                        with st.expander(f"{indent}{icon} {node_name} (L{level}){tag_info}", expanded=False):
                            col_a, col_b = st.columns([3, 1])
                            
                            with col_a:
                                st.markdown(f"**ID**: `{node_id}`")
                                if node.get('description'):
                                    st.markdown(f"**描述**: {node['description']}")
                                
                                # 显示样本JD（仅第三层级）
                                if level == 3 and node.get('sample_jd_ids'):
                                    st.markdown(f"**样本JD**: {len(node['sample_jd_ids'])} 个")
                                    for jd_id in node['sample_jd_ids']:
                                        st.markdown(f"- `{jd_id}`")
                                
                                # 显示标签列表（仅第三层级）
                                if level == 3 and tags:
                                    st.markdown("---")
                                    st.markdown(f"**标签** ({len(tags)})")
                                    for tag in tags:
                                        st.markdown(f"🏷️ **{tag.get('name', '未命名')}** ({tag.get('tag_type', '未分类')})")
                                        if tag.get('description'):
                                            st.caption(tag['description'])
                                elif level == 3:
                                    st.markdown("---")
                                    st.info("该分类暂无标签")
                            
                            with col_b:
                                if node_id and st.button("✏️ 编辑", key=f"edit_{node_id}", use_container_width=True):
                                    st.session_state.edit_category_id = node_id
                                    st.session_state.edit_category_data = node
                                    st.rerun()
                                
                                # 第三层级添加"添加标签"按钮
                                if level == 3 and node_id:
                                    if st.button("🏷️ 添加标签", key=f"add_tag_{node_id}", use_container_width=True):
                                        st.session_state.add_tag_category_id = node_id
                                        st.rerun()
                                
                                if node_id and st.button("🗑️ 删除", key=f"del_{node_id}", use_container_width=True):
                                    del_response = api_request("DELETE", f"/categories/{node_id}")
                                    if del_response.get("success"):
                                        st.success("✅ 删除成功")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {del_response.get('error', '删除失败')}")
                            
                            # 添加标签表单（点击"添加标签"按钮后显示）
                            # 只在当前分类被选中时显示表单，并且确保只显示一次
                            if level == 3 and node_id and st.session_state.get('add_tag_category_id') == node_id and not form_displayed:
                                form_displayed = True  # 标记表单已显示
                                st.markdown("---")
                                st.markdown("**➕ 添加新标签**")
                                # 使用分类ID作为唯一key
                                with st.form(key=f"add_tag_form_{node_id}", clear_on_submit=True):
                                    tag_name = st.text_input(
                                        "标签名称*",
                                        placeholder="例如：高战略重要性"
                                    )
                                    
                                    tag_type = st.selectbox(
                                        "标签类型*",
                                        [
                                            "战略重要性",
                                            "业务价值",
                                            "技能稀缺性",
                                            "市场竞争度",
                                            "发展潜力",
                                            "风险等级"
                                        ]
                                    )
                                    
                                    tag_description = st.text_area(
                                        "标签描述*",
                                        placeholder="描述该标签的含义和对岗位评估的影响...",
                                        help="详细说明该标签如何影响岗位评估"
                                    )
                                    
                                    form_col1, form_col2 = st.columns(2)
                                    with form_col1:
                                        add_tag_btn = st.form_submit_button(
                                            "✅ 添加",
                                            use_container_width=True,
                                            type="primary"
                                        )
                                    with form_col2:
                                        cancel_btn = st.form_submit_button(
                                            "❌ 取消",
                                            use_container_width=True
                                        )
                                    
                                    if add_tag_btn:
                                        if not tag_name or not tag_description:
                                            st.error("❌ 请填写所有必填字段")
                                        else:
                                            add_tag_data = {
                                                "name": tag_name,
                                                "tag_type": tag_type,
                                                "description": tag_description
                                            }
                                            
                                            add_tag_response = api_request(
                                                "POST",
                                                f"/categories/{node_id}/tags",
                                                json=add_tag_data
                                            )
                                            
                                            if add_tag_response.get("success"):
                                                # 设置成功消息
                                                st.session_state.tag_success_message = "✅ 标签添加成功！"
                                                # 清除表单状态（必须在rerun之前）
                                                st.session_state.pop('add_tag_category_id', None)
                                                # 强制重新加载页面
                                                st.rerun()
                                            else:
                                                st.error(f"❌ {add_tag_response.get('detail', '添加失败')}")
                                    
                                    if cancel_btn:
                                        st.session_state.pop('add_tag_category_id', None)
                                        st.rerun()
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
        
        # 先在表单外选择层级，这样可以动态显示父级选择
        cat_level = st.selectbox(
            "层级*", 
            [1, 2, 3], 
            format_func=lambda x: f"第{x}层级",
            key="create_cat_level"
        )
        
        # 根据层级动态显示父级选择（在表单外）
        parent_id = None
        parent_options = []
        if cat_level > 1:
            st.info(f"💡 第{cat_level}层级分类需要选择第{cat_level-1}层级作为父级")
            parent_response = api_request("GET", f"/companies/{selected_company_id}/categories?level={cat_level - 1}")
            if parent_response.get("success"):
                parent_options = parent_response.get("data", [])
                if parent_options:
                    # 创建更清晰的选项显示：名称 (ID)
                    parent_dict = {f"{p['name']} ({p['id']})": p['id'] for p in parent_options}
                    parent_display = st.selectbox(
                        f"选择父级分类（第{cat_level-1}层级）*",
                        list(parent_dict.keys()),
                        help=f"选择一个第{cat_level-1}层级分类作为父级",
                        key="create_parent_select"
                    )
                    parent_id = parent_dict[parent_display]
                else:
                    st.warning(f"⚠️ 请先创建第{cat_level-1}层级分类")
                    st.info(f"💡 提示：先将层级改为'第{cat_level-1}层级'，创建父级分类后，再创建第{cat_level}层级")
        
        st.markdown("---")
        
        # 表单部分
        with st.form("create_category_form"):
            cat_name = st.text_input("分类名称*", placeholder="例如：技术类")
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
                        "company_id": selected_company_id,
                        "name": cat_name,
                        "level": cat_level,
                        "parent_id": parent_id,
                        "description": cat_desc if cat_desc else None,
                        "sample_jd_ids": sample_jd_ids
                    }
                    
                    response = api_request("POST", f"/companies/{selected_company_id}/categories", json=create_data)
                    
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
        
        # 编辑标签
        if "edit_tag_id" in st.session_state:
            st.markdown("---")
            st.subheader("✏️ 编辑标签")
            
            tag_data = st.session_state.edit_tag_data
            category_id = st.session_state.edit_tag_category_id
            
            with st.form("edit_tag_form"):
                st.info(f"正在编辑标签: {tag_data['name']}")
                
                new_tag_name = st.text_input("标签名称*", value=tag_data['name'])
                
                new_tag_type = st.selectbox(
                    "标签类型*",
                    [
                        "战略重要性",
                        "业务价值",
                        "技能稀缺性",
                        "市场竞争度",
                        "发展潜力",
                        "风险等级"
                    ],
                    index=[
                        "战略重要性",
                        "业务价值",
                        "技能稀缺性",
                        "市场竞争度",
                        "发展潜力",
                        "风险等级"
                    ].index(tag_data['tag_type']) if tag_data['tag_type'] in [
                        "战略重要性",
                        "业务价值",
                        "技能稀缺性",
                        "市场竞争度",
                        "发展潜力",
                        "风险等级"
                    ] else 0
                )
                
                new_tag_description = st.text_area(
                    "标签描述*",
                    value=tag_data.get('description', ''),
                    help="详细说明该标签如何影响岗位评估"
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    update_tag_btn = st.form_submit_button("💾 保存", use_container_width=True, type="primary")
                with col_b:
                    cancel_tag_btn = st.form_submit_button("❌ 取消", use_container_width=True)
                
                if update_tag_btn:
                    if not new_tag_name or not new_tag_description:
                        st.error("❌ 请填写所有必填字段")
                    else:
                        update_tag_data = {
                            "name": new_tag_name,
                            "tag_type": new_tag_type,
                            "description": new_tag_description
                        }
                        
                        update_tag_response = api_request(
                            "PUT",
                            f"/tags/{tag_data['id']}",
                            json=update_tag_data
                        )
                        
                        if update_tag_response.get("success"):
                            st.success("✅ 标签更新成功！")
                            del st.session_state.edit_tag_id
                            del st.session_state.edit_tag_data
                            del st.session_state.edit_tag_category_id
                            st.rerun()
                        else:
                            st.error(f"❌ {update_tag_response.get('detail', '更新失败')}")
                
                if cancel_tag_btn:
                    del st.session_state.edit_tag_id
                    del st.session_state.edit_tag_data
                    del st.session_state.edit_tag_category_id
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
                                st.markdown(f"**问卷ID**: `{quest_data.get('id', 'N/A')}`")
                                st.markdown(f"**标题**: {quest_data.get('title', '未命名')}")
                                st.markdown(f"**描述**: {quest_data.get('description', '无描述')}")
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
                            st.markdown(f"**JD ID**: `{quest.get('jd_id', 'N/A')}`")
                            st.markdown(f"**描述**: {quest.get('description', '无描述')}")
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
