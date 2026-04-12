#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io import BytesIO
from datetime import datetime
from typing import List
import os
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from utils.text_cleaner import clean_ai_conversation


# =========================
# ✅ 中文 + 粗体支持（核心修复）
# =========================
def setup_chinese_support():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfmetrics import registerFontFamily

    # 主要字体：微软雅黑（用于正文）
    normal_path = "C:/Windows/Fonts/msyh.ttc"
    bold_path = "C:/Windows/Fonts/msyhbd.ttc"

    # 代码字体：SimSun（用于代码块，支持中文）
    code_font_path = "C:/Windows/Fonts/simsun.ttc"

    if os.path.exists(normal_path) and os.path.exists(bold_path):
        # 注册正文字体
        pdfmetrics.registerFont(TTFont('YaHei', normal_path))
        pdfmetrics.registerFont(TTFont('YaHei-Bold', bold_path))

        registerFontFamily(
            'YaHei',
            normal='YaHei',
            bold='YaHei-Bold',
            italic='YaHei',          # 没有斜体，用正常代替
            boldItalic='YaHei-Bold'
        )

        # 注册代码字体（如果存在）
        if os.path.exists(code_font_path):
            pdfmetrics.registerFont(TTFont('SimSun', code_font_path))
            # 返回字体名称元组：(正文字体, 代码字体)
            return 'YaHei', 'SimSun'
        else:
            # 如果没有代码字体，使用正文字体
            return 'YaHei', 'YaHei'

    # fallback
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    return 'STSong-Light', 'STSong-Light'


# =========================
# 文本清理（基本保持你原逻辑）
# =========================
def clean_text_for_pdf(text):
    # 1. 移除转义的分隔线
    text = re.sub(r'\\+---', '', text)

    lines = text.split('\n')
    cleaned_lines = []
    in_code_block = False

    for line in lines:
        # 检查是否进入或退出代码块
        if re.match(r'^```(\w*)$', line):
            in_code_block = not in_code_block
            cleaned_lines.append(line)
            continue

        if in_code_block:
            # 在代码块内，保留原样（包括缩进）
            cleaned_lines.append(line)
            continue

        # 不在代码块内，进行清理
        line_stripped = line.strip()
        if not line_stripped:
            # 空行，但如果是代码块后的空行，可能需要保留
            cleaned_lines.append('')
            continue

        # 2. 跳过时间戳行
        if re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', line_stripped):
            continue

        # 3. 跳过轮次和编号信息
        # 只删除作为元数据的#，不删除代码中的#（注释）
        if '轮次' in line_stripped:
            continue

        # 检查是否是消息编号（如 #1, #2 等）
        if re.match(r'^#\d+$', line_stripped):
            continue

        # 4. 跳过表情符号行
        if re.match(r'^[👤🤖⚙️❓]\s*', line_stripped):
            continue

        # 5. 增强NousSave签名检测
        # 匹配不同格式的签名
        noussave_patterns = [
            r'NousSave.*生成.*deepseek',
            r'由.*NousSave.*生成',
            r'生成\s*\|\s*deepseek\s*\|\s*\d{4}/\d{1,2}/\d{1,2}',
            r'deepseek\s*\|\s*\d{4}/\d{1,2}/\d{1,2}',
            r'导出时间:.*NousSave',
            r'NousSave Ai Chat Exporter',
        ]

        skip_line = False
        for pattern in noussave_patterns:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                skip_line = True
                break

        if skip_line:
            continue

        # 6. 删除行尾多余的反斜杠
        # 匹配行尾的一个或多个反斜杠
        line_stripped = re.sub(r'\\+$', '', line_stripped)

        # 7. 删除行首多余的反斜杠（如果不是转义字符的一部分）
        line_stripped = re.sub(r'^\\+', '', line_stripped)

        cleaned_lines.append(line_stripped)

    cleaned_text = '\n'.join(cleaned_lines)

    # 8. 全局清理转义字符
    # 处理常见的转义字符组合
    escape_patterns = [
        (r'\\\\([=*])', r'\1'),      # \\= -> =, \\* -> *
        (r'\\\\([_#])', r'\1'),      # \\_ -> _, \\# -> #
        (r'\\\\\\([{}()\[\]])', r'\1'),  # \\\{ -> {, 等等
    ]

    for pattern, replacement in escape_patterns:
        cleaned_text = re.sub(pattern, replacement, cleaned_text)

    # 9. 删除连续的空行
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

    # 10. 删除文档末尾的冗余签名（跨多行）
    # 匹配常见的结尾签名模式
    end_patterns = [
        r'\n.*NousSave.*\n.*deepseek.*\n.*\d{4}/\d{1,2}/\d{1,2}.*$',
        r'\n.*生成\s*\|\s*deepseek\s*\|\s*\d{4}/\d{1,2}/\d{1,2}.*$',
        r'\n.*由.*NousSave.*生成.*$',
    ]

    for pattern in end_patterns:
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL | re.IGNORECASE)

    return cleaned_text.strip()


# =========================
# Markdown → ReportLab（修复重点在这里）
# =========================
def convert_markdown_to_reportlab(text, base_style, code_font=None):
    from reportlab.platypus import Paragraph
    from html import escape

    result_elements = []
    lines = text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # 检查是否是代码块开始
        code_match = re.match(r'^```(\w*)$', line)
        if code_match:
            language = code_match.group(1)
            code_lines = []
            i += 1

            # 收集代码行，直到代码块结束
            while i < len(lines) and not re.match(r'^```$', lines[i]):
                code_lines.append(lines[i])
                i += 1

            # 跳过结束的 ```
            if i < len(lines):
                i += 1

            # 创建代码块段落
            if code_lines:
                # 处理代码行，确保空行被正确表示
                processed_lines = []
                for line in code_lines:
                    if line.strip() == '':  # 空行
                        processed_lines.append('&nbsp;')  # 使用非断空格保持空行
                    else:
                        # HTML 转义代码内容
                        escaped_line = escape(line)
                        processed_lines.append(escaped_line)

                # 将换行符转换为<br/>标签，以便Paragraph正确显示
                code_text = '<br/>'.join(processed_lines)
                # 创建代码样式
                code_style = ParagraphStyle(
                    'CodeStyle',
                    parent=base_style,
                    fontName=code_font if code_font else base_style.fontName,
                    fontSize=9,  # 代码字体稍小
                    leading=12,
                    leftIndent=20,  # 代码缩进
                    textColor=colors.darkblue,  # 代码颜色
                    backColor=colors.lightgrey,  # 背景色
                    borderPadding=5,
                    spaceBefore=6,
                    spaceAfter=6
                )
                result_elements.append(Paragraph(code_text, code_style))
            continue

        # 检查是否是标题（# ## ### 等）
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if heading_match:
            level = len(heading_match.group(1))  # # 的数量
            title_text = heading_match.group(2)

            # 根据标题级别设置字体大小
            font_sizes = {1: 24, 2: 18, 3: 16, 4: 14, 5: 12, 6: 11}
            font_size = font_sizes.get(level, 16)

            # 处理标题内的粗体、斜体等格式
            title_text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', title_text)
            title_text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', title_text)

            heading_style = ParagraphStyle(
                'HeadingStyle',
                parent=base_style,
                fontName=base_style.fontName,
                fontSize=font_size,
                leading=font_size + 6,
                spaceBefore=12,
                spaceAfter=6,
                textColor=colors.black
            )

            result_elements.append(Paragraph(title_text, heading_style))
            i += 1
            continue

        # 普通文本
        if line.strip():
            # 处理当前段落
            paragraph_lines = []
            while i < len(lines) and lines[i].strip() and not re.match(r'^```', lines[i]) and not re.match(
                    r'^#{1,6}\s+', lines[i]):
                paragraph_lines.append(lines[i])
                i += 1

            if paragraph_lines:
                paragraph_text = '<br/>'.join(paragraph_lines)

                # 处理行内格式
                # 粗体
                paragraph_text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', paragraph_text)
                # 斜体
                paragraph_text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', paragraph_text)
                # 行内代码
                if code_font:
                    paragraph_text = re.sub(r'`([^`]+)`', r'<font name="{}">\1</font>'.format(code_font),
                                            paragraph_text)

                result_elements.append(Paragraph(paragraph_text, base_style))
        else:
            # 空行
            i += 1

    # 如果没有元素，添加空段落
    if not result_elements:
        result_elements.append(Paragraph('', base_style))

    return result_elements


# =========================
# 主函数（接口完全保持不变）
# =========================
def create_conversation_pdf(messages, title="AI对话记录", author="", course="", date=None):

    if date is None:
        date = datetime.now()

    chinese_font, code_font = setup_chinese_support()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ChineseTitle',
        parent=styles['Title'],
        fontName=chinese_font,
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER
    )

    normal_style = ParagraphStyle(
        'ChineseNormal',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=10,
        leading=14
    )

    story = []

    # 标题
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 15))

    # 元信息（保留原接口）
    if author:
        story.append(Paragraph(f"<b>作者:</b> {author}", normal_style))
    if course:
        story.append(Paragraph(f"<b>课程:</b> {course}", normal_style))

    story.append(Paragraph(f"<b>日期:</b> {date.strftime('%Y年%m月%d日')}", normal_style))
    story.append(Paragraph(f"<b>消息数量:</b> {len(messages)} 条", normal_style))

    story.append(Spacer(1, 20))

    # 内容
    for msg in messages:

        is_user = msg.role == "user"

        # ===== 颜色与对齐 =====
        if is_user:
            color = "#007AFF"  # 蓝
            align = TA_RIGHT
            role_text = "用户"
        else:
            color = "#34C759"  # 绿
            align = TA_LEFT
            role_text = "AI助手"

        # ===== style（关键：控制对齐）=====
        msg_style = ParagraphStyle(
            name="msg_style",
            parent=normal_style,
            fontName=chinese_font,
            fontSize=10,
            leading=14,
            alignment=align,  # ⭐关键：左右对齐
        )

        # ===== 内容 =====
        # 先转换代码块格式，再清理文本
        content = clean_ai_conversation(msg.content)  # 转换非标准代码块格式
        content = clean_text_for_pdf(content)         # 清理文本用于PDF

        # Markdown 转换（传递代码字体）
        elems = convert_markdown_to_reportlab(content, msg_style, code_font)

        # ===== 拼接颜色标题 + 黑色正文 =====
        header = Paragraph(
            f"<font color='{color}'><b>{role_text}</b></font>",
            msg_style
        )

        story.append(header)

        # 正文（黑色）
        story.extend(elems)

        story.append(Spacer(1, 12))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes