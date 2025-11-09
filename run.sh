#!/bin/bash
# Run script for mcp-kroki server

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default values
PORT=${PORT:-8084}
HOST=${HOST:-0.0.0.0}
KROKI_URL=${KROKI_URL:-http://localhost:8000}

echo "Starting Kroki MCP Server..."
echo "Server: http://${HOST}:${PORT}"
echo "Kroki URL: ${KROKI_URL}"
echo ""

# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "uvicorn not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the server
uvicorn mcp_kroki_server:app --host "${HOST}" --port "${PORT}" --reload
