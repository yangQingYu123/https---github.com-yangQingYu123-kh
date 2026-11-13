#!/usr/bin/env bash

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "❌ 未找到 python，请先安装 Python 3.8+"
fi


cd "$(dirname "$0")/backend" 

if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
fi

source venv/bin/activate

$PYTHON -m pip install -r requirements.txt



echo "==> 启动后端  http://127.0.0.1:8000"
echo "==> 接口文档  http://127.0.0.1:8000/docs"
echo "==> 默认账号  admin / admin123"
echo ""
$PYTHON run.py
