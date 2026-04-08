#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI对话记录导出工具 - 增强版主应用
现代化Streamlit界面，提供更好的用户体验
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
from pathlib import Path
import json

# 添加项目目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
try:
    from config import (
        APP_CONFIG, PDF_CONFIG, TEXT_CLEAN_CONFIG, EXPORT_CONFIG,
        get_export_path, validate_filename, generate_filename
    )
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    # 默认配置
    APP_CONFIG = {
        "name": "AI对话导出工具",
        "version": "1.0.0",
        "default_title": "AI对话记录",
    }
    PDF_CONFIG = {}
    TEXT_CLEAN_CONFIG = {}
    EXPORT_CONFIG = {}

# 导入工具模块
try:
    from utils.text_cleaner import (
        clean_ai_conversation,
        split_into_messages,
        format_for_preview,
        detect_conversation_format,
        MessageRole,
        Message
    )
    TEXT_CLEANER_AVAILABLE = True
except ImportError as e:
    st.error(f"无法导入文本清理模块: {e}")
    TEXT_CLEANER_AVAILABLE = False
    # 定义占位函数和类
    def clean_ai_conversation(text): return text
    def split_into_messages(text): return []
    def format_for_preview(messages): return ""
    def detect_conversation_format(text): return {"estimated_format": "unknown"}

    class MessageRole:
        USER = "user"
        ASSISTANT = "assistant"
        SYSTEM = "system"
        UNKNOWN = "unknown"

    class Message:
        def __init__(self, id, role, content, timestamp, metadata=None):
            self.id = id
            self.role = role
            self.content = content
            self.timestamp = timestamp
            self.metadata = metadata or {}

# 导入PDF生成模块
try:
    from utils.pdf_generator import create_conversation_pdf
    PDF_GENERATOR_AVAILABLE = True
except ImportError as e:
    st.error(f"无法导入PDF生成模块: {e}")
    PDF_GENERATOR_AVAILABLE = False
    def create_conversation_pdf(messages, title, author, course, date):
        return b"PDF生成模块不可用"

# 页面配置
st.set_page_config(
    page_title=APP_CONFIG.get("name", "AI对话导出工具"),
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/ai-chat-export',
        'Report a bug': 'https://github.com/yourusername/ai-chat-export/issues',
        'About': f"{APP_CONFIG.get('name')} v{APP_CONFIG.get('version')}"
    }
)

