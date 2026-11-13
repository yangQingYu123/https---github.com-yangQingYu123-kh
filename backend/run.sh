#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then

    python3 -m venv .venv
fi

source .venv/bin/activate

pip install -q -r requirements.txt



echo "==> 启动后端  http://127.0.0.1:8000"
echo "==> 接口文档  http://127.0.0.1:8000/docs"
echo "==> 默认账号  admin / admin123"
echo ""
python run.py
