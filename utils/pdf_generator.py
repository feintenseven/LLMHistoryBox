#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单PDF生成工具 - 支持中文的版本
使用更简单的方法确保中文显示正常
"""

from io import BytesIO
from datetime import datetime
from typing import List
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors

# 尝试使用不同的方法支持中文
def setup_chinese_support():
    """设置中文支持 - 使用更美观的字体"""
    try:
        # 方法1: 使用TTF字体 - 优先使用更美观的字体
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # 尝试更美观的中文字体路径
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑 - 更现代
            "C:/Windows/Fonts/simhei.ttf",      # 黑体 - 清晰
            "C:/Windows/Fonts/simsun.ttc",      # 宋体
            "C:/Windows/Fonts/simkai.ttf",      # 楷体
            "C:/Windows/Fonts/simfang.ttf",     # 仿宋
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # 根据字体文件设置不同的字体名称
                    if "msyh" in font_path.lower():
                        font_name = "MicrosoftYaHei"
                    elif "simhei" in font_path.lower():
                        font_name = "SimHei"
                    elif "simsun" in font_path.lower():
                        font_name = "SimSun"
                    elif "simkai" in font_path.lower():
                        font_name = "SimKai"
                    elif "simfang" in font_path.lower():
                        font_name = "SimFang"
                    else:
                        font_name = "ChineseFont"

                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"使用字体: {font_name} ({font_path})")
                    return font_name
                except Exception as e:
                    print(f"注册字体失败 {font_path}: {e}")
                    continue
    except Exception as e:
        print(f"TTF字体设置失败: {e}")

    try:
        # 方法2: 使用CID字体作为备选
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        print("使用CID字体: STSong-Light")
        return 'STSong-Light'
    except Exception as e:
        print(f"CID字体设置失败: {e}")

    # 方法3: 使用默认字体
    print("使用默认字体: Helvetica")
    return "Helvetica"

def clean_text_for_pdf(text):
    """清理文本"""
    import re

    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 移除分隔线
    text = text.replace('---', '')

    # 移除元数据行
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 跳过时间戳行
        if re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', line):
            continue

        # 跳过轮次信息
        if '轮次' in line or '#' in line:
            continue

        # 跳过表情符号行
        if re.match(r'^[👤🤖⚙️❓]\s*', line):
            continue

        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

def create_conversation_pdf(messages, title="AI对话记录", author="", course="", date=None):
    """创建对话PDF - 确保中文正常显示，添加美观的对话框样式"""
    if date is None:
        date = datetime.now()

    # 设置中文支持
    chinese_font = setup_chinese_support()

    # 创建PDF
    buffer = BytesIO()

    # 文档设置
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # 样式
    styles = getSampleStyleSheet()

    # 创建使用中文字体的样式
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

    heading_style = ParagraphStyle(
        'ChineseHeading',
        parent=styles['Heading2'],
        fontName=chinese_font,
        fontSize=14,
        spaceAfter=10
    )

    # 对话框样式 - 无填充，只有圆角边框，黑色文字
    user_bubble_style = ParagraphStyle(
        'UserBubble',
        parent=normal_style,
        fontName=chinese_font,
        fontSize=11,  # 稍微增大字体
        leading=16,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=8,
        spaceAfter=8,
        textColor=colors.black,  # 黑色文字
        borderColor=colors.HexColor('#007AFF'),  # 蓝色边框
        borderWidth=1.5,
        borderPadding=12,
        borderRadius=8,
        # 设置边框样式
        leftPadding=12,
        rightPadding=12,
        topPadding=8,
        bottomPadding=8
    )

    ai_bubble_style = ParagraphStyle(
        'AIBubble',
        parent=normal_style,
        fontName=chinese_font,
        fontSize=11,  # 稍微增大字体
        leading=16,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=8,
        spaceAfter=8,
        textColor=colors.black,  # 黑色文字
        borderColor=colors.HexColor('#34C759'),  # 绿色边框
        borderWidth=1.5,
        borderPadding=12,
        borderRadius=8,
        # 设置边框样式
        leftPadding=12,
        rightPadding=12,
        topPadding=8,
        bottomPadding=8
    )

    # 构建内容
    story = []

    # 标题
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 15))

    # 元信息
    if author:
        story.append(Paragraph(f"<b>作者:</b> {author}", normal_style))
    if course:
        story.append(Paragraph(f"<b>课程:</b> {course}", normal_style))
    story.append(Paragraph(f"<b>日期:</b> {date.strftime('%Y年%m月%d日')}", normal_style))
    story.append(Paragraph(f"<b>消息数量:</b> {len(messages)} 条", normal_style))

    story.append(Spacer(1, 20))

    # 对话内容标题
    story.append(Paragraph("对话内容", heading_style))
    story.append(Spacer(1, 15))

    # 消息
    for i, msg in enumerate(messages, 1):
        # 角色
        role_text = "用户" if msg.role == "user" else "AI助手" if msg.role == "assistant" else "系统"

        # 根据角色选择样式
        if msg.role == "user":
            bubble_style = user_bubble_style
            role_color = "#007AFF"  # 蓝色
            role_icon = "👤"
            alignment = TA_RIGHT
        else:
            bubble_style = ai_bubble_style
            role_color = "#34C759"  # 绿色
            role_icon = "🤖"
            alignment = TA_LEFT

        # 角色标签 - 放在对话框内
        role_html = f'<font color="{role_color}"><b>{role_icon} {role_text}</b></font>'

        # 内容
        content = clean_text_for_pdf(msg.content)
        if content.strip():
            # 将换行符转换为HTML换行标签
            content_with_breaks = content.replace('\n', '<br/>')

            # 将角色标签和内容合并
            full_content = f"{role_html}<br/>{content_with_breaks}"

            # 创建对话框样式的段落
            bubble_paragraph = Paragraph(full_content, bubble_style)
            story.append(bubble_paragraph)
            story.append(Spacer(1, 15))

    # 生成PDF
    doc.build(story)

    # 返回字节
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes