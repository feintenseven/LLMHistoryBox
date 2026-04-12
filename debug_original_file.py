#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试原始文件中的问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.text_cleaner import clean_ai_conversation

def debug_original_file():
    """调试原始文件中的问题"""

    # 读取原始文件
    with open('testfile_deepseek.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取包含代码的部分
    lines = content.split('\n')
    start = None
    end = None

    for i, line in enumerate(lines):
        if 'python' in line and start is None:
            start = i
        if '运行结果：' in line and start is not None and end is None:
            end = i + 5  # 多取几行

    if start is not None and end is not None:
        code_section = '\n'.join(lines[start:end])
        print("原始文件中的代码部分:")
        print(code_section)

        print("\n" + "=" * 80)
        print("清理后的文本:")
        cleaned = clean_ai_conversation(code_section)
        print(cleaned)

        # 检查是否包含num = 29
        if 'num = 29' in cleaned:
            print("\n✓ num = 29 在清理后的文本中")
        else:
            print("\n✗ num = 29 不在清理后的文本中")

        # 检查代码块结束位置
        if '```' in cleaned:
            parts = cleaned.split('```')
            if len(parts) >= 3:
                code_block = parts[1]
                print(f"\n代码块内容（前200字符）:")
                print(code_block[:200])

                # 检查num = 29是否在代码块中
                if 'num = 29' in code_block:
                    print("✓ num = 29 在代码块中")
                else:
                    print("✗ num = 29 不在代码块中")

if __name__ == "__main__":
    debug_original_file()