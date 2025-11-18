"""报告生成Agent - 生成分析报告"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage

logger = logging.getLogger(__name__)


class ReportAgent(MCPAgent):
    """报告生成Agent
    
    职责：
    - 汇总报告数据
    - 生成PDF报告
    - 生成可视化图表
    """
    
    def __init__(
        self,
        mcp_server: MCPServer,
        agent_id: str = "reporter",
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type="reporter",
            mcp_server=mcp_server,
            metadata=metadata
        )
        
        # 注册消息处理器
        self.register_handler("generate_report", self.handle_generate_report)
        self.register_handler("generate_match_report", self.handle_generate_match_report)
        
        logger.info(f"ReportAgent initialized: {agent_id}")
    
    async def handle_generate_report(self, message: MCPMessage) -> None:
        """处理报告生成请求（JD分析报告）"""
        jd_id = message.payload.get("jd_id")
        report_format = message.payload.get("format", "pdf")
        
        logger.info(f"收到报告生成请求: jd_id={jd_id}, format={report_format}")
        
        try:
            # 获取JD数据
            jd_response = await self.send_request(
                receiver="data_manager",
                action="get_jd",
                payload={"jd_id": jd_id},
                context_id=message.context_id,
                timeout=30.0
            )
            
            # 获取评估结果
            eval_response = await self.send_request(
                receiver="data_manager",
                action="get_evaluation",
                payload={"jd_id": jd_id},
                context_id=message.context_id,
                timeout=30.0
            )
            
            jd_data = jd_response.payload.get("jd", {})
            evaluation = eval_response.payload.get("evaluation", {})
            
            # 生成报告
            report = self._generate_jd_report(jd_data, evaluation, report_format)
            
            logger.info(f"报告生成完成: jd_id={jd_id}")
            
            await self.send_response(message, {
                "success": True,
                "report": report
            })
            
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_generate_match_report(self, message: MCPMessage) -> None:
        """处理匹配报告生成请求"""
        match_id = message.payload.get("match_id")
        report_format = message.payload.get("format", "pdf")
        
        logger.info(f"收到匹配报告生成请求: match_id={match_id}")
        
        try:
            # 获取匹配结果
            match_response = await self.send_request(
                receiver="data_manager",
                action="get_match_result",
                payload={"match_id": match_id},
                context_id=message.context_id,
                timeout=30.0
            )
            
            match_result = match_response.payload.get("match_result", {})
            
            # 生成报告
            report = self._generate_match_report(match_result, report_format)
            
            logger.info(f"匹配报告生成完成: match_id={match_id}")
            
            await self.send_response(message, {
                "success": True,
                "report": report
            })
            
        except Exception as e:
            logger.error(f"匹配报告生成失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    def _generate_jd_report(
        self,
        jd_data: Dict,
        evaluation: Dict,
        report_format: str
    ) -> Dict:
        """生成JD分析报告
        
        Args:
            jd_data: JD数据
            evaluation: 评估结果
            report_format: 报告格式（pdf, html, json）
            
        Returns:
            报告数据
        """
        report = {
            "title": f"岗位JD分析报告 - {jd_data.get('job_title', '未知职位')}",
            "generated_at": datetime.now().isoformat(),
            "format": report_format,
            "sections": [
                {
                    "title": "执行摘要",
                    "content": {
                        "job_title": jd_data.get("job_title"),
                        "overall_score": evaluation.get("overall_score", 0),
                        "key_findings": evaluation.get("analysis", "")
                    }
                },
                {
                    "title": "JD详情",
                    "content": jd_data
                },
                {
                    "title": "质量评估",
                    "content": evaluation
                },
                {
                    "title": "可视化图表",
                    "content": {
                        "dimension_scores": evaluation.get("dimension_scores", {}),
                        "chart_type": "radar"
                    }
                }
            ]
        }
        
        # 如果是PDF格式，这里应该调用PDF生成库
        # 简化处理，返回结构化数据
        if report_format == "pdf":
            report["file_path"] = f"/reports/jd_{jd_data.get('id', 'unknown')}.pdf"
            report["note"] = "PDF生成功能待实现"
        
        return report
    
    def _generate_match_report(
        self,
        match_result: Dict,
        report_format: str
    ) -> Dict:
        """生成匹配度报告
        
        Args:
            match_result: 匹配结果
            report_format: 报告格式
            
        Returns:
            报告数据
        """
        report = {
            "title": "候选人匹配度报告",
            "generated_at": datetime.now().isoformat(),
            "format": report_format,
            "sections": [
                {
                    "title": "匹配度概览",
                    "content": {
                        "overall_score": match_result.get("overall_score", 0),
                        "dimension_scores": match_result.get("dimension_scores", {})
                    }
                },
                {
                    "title": "优势分析",
                    "content": {
                        "strengths": match_result.get("strengths", [])
                    }
                },
                {
                    "title": "能力差距",
                    "content": {
                        "gaps": match_result.get("gaps", [])
                    }
                },
                {
                    "title": "发展建议",
                    "content": {
                        "recommendations": match_result.get("recommendations", [])
                    }
                },
                {
                    "title": "可视化图表",
                    "content": {
                        "dimension_scores": match_result.get("dimension_scores", {}),
                        "chart_type": "radar"
                    }
                }
            ]
        }
        
        if report_format == "pdf":
            report["file_path"] = f"/reports/match_{match_result.get('id', 'unknown')}.pdf"
            report["note"] = "PDF生成功能待实现"
        
        return report


async def create_report_agent(
    mcp_server: MCPServer,
    agent_id: str = "reporter",
    auto_start: bool = True
) -> ReportAgent:
    agent = ReportAgent(mcp_server=mcp_server, agent_id=agent_id)
    if auto_start:
        await agent.start()
    return agent
