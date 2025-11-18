"""DeepSeek-R1 LLM客户端封装"""

import json
import hashlib
import asyncio
from typing import Dict, Any, Optional, List, AsyncGenerator
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging
from .config import settings
from .llm_cache import LLMCache, create_memory_cache, create_redis_cache

# 配置日志
logger = logging.getLogger(__name__)


class LLMException(Exception):
    """LLM调用异常基类"""
    pass


class LLMConnectionError(LLMException):
    """LLM连接错误"""
    pass


class LLMRateLimitError(LLMException):
    """LLM速率限制错误"""
    pass


class LLMTimeoutError(LLMException):
    """LLM超时错误"""
    pass


class DeepSeekR1Client:
    """DeepSeek-R1客户端封装
    
    特性：
    - 异步API调用
    - 自动重试机制（指数退避）
    - 错误处理和分类
    - 响应缓存
    - 批量调用支持
    - 流式输出支持
    - 连接池优化
    - 请求去重
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
        cache: Optional[LLMCache] = None,
        enable_cache: bool = True,
        max_concurrent: int = 10
    ):
        """初始化DeepSeek-R1客户端
        
        Args:
            api_key: API密钥，默认从配置读取
            base_url: API基础URL，默认从配置读取
            model: 模型名称，默认使用deepseek-reasoner
            max_retries: 最大重试次数
            timeout: 请求超时时间（秒）
            cache: LLMCache实例，默认使用内存缓存
            enable_cache: 是否启用缓存
            max_concurrent: 最大并发请求数
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self.model = model or settings.LLM_MODEL
        self.max_retries = max_retries
        self.timeout = timeout
        self.enable_cache = enable_cache
        self.max_concurrent = max_concurrent
        
        # 初始化OpenAI客户端（DeepSeek兼容OpenAI API）
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=0  # 我们自己处理重试
        )
        
        # 初始化缓存（默认使用内存缓存）
        self.cache = cache or create_memory_cache()
        
        # 并发控制
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # 请求去重（防止相同请求并发执行）
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._request_lock = asyncio.Lock()
        
        logger.info(f"DeepSeek-R1客户端初始化完成: model={self.model}, base_url={self.base_url}, cache={self.cache.backend.__class__.__name__}, max_concurrent={max_concurrent}")
    
    async def clear_cache(self):
        """清空缓存"""
        await self.cache.clear()
        logger.info("缓存已清空")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIConnectionError, APITimeoutError, RateLimitError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _call_api(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool = False
    ) -> Any:
        """调用DeepSeek API（带重试）
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
            
        Returns:
            API响应对象
            
        Raises:
            LLMConnectionError: 连接错误
            LLMRateLimitError: 速率限制错误
            LLMTimeoutError: 超时错误
            LLMException: 其他错误
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            return response
            
        except APIConnectionError as e:
            logger.error(f"DeepSeek API连接错误: {e}")
            raise LLMConnectionError(f"无法连接到DeepSeek API: {e}") from e
            
        except RateLimitError as e:
            logger.warning(f"DeepSeek API速率限制: {e}")
            raise LLMRateLimitError(f"API调用速率超限，请稍后重试: {e}") from e
            
        except APITimeoutError as e:
            logger.error(f"DeepSeek API超时: {e}")
            raise LLMTimeoutError(f"API调用超时: {e}") from e
            
        except APIError as e:
            logger.error(f"DeepSeek API错误: {e}")
            raise LLMException(f"API调用失败: {e}") from e
            
        except Exception as e:
            logger.error(f"DeepSeek调用未知错误: {e}")
            raise LLMException(f"LLM调用失败: {e}") from e
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_message: Optional[str] = None,
        cache_ttl: Optional[int] = None
    ) -> str:
        """生成文本响应（优化版：支持请求去重和并发控制）
        
        Args:
            prompt: 用户提示词
            model: 模型名称，默认使用初始化时的模型
            temperature: 温度参数（0-1），控制随机性
            max_tokens: 最大生成token数
            system_message: 系统消息，默认为HR专家角色
            cache_ttl: 缓存过期时间（秒），None使用默认值
            
        Returns:
            生成的文本内容
            
        Raises:
            LLMException: LLM调用失败
        """
        model = model or self.model
        system_message = system_message or "你是一个专业的HR岗位分析专家。"
        
        # 生成缓存键
        cache_key = LLMCache.generate_cache_key(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_message=system_message
        )
        
        # 如果启用缓存，尝试从缓存获取
        if self.enable_cache:
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info(f"从缓存返回结果: {cache_key[:8]}...")
                return cached_result
        
        # 请求去重：如果相同请求正在执行，等待其完成
        async with self._request_lock:
            if cache_key in self._pending_requests:
                logger.info(f"等待重复请求完成: {cache_key[:8]}...")
                return await self._pending_requests[cache_key]
            
            # 创建Future用于请求去重
            future = asyncio.Future()
            self._pending_requests[cache_key] = future
        
        try:
            # 并发控制
            async with self.semaphore:
                # 构建消息
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
                
                # 调用API
                logger.info(f"调用DeepSeek-R1: model={model}, prompt_length={len(prompt)}")
                response = await self._call_api(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False
                )
                
                # 提取结果
                result = response.choices[0].message.content
                
                # 保存到缓存
                if self.enable_cache:
                    await self.cache.set(cache_key, result, cache_ttl)
                
                logger.info(f"DeepSeek-R1响应成功: response_length={len(result)}")
                
                # 设置Future结果
                future.set_result(result)
                
                return result
        except Exception as e:
            # 设置Future异常
            future.set_exception(e)
            raise
        finally:
            # 清理pending请求
            async with self._request_lock:
                self._pending_requests.pop(cache_key, None)
    
    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成JSON格式响应
        
        Args:
            prompt: 用户提示词（应包含JSON格式要求）
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            system_message: 系统消息
            
        Returns:
            解析后的JSON对象
            
        Raises:
            LLMException: LLM调用失败
            ValueError: JSON解析失败
        """
        response_text = await self.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_message=system_message
        )
        
        # 尝试提取和解析JSON
        try:
            # 尝试从markdown代码块中提取
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            
            # 解析JSON
            result = json.loads(json_str)
            logger.debug("JSON解析成功")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 原始响应: {response_text[:200]}...")
            raise ValueError(f"无法解析JSON响应: {e}") from e
    
    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_message: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """流式生成文本响应
        
        Args:
            prompt: 用户提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            system_message: 系统消息
            
        Yields:
            生成的文本片段
            
        Raises:
            LLMException: LLM调用失败
        """
        model = model or self.model
        system_message = system_message or "你是一个专业的HR岗位分析专家。"
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        # 调用API（流式）
        logger.info(f"流式调用DeepSeek-R1: model={model}")
        stream = await self._call_api(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        # 逐块返回
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def batch_generate(
        self,
        prompts: List[str],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_message: Optional[str] = None,
        max_concurrent: int = 5
    ) -> List[str]:
        """批量生成文本响应
        
        Args:
            prompts: 提示词列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            system_message: 系统消息
            max_concurrent: 最大并发数
            
        Returns:
            生成的文本列表（顺序与输入一致）
            
        Raises:
            LLMException: LLM调用失败
        """
        logger.info(f"批量调用DeepSeek-R1: count={len(prompts)}, max_concurrent={max_concurrent}")
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(prompt: str) -> str:
            async with semaphore:
                return await self.generate(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_message=system_message
                )
        
        # 并发执行
        tasks = [generate_with_semaphore(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"批量调用第{i}个请求失败: {result}")
                processed_results.append(f"ERROR: {str(result)}")
            else:
                processed_results.append(result)
        
        logger.info(f"批量调用完成: 成功={sum(1 for r in results if not isinstance(r, Exception))}/{len(prompts)}")
        return processed_results
    
    async def batch_generate_json(
        self,
        prompts: List[str],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_message: Optional[str] = None,
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """批量生成JSON格式响应
        
        Args:
            prompts: 提示词列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            system_message: 系统消息
            max_concurrent: 最大并发数
            
        Returns:
            解析后的JSON对象列表
        """
        logger.info(f"批量JSON调用DeepSeek-R1: count={len(prompts)}")
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_json_with_semaphore(prompt: str) -> Dict[str, Any]:
            async with semaphore:
                try:
                    return await self.generate_json(
                        prompt=prompt,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_message=system_message
                    )
                except Exception as e:
                    logger.error(f"JSON生成失败: {e}")
                    return {"error": str(e)}
        
        # 并发执行
        tasks = [generate_json_with_semaphore(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = await self.cache.get_stats()
        stats["enabled"] = self.enable_cache
        return stats


# 全局DeepSeek-R1客户端实例
deepseek_client = DeepSeekR1Client()

# 向后兼容的别名
llm_client = deepseek_client
LLMClient = DeepSeekR1Client
