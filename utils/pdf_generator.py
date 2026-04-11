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


# =========================
# ✅ 中文 + 粗体支持（核心修复）
# =========================
def setup_chinese_support():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfmetrics import registerFontFamily

    normal_path = "C:/Windows/Fonts/msyh.ttc"
    bold_path = "C:/Windows/Fonts/msyhbd.ttc"

    if os.path.exists(normal_path) and os.path.exists(bold_path):
        pdfmetrics.registerFont(TTFont('YaHei', normal_path))
        pdfmetrics.registerFont(TTFont('YaHei-Bold', bold_path))

        registerFontFamily(
            'YaHei',
            normal='YaHei',
            bold='YaHei-Bold',
            italic='YaHei',          # 没有斜体，用正常代替
            boldItalic='YaHei-Bold'
        )

        return 'YaHei'

    # fallback
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    return 'STSong-Light'


# =========================
# 文本清理（基本保持你原逻辑）
# =========================
def clean_text_for_pdf(text):
    text = re.sub(r'\\+---', '', text)

    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', line):
            continue

        if '轮次' in line or '#' in line:
            continue

        if re.match(r'^[👤🤖⚙️❓]\s*', line):
            continue

        if 'NousSave' in line or '生成 | deepseek |' in line:
            continue

        cleaned_lines.append(line)

    cleaned_text = '\n'.join(cleaned_lines)

    cleaned_text = re.sub(r'\\\\([=*])', r'\1', cleaned_text)

    return cleaned_text


# =========================
# Markdown → ReportLab（修复重点在这里）
# =========================
def convert_markdown_to_reportlab(text, base_style):

    # -------- 代码块 --------
    def replace_code_block(match):
        code_content = match.group(2)
        code_content = code_content.replace('\n', '<br/>')
        return f'<font name="Courier">{code_content}</font>'

    text = re.sub(r'```(\w*)\n([\s\S]*?)```', replace_code_block, text)

    # -------- 标题 --------
    text = re.sub(r'^### (.+)$', r'<font size="14"><b>\1</b></font>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<font size="16"><b>\1</b></font>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<font size="18"><b>\1</b></font>', text, flags=re.MULTILINE)

    # -------- 粗体（先处理）--------
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)

    # -------- 斜体（避免冲突）--------
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', text)

    # -------- 行内代码 --------
    text = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)

    # -------- 列表 --------
    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        unordered_match = re.match(r'^[-*]\s+(.+)$', line)
        if unordered_match:
            processed_lines.append(f'• {unordered_match.group(1)}')
        else:
            ordered_match = re.match(r'^(\d+)[.)]\s+(.+)$', line)
            if ordered_match:
                processed_lines.append(f'{ordered_match.group(1)}. {ordered_match.group(2)}')
            else:
                processed_lines.append(line)

    text = '<br/>'.join(processed_lines)

    return [Paragraph(text, base_style)]


# =========================
# 主函数（接口完全保持不变）
# =========================
def create_conversation_pdf(messages, title="AI对话记录", author="", course="", date=None):

    if date is None:
        date = datetime.now()

    chinese_font = setup_chinese_support()

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
        content = clean_text_for_pdf(msg.content)

        # Markdown 转换（保持你原逻辑）
        elems = convert_markdown_to_reportlab(content, msg_style)

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