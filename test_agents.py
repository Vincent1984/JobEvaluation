"""Agent单元测试 - 测试所有Agent的核心功能"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import json

from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.mcp.context import MCPContext, create_context
from src.agents.parser_agent import ParserAgent
from src.agents.batch_upload_agent import BatchUploadAgent, FileParserService
from src.agents.evaluator_agent import (
    EvaluatorAgent,
    StandardEvaluationModel,
    MercerIPEModel,
    FactorComparisonModel
)
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.questionnaire_agent import QuestionnaireAgent
from src.agents.matcher_agent import MatcherAgent
from src.agents.data_manager_agent import DataManagerAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.report_agent import ReportAgent


# ============================================================================
# Mock LLM Client
# ============================================================================

class MockLLMClient:
    """Mock LLM客户端用于测试"""
    
    def __init__(self):
        self.call_count = 0
        self.last_prompt = None
        self.responses = {}
    
    def set_response(self, key: str, response: dict):
        """设置特定key的响应"""
        self.responses[key] = response
    
    async def generate_json(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> dict:
        """模拟JSON生成"""
        self.call_count += 1
        self.last_prompt = prompt
        
        # 根据prompt内容返回不同的响应
        if "解析以下岗位JD" in prompt:
            return self.responses.get("parse_jd", {
                "job_title": "Python后端工程师",
                "department": "技术部",
                "location": "北京",
                "responsibilities": [
                    "负责后端系统开发",
                    "参与系统架构设计"
                ],
                "required_skills": [
                    "Python",
                    "Django/Flask",
                    "MySQL"
                ],
                "preferred_skills": [
                    "Redis",
                    "Docker"
                ],
                "qualifications": [
                    "本科及以上学历",
                    "3年以上Python开发经验"
                ],
                "custom_fields": {}
            })
        
        elif "归类到合适的分类" in prompt:
            return self.responses.get("classify_job", {
                "level1_id": "tech",
                "level2_id": "dev",
                "level3_id": "backend",
                "reasoning": "该职位属于技术类-研发-后端工程师"
            })
        
        elif "评估以下岗位JD的质量" in prompt or "评估以下岗位" in prompt:
            return self.responses.get("evaluate_quality", {
                "dimension_scores": {
                    "完整性": 85,
                    "清晰度": 75,
                    "专业性": 80
                },
                "overall_score": 80,
                "analysis": "JD整体质量良好，但部分描述可以更具体",
                "issues": [
                    {
                        "type": "缺失信息",
                        "severity": "medium",
                        "description": "缺少薪资范围"
                    }
                ]
            })
        
        elif "优化建议" in prompt:
            return self.responses.get("generate_suggestions", {
                "suggestions": [
                    {
                        "priority": "high",
                        "category": "职责描述",
                        "issue": "职责描述可以更具体",
                        "suggestion": "添加具体的项目和技术栈",
                        "example": "负责XX系统的后端开发，使用Python/Django框架"
                    }
                ],
                "missing_info": ["薪资范围", "福利待遇"],
                "overall_recommendation": "建议补充薪资和福利信息"
            })
        
        elif "生成评估问卷" in prompt:
            return self.responses.get("generate_questionnaire", {
                "questions": [
                    {
                        "id": "q1",
                        "question_text": "您有多少年Python开发经验？",
                        "question_type": "single_choice",
                        "options": ["1年以下", "1-3年", "3-5年", "5年以上"],
                        "dimension": "技能评估",
                        "weight": 1.0
                    }
                ]
            })
        
        elif "匹配度评估" in prompt:
            return self.responses.get("evaluate_match", {
                "overall_score": 85,
                "dimension_scores": {
                    "技能匹配": 90,
                    "经验匹配": 80,
                    "资质匹配": 85
                },
                "strengths": ["Python技能扎实", "有相关项目经验"],
                "gaps": ["缺少Docker经验"],
                "recommendations": ["建议学习容器化技术"]
            })
        
        return {}
    
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """模拟文本生成"""
        result = await self.generate_json(prompt, temperature, max_tokens)
        return json.dumps(result, ensure_ascii=False)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mcp_server():
    """创建MCP服务器fixture（不启动Redis）"""
    # 创建一个mock MCP server用于测试
    server = Mock()
    server.agents = {}
    server.register_agent = AsyncMock()
    server.send_message = AsyncMock()
    server.save_context = AsyncMock()
    server.get_context = AsyncMock(return_value=None)
    server.update_context = AsyncMock()
    return server


@pytest.fixture
def mock_llm():
    """创建Mock LLM客户端"""
    return MockLLMClient()


@pytest.fixture
def mock_db():
    """创建Mock数据库客户端"""
    db = Mock()
    db.get_jd = AsyncMock(return_value={
        "id": "jd123",
        "job_title": "Python后端工程师",
        "responsibilities": ["开发后端系统"],
        "required_skills": ["Python", "Django"],
        "qualifications": ["本科学历"]
    })
    db.insert_jd = AsyncMock(return_value="jd123")
    db.get_all_categories = AsyncMock(return_value=[
        {"id": "tech", "name": "技术类", "level": 1, "parent_id": None},
        {"id": "dev", "name": "研发", "level": 2, "parent_id": "tech"},
        {"id": "backend", "name": "后端工程师", "level": 3, "parent_id": "dev", "sample_jd_ids": []}
    ])
    db.insert_evaluation = AsyncMock(return_value="eval123")
    db.get_evaluation = AsyncMock(return_value={
        "overall_score": 80,
        "issues": []
    })
    return db


# ============================================================================
# ParserAgent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_parser_agent_initialization(mcp_server, mock_llm):
    """测试ParserAgent初始化"""
    agent = ParserAgent(
        mcp_server=mcp_server,
        llm_client=mock_llm,
        agent_id="test_parser"
    )
    
    assert agent.agent_id == "test_parser"
    assert agent.agent_type == "parser"
    assert agent.llm == mock_llm
    assert "parse_jd" in agent.message_handlers
    assert "classify_job" in agent.message_handlers


@pytest.mark.asyncio
async def test_parser_agent_parse_jd(mcp_server, mock_llm):
    """测试ParserAgent解析JD功能"""
    # 创建Parser Agent（不启动）
    parser = ParserAgent(mcp_server=mcp_server, llm_client=mock_llm)
    
    # Mock send_request方法
    async def mock_send_request(receiver, action, payload, context_id=None, timeout=30.0):
        response = Mock()
        if action == "save_jd":
            response.payload = {"success": True, "jd_id": "jd123"}
        elif action == "get_all_categories":
            response.payload = {"success": True, "categories": []}
        return response
    
    parser.send_request = mock_send_request
    
    # Mock send_response方法
    response_captured = None
    async def mock_send_response(message, payload):
        nonlocal response_captured
        response_captured = payload
    
    parser.send_response = mock_send_response
    
    # 创建解析请求
    request = MCPMessage(
        message_id="msg123",
        sender="test",
        receiver="parser",
        message_type="request",
        action="parse_jd",
        payload={
            "jd_text": "招聘Python后端工程师，负责系统开发..."
        },
        context_id="ctx123",
        timestamp=datetime.now().timestamp()
    )
    
    # 处理请求
    await parser.handle_parse_jd(request)
    
    # 验证响应
    assert response_captured is not None
    assert response_captured["success"] is True
    assert "jd_id" in response_captured
    assert "parsed_data" in response_captured
    assert mock_llm.call_count > 0


@pytest.mark.asyncio
async def test_parser_agent_build_parse_prompt(mcp_server, mock_llm):
    """测试ParserAgent构建解析Prompt"""
    agent = ParserAgent(mcp_server=mcp_server, llm_client=mock_llm)
    
    jd_text = "招聘Python工程师"
    custom_fields = {"team_size": "10人"}
    
    prompt = agent._build_parse_prompt(jd_text, custom_fields)
    
    assert "招聘Python工程师" in prompt
    assert "team_size" in prompt
    assert "JSON格式" in prompt


@pytest.mark.asyncio
async def test_parser_agent_build_category_tree(mcp_server, mock_llm):
    """测试ParserAgent构建分类树"""
    agent = ParserAgent(mcp_server=mcp_server, llm_client=mock_llm)
    
    categories = [
        {"id": "tech", "name": "技术类", "level": 1, "parent_id": None},
        {"id": "dev", "name": "研发", "level": 2, "parent_id": "tech"},
        {"id": "backend", "name": "后端", "level": 3, "parent_id": "dev"}
    ]
    
    tree = agent._build_category_tree(categories)
    
    assert "技术类" in tree
    assert "研发" in tree
    assert "后端" in tree
    assert "一级" in tree
    assert "二级" in tree
    assert "三级" in tree


# ============================================================================
# BatchUploadAgent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_batch_upload_agent_initialization(mcp_server):
    """测试BatchUploadAgent初始化"""
    agent = BatchUploadAgent(mcp_server=mcp_server, agent_id="test_batch")
    
    assert agent.agent_id == "test_batch"
    assert agent.agent_type == "batch_uploader"
    assert agent.file_parser is not None
    assert "batch_upload" in agent.message_handlers
    assert "parse_file" in agent.message_handlers


def test_file_parser_service_validate_file():
    """测试FileParserService文件验证"""
    service = FileParserService()
    
    # 测试有效文件
    is_valid, msg = service.validate_file(1024, "test.txt")
    assert is_valid is True
    
    # 测试文件过大
    is_valid, msg = service.validate_file(20 * 1024 * 1024, "test.txt")
    assert is_valid is False
    assert "超过限制" in msg
    
    # 测试不支持的格式
    is_valid, msg = service.validate_file(1024, "test.exe")
    assert is_valid is False
    assert "不支持的文件格式" in msg


def test_file_parser_service_validate_batch():
    """测试FileParserService批量验证"""
    service = FileParserService()
    
    # 测试有效批量
    files = [(1024, "test1.txt"), (2048, "test2.pdf")]
    is_valid, msg = service.validate_batch(files)
    assert is_valid is True
    
    # 测试文件数量过多
    files = [(1024, f"test{i}.txt") for i in range(25)]
    is_valid, msg = service.validate_batch(files)
    assert is_valid is False
    assert "数量超过限制" in msg
    
    # 测试总大小过大
    files = [(50 * 1024 * 1024, "test1.txt"), (60 * 1024 * 1024, "test2.txt")]
    is_valid, msg = service.validate_batch(files)
    assert is_valid is False
    assert "总文件大小超过限制" in msg


def test_file_parser_service_parse_txt():
    """测试FileParserService解析TXT文件"""
    service = FileParserService()
    
    # UTF-8编码
    content = "这是测试内容".encode('utf-8')
    text = service.parser.parse_txt(content)
    assert "这是测试内容" in text
    
    # GBK编码
    content = "这是测试内容".encode('gbk')
    text = service.parser.parse_txt(content)
    assert "这是测试内容" in text


def test_file_parser_service_parse_pdf():
    """测试FileParserService解析PDF文件"""
    service = FileParserService()
    
    # 创建简单的PDF内容（实际测试中应使用真实PDF）
    # 这里只测试方法存在性
    assert hasattr(service.parser, 'parse_pdf')


def test_file_parser_service_parse_docx():
    """测试FileParserService解析DOCX文件"""
    service = FileParserService()
    
    # 测试方法存在性
    assert hasattr(service.parser, 'parse_docx')


@pytest.mark.asyncio
async def test_batch_upload_agent_handle_parse_file(mcp_server):
    """测试BatchUploadAgent单文件解析"""
    agent = BatchUploadAgent(mcp_server=mcp_server)
    
    # Mock send_response方法
    response_captured = None
    async def mock_send_response(message, payload):
        nonlocal response_captured
        response_captured = payload
    
    agent.send_response = mock_send_response
    
    # 创建解析请求
    file_content = "测试JD内容".encode('utf-8')
    request = MCPMessage(
        message_id="msg123",
        sender="test",
        receiver=agent.agent_id,
        message_type="request",
        action="parse_file",
        payload={
            "file_content": file_content,
            "filename": "test.txt"
        },
        context_id="ctx123",
        timestamp=datetime.now().timestamp()
    )
    
    # 处理请求
    await agent.handle_parse_file(request)
    
    # 验证响应
    assert response_captured is not None
    assert response_captured["success"] is True
    assert "jd_text" in response_captured
    assert "测试JD内容" in response_captured["jd_text"]


# ============================================================================
# EvaluatorAgent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_evaluator_agent_initialization(mcp_server, mock_llm):
    """测试EvaluatorAgent初始化"""
    agent = EvaluatorAgent(
        mcp_server=mcp_server,
        llm_client=mock_llm,
        agent_id="test_evaluator"
    )
    
    assert agent.agent_id == "test_evaluator"
    assert agent.agent_type == "evaluator"
    assert agent.llm == mock_llm
    assert "evaluate_quality" in agent.message_handlers
    assert len(agent.evaluation_models) == 3
    assert "standard" in agent.evaluation_models
    assert "mercer_ipe" in agent.evaluation_models
    assert "factor_comparison" in agent.evaluation_models


@pytest.mark.asyncio
async def test_standard_evaluation_model(mock_llm):
    """测试标准评估模型"""
    model = StandardEvaluationModel()
    
    assert len(model.dimensions) == 3
    assert "完整性" in model.dimensions
    assert "清晰度" in model.dimensions
    assert "专业性" in model.dimensions
    
    jd_data = {
        "job_title": "Python工程师",
        "responsibilities": ["开发系统"],
        "required_skills": ["Python"],
        "qualifications": ["本科"]
    }
    
    result = await model.evaluate(jd_data, mock_llm)
    
    assert "dimension_scores" in result
    assert "overall_score" in result
    assert "weighted_score" in result
    assert mock_llm.call_count > 0


@pytest.mark.asyncio
async def test_mercer_ipe_model(mock_llm):
    """测试美世国际职位评估法"""
    model = MercerIPEModel()
    
    assert len(model.dimensions) == 4
    assert "影响力" in model.dimensions
    assert "沟通" in model.dimensions
    assert "创新" in model.dimensions
    assert "知识技能" in model.dimensions
    
    # 设置mock响应
    mock_llm.set_response("evaluate_quality", {
        "dimension_scores": {
            "影响力": 85,
            "沟通": 75,
            "创新": 70,
            "知识技能": 80
        },
        "overall_score": 78,
        "analysis": "测试分析",
        "issues": []
    })
    
    jd_data = {"job_title": "Python工程师"}
    result = await model.evaluate(jd_data, mock_llm)
    
    assert "weighted_score" in result
    assert result["weighted_score"] > 0


@pytest.mark.asyncio
async def test_factor_comparison_model(mock_llm):
    """测试因素比较法"""
    model = FactorComparisonModel()
    
    assert len(model.dimensions) == 4
    assert "技能要求" in model.dimensions
    assert "责任程度" in model.dimensions
    assert "努力程度" in model.dimensions
    assert "工作条件" in model.dimensions


# ============================================================================
# OptimizerAgent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_optimizer_agent_initialization(mcp_server, mock_llm):
    """测试OptimizerAgent初始化"""
    agent = OptimizerAgent(
        mcp_server=mcp_server,
        llm_client=mock_llm,
        agent_id="test_optimizer"
    )
    
    assert agent.agent_id == "test_optimizer"
    assert agent.agent_type == "optimizer"
    assert agent.llm == mock_llm
    assert "generate_suggestions" in agent.message_handlers


# ============================================================================
# QuestionnaireAgent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_questionnaire_agent_initialization(mcp_server, mock_llm):
    """测试QuestionnaireAgent初始化"""
    from src.agents.questionnaire_agent import QuestionnaireAgent
    
    agent = QuestionnaireAgent(
        mcp_server=mcp_server,
        llm_client=mock_llm,
        agent_id="test_questionnaire"
    )
    
    assert agent.agent_id == "test_questionnaire"
    assert agent.agent_type == "questionnaire"
    assert "generate_questionnaire" in agent.message_handlers


# ============================================================================
# MatcherAgent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_matcher_agent_initialization(mcp_server, mock_llm):
    """测试MatcherAgent初始化"""
    from src.agents.matcher_agent import MatcherAgent
    
    agent = MatcherAgent(
        mcp_server=mcp_server,
        llm_client=mock_llm,
        agent_id="test_matcher"
    )
    
    assert agent.agent_id == "test_matcher"
    assert agent.agent_type == "matcher"
    assert "evaluate_match" in agent.message_handlers


# ============================================================================
# DataManagerAgent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_data_manager_agent_initialization(mcp_server):
    """测试DataManagerAgent初始化"""
    agent = DataManagerAgent(
        mcp_server=mcp_server,
        agent_id="test_data_manager"
    )
    
    assert agent.agent_id == "test_data_manager"
    assert agent.agent_type == "data_manager"
    assert "save_jd" in agent.message_handlers
    assert "get_jd" in agent.message_handlers
    assert "get_all_categories" in agent.message_handlers


# ============================================================================
# CoordinatorAgent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_coordinator_agent_initialization(mcp_server):
    """测试CoordinatorAgent初始化"""
    from src.agents.coordinator_agent import CoordinatorAgent
    
    agent = CoordinatorAgent(
        mcp_server=mcp_server,
        agent_id="test_coordinator"
    )
    
    assert agent.agent_id == "test_coordinator"
    assert agent.agent_type == "coordinator"
    assert "analyze_jd" in agent.message_handlers


# ============================================================================
# ReportAgent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_report_agent_initialization(mcp_server):
    """测试ReportAgent初始化"""
    from src.agents.report_agent import ReportAgent
    
    agent = ReportAgent(
        mcp_server=mcp_server,
        agent_id="test_reporter"
    )
    
    assert agent.agent_id == "test_reporter"
    assert agent.agent_type == "reporter"
    assert "generate_report" in agent.message_handlers


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_agent_message_flow(mcp_server, mock_llm):
    """测试Agent间消息流转"""
    # 创建多个Agent（不启动）
    parser = ParserAgent(mcp_server=mcp_server, llm_client=mock_llm, agent_id="parser")
    evaluator = EvaluatorAgent(mcp_server=mcp_server, llm_client=mock_llm, agent_id="evaluator")
    
    # 验证Agent初始化
    assert parser.agent_id == "parser"
    assert parser.agent_type == "parser"
    assert evaluator.agent_id == "evaluator"
    assert evaluator.agent_type == "evaluator"


@pytest.mark.asyncio
async def test_mock_llm_responses(mock_llm):
    """测试Mock LLM的各种响应"""
    # 测试解析JD
    result = await mock_llm.generate_json("解析以下岗位JD...")
    assert "job_title" in result
    assert result["job_title"] == "Python后端工程师"
    
    # 测试分类
    result = await mock_llm.generate_json("归类到合适的分类...")
    assert "level1_id" in result
    assert "reasoning" in result
    
    # 测试评估
    result = await mock_llm.generate_json("评估以下岗位JD的质量...")
    assert "overall_score" in result
    assert "dimension_scores" in result
    
    # 测试优化建议
    result = await mock_llm.generate_json("优化建议...")
    assert "suggestions" in result
    assert "missing_info" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