# 自定义CSS样式
def load_custom_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
    /* 主标题样式 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* 副标题样式 */
    .sub-title {
        font-size: 1.2rem;
        color: #7f8c8d;
        margin-bottom: 2rem;
        text-align: center;
    }

    /* 卡片样式 */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 5px solid #3498db;
    }

    .card-success {
        border-left-color: #2ecc71;
    }

    .card-warning {
        border-left-color: #f39c12;
    }

    .card-danger {
        border-left-color: #e74c3c;
    }

    /* 状态指示器 */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }

    .status-ready {
        background-color: #2ecc71;
    }

    .status-processing {
        background-color: #f39c12;
        animation: pulse 1.5s infinite;
    }

    .status-error {
        background-color: #e74c3c;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    /* 消息气泡样式 */
    .message-bubble {
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        word-wrap: break-word;
    }

    .message-user {
        background-color: #3498db;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }

    .message-ai {
        background-color: #ecf0f1;
        color: #2c3e50;
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }

    /* 进度条样式 */
    .stProgress > div > div > div > div {
        background-color: #3498db;
    }

    /* 按钮样式增强 */
    .stButton > button {
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* 表格样式 */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* 代码块样式 */
    pre {
        border-radius: 8px;
        padding: 1rem;
        background-color: #2c3e50 !important;
        color: #ecf0f1 !important;
    }

    code {
        background-color: #34495e;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    """初始化session state"""
    defaults = {
        'cleaned_text': "",
        'messages': [],
        'selected_indices': [],
        'pdf_generated': False,
        'pdf_bytes': None,
        'conversation_stats': {},
        'processing_step': 0,
        'example_loaded': "",
        'export_settings': {
            'title': APP_CONFIG.get("default_title", "AI对话记录"),
            'author': "",
            'course': "",
            'date': datetime.now(),
            'page_size': "A4",
            'include_cover': True,
            'include_stats': True,
            'filename': ""
        }
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def show_header():
    """显示应用头部"""
    st.markdown(f'<h1 class="main-title">🤖 {APP_CONFIG.get("name")}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">整理和导出AI对话记录，适合课程作业提交 | 版本 {APP_CONFIG.get("version")}</p>', unsafe_allow_html=True)

    # 功能亮点
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 智能清理", "自动优化格式")
    with col2:
        st.metric("✅ 消息选择", "自由选择导出")
    with col3:
        st.metric("📄 PDF导出", "专业格式文档")
    with col4:
        st.metric("⚡ 快速处理", "实时预览效果")

def show_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        st.markdown("### 🎯 快速导航")

        # 步骤指示器
        steps = ["输入对话", "清理格式", "选择消息", "导出设置", "生成PDF"]
        current_step = st.session_state.get('processing_step', 0)

        for i, step in enumerate(steps):
            status_icon = "✅" if i < current_step else "⭕" if i == current_step else "○"
            color = "#2ecc71" if i < current_step else "#3498db" if i == current_step else "#95a5a6"
            st.markdown(f'<span style="color:{color}; font-weight:bold;">{status_icon} {step}</span>', unsafe_allow_html=True)

        st.divider()

        # 工具信息
        st.markdown("### 📊 工具信息")
        st.markdown(f"""
        **版本:** {APP_CONFIG.get('version')}
        **作者:** {APP_CONFIG.get('author', 'AI对话导出工具团队')}
        **用途:** {APP_CONFIG.get('description', '课程作业对话导出')}
        **支持格式:** {', '.join(APP_CONFIG.get('supported_formats', ['ChatGPT', 'Claude']))}
        **输出格式:** PDF文档
        """)

        st.divider()

        # 设置
        st.markdown("### ⚙️ 设置")

        with st.expander("PDF设置", expanded=False):
            page_size = st.selectbox(
                "页面尺寸",
                APP_CONFIG.get("page_sizes", ["A4", "Letter"]),
                index=0,
                help="选择PDF页面尺寸"
            )
            st.session_state.export_settings['page_size'] = page_size

            col1, col2 = st.columns(2)
            with col1:
                include_cover = st.checkbox("包含封面", value=True)
                st.session_state.export_settings['include_cover'] = include_cover
            with col2:
                include_stats = st.checkbox("包含统计", value=True)
                st.session_state.export_settings['include_stats'] = include_stats

        with st.expander("文本处理设置", expanded=False):
            preserve_code = st.checkbox("保留代码缩进", value=True)
            merge_empty = st.checkbox("合并连续空行", value=True)

        st.divider()

        # 帮助
        st.markdown("### ❓ 使用帮助")
        with st.expander("点击查看详细说明", expanded=False):
            st.markdown("""
            ### 🚀 使用步骤
            1. **粘贴对话**: 从AI工具复制完整对话
            2. **清理格式**: 点击按钮自动优化格式
            3. **选择消息**: 勾选要导出的部分
            4. **设置信息**: 填写标题、作者等信息
            5. **生成PDF**: 点击按钮生成并下载

            ### ✨ 支持的功能
            - 智能格式清理
            - 消息选择性导出
            - 代码块高亮显示
            - 多角色识别
            - 自动生成封面
            - 对话统计信息

            ### ⚠️ 注意事项
            - 确保对话包含角色标记（如"用户："、"AI："）
            - 代码块使用三个反引号包裹
            - 长对话可能需要较长时间处理
            - 建议一次处理不超过100条消息
            """)

def show_conversation_input():
    """显示对话输入区域"""
    st.markdown("### 📝 第一步：输入对话内容")

    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            # 文本输入区域
            raw_text = st.text_area(
                "从AI对话页面复制粘贴完整对话：",
                height=250,
                value=st.session_state.example_loaded,
                placeholder="例如：\n用户：请帮我写一个Python函数...\nAI：当然，这是一个示例函数...\n用户：谢谢！\nAI：不客气！",
                help="支持从ChatGPT、Claude等AI工具粘贴对话",
                key="conversation_input_main"
            )

            # 操作按钮
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("🗑️ 清空输入", use_container_width=True):
                    st.session_state.example_loaded = ""
                    st.session_state.cleaned_text = ""
                    st.session_state.messages = []
                    st.session_state.selected_indices = []
                    st.session_state.processing_step = 0
                    st.rerun()

            with col_btn2:
                if st.button("📋 加载示例", use_container_width=True):
                    example_text = """用户：请帮我写一个Python函数，计算斐波那契数列

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

用户：能否解释一下为什么是O(n)？

AI：当然。这个函数使用了一个for循环，循环执行n-2次（当n>2时），每次循环执行常数时间的操作（加法和列表追加）。因此总操作次数与n成正比，所以时间复杂度是O(n)。"""
                    st.session_state.example_loaded = example_text
                    st.rerun()

            with col_btn3:
                if st.button("🔄 自动清理", type="primary", use_container_width=True):
                    if raw_text.strip():
                        st.session_state.processing_step = 1
                        process_conversation(raw_text)
                    else:
                        st.warning("请先输入对话内容")

        with col2:
            st.markdown("### 💡 提示")
            st.markdown("""
            - **确保完整**: 复制完整的对话内容
            - **保留标记**: 保留用户和AI的角色标记
            - **代码块**: 使用三个反引号包裹代码
            - **格式**: 支持Markdown格式
            - **长度**: 建议不超过5000字符
            """)

            # 文件上传
            uploaded_file = st.file_uploader(
                "或上传文本文件",
                type=['txt', 'md', 'log'],
                help="支持.txt, .md, .log格式"
            )

            if uploaded_file is not None:
                try:
                    text_content = uploaded_file.getvalue().decode("utf-8")
                    st.session_state.example_loaded = text_content
                    st.success(f"已加载文件: {uploaded_file.name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"读取文件失败: {e}")

def process_conversation(raw_text):
    """处理对话文本"""
    with st.spinner("正在处理对话..."):
        try:
            # 更新进度
            progress_bar = st.progress(0)

            # 步骤1: 检测格式
            progress_bar.progress(20)
            if TEXT_CLEANER_AVAILABLE:
                format_info = detect_conversation_format(raw_text)
                st.info(f"📊 检测到格式: **{format_info['estimated_format']}**")

            # 步骤2: 清理文本
            progress_bar.progress(40)
            if TEXT_CLEANER_AVAILABLE:
                cleaned_text = clean_ai_conversation(raw_text)
                st.session_state.cleaned_text = cleaned_text
            else:
                st.session_state.cleaned_text = raw_text
                st.warning("文本清理模块不可用，使用原始文本")

            # 步骤3: 分割消息
            progress_bar.progress(60)
            if TEXT_CLEANER_AVAILABLE:
                messages = split_into_messages(st.session_state.cleaned_text)
                st.session_state.messages = messages
                st.session_state.selected_indices = list(range(len(messages)))
            else:
                st.session_state.messages = []

            # 步骤4: 计算统计信息
            progress_bar.progress(80)
            if st.session_state.messages:
                user_count = sum(1 for msg in st.session_state.messages if msg.role == MessageRole.USER)
                ai_count = sum(1 for msg in st.session_state.messages if msg.role == MessageRole.ASSISTANT)
                total_chars = sum(len(msg.content) for msg in st.session_state.messages)

                st.session_state.conversation_stats = {
                    "total_messages": len(st.session_state.messages),
                    "user_messages": user_count,
                    "ai_messages": ai_count,
                    "total_chars": total_chars,
                    "avg_chars_per_msg": total_chars // len(st.session_state.messages) if st.session_state.messages else 0
                }

            progress_bar.progress(100)
            st.session_state.processing_step = 2
            st.success(f"✅ 处理完成！识别到 {len(st.session_state.messages)} 条消息")

        except Exception as e:
            st.error(f"处理对话时出错: {str(e)}")
            st.exception(e)

def show_conversation_stats():
    """显示对话统计信息"""
    if not st.session_state.conversation_stats:
        return

    stats = st.session_state.conversation_stats
    st.markdown("### 📊 对话统计")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总消息数", stats["total_messages"])
    with col2:
        st.metric("用户消息", stats["user_messages"])
    with col3:
        st.metric("AI消息", stats["ai_messages"])
    with col4:
        st.metric("总字数", f"{stats['total_chars']:,}")

def show_message_selection():
    """显示消息选择界面"""
    if not st.session_state.messages:
        return

    st.markdown("### ✅ 第二步：选择要导出的消息")

    # 控制按钮
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("全选", use_container_width=True):
            st.session_state.selected_indices = list(range(len(st.session_state.messages)))
            st.rerun()
    with col2:
        if st.button("全不选", use_container_width=True):
            st.session_state.selected_indices = []
            st.rerun()
    with col3:
        if st.button("仅选用户", use_container_width=True):
            st.session_state.selected_indices = [
                i for i, msg in enumerate(st.session_state.messages)
                if msg.role == MessageRole.USER
            ]
            st.rerun()
    with col4:
        if st.button("仅选AI", use_container_width=True):
            st.session_state.selected_indices = [
                i for i, msg in enumerate(st.session_state.messages)
                if msg.role == MessageRole.ASSISTANT
            ]
            st.rerun()

    # 消息列表
    st.markdown("---")

    # 使用容器显示消息
    selected_messages = []

    for i, msg in enumerate(st.session_state.messages):
        # 确定角色样式
        if msg.role == MessageRole.USER:
            role_icon = "👤"
            role_text = "用户"
            bubble_class = "message-user"
            bg_color = "#3498db"
        elif msg.role == MessageRole.ASSISTANT:
            role_icon = "🤖"
            role_text = "AI助手"
            bubble_class = "message-ai"
            bg_color = "#ecf0f1"
        else:
            role_icon = "❓"
            role_text = "未知"
            bubble_class = "message-ai"
            bg_color = "#95a5a6"

        # 创建消息卡片
        with st.container():
            col_check, col_content = st.columns([1, 10])

            with col_check:
                selected = st.checkbox(
                    f"消息 {i+1}",
                    value=i in st.session_state.selected_indices,
                    key=f"msg_select_{i}"
                )
                if selected and i not in st.session_state.selected_indices:
                    st.session_state.selected_indices.append(i)
                    st.rerun()
                elif not selected and i in st.session_state.selected_indices:
                    st.session_state.selected_indices.remove(i)
                    st.rerun()

            with col_content:
                # 显示消息摘要
                content_preview = msg.content
                if len(content_preview) > 100:
                    content_preview = content_preview[:100] + "..."

                # 使用HTML显示消息气泡
                st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 12px 16px; border-radius: 18px; margin: 8px 0; max-width: 80%;">
                    <strong>{role_icon} {role_text}</strong>
                    <p style="margin: 5px 0; color: {'white' if msg.role == MessageRole.USER else '#2c3e50'};">{content_preview}</p>
                    <small style="color: {'#bdc3c7' if msg.role == MessageRole.USER else '#7f8c8d'};">ID: {msg.id} | 长度: {len(msg.content)} 字符</small>
                </div>
                """, unsafe_allow_html=True)

        if i in st.session_state.selected_indices:
            selected_messages.append(msg)

    st.markdown(f"**已选择 {len(selected_messages)}/{len(st.session_state.messages)} 条消息**")

    # 显示选中的消息预览
    if selected_messages:
        st.markdown("### 👁️ 预览选中的消息")
        preview_text = format_for_preview(selected_messages)
        with st.expander("点击查看完整预览", expanded=False):
            st.text_area("预览内容", preview_text, height=300, label_visibility="collapsed")

    # 更新处理步骤
    if selected_messages:
        st.session_state.processing_step = 3

def show_export_settings():
    """显示导出设置"""
    st.markdown("### ⚙️ 第三步：导出设置")

    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input(
            "文档标题",
            value=st.session_state.export_settings['title'],
            help="PDF文档的标题"
        )
        st.session_state.export_settings['title'] = title

        author = st.text_input(
            "作者姓名",
            value=st.session_state.export_settings['author'],
            placeholder="请输入您的姓名",
            help="文档作者姓名"
        )
        st.session_state.export_settings['author'] = author

    with col2:
        course = st.text_input(
            "课程名称",
            value=st.session_state.export_settings['course'],
            placeholder="例如：计算概论(C)",
            help="相关课程名称"
        )
        st.session_state.export_settings['course'] = course

        date = st.date_input(
            "文档日期",
            value=st.session_state.export_settings['date'],
            help="文档生成日期"
        )
        st.session_state.export_settings['date'] = date

    # 文件名设置
    st.markdown("### 📄 文件设置")
    col_name1, col_name2 = st.columns([3, 1])

    with col_name1:
        default_filename = generate_filename(
            st.session_state.export_settings['title'],
            st.session_state.export_settings['date']
        )
        filename = st.text_input(
            "文件名",
            value=default_filename,
            help="PDF文件名"
        )
        st.session_state.export_settings['filename'] = filename

    with col_name2:
        st.markdown("###")
        if st.button("生成默认名", use_container_width=True):
            default_name = generate_filename(
                st.session_state.export_settings['title'],
                st.session_state.export_settings['date']
            )
            st.session_state.export_settings['filename'] = default_name
            st.rerun()

    # 更新处理步骤
    st.session_state.processing_step = 4

def show_pdf_generation():
    """显示PDF生成界面"""
    st.markdown("### 🚀 第四步：生成PDF")

    # 检查是否有选中的消息
    selected_messages = []
    if st.session_state.messages and st.session_state.selected_indices:
        selected_messages = [st.session_state.messages[i] for i in st.session_state.selected_indices]

    if not selected_messages:
        st.warning("⚠️ 请先选择要导出的消息")
        return

    # 显示生成选项
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 生成选项")
        st.markdown(f"""
        - **文档标题**: {st.session_state.export_settings['title']}
        - **作者**: {st.session_state.export_settings['author'] or '未设置'}
        - **课程**: {st.session_state.export_settings['course'] or '未设置'}
        - **日期**: {st.session_state.export_settings['date']}
        - **消息数量**: {len(selected_messages)} 条
        - **页面尺寸**: {st.session_state.export_settings['page_size']}
        """)

    with col2:
        st.markdown("#### 📊 内容预览")
        user_count = sum(1 for msg in selected_messages if msg.role == MessageRole.USER)
        ai_count = sum(1 for msg in selected_messages if msg.role == MessageRole.ASSISTANT)
        total_chars = sum(len(msg.content) for msg in selected_messages)

        st.markdown(f"""
        - **用户消息**: {user_count} 条
        - **AI消息**: {ai_count} 条
        - **总字数**: {total_chars:,} 字符
        - **平均长度**: {total_chars // len(selected_messages) if selected_messages else 0} 字符/条
        """)

    # 生成按钮
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

    with col_btn2:
        if st.button("🎯 生成PDF文档", type="primary", use_container_width=True):
            generate_pdf(selected_messages)

def generate_pdf(selected_messages):
    """生成PDF文件"""
    with st.spinner("正在生成PDF，请稍候..."):
        try:
            # 生成PDF
            pdf_bytes = create_conversation_pdf(
                messages=selected_messages,
                title=st.session_state.export_settings['title'],
                author=st.session_state.export_settings['author'],
                course=st.session_state.export_settings['course'],
                date=st.session_state.export_settings['date']
            )

            # 保存到session state
            st.session_state.pdf_bytes = pdf_bytes
            st.session_state.pdf_generated = True

            # 提供下载按钮
            st.success("✅ PDF生成完成！")

            # 获取文件名
            filename = st.session_state.export_settings['filename']
            if not filename.endswith('.pdf'):
                filename += '.pdf'

            # 下载按钮
            st.download_button(
                label="📥 下载PDF文件",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

            # 显示文件信息
            file_size_kb = len(pdf_bytes) // 1024
            st.info(f"""
            **文件信息:**
            - 文件名: {filename}
            - 文件大小: {file_size_kb} KB
            - 包含消息: {len(selected_messages)} 条
            - 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """)

            # 保存到本地文件
            try:
                export_path = get_export_path(filename)
                with open(export_path, 'wb') as f:
                    f.write(pdf_bytes)
                st.success(f"文件已保存到: {export_path}")
            except Exception as e:
                st.warning(f"保存到本地文件失败: {e}")

        except Exception as e:
            st.error(f"生成PDF时出错: {str(e)}")
            st.exception(e)

def show_footer():
    """显示页脚"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p style='font-size: 1.1rem; font-weight: bold;'>🤖 AI对话导出工具</p>
        <p>专为课程作业设计 | 版本 {version} | 遇到问题请联系开发者</p>
        <p style='font-size: 0.9rem; margin-top: 1rem;'>
            <a href='https://github.com/yourusername/ai-chat-export' style='color: #3498db; text-decoration: none; margin: 0 1rem;'>GitHub</a> •
            <a href='https://github.com/yourusername/ai-chat-export/issues' style='color: #3498db; text-decoration: none; margin: 0 1rem;'>报告问题</a> •
            <a href='mailto:your-email@example.com' style='color: #3498db; text-decoration: none; margin: 0 1rem;'>联系我们</a>
        </p>
    </div>
    """.format(version=APP_CONFIG.get("version", "1.0.0")), unsafe_allow_html=True)

def main():
    """主函数"""
    # 加载CSS样式
    load_custom_css()

    # 初始化session state
    init_session_state()

    # 显示应用头部
    show_header()

    # 显示侧边栏
    show_sidebar()

    # 显示对话输入区域
    show_conversation_input()

    # 显示清理后的文本（如果有）
    if st.session_state.cleaned_text:
        with st.expander("📋 清理后的对话预览", expanded=False):
            st.text_area("预览", st.session_state.cleaned_text, height=150, label_visibility="collapsed")

    # 显示对话统计
    if st.session_state.conversation_stats:
        show_conversation_stats()

    # 显示消息选择
    if st.session_state.messages:
        show_message_selection()

    # 显示导出设置
    if st.session_state.selected_indices:
        show_export_settings()

    # 显示PDF生成
    if (st.session_state.selected_indices and
        st.session_state.export_settings['title'] and
        st.session_state.processing_step >= 3):
        show_pdf_generation()

    # 显示页脚
    show_footer()

if __name__ == "__main__":
    main()