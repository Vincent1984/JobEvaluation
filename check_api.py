"""检查 API 服务状态"""

import requests
import sys
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def check_api():
    """检查 API 服务是否运行"""
    print("="*70)
    print("API 服务状态检查")
    print("="*70)
    
    print(f"\n检查 API 服务: {API_BASE_URL}")
    
    try:
        # 尝试连接健康检查端点
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ API 服务正常运行")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.json()}")
            print(f"\n📚 API 文档:")
            print(f"   Swagger UI: {API_BASE_URL}/docs")
            print(f"   ReDoc: {API_BASE_URL}/redoc")
            return True
        else:
            print(f"⚠️ API 返回异常状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 API 服务")
        print(f"\n💡 解决方案:")
        print(f"   1. 启动 API 服务:")
        print(f"      python -m src.api.main")
        print(f"\n   2. 或使用 uvicorn:")
        print(f"      uvicorn src.api.main:app --host 0.0.0.0 --port 8000")
        print(f"\n   3. 检查端口是否被占用:")
        print(f"      netstat -ano | findstr :8000")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ API 服务响应超时")
        print("   服务可能正在启动或负载过高")
        return False
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def check_endpoints():
    """检查关键 API 端点"""
    print("\n" + "="*70)
    print("检查关键 API 端点")
    print("="*70)
    
    endpoints = [
        ("GET", "/api/v1/companies", "企业列表"),
        ("GET", "/api/v1/categories", "分类列表"),
        ("GET", "/api/v1/templates", "模板列表"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        url = f"{API_BASE_URL}{endpoint}"
        print(f"\n检查: {description}")
        print(f"   {method} {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.request(method, url, timeout=5)
            
            if response.status_code in [200, 404]:
                # 200 = 成功, 404 = 端点存在但无数据
                print(f"   ✅ 端点可访问 (状态码: {response.status_code})")
                results.append(True)
            else:
                print(f"   ⚠️ 状态码: {response.status_code}")
                results.append(False)
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 无法连接")
            results.append(False)
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            results.append(False)
    
    return all(results)

def main():
    """主函数"""
    # 检查 API 服务
    api_running = check_api()
    
    if not api_running:
        print("\n" + "="*70)
        print("❌ API 服务未运行，无法继续检查")
        print("="*70)
        return False
    
    # 检查端点
    endpoints_ok = check_endpoints()
    
    # 总结
    print("\n" + "="*70)
    print("检查结果总结")
    print("="*70)
    
    if api_running and endpoints_ok:
        print("✅ 所有检查通过！")
        print("\n您现在可以:")
        print("   1. 访问 API 文档: http://localhost:8000/docs")
        print("   2. 启动 UI: streamlit run src/ui/app.py")
    elif api_running:
        print("⚠️ API 服务运行中，但部分端点可能未实现")
        print("\n您仍然可以:")
        print("   1. 启动 UI: streamlit run src/ui/app.py")
        print("   2. 使用已实现的功能")
    else:
        print("❌ API 服务未运行")
        print("\n请先启动 API 服务:")
        print("   python -m src.api.main")
    
    print("="*70)
    
    return api_running

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
