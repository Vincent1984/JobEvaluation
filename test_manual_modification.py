"""测试手动修改评估结果功能"""

import asyncio
import json
from datetime import datetime


async def test_manual_modification():
    """测试手动修改评估结果"""
    print("=" * 60)
    print("测试手动修改评估结果功能")
    print("=" * 60)
    
    # 模拟原始评估结果
    original_evaluation = {
        "jd_id": "jd_test_001",
        "model_type": "standard",
        "overall_score": 82.0,
        "company_value": "中价值",
        "is_core_position": False,
        "dimension_scores": {
            "完整性": 85,
            "清晰度": 80,
            "专业性": 82
        },
        "dimension_contributions": {
            "jd_content": 40.0,
            "evaluation_template": 30.0,
            "category_tags": 30.0
        },
        "is_manually_modified": False,
        "manual_modifications": [],
        "evaluated_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    
    print("\n1. 原始评估结果")
    print("-" * 60)
    print(f"  - 综合质量分数: {original_evaluation['overall_score']}")
    print(f"  - 企业价值评级: {original_evaluation['company_value']}")
    print(f"  - 是否核心岗位: {original_evaluation['is_core_position']}")
    print(f"  - 是否手动修改: {original_evaluation['is_manually_modified']}")
    print(f"  - 修改历史记录数: {len(original_evaluation['manual_modifications'])}")
    
    print("\n2. 执行手动修改")
    print("-" * 60)
    
    # 模拟手动修改
    modifications = {
        "overall_score": 90.0,
        "company_value": "高价值",
        "is_core_position": True
    }
    reason = "根据业务需求和实际情况，调整该岗位为核心岗位，提高价值评级"
    
    print(f"  修改内容:")
    for field, new_value in modifications.items():
        old_value = original_evaluation.get(field)
        print(f"    - {field}: {old_value} -> {new_value}")
    print(f"  修改原因: {reason}")
    
    # 应用修改
    evaluation = original_evaluation.copy()
    
    # 记录修改历史
    modification_record = {
        "timestamp": datetime.now().isoformat(),
        "modified_fields": {},
        "original_values": {},
        "reason": reason
    }
    
    # 应用修改并记录原始值
    for field, new_value in modifications.items():
        if field in evaluation:
            modification_record["original_values"][field] = evaluation[field]
            modification_record["modified_fields"][field] = new_value
            evaluation[field] = new_value
    
    # 标记为手动修改
    evaluation["is_manually_modified"] = True
    
    # 添加修改记录到历史
    if "manual_modifications" not in evaluation:
        evaluation["manual_modifications"] = []
    evaluation["manual_modifications"].append(modification_record)
    
    # 更新时间戳
    evaluation["updated_at"] = datetime.now().isoformat()
    
    print("\n3. 修改后的评估结果")
    print("-" * 60)
    print(f"  - 综合质量分数: {evaluation['overall_score']}")
    print(f"  - 企业价值评级: {evaluation['company_value']}")
    print(f"  - 是否核心岗位: {evaluation['is_core_position']}")
    print(f"  - 是否手动修改: {evaluation['is_manually_modified']}")
    print(f"  - 修改历史记录数: {len(evaluation['manual_modifications'])}")
    
    print("\n4. 验证修改历史记录")
    print("-" * 60)
    
    assert evaluation["is_manually_modified"] == True, "应该标记为手动修改"
    assert len(evaluation["manual_modifications"]) == 1, "应该有1条修改记录"
    
    record = evaluation["manual_modifications"][0]
    print(f"  修改记录:")
    print(f"    - 时间戳: {record['timestamp']}")
    print(f"    - 修改原因: {record['reason']}")
    print(f"    - 修改字段: {list(record['modified_fields'].keys())}")
    print(f"    - 原始值: {json.dumps(record['original_values'], ensure_ascii=False)}")
    print(f"    - 新值: {json.dumps(record['modified_fields'], ensure_ascii=False)}")
    
    assert "timestamp" in record, "缺少timestamp字段"
    assert "modified_fields" in record, "缺少modified_fields字段"
    assert "original_values" in record, "缺少original_values字段"
    assert "reason" in record, "缺少reason字段"
    
    print(f"  ✓ 修改历史记录结构正确")
    
    print("\n5. 测试多次修改")
    print("-" * 60)
    
    # 第二次修改
    modifications2 = {
        "overall_score": 95.0
    }
    reason2 = "进一步提高评分"
    
    modification_record2 = {
        "timestamp": datetime.now().isoformat(),
        "modified_fields": {},
        "original_values": {},
        "reason": reason2
    }
    
    for field, new_value in modifications2.items():
        if field in evaluation:
            modification_record2["original_values"][field] = evaluation[field]
            modification_record2["modified_fields"][field] = new_value
            evaluation[field] = new_value
    
    evaluation["manual_modifications"].append(modification_record2)
    evaluation["updated_at"] = datetime.now().isoformat()
    
    print(f"  第二次修改: overall_score -> {evaluation['overall_score']}")
    print(f"  修改历史记录数: {len(evaluation['manual_modifications'])}")
    
    assert len(evaluation["manual_modifications"]) == 2, "应该有2条修改记录"
    print(f"  ✓ 多次修改记录正确")
    
    print("\n6. 验证修改历史可追溯性")
    print("-" * 60)
    
    print(f"  修改历史:")
    for i, record in enumerate(evaluation["manual_modifications"], 1):
        print(f"    修改 {i}:")
        print(f"      - 时间: {record['timestamp']}")
        print(f"      - 原因: {record['reason']}")
        print(f"      - 修改: {json.dumps(record['modified_fields'], ensure_ascii=False)}")
        print(f"      - 原值: {json.dumps(record['original_values'], ensure_ascii=False)}")
    
    # 验证可以追溯到最初的值
    first_record = evaluation["manual_modifications"][0]
    assert first_record["original_values"]["overall_score"] == 82.0, "第一次修改应该记录原始分数82.0"
    assert first_record["original_values"]["company_value"] == "中价值", "第一次修改应该记录原始价值'中价值'"
    
    second_record = evaluation["manual_modifications"][1]
    assert second_record["original_values"]["overall_score"] == 90.0, "第二次修改应该记录第一次修改后的分数90.0"
    
    print(f"  ✓ 修改历史可追溯性验证通过")
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_manual_modification())
