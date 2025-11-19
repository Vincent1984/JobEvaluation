"""测试企业管理API端点"""

import sys
import asyncio
from pathlib import Path

# Windows平台asyncio修复
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_create_company():
    """测试创建企业"""
    response = client.post(
        "/api/v1/companies",
        json={"name": "测试科技有限公司"}
    )
    
    print(f"创建企业响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["name"] == "测试科技有限公司"
    
    return data["data"]["id"]


def test_list_companies():
    """测试列出所有企业"""
    response = client.get("/api/v1/companies")
    
    print(f"\n列出企业响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_company(company_id: str):
    """测试获取企业详情"""
    response = client.get(f"/api/v1/companies/{company_id}")
    
    print(f"\n获取企业详情响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == company_id


def test_update_company(company_id: str):
    """测试更新企业名称"""
    response = client.put(
        f"/api/v1/companies/{company_id}",
        json={"name": "新测试科技有限公司"}
    )
    
    print(f"\n更新企业响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "新测试科技有限公司"


def test_list_company_categories(company_id: str):
    """测试列出企业的分类"""
    response = client.get(f"/api/v1/companies/{company_id}/categories")
    
    print(f"\n列出企业分类响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_get_company_category_tree(company_id: str):
    """测试获取企业的分类树"""
    response = client.get(f"/api/v1/companies/{company_id}/categories/tree")
    
    print(f"\n获取企业分类树响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "company" in data["data"]
    assert "category_tree" in data["data"]


def test_delete_company_without_confirm(company_id: str):
    """测试删除企业（不确认）"""
    response = client.delete(f"/api/v1/companies/{company_id}")
    
    print(f"\n删除企业（不确认）响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["confirm_required"] is True


def test_delete_company_with_confirm(company_id: str):
    """测试删除企业（确认）"""
    response = client.delete(f"/api/v1/companies/{company_id}?confirm=true")
    
    print(f"\n删除企业（确认）响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_create_category_with_company():
    """测试创建带企业ID的分类"""
    # 先创建企业
    company_response = client.post(
        "/api/v1/companies",
        json={"name": "分类测试企业"}
    )
    company_id = company_response.json()["data"]["id"]
    
    # 创建一级分类
    response = client.post(
        "/api/v1/categories",
        json={
            "company_id": company_id,
            "name": "技术类",
            "level": 1,
            "description": "技术相关岗位"
        }
    )
    
    print(f"\n创建分类响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["company_id"] == company_id
    
    return company_id


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试企业管理API端点")
    print("=" * 60)
    
    try:
        # 测试创建企业
        company_id = test_create_company()
        
        # 测试列出企业
        test_list_companies()
        
        # 测试获取企业详情
        test_get_company(company_id)
        
        # 测试更新企业
        test_update_company(company_id)
        
        # 测试列出企业分类
        test_list_company_categories(company_id)
        
        # 测试获取企业分类树
        test_get_company_category_tree(company_id)
        
        # 测试删除企业（不确认）
        test_delete_company_without_confirm(company_id)
        
        # 测试删除企业（确认）
        test_delete_company_with_confirm(company_id)
        
        # 测试创建带企业ID的分类
        test_create_category_with_company()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        raise
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
