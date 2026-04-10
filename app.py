#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI对话记录导出工具
简单版 - 用于整理和导出AI对话记录
"""

import streamlit as st
from datetime import datetime
import sys
import os

# 添加utils目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入工具模块
try:
    from utils.text_cleaner import (
        clean_ai_conversation,
        split_into_messages,
        format_message_for_display,
        MessageRole,
        Message
    )
    TEXT_CLEANER_AVAILABLE = True
except ImportError as e:
    st.error(f"无法导入文本清理模块: {e}")
    TEXT_CLEANER_AVAILABLE = False
    # 简单占位函数
    def clean_ai_conversation(text): return text
    def split_into_messages(text): return []
    def format_message_for_display(message): return [{'type': 'text', 'content': message.content}]

    class MessageRole:
        USER = "user"
        ASSISTANT = "assistant"
        SYSTEM = "system"
        UNKNOWN = "unknown"

    class Message:
        def __init__(self, id, role, content, timestamp=None, metadata=None):
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
        return b"PDF module not available"

# 页面配置
st.set_page_config(
    page_title="AI对话导出工具",
    page_icon="🤖",
    layout="wide"
)

def main():
    """主应用函数"""

    st.title("🤖 AI对话记录导出工具")
    st.markdown("整理和导出与AI的对话记录，适合课程作业提交")

    # 初始化session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'selected_indices' not in st.session_state:
        st.session_state.selected_indices = []

    # 1. 输入对话
    st.header("📝 第一步：输入对话")

    raw_text = st.text_area(
        "从AI对话页面复制粘贴完整对话：",
        height=200,
        placeholder="例如：\n用户：请帮我写一个Python函数...\nAI：当然，这是一个示例函数...\n用户：谢谢！\nAI：不客气！",
        help="支持从ChatGPT、Claude等AI工具粘贴对话"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 加载示例对话"):
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
            st.session_state.example_text = example_text
            st.rerun()

    with col2:
        if st.button("🔄 清理格式", type="primary"):
            if raw_text.strip():
                if TEXT_CLEANER_AVAILABLE:
                    with st.spinner("正在清理格式..."):
                        # 清理文本
                        cleaned_text = clean_ai_conversation(raw_text)

                        # 分割消息
                        messages = split_into_messages(cleaned_text)
                        st.session_state.messages = messages
                        st.session_state.selected_indices = list(range(len(messages)))

                        st.success(f"识别到 {len(messages)} 条消息")
                else:
                    st.warning("文本清理模块不可用")
            else:
                st.warning("请先输入对话内容")

    # 2. 选择消息
    if st.session_state.messages:
        st.header("✅ 第二步：选择要导出的消息")

        # 控制按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("全选"):
                st.session_state.selected_indices = list(range(len(st.session_state.messages)))
                st.rerun()
        with col2:
            if st.button("全不选"):
                st.session_state.selected_indices = []
                st.rerun()

        # 消息列表
        selected_messages = []
        for i, msg in enumerate(st.session_state.messages):
            col1, col2 = st.columns([1, 4])

            with col1:
                selected = st.checkbox(
                    f"消息 {i+1}",
                    value=i in st.session_state.selected_indices,
                    key=f"msg_{i}"
                )
                if selected and i not in st.session_state.selected_indices:
                    st.session_state.selected_indices.append(i)
                    st.rerun()
                elif not selected and i in st.session_state.selected_indices:
                    st.session_state.selected_indices.remove(i)
                    st.rerun()

            with col2:
                # 显示消息摘要
                role_icon = "👤" if msg.role == MessageRole.USER else "🤖"
                role_text = "用户" if msg.role == MessageRole.USER else "AI助手"

                st.markdown(f"**{role_icon} {role_text}**")

                # 使用Markdown渲染预览
                if TEXT_CLEANER_AVAILABLE:
                    elements = format_message_for_display(msg)
                    # 只显示前两个元素作为预览
                    preview_shown = 0
                    for elem in elements:
                        if preview_shown >= 2:  # 最多显示两个元素
                            st.markdown("...")
                            break

                        elem_type = elem.get('type', 'text')

                        if elem_type == 'heading':
                            content = elem.get('content', '')
                            st.markdown(f"**{content}**")
                            preview_shown += 1
                        elif elem_type == 'paragraph':
                            content = elem.get('content', '')
                            # 截断长文本
                            if len(content) > 100:
                                content = content[:100] + "..."
                            st.markdown(content, unsafe_allow_html=True)
                            preview_shown += 1
                        elif elem_type == 'code':
                            st.markdown("`[代码块]`")
                            preview_shown += 1
                        elif elem_type in ['unordered_list', 'ordered_list']:
                            st.markdown("`[列表]`")
                            preview_shown += 1
                        elif elem_type == 'text':
                            content = elem.get('content', '')
                            if len(content) > 100:
                                content = content[:100] + "..."
                            st.markdown(content)
                            preview_shown += 1
                else:
                    # 回退到简单预览
                    content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                    st.markdown(content_preview)

            if selected:
                selected_messages.append(msg)

        st.markdown(f"**已选择 {len(selected_messages)}/{len(st.session_state.messages)} 条消息**")

    # 3. 导出设置
    st.header("⚙️ 第三步：导出设置")

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("文档标题", value="AI对话记录")
        author = st.text_input("作者姓名（可选）", placeholder="请输入您的姓名")
    with col2:
        course = st.text_input("课程名称（可选）", placeholder="例如：计算概论(C)")
        date = st.date_input("文档日期", value=datetime.now())

    # 4. 生成PDF
    st.header("📄 第四步：生成PDF")

    # 检查是否有选中的消息
    selected_messages = []
    if st.session_state.messages and st.session_state.selected_indices:
        selected_messages = [st.session_state.messages[i] for i in st.session_state.selected_indices]

    if selected_messages:
        if st.button("🚀 生成PDF文档", type="primary"):
            with st.spinner("正在生成PDF，请稍候..."):
                try:
                    # 生成PDF
                    pdf_bytes = create_conversation_pdf(
                        messages=selected_messages,
                        title=title,
                        author=author,
                        course=course,
                        date=date
                    )

                    # 提供下载按钮
                    st.success("✅ PDF生成完成！")

                    # 生成文件名
                    filename = f"{title}_{date.strftime('%Y%m%d')}.pdf".replace(" ", "_")

                    st.download_button(
                        label="📥 下载PDF文件",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        type="primary"
                    )

                    # 显示文件信息
                    st.info(f"文件大小: {len(pdf_bytes) // 1024} KB | 包含 {len(selected_messages)} 条消息")

                except Exception as e:
                    st.error(f"生成PDF时出错: {str(e)}")
    else:
        st.warning("请先选择要导出的消息")

if __name__ == "__main__":
    main()