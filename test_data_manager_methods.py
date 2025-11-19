"""测试DataManagerAgent的方法实现（不需要Redis）"""

import sys
import inspect
from src.agents.data_manager_agent import DataManagerAgent


def test_methods_exist():
    """测试所有必需的方法是否存在"""
    print("=== 测试DataManagerAgent方法是否存在 ===\n")
    
    required_methods = [
        # 企业管理
        "handle_save_company",
        "handle_get_company",
        "handle_get_all_companies",
        "handle_delete_company",
        
        # 分类标签管理
        "handle_save_category_tag",
        "handle_get_category_tags",
        "handle_delete_category_tag",
        
        # 分类管理
        "handle_get_company_categories",
        
        # JD和评估（更新的）
        "handle_get_jd",
        "handle_save_evaluation",
        "handle_get_evaluation",
    ]
    
    all_passed = True
    
    for method_name in required_methods:
        if hasattr(DataManagerAgent, method_name):
            method = getattr(DataManagerAgent, method_name)
            if callable(method):
                # 检查是否是async方法
                is_async = inspect.iscoroutinefunction(method)
                status = "✓ PASS (async)" if is_async else "✓ PASS (sync)"
                print(f"{status} - {method_name}")
            else:
                print(f"✗ FAIL - {method_name} 不是可调用的方法")
                all_passed = False
        else:
            print(f"✗ FAIL - {method_name} 不存在")
            all_passed = False
    
    return all_passed


def test_handler_registration():
    """测试处理器是否正确注册"""
    print("\n=== 测试处理器注册 ===\n")
    
    # 检查__init__方法中的register_handler调用
    init_source = inspect.getsource(DataManagerAgent.__init__)
    
    required_handlers = [
        "save_company",
        "get_company",
        "get_all_companies",
        "delete_company",
        "save_category_tag",
        "get_category_tags",
        "delete_category_tag",
        "get_company_categories",
    ]
    
    all_registered = True
    
    for handler in required_handlers:
        if f'register_handler("{handler}"' in init_source:
            print(f"✓ PASS - {handler} 已注册")
        else:
            print(f"✗ FAIL - {handler} 未注册")
            all_registered = False
    
    return all_registered


def test_method_signatures():
    """测试方法签名是否正确"""
    print("\n=== 测试方法签名 ===\n")
    
    methods_to_check = {
        "handle_save_company": ["self", "message"],
        "handle_get_company": ["self", "message"],
        "handle_get_all_companies": ["self", "message"],
        "handle_delete_company": ["self", "message"],
        "handle_save_category_tag": ["self", "message"],
        "handle_get_category_tags": ["self", "message"],
        "handle_delete_category_tag": ["self", "message"],
        "handle_get_company_categories": ["self", "message"],
    }
    
    all_correct = True
    
    for method_name, expected_params in methods_to_check.items():
        if hasattr(DataManagerAgent, method_name):
            method = getattr(DataManagerAgent, method_name)
            sig = inspect.signature(method)
            actual_params = list(sig.parameters.keys())
            
            if actual_params == expected_params:
                print(f"✓ PASS - {method_name} 签名正确: {actual_params}")
            else:
                print(f"✗ FAIL - {method_name} 签名不正确")
                print(f"  期望: {expected_params}")
                print(f"  实际: {actual_params}")
                all_correct = False
        else:
            print(f"✗ FAIL - {method_name} 不存在")
            all_correct = False
    
    return all_correct


def test_imports():
    """测试必要的导入是否存在"""
    print("\n=== 测试导入 ===\n")
    
    import src.agents.data_manager_agent as module
    
    required_imports = [
        "CompanyDB",
        "CategoryTagDB",
        "JobCategoryDB",
        "EvaluationResultDB",
        "CategoryRepository",
    ]
    
    all_imported = True
    
    for import_name in required_imports:
        if hasattr(module, import_name):
            print(f"✓ PASS - {import_name} 已导入")
        else:
            print(f"✗ FAIL - {import_name} 未导入")
            all_imported = False
    
    return all_imported


def test_docstrings():
    """测试方法是否有文档字符串"""
    print("\n=== 测试文档字符串 ===\n")
    
    methods_to_check = [
        "handle_save_company",
        "handle_get_company",
        "handle_get_all_companies",
        "handle_delete_company",
        "handle_save_category_tag",
        "handle_get_category_tags",
        "handle_delete_category_tag",
        "handle_get_company_categories",
    ]
    
    all_documented = True
    
    for method_name in methods_to_check:
        if hasattr(DataManagerAgent, method_name):
            method = getattr(DataManagerAgent, method_name)
            if method.__doc__:
                doc = method.__doc__.strip()
                print(f"✓ PASS - {method_name}: {doc[:50]}...")
            else:
                print(f"✗ FAIL - {method_name} 缺少文档字符串")
                all_documented = False
        else:
            print(f"✗ FAIL - {method_name} 不存在")
            all_documented = False
    
    return all_documented


def main():
    """运行所有测试"""
    print("开始测试DataManagerAgent增强功能...\n")
    print("="*60)
    
    results = []
    
    # 运行测试
    results.append(("方法存在性", test_methods_exist()))
    results.append(("处理器注册", test_handler_registration()))
    results.append(("方法签名", test_method_signatures()))
    results.append(("导入检查", test_imports()))
    results.append(("文档字符串", test_docstrings()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总:")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✓ 所有测试通过！DataManagerAgent增强功能实现正确。")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查实现。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
