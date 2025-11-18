"""测试 DeepSeek API 连接"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from src.core.config import settings
from openai import AsyncOpenAI


async def test_deepseek_api():
    """测试 DeepSeek API 连接"""
    print("=" * 60)
    print("测试 DeepSeek API 连接")
    print("=" * 60)
    
    # 显示配置信息
    print(f"\n【配置信息】")
    print(f"API Key: {settings.DEEPSEEK_API_KEY[:10]}...{settings.DEEPSEEK_API_KEY[-4:]}")
    print(f"Base URL: {settings.DEEPSEEK_BASE_URL}")
    print(f"Model: {settings.DEEPSEEK_MODEL}")
    
    # 创建客户端
    client = AsyncOpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL
    )
    
    print(f"\n【测试连接】")
    print("发送测试请求...")
    
    try:
        # 发送简单的测试请求
        response = await client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[
                {"role": "user", "content": "你好，请回复'连接成功'"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        # 获取响应
        reply = response.choices[0].message.content
        
        print(f"\n✅ 连接成功！")
        print(f"模型响应: {reply}")
        print(f"使用的模型: {response.model}")
        print(f"Token 使用: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败！")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        
        # 检查常见问题
        print(f"\n【故障排查】")
        
        if "401" in str(e) or "Authentication" in str(e):
            print("⚠️ 认证失败 - API Key 可能无效或已过期")
            print("   请检查 .env 文件中的 DEEPSEEK_API_KEY")
            
        elif "404" in str(e):
            print("⚠️ 端点未找到 - Base URL 可能不正确")
            print(f"   当前 Base URL: {settings.DEEPSEEK_BASE_URL}")
            
        elif "timeout" in str(e).lower():
            print("⚠️ 连接超时 - 网络可能有问题")
            print("   请检查网络连接")
            
        else:
            print("⚠️ 未知错误")
            print("   请查看上面的详细错误信息")
        
        return False


async def test_with_config_file():
    """使用配置文件测试"""
    print("\n" + "=" * 60)
    print("检查配置文件")
    print("=" * 60)
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("\n❌ .env 文件不存在！")
        print("请创建 .env 文件并添加以下内容：")
        print("""
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
""")
        return False
    
    print(f"\n✅ .env 文件存在")
    
    # 读取并显示配置（隐藏敏感信息）
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"\n【.env 文件内容】")
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if 'API_KEY' in line:
                key, value = line.split('=', 1)
                if len(value) > 10:
                    masked_value = value[:10] + '...' + value[-4:]
                else:
                    masked_value = '***'
                print(f"{key}={masked_value}")
            else:
                print(line)
    
    return True


async def main():
    """主测试函数"""
    print("\n🚀 DeepSeek API 连接测试\n")
    
    # 检查配置文件
    config_ok = await test_with_config_file()
    
    if not config_ok:
        return
    
    # 测试 API 连接
    api_ok = await test_deepseek_api()
    
    print("\n" + "=" * 60)
    if api_ok:
        print("✅ 所有测试通过！DeepSeek API 可以正常使用")
    else:
        print("❌ 测试失败！请检查配置和网络连接")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
