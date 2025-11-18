"""简单的FastAPI端点测试（不需要LLM）"""

import sys
import asyncio

# Windows平台asyncio修复
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.api import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["version"] == "1.0.0"
    print("✓ 根路径测试通过")


def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ 健康检查测试通过")


def test_categories_crud():
    """测试职位分类CRUD"""
    # 创建一级分类
    response = client.post(
        "/api/v1/categories",
        json={
            "name": "技术类",
            "level": 1,
            "description": "技术相关岗位"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    cat1_id = data["data"]["id"]
    print(f"✓ 创建一级分类测试通过 - ID: {cat1_id}")
    
    # 创建二级分类
    response = client.post(
        "/api/v1/categories",
        json={
            "name": "研发",
            "level": 2,
            "parent_id": cat1_id,
            "description": "研发岗位"
        }
    )
    assert response.status_code == 200
    cat2_id = response.json()["data"]["id"]
    print(f"✓ 创建二级分类测试通过 - ID: {cat2_id}")
    
    # 创建三级分类
    response = client.post(
        "/api/v1/categories",
        json={
            "name": "后端工程师",
            "level": 3,
            "parent_id": cat2_id,
            "sample_jd_ids": []
        }
    )
    assert response.status_code == 200
    cat3_id = response.json()["data"]["id"]
    print(f"✓ 创建三级分类测试通过 - ID: {cat3_id}")
    
    # 列出所有分类
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    print(f"✓ 列出分类测试通过 - 共{data['total']}个分类")
    
    # 获取分类树
    response = client.get("/api/v1/categories/tree")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1
    print(f"✓ 获取分类树测试通过")
    
    # 获取单个分类
    response = client.get(f"/api/v1/categories/{cat3_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "后端工程师"
    print(f"✓ 获取分类详情测试通过")
    
    # 更新分类
    response = client.put(
        f"/api/v1/categories/{cat3_id}",
        json={"description": "负责后端系统开发"}
    )
    assert response.status_code == 200
    print(f"✓ 更新分类测试通过")
    
    # 更新样本JD（应该成功，因为是第三层级）
    response = client.put(
        f"/api/v1/categories/{cat3_id}/samples",
        json={"sample_jd_ids": ["jd_001"]}
    )
    assert response.status_code == 200
    print(f"✓ 更新样本JD测试通过")
    
    # 尝试为非第三层级添加样本JD（应该失败）
    response = client.put(
        f"/api/v1/categories/{cat2_id}/samples",
        json={"sample_jd_ids": ["jd_001"]}
    )
    assert response.status_code == 400
    print(f"✓ 样本JD层级验证测试通过")
    
    # 删除分类（有子分类应该失败）
    response = client.delete(f"/api/v1/categories/{cat2_id}")
    assert response.status_code == 400
    print(f"✓ 删除分类验证测试通过")
    
    # 删除叶子分类（应该成功）
    response = client.delete(f"/api/v1/categories/{cat3_id}")
    assert response.status_code == 200
    print(f"✓ 删除叶子分类测试通过")
    
    return cat1_id, cat2_id


def test_templates_crud():
    """测试模板CRUD"""
    # 列出默认模板
    response = client.get("/api/v1/templates")
    assert response.status_code == 200
    data = response.json()
    initial_count = data["total"]
    print(f"✓ 列出模板测试通过 - 共{initial_count}个默认模板")
    
    # 创建解析模板
    response = client.post(
        "/api/v1/templates",
        json={
            "name": "销售岗位解析模板",
            "template_type": "parsing",
            "config": {
                "custom_fields": ["销售目标", "客户类型", "提成方案"]
            }
        }
    )
    assert response.status_code == 200
    template_id = response.json()["data"]["id"]
    print(f"✓ 创建模板测试通过 - ID: {template_id}")
    
    # 获取模板
    response = client.get(f"/api/v1/templates/{template_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "销售岗位解析模板"
    print(f"✓ 获取模板详情测试通过")
    
    # 更新模板
    response = client.put(
        f"/api/v1/templates/{template_id}",
        json={
            "name": "销售岗位解析模板V2",
            "config": {
                "custom_fields": ["销售目标", "客户类型", "提成方案", "团队规模"]
            }
        }
    )
    assert response.status_code == 200
    print(f"✓ 更新模板测试通过")
    
    # 按类型筛选
    response = client.get("/api/v1/templates?template_type=parsing")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2  # 至少有默认的和新创建的
    print(f"✓ 按类型筛选模板测试通过")
    
    # 删除模板
    response = client.delete(f"/api/v1/templates/{template_id}")
    assert response.status_code == 200
    print(f"✓ 删除模板测试通过")
    
    # 验证删除
    response = client.get(f"/api/v1/templates/{template_id}")
    assert response.status_code == 404
    print(f"✓ 验证删除测试通过")


def test_api_structure():
    """测试API结构"""
    # 测试所有路由是否正确注册
    routes = [route.path for route in app.routes]
    
    expected_routes = [
        "/",
        "/health",
        "/api/v1/jd/analyze",
        "/api/v1/jd/parse",
        "/api/v1/jd/{jd_id}",
        "/api/v1/jd/{jd_id}/evaluation",
        "/api/v1/jd/{jd_id}/category",
        "/api/v1/jd/upload",
        "/api/v1/categories",
        "/api/v1/categories/tree",
        "/api/v1/categories/{category_id}",
        "/api/v1/categories/{category_id}/samples",
        "/api/v1/questionnaire/generate",
        "/api/v1/questionnaire/{questionnaire_id}",
        "/api/v1/questionnaire/{questionnaire_id}/submit",
        "/api/v1/match/{match_id}",
        "/api/v1/match/{match_id}/report",
        "/api/v1/match/jd/{jd_id}/matches",
        "/api/v1/templates",
        "/api/v1/templates/{template_id}",
        "/api/v1/batch/upload",
        "/api/v1/batch/status/{batch_id}",
        "/api/v1/batch/results/{batch_id}",
        "/api/v1/batch/analyze",
        "/api/v1/batch/match"
    ]
    
    for expected in expected_routes:
        assert expected in routes, f"路由 {expected} 未找到"
    
    print(f"✓ API结构测试通过 - 所有{len(expected_routes)}个端点已注册")


def run_all_tests():
    """运行所有测试"""
    print("\n=== 开始测试FastAPI端点 ===\n")
    
    try:
        # 基础测试
        test_root()
        test_health_check()
        
        # API结构测试
        test_api_structure()
        
        # 分类管理测试
        test_categories_crud()
        
        # 模板管理测试
        test_templates_crud()
        
        print("\n=== ✓ 所有测试通过！===\n")
        print("注意：需要LLM的端点（JD分析、问卷生成等）需要配置DeepSeek API才能测试")
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}\n")
        raise
    except Exception as e:
        print(f"\n✗ 测试出错: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
