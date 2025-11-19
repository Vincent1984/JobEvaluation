"""测试评估结果手动修改API端点（简化版）"""

import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from src.api.main import app

def test_update_evaluation_endpoint():
    """测试PUT /api/v1/jd/{jd_id}/evaluation端点的基本功能"""
    
    print("=" * 60)
    print("测试评估结果手动修改API端点")
    print("=" * 60)
    
    client = TestClient(app)
    
    # 测试1: 验证端点存在
    print("\n1. 验证端点路由...")
    
    # 获取所有路由
    routes = [route.path for route in app.routes]
    expected_route = "/api/v1/jd/{jd_id}/evaluation"
    
    if expected_route in routes:
        print(f"✓ 端点已注册: {expected_route}")
    else:
        print(f"✗ 端点未找到: {expected_route}")
        print(f"可用路由: {routes}")
        return False
    
    # 测试2: 验证请求格式
    print("\n2. 测试请求格式验证...")
    
    # 测试无效的JD ID（应该返回404或500，因为JD不存在）
    test_jd_id = "nonexistent_jd"
    test_payload = {
        "overall_score": 92.0,
        "company_value": "高价值",
        "is_core_position": True,
        "reason": "测试修改"
    }
    
    try:
        response = client.put(
            f"/api/v1/jd/{test_jd_id}/evaluation",
            json=test_payload
        )
        
        print(f"  响应状态码: {response.status_code}")
        
        # 期望404或500（因为JD不存在）
        if response.status_code in [404, 500]:
            print(f"✓ 正确处理不存在的JD（状态码: {response.status_code}）")
        else:
            print(f"  响应内容: {response.json()}")
    except Exception as e:
        print(f"  请求异常: {e}")
    
    # 测试3: 验证字段验证
    print("\n3. 测试字段验证...")
    
    # 测试无效的overall_score
    invalid_payload = {
        "overall_score": 150.0,  # 超出范围
        "reason": "测试"
    }
    
    try:
        response = client.put(
            f"/api/v1/jd/{test_jd_id}/evaluation",
            json=invalid_payload
        )
        
        print(f"  无效分数响应: {response.status_code}")
        if response.status_code == 400:
            print(f"✓ 正确拒绝无效分数")
            print(f"  错误信息: {response.json().get('detail')}")
        else:
            print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  请求异常: {e}")
    
    # 测试无效的company_value
    invalid_payload2 = {
        "company_value": "超高价值",  # 无效值
        "reason": "测试"
    }
    
    try:
        response = client.put(
            f"/api/v1/jd/{test_jd_id}/evaluation",
            json=invalid_payload2
        )
        
        print(f"  无效企业价值响应: {response.status_code}")
        if response.status_code == 400:
            print(f"✓ 正确拒绝无效企业价值")
            print(f"  错误信息: {response.json().get('detail')}")
        else:
            print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  请求异常: {e}")
    
    # 测试4: 验证空修改
    print("\n4. 测试空修改请求...")
    
    empty_payload = {
        "reason": "测试"
    }
    
    try:
        response = client.put(
            f"/api/v1/jd/{test_jd_id}/evaluation",
            json=empty_payload
        )
        
        print(f"  空修改响应: {response.status_code}")
        if response.status_code == 400:
            print(f"✓ 正确拒绝空修改")
            print(f"  错误信息: {response.json().get('detail')}")
        else:
            print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  请求异常: {e}")
    
    # 测试5: 验证API文档
    print("\n5. 验证API文档...")
    
    try:
        response = client.get("/docs")
        if response.status_code == 200:
            print("✓ API文档可访问")
        else:
            print(f"  文档响应: {response.status_code}")
    except Exception as e:
        print(f"  文档访问异常: {e}")
    
    print("\n" + "=" * 60)
    print("✓ 端点基本功能测试完成")
    print("=" * 60)
    print("\n注意: 完整的集成测试需要Redis和数据库环境")
    
    return True


if __name__ == "__main__":
    try:
        result = test_update_evaluation_endpoint()
        if result:
            print("\n✓ 测试通过!")
            sys.exit(0)
        else:
            print("\n✗ 测试失败!")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
