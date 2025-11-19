"""测试职位分类管理UI的企业选择功能"""

import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"


def test_category_ui_workflow():
    """测试完整的分类管理工作流"""
    
    print("=" * 60)
    print("测试职位分类管理UI - 企业选择功能")
    print("=" * 60)
    print()
    
    # 1. 创建测试企业
    print("1️⃣ 创建测试企业...")
    company_data = {
        "name": "测试科技公司"
    }
    
    response = requests.post(f"{API_BASE_URL}/companies", json=company_data)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            company = result.get("data", {})
            company_id = company.get("id")
            print(f"   ✅ 企业创建成功")
            print(f"   企业ID: {company_id}")
            print(f"   企业名称: {company.get('name')}")
        else:
            print(f"   ❌ 创建失败: {result.get('detail')}")
            return
    else:
        print(f"   ❌ 请求失败: {response.text}")
        return
    
    print()
    
    # 2. 获取所有企业（模拟UI的企业选择器）
    print("2️⃣ 获取所有企业（模拟UI选择器）...")
    response = requests.get(f"{API_BASE_URL}/companies")
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            companies = result.get("data", [])
            print(f"   ✅ 获取成功，共 {len(companies)} 个企业")
            for c in companies:
                print(f"   - {c['name']} ({c['id']})")
        else:
            print(f"   ❌ 获取失败")
            return
    else:
        print(f"   ❌ 请求失败")
        return
    
    print()
    
    # 3. 为企业创建第一层级分类
    print("3️⃣ 为企业创建第一层级分类...")
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
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            category = result.get("data", {})
            category_id = category.get("id")
            print(f"   ✅ 分类创建成功")
            print(f"   分类ID: {category_id}")
            print(f"   分类名称: {category.get('name')}")
        else:
            print(f"   ❌ 创建失败: {result.get('detail')}")
            return
    else:
        print(f"   ❌ 请求失败: {response.text}")
        return
    
    print()
    
    # 4. 获取企业的分类树
    print("4️⃣ 获取企业的分类树...")
    response = requests.get(f"{API_BASE_URL}/companies/{company_id}/categories/tree")
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            tree = result.get("data", [])
            print(f"   ✅ 获取成功")
            print(f"   分类树结构:")
            print(json.dumps(tree, ensure_ascii=False, indent=2))
        else:
            print(f"   ❌ 获取失败")
    else:
        print(f"   ❌ 请求失败")
    
    print()
    
    # 5. 清理测试数据
    print("5️⃣ 清理测试数据...")
    response = requests.delete(f"{API_BASE_URL}/companies/{company_id}")
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"   ✅ 企业删除成功")
        else:
            print(f"   ❌ 删除失败")
    else:
        print(f"   ❌ 请求失败")
    
    print()
    print("=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_category_ui_workflow()
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
