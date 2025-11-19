"""生成完整的测试数据：企业、三层级职位分类和标签"""

import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"

def api_request(method, endpoint, **kwargs):
    """发送API请求"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, **kwargs)
        print(f"   状态码: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 请求失败: {str(e)}")
        return None

print("=" * 60)
print("生成完整测试数据")
print("=" * 60)

# 1. 创建企业
print("\n1️⃣ 创建测试企业...")
company_data = {
    "name": "示例科技公司",
    "description": "用于测试的示例企业"
}
company_response = api_request("POST", "/companies", json=company_data)
if company_response and company_response.get("success"):
    company = company_response["data"]
    company_id = company["id"]
    print(f"   ✅ 企业创建成功: {company['name']} ({company_id})")
else:
    print("   ❌ 企业创建失败")
    exit(1)

# 2. 创建三层级职位分类
print("\n2️⃣ 创建三层级职位分类...")

# 第一层级：技术类
print("\n   创建第一层级：技术类")
level1_data = {
    "company_id": company_id,
    "name": "技术类",
    "level": 1,
    "description": "技术相关岗位"
}
level1_response = api_request("POST", "/categories", json=level1_data)
if level1_response and level1_response.get("success"):
    level1_cat = level1_response["data"]
    level1_id = level1_cat["id"]
    print(f"   ✅ 第一层级创建成功: {level1_cat['name']} ({level1_id})")
else:
    print("   ❌ 第一层级创建失败")
    exit(1)

# 第二层级：研发部
print("\n   创建第二层级：研发部")
level2_data = {
    "company_id": company_id,
    "name": "研发部",
    "level": 2,
    "parent_id": level1_id,
    "description": "软件研发相关岗位"
}
level2_response = api_request("POST", "/categories", json=level2_data)
if level2_response and level2_response.get("success"):
    level2_cat = level2_response["data"]
    level2_id = level2_cat["id"]
    print(f"   ✅ 第二层级创建成功: {level2_cat['name']} ({level2_id})")
else:
    print("   ❌ 第二层级创建失败")
    exit(1)

# 第三层级：后端开发
print("\n   创建第三层级：后端开发")
level3_data = {
    "company_id": company_id,
    "name": "后端开发",
    "level": 3,
    "parent_id": level2_id,
    "description": "后端开发工程师岗位"
}
level3_response = api_request("POST", "/categories", json=level3_data)
if level3_response and level3_response.get("success"):
    level3_cat = level3_response["data"]
    level3_id = level3_cat["id"]
    print(f"   ✅ 第三层级创建成功: {level3_cat['name']} ({level3_id})")
else:
    print("   ❌ 第三层级创建失败")
    exit(1)

# 3. 为第三层级添加标签
print("\n3️⃣ 为第三层级分类添加标签...")

tags = [
    {
        "name": "Python开发",
        "tag_type": "技术栈",
        "description": "需要Python编程能力"
    },
    {
        "name": "数据库设计",
        "tag_type": "技术栈",
        "description": "需要数据库设计和优化能力"
    },
    {
        "name": "API设计",
        "tag_type": "技术栈",
        "description": "需要RESTful API设计能力"
    },
    {
        "name": "团队协作",
        "tag_type": "软技能",
        "description": "需要良好的团队协作能力"
    },
    {
        "name": "问题解决",
        "tag_type": "软技能",
        "description": "需要独立解决问题的能力"
    }
]

for tag_data in tags:
    tag_response = api_request("POST", f"/categories/{level3_id}/tags", json=tag_data)
    if tag_response and tag_response.get("success"):
        tag = tag_response["data"]
        print(f"   ✅ 标签创建成功: {tag['name']} ({tag['tag_type']})")
    else:
        print(f"   ❌ 标签创建失败: {tag_data['name']}")

# 4. 验证分类树
print("\n4️⃣ 验证分类树结构...")
tree_response = api_request("GET", f"/companies/{company_id}/categories/tree")
if tree_response and tree_response.get("success"):
    tree_data = tree_response["data"]
    print(f"   ✅ 分类树获取成功")
    print(f"\n   分类树结构:")
    print(json.dumps(tree_data, indent=2, ensure_ascii=False))
else:
    print("   ❌ 分类树获取失败")

# 5. 验证标签
print("\n5️⃣ 验证第三层级标签...")
tags_response = api_request("GET", f"/categories/{level3_id}/tags")
if tags_response and tags_response.get("success"):
    tags_list = tags_response["data"]
    print(f"   ✅ 标签获取成功，共 {len(tags_list)} 个标签")
    for tag in tags_list:
        print(f"      - {tag['name']} ({tag['tag_type']}): {tag['description']}")
else:
    print("   ❌ 标签获取失败")

print("\n" + "=" * 60)
print("✅ 测试数据生成完成！")
print("=" * 60)
print(f"\n企业ID: {company_id}")
print(f"第一层级ID: {level1_id}")
print(f"第二层级ID: {level2_id}")
print(f"第三层级ID: {level3_id}")
print("\n现在可以在UI中测试JD评估功能了！")
