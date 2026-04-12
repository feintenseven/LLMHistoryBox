#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF渲染问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.text_cleaner import clean_ai_conversation, split_into_messages
from utils.pdf_generator import create_conversation_pdf, convert_markdown_to_reportlab
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

def test_pdf_rendering():
    """测试PDF渲染问题"""

    # 测试文本
    test_text = """python

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# 测试一下
num = 29
if is_prime(num):
    print(f"{num} 是质数")
else:
    print(f"{num} 不是质数")

运行结果：

text

29 是质数"""

    print("1. 原始文本:")
    print(test_text)

    print("\n" + "=" * 80)
    print("2. 清理后的文本:")
    cleaned = clean_ai_conversation(test_text)
    print(cleaned)

    print("\n" + "=" * 80)
    print("3. 检查代码块标识:")
    if '```python' in cleaned:
        print("✓ 找到 ```python 开始标识")
        # 找到代码块结束
        lines = cleaned.split('\n')
        in_code_block = False
        code_block_lines = []
        for i, line in enumerate(lines):
            if line.strip() == '```python':
                in_code_block = True
                print(f"   第{i}行: 代码块开始")
                continue
            elif line.strip() == '```' and in_code_block:
                in_code_block = False
                print(f"   第{i}行: 代码块结束")
                print(f"   代码块共 {len(code_block_lines)} 行")
                # 检查是否包含num = 29
                code_block_text = '\n'.join(code_block_lines)
                if 'num = 29' in code_block_text:
                    print("   ✓ 代码块中包含 'num = 29'")
                else:
                    print("   ✗ 代码块中不包含 'num = 29'")
                break
            elif in_code_block:
                code_block_lines.append(line)
    else:
        print("✗ 没有找到 ```python 开始标识")

    print("\n" + "=" * 80)
    print("4. 测试convert_markdown_to_reportlab函数:")
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'TestNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )

    # 测试转换
    elements = convert_markdown_to_reportlab(cleaned, normal_style)
    print(f"转换出 {len(elements)} 个元素")

    # 检查元素类型
    for i, elem in enumerate(elements):
        if hasattr(elem, 'style'):
            style_name = elem.style.name
            print(f"  元素 {i}: 样式={style_name}")
            if style_name == 'CodeStyle':
                print("  ✓ 这是代码块元素")
                # 获取文本内容
                text = getattr(elem, 'text', str(elem))
                if 'num = 29' in text:
                    print("  ✓ 包含 'num = 29'")
                else:
                    print("  ✗ 不包含 'num = 29'")
                    print(f"  文本内容预览: {text[:100]}...")

    print("\n" + "=" * 80)
    print("5. 完整的PDF生成测试:")
    messages = split_into_messages(cleaned)
    print(f"分割出 {len(messages)} 条消息")

    for i, msg in enumerate(messages):
        print(f"  消息 {i+1}: {msg.role}")
        if 'num = 29' in msg.content:
            print(f"  ✓ 包含 'num = 29'")
        else:
            print(f"  ✗ 不包含 'num = 29'")

    # 生成PDF
    try:
        pdf_bytes = create_conversation_pdf(
            messages=messages,
            title="测试PDF渲染",
            author="测试",
            course="测试",
            date=datetime.now()
        )
        print(f"\n✓ PDF生成成功，大小: {len(pdf_bytes)} 字节")

        # 保存PDF
        with open("test_render.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("✓ PDF已保存为 test_render.pdf")

    except Exception as e:
        print(f"\n✗ PDF生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_rendering()