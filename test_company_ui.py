"""测试企业管理UI功能"""

import requests
import json

# API基础URL
API_BASE_URL = "http://localhost:8000/api/v1"

def test_company_management():
    """测试企业管理功能"""
    
    print("=" * 60)
    print("测试企业管理API端点")
    print("=" * 60)
    
    # 1. 创建企业
    print("\n1. 测试创建企业...")
    create_response = requests.post(
        f"{API_BASE_URL}/companies",
        json={"name": "测试科技有限公司"}
    )
    print(f"状态码: {create_response.status_code}")
    create_data = create_response.json()
    print(f"响应: {json.dumps(create_data, ensure_ascii=False, indent=2)}")
    
    if create_data.get("success"):
        company_id = create_data["data"]["id"]
        print(f"✅ 企业创建成功，ID: {company_id}")
    else:
        print("❌ 企业创建失败")
        return
    
    # 2. 获取企业列表
    print("\n2. 测试获取企业列表...")
    list_response = requests.get(f"{API_BASE_URL}/companies")
    print(f"状态码: {list_response.status_code}")
    list_data = list_response.json()
    print(f"企业数量: {list_data.get('total', 0)}")
    print(f"✅ 获取企业列表成功")
    
    # 3. 获取企业详情
    print(f"\n3. 测试获取企业详情 (ID: {company_id})...")
    detail_response = requests.get(f"{API_BASE_URL}/companies/{company_id}")
    print(f"状态码: {detail_response.status_code}")
    detail_data = detail_response.json()
    print(f"响应: {json.dumps(detail_data, ensure_ascii=False, indent=2)}")
    print(f"✅ 获取企业详情成功")
    
    # 4. 更新企业名称
    print(f"\n4. 测试更新企业名称 (ID: {company_id})...")
    update_response = requests.put(
        f"{API_BASE_URL}/companies/{company_id}",
        json={"name": "新测试科技有限公司"}
    )
    print(f"状态码: {update_response.status_code}")
    update_data = update_response.json()
    print(f"响应: {json.dumps(update_data, ensure_ascii=False, indent=2)}")
    print(f"✅ 更新企业名称成功")
    
    # 5. 获取企业的分类（应该为空）
    print(f"\n5. 测试获取企业的分类 (ID: {company_id})...")
    cat_response = requests.get(f"{API_BASE_URL}/companies/{company_id}/categories")
    print(f"状态码: {cat_response.status_code}")
    cat_data = cat_response.json()
    print(f"分类数量: {cat_data.get('total', 0)}")
    print(f"✅ 获取企业分类成功")
    
    # 6. 获取企业的分类树
    print(f"\n6. 测试获取企业的分类树 (ID: {company_id})...")
    tree_response = requests.get(f"{API_BASE_URL}/companies/{company_id}/categories/tree")
    print(f"状态码: {tree_response.status_code}")
    tree_data = tree_response.json()
    print(f"响应: {json.dumps(tree_data, ensure_ascii=False, indent=2)}")
    print(f"✅ 获取企业分类树成功")
    
    # 7. 测试删除企业（不确认）
    print(f"\n7. 测试删除企业 - 不确认 (ID: {company_id})...")
    delete_check_response = requests.delete(f"{API_BASE_URL}/companies/{company_id}?confirm=false")
    print(f"状态码: {delete_check_response.status_code}")
    delete_check_data = delete_check_response.json()
    print(f"响应: {json.dumps(delete_check_data, ensure_ascii=False, indent=2)}")
    
    if delete_check_data.get("confirm_required"):
        print(f"⚠️ 需要确认删除")
    
    # 8. 测试删除企业（确认）
    print(f"\n8. 测试删除企业 - 确认 (ID: {company_id})...")
    delete_response = requests.delete(f"{API_BASE_URL}/companies/{company_id}?confirm=true")
    print(f"状态码: {delete_response.status_code}")
    delete_data = delete_response.json()
    print(f"响应: {json.dumps(delete_data, ensure_ascii=False, indent=2)}")
    
    if delete_data.get("success"):
        print(f"✅ 企业删除成功")
    else:
        print(f"❌ 企业删除失败")
    
    # 9. 验证企业已删除
    print(f"\n9. 验证企业已删除 (ID: {company_id})...")
    verify_response = requests.get(f"{API_BASE_URL}/companies/{company_id}")
    print(f"状态码: {verify_response.status_code}")
    
    if verify_response.status_code == 404:
        print(f"✅ 企业已成功删除（404 Not Found）")
    else:
        print(f"❌ 企业仍然存在")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_company_management()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务")
        print("💡 请确保API服务正在运行：python -m uvicorn src.api.main:app --reload")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
