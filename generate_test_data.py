"""生成企业管理和职位分类管理的测试数据"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000/api/v1"


def create_company(name):
    """创建企业"""
    response = requests.post(
        f"{API_BASE_URL}/companies",
        json={"name": name}
    )
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return result["data"]["id"]
    return None


def create_category(company_id, name, level, parent_id=None, description=None, sample_jd_ids=None):
    """创建分类"""
    data = {
        "company_id": company_id,
        "name": name,
        "level": level,
        "parent_id": parent_id,
        "description": description,
        "sample_jd_ids": sample_jd_ids or []
    }
    
    response = requests.post(
        f"{API_BASE_URL}/companies/{company_id}/categories",
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return result["data"]["id"]
    return None


def create_tag(category_id, name, tag_type, description):
    """创建标签"""
    data = {
        "name": name,
        "tag_type": tag_type,
        "description": description
    }
    
    response = requests.post(
        f"{API_BASE_URL}/categories/{category_id}/tags",
        json=data
    )
    
    return response.status_code == 200 and response.json().get("success")


def generate_test_data():
    """生成完整的测试数据"""
    
    print("=" * 60)
    print("生成企业管理和职位分类管理测试数据")
    print("=" * 60)
    print()
    
    # 1. 创建企业
    print("📊 创建企业...")
    companies = [
        "科技创新有限公司",
        "互联网科技集团",
        "数字化转型咨询公司"
    ]
    
    company_ids = {}
    for company_name in companies:
        company_id = create_company(company_name)
        if company_id:
            company_ids[company_name] = company_id
            print(f"   ✅ {company_name}: {company_id}")
        else:
            print(f"   ❌ {company_name}: 创建失败")
    
    print()
    
    # 2. 为第一个企业创建完整的分类体系
    if companies[0] in company_ids:
        company_id = company_ids[companies[0]]
        print(f"📁 为 {companies[0]} 创建分类体系...")
        
        # 第一层级：技术类
        tech_id = create_category(
            company_id,
            "技术类",
            1,
            description="技术相关岗位"
        )
        print(f"   ✅ L1: 技术类 ({tech_id})")
        
        # 第二层级：研发工程师
        dev_id = create_category(
            company_id,
            "研发工程师",
            2,
            parent_id=tech_id,
            description="软件研发相关岗位"
        )
        print(f"      ✅ L2: 研发工程师 ({dev_id})")
        
        # 第三层级：Python后端工程师
        python_id = create_category(
            company_id,
            "Python后端工程师",
            3,
            parent_id=dev_id,
            description="Python后端开发岗位",
            sample_jd_ids=["jd_python_001"]
        )
        print(f"         ✅ L3: Python后端工程师 ({python_id})")
        
        # 为Python后端工程师添加标签
        if python_id:
            tags = [
                ("高战略重要性", "战略重要性", "该岗位对企业战略目标实现具有重要影响，是核心技术团队的关键成员"),
                ("高技能稀缺性", "技能稀缺性", "Python后端开发人才在市场上较为稀缺，尤其是有大型项目经验的高级工程师"),
                ("高业务价值", "业务价值", "直接参与核心业务系统开发，对业务增长有直接贡献")
            ]
            
            for tag_name, tag_type, tag_desc in tags:
                if create_tag(python_id, tag_name, tag_type, tag_desc):
                    print(f"            🏷️ {tag_name}")
        
        # 第三层级：Java后端工程师
        java_id = create_category(
            company_id,
            "Java后端工程师",
            3,
            parent_id=dev_id,
            description="Java后端开发岗位",
            sample_jd_ids=["jd_java_001", "jd_java_002"]
        )
        print(f"         ✅ L3: Java后端工程师 ({java_id})")
        
        # 为Java后端工程师添加标签
        if java_id:
            tags = [
                ("中战略重要性", "战略重要性", "支持企业级应用开发，重要但非核心"),
                ("中技能稀缺性", "技能稀缺性", "Java开发人才市场供应相对充足")
            ]
            
            for tag_name, tag_type, tag_desc in tags:
                if create_tag(java_id, tag_name, tag_type, tag_desc):
                    print(f"            🏷️ {tag_name}")
        
        # 第三层级：前端工程师
        frontend_id = create_category(
            company_id,
            "前端工程师",
            3,
            parent_id=dev_id,
            description="前端开发岗位",
            sample_jd_ids=["jd_frontend_001"]
        )
        print(f"         ✅ L3: 前端工程师 ({frontend_id})")
        
        # 第二层级：测试工程师
        test_id = create_category(
            company_id,
            "测试工程师",
            2,
            parent_id=tech_id,
            description="软件测试相关岗位"
        )
        print(f"      ✅ L2: 测试工程师 ({test_id})")
        
        # 第三层级：自动化测试工程师
        auto_test_id = create_category(
            company_id,
            "自动化测试工程师",
            3,
            parent_id=test_id,
            description="自动化测试开发岗位"
        )
        print(f"         ✅ L3: 自动化测试工程师 ({auto_test_id})")
        
        # 第一层级：业务类
        business_id = create_category(
            company_id,
            "业务类",
            1,
            description="业务相关岗位"
        )
        print(f"   ✅ L1: 业务类 ({business_id})")
        
        # 第二层级：产品经理
        pm_id = create_category(
            company_id,
            "产品经理",
            2,
            parent_id=business_id,
            description="产品管理相关岗位"
        )
        print(f"      ✅ L2: 产品经理 ({pm_id})")
        
        # 第三层级：高级产品经理
        senior_pm_id = create_category(
            company_id,
            "高级产品经理",
            3,
            parent_id=pm_id,
            description="高级产品管理岗位"
        )
        print(f"         ✅ L3: 高级产品经理 ({senior_pm_id})")
        
        # 为高级产品经理添加标签
        if senior_pm_id:
            tags = [
                ("高战略重要性", "战略重要性", "负责核心产品规划，对公司战略有重要影响"),
                ("高发展潜力", "发展潜力", "产品经理岗位有很大的职业发展空间")
            ]
            
            for tag_name, tag_type, tag_desc in tags:
                if create_tag(senior_pm_id, tag_name, tag_type, tag_desc):
                    print(f"            🏷️ {tag_name}")
        
        # 第二层级：运营专员
        ops_id = create_category(
            company_id,
            "运营专员",
            2,
            parent_id=business_id,
            description="运营相关岗位"
        )
        print(f"      ✅ L2: 运营专员 ({ops_id})")
        
        # 第三层级：用户运营
        user_ops_id = create_category(
            company_id,
            "用户运营",
            3,
            parent_id=ops_id,
            description="用户运营岗位"
        )
        print(f"         ✅ L3: 用户运营 ({user_ops_id})")
        
        # 第一层级：管理类
        mgmt_id = create_category(
            company_id,
            "管理类",
            1,
            description="管理相关岗位"
        )
        print(f"   ✅ L1: 管理类 ({mgmt_id})")
        
        # 第二层级：项目经理
        proj_mgr_id = create_category(
            company_id,
            "项目经理",
            2,
            parent_id=mgmt_id,
            description="项目管理岗位"
        )
        print(f"      ✅ L2: 项目经理 ({proj_mgr_id})")
        
        # 第三层级：技术项目经理
        tech_pm_id = create_category(
            company_id,
            "技术项目经理",
            3,
            parent_id=proj_mgr_id,
            description="技术项目管理岗位"
        )
        print(f"         ✅ L3: 技术项目经理 ({tech_pm_id})")
    
    print()
    
    # 3. 为第二个企业创建简单的分类体系
    if len(companies) > 1 and companies[1] in company_ids:
        company_id = company_ids[companies[1]]
        print(f"📁 为 {companies[1]} 创建分类体系...")
        
        # 第一层级：技术部
        tech_dept_id = create_category(
            company_id,
            "技术部",
            1,
            description="技术部门岗位"
        )
        print(f"   ✅ L1: 技术部 ({tech_dept_id})")
        
        # 第二层级：开发团队
        dev_team_id = create_category(
            company_id,
            "开发团队",
            2,
            parent_id=tech_dept_id,
            description="开发团队岗位"
        )
        print(f"      ✅ L2: 开发团队 ({dev_team_id})")
        
        # 第三层级：全栈工程师
        fullstack_id = create_category(
            company_id,
            "全栈工程师",
            3,
            parent_id=dev_team_id,
            description="全栈开发岗位"
        )
        print(f"         ✅ L3: 全栈工程师 ({fullstack_id})")
        
        # 为全栈工程师添加标签
        if fullstack_id:
            tags = [
                ("高技能稀缺性", "技能稀缺性", "全栈工程师需要掌握前后端技术，人才较为稀缺"),
                ("高市场竞争度", "市场竞争度", "全栈工程师在市场上竞争激烈")
            ]
            
            for tag_name, tag_type, tag_desc in tags:
                if create_tag(fullstack_id, tag_name, tag_type, tag_desc):
                    print(f"            🏷️ {tag_name}")
    
    print()
    print("=" * 60)
    print("✅ 测试数据生成完成！")
    print("=" * 60)
    print()
    print("📊 数据统计:")
    print(f"   - 企业数量: {len(company_ids)}")
    print(f"   - 第一个企业: 完整的三层级分类体系（3个一级，5个二级，8个三级）")
    print(f"   - 第二个企业: 简单的分类体系（1个一级，1个二级，1个三级）")
    print(f"   - 标签: 多个第三层级分类包含标签")
    print()
    print("🎯 现在可以在UI中查看和管理这些数据！")
    print("   - 企业管理: http://localhost:8501 → 企业管理")
    print("   - 职位分类管理: http://localhost:8501 → 职位分类管理")


if __name__ == "__main__":
    try:
        generate_test_data()
    except Exception as e:
        print(f"\n❌ 生成测试数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
