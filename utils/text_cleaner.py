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

    for i, line in enumerate(lines):
        line = line.strip()

        # 跳过空行
        if not line:
            continue

        # 如果设置了跳过下一行
        if skip_next_line:
            skip_next_line = False
            continue

        # 检查是否是DeepSeek格式的消息开始 (## User, ## Assistant等)
        if line.startswith('## '):
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
            if 'User' in line or '用户' in line:
                current_role = MessageRole.USER
            elif 'Assistant' in line or '助手' in line or 'AI' in line or 'deepseek' in line:
                current_role = MessageRole.ASSISTANT
            elif 'System' in line or '系统' in line:
                current_role = MessageRole.SYSTEM
            else:
                current_role = MessageRole.UNKNOWN

            in_message = True
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

def format_message_for_display(message):
    """格式化消息用于显示"""
    # 简单实现：返回文本内容
    return [{'type': 'text', 'content': message.content}]