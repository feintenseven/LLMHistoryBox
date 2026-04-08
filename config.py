#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
管理应用设置和常量
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
EXPORTS_DIR = DATA_DIR / "exports"

# 确保目录存在
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# 应用配置
APP_CONFIG = {
    "name": "AI对话导出工具",
    "version": "1.0.0",
    "description": "整理和导出AI对话记录的工具",
    "author": "AI对话导出工具团队",
    "default_title": "AI对话记录",
    "default_author": "",
    "default_course": "",
    "page_sizes": ["A4", "Letter"],
    "default_page_size": "A4",
    "supported_formats": ["ChatGPT", "Claude", "通用AI对话"],
    "max_file_size_mb": 10,
    "max_messages": 1000,
}

# PDF配置
PDF_CONFIG = {
    "default_margin": 1.0,  # 英寸
    "font_sizes": {
        "title": 24,
        "heading1": 18,
        "heading2": 16,
        "heading3": 14,
        "normal": 11,
        "small": 9,
        "code": 9,
    },
    "colors": {
        "title": "#2c3e50",
        "heading": "#34495e",
        "user_message": "#f8f9fa",
        "ai_message": "#e8f4fd",
        "code_block": "#f5f5f5",
        "border": "#dee2e6",
        "footer": "#666666",
    },
    "page_break_after": 5,  # 每5条消息后分页
}

# 文本清理配置
TEXT_CLEAN_CONFIG = {
    "role_patterns": {
        "user": [
            r'^用户[:：]\s*',
            r'^User[:：]\s*',
            r'^Human[:：]\s*',
            r'^提问[:：]\s*',
            r'^Q[:：]\s*',
            r'^我[:：]\s*',
            r'^提问者[:：]\s*',
        ],
        "assistant": [
            r'^AI[:：]\s*',
            r'^Assistant[:：]\s*',
            r'^模型[:：]\s*',
            r'^回答[:：]\s*',
            r'^A[:：]\s*',
            r'^助手[:：]\s*',
            r'^Claude[:：]\s*',
            r'^ChatGPT[:：]\s*',
            r'^GPT[:：]\s*',
        ],
        "system": [
            r'^系统[:：]\s*',
            r'^System[:：]\s*',
        ]
    },
    "max_preview_length": 150,  # 预览文本最大长度
    "preserve_code_indent": True,
    "merge_consecutive_empty_lines": True,
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": DATA_DIR / "app.log",
    "max_size_mb": 10,
    "backup_count": 5,
}

# 导出配置
EXPORT_CONFIG = {
    "default_filename_template": "{title}_{date}.pdf",
    "date_format": "%Y%m%d",
    "allowed_extensions": [".pdf"],
    "auto_open_after_export": False,
}

def get_export_path(filename: str) -> Path:
    """获取导出文件路径"""
    return EXPORTS_DIR / filename

def validate_filename(filename: str) -> bool:
    """验证文件名是否有效"""
    if not filename:
        return False
    # 检查扩展名
    ext = os.path.splitext(filename)[1].lower()
    return ext in EXPORT_CONFIG["allowed_extensions"]

def generate_filename(title: str, date=None) -> str:
    """生成默认文件名"""
    from datetime import datetime

    if date is None:
        date = datetime.now()

    date_str = date.strftime(EXPORT_CONFIG["date_format"])
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-")
    safe_title = safe_title.replace(" ", "_")[:50]  # 限制长度

    filename = EXPORT_CONFIG["default_filename_template"].format(
        title=safe_title,
        date=date_str
    )

    return filename