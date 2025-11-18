"""JD解析Agent - 解析职位描述并自动分类"""

import logging
import json
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from src.mcp.agent import MCPAgent
from src.mcp.server import MCPServer
from src.mcp.message import MCPMessage
from src.core.llm_client import DeepSeekR1Client

logger = logging.getLogger(__name__)


class ParserAgent(MCPAgent):
    """JD解析Agent
    
    职责：
    - 解析JD文本，提取结构化信息
    - 应用自定义字段提取
    - 职位自动分类（基于3层级分类体系）
    - 获取样本JD并用于分类参考
    - 构建分类Prompt（包含样本JD参考）
    - 与DataManagerAgent通讯
    """
    
    def __init__(
        self,
        mcp_server: MCPServer,
        llm_client: DeepSeekR1Client,
        agent_id: str = "parser",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """初始化JD解析Agent
        
        Args:
            mcp_server: MCP服务器实例
            llm_client: LLM客户端
            agent_id: Agent ID
            metadata: 元数据
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="parser",
            mcp_server=mcp_server,
            metadata=metadata
        )
        
        self.llm = llm_client
        
        # 注册消息处理器
        self.register_handler("parse_jd", self.handle_parse_jd)
        self.register_handler("classify_job", self.handle_classify_job)
        
        logger.info(f"ParserAgent initialized: {agent_id}")
    
    async def handle_parse_jd(self, message: MCPMessage) -> None:
        """处理JD解析请求
        
        Args:
            message: MCP消息，payload包含:
                - jd_text: JD文本
                - custom_fields: 自定义字段（可选）
        """
        jd_text = message.payload.get("jd_text")
        custom_fields = message.payload.get("custom_fields", {})
        
        logger.info(f"收到JD解析请求, 文本长度={len(jd_text)}")
        
        try:
            # 使用LLM解析JD
            parsed_data = await self._parse_jd_with_llm(jd_text, custom_fields)
            
            # 自动分类职位
            category_ids = await self._classify_job(parsed_data, message.context_id)
            parsed_data.update(category_ids)
            
            # 添加元数据
            parsed_data["raw_text"] = jd_text
            parsed_data["id"] = str(uuid.uuid4())
            parsed_data["created_at"] = datetime.now().isoformat()
            parsed_data["updated_at"] = datetime.now().isoformat()
            
            # 请求数据Agent保存
            save_response = await self.send_request(
                receiver="data_manager",
                action="save_jd",
                payload=parsed_data,
                context_id=message.context_id,
                timeout=30.0
            )
            
            if not save_response.payload.get("success", True):
                raise Exception(f"保存JD失败: {save_response.payload.get('error', '未知错误')}")
            
            jd_id = save_response.payload["jd_id"]
            
            logger.info(f"JD解析成功: jd_id={jd_id}, 职位={parsed_data.get('job_title')}")
            
            # 返回结果
            await self.send_response(message, {
                "success": True,
                "jd_id": jd_id,
                "parsed_data": parsed_data
            })
            
        except Exception as e:
            logger.error(f"JD解析失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def handle_classify_job(self, message: MCPMessage) -> None:
        """处理职位分类请求
        
        Args:
            message: MCP消息，payload包含:
                - jd_data: JD数据
        """
        jd_data = message.payload.get("jd_data")
        
        logger.info(f"收到职位分类请求: {jd_data.get('job_title', '未知职位')}")
        
        try:
            category_ids = await self._classify_job(jd_data, message.context_id)
            
            await self.send_response(message, {
                "success": True,
                "category_ids": category_ids
            })
            
        except Exception as e:
            logger.error(f"职位分类失败: {e}")
            await self.send_response(message, {
                "success": False,
                "error": str(e)
            })
    
    async def _parse_jd_with_llm(
        self,
        jd_text: str,
        custom_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用LLM解析JD
        
        Args:
            jd_text: JD文本
            custom_fields: 自定义字段
            
        Returns:
            解析后的结构化数据
        """
        prompt = self._build_parse_prompt(jd_text, custom_fields)
        
        try:
            result = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.3,  # 较低温度以获得更稳定的结果
                max_tokens=2000
            )
            
            # 验证必需字段
            required_fields = ["job_title", "responsibilities", "required_skills", "qualifications"]
            for field in required_fields:
                if field not in result:
                    result[field] = [] if field != "job_title" else "未知职位"
            
            return result
            
        except Exception as e:
            logger.error(f"LLM解析失败: {e}")
            raise Exception(f"JD解析失败: {e}")
    
    def _build_parse_prompt(self, jd_text: str, custom_fields: Dict[str, Any]) -> str:
        """构建解析Prompt
        
        Args:
            jd_text: JD文本
            custom_fields: 自定义字段
            
        Returns:
            Prompt字符串
        """
        custom_fields_str = ""
        if custom_fields:
            custom_fields_str = f"\n\n自定义字段（请额外提取）:\n{json.dumps(custom_fields, ensure_ascii=False, indent=2)}"
        
        prompt = f"""你是一个专业的HR岗位分析专家。请解析以下岗位JD，提取结构化信息。

岗位JD:
{jd_text}
{custom_fields_str}

请以JSON格式返回以下信息：
{{
    "job_title": "职位名称",
    "department": "部门（如果有）",
    "location": "工作地点（如果有）",
    "responsibilities": ["职责1", "职责2", ...],
    "required_skills": ["必备技能1", "必备技能2", ...],
    "preferred_skills": ["优选技能1", "优选技能2", ...],
    "qualifications": ["任职资格1", "任职资格2", ...],
    "custom_fields": {{
        // 自定义字段的提取结果
    }}
}}

注意：
1. 如果某些信息在JD中未提及，请使用空字符串或空数组
2. responsibilities、required_skills等应该是数组格式
3. 尽可能详细地提取信息
4. 保持原文的专业性和准确性
"""
        
        return prompt
    
    async def _classify_job(
        self,
        jd_data: Dict[str, Any],
        context_id: Optional[str]
    ) -> Dict[str, Optional[str]]:
        """自动分类职位到3层级分类体系
        
        Args:
            jd_data: JD数据
            context_id: 上下文ID
            
        Returns:
            分类ID字典 {category_level1_id, category_level2_id, category_level3_id}
        """
        try:
            # 获取所有分类
            categories_response = await self.send_request(
                receiver="data_manager",
                action="get_all_categories",
                payload={},
                context_id=context_id,
                timeout=30.0
            )
            
            if not categories_response.payload.get("success", True):
                logger.warning("获取分类失败，跳过自动分类")
                return {
                    "category_level1_id": None,
                    "category_level2_id": None,
                    "category_level3_id": None
                }
            
            categories = categories_response.payload.get("categories", [])
            
            if not categories:
                logger.info("没有可用的分类，跳过自动分类")
                return {
                    "category_level1_id": None,
                    "category_level2_id": None,
                    "category_level3_id": None
                }
            
            # 获取样本JD（用于提高分类准确性）
            sample_jds = await self._get_sample_jds(categories, context_id)
            
            # 使用LLM进行分类
            prompt = self._build_classification_prompt(jd_data, categories, sample_jds)
            
            classification = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.2,  # 更低温度以获得更一致的分类
                max_tokens=1000
            )
            
            return {
                "category_level1_id": classification.get("level1_id"),
                "category_level2_id": classification.get("level2_id"),
                "category_level3_id": classification.get("level3_id")
            }
            
        except Exception as e:
            logger.error(f"职位分类失败: {e}")
            return {
                "category_level1_id": None,
                "category_level2_id": None,
                "category_level3_id": None
            }
    
    async def _get_sample_jds(
        self,
        categories: List[Dict],
        context_id: Optional[str]
    ) -> Dict[str, List[Dict]]:
        """获取各分类的样本JD
        
        Args:
            categories: 分类列表
            context_id: 上下文ID
            
        Returns:
            样本JD字典 {category_id: [jd1, jd2, ...]}
        """
        sample_jds = {}
        
        for category in categories:
            if category.get("level") == 3 and category.get("sample_jd_ids"):
                # 获取样本JD内容
                for jd_id in category["sample_jd_ids"]:
                    try:
                        jd_response = await self.send_request(
                            receiver="data_manager",
                            action="get_jd",
                            payload={"jd_id": jd_id},
                            context_id=context_id,
                            timeout=10.0
                        )
                        
                        if jd_response.payload.get("success", True):
                            if category["id"] not in sample_jds:
                                sample_jds[category["id"]] = []
                            sample_jds[category["id"]].append(jd_response.payload["jd"])
                    
                    except Exception as e:
                        logger.warning(f"获取样本JD失败: jd_id={jd_id}, 错误={e}")
                        continue
        
        return sample_jds
    
    def _build_classification_prompt(
        self,
        jd_data: Dict[str, Any],
        categories: List[Dict],
        sample_jds: Dict[str, List[Dict]]
    ) -> str:
        """构建分类Prompt
        
        Args:
            jd_data: JD数据
            categories: 分类列表
            sample_jds: 样本JD字典
            
        Returns:
            Prompt字符串
        """
        # 构建分类树结构
        category_tree = self._build_category_tree(categories)
        
        prompt = f"""你是一个专业的HR岗位分类专家。请将以下职位归类到合适的分类中。

职位信息:
职位名称: {jd_data.get('job_title', '未知')}
部门: {jd_data.get('department', '未知')}
职责: {', '.join(jd_data.get('responsibilities', [])[:3])}
必备技能: {', '.join(jd_data.get('required_skills', [])[:5])}

可用分类（3层级）:
{category_tree}
"""
        
        # 添加样本JD作为参考
        if sample_jds:
            prompt += "\n\n参考样本职位JD（用于提高分类准确性）:\n"
            for category_id, samples in sample_jds.items():
                category_name = next((c["name"] for c in categories if c["id"] == category_id), "")
                prompt += f"\n分类 '{category_name}' 的样本:\n"
                for idx, sample in enumerate(samples[:2], 1):  # 最多2个样本
                    prompt += f"  样本{idx}: {sample.get('job_title', '未知')} - {', '.join(sample.get('required_skills', [])[:3])}\n"
        
        prompt += """

请返回JSON格式：
{
    "level1_id": "一级分类ID",
    "level2_id": "二级分类ID",
    "level3_id": "三级分类ID",
    "reasoning": "分类理由（简短说明）"
}

注意：
1. 必须选择最合适的分类
2. 如果某个层级没有合适的分类，可以返回null
3. 优先参考样本JD进行分类
4. 分类理由要简洁明了
"""
        
        return prompt
    
    def _build_category_tree(self, categories: List[Dict]) -> str:
        """构建分类树字符串
        
        Args:
            categories: 分类列表
            
        Returns:
            分类树字符串
        """
        # 按层级组织分类
        level1_cats = [c for c in categories if c.get("level") == 1]
        level2_cats = [c for c in categories if c.get("level") == 2]
        level3_cats = [c for c in categories if c.get("level") == 3]
        
        tree_str = ""
        for l1 in level1_cats:
            tree_str += f"\n一级: {l1['name']} (ID: {l1['id']})"
            
            # 找到该一级分类下的二级分类
            l2_children = [c for c in level2_cats if c.get("parent_id") == l1["id"]]
            for l2 in l2_children:
                tree_str += f"\n  二级: {l2['name']} (ID: {l2['id']})"
                
                # 找到该二级分类下的三级分类
                l3_children = [c for c in level3_cats if c.get("parent_id") == l2["id"]]
                for l3 in l3_children:
                    tree_str += f"\n    三级: {l3['name']} (ID: {l3['id']})"
        
        return tree_str


# 便捷函数
async def create_parser_agent(
    mcp_server: MCPServer,
    llm_client: DeepSeekR1Client,
    agent_id: str = "parser",
    auto_start: bool = True
) -> ParserAgent:
    """创建并启动JD解析Agent
    
    Args:
        mcp_server: MCP服务器实例
        llm_client: LLM客户端
        agent_id: Agent ID
        auto_start: 是否自动启动
        
    Returns:
        ParserAgent实例
    """
    agent = ParserAgent(
        mcp_server=mcp_server,
        llm_client=llm_client,
        agent_id=agent_id
    )
    
    if auto_start:
        await agent.start()
    
    return agent
