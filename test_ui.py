"""测试UI模块"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_ui_imports():
    """测试UI模块导入"""
    try:
        # 测试导入主要依赖
        import streamlit as st
        import requests
        import pandas as pd
        import plotly.graph_objects as go
        
        print("✅ 所有UI依赖导入成功")
        
        # 测试模型导入
        from src.models.schemas import EvaluationModel
        print("✅ 模型导入成功")
        
        # 验证API基础URL配置
        API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
        print(f"✅ API基础URL: {API_BASE_URL}")
        
        print("\n✅ UI模块测试通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    success = test_ui_imports()
    sys.exit(0 if success else 1)
