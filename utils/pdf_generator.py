#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF生成工具
使用ReportLab生成格式清晰的对话PDF
"""

import os
import tempfile
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, PageTemplate, Frame, NextPageTemplate
)
from reportlab.platypus.flowables import Image
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 导入消息类型
from .text_cleaner import Message, MessageRole


class PDFGenerator:
    """PDF生成器类"""

    def __init__(self, page_size='A4', margin=1*inch):
        """
        初始化PDF生成器

        Args:
            page_size: 页面尺寸 ('A4' 或 'letter')
            margin: 页边距（英寸）
        """
        self.page_size = A4 if page_size == 'A4' else letter
        self.margin = margin

        # 注册中文字体
        self._register_chinese_fonts()

        self.styles = self._create_styles()

    def _register_chinese_fonts(self):
        """注册中文字体"""
        try:
            # 尝试注册常见的中文字体
            # Windows系统常见中文字体
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",      # 黑体
                "C:/Windows/Fonts/simsun.ttc",      # 宋体
                "C:/Windows/Fonts/simkai.ttf",      # 楷体
                "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
                "C:/Windows/Fonts/msyhbd.ttc",      # 微软雅黑粗体
            ]

            registered = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        if "simhei" in font_path.lower():
                            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                            pdfmetrics.registerFont(TTFont('ChineseFont-Bold', font_path))
                            self.chinese_font = 'ChineseFont'
                            registered = True
                            break
                        elif "msyh" in font_path.lower():
                            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                            pdfmetrics.registerFont(TTFont('ChineseFont-Bold', font_path))
                            self.chinese_font = 'ChineseFont'
                            registered = True
                            break
                        elif "simsun" in font_path.lower():
                            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                            pdfmetrics.registerFont(TTFont('ChineseFont-Bold', font_path))
                            self.chinese_font = 'ChineseFont'
                            registered = True
                            break
                    except Exception as e:
                        print(f"注册字体 {font_path} 失败: {e}")
                        continue

            if not registered:
                # 如果没有找到中文字体，使用默认字体
                self.chinese_font = 'Helvetica'
                print("警告: 未找到中文字体，使用默认字体")
        except Exception as e:
            print(f"注册中文字体时出错: {e}")
            self.chinese_font = 'Helvetica'

    def _create_styles(self):
        """创建PDF样式"""
        styles = getSampleStyleSheet()

        # 基础字体设置
        base_font_name = self.chinese_font

        # 自定义样式
        # 标题样式
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontName=base_font_name,
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        ))

        # 副标题样式
        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontName=base_font_name,
            fontSize=18,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        ))

        # 用户消息样式
        styles.add(ParagraphStyle(
            name='UserMessage',
            parent=styles['Normal'],
            fontName=base_font_name,
            fontSize=11,
            leftIndent=20,
            rightIndent=60,
            spaceBefore=6,
            spaceAfter=6,
            backColor=colors.HexColor('#f8f9fa'),
            borderColor=colors.HexColor('#dee2e6'),
            borderWidth=1,
            borderPadding=8,
            borderRadius=5,
            alignment=TA_LEFT
        ))

        # AI消息样式
        styles.add(ParagraphStyle(
            name='AIMessage',
            parent=styles['Normal'],
            fontName=base_font_name,
            fontSize=11,
            leftIndent=60,
            rightIndent=20,
            spaceBefore=6,
            spaceAfter=6,
            backColor=colors.HexColor('#e8f4fd'),
            borderColor=colors.HexColor('#cce5ff'),
            borderWidth=1,
            borderPadding=8,
            borderRadius=5,
            alignment=TA_LEFT
        ))

        # 代码块样式（使用等宽字体）
        styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=styles['Code'],
            fontSize=9,
            fontName='Courier',  # 代码使用等宽字体
            leftIndent=30,
            rightIndent=30,
            spaceBefore=8,
            spaceAfter=8,
            backColor=colors.HexColor('#f5f5f5'),
            borderColor=colors.HexColor('#ddd'),
            borderWidth=1,
            borderPadding=10,
            textColor=colors.HexColor('#c7254e')
        ))

        # 元信息样式
        styles.add(ParagraphStyle(
            name='MetaInfo',
            parent=styles['Normal'],
            fontName=base_font_name,
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))

        # 页脚样式
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontName=base_font_name,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))

        # 也修改基础样式
        styles['Normal'].fontName = base_font_name
        styles['BodyText'].fontName = base_font_name
        styles['Italic'].fontName = base_font_name
        styles['Heading1'].fontName = base_font_name
        styles['Heading2'].fontName = base_font_name
        styles['Heading3'].fontName = base_font_name
        styles['Title'].fontName = base_font_name

        return styles

    def _create_cover_page(self, story, title, author, course, date):
        """创建封面页"""
        # 标题
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))

        # 作者信息
        if author:
            story.append(Paragraph(f"作者: {author}", self.styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))

        # 课程信息
        if course:
            story.append(Paragraph(f"课程: {course}", self.styles['Heading3']))
            story.append(Spacer(1, 0.2*inch))

        # 日期
        date_str = date.strftime("%Y年%m月%d日") if hasattr(date, 'strftime') else str(date)
        story.append(Paragraph(f"生成日期: {date_str}", self.styles['Heading3']))
        story.append(Spacer(1, 0.5*inch))

        # 分隔线
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("_" * 50, self.styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        # 说明文字
        story.append(Paragraph("AI对话记录导出文档", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("本文档由AI对话导出工具自动生成", self.styles['MetaInfo']))

        # 添加分页
        story.append(PageBreak())

    def _format_message_content(self, content: str) -> List:
        """格式化消息内容为PDF元素列表"""
        elements = []
        lines = content.split('\n')

        in_code_block = False
        code_block_lines = []

        for line in lines:
            # 检测代码块
            if line.strip().startswith('```'):
                if in_code_block:
                    # 结束代码块
                    if code_block_lines:
                        code_text = '<br/>'.join(code_block_lines)
                        elements.append(Paragraph(code_text, self.styles['CodeBlock']))
                        code_block_lines = []
                    in_code_block = False
                else:
                    # 开始代码块
                    in_code_block = True
                continue

            if in_code_block:
                # 在代码块中
                code_block_lines.append(line.replace(' ', '&nbsp;'))
            else:
                # 普通文本
                if line.strip():
                    # 处理Markdown-like格式
                    formatted_line = self._format_text_line(line)
                    elements.append(Paragraph(formatted_line, self.styles['Normal']))
                else:
                    # 空行
                    elements.append(Spacer(1, 6))

        # 处理最后一个代码块
        if in_code_block and code_block_lines:
            code_text = '<br/>'.join(code_block_lines)
            elements.append(Paragraph(code_text, self.styles['CodeBlock']))

        return elements

    def _format_text_line(self, line: str) -> str:
        """格式化文本行（处理简单Markdown）"""
        # 替换特殊字符
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # 简单Markdown处理
        # 粗体
        line = line.replace('**', '<b>').replace('**', '</b>')
        # 斜体
        line = line.replace('*', '<i>').replace('*', '</i>')
        line = line.replace('_', '<i>').replace('_', '</i>')
        # 代码片段
        line = line.replace('`', '<font name="Courier"><b>').replace('`', '</b></font>')

        return line

    def _add_message_to_story(self, story, message: Message):
        """添加消息到PDF故事流"""
        # 角色标签
        if message.role == MessageRole.USER:
            role_text = "👤 用户"
            style_name = 'UserMessage'
        elif message.role == MessageRole.ASSISTANT:
            role_text = "🤖 AI助手"
            style_name = 'AIMessage'
        elif message.role == MessageRole.SYSTEM:
            role_text = "⚙️ 系统"
            style_name = 'AIMessage'  # 使用AI样式
        else:
            role_text = "❓ 未知"
            style_name = 'UserMessage'

        # 时间戳
        timestamp = message.timestamp.strftime("%H:%M:%S") if hasattr(message.timestamp, 'strftime') else ""

        # 创建消息容器
        message_header = f"<b>{role_text}</b>"
        if timestamp:
            message_header += f" <font size=8 color=grey>({timestamp})</font>"

        story.append(Paragraph(message_header, self.styles['Heading3']))
        story.append(Spacer(1, 4))

        # 添加消息内容
        content_elements = self._format_message_content(message.content)
        for element in content_elements:
            if isinstance(element, Paragraph):
                # 应用消息样式
                element.style = self.styles[style_name]
            story.append(element)

        story.append(Spacer(1, 12))

    def _add_footer(self, canvas, doc):
        """添加页脚"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)

        # 页脚文本
        footer_text = f"第 {doc.page} 页 | AI对话导出工具生成 | {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        # 绘制页脚
        canvas.drawCentredString(doc.width / 2.0, 0.5 * inch, footer_text)

        canvas.restoreState()

    def create_conversation_pdf(
        self,
        messages: List[Message],
        title: str = "AI对话记录",
        author: str = "",
        course: str = "",
        date: datetime = None
    ) -> bytes:
        """
        生成对话PDF

        Args:
            messages: 消息列表
            title: 文档标题
            author: 作者
            course: 课程名称
            date: 日期

        Returns:
            PDF文件的字节数据
        """
        if date is None:
            date = datetime.now()

        # 创建字节流
        buffer = BytesIO()

        # 创建文档模板
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )

        # 构建PDF内容
        story = []

        # 封面页
        self._create_cover_page(story, title, author, course, date)

        # 对话内容标题
        story.append(Paragraph("对话记录", self.styles['CustomHeading1']))
        story.append(Spacer(1, 0.3*inch))

        # 添加消息统计
        user_count = sum(1 for msg in messages if msg.role == MessageRole.USER)
        ai_count = sum(1 for msg in messages if msg.role == MessageRole.ASSISTANT)
        total_chars = sum(len(msg.content) for msg in messages)

        stats_text = f"共 {len(messages)} 条消息（用户: {user_count}, AI: {ai_count}），总字数: {total_chars}"
        story.append(Paragraph(stats_text, self.styles['MetaInfo']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("_" * 30, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # 添加所有消息
        for i, message in enumerate(messages):
            # 添加消息序号
            story.append(Paragraph(f"消息 {i+1}", self.styles['Heading4']))
            self._add_message_to_story(story, message)

            # 每5条消息后添加分页（避免太长）
            if (i + 1) % 5 == 0 and i < len(messages) - 1:
                story.append(PageBreak())

        # 结束页
        story.append(PageBreak())
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("--- 结束 ---", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("感谢使用AI对话导出工具", self.styles['MetaInfo']))

        # 构建PDF
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

        # 获取字节数据
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def save_pdf_to_file(
        self,
        messages: List[Message],
        output_path: str,
        title: str = "AI对话记录",
        author: str = "",
        course: str = "",
        date: datetime = None
    ) -> str:
        """
        生成并保存PDF到文件

        Args:
            messages: 消息列表
            output_path: 输出文件路径
            title: 文档标题
            author: 作者
            course: 课程名称
            date: 日期

        Returns:
            保存的文件路径
        """
        pdf_bytes = self.create_conversation_pdf(messages, title, author, course, date)

        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 保存文件
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)

        return output_path


# 简化接口函数
def create_conversation_pdf(
    messages: List[Message],
    title: str = "AI对话记录",
    author: str = "",
    course: str = "",
    date: datetime = None
) -> bytes:
    """
    创建对话PDF的简化接口

    Args:
        messages: 消息列表
        title: 文档标题
        author: 作者
        course: 课程名称
        date: 日期

    Returns:
        PDF文件的字节数据
    """
    generator = PDFGenerator()
    return generator.create_conversation_pdf(messages, title, author, course, date)


def save_conversation_pdf(
    messages: List[Message],
    output_path: str,
    title: str = "AI对话记录",
    author: str = "",
    course: str = "",
    date: datetime = None
) -> str:
    """
    保存对话PDF到文件的简化接口

    Args:
        messages: 消息列表
        output_path: 输出文件路径
        title: 文档标题
        author: 作者
        course: 课程名称
        date: 日期

    Returns:
        保存的文件路径
    """
    generator = PDFGenerator()
    return generator.save_pdf_to_file(messages, output_path, title, author, course, date)


# 测试函数
if __name__ == "__main__":
    # 创建测试消息
    from datetime import datetime
    from .text_cleaner import Message, MessageRole

    test_messages = [
        Message(
            id=0,
            role=MessageRole.USER,
            content="请帮我写一个Python函数，计算斐波那契数列的前n项",
            timestamp=datetime.now(),
            metadata={}
        ),
        Message(
            id=1,
            role=MessageRole.ASSISTANT,
            content="当然，这是一个计算斐波那契数列的Python函数：\n\n```python\ndef fibonacci(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n\n    fib = [0, 1]\n    for i in range(2, n):\n        fib.append(fib[i-1] + fib[i-2])\n    return fib\n```\n\n这个函数的时间复杂度是O(n)，空间复杂度也是O(n)。",
            timestamp=datetime.now(),
            metadata={}
        ),
        Message(
            id=2,
            role=MessageRole.USER,
            content="谢谢！能否也提供一个递归版本的实现？",
            timestamp=datetime.now(),
            metadata={}
        ),
        Message(
            id=3,
            role=MessageRole.ASSISTANT,
            content="当然，这是递归版本的实现：\n\n```python\ndef fibonacci_recursive(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    \n    prev = fibonacci_recursive(n-1)\n    return prev + [prev[-1] + prev[-2]]\n```\n\n注意：递归版本的效率较低，时间复杂度为O(2^n)，不适合大的n值。",
            timestamp=datetime.now(),
            metadata={}
        )
    ]

    # 生成PDF
    print("正在生成测试PDF...")
    pdf_bytes = create_conversation_pdf(
        messages=test_messages,
        title="Python编程对话记录",
        author="测试用户",
        course="计算概论(C)",
        date=datetime.now()
    )

    # 保存测试文件
    test_output = "test_conversation.pdf"
    with open(test_output, 'wb') as f:
        f.write(pdf_bytes)

    print(f"PDF已生成: {test_output}")
    print(f"文件大小: {len(pdf_bytes)} 字节")