"""简化的服务启动脚本"""

import subprocess
import sys
import time
import os

def start_service(name, command, log_file):
    """启动服务"""
    print(f"🚀 启动 {name}...")
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 打开日志文件
    log_path = os.path.join("logs", log_file)
    log = open(log_path, "w", encoding="utf-8", buffering=1)
    
    # 启动进程
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=log,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    
    print(f"   ✓ {name} 已启动 (PID: {process.pid})")
    return process

def main():
    print("=" * 60)
    print("岗位JD分析器 - 启动所有服务")
    print("=" * 60)
    print()
    
    processes = []
    
    try:
        # 1. 启动 API 服务
        api_process = start_service(
            "API服务",
            "python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000",
            "api.log"
        )
        processes.append(("API", api_process))
        time.sleep(3)
        
        # 2. 启动 Streamlit UI
        ui_process = start_service(
            "Streamlit UI",
            "python -m streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0",
            "ui.log"
        )
        processes.append(("UI", ui_process))
        time.sleep(3)
        
        print()
        print("=" * 60)
        print("✅ 所有服务已启动！")
        print("=" * 60)
        print()
        print("访问地址：")
        print("  - Streamlit UI: http://localhost:8501")
        print("  - API文档: http://localhost:8000/docs")
        print("  - API健康检查: http://localhost:8000/health")
        print()
        print("查看日志：")
        print("  - logs/api.log")
        print("  - logs/ui.log")
        print()
        print("进程信息：")
        for name, proc in processes:
            print(f"  - {name}: PID {proc.pid}")
        print()
        print("按 Ctrl+C 停止所有服务")
        print("=" * 60)
        
        # 保持运行
        while True:
            time.sleep(1)
            # 检查进程是否还在运行
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"⚠️  {name} 已停止")
                    
    except KeyboardInterrupt:
        print("\n\n停止所有服务...")
        for name, proc in processes:
            print(f"  停止 {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("✓ 所有服务已停止")

if __name__ == "__main__":
    main()
