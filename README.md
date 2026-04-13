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

### 3. 使用步骤
1. **粘贴对话**：从AI工具复制完整对话，或上传文本文件
2. **清理格式**：点击"自动清理"按钮优化格式
3. **选择消息**：使用批量操作选择要导出的消息
4. **设置信息**：填写标题、作者、课程等信息
5. **生成PDF**：点击生成按钮并下载文档



## 支持的AI对话格式

- DeepSeek网页版
- Claude网页版
- 其他常见AI工具的对话格式
- 包含代码块的对话


## 🔮 未来规划

### 计划功能
- [ ] 支持更多AI平台格式（文心一言、通义千问等）
- [ ] 添加批量处理功能

### 界面改进
- [ ] 暗色主题支持
- [ ] 多语言界面


## 👥 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request


---
