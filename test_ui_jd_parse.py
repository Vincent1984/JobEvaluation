"""测试 JD 解析页面的功能"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_imports():
    """测试所有必要的导入"""
    print("测试导入...")
    
    try:
        import streamlit as st
        print("✅ Streamlit 导入成功")
    except ImportError as e:
        print(f"❌ Streamlit 导入失败: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests 导入成功")
    except ImportError as e:
        print(f"❌ Requests 导入失败: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas 导入成功")
    except ImportError as e:
        print(f"❌ Pandas 导入失败: {e}")
        return False
    
    try:
        from src.models.schemas import EvaluationModel
        print("✅ EvaluationModel 导入成功")
    except ImportError as e:
        print(f"❌ EvaluationModel 导入失败: {e}")
        return False
    
    return True


def test_api_connection():
    """测试 API 连接"""
    print("\n测试 API 连接...")
    
    import requests
    
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API 服务正常运行: {API_BASE_URL}")
            return True
        else:
            print(f"⚠️ API 返回状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 API 服务: {API_BASE_URL}")
        print("💡 请确保 API 服务正在运行")
        return False
    except Exception as e:
        print(f"❌ API 连接测试失败: {e}")
        return False


def test_file_structure():
    """测试文件结构"""
    print("\n测试文件结构...")
    
    required_files = [
        "src/ui/app.py",
        "src/models/schemas.py",
        "src/api/main.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist


def test_ui_syntax():
    """测试 UI 文件语法"""
    print("\n测试 UI 文件语法...")
    
    try:
        with open("src/ui/app.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        compile(code, "src/ui/app.py", "exec")
        print("✅ UI 文件语法正确")
        return True
    except SyntaxError as e:
        print(f"❌ UI 文件语法错误: {e}")
        print(f"   行号: {e.lineno}")
        print(f"   错误位置: {e.text}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("="*70)
    print("JD 解析页面诊断测试")
    print("="*70)
    
    results = {
        "导入测试": test_imports(),
        "文件结构测试": test_file_structure(),
        "语法测试": test_ui_syntax(),
        "API连接测试": test_api_connection()
    }
    
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ 所有测试通过！")
        print("\n您可以运行以下命令启动 UI:")
        print("  streamlit run src/ui/app.py")
    else:
        print("❌ 部分测试失败，请检查上述错误信息")
        print("\n常见问题解决方案:")
        print("1. 如果导入失败，请安装依赖: pip install -r requirements.txt")
        print("2. 如果 API 连接失败，请启动 API 服务: python -m src.api.main")
        print("3. 如果文件不存在，请检查项目结构")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
