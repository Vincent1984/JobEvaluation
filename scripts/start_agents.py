#!/usr/bin/env python3
"""
Agent启动脚本
启动所有MCP Agents并保持运行
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.core.database import init_db
from src.mcp.server import MCPServer
from src.agents.parser_agent import ParserAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.questionnaire_agent import QuestionnaireAgent
from src.agents.matcher_agent import MatcherAgent
from src.agents.data_manager_agent import DataManagerAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.report_agent import ReportAgent
from src.agents.batch_upload_agent import BatchUploadAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/agents.log')
    ]
)

logger = logging.getLogger(__name__)


class AgentManager:
    """Agent管理器"""
    
    def __init__(self):
        self.mcp_server = None
        self.agents = []
        self.running = False
    
    async def start(self):
        """启动所有Agents"""
        try:
            logger.info("正在初始化数据库...")
            await init_db()
            
            logger.info("正在启动MCP Server...")
            self.mcp_server = MCPServer()
            await self.mcp_server.start()
            
            logger.info("正在启动Agents...")
            
            # 创建所有Agents
            self.agents = [
                DataManagerAgent(self.mcp_server),
                ParserAgent(self.mcp_server),
                EvaluatorAgent(self.mcp_server),
                OptimizerAgent(self.mcp_server),
                QuestionnaireAgent(self.mcp_server),
                MatcherAgent(self.mcp_server),
                ReportAgent(self.mcp_server),
                BatchUploadAgent(self.mcp_server),
                CoordinatorAgent(self.mcp_server),  # 协调Agent最后启动
            ]
            
            # 启动所有Agents
            for agent in self.agents:
                await agent.start()
                logger.info(f"✓ {agent.__class__.__name__} 已启动")
            
            self.running = True
            logger.info(f"所有Agents已启动 (共{len(self.agents)}个)")
            logger.info("系统就绪，等待任务...")
            
            # 保持运行
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"启动失败: {e}", exc_info=True)
            await self.stop()
            sys.exit(1)
    
    async def stop(self):
        """停止所有Agents"""
        logger.info("正在停止Agents...")
        self.running = False
        
        # 停止所有Agents
        for agent in self.agents:
            try:
                await agent.stop()
                logger.info(f"✓ {agent.__class__.__name__} 已停止")
            except Exception as e:
                logger.error(f"停止 {agent.__class__.__name__} 失败: {e}")
        
        # 停止MCP Server
        if self.mcp_server:
            try:
                await self.mcp_server.stop()
                logger.info("✓ MCP Server 已停止")
            except Exception as e:
                logger.error(f"停止MCP Server失败: {e}")
        
        logger.info("所有服务已停止")


async def main():
    """主函数"""
    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)
    
    manager = AgentManager()
    
    # 注册信号处理
    def signal_handler(sig, frame):
        logger.info(f"收到信号 {sig}，正在关闭...")
        asyncio.create_task(manager.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动Agents
    await manager.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出...")
    except Exception as e:
        logger.error(f"运行错误: {e}", exc_info=True)
        sys.exit(1)
