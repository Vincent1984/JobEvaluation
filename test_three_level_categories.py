"""测试三层级分类创建流程"""

import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"


def test_three_level_categories():
    """测试完整的三层级分类创建"""
    
    print("=" * 60)
    print("测试三层级分类创建流程")
    print("=" * 60)
    print()
    
    # 1. 创建企业
    print("1️⃣ 创建测试企业...")
    company_data = {"name": "三层级测试企业"}
    response = requests.post(f"{API_BASE_URL}/companies", json=company_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            company_id = result["data"]["id"]
            print(f"   ✅ 企业创建成功: {company_id}")
        else:
            print(f"   ❌ 失败")
            return
    else:
        print(f"   ❌ 请求失败")
        return
    
    print()
    
    # 2. 创建第一层级分类
    print("2️⃣ 创建第一层级分类...")
    level1_data = {
        "company_id": company_id,
        "name": "技术类",
        "level": 1,
        "description": "技术相关岗位"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/companies/{company_id}/categories",
        json=level1_data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            level1_id = result["data"]["id"]
            print(f"   ✅ 第一层级创建成功: {level1_id}")
            print(f"   名称: {result['data']['name']}")
        else:
            print(f"   ❌ 失败: {result}")
            return
    else:
        print(f"   ❌ 请求失败: {response.text}")
        return
    
    print()
    
    # 3. 获取第一层级分类列表（用于创建第二层级时选择父级）
    print("3️⃣ 获取第一层级分类列表...")
    response = requests.get(f"{API_BASE_URL}/companies/{company_id}/categories?level=1")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            level1_categories = result.get("data", [])
            print(f"   ✅ 获取成功，共 {len(level1_categories)} 个第一层级分类")
            for cat in level1_categories:
                print(f"   - {cat['name']} ({cat['id']})")
        else:
            print(f"   ❌ 失败")
            return
    else:
        print(f"   ❌ 请求失败")
        return
    
    print()
    
    # 4. 创建第二层级分类
    print("4️⃣ 创建第二层级分类...")
    level2_data = {
        "company_id": company_id,
        "name": "研发工程师",
        "level": 2,
        "parent_id": level1_id,  # 关联到第一层级
        "description": "软件研发相关岗位"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/companies/{company_id}/categories",
        json=level2_data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            level2_id = result["data"]["id"]
            print(f"   ✅ 第二层级创建成功: {level2_id}")
            print(f"   名称: {result['data']['name']}")
            print(f"   父级ID: {result['data']['parent_id']}")
        else:
            print(f"   ❌ 失败: {result}")
            return
    else:
        print(f"   ❌ 请求失败: {response.text}")
        return
    
    print()
    
    # 5. 获取第二层级分类列表（用于创建第三层级时选择父级）
    print("5️⃣ 获取第二层级分类列表...")
    response = requests.get(f"{API_BASE_URL}/companies/{company_id}/categories?level=2")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            level2_categories = result.get("data", [])
            print(f"   ✅ 获取成功，共 {len(level2_categories)} 个第二层级分类")
            for cat in level2_categories:
                print(f"   - {cat['name']} ({cat['id']}) -> 父级: {cat['parent_id']}")
        else:
            print(f"   ❌ 失败")
            return
    else:
        print(f"   ❌ 请求失败")
        return
    
    print()
    
    # 6. 创建第三层级分类
    print("6️⃣ 创建第三层级分类...")
    level3_data = {
        "company_id": company_id,
        "name": "Python后端工程师",
        "level": 3,
        "parent_id": level2_id,  # 关联到第二层级
        "description": "Python后端开发岗位",
        "sample_jd_ids": ["jd_sample_001"]
    }
    
    response = requests.post(
        f"{API_BASE_URL}/companies/{company_id}/categories",
        json=level3_data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            level3_id = result["data"]["id"]
            print(f"   ✅ 第三层级创建成功: {level3_id}")
            print(f"   名称: {result['data']['name']}")
            print(f"   父级ID: {result['data']['parent_id']}")
            print(f"   样本JD: {result['data']['sample_jd_ids']}")
        else:
            print(f"   ❌ 失败: {result}")
            return
    else:
        print(f"   ❌ 请求失败: {response.text}")
        return
    
    print()
    
    # 7. 获取完整的分类树
    print("7️⃣ 获取完整的分类树...")
    response = requests.get(f"{API_BASE_URL}/companies/{company_id}/categories/tree")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result.get("data", {})
            tree = data.get("category_tree", [])
            print(f"   ✅ 获取成功")
            print(f"   分类树结构:")
            print(json.dumps(tree, ensure_ascii=False, indent=2))
        else:
            print(f"   ❌ 失败")
    else:
        print(f"   ❌ 请求失败")
    
    print()
    
    # 8. 清理
    print("8️⃣ 清理测试数据...")
    response = requests.delete(f"{API_BASE_URL}/companies/{company_id}?confirm=true")
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"   ✅ 清理成功")
    
    print()
    print("=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print()
    print("📋 总结:")
    print("   - 第一层级: 技术类")
    print("   - 第二层级: 研发工程师 (父级: 技术类)")
    print("   - 第三层级: Python后端工程师 (父级: 研发工程师)")


if __name__ == "__main__":
    try:
        test_three_level_categories()
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
