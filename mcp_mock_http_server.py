#!/usr/bin/env python3
"""Mock MCP Server using HTTP/JSON-RPC with streaming support"""

import os
import logging
from fastmcp import FastMCP
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", 8084))
HOST = os.getenv("HOST", "0.0.0.0")

logger.info(f"Initializing Mock MCP HTTP Server on {HOST}:{PORT}")


mcp = FastMCP("mock-mcp-http-server")

@mcp.tool()
def get_weather(city: str, units: str = "celsius") -> dict:
    """Get weather information for a city"""
    logger.info(f"get_weather called for {city}")
    return {
        "city": city,
        "temperature": 22.5,
        "units": units,
        "condition": "Partly cloudy",
        "humidity": 65,
    }


@mcp.tool()
def search_web(query: str, limit: int = 10) -> dict:
    """Search the web for information"""
    logger.info(f"search_web called with query: {query}")
    return {
        "query": query,
        "results": [
            {
                "title": f"Result {i + 1}",
                "url": f"https://example.com/result{i + 1}",
                "snippet": f"Mock result for query: {query}",
            }
            for i in range(min(limit, 10))
        ],
        "total": limit,
    }


@mcp.tool()
def send_email(recipient: str, subject: str, body: str) -> dict:
    """Send an email (mock implementation)"""
    logger.info(f"send_email called to {recipient}")
    return {
        "success": True,
        "recipient": recipient,
        "subject": subject,
        "message_id": f"mock-{hash(recipient + subject) % 1000000}",
        "timestamp": "2024-11-03T12:00:00Z",
    }

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins; use specific origins for security
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=[
            "mcp-protocol-version",
            "mcp-session-id",
            "Authorization",
            "Content-Type",
        ],
        expose_headers=["mcp-session-id"],
    )
]

# Create the MCP HTTP app with streaming support (no SSE)
mcp_app = mcp.http_app(middleware=middleware)

# Create FastAPI app with MCP lifespan
app = FastAPI(
    redirect_slashes=False,
    lifespan=mcp_app.lifespan  # IMPORTANT: Pass the MCP app lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def status():
    return {"status": "ok"}

# Mount the MCP app at the root
app.mount("/", mcp_app)
