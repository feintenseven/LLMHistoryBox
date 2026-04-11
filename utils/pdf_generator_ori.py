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
    """清理文本，保留Markdown格式，删除冗余内容"""
    import re

    # 移除HTML标签但保留Markdown
    # 不在这里移除HTML标签，因为可能包含格式化标签

    # 移除分隔线（包括转义的分隔线）
    text = re.sub(r'\\+---', '', text)

    # 移除元数据行和冗余内容
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

        # 跳过NousSave导出器签名
        if 'NousSave' in line or '生成 | deepseek |' in line:
            continue

        cleaned_lines.append(line)

    cleaned_text = '\n'.join(cleaned_lines)

    # 处理Markdown转义字符（在代码块中常见的）
    # 例如：\\* 应该转换为 *，\\== 应该转换为 ==
    cleaned_text = re.sub(r'\\\\([=*])', r'\1', cleaned_text)

    return cleaned_text

def convert_markdown_to_reportlab(text, base_style):
    """将Markdown文本转换为ReportLab格式，使用基础样式"""
    import re
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors

    # 首先处理Markdown转换为简单HTML
    # ReportLab的Paragraph支持有限的HTML标签：<b>, <i>, <u>, <font>, <br/>, <bullet>, <seq>

    # 处理代码块（先处理，避免干扰其他处理）
    # 使用更稳健的匹配方式
    def replace_code_block(match):
        language = match.group(1) or ''
        code_content = match.group(2)
        # 将代码内容中的换行符转换为<br/>
        code_content = code_content.replace('\n', '<br/>')
        return f'<font name="Courier" color="#0066CC">{code_content}</font>'

    text = re.sub(r'```(\w*)\n([\s\S]*?)```', replace_code_block, text)

    # 处理标题
    text = re.sub(r'^### (.+)$', r'<font size="14"><b>\1</b></font><br/>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<font size="16"><b>\1</b></font><br/>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<font size="18"><b>\1</b></font><br/>', text, flags=re.MULTILINE)

    # 处理粗体 - 使用<strong>或<b>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)

    # 处理斜体 - 使用<i>标签，ReportLab支持
    text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)

    # 处理行内代码 - 使用等宽字体并加粗
    text = re.sub(r'`([^`]+)`', r'<font name="Courier"><b>\1</b></font>', text)

    # 处理列表 - 使用简单的项目符号字符
    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        # 检查无序列表项
        unordered_match = re.match(r'^[-*]\s+(.+)$', line)
        if unordered_match:
            # 使用Unicode项目符号字符
            processed_lines.append(f'• {unordered_match.group(1)}')
        else:
            # 检查有序列表项
            ordered_match = re.match(r'^(\d+)[.)]\s+(.+)$', line)
            if ordered_match:
                # 保持原数字格式
                num = ordered_match.group(1)
                content = ordered_match.group(2)
                processed_lines.append(f'{num}. {content}')
            else:
                processed_lines.append(line)

    text = '\n'.join(processed_lines)

    # 将换行符转换为<br/>
    text = text.replace('\n', '<br/>')

    # 创建Paragraph
    if text.strip():
        return [Paragraph(text, base_style)]
    else:
        return []

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

        # 内容 - 使用Markdown转换
        content = clean_text_for_pdf(msg.content)
        if content.strip():
            # 将角色标签添加到内容开头
            role_html = f'<font color="{role_color}"><b>{role_icon} {role_text}</b></font><br/>'
            full_content = role_html + content

            # 转换Markdown内容
            markdown_elements = convert_markdown_to_reportlab(full_content, bubble_style)

            # 将转换后的元素添加到story中
            for elem in markdown_elements:
                story.append(elem)

            story.append(Spacer(1, 15))

    # 生成PDF
    doc.build(story)

    # 返回字节
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes