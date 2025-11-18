"""问卷填写页面 - 独立页面供候选人填写"""

import streamlit as st
import requests
import os
from typing import Dict, Any

# API基础URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# 页面配置
st.set_page_config(
    page_title="问卷填写",
    page_icon="📝",
    layout="wide"
)

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


# 获取问卷ID（从URL参数）
query_params = st.query_params
questionnaire_id = query_params.get("id", None)

if not questionnaire_id:
    st.error("❌ 缺少问卷ID参数")
    st.info("💡 请使用正确的问卷链接访问")
    st.stop()

# 获取问卷详情
response = api_request("GET", f"/questionnaire/{questionnaire_id}")

if not response.get("success"):
    st.error(f"❌ 问卷不存在或已失效")
    st.stop()

questionnaire = response.get("data", {})

# 显示问卷标题和描述
st.title(f"📝 {questionnaire['title']}")
st.markdown(questionnaire['description'])
st.markdown("---")

# 问卷填写表单
with st.form("questionnaire_form"):
    st.subheader("请回答以下问题")
    
    answers = {}
    
    for idx, question in enumerate(questionnaire['questions'], 1):
        st.markdown(f"### {idx}. {question['question_text']}")
        st.caption(f"维度: {question['dimension']}")
        
        q_id = question['id']
        q_type = question['question_type']
        
        if q_type == "single_choice":
            # 单选题
            answer = st.radio(
                "请选择一个答案",
                options=question['options'],
                key=f"q_{q_id}",
                label_visibility="collapsed"
            )
            answers[q_id] = answer
        
        elif q_type == "multiple_choice":
            # 多选题
            answer = st.multiselect(
                "请选择一个或多个答案",
                options=question['options'],
                key=f"q_{q_id}",
                label_visibility="collapsed"
            )
            answers[q_id] = answer
        
        elif q_type == "scale":
            # 量表题
            answer = st.slider(
                "请评分（1-5分）",
                min_value=1,
                max_value=5,
                value=3,
                key=f"q_{q_id}",
                label_visibility="collapsed"
            )
            answers[q_id] = answer
        
        elif q_type == "open_ended":
            # 开放题
            answer = st.text_area(
                "请输入您的答案",
                key=f"q_{q_id}",
                height=100,
                label_visibility="collapsed"
            )
            answers[q_id] = answer
        
        st.markdown("---")
    
    # 填写人信息
    st.subheader("个人信息（可选）")
    respondent_name = st.text_input("姓名", placeholder="可选填写")
    
    # 提交按钮
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submitted = st.form_submit_button("✅ 提交问卷", type="primary", use_container_width=True)

# 处理提交
if submitted:
    # 验证所有问题都已回答
    all_answered = True
    for question in questionnaire['questions']:
        if question['id'] not in answers or not answers[question['id']]:
            all_answered = False
            break
    
    if not all_answered:
        st.error("❌ 请回答所有问题后再提交")
    else:
        with st.spinner("📤 正在提交问卷..."):
            submit_data = {
                "respondent_name": respondent_name if respondent_name else None,
                "answers": answers
            }
            
            submit_response = api_request(
                "POST",
                f"/questionnaire/{questionnaire_id}/submit",
                json=submit_data
            )
            
            if submit_response.get("success"):
                st.success("✅ 问卷提交成功！")
                
                # 显示匹配结果
                result_data = submit_response.get("data", {})
                match_result = result_data.get("match_result", {})
                
                if match_result:
                    st.markdown("---")
                    st.subheader("🎯 您的匹配结果")
                    
                    # 综合匹配度
                    score = match_result['overall_score']
                    st.metric("综合匹配度", f"{score:.1f}分")
                    
                    # 进度条
                    st.progress(score / 100)
                    
                    # 匹配等级
                    if score >= 90:
                        st.success("🌟 优秀匹配 - 您非常适合这个岗位！")
                    elif score >= 80:
                        st.info("👍 良好匹配 - 您基本符合岗位要求")
                    elif score >= 70:
                        st.warning("⚠️ 中等匹配 - 您部分符合岗位要求")
                    else:
                        st.error("❌ 匹配度较低 - 建议考虑其他岗位")
                    
                    # 维度得分
                    if match_result.get('dimension_scores'):
                        st.markdown("#### 📊 各维度得分")
                        
                        cols = st.columns(len(match_result['dimension_scores']))
                        for idx, (dim, dim_score) in enumerate(match_result['dimension_scores'].items()):
                            with cols[idx]:
                                st.metric(dim, f"{dim_score:.1f}")
                    
                    # 优势和差距
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### ✅ 您的优势")
                        if match_result.get('strengths'):
                            for strength in match_result['strengths']:
                                st.success(f"✓ {strength}")
                        else:
                            st.info("暂无优势分析")
                    
                    with col2:
                        st.markdown("#### ⚠️ 需要提升的方面")
                        if match_result.get('gaps'):
                            for gap in match_result['gaps']:
                                st.warning(f"✗ {gap}")
                        else:
                            st.info("暂无差距分析")
                    
                    # 建议
                    if match_result.get('recommendations'):
                        st.markdown("#### 💡 发展建议")
                        for rec in match_result['recommendations']:
                            st.info(f"→ {rec}")
                    
                    st.markdown("---")
                    st.markdown("感谢您的参与！我们会尽快与您联系。")
            else:
                st.error(f"❌ 提交失败: {submit_response.get('detail', '未知错误')}")

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>岗位JD分析器 | Powered by AI</div>",
    unsafe_allow_html=True
)
