"""测试职位分类创建修复"""

import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"


def test_category_creation():
    """测试分类创建流程"""
    
    print("=" * 60)
    print("测试职位分类创建修复")
    print("=" * 60)
    print()
    
    # 1. 创建测试企业
    print("1️⃣ 创建测试企业...")
    company_data = {"name": "测试企业-分类创建"}
    
    response = requests.post(f"{API_BASE_URL}/companies", json=company_data)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            company_id = result["data"]["id"]
            print(f"   ✅ 企业创建成功: {company_id}")
        else:
            print(f"   ❌ 失败: {result}")
            return
    else:
        print(f"   ❌ 请求失败: {response.status_code}")
        return
    
    print()
    
    # 2. 获取企业分类树（应该为空）
    print("2️⃣ 获取企业分类树（初始状态）...")
    response = requests.get(f"{API_BASE_URL}/companies/{company_id}/categories/tree")
    if response.status_code == 200:
        result = response.json()
        print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get("success"):
            data = result.get("data", {})
            tree = data.get("category_tree", [])
            print(f"   ✅ 获取成功，分类数量: {len(tree)}")
        else:
            print(f"   ❌ 失败")
    else:
        print(f"   ❌ 请求失败: {response.status_code}")
    
    print()
    
    # 3. 创建第一层级分类
    print("3️⃣ 创建第一层级分类...")
    category_data = {
        "company_id": company_id,
        "name": "技术类",
        "level": 1,
        "description": "技术相关岗位"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/companies/{company_id}/categories",
        json=category_data
    )
    
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            category_id = result["data"]["id"]
            print(f"   ✅ 分类创建成功: {category_id}")
        else:
            print(f"   ❌ 失败: {result}")
            return
    else:
        print(f"   ❌ 请求失败")
        return
    
    print()
    
    # 4. 再次获取分类树（应该有一个分类）
    print("4️⃣ 获取企业分类树（创建后）...")
    response = requests.get(f"{API_BASE_URL}/companies/{company_id}/categories/tree")
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", {})
            tree = data.get("category_tree", [])
            print(f"   ✅ 获取成功，分类数量: {len(tree)}")
            print(f"   分类树: {json.dumps(tree, ensure_ascii=False, indent=2)}")
        else:
            print(f"   ❌ 失败")
    else:
        print(f"   ❌ 请求失败")
    
    print()
    
    # 5. 清理
    print("5️⃣ 清理测试数据...")
    response = requests.delete(f"{API_BASE_URL}/companies/{company_id}?confirm=true")
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"   ✅ 清理成功")
        else:
            print(f"   ❌ 清理失败")
    
    print()
    print("=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_category_creation()
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
