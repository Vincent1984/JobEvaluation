"""项目启动检查脚本"""

import sys
import os
import subprocess


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_check(name, status, message=""):
    """打印检查结果"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
    if message:
        print(f"   {message}")


def check_python_version():
    """检查Python版本"""
    print_header("检查Python版本")
    version = sys.version_info
    required = (3, 11)
    
    current = f"{version.major}.{version.minor}.{version.micro}"
    required_str = f"{required[0]}.{required[1]}.0"
    
    is_ok = version >= required
    print_check(
        f"Python版本: {current}",
        is_ok,
        f"需要 >= {required_str}" if not is_ok else "版本符合要求"
    )
    return is_ok


def check_files():
    """检查必需文件"""
    print_header("检查必需文件")
    
    required_files = [
        "requirements.txt",
        ".env.example",
        "src/core/config.py",
        "src/core/llm_client.py",
        "src/models/schemas.py",
        "src/services/jd_service.py",
        "src/ui/app.py"
    ]
    
    all_ok = True
    for file in required_files:
        exists = os.path.exists(file)
        print_check(file, exists, "文件不存在" if not exists else "")
        all_ok = all_ok and exists
    
    return all_ok


def check_env_file():
    """检查环境变量文件"""
    print_header("检查环境变量配置")
    
    env_exists = os.path.exists(".env")
    print_check(".env文件", env_exists, "请从.env.example复制" if not env_exists else "")
    
    if env_exists:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
            has_key = "OPENAI_API_KEY" in content and "sk-" in content
            print_check(
                "API密钥配置",
                has_key,
                "请配置有效的API密钥" if not has_key else "已配置"
            )
            return has_key
    
    return False


def check_dependencies():
    """检查依赖包"""
    print_header("检查依赖包")
    
    required_packages = [
        "streamlit",
        "fastapi",
        "pydantic",
        "openai"
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print_check(package, True, "已安装")
        except ImportError:
            print_check(package, False, "未安装")
            all_ok = False
    
    if not all_ok:
        print("\n💡 提示: 运行 'pip install -r requirements.txt' 安装依赖")
    
    return all_ok


def check_data_dir():
    """检查数据目录"""
    print_header("检查数据目录")
    
    if not os.path.exists("data"):
        os.makedirs("data")
        print_check("data目录", True, "已创建")
    else:
        print_check("data目录", True, "已存在")
    
    return True


def main():
    """主函数"""
    print("\n" + "🔍 岗位JD分析器 - 启动检查".center(60))
    
    checks = [
        ("Python版本", check_python_version),
        ("必需文件", check_files),
        ("环境变量", check_env_file),
        ("依赖包", check_dependencies),
        ("数据目录", check_data_dir)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 检查 {name} 时出错: {e}")
            results.append((name, False))
    
    # 总结
    print_header("检查总结")
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        symbol = "✅" if result else "❌"
        print(f"{symbol} {name}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 所有检查通过！系统已准备就绪。")
        print("\n下一步:")
        print("  1. 运行 'python run.py' 启动应用")
        print("  2. 或运行 'streamlit run src/ui/app.py' 直接启动UI")
    else:
        print("⚠️  部分检查未通过，请根据上述提示进行修复。")
        print("\n常见问题:")
        print("  - Python版本过低: 安装Python 3.11+")
        print("  - 缺少依赖: 运行 'pip install -r requirements.txt'")
        print("  - 缺少.env: 从.env.example复制并配置API密钥")
    
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
