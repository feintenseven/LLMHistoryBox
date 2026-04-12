#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试转义字符对代码识别的影响
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.text_cleaner import _looks_like_code

def debug_escape_chars():
    """调试转义字符对代码识别的影响"""

    test_lines = [
        "def is_prime(n):",  # 正常
        "def is\\_prime(n):",  # 有转义
        "# 测试一下",  # 正常注释
        "\\# 测试一下",  # 转义注释
        "i = 5",  # 正常赋值
        "i \\= 5",  # 转义赋值
        "i * i",  # 正常乘法
        "i \\* i",  # 转义乘法
        "n % i == 0",  # 正常比较
        "n % i \\== 0",  # 转义比较
        "num = 29",  # 正常
        "if is_prime(num):",  # 正常
        "print(f\"{num} 是质数\")",  # 正常
    ]

    print("测试转义字符对代码识别的影响")
    print("=" * 80)
    print(f"{'代码行':<30} {'_looks_like_code':<20}")
    print("-" * 80)

    for line in test_lines:
        result = _looks_like_code(line, "python")
        print(f"{line:<30} {result:<20}")

if __name__ == "__main__":
    debug_escape_chars()