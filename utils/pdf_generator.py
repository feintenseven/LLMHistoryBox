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
# 段间距计算（1.5倍）
# =========================
def get_paragraph_spacing(base_style, multiplier=1.5):
    leading = getattr(base_style, 'leading', base_style.fontSize * 1.2)
    return leading * multiplier


# =========================
# 中文字体支持
# =========================
def setup_chinese_support():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfmetrics import registerFontFamily

    normal_path = "C:/Windows/Fonts/msyh.ttc"
    bold_path = "C:/Windows/Fonts/msyhbd.ttc"
    code_font_path = "C:/Windows/Fonts/simsun.ttc"

    if os.path.exists(normal_path) and os.path.exists(bold_path):
        pdfmetrics.registerFont(TTFont('YaHei', normal_path))
        pdfmetrics.registerFont(TTFont('YaHei-Bold', bold_path))

        registerFontFamily(
            'YaHei',
            normal='YaHei',
            bold='YaHei-Bold',
            italic='YaHei',
            boldItalic='YaHei-Bold'
        )

        if os.path.exists(code_font_path):
            pdfmetrics.registerFont(TTFont('SimSun', code_font_path))
            return 'YaHei', 'SimSun'
        else:
            return 'YaHei', 'YaHei'

    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    return 'STSong-Light', 'STSong-Light'


# =========================
# 文本清理
# =========================
def clean_text_for_pdf(text):
    text = re.sub(r'\\+---', '', text)

    lines = text.split('\n')
    cleaned_lines = []
    in_code_block = False

    for line in lines:
        if re.match(r'^```(\w*)$', line):
            in_code_block = not in_code_block
            cleaned_lines.append(line)
            continue

        if in_code_block:
            cleaned_lines.append(line)
            continue

        line_stripped = line.strip()

        if not line_stripped:
            cleaned_lines.append('')
            continue

        if re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', line_stripped):
            continue

        if '轮次' in line_stripped:
            continue

        if re.match(r'^#\d+$', line_stripped):
            continue

        if re.match(r'^[👤🤖⚙️❓]\s*', line_stripped):
            continue

        noussave_patterns = [
            r'NousSave.*生成.*deepseek',
            r'由.*NousSave.*生成',
            r'deepseek\s*\|\s*\d{4}/\d{1,2}/\d{1,2}',
        ]

        skip_line = False
        for pattern in noussave_patterns:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                skip_line = True
                break

        if skip_line:
            continue

        line_stripped = re.sub(r'\\+$', '', line_stripped)
        line_stripped = re.sub(r'^\\+', '', line_stripped)

        cleaned_lines.append(line_stripped)

    cleaned_text = '\n'.join(cleaned_lines)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

    return cleaned_text.strip()


# =========================
# Markdown → ReportLab
# =========================
def convert_markdown_to_reportlab(text, base_style, code_font=None):
    from reportlab.platypus import Paragraph
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    import re

    result_elements = []
    lines = text.split('\n')
    i = 0

    paragraph_spacing = 15.5  # 固定为16.0，大约是1.14倍行距

    # ===== 段落样式（关键）=====
    paragraph_style = ParagraphStyle(
        'ParagraphWithSpacing',
        parent=base_style,
        spaceAfter=paragraph_spacing,
    )

    while i < len(lines):
        line = lines[i]

        # =====================
        # code block
        # =====================
        code_match = re.match(r'^```(\w*)$', line)
        if code_match:
            code_lines = []
            i += 1

            while i < len(lines) and not re.match(r'^```$', lines[i]):
                code_lines.append(lines[i])
                i += 1

            if i < len(lines):
                i += 1

            if code_lines:
                processed_lines = []
                for l in code_lines:
                    if l.strip() == '':
                        processed_lines.append('&nbsp;')
                    else:
                        processed_lines.append(
                            l.replace('&', '&amp;')
                             .replace('<', '&lt;')
                             .replace('>', '&gt;')
                        )

                code_text = '<br/>'.join(processed_lines)

                code_style = ParagraphStyle(
                    'CodeStyle',
                    parent=base_style,
                    fontName=code_font if code_font else base_style.fontName,
                    fontSize=9,
                    leading=12,
                    leftIndent=20,
                    textColor=colors.darkblue,
                    backColor=colors.lightgrey,
                    spaceBefore=10,
                    spaceAfter=10
                )

                result_elements.append(Paragraph(code_text, code_style))

            continue

        # =====================
        # heading
        # =====================
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if heading_match:
            level = len(heading_match.group(1))
            title_text = heading_match.group(2)

            font_sizes = {1: 24, 2: 18, 3: 16, 4: 14, 5: 12, 6: 11}
            font_size = font_sizes.get(level, 16)

            title_text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', title_text)
            title_text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', title_text)

            heading_style = ParagraphStyle(
                'Heading',
                parent=base_style,
                fontSize=font_size,
                leading=font_size + 6,
                spaceBefore=15,
                spaceAfter=8
            )

            result_elements.append(Paragraph(title_text, heading_style))

            i += 1
            continue

        # =====================
        # normal text（每行都是独立段落）
        # =====================
        if line.strip():
            paragraph_text = line

            # inline format
            paragraph_text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', paragraph_text)
            paragraph_text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', paragraph_text)

            if code_font:
                paragraph_text = re.sub(
                    r'`([^`]+)`',
                    r'<font name="{}">\1</font>'.format(code_font),
                    paragraph_text
                )

            result_elements.append(Paragraph(paragraph_text, paragraph_style))

        i += 1

    # =====================
    # fallback（必须在 while 外）
    # =====================
    if not result_elements:
        result_elements.append(Paragraph('', base_style))

    return result_elements


# =========================
# 主函数
# =========================
def create_conversation_pdf(messages, title="AI对话记录", author="", course="", date=None):
    if date is None:
        date = datetime.now()

    chinese_font, code_font = setup_chinese_support()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName=chinese_font,
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=10,
        leading=14
    )

    story = []

    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 15))

    if author:
        story.append(Paragraph(f"<b>作者:</b> {author}", normal_style))
    if course:
        story.append(Paragraph(f"<b>课程:</b> {course}", normal_style))

    story.append(Paragraph(f"<b>日期:</b> {date.strftime('%Y年%m月%d日')}", normal_style))
    story.append(Paragraph(f"<b>消息数量:</b> {len(messages)} 条", normal_style))

    story.append(Spacer(1, 20))

    for idx, msg in enumerate(messages):

        is_user = msg.role == "user"

        color = "#007AFF" if is_user else "#34C759"
        role_text = "用户" if is_user else "AI助手"

        msg_style = ParagraphStyle(
            name="msg_style",
            parent=normal_style,
            fontName=chinese_font,
            fontSize=10,
            leading=14
        )

        content = clean_ai_conversation(msg.content)
        content = clean_text_for_pdf(content)

        elems = convert_markdown_to_reportlab(content, msg_style, code_font)

        header = Paragraph(
            f"<font color='{color}'><b>{role_text}</b></font>",
            msg_style
        )

        story.append(header)
        story.extend(elems)

        if idx < len(messages) - 1:
            story.append(Spacer(1, get_paragraph_spacing(normal_style, 1.5)))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes