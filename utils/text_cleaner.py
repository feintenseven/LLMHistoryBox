#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单文本清理工具
"""

import re
from typing import List
from datetime import datetime

class MessageRole:
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    UNKNOWN = "unknown"

class Message:
    """对话消息"""
    def __init__(self, id, role, content, timestamp=None, metadata=None):
        self.id = id
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

def clean_ai_conversation(text: str) -> str:
    """简单清理AI对话文本"""
    # 统一换行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # 移除多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()

def split_into_messages(text: str) -> List[Message]:
    """分割消息，支持多种格式"""
    messages = []
    lines = text.split('\n')

    current_role = None
    current_content = []
    msg_id = 1
    in_message = False
    skip_next_line = False
    in_metadata = False  # 标记是否在元数据部分

    for i, line in enumerate(lines):
        line = line.strip()

        # 跳过空行
        if not line:
            continue

        # 如果设置了跳过下一行
        if skip_next_line:
            skip_next_line = False
            continue

        # 检查是否进入或退出元数据部分（YAML frontmatter）
        # 只在文件开头处理YAML frontmatter
        if line == '---' and i == 0:
            in_metadata = True
            continue
        elif line == '---' and in_metadata:
            in_metadata = False
            continue

        # 如果在元数据部分，跳过所有行
        if in_metadata:
            continue

        # 跳过分隔线（但不是元数据分隔符）
        if line == '---':
            continue

        # 检查是否是DeepSeek格式的消息开始 (## User, ## Assistant等)
        # 需要确保是角色标题，而不是消息内容中的标题
        if line.startswith('## '):
            # 检查是否是角色标题（包含特定关键词或表情符号）
            is_role_line = (
                'User' in line or '用户' in line or
                'Assistant' in line or '助手' in line or
                'AI' in line or 'deepseek' in line or
                'System' in line or '系统' in line or
                '👤' in line or '🤖' in line or '⚙️' in line
            )

            if is_role_line:
                # 保存上一条消息
                if current_content and current_role:
                    messages.append(Message(
                        id=msg_id,
                        role=current_role,
                        content='\n'.join(current_content)
                    ))
                    msg_id += 1
                    current_content = []

                # 确定角色
                if 'User' in line or '用户' in line or '👤' in line:
                    current_role = MessageRole.USER
                elif 'Assistant' in line or '助手' in line or 'AI' in line or 'deepseek' in line or '🤖' in line:
                    current_role = MessageRole.ASSISTANT
                elif 'System' in line or '系统' in line or '⚙️' in line:
                    current_role = MessageRole.SYSTEM
                else:
                    current_role = MessageRole.UNKNOWN

                in_message = True
                continue
            else:
                # 这是消息内容中的标题，不是新的消息开始
                # 将其作为当前消息的内容
                if in_message and current_role:
                    current_content.append(line)
                continue

        # 检查是否是带表情符号的角色行 (👤 用户, 🤖 deepseek等)
        elif re.match(r'^[👤🤖⚙️❓]\s+', line):
            # 保存上一条消息
            if current_content and current_role:
                messages.append(Message(
                    id=msg_id,
                    role=current_role,
                    content='\n'.join(current_content)
                ))
                msg_id += 1
                current_content = []

            # 确定角色
            if '用户' in line or 'User' in line:
                current_role = MessageRole.USER
            elif 'deepseek' in line or 'AI' in line or '助手' in line or 'Assistant' in line:
                current_role = MessageRole.ASSISTANT
            elif '系统' in line or 'System' in line:
                current_role = MessageRole.SYSTEM
            else:
                current_role = MessageRole.UNKNOWN

            in_message = True
            # 跳过下一行（通常是时间戳）
            skip_next_line = True
            continue

        # 检查是否是传统格式的消息开始
        elif (line.startswith('用户:') or line.startswith('用户：') or
              line.startswith('User:') or line.startswith('Human:')):
            # 保存上一条消息
            if current_content and current_role:
                messages.append(Message(
                    id=msg_id,
                    role=current_role,
                    content='\n'.join(current_content)
                ))
                msg_id += 1
                current_content = []

            current_role = MessageRole.USER
            in_message = True
            # 移除角色前缀
            line = re.sub(r'^(用户[:：]|User[:：]|Human[:：])\s*', '', line)
            if line:
                current_content.append(line)
            continue

        elif (line.startswith('AI:') or line.startswith('AI：') or
              line.startswith('Assistant:') or line.startswith('助手:')):
            # 保存上一条消息
            if current_content and current_role:
                messages.append(Message(
                    id=msg_id,
                    role=current_role,
                    content='\n'.join(current_content)
                ))
                msg_id += 1
                current_content = []

            current_role = MessageRole.ASSISTANT
            in_message = True
            # 移除角色前缀
            line = re.sub(r'^(AI[:：]|Assistant[:：]|助手[:：])\s*', '', line)
            if line:
                current_content.append(line)
            continue

        # 跳过分隔线和HTML标签
        elif line == '---' or line.startswith('<a id='):
            continue

        # 跳过时间戳和元数据行
        elif ('T' in line and ':' in line and '-' in line) or '轮次' in line or '#' in line:
            continue

        # 如果是消息内容（以>开头的是引用内容）
        elif in_message and line:
            # 移除引用标记
            if line.startswith('> '):
                line = line[2:]
            current_content.append(line)

    # 保存最后一条消息
    if current_content and current_role:
        messages.append(Message(
            id=msg_id,
            role=current_role,
            content='\n'.join(current_content)
        ))

    return messages

def parse_markdown(text: str):
    """简单Markdown解析，转换为Streamlit可显示的格式"""
    import re

    # 如果文本为空，返回空列表
    if not text.strip():
        return [{'type': 'text', 'content': ''}]

    result = []
    lines = text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        # 检查标题 (### 标题)
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2)
            result.append({'type': 'heading', 'level': level, 'content': content})
            i += 1
            continue

        # 检查代码块开始 (```python 或 ```)
        code_block_match = re.match(r'^```(\w*)$', line)
        if code_block_match:
            language = code_block_match.group(1) or ''
            code_lines = []
            i += 1

            # 收集代码块内容
            while i < len(lines) and not re.match(r'^```$', lines[i]):
                code_lines.append(lines[i])
                i += 1

            # 跳过结束的 ```
            if i < len(lines):
                i += 1

            code_content = '\n'.join(code_lines)
            result.append({'type': 'code', 'language': language, 'content': code_content})
            continue

        # 检查无序列表项 (- 或 * 开头)
        if re.match(r'^[-*]\s+.+$', line):
            list_items = []
            while i < len(lines) and re.match(r'^[-*]\s+.+$', lines[i]):
                # 移除列表标记和空格
                item_content = re.sub(r'^[-*]\s+', '', lines[i])
                list_items.append(item_content)
                i += 1
            result.append({'type': 'unordered_list', 'items': list_items})
            continue

        # 检查有序列表项 (1. 或 1) 开头)
        if re.match(r'^\d+[.)]\s+.+$', line):
            list_items = []
            while i < len(lines) and re.match(r'^\d+[.)]\s+.+$', lines[i]):
                # 移除数字和标记
                item_content = re.sub(r'^\d+[.)]\s+', '', lines[i])
                list_items.append(item_content)
                i += 1
            result.append({'type': 'ordered_list', 'items': list_items})
            continue

        # 普通段落
        if line.strip():
            paragraph_lines = []
            while i < len(lines) and lines[i].strip():
                paragraph_lines.append(lines[i])
                i += 1

            paragraph_text = '\n'.join(paragraph_lines)

            # 处理行内格式：粗体、斜体、行内代码
            # 先处理代码块，避免干扰
            paragraph_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', paragraph_text)
            # 处理粗体
            paragraph_text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', paragraph_text)
            # 处理斜体
            paragraph_text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', paragraph_text)

            result.append({'type': 'paragraph', 'content': paragraph_text})
        else:
            # 空行
            i += 1

    # 如果没有解析出任何内容，返回原始文本
    if not result:
        result.append({'type': 'text', 'content': text})

    return result

def format_message_for_display(message):
    """格式化消息用于显示，支持Markdown"""
    return parse_markdown(message.content)