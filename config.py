#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单配置文件
"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
EXPORTS_DIR = DATA_DIR / "exports"

# 确保目录存在
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)