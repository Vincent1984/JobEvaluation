#!/usr/bin/env python3
"""
服务健康检查脚本
检查所有服务的运行状态
"""

import asyncio
import sys
import httpx
import redis.asyncio as aioredis
from pathlib import Path
from typing import Dict, List, Tuple

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
    
    async def check_redis(self) -> Tuple[bool, str]:
        """检查Redis连接"""
        try:
            redis_client = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True
            )
            
            # 测试连接
            await redis_client.ping()
            await redis_client.close()
            
            return True, "Redis连接正常"
        except Exception as e:
            return False, f"Redis连接失败: {str(e)}"
    
    async def check_api(self) -> Tuple[bool, str]:
        """检查API服务"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{settings.API_HOST}:{settings.API_PORT}/health",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return True, "API服务正常"
                else:
                    return False, f"API返回状态码: {response.status_code}"
        except httpx.ConnectError:
            return False, "无法连接到API服务"
        except Exception as e:
            return False, f"API检查失败: {str(e)}"
    
    async def check_database(self) -> Tuple[bool, str]:
        """检查数据库"""
        try:
            from src.core.database import get_db
            
            # 尝试获取数据库连接
            async for db in get_db():
                # 执行简单查询
                result = await db.execute("SELECT 1")
                if result:
                    return True, "数据库连接正常"
                break
            
            return False, "数据库查询失败"
        except Exception as e:
            return False, f"数据库检查失败: {str(e)}"
    
    async def check_mcp_agents(self) -> Tuple[bool, str]:
        """检查MCP Agents状态"""
        try:
            redis_client = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True
            )
            
            # 检查已注册的Agents
            agents = await redis_client.smembers("mcp:agents")
            
            await redis_client.close()
            
            if agents:
                agent_count = len(agents)
                return True, f"发现 {agent_count} 个活跃Agents: {', '.join(agents)}"
            else:
                return False, "未发现活跃的Agents"
        except Exception as e:
            return False, f"Agent检查失败: {str(e)}"
    
    async def check_all(self) -> Dict[str, Tuple[bool, str]]:
        """执行所有健康检查"""
        checks = {
            "Redis": self.check_redis(),
            "API": self.check_api(),
            "Database": self.check_database(),
            "MCP Agents": self.check_mcp_agents(),
        }
        
        results = {}
        for name, check_coro in checks.items():
            try:
                success, message = await check_coro
                results[name] = (success, message)
            except Exception as e:
                results[name] = (False, f"检查异常: {str(e)}")
        
        return results
    
    def print_results(self, results: Dict[str, Tuple[bool, str]]):
        """打印检查结果"""
        print("\n" + "="*60)
        print("服务健康检查报告")
        print("="*60 + "\n")
        
        all_healthy = True
        
        for service, (success, message) in results.items():
            status = "✓ 正常" if success else "✗ 异常"
            color = "\033[92m" if success else "\033[91m"
            reset = "\033[0m"
            
            print(f"{color}{status}{reset} {service:15} - {message}")
            
            if not success:
                all_healthy = False
        
        print("\n" + "="*60)
        
        if all_healthy:
            print("\033[92m所有服务运行正常\033[0m")
            return 0
        else:
            print("\033[91m部分服务存在问题\033[0m")
            return 1


async def main():
    """主函数"""
    checker = HealthChecker()
    results = await checker.check_all()
    exit_code = checker.print_results(results)
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n检查已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n检查失败: {e}")
        sys.exit(1)
