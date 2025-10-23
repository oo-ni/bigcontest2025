#!/bin/bash
# MCP 서버 실행 스크립트

cd "$(dirname "$0")/.."

echo "Starting MCP RAG Server..."

# 가상환경 활성화 (필요한 경우)
# source venv/bin/activate

cd mcp_server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
