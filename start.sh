#!/bin/bash
# 自动发布机器人 - 快速启动脚本

echo "============================================================"
echo "🤖 自动发布机器人 - 启动脚本"
echo "============================================================"
echo ""

# 检查 Python 版本
echo "📋 检查 Python 环境..."
python3 --version

# 安装依赖
echo ""
echo "📦 安装依赖..."
pip3 install -r requirements.txt -q

# 启动后端服务
echo ""
echo "🚀 启动后端服务..."
echo "   API 地址：http://localhost:8000"
echo "   文档地址：http://localhost:8000/docs"
echo ""
echo "💡 提示：在浏览器中打开 frontend.html 即可使用"
echo ""

# 启动服务
python3 backend.py
