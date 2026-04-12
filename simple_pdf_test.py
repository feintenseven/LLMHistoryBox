#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单PDF测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.text_cleaner import clean_ai_conversation, split_into_messages
from utils.pdf_generator import create_conversation_pdf
from datetime import datetime

def simple_test():
    """简单测试"""

    # 简单测试文本
    test_text = """用户：测试代码

python

print("Hello")
num = 29
print(num)

AI：这是结果

text

输出完成"""

    print("测试文本:")
    print(test_text)

    print("\n清理后:")
    cleaned = clean_ai_conversation(test_text)
    print(cleaned)

    print("\n分割消息:")
    messages = split_into_messages(cleaned)
    for i, msg in enumerate(messages):
        print(f"消息 {i+1} ({msg.role}):")
        print(msg.content[:100] + "..." if len(msg.content) > 100 else msg.content)
        print()

    # 生成PDF
    try:
        pdf_bytes = create_conversation_pdf(
            messages=messages,
            title="简单测试",
            author="测试",
            course="测试",
            date=datetime.now()
        )

        print(f"PDF生成成功! 大小: {len(pdf_bytes)} bytes")

        # 保存
        with open("simple_test.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("已保存为 simple_test.pdf")

    except Exception as e:
        print(f"PDF生成失败: {e}")

if __name__ == "__main__":
    simple_test()