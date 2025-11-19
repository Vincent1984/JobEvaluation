"""测试分类标签管理API端点"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 设置环境变量
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/jd_analyzer.db")

from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_tag_management_workflow():
    """测试完整的标签管理工作流"""
    
    # 1. 创建企业
    print("\n1. 创建企业...")
    company_response = client.post(
        "/api/v1/companies",
        json={"name": "测试科技公司"}
    )
    assert company_response.status_code == 200
    company_id = company_response.json()["data"]["id"]
    print(f"   企业创建成功: {company_id}")
    
    # 2. 创建第一层级分类
    print("\n2. 创建第一层级分类...")
    level1_response = client.post(
        "/api/v1/categories",
        json={
            "company_id": company_id,
            "name": "技术类",
            "level": 1,
            "description": "技术相关岗位"
        }
    )
    assert level1_response.status_code == 200
    level1_id = level1_response.json()["data"]["id"]
    print(f"   第一层级分类创建成功: {level1_id}")
    
    # 3. 创建第二层级分类
    print("\n3. 创建第二层级分类...")
    level2_response = client.post(
        "/api/v1/categories",
        json={
            "company_id": company_id,
            "name": "研发",
            "level": 2,
            "parent_id": level1_id,
            "description": "研发团队"
        }
    )
    assert level2_response.status_code == 200
    level2_id = level2_response.json()["data"]["id"]
    print(f"   第二层级分类创建成功: {level2_id}")
    
    # 4. 创建第三层级分类
    print("\n4. 创建第三层级分类...")
    level3_response = client.post(
        "/api/v1/categories",
        json={
            "company_id": company_id,
            "name": "后端工程师",
            "level": 3,
            "parent_id": level2_id,
            "description": "后端开发岗位"
        }
    )
    assert level3_response.status_code == 200
    level3_id = level3_response.json()["data"]["id"]
    print(f"   第三层级分类创建成功: {level3_id}")
    
    # 5. 为第三层级分类添加标签
    print("\n5. 为第三层级分类添加标签...")
    tag1_response = client.post(
        f"/api/v1/categories/{level3_id}/tags",
        json={
            "name": "高战略重要性",
            "tag_type": "战略重要性",
            "description": "该岗位对企业战略目标实现具有重要影响"
        }
    )
    assert tag1_response.status_code == 200
    tag1_id = tag1_response.json()["data"]["id"]
    print(f"   标签1创建成功: {tag1_id}")
    print(f"   标签内容: {tag1_response.json()['data']}")
    
    # 6. 添加第二个标签
    print("\n6. 添加第二个标签...")
    tag2_response = client.post(
        f"/api/v1/categories/{level3_id}/tags",
        json={
            "name": "高技能稀缺性",
            "tag_type": "技能稀缺性",
            "description": "该岗位所需技能在市场上较为稀缺"
        }
    )
    assert tag2_response.status_code == 200
    tag2_id = tag2_response.json()["data"]["id"]
    print(f"   标签2创建成功: {tag2_id}")
    
    # 7. 获取分类的所有标签
    print("\n7. 获取分类的所有标签...")
    get_tags_response = client.get(f"/api/v1/categories/{level3_id}/tags")
    assert get_tags_response.status_code == 200
    tags = get_tags_response.json()["data"]
    assert len(tags) == 2
    print(f"   获取到 {len(tags)} 个标签")
    for tag in tags:
        print(f"   - {tag['name']} ({tag['tag_type']})")
    
    # 8. 更新标签
    print("\n8. 更新标签...")
    update_response = client.put(
        f"/api/v1/tags/{tag1_id}",
        json={
            "name": "极高战略重要性",
            "description": "该岗位对企业战略目标实现具有极其重要的影响"
        }
    )
    assert update_response.status_code == 200
    updated_tag = update_response.json()["data"]
    assert updated_tag["name"] == "极高战略重要性"
    print(f"   标签更新成功: {updated_tag['name']}")
    
    # 9. 删除标签
    print("\n9. 删除标签...")
    delete_response = client.delete(f"/api/v1/tags/{tag2_id}")
    assert delete_response.status_code == 200
    print(f"   标签删除成功")
    
    # 10. 验证标签已删除
    print("\n10. 验证标签已删除...")
    get_tags_after_delete = client.get(f"/api/v1/categories/{level3_id}/tags")
    assert get_tags_after_delete.status_code == 200
    remaining_tags = get_tags_after_delete.json()["data"]
    assert len(remaining_tags) == 1
    print(f"   剩余 {len(remaining_tags)} 个标签")
    
    print("\n✅ 所有测试通过！")


def test_tag_validation():
    """测试标签验证规则"""
    
    print("\n=== 测试标签验证规则 ===")
    
    # 1. 创建测试数据
    company_response = client.post(
        "/api/v1/companies",
        json={"name": "验证测试公司"}
    )
    company_id = company_response.json()["data"]["id"]
    
    level1_response = client.post(
        "/api/v1/categories",
        json={
            "company_id": company_id,
            "name": "测试类",
            "level": 1
        }
    )
    level1_id = level1_response.json()["data"]["id"]
    
    level2_response = client.post(
        "/api/v1/categories",
        json={
            "company_id": company_id,
            "name": "测试子类",
            "level": 2,
            "parent_id": level1_id
        }
    )
    level2_id = level2_response.json()["data"]["id"]
    
    level3_response = client.post(
        "/api/v1/categories",
        json={
            "company_id": company_id,
            "name": "测试岗位",
            "level": 3,
            "parent_id": level2_id
        }
    )
    level3_id = level3_response.json()["data"]["id"]
    
    # 2. 测试：只有第三层级可以添加标签
    print("\n1. 测试：只有第三层级可以添加标签")
    invalid_response = client.post(
        f"/api/v1/categories/{level1_id}/tags",
        json={
            "name": "测试标签",
            "tag_type": "战略重要性",
            "description": "测试"
        }
    )
    assert invalid_response.status_code == 400
    assert "只有第三层级分类才能添加标签" in invalid_response.json()["detail"]
    print("   ✓ 非第三层级分类无法添加标签")
    
    # 3. 测试：无效的标签类型
    print("\n2. 测试：无效的标签类型")
    invalid_type_response = client.post(
        f"/api/v1/categories/{level3_id}/tags",
        json={
            "name": "测试标签",
            "tag_type": "无效类型",
            "description": "测试"
        }
    )
    assert invalid_type_response.status_code == 400
    assert "无效的标签类型" in invalid_type_response.json()["detail"]
    print("   ✓ 无效的标签类型被拒绝")
    
    # 4. 测试：有效的标签类型
    print("\n3. 测试：所有有效的标签类型")
    valid_types = [
        "战略重要性", "业务价值", "技能稀缺性", 
        "市场竞争度", "发展潜力", "风险等级"
    ]
    for tag_type in valid_types:
        response = client.post(
            f"/api/v1/categories/{level3_id}/tags",
            json={
                "name": f"测试{tag_type}",
                "tag_type": tag_type,
                "description": f"测试{tag_type}描述"
            }
        )
        assert response.status_code == 200
        print(f"   ✓ {tag_type} 类型有效")
    
    # 5. 测试：更新不存在的标签
    print("\n4. 测试：更新不存在的标签")
    update_invalid = client.put(
        "/api/v1/tags/invalid_tag_id",
        json={"name": "新名称"}
    )
    assert update_invalid.status_code == 404
    print("   ✓ 更新不存在的标签返回404")
    
    # 6. 测试：删除不存在的标签
    print("\n5. 测试：删除不存在的标签")
    delete_invalid = client.delete("/api/v1/tags/invalid_tag_id")
    assert delete_invalid.status_code == 404
    print("   ✓ 删除不存在的标签返回404")
    
    print("\n✅ 所有验证测试通过！")


if __name__ == "__main__":
    print("=" * 60)
    print("测试分类标签管理API端点")
    print("=" * 60)
    
    try:
        test_tag_management_workflow()
        test_tag_validation()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试成功完成！")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
