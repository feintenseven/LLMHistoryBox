#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF转换器
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.pdf_generator import convert_markdown_to_reportlab
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def test_converter():
    """测试PDF转换器"""

    # 测试1: 包含代码块的文本
    test1 = """用户：测试

```python
print("Hello")
num = 29
print(num)
```

AI：回复"""

    print("测试1 - 标准Markdown代码块:")
    print(test1)

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'TestNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )

    elements = convert_markdown_to_reportlab(test1, normal_style)
    print(f"转换出 {len(elements)} 个元素")

    for i, elem in enumerate(elements):
        if hasattr(elem, 'style'):
            style_name = elem.style.name
            print(f"  元素 {i}: 样式={style_name}")
            if style_name == 'CodeStyle':
                print("  ✓ 代码块")
                text = getattr(elem, 'text', str(elem))
                if 'num = 29' in text:
                    print("  ✓ 包含 'num = 29'")
                else:
                    print("  ✗ 不包含 'num = 29'")
                    print(f"    文本: {text[:50]}...")

    print("\n" + "=" * 80)

    # 测试2: 清理后的文本（可能有问题）
    test2 = """用户：测试

```python

print("Hello")
num = 29
print(num)

AI：回复

```

text

输出"""

    print("测试2 - 清理后的文本（注意代码块包含AI：回复）:")
    print(test2)

    elements2 = convert_markdown_to_reportlab(test2, normal_style)
    print(f"转换出 {len(elements2)} 个元素")

    for i, elem in enumerate(elements2):
        if hasattr(elem, 'style'):
            style_name = elem.style.name
            print(f"  元素 {i}: 样式={style_name}")
            if style_name == 'CodeStyle':
                print("  ✓ 代码块")
                text = getattr(elem, 'text', str(elem))
                if 'num = 29' in text:
                    print("  ✓ 包含 'num = 29'")
                else:
                    print("  ✗ 不包含 'num = 29'")
                if 'AI：回复' in text:
                    print("  ⚠ 包含 'AI：回复'（不应该在代码块中）")

if __name__ == "__main__":
    test_converter()