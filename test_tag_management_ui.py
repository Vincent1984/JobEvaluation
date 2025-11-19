"""测试分类标签管理UI功能"""

import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"


def test_tag_management_workflow():
    """测试完整的标签管理工作流"""
    
    print("=" * 60)
    print("测试分类标签管理UI功能")
    print("=" * 60)
    
    # 1. 创建测试企业
    print("\n1. 创建测试企业...")
    company_response = requests.post(
        f"{API_BASE_URL}/companies",
        json={"name": "测试企业-标签管理"}
    )
    
    if company_response.status_code == 200:
        company_data = company_response.json()
        company_id = company_data["data"]["id"]
        print(f"✅ 企业创建成功: {company_id}")
    else:
        print(f"❌ 企业创建失败: {company_response.text}")
        return
    
    # 2. 创建三层级分类
    print("\n2. 创建三层级分类...")
    
    # 第一层级
    cat1_response = requests.post(
        f"{API_BASE_URL}/categories",
        json={
            "name": "技术类",
            "level": 1,
            "company_id": company_id,
            "description": "技术相关岗位"
        }
    )
    cat1_id = cat1_response.json()["data"]["id"]
    print(f"✅ 第一层级创建成功: {cat1_id}")
    
    # 第二层级
    cat2_response = requests.post(
        f"{API_BASE_URL}/categories",
        json={
            "name": "研发",
            "level": 2,
            "parent_id": cat1_id,
            "company_id": company_id,
            "description": "研发团队"
        }
    )
    cat2_id = cat2_response.json()["data"]["id"]
    print(f"✅ 第二层级创建成功: {cat2_id}")
    
    # 第三层级
    cat3_response = requests.post(
        f"{API_BASE_URL}/categories",
        json={
            "name": "后端工程师",
            "level": 3,
            "parent_id": cat2_id,
            "company_id": company_id,
            "description": "后端开发岗位"
        }
    )
    cat3_id = cat3_response.json()["data"]["id"]
    print(f"✅ 第三层级创建成功: {cat3_id}")
    
    # 3. 为第三层级添加标签
    print("\n3. 为第三层级分类添加标签...")
    
    tags_to_create = [
        {
            "name": "高战略重要性",
            "tag_type": "战略重要性",
            "description": "该岗位对公司战略目标实现具有重要影响"
        },
        {
            "name": "高业务价值",
            "tag_type": "业务价值",
            "description": "该岗位直接创造业务价值，对营收有显著贡献"
        },
        {
            "name": "技能稀缺",
            "tag_type": "技能稀缺性",
            "description": "该岗位所需技能在市场上较为稀缺，招聘难度大"
        }
    ]
    
    created_tag_ids = []
    for tag_data in tags_to_create:
        tag_response = requests.post(
            f"{API_BASE_URL}/categories/{cat3_id}/tags",
            json=tag_data
        )
        
        if tag_response.status_code == 200:
            tag_id = tag_response.json()["data"]["id"]
            created_tag_ids.append(tag_id)
            print(f"✅ 标签创建成功: {tag_data['name']} ({tag_id})")
        else:
            print(f"❌ 标签创建失败: {tag_response.text}")
    
    # 4. 获取分类的所有标签
    print("\n4. 获取分类的所有标签...")
    get_tags_response = requests.get(f"{API_BASE_URL}/categories/{cat3_id}/tags")
    
    if get_tags_response.status_code == 200:
        tags = get_tags_response.json()["data"]
        print(f"✅ 获取到 {len(tags)} 个标签:")
        for tag in tags:
            print(f"   - {tag['name']} ({tag['tag_type']}): {tag['description']}")
    else:
        print(f"❌ 获取标签失败: {get_tags_response.text}")
    
    # 5. 更新标签
    print("\n5. 更新第一个标签...")
    if created_tag_ids:
        update_tag_response = requests.put(
            f"{API_BASE_URL}/tags/{created_tag_ids[0]}",
            json={
                "name": "极高战略重要性",
                "description": "该岗位对公司战略目标实现具有极其重要的影响，属于核心岗位"
            }
        )
        
        if update_tag_response.status_code == 200:
            print(f"✅ 标签更新成功")
            updated_tag = update_tag_response.json()["data"]
            print(f"   新名称: {updated_tag['name']}")
            print(f"   新描述: {updated_tag['description']}")
        else:
            print(f"❌ 标签更新失败: {update_tag_response.text}")
    
    # 6. 删除一个标签
    print("\n6. 删除最后一个标签...")
    if len(created_tag_ids) > 1:
        delete_tag_response = requests.delete(
            f"{API_BASE_URL}/tags/{created_tag_ids[-1]}"
        )
        
        if delete_tag_response.status_code == 200:
            print(f"✅ 标签删除成功")
        else:
            print(f"❌ 标签删除失败: {delete_tag_response.text}")
    
    # 7. 验证删除后的标签列表
    print("\n7. 验证删除后的标签列表...")
    final_tags_response = requests.get(f"{API_BASE_URL}/categories/{cat3_id}/tags")
    
    if final_tags_response.status_code == 200:
        final_tags = final_tags_response.json()["data"]
        print(f"✅ 当前剩余 {len(final_tags)} 个标签:")
        for tag in final_tags:
            print(f"   - {tag['name']} ({tag['tag_type']})")
    else:
        print(f"❌ 获取标签失败: {final_tags_response.text}")
    
    # 8. 获取分类树（验证标签徽章显示）
    print("\n8. 获取分类树（验证标签数量）...")
    tree_response = requests.get(f"{API_BASE_URL}/categories/tree")
    
    if tree_response.status_code == 200:
        tree_data = tree_response.json()["data"]
        print(f"✅ 分类树获取成功")
        
        # 递归查找第三层级分类
        def find_level3_categories(nodes, level=1):
            level3_cats = []
            for node in nodes:
                if level == 3:
                    level3_cats.append(node)
                if node.get('children'):
                    level3_cats.extend(find_level3_categories(node['children'], level + 1))
            return level3_cats
        
        level3_cats = find_level3_categories(tree_data)
        for cat in level3_cats:
            # 获取该分类的标签数量
            tags_resp = requests.get(f"{API_BASE_URL}/categories/{cat['id']}/tags")
            if tags_resp.status_code == 200:
                tag_count = len(tags_resp.json()["data"])
                print(f"   - {cat['name']}: {tag_count} 个标签")
    else:
        print(f"❌ 获取分类树失败: {tree_response.text}")
    
    # 清理：删除测试企业
    print("\n9. 清理测试数据...")
    delete_company_response = requests.delete(
        f"{API_BASE_URL}/companies/{company_id}?confirm=true"
    )
    
    if delete_company_response.status_code == 200:
        print(f"✅ 测试企业删除成功")
    else:
        print(f"❌ 测试企业删除失败: {delete_company_response.text}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_tag_management_workflow()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器")
        print("💡 请确保API服务正在运行: python -m uvicorn src.api.main:app --reload")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
