#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本清理工具
处理从AI对话页面粘贴的混乱格式
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import datetime


class MessageRole(Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class Message:
    """对话消息数据类"""
    id: int
    role: MessageRole
    content: str
    timestamp: datetime.datetime
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


def clean_ai_conversation(text: str) -> str:
    """
    清理从AI对话页面粘贴的文本

    处理问题：
    1. 多余的换行和空格
    2. 不一致的缩进
    3. 特殊字符处理
    4. 消息分割识别

    Args:
        text: 原始对话文本

    Returns:
        清理后的文本
    """
    if not text or not text.strip():
        return ""

    # 1. 标准化换行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # 2. 清理行首行尾空格
    lines = [line.rstrip() for line in text.split('\n')]

    # 3. 合并连续空行（最多保留一个空行）
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        is_empty = not line.strip()
        if is_empty and prev_empty:
            continue  # 跳过连续的空行
        cleaned_lines.append(line)
        prev_empty = is_empty

    # 4. 清理行首的空白字符（但保留代码块的缩进）
    final_lines = []
    in_code_block = False
    code_block_indent = 0

    for line in cleaned_lines:
        # 检测代码块开始/结束
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            final_lines.append(line)
            continue

        if in_code_block:
            # 在代码块中，保留原始缩进
            final_lines.append(line)
        else:
            # 不在代码块中，清理行首空白（但保留列表项等特殊格式）
            if re.match(r'^[\s]*[•\-*]\s', line) or re.match(r'^[\s]*\d+\.\s', line):
                # 列表项：清理多余空格但保留列表标记
                line = re.sub(r'^[\s]+', '  ', line)  # 保留2空格缩进
            elif re.match(r'^[\s]*#', line):
                # Markdown标题：保留缩进
                pass
            else:
                # 普通文本：清理行首空白
                line = line.lstrip()
            final_lines.append(line)

    # 5. 重新组合文本
    cleaned_text = '\n'.join(final_lines)

    # 6. 清理多余的空格（多个空格合并为一个）
    cleaned_text = re.sub(r'[ \t]{2,}', ' ', cleaned_text)

    return cleaned_text


def identify_message_role(line: str) -> Optional[MessageRole]:
    """
    识别消息角色

    支持的模式：
    - "用户："、"User："、"Human："
    - "AI："、"Assistant："、"模型："
    - "系统："、"System："

    Args:
        line: 文本行

    Returns:
        消息角色，如果无法识别则返回None
    """
    # 定义角色识别模式（不区分大小写）
    patterns = {
        MessageRole.USER: [
            r'^用户[:：]\s*',
            r'^User[:：]\s*',
            r'^Human[:：]\s*',
            r'^提问[:：]\s*',
            r'^Q[:：]\s*',
            r'^我[:：]\s*',
            r'^提问者[:：]\s*',
        ],
        MessageRole.ASSISTANT: [
            r'^AI[:：]\s*',
            r'^Assistant[:：]\s*',
            r'^模型[:：]\s*',
            r'^回答[:：]\s*',
            r'^A[:：]\s*',
            r'^助手[:：]\s*',
            r'^Claude[:：]\s*',
            r'^ChatGPT[:：]\s*',
            r'^GPT[:：]\s*',
        ],
        MessageRole.SYSTEM: [
            r'^系统[:：]\s*',
            r'^System[:：]\s*',
        ]
    }

    for role, role_patterns in patterns.items():
        for pattern in role_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return role

    return None


def extract_role_prefix(line: str) -> Tuple[Optional[MessageRole], str]:
    """
    提取消息角色前缀并返回剩余内容

    Args:
        line: 文本行

    Returns:
        (角色, 剩余内容)
    """
    role = identify_message_role(line)
    if role:
        # 找到匹配的角色前缀并移除
        for pattern in [
            r'^用户[:：]\s*', r'^User[:：]\s*', r'^Human[:：]\s*',
            r'^AI[:：]\s*', r'^Assistant[:：]\s*', r'^模型[:：]\s*',
            r'^系统[:：]\s*', r'^System[:：]\s*'
        ]:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                remaining = line[match.end():].strip()
                return role, remaining

    return None, line.strip()


def split_into_messages(text: str) -> List[Message]:
    """
    将对话文本分割成单独的消息

    Args:
        text: 清理后的对话文本

    Returns:
        消息对象列表
    """
    if not text:
        return []

    messages = []
    lines = text.split('\n')

    current_role = None
    current_content = []
    message_id = 0

    for line in lines:
        # 尝试识别新消息的开始
        role, remaining = extract_role_prefix(line)

        if role:
            # 保存上一条消息（如果有）
            if current_role is not None and current_content:
                message = Message(
                    id=message_id,
                    role=current_role,
                    content='\n'.join(current_content).strip(),
                    timestamp=datetime.datetime.now(),
                    metadata={"source": "parsed"}
                )
                messages.append(message)
                message_id += 1
                current_content = []

            # 开始新消息
            current_role = role
            if remaining:  # 如果这一行有内容
                current_content.append(remaining)
        else:
            # 继续当前消息
            if current_role is not None:
                current_content.append(line)
            else:
                # 如果没有识别到角色，可能是对话开始前的文本
                # 尝试根据内容推断角色
                if not messages and current_content:
                    # 第一条消息，假设是用户
                    current_role = MessageRole.USER
                    current_content.append(line)
                elif messages:
                    # 添加到上一条消息
                    if current_content:
                        current_content.append(line)

    # 保存最后一条消息
    if current_role is not None and current_content:
        message = Message(
            id=message_id,
            role=current_role,
            content='\n'.join(current_content).strip(),
            timestamp=datetime.datetime.now(),
            metadata={"source": "parsed"}
        )
        messages.append(message)

    # 如果没有识别到任何消息，将整个文本作为一条消息
    if not messages and text.strip():
        message = Message(
            id=0,
            role=MessageRole.UNKNOWN,
            content=text.strip(),
            timestamp=datetime.datetime.now(),
            metadata={"source": "fallback"}
        )
        messages.append(message)

    return messages


def format_for_preview(messages: List[Message]) -> str:
    """
    将消息列表格式化为预览文本

    Args:
        messages: 消息对象列表

    Returns:
        格式化后的预览文本
    """
    if not messages:
        return ""

    preview_lines = []

    for msg in messages:
        # 添加角色标签
        if msg.role == MessageRole.USER:
            role_label = "👤 用户"
        elif msg.role == MessageRole.ASSISTANT:
            role_label = "🤖 AI助手"
        elif msg.role == MessageRole.SYSTEM:
            role_label = "⚙️ 系统"
        else:
            role_label = "❓ 未知"

        preview_lines.append(f"{role_label}:")
        preview_lines.append("-" * 40)

        # 添加消息内容
        content_lines = msg.content.split('\n')
        for content_line in content_lines:
            preview_lines.append(f"  {content_line}")

        preview_lines.append("")  # 空行分隔

    return '\n'.join(preview_lines)


def detect_conversation_format(text: str) -> Dict:
    """
    检测对话文本的格式类型

    Args:
        text: 对话文本

    Returns:
        格式检测结果
    """
    lines = text.split('\n')[:10]  # 检查前10行

    format_info = {
        "has_role_markers": False,
        "has_code_blocks": False,
        "has_markdown": False,
        "estimated_format": "unknown"
    }

    # 检查角色标记
    role_patterns = [
        r'用户[:：]', r'User[:：]', r'Human[:：]',
        r'AI[:：]', r'Assistant[:：]', r'模型[:：]'
    ]

    for line in lines:
        for pattern in role_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                format_info["has_role_markers"] = True
                break

        # 检查代码块
        if '```' in line:
            format_info["has_code_blocks"] = True

        # 检查Markdown
        if re.match(r'^#+\s', line) or re.match(r'^[\*\-]\s', line):
            format_info["has_markdown"] = True

    # 推断格式类型
    if format_info["has_role_markers"]:
        format_info["estimated_format"] = "standard_ai"
    elif format_info["has_code_blocks"]:
        format_info["estimated_format"] = "code_heavy"
    elif format_info["has_markdown"]:
        format_info["estimated_format"] = "markdown"
    else:
        format_info["estimated_format"] = "plain_text"

    return format_info


# 测试函数
if __name__ == "__main__":
    # 测试用例
    test_text = """
    用户：请帮我写一个Python函数，计算斐波那契数列

    AI：当然，这是一个计算斐波那契数列的Python函数：

    ```python
    def fibonacci(n):
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        elif n == 2:
            return [0, 1]

        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        return fib
    ```

    用户：谢谢！这个函数的时间复杂度是多少？

    AI：这个函数的时间复杂度是O(n)，空间复杂度也是O(n)。
    """

    print("原始文本:")
    print(test_text)
    print("\n" + "="*50 + "\n")

    cleaned = clean_ai_conversation(test_text)
    print("清理后文本:")
    print(cleaned)
    print("\n" + "="*50 + "\n")

    messages = split_into_messages(cleaned)
    print(f"识别到 {len(messages)} 条消息:")
    for msg in messages:
        print(f"[{msg.role.value}] {msg.content[:50]}...")

    print("\n" + "="*50 + "\n")

    preview = format_for_preview(messages)
    print("预览格式:")
    print(preview)

    print("\n" + "="*50 + "\n")

    format_info = detect_conversation_format(test_text)
    print("格式检测:")
    for key, value in format_info.items():
        print(f"  {key}: {value}")