#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI对话导出工具 - 启动脚本
"""

import subprocess
import sys

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import reportlab
        print("[OK] 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"[ERROR] 缺少依赖: {e}")
        print("正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("[OK] 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False

def main():
    """主函数"""
    print("AI对话导出工具")
    print("=" * 40)

    print("正在检查依赖...")
    if not check_dependencies():
        print("请先安装依赖后再运行")
        return

    print("\n启动应用...")
    print("应用将在浏览器中打开，请稍候...")
    print("如果浏览器没有自动打开，请访问: http://localhost:8501")
    print("按 Ctrl+C 停止应用")
    print("-" * 40)

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n应用已停止")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()