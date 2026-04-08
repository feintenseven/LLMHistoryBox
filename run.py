#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI对话导出工具 - 启动脚本
提供多个版本选择
"""

import subprocess
import sys
import os
from pathlib import Path

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import reportlab
        import pandas
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

def show_menu():
    """显示菜单"""
    print("=" * 60)
    print("AI对话导出工具 - 版本选择")
    print("=" * 60)
    print()
    print("请选择要运行的版本:")
    print("1. 增强版 (推荐) - 现代化界面，更多功能")
    print("2. 基础版 - 简洁界面，基本功能")
    print("3. 测试模式 - 运行单元测试")
    print("4. 查看文档")
    print("5. 退出")
    print()

def run_enhanced_version():
    """运行增强版"""
    print("启动增强版应用...")
    print("应用将在浏览器中打开，请稍候...")
    print("如果浏览器没有自动打开，请访问: http://localhost:8501")
    print("按 Ctrl+C 停止应用")
    print("-" * 60)

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app_enhanced.py"])
    except KeyboardInterrupt:
        print("\n应用已停止")
    except Exception as e:
        print(f"启动失败: {e}")

def run_basic_version():
    """运行基础版"""
    print("启动基础版应用...")
    print("应用将在浏览器中打开，请稍候...")
    print("如果浏览器没有自动打开，请访问: http://localhost:8501")
    print("按 Ctrl+C 停止应用")
    print("-" * 60)

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n应用已停止")
    except Exception as e:
        print(f"启动失败: {e}")

def run_tests():
    """运行测试"""
    print("运行测试...")
    print("-" * 60)

    try:
        # 运行文本清理测试
        print("运行文本清理测试...")
        subprocess.run([sys.executable, "-m", "pytest", "utils/text_cleaner.py::__main__", "-v"])

        # 运行PDF生成测试
        print("\n运行PDF生成测试...")
        subprocess.run([sys.executable, "-m", "pytest", "utils/pdf_generator.py::__main__", "-v"])

        print("\n[OK] 测试完成")
    except Exception as e:
        print(f"测试失败: {e}")

def show_documentation():
    """显示文档"""
    print("文档")
    print("=" * 60)

    # 读取README
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
            print(content)
    except FileNotFoundError:
        print("README.md 文件不存在")

    print("\n" + "=" * 60)
    print("项目结构:")

    # 显示项目结构
    for root, dirs, files in os.walk("."):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")

        subindent = " " * 2 * (level + 1)
        for file in files:
            if not file.startswith('.'):
                print(f"{subindent}{file}")

    print("\n" + "=" * 60)
    input("按 Enter 键返回菜单...")

def main():
    """主函数"""
    print("正在检查依赖...")
    if not check_dependencies():
        print("请先安装依赖后再运行")
        return

    while True:
        show_menu()

        try:
            choice = input("请输入选择 (1-5): ").strip()

            if choice == "1":
                run_enhanced_version()
            elif choice == "2":
                run_basic_version()
            elif choice == "3":
                run_tests()
            elif choice == "4":
                show_documentation()
            elif choice == "5":
                print("再见！")
                break
            else:
                print("[ERROR] 无效选择，请重新输入")
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()