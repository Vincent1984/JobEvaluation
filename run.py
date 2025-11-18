"""启动脚本"""

import os
import sys
import subprocess
import time


def check_env_file():
    """检查环境变量文件"""
    if not os.path.exists(".env"):
        print("⚠️  未找到 .env 文件")
        print("📝 正在从 .env.example 创建 .env 文件...")
        
        if os.path.exists(".env.example"):
            with open(".env.example", "r", encoding="utf-8") as f:
                content = f.read()
            with open(".env", "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ .env 文件已创建")
            print("⚠️  请编辑 .env 文件，填入你的 API 密钥")
            print()
        else:
            print("❌ 未找到 .env.example 文件")
            return False
    
    return True


def create_data_dir():
    """创建数据目录"""
    if not os.path.exists("data"):
        os.makedirs("data")
        print("✅ 数据目录已创建")


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 岗位JD分析器 - MVP启动器")
    print("=" * 60)
    print()
    
    # 检查环境
    if not check_env_file():
        return
    
    # 创建数据目录
    create_data_dir()
    
    print("📋 启动选项:")
    print("1. 启动 Streamlit UI (推荐)")
    print("2. 启动 FastAPI 后端")
    print("3. 同时启动 UI 和后端")
    print("0. 退出")
    print()
    
    choice = input("请选择 (0-3): ").strip()
    
    if choice == "1":
        print("\n🎨 正在启动 Streamlit UI...")
        print("📍 访问地址: http://localhost:8501")
        print("💡 提示: 按 Ctrl+C 停止服务")
        print()
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "src/ui/app.py",
            "--server.port=8501"
        ])
    
    elif choice == "2":
        print("\n🔧 正在启动 FastAPI 后端...")
        print("📍 API文档: http://localhost:8000/docs")
        print("💡 提示: 按 Ctrl+C 停止服务")
        print()
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.api.main:app",
            "--reload",
            "--host=0.0.0.0",
            "--port=8000"
        ])
    
    elif choice == "3":
        print("\n🚀 正在同时启动 UI 和后端...")
        print("📍 Streamlit UI: http://localhost:8501")
        print("📍 API文档: http://localhost:8000/docs")
        print("💡 提示: 按 Ctrl+C 停止所有服务")
        print()
        
        # 启动后端
        backend = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "src.api.main:app",
            "--reload",
            "--host=0.0.0.0",
            "--port=8000"
        ])
        
        time.sleep(2)
        
        # 启动前端
        frontend = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run",
            "src/ui/app.py",
            "--server.port=8501"
        ])
        
        try:
            backend.wait()
            frontend.wait()
        except KeyboardInterrupt:
            print("\n\n⏹️  正在停止服务...")
            backend.terminate()
            frontend.terminate()
            print("✅ 服务已停止")
    
    elif choice == "0":
        print("👋 再见！")
    
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    main()
