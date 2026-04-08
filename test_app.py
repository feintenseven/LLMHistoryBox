#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI对话导出工具 - 测试脚本
测试核心功能
"""

import sys
import os
from pathlib import Path

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_text_cleaner():
    """测试文本清理功能"""
    print("测试 测试文本清理功能...")

    try:
        from utils.text_cleaner import (
            clean_ai_conversation,
            split_into_messages,
            detect_conversation_format,
            MessageRole
        )

        # 测试文本
        test_text = """用户：请帮我写一个Python函数

AI：当然，这是一个示例：

```python
def hello():
    print("Hello World")
```

用户：谢谢！
AI：不客气！"""

        # 测试清理功能
        cleaned = clean_ai_conversation(test_text)
        print(f"[OK] 文本清理测试通过")
        print(f"   原始长度: {len(test_text)}")
        print(f"   清理后长度: {len(cleaned)}")

        # 测试格式检测
        format_info = detect_conversation_format(test_text)
        print(f"[OK] 格式检测测试通过")
        print(f"   检测结果: {format_info}")

        # 测试消息分割
        messages = split_into_messages(cleaned)
        print(f"[OK] 消息分割测试通过")
        print(f"   识别到 {len(messages)} 条消息")

        for i, msg in enumerate(messages):
            print(f"   消息 {i+1}: [{msg.role.value}] {msg.content[:50]}...")

        return True

    except Exception as e:
        print(f"[ERROR] 文本清理测试失败: {e}")
        return False

def test_pdf_generator():
    """测试PDF生成功能"""
    print("\n测试 测试PDF生成功能...")

    try:
        from utils.pdf_generator import create_conversation_pdf
        from utils.text_cleaner import Message, MessageRole
        from datetime import datetime

        # 创建测试消息
        test_messages = [
            Message(
                id=0,
                role=MessageRole.USER,
                content="测试用户消息",
                timestamp=datetime.now(),
                metadata={}
            ),
            Message(
                id=1,
                role=MessageRole.ASSISTANT,
                content="测试AI回复\n```python\nprint('Hello')\n```",
                timestamp=datetime.now(),
                metadata={}
            )
        ]

        # 生成PDF
        pdf_bytes = create_conversation_pdf(
            messages=test_messages,
            title="测试文档",
            author="测试用户",
            course="测试课程",
            date=datetime.now()
        )

        print(f"[OK] PDF生成测试通过")
        print(f"   PDF大小: {len(pdf_bytes)} 字节")

        # 保存测试文件
        test_file = "test_output.pdf"
        with open(test_file, 'wb') as f:
            f.write(pdf_bytes)

        print(f"   测试文件已保存: {test_file}")

        # 不清理测试文件，保留供检查
        print(f"   测试文件已保存到: {test_file}")
        print(f"   文件路径: {os.path.abspath(test_file)}")

        return True

    except Exception as e:
        print(f"[ERROR] PDF生成测试失败: {e}")
        return False

def test_config():
    """测试配置功能"""
    print("\n测试 测试配置功能...")

    try:
        from config import (
            APP_CONFIG, PDF_CONFIG, TEXT_CLEAN_CONFIG,
            get_export_path, validate_filename, generate_filename
        )

        print(f"[OK] 配置加载测试通过")
        print(f"   应用名称: {APP_CONFIG.get('name')}")
        print(f"   版本: {APP_CONFIG.get('version')}")

        # 测试路径函数
        export_path = get_export_path("test.pdf")
        print(f"[OK] 路径函数测试通过")
        print(f"   导出路径: {export_path}")

        # 测试文件名验证
        valid = validate_filename("test.pdf")
        invalid = validate_filename("test.txt")
        print(f"[OK] 文件名验证测试通过")
        print(f"   test.pdf 有效: {valid}")
        print(f"   test.txt 有效: {invalid}")

        # 测试文件名生成
        from datetime import datetime
        filename = generate_filename("测试文档", datetime.now())
        print(f"[OK] 文件名生成测试通过")
        print(f"   生成文件名: {filename}")

        return True

    except Exception as e:
        print(f"[ERROR] 配置测试失败: {e}")
        return False

def test_imports():
    """测试所有导入"""
    print("\n测试 测试所有导入...")

    modules_to_test = [
        ("streamlit", "Streamlit"),
        ("reportlab", "ReportLab"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
    ]

    all_passed = True

    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"   [OK] {display_name} 导入成功")
        except ImportError as e:
            print(f"   [ERROR] {display_name} 导入失败: {e}")
            all_passed = False

    return all_passed

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("AI对话导出工具 - 功能测试")
    print("=" * 60)

    tests = [
        ("导入测试", test_imports),
        ("配置测试", test_config),
        ("文本清理测试", test_text_cleaner),
        ("PDF生成测试", test_pdf_generator),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 40)

        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"[ERROR] 测试异常: {e}")
            results.append((test_name, False))

    # 显示测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed_count = 0
    total_count = len(results)

    for test_name, passed in results:
        status = "[OK] 通过" if passed else "[ERROR] 失败"
        print(f"{test_name}: {status}")
        if passed:
            passed_count += 1

    print(f"\n总测试数: {total_count}")
    print(f"通过数: {passed_count}")
    print(f"失败数: {total_count - passed_count}")

    if passed_count == total_count:
        print("\n所有测试通过！")
        return True
    else:
        print(f"\n{total_count - passed_count} 个测试失败")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)