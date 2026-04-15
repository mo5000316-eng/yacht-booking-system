#!/bin/bash
# Tomorrow World 遊艇預訂系統 - 啟動腳本

echo "=========================================="
echo "  Tomorrow World 遊艇預訂系統"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 請先安裝 Python 3"
    exit 1
fi

# Install dependencies
echo "📦 安裝套件..."
pip3 install -r requirements.txt

echo ""
echo "🚀 啟動伺服器..."
echo "   網址：http://localhost:5000"
echo "   Admin 後台：http://localhost:5000/admin"
echo ""
echo "   預設帳號："
echo "   Admin:  admin / Admin@123"
echo "   Staff:  staff1 / Staff@123"
echo ""
echo "按 Ctrl+C 停止伺服器"
echo "=========================================="

python3 app.py
