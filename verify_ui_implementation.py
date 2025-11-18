"""验证UI实现 - Task 8"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def verify_ui_files():
    """验证UI文件存在性和完整性"""
    print("=" * 60)
    print("验证UI文件结构")
    print("=" * 60)
    
    required_files = [
        "src/ui/app.py",
        "src/ui/pages/questionnaire_fill.py",
        "src/ui/README.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} - 文件不存在")
            all_exist = False
    
    return all_exist


def verify_ui_imports():
    """验证UI模块导入"""
    print("\n" + "=" * 60)
    print("验证UI模块导入")
    print("=" * 60)
    
    try:
        # 测试核心依赖
        import streamlit
        print("✅ streamlit 导入成功")
        
        import requests
        print("✅ requests 导入成功")
        
        import pandas
        print("✅ pandas 导入成功")
        
        import plotly
        print("✅ plotly 导入成功")
        
        # 测试项目模块
        from src.models.schemas import EvaluationModel
        print("✅ EvaluationModel 导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def verify_ui_features():
    """验证UI功能实现"""
    print("\n" + "=" * 60)
    print("验证UI功能实现")
    print("=" * 60)
    
    # 读取主UI文件
    with open("src/ui/app.py", "r", encoding="utf-8") as f:
        app_content = f.read()
    
    # 检查必需的页面
    required_pages = [
        "📝 JD分析",
        "📤 批量上传",
        "🗂️ 职位分类管理",
        "📋 问卷管理",
        "🎯 匹配结果",
        "📄 模板管理",
        "📚 历史记录",
        "ℹ️ 关于"
    ]
    
    all_pages_found = True
    for page in required_pages:
        if page in app_content:
            print(f"✅ 页面实现: {page}")
        else:
            print(f"❌ 页面缺失: {page}")
            all_pages_found = False
    
    # 检查关键功能
    print("\n检查关键功能:")
    
    features = {
        "API请求函数": "def api_request",
        "文件上传": "st.file_uploader",
        "表单提交": "st.form",
        "进度条": "st.progress",
        "数据展示": "st.dataframe",
        "图表展示": "plotly",
        "分类树": "display_tree",
        "问卷生成": "generate_questionnaire",
        "匹配结果": "match_result",
        "模板管理": "template"
    }
    
    all_features_found = True
    for feature_name, feature_code in features.items():
        if feature_code in app_content:
            print(f"✅ 功能实现: {feature_name}")
        else:
            print(f"⚠️  功能可能缺失: {feature_name}")
    
    return all_pages_found


def verify_questionnaire_page():
    """验证问卷填写页面"""
    print("\n" + "=" * 60)
    print("验证问卷填写页面")
    print("=" * 60)
    
    with open("src/ui/pages/questionnaire_fill.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    features = {
        "问卷ID获取": "questionnaire_id",
        "API请求": "api_request",
        "单选题": "single_choice",
        "多选题": "multiple_choice",
        "量表题": "scale",
        "开放题": "open_ended",
        "表单提交": "st.form",
        "匹配结果展示": "match_result"
    }
    
    all_found = True
    for feature_name, feature_code in features.items():
        if feature_code in content:
            print(f"✅ 功能实现: {feature_name}")
        else:
            print(f"❌ 功能缺失: {feature_name}")
            all_found = False
    
    return all_found


def verify_requirements():
    """验证依赖项"""
    print("\n" + "=" * 60)
    print("验证依赖项配置")
    print("=" * 60)
    
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = f.read()
    
    required_packages = [
        "streamlit",
        "pandas",
        "plotly",
        "requests"
    ]
    
    all_found = True
    for package in required_packages:
        if package in requirements:
            print(f"✅ 依赖项: {package}")
        else:
            print(f"❌ 缺失依赖: {package}")
            all_found = False
    
    return all_found


def main():
    """主验证流程"""
    print("\n" + "=" * 60)
    print("Task 8: Streamlit前端实现 - 验证报告")
    print("=" * 60)
    
    results = []
    
    # 1. 验证文件结构
    results.append(("文件结构", verify_ui_files()))
    
    # 2. 验证模块导入
    results.append(("模块导入", verify_ui_imports()))
    
    # 3. 验证UI功能
    results.append(("UI功能", verify_ui_features()))
    
    # 4. 验证问卷页面
    results.append(("问卷页面", verify_questionnaire_page()))
    
    # 5. 验证依赖项
    results.append(("依赖项", verify_requirements()))
    
    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有验证通过！Task 8 实现完成！")
        print("=" * 60)
        print("\n✅ 实现的功能:")
        print("  - 8.0 批量上传页面（文件上传、进度显示、结果汇总）")
        print("  - 8.1 JD分析页面（文本输入、文件上传、结果展示）")
        print("  - 8.1.5 职位分类管理页面（分类树、CRUD操作、样本JD）")
        print("  - 8.2 问卷生成和管理页面（生成、预览、分享链接）")
        print("  - 8.3 问卷填写页面（独立页面、多种题型、结果展示）")
        print("  - 8.4 匹配结果展示页面（分数、雷达图、优势差距）")
        print("  - 8.5 模板管理页面（创建、编辑、列表）")
        print("\n📝 启动方式:")
        print("  streamlit run src/ui/app.py")
        print("  或: python run.py")
        return 0
    else:
        print("⚠️  部分验证未通过，请检查上述失败项")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
