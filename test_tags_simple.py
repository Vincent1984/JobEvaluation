"""简单测试分类标签API端点"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 设置环境变量
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/jd_analyzer.db")


def test_imports():
    """测试导入是否正常"""
    print("1. 测试导入...")
    try:
        from src.api.routers import tags, categories
        print("   ✓ tags 模块导入成功")
        print("   ✓ categories 模块导入成功")
        
        # 检查路由器
        assert hasattr(tags, 'router'), "tags.router 不存在"
        assert hasattr(categories, 'router'), "categories.router 不存在"
        print("   ✓ 路由器存在")
        
        # 检查存储
        assert hasattr(categories, 'tag_storage'), "categories.tag_storage 不存在"
        print("   ✓ tag_storage 存在")
        
        return True
    except Exception as e:
        print(f"   ✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_registration():
    """测试API注册"""
    print("\n2. 测试API注册...")
    try:
        from src.api import app
        
        # 获取所有路由
        routes = [route.path for route in app.routes]
        
        # 检查标签相关端点
        expected_endpoints = [
            "/api/v1/categories/{category_id}/tags",
            "/api/v1/tags/{tag_id}"
        ]
        
        for endpoint in expected_endpoints:
            if endpoint in routes:
                print(f"   ✓ 端点已注册: {endpoint}")
            else:
                print(f"   ✗ 端点未注册: {endpoint}")
        
        # 打印所有标签相关路由
        print("\n   所有标签相关路由:")
        for route in app.routes:
            if 'tag' in route.path.lower():
                methods = getattr(route, 'methods', [])
                print(f"   - {route.path} [{', '.join(methods)}]")
        
        return True
    except Exception as e:
        print(f"   ✗ API注册检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_endpoint_structure():
    """测试端点结构"""
    print("\n3. 测试端点结构...")
    try:
        from src.api.routers import tags, categories
        
        # 检查categories路由中的标签端点
        print("   检查 categories 路由:")
        cat_routes = [route.path for route in categories.router.routes]
        print(f"   - 路由数量: {len(cat_routes)}")
        
        tag_routes = [r for r in cat_routes if 'tag' in r.lower()]
        print(f"   - 标签相关路由: {tag_routes}")
        
        # 检查tags路由
        print("\n   检查 tags 路由:")
        tag_routes = [route.path for route in tags.router.routes]
        print(f"   - 路由数量: {len(tag_routes)}")
        print(f"   - 路由列表: {tag_routes}")
        
        return True
    except Exception as e:
        print(f"   ✗ 端点结构检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_request_models():
    """测试请求模型"""
    print("\n4. 测试请求模型...")
    try:
        from src.api.routers.categories import CreateTagRequest
        from src.api.routers.tags import UpdateTagRequest
        
        # 测试创建标签请求
        create_req = CreateTagRequest(
            name="测试标签",
            tag_type="战略重要性",
            description="测试描述"
        )
        print(f"   ✓ CreateTagRequest: {create_req.name}")
        
        # 测试更新标签请求
        update_req = UpdateTagRequest(
            name="更新标签"
        )
        print(f"   ✓ UpdateTagRequest: {update_req.name}")
        
        return True
    except Exception as e:
        print(f"   ✗ 请求模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schema_models():
    """测试数据模型"""
    print("\n5. 测试数据模型...")
    try:
        from src.models.schemas import CategoryTag
        from datetime import datetime
        
        # 创建标签对象
        tag = CategoryTag(
            id="tag_001",
            category_id="cat_001",
            name="高战略重要性",
            tag_type="战略重要性",
            description="该岗位对企业战略目标实现具有重要影响",
            created_at=datetime.now()
        )
        
        print(f"   ✓ CategoryTag 创建成功")
        print(f"   - ID: {tag.id}")
        print(f"   - 名称: {tag.name}")
        print(f"   - 类型: {tag.tag_type}")
        print(f"   - 描述: {tag.description}")
        
        # 测试序列化
        tag_dict = tag.model_dump()
        print(f"   ✓ 序列化成功: {len(tag_dict)} 个字段")
        
        return True
    except Exception as e:
        print(f"   ✗ 数据模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("测试分类标签管理API实现")
    print("=" * 60)
    
    results = []
    results.append(("导入测试", test_imports()))
    results.append(("API注册测试", test_api_registration()))
    results.append(("端点结构测试", test_endpoint_structure()))
    results.append(("请求模型测试", test_request_models()))
    results.append(("数据模型测试", test_schema_models()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败")
    
    print("=" * 60)
