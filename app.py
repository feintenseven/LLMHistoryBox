#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI对话记录导出工具 - 主应用
Streamlit应用，用于整理和导出AI对话记录
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
        return "PDF生成模块不可用"

# 页面配置
st.set_page_config(
    page_title="AI对话导出工具",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """主应用函数"""

    # 应用标题和说明
    st.title("🤖 AI对话记录导出工具")

    # 侧边栏
    with st.sidebar:
        st.header("📊 工具信息")
        st.markdown("""
        **版本:** 1.0.0
        **用途:** 课程作业对话导出
        **支持格式:** ChatGPT, Claude等
        **输出格式:** PDF文档
        """)

        st.divider()

        st.header("⚙️ 设置")
        page_size = st.selectbox(
            "页面尺寸",
            ["A4", "Letter"],
            help="选择PDF页面尺寸"
        )

        st.divider()

        st.header("❓ 使用帮助")
        with st.expander("点击查看详细说明"):
            st.markdown("""
            ### 使用步骤
            1. **粘贴对话**: 从AI工具复制完整对话
            2. **清理格式**: 点击按钮自动优化格式
            3. **选择消息**: 勾选要导出的部分
            4. **设置信息**: 填写标题、作者等信息
            5. **生成PDF**: 点击按钮生成并下载

            ### 支持的功能
            - 智能格式清理
            - 消息选择性导出
            - 代码块高亮显示
            - 多角色识别
            - 自动生成封面

            ### 注意事项
            - 确保对话包含角色标记（如"用户："、"AI："）
            - 代码块使用三个反引号包裹
            - 长对话可能需要较长时间处理
            """)

    # 主内容区
    st.markdown("""
    ### 整理和导出与AI的对话记录，适合课程作业提交

    **使用步骤：**
    1. 从AI对话页面复制完整对话
    2. 粘贴到下面的文本区域
    3. 点击"自动清理格式"按钮
    4. 选择要导出的消息
    5. 设置文档信息
    6. 生成并下载PDF

    ---
    """)

    # 初始化session state
    if 'cleaned_text' not in st.session_state:
        st.session_state.cleaned_text = ""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'selected_indices' not in st.session_state:
        st.session_state.selected_indices = []
    if 'pdf_generated' not in st.session_state:
        st.session_state.pdf_generated = False
    if 'pdf_bytes' not in st.session_state:
        st.session_state.pdf_bytes = None

    # 状态指示器
    st.markdown("### 📋 当前状态")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        has_input = bool(st.session_state.get('example_loaded') or st.session_state.get('cleaned_text'))
        status_icon = "✅" if has_input else "⭕"
        st.metric("输入状态", status_icon)

    with col2:
        msg_count = len(st.session_state.messages)
        st.metric("识别消息", f"{msg_count} 条")

    with col3:
        selected_count = len(st.session_state.selected_indices)
        st.metric("选中消息", f"{selected_count} 条")

    with col4:
        pdf_status = "✅" if st.session_state.pdf_generated else "⭕"
        st.metric("PDF状态", pdf_status)

    st.divider()

    # 对话输入区
    with st.expander("📝 第一步：粘贴对话", expanded=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            # 初始化session state
            if 'example_loaded' not in st.session_state:
                st.session_state.example_loaded = ""

            raw_text = st.text_area(
                "从AI对话页面复制粘贴完整对话：",
                height=200,
                value=st.session_state.example_loaded,
                placeholder="例如：\n用户：请帮我写一个Python函数...\nAI：当然，这是一个示例函数...\n用户：谢谢！\nAI：不客气！",
                help="支持从ChatGPT、Claude等AI工具粘贴对话",
                key="conversation_input"
            )

            # 清空按钮
            if raw_text and st.button("🗑️ 清空输入", use_container_width=True):
                st.session_state.example_loaded = ""
                st.session_state.cleaned_text = ""
                st.session_state.messages = []
                st.session_state.selected_indices = []
                st.rerun()

        with col2:
            st.markdown("### 提示")
            st.markdown("""
            - 确保包含完整的对话
            - 保留用户和AI的标记
            - 代码块会特殊处理
            - 点击清理按钮优化格式
            """)

            # 示例对话按钮
            if st.button("📋 加载示例对话", use_container_width=True):
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

            if st.button("🔄 自动清理格式", type="primary", use_container_width=True):
                if raw_text.strip():
                    if TEXT_CLEANER_AVAILABLE:
                        with st.spinner("正在清理格式..."):
                            # 检测格式
                            format_info = detect_conversation_format(raw_text)
                            st.info(f"检测到格式: {format_info['estimated_format']}")

                            # 清理文本
                            cleaned_text = clean_ai_conversation(raw_text)
                            st.session_state.cleaned_text = cleaned_text

                            # 分割消息
                            messages = split_into_messages(cleaned_text)
                            st.session_state.messages = messages
                            st.session_state.selected_indices = list(range(len(messages)))

                            st.success(f"格式清理完成！识别到 {len(messages)} 条消息")
                    else:
                        st.session_state.cleaned_text = raw_text
                        st.warning("文本清理模块不可用，使用原始文本")
                    st.rerun()
                else:
                    st.warning("请先输入对话内容")

    # 显示清理后的文本（如果有）
    if st.session_state.cleaned_text:
        st.subheader("📋 清理后的对话")
        st.text_area("预览清理结果", st.session_state.cleaned_text, height=150)

    # 消息选择区
    if st.session_state.messages:
        st.subheader("✅ 第二步：选择要导出的消息")

        # 全选/全不选控制
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("全选", use_container_width=True):
                st.session_state.selected_indices = list(range(len(st.session_state.messages)))
                st.rerun()
        with col2:
            if st.button("全不选", use_container_width=True):
                st.session_state.selected_indices = []
                st.rerun()

        # 消息列表
        st.markdown("---")
        selected_messages = []

        for i, msg in enumerate(st.session_state.messages):
            # 确定角色图标和颜色
            if msg.role == MessageRole.USER:
                role_icon = "👤"
                role_color = "blue"
                role_text = "用户"
            elif msg.role == MessageRole.ASSISTANT:
                role_icon = "🤖"
                role_color = "green"
                role_text = "AI助手"
            elif msg.role == MessageRole.SYSTEM:
                role_icon = "⚙️"
                role_color = "gray"
                role_text = "系统"
            else:
                role_icon = "❓"
                role_color = "orange"
                role_text = "未知"

            # 创建消息卡片
            with st.container():
                col1, col2 = st.columns([1, 10])

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
                    content_preview = msg.content
                    if len(content_preview) > 150:
                        content_preview = content_preview[:150] + "..."

                    st.markdown(f"""
                    <div style="padding: 10px; border-left: 4px solid {role_color}; background-color: #f8f9fa; border-radius: 4px;">
                        <strong>{role_icon} {role_text}</strong>
                        <p style="margin: 5px 0; color: #333;">{content_preview}</p>
                        <small style="color: #666;">ID: {msg.id} | 长度: {len(msg.content)} 字符</small>
                    </div>
                    """, unsafe_allow_html=True)

            if selected:
                selected_messages.append(msg)

        st.markdown(f"**已选择 {len(selected_messages)}/{len(st.session_state.messages)} 条消息**")

        # 预览选中的消息
        if selected_messages:
            st.subheader("👁️ 预览选中的消息")
            preview_text = format_for_preview(selected_messages)
            st.text_area("预览内容", preview_text, height=200)

    # 导出设置区
    st.subheader("⚙️ 第三步：导出设置")

    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("文档标题", value="AI对话记录")
        author = st.text_input("作者姓名（可选）", placeholder="请输入您的姓名")

    with col2:
        course = st.text_input("课程名称（可选）", placeholder="例如：计算概论(C)")
        date = st.date_input("文档日期", value=datetime.now())

    # 生成PDF按钮
    st.subheader("📄 第四步：生成PDF")

    # 检查是否有选中的消息
    selected_messages = []
    if st.session_state.messages and st.session_state.selected_indices:
        selected_messages = [st.session_state.messages[i] for i in st.session_state.selected_indices]

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if selected_messages:
            if st.button("🚀 生成PDF文档", type="primary", use_container_width=True):
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
                            type="primary",
                            use_container_width=True
                        )

                        # 显示文件信息
                        st.info(f"文件大小: {len(pdf_bytes) // 1024} KB | 包含 {len(selected_messages)} 条消息")

                    except Exception as e:
                        st.error(f"生成PDF时出错: {str(e)}")
                        st.exception(e)
        else:
            st.warning("请先选择要导出的消息")
            if st.button("🚀 生成PDF文档", type="primary", disabled=True, use_container_width=True):
                pass

    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>AI对话导出工具 | 专为课程作业设计 | 版本 1.0.0</p>
        <p>遇到问题？请检查对话格式或联系开发者</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()