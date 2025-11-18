"""
工作流测试

测试JD分析工作流和问卷评估工作流的基本功能
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.workflows import JDAnalysisWorkflow, QuestionnaireWorkflow
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.mcp.context import MCPContext


@pytest.fixture
def mock_mcp_server():
    """创建Mock MCP Server"""
    server = MagicMock(spec=MCPServer)
    server.send_message = AsyncMock()
    server.update_context = AsyncMock()
    server.get_context = AsyncMock()
    return server


@pytest.fixture
def mock_response():
    """创建Mock响应"""
    response = MagicMock()
    response.payload = {}
    return response


class TestJDAnalysisWorkflow:
    """测试JD分析工作流"""
    
    @pytest.mark.asyncio
    async def test_execute_full_analysis_success(self, mock_mcp_server):
        """测试成功执行完整分析"""
        # 准备Mock响应
        parse_response = MagicMock()
        parse_response.payload = {
            "jd_id": "test_jd_123",
            "parsed_data": {
                "job_title": "Python工程师",
                "department": "技术部",
                "responsibilities": ["开发", "测试"],
                "required_skills": ["Python", "Django"]
            }
        }
        
        eval_response = MagicMock()
        eval_response.payload = {
            "quality_score": {
                "overall_score": 85.0,
                "completeness": 90.0,
                "clarity": 80.0,
                "professionalism": 85.0
            },
            "issues": []
        }
        
        opt_response = MagicMock()
        opt_response.payload = {
            "recommendations": [
                "建议补充薪资范围",
                "建议明确工作地点"
            ]
        }
        
        # 配置Mock Server
        mock_mcp_server.wait_for_response = AsyncMock(
            side_effect=[parse_response, eval_response, opt_response]
        )
        
        # 创建工作流
        workflow = JDAnalysisWorkflow(mock_mcp_server)
        
        # 执行分析
        result = await workflow.execute_full_analysis(
            jd_text="测试JD文本",
            evaluation_model="standard"
        )
        
        # 验证结果
        assert result["status"] == "completed"
        assert result["jd_id"] == "test_jd_123"
        assert "parsed_data" in result
        assert "evaluation" in result
        assert "suggestions" in result
        assert "workflow_id" in result
        assert "execution_time" in result
        
        # 验证调用
        assert mock_mcp_server.send_message.call_count == 3  # parse, eval, opt
        assert mock_mcp_server.update_context.call_count >= 4  # create + 3 steps
    
    @pytest.mark.asyncio
    async def test_execute_full_analysis_parse_failure(self, mock_mcp_server):
        """测试解析失败的情况"""
        # 配置Mock Server返回超时
        mock_mcp_server.wait_for_response = AsyncMock(
            side_effect=TimeoutError("解析超时")
        )
        
        # 创建工作流
        workflow = JDAnalysisWorkflow(mock_mcp_server)
        
        # 执行分析
        result = await workflow.execute_full_analysis(
            jd_text="测试JD文本",
            evaluation_model="standard"
        )
        
        # 验证结果
        assert result["status"] == "failed"
        assert "error" in result
        assert "workflow_id" in result
    
    @pytest.mark.asyncio
    async def test_get_workflow_status(self, mock_mcp_server):
        """测试获取工作流状态"""
        # 准备Mock上下文
        mock_context = MCPContext(
            context_id="test_workflow_123",
            task_id="test_task_123",
            shared_data={
                "status": "running",
                "step": "evaluation",
                "jd_id": "test_jd_456",
                "start_time": 1234567890.0
            },
            metadata={}
        )
        
        mock_mcp_server.get_context = AsyncMock(return_value=mock_context)
        
        # 创建工作流
        workflow = JDAnalysisWorkflow(mock_mcp_server)
        
        # 获取状态
        status = await workflow.get_workflow_status("test_workflow_123")
        
        # 验证结果
        assert status is not None
        assert status["workflow_id"] == "test_workflow_123"
        assert status["status"] == "running"
        assert status["step"] == "evaluation"
        assert status["jd_id"] == "test_jd_456"


class TestQuestionnaireWorkflow:
    """测试问卷工作流"""
    
    @pytest.mark.asyncio
    async def test_generate_questionnaire_success(self, mock_mcp_server):
        """测试成功生成问卷"""
        # 准备Mock响应
        response = MagicMock()
        response.payload = {
            "questionnaire_id": "quest_123",
            "questionnaire": {
                "title": "Python工程师评估问卷",
                "questions": [
                    {
                        "id": "q1",
                        "question_text": "您有多少年Python开发经验？",
                        "question_type": "single_choice",
                        "options": ["1-2年", "3-5年", "5年以上"]
                    }
                ]
            }
        }
        
        mock_mcp_server.wait_for_response = AsyncMock(return_value=response)
        
        # 创建工作流
        workflow = QuestionnaireWorkflow(mock_mcp_server)
        
        # 生成问卷
        result = await workflow.generate_questionnaire(
            jd_id="test_jd_123",
            evaluation_model="standard"
        )
        
        # 验证结果
        assert result["status"] == "completed"
        assert result["questionnaire_id"] == "quest_123"
        assert "questionnaire" in result
        assert "workflow_id" in result
        assert "execution_time" in result
    
    @pytest.mark.asyncio
    async def test_evaluate_match_success(self, mock_mcp_server):
        """测试成功评估匹配度"""
        # 准备Mock响应
        response = MagicMock()
        response.payload = {
            "match_id": "match_123",
            "match_result": {
                "overall_score": 85.0,
                "dimension_scores": {
                    "技能匹配": 90.0,
                    "经验匹配": 80.0
                },
                "strengths": ["Python经验丰富"],
                "gaps": ["缺少Django经验"]
            }
        }
        
        mock_mcp_server.wait_for_response = AsyncMock(return_value=response)
        
        # 创建工作流
        workflow = QuestionnaireWorkflow(mock_mcp_server)
        
        # 评估匹配度
        result = await workflow.evaluate_match(
            jd_id="test_jd_123",
            questionnaire_id="quest_456",
            responses={"q1": "5年以上"},
            respondent_name="张三"
        )
        
        # 验证结果
        assert result["status"] == "completed"
        assert result["match_id"] == "match_123"
        assert "match_result" in result
        assert result["match_result"]["overall_score"] == 85.0
    
    @pytest.mark.asyncio
    async def test_batch_evaluate_candidates_success(self, mock_mcp_server):
        """测试批量评估候选人"""
        # 准备Mock响应
        def create_response(idx):
            response = MagicMock()
            response.payload = {
                "match_id": f"match_{idx}",
                "match_result": {
                    "overall_score": 80.0 + idx,
                    "dimension_scores": {},
                    "strengths": [],
                    "gaps": []
                }
            }
            return response
        
        mock_mcp_server.wait_for_response = AsyncMock(
            side_effect=[create_response(i) for i in range(3)]
        )
        
        # 创建工作流
        workflow = QuestionnaireWorkflow(mock_mcp_server)
        
        # 准备候选人数据
        candidate_responses = [
            {"respondent_name": "张三", "responses": {"q1": "5年"}},
            {"respondent_name": "李四", "responses": {"q1": "3年"}},
            {"respondent_name": "王五", "responses": {"q1": "7年"}}
        ]
        
        # 批量评估
        result = await workflow.batch_evaluate_candidates(
            jd_id="test_jd_123",
            questionnaire_id="quest_456",
            candidate_responses=candidate_responses
        )
        
        # 验证结果
        assert result["status"] == "completed"
        assert result["total"] == 3
        assert result["successful"] == 3
        assert result["failed"] == 0
        assert len(result["results"]) == 3
        assert len(result["failed_candidates"]) == 0
    
    @pytest.mark.asyncio
    async def test_batch_evaluate_with_failures(self, mock_mcp_server):
        """测试批量评估中部分失败的情况"""
        # 准备Mock响应（第2个失败）
        response1 = MagicMock()
        response1.payload = {
            "match_id": "match_0",
            "match_result": {"overall_score": 80.0}
        }
        
        response3 = MagicMock()
        response3.payload = {
            "match_id": "match_2",
            "match_result": {"overall_score": 80.0}
        }
        
        mock_mcp_server.wait_for_response = AsyncMock(
            side_effect=[response1, Exception("评估失败"), response3]
        )
        
        # 创建工作流
        workflow = QuestionnaireWorkflow(mock_mcp_server)
        
        # 准备候选人数据
        candidate_responses = [
            {"respondent_name": "张三", "responses": {"q1": "5年"}},
            {"respondent_name": "李四", "responses": {"q1": "3年"}},
            {"respondent_name": "王五", "responses": {"q1": "7年"}}
        ]
        
        # 批量评估
        result = await workflow.batch_evaluate_candidates(
            jd_id="test_jd_123",
            questionnaire_id="quest_456",
            candidate_responses=candidate_responses
        )
        
        # 验证结果
        assert result["status"] == "completed"
        assert result["total"] == 3
        assert result["successful"] == 2
        assert result["failed"] == 1
        assert len(result["failed_candidates"]) == 1
        assert result["failed_candidates"][0]["respondent_name"] == "李四"
    
    @pytest.mark.asyncio
    async def test_get_workflow_status_batch(self, mock_mcp_server):
        """测试获取批量评估工作流状态"""
        # 准备Mock上下文
        mock_context = MCPContext(
            context_id="batch_123",
            task_id="batch_123",
            shared_data={
                "workflow_type": "batch_evaluation",
                "status": "running",
                "total_candidates": 10,
                "processed_candidates": 5,
                "successful_candidates": 4,
                "failed_candidates": 1
            },
            metadata={}
        )
        
        mock_mcp_server.get_context = AsyncMock(return_value=mock_context)
        
        # 创建工作流
        workflow = QuestionnaireWorkflow(mock_mcp_server)
        
        # 获取状态
        status = await workflow.get_workflow_status("batch_123")
        
        # 验证结果
        assert status is not None
        assert status["workflow_type"] == "batch_evaluation"
        assert status["total_candidates"] == 10
        assert status["processed_candidates"] == 5
        assert status["successful_candidates"] == 4
        assert status["failed_candidates"] == 1


def test_workflow_imports():
    """测试工作流模块导入"""
    from src.workflows import JDAnalysisWorkflow, QuestionnaireWorkflow
    
    assert JDAnalysisWorkflow is not None
    assert QuestionnaireWorkflow is not None


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
