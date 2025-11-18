"""测试FastAPI端点"""

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
    print("✓ 根路径测试通过")


def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ 健康检查测试通过")


def test_jd_parse():
    """测试JD解析"""
    jd_text = """
    招聘高级Python工程师
    
    岗位职责：
    1. 负责后端服务开发
    2. 优化系统性能
    
    任职要求：
    - 3年以上Python开发经验
    - 熟悉FastAPI、Django等框架
    - 熟悉MySQL、Redis
    """
    
    response = client.post(
        "/api/v1/jd/parse",
        json={"jd_text": jd_text}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    print(f"✓ JD解析测试通过 - 职位: {data['data']['job_title']}")
    return data["data"]["id"]


def test_jd_analyze():
    """测试完整JD分析"""
    jd_text = """
    招聘前端工程师
    
    岗位职责：
    1. 负责前端页面开发
    2. 优化用户体验
    
    任职要求：
    - 2年以上前端开发经验
    - 熟悉React、Vue
    """
    
    response = client.post(
        "/api/v1/jd/analyze",
        json={"jd_text": jd_text, "model_type": "standard"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "jd" in data["data"]
    assert "evaluation" in data["data"]
    print(f"✓ JD分析测试通过 - 质量分数: {data['data']['evaluation']['quality_score']['overall_score']:.1f}")
    return data["data"]["jd"]["id"]


def test_get_jd(jd_id: str):
    """测试获取JD详情"""
    response = client.get(f"/api/v1/jd/{jd_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"✓ 获取JD详情测试通过")


def test_update_jd_category(jd_id: str):
    """测试更新JD分类"""
    response = client.put(
        f"/api/v1/jd/{jd_id}/category",
        json={
            "category_level1_id": "cat_tech",
            "category_level2_id": "cat_dev",
            "category_level3_id": "cat_backend"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"✓ 更新JD分类测试通过")


def test_categories():
    """测试职位分类管理"""
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
    cat1_id = response.json()["data"]["id"]
    print(f"✓ 创建一级分类测试通过")
    
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
    print(f"✓ 创建二级分类测试通过")
    
    # 创建三级分类（带样本JD）
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
    print(f"✓ 创建三级分类测试通过")
    
    # 获取分类树
    response = client.get("/api/v1/categories/tree")
    assert response.status_code == 200
    print(f"✓ 获取分类树测试通过")
    
    return cat3_id


def test_templates():
    """测试模板管理"""
    # 列出模板
    response = client.get("/api/v1/templates")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"✓ 列出模板测试通过 - 共{data['total']}个模板")
    
    # 创建模板
    response = client.post(
        "/api/v1/templates",
        json={
            "name": "测试模板",
            "template_type": "parsing",
            "config": {"custom_fields": ["field1", "field2"]}
        }
    )
    assert response.status_code == 200
    template_id = response.json()["data"]["id"]
    print(f"✓ 创建模板测试通过")
    
    # 更新模板
    response = client.put(
        f"/api/v1/templates/{template_id}",
        json={"name": "更新后的模板"}
    )
    assert response.status_code == 200
    print(f"✓ 更新模板测试通过")
    
    return template_id


def test_questionnaire(jd_id: str):
    """测试问卷管理"""
    # 生成问卷
    response = client.post(
        "/api/v1/questionnaire/generate",
        json={
            "jd_id": jd_id,
            "evaluation_model": "standard"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    questionnaire_id = data["data"]["id"]
    print(f"✓ 生成问卷测试通过 - 共{len(data['data']['questions'])}个问题")
    
    # 获取问卷
    response = client.get(f"/api/v1/questionnaire/{questionnaire_id}")
    assert response.status_code == 200
    print(f"✓ 获取问卷测试通过")
    
    return questionnaire_id


def test_batch_analyze():
    """测试批量分析"""
    jd_texts = [
        "招聘Java工程师，要求3年经验",
        "招聘产品经理，要求5年经验",
        "招聘UI设计师，要求熟悉Figma"
    ]
    
    response = client.post(
        "/api/v1/batch/analyze",
        json={
            "jd_texts": jd_texts,
            "model_type": "standard"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"✓ 批量分析测试通过 - 成功{data['data']['summary']['successful']}个")


def run_all_tests():
    """运行所有测试"""
    print("\n=== 开始测试FastAPI端点 ===\n")
    
    try:
        # 基础测试
        test_root()
        test_health_check()
        
        # JD分析测试
        jd_id = test_jd_parse()
        jd_id2 = test_jd_analyze()
        test_get_jd(jd_id2)
        test_update_jd_category(jd_id2)
        
        # 分类管理测试
        cat_id = test_categories()
        
        # 模板管理测试
        template_id = test_templates()
        
        # 问卷管理测试
        questionnaire_id = test_questionnaire(jd_id2)
        
        # 批量处理测试
        test_batch_analyze()
        
        print("\n=== ✓ 所有测试通过！===\n")
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}\n")
        raise
    except Exception as e:
        print(f"\n✗ 测试出错: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
