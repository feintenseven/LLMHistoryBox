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

    # 修正代码块格式（将非标准格式转换为标准Markdown代码块）
    text = fix_code_block_format(text)

    # 移除多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def fix_code_block_format(text: str) -> str:
    """修正非标准的代码块格式为标准的Markdown代码块格式

    处理DeepSeek等AI工具导出的非标准代码格式：
    1. 单独的编程语言标识行（如"python"、"javascript"等）
    2. 代码内容
    3. 转换为标准格式：```language\ncode\n```

    注意：不处理text标识，text当作正常文本输出
    """
    lines = text.split('\n')
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 检查是否是编程语言标识行（排除text）
        if _is_programming_language(line):
            language = line.strip().lower()
            code_lines = []
            i += 1

            # 收集代码行，直到遇到空行或明显非代码内容
            while i < len(lines):
                next_line = lines[i]

                # 检查是否看起来像代码
                if not _looks_like_code(next_line, language):
                    # 如果不是代码，检查是否是另一个语言标识
                    if _is_programming_language(next_line) or _is_text_indicator(next_line):
                        break
                    # 如果以中文开头，停止（根据任务要求：重新出现文字开头的一行）
                    if _starts_with_chinese(next_line):
                        break

                code_lines.append(next_line)
                i += 1

            # 转换为标准代码块格式
            if code_lines:
                # 移除代码块末尾的连续空行（保留最后一个空行前的空行）
                while len(code_lines) > 1 and not code_lines[-1].strip() and not code_lines[-2].strip():
                    code_lines.pop()

                result_lines.append(f'```{language}')
                result_lines.extend(code_lines)
                result_lines.append('```')
            else:
                # 如果不是真正的代码块，保留原行
                result_lines.append(line)
                i += 1
        else:
            result_lines.append(line)
            i += 1

    return '\n'.join(result_lines)


def _is_programming_language(line: str) -> bool:
    """判断是否为编程语言标识行（排除text）"""
    line = line.strip().lower()
    if not line:
        return False

    # 只处理编程语言，不处理text
    programming_languages = {
        'python', 'javascript', 'js', 'java', 'cpp', 'c++', 'c',
        'go', 'golang', 'rust', 'html', 'css', 'bash', 'shell', 'sh',
        'sql', 'json', 'xml', 'yaml', 'yml', 'markdown', 'md',
        'typescript', 'ts', 'php', 'ruby', 'rb', 'swift', 'kotlin',
        'scala', 'r', 'matlab', 'perl', 'lua'
    }

    return line in programming_languages


def _is_text_indicator(line: str) -> bool:
    """判断是否为text标识"""
    return line.strip().lower() == 'text'


def _looks_like_code(line: str, language: str) -> bool:
    """判断一行是否看起来像代码"""
    line_stripped = line.strip()

    if not line_stripped:
        return True  # 空行可能是代码的一部分

    # 首先检查是否是明显的非代码文本
    # 检查是否以常见的非代码文本模式开头
    non_code_patterns = [
        r'^\s*[A-Z][a-z]+\s*[:：]\s*$',  # 首字母大写的单词后跟冒号（如"Result:"）
        r'^\s*[A-Z][a-z]+\s*[:：]\s*\w',  # 首字母大写的单词: 单词（如"Output: here"）
        r'^\s*运行结果\s*[:：]',  # 中文"运行结果："
        r'^\s*输出\s*[:：]',  # 中文"输出："
        r'^\s*结果\s*[:：]',  # 中文"结果："
        r'^\s*[a-z]+\s*[:：]\s*$',  # 小写单词后跟冒号，但不是代码关键字（如"result:"）
    ]

    # 排除代码关键字
    code_keywords = {'else', 'elif', 'case', 'default', 'try', 'catch', 'finally'}
    line_lower = line_stripped.lower()
    for keyword in code_keywords:
        if line_lower.startswith(keyword + ':') or line_lower.startswith(keyword + '：'):
            # 这是代码关键字后跟冒号，不是非代码文本
            return True

    for pattern in non_code_patterns:
        if re.match(pattern, line_stripped):
            return False

    # 检查常见的代码模式
    code_patterns = [
        # 缩进（Python风格）
        r'^\s{2,}',
        # 代码关键字
        r'^\s*(def|class|import|from|if|elif|else|for|while|try|except|finally|with|return|yield|async|await|print|raise|assert|break|continue|pass)\b',
        r'^\s*(function|var|let|const|export|import|from|return|throw|try|catch|finally|if|else|for|while|do|switch|case|default|break|continue)\b',
        # 括号
        r'^\s*[{}()\[\]]',
        # 变量赋值
        r'^\s*\w+\s*=\s*\w',  # 变量赋值 a = b
        # 函数调用
        r'^\s*\w+\.\w+\(',  # obj.method(
        r'^\s*\w+\(',  # function(
        # 注释
        r'^\s*#.*',
        r'^\s*//.*',
        r'^\s*/\*.*',
        r'^\s*\*.*',
        # 字符串
        r'^\s*[\'\"].*',
    ]

    for pattern in code_patterns:
        if re.match(pattern, line):
            return True

    # 检查是否包含代码中常见的运算符（在行中间）
    code_operators = ['==', '!=', '<', '>', '<=', '>=', '+=', '-=', '*=', '/=', '%=', '&&', '||']
    for op in code_operators:
        if op in line:
            return True

    # 对于简单的=，检查它是否在变量赋值中，而不是在文本中
    if '=' in line:
        # 检查是否是变量赋值模式
        if re.match(r'^\s*\w+\s*=\s*\w', line):
            return True
        # 检查是否是函数调用中的等号
        if re.search(r'\(\s*\w+\s*=\s*\w', line):
            return True

    # 检查是否是常见的代码结构
    # 包含点号的方法调用（如console.log）
    if re.search(r'\w+\.\w+', line):
        # 但排除看起来像URL或普通文本的情况
        if not re.match(r'^\s*(http|https|www|ftp)://', line_stripped):
            return True

    return False


def _starts_with_chinese(line: str) -> bool:
    """判断是否以中文开头"""
    line_stripped = line.strip()

    if not line_stripped:
        return False

    # 检查是否以中文开头
    return re.match(r'^[\u4e00-\u9fff]', line_stripped) is not None

def _is_chinese_text(line: str) -> bool:
    """判断是否为中文文本"""
    line_stripped = line.strip()

    if not line_stripped:
        return False

    # 检查是否以中文开头
    if re.match(r'^[\u4e00-\u9fff]', line_stripped):
        return True

    # 检查是否包含中文字符
    # 检查第一个字符是否为中文字符
    if line_stripped and re.match(r'[\u4e00-\u9fff]', line_stripped[0]):
        return True
    else:
        return False

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