# 🤖 AI对话记录导出工具

一个简单的工具，用于整理和导出与AI的对话记录，适合课程作业提交。

## ✨ 功能特点

- **格式清理**：自动处理从AI页面粘贴的对话格式
- **消息选择**：选择要导出的对话部分
- **PDF导出**：生成简单的PDF文档
- **简单界面**：易于使用的Streamlit界面

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行应用
```bash
python run.py
```
或者直接运行：
```bash
streamlit run app.py
```
# 运行功能测试
python test_app.py

# 运行单元测试
python -m pytest

### 4. 使用步骤
1. **粘贴对话**：从AI工具复制完整对话，或上传文本文件
2. **清理格式**：点击"自动清理"按钮优化格式
3. **选择消息**：使用批量操作选择要导出的消息
4. **设置信息**：填写标题、作者、课程等信息
5. **生成PDF**：点击生成按钮并下载文档

## 📁 项目结构

```
ai-chat-export/
├── app.py              # Streamlit基础版应用
├── app_enhanced.py     # Streamlit增强版应用（推荐）
├── run.py              # 启动脚本（多版本选择）
├── test_app.py         # 功能测试脚本
├── config.py           # 配置文件
├── requirements.txt    # Python依赖包
├── README.md           # 使用说明文档
├── .gitignore          # Git忽略文件
├── utils/              # 工具函数模块
│   ├── __init__.py     # 包初始化
│   ├── text_cleaner.py # 文本清理工具
│   └── pdf_generator.py # PDF生成工具
└── data/               # 数据目录
    └── exports/        # 生成的PDF文件存储
        └── .gitkeep    # 保持目录存在
```

## 支持的AI对话格式

- ChatGPT网页版
- Claude网页版
- 其他常见AI工具的对话格式
- 包含代码块的对话
- 包含列表和表格的对话

## 🛠️ 技术栈

### 核心框架
- **Streamlit**：现代化Web应用框架
- **ReportLab**：专业PDF生成库
- **Python 3.8+**：后端编程语言

### 数据处理
- **Pandas**：数据分析和处理
- **NumPy**：数值计算
- **Pillow**：图像处理（未来扩展）

### 开发工具
- **pytest**：单元测试框架
- **black**：代码格式化（建议）
- **flake8**：代码检查（建议）

## 💻 开发指南

### 代码结构说明
- `app.py`：基础版应用界面
- `app_enhanced.py`：增强版应用界面（主推）
- `config.py`：集中管理配置和常量
- `utils/text_cleaner.py`：文本清理和消息解析逻辑
- `utils/pdf_generator.py`：PDF生成和格式化逻辑

### 运行测试
```bash
# 运行所有功能测试
python test_app.py

# 运行特定模块测试
python -m pytest utils/text_cleaner.py::__main__ -v
python -m pytest utils/pdf_generator.py::__main__ -v
```

### 开发建议
1. 使用增强版 `app_enhanced.py` 作为主要开发目标
2. 通过 `config.py` 管理所有配置
3. 添加新功能时，同时更新测试脚本
4. 保持界面响应式和用户友好

## 🔮 未来规划

### 计划功能
- [ ] 支持更多AI平台格式（文心一言、通义千问等）
- [ ] 添加Word文档导出功能
- [ ] 支持对话翻译
- [ ] 添加批量处理功能
- [ ] 集成云存储（Google Drive, OneDrive）
- [ ] 添加API接口

### 界面改进
- [ ] 暗色主题支持
- [ ] 多语言界面
- [ ] 移动端优化
- [ ] 自定义主题

## 👥 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request


---

**✨ 提示**：建议使用增强版 (`app_enhanced.py`) 获得最佳体验！
