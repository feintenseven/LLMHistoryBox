#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试num = 29不被识别为代码的问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.text_cleaner import clean_ai_conversation, _looks_like_code, _starts_with_chinese

def debug_num_29():
    """调试num = 29不被识别为代码的问题"""

    # 从testfile_deepseek.md中提取相关部分
    test_code = """python

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

    print("测试代码:")
    print(test_code)
    print("\n" + "=" * 80)

    # 清理文本
    cleaned = clean_ai_conversation(test_code)
    print("清理后的文本:")
    print(cleaned)

    print("\n" + "=" * 80)
    print("逐行分析:")
    print("=" * 80)

    lines = test_code.split('\n')
    for i, line in enumerate(lines):
        print(f"行 {i}: '{line}'")
        if line.strip() == "python":
            print(f"  这是语言标识")
        elif line.strip():
            looks_like = _looks_like_code(line, "python")
            starts_chinese = _starts_with_chinese(line)
            print(f"  _looks_like_code('python'): {looks_like}")
            print(f"  _starts_with_chinese: {starts_chinese}")
        print()

if __name__ == "__main__":
    debug_num_29()