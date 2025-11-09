#!/usr/bin/env python3
"""Kroki MCP Server using HTTP/JSON-RPC with streaming support"""

import os
import logging
import base64
import zlib
import requests
from typing import Optional
from fastmcp import FastMCP
from fastapi import FastAPI, Depends
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Import OAuth middleware
from oauth_middleware import get_current_user, optional_authentication, oauth_validator

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", 8084))
HOST = os.getenv("HOST", "0.0.0.0")
KROKI_URL = os.getenv("KROKI_URL", "http://localhost:8000")

logger.info(f"Initializing Kroki MCP HTTP Server on {HOST}:{PORT}")
logger.info(f"Kroki server URL: {KROKI_URL}")

# Log OAuth status
if oauth_validator.enabled:
    logger.info("OAuth 2.1 authentication is ENABLED")
else:
    logger.info("OAuth 2.1 authentication is DISABLED")

mcp = FastMCP("kroki-mcp-server")

# Supported diagram types from Kroki
DIAGRAM_TYPES = [
    "blockdiag", "seqdiag", "actdiag", "nwdiag", "packetdiag", "rackdiag",
    "bpmn", "bytefield", "c4plantuml", "d2", "dbml", "ditaa", "erd",
    "excalidraw", "graphviz", "mermaid", "nomnoml", "pikchr", "plantuml",
    "structurizr", "svgbob", "symbolator", "umlet", "vega", "vegalite",
    "wavedrom", "wireviz"
]

# Diagram types that support validation (through schema or library capabilities)
# Based on research, these formats have formal schemas or validation capabilities
VALIDATABLE_TYPES = {
    "vega": "JSON Schema",
    "vegalite": "JSON Schema",
    "dbml": "Parser validation",
    "mermaid": "Parser validation",
    "plantuml": "Parser validation",
    "bpmn": "XML Schema",
    "graphviz": "Parser validation"
}


def encode_diagram(diagram_source: str) -> str:
    """Encode diagram source for Kroki URL"""
    compressed = zlib.compress(diagram_source.encode('utf-8'), level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')
    return encoded


def call_kroki(diagram_type: str, diagram_source: str, output_format: str = "svg") -> dict:
    """
    Call Kroki API to generate diagram

    Args:
        diagram_type: Type of diagram (e.g., 'plantuml', 'mermaid')
        diagram_source: Source code of the diagram
        output_format: Output format (svg, png, pdf, jpeg, base64)

    Returns:
        dict with success status, data/error, and diagram_url
    """
    try:
        # Method 1: POST request with JSON payload (preferred)
        url = f"{KROKI_URL}/{diagram_type}/{output_format}"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "diagram_source": diagram_source
        }

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            # Generate URL for reference
            encoded = encode_diagram(diagram_source)
            diagram_url = f"{KROKI_URL}/{diagram_type}/{output_format}/{encoded}"

            if output_format in ["svg", "txt"]:
                result_data = response.text
            else:
                result_data = base64.b64encode(response.content).decode('utf-8')

            return {
                "success": True,
                "data": result_data,
                "diagram_url": diagram_url,
                "format": output_format
            }
        else:
            return {
                "success": False,
                "error": f"Kroki server returned error: {response.status_code} - {response.text}",
                "status_code": response.status_code
            }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Kroki: {e}")
        return {
            "success": False,
            "error": f"Failed to connect to Kroki server: {str(e)}"
        }


# Generate tools for each diagram type
def create_generate_tool(diagram_type: str):
    """Create a generate tool for a specific diagram type"""

    @mcp.tool()
    def tool(diagram_source: str, output_format: str = "svg") -> dict:
        f"""Generate {diagram_type} diagram

        Args:
            diagram_source: Source code for the {diagram_type} diagram
            output_format: Output format (svg, png, pdf, jpeg, base64). Default: svg

        Returns:
            Dictionary with diagram data and URL
        """
        logger.info(f"Generating {diagram_type} diagram")
        return call_kroki(diagram_type, diagram_source, output_format)

    # Set the function name dynamically
    tool.__name__ = f"generate_diagram_{diagram_type}"
    return tool


def create_validate_tool(diagram_type: str):
    """Create a validate tool for diagram types that support validation"""

    @mcp.tool()
    def tool(diagram_source: str) -> dict:
        f"""Validate {diagram_type} diagram syntax

        This tool validates the diagram syntax by attempting to generate it.
        Validation method: {VALIDATABLE_TYPES.get(diagram_type, 'Parser validation')}

        Args:
            diagram_source: Source code for the {diagram_type} diagram

        Returns:
            Dictionary with validation result
        """
        logger.info(f"Validating {diagram_type} diagram")
        result = call_kroki(diagram_type, diagram_source, "svg")

        if result["success"]:
            return {
                "valid": True,
                "message": f"{diagram_type} diagram syntax is valid",
                "validation_method": VALIDATABLE_TYPES.get(diagram_type, "Parser validation")
            }
        else:
            return {
                "valid": False,
                "message": f"{diagram_type} diagram syntax is invalid",
                "error": result.get("error", "Unknown error"),
                "validation_method": VALIDATABLE_TYPES.get(diagram_type, "Parser validation")
            }

    tool.__name__ = f"validate_diagram_{diagram_type}"
    return tool


# Register tools for all diagram types
for dtype in DIAGRAM_TYPES:
    create_generate_tool(dtype)

    # Only create validate tool for types that support validation
    if dtype in VALIDATABLE_TYPES:
        create_validate_tool(dtype)


@mcp.tool()
def obtain_svg_from_diagram(diagram_url: str) -> dict:
    """Obtain SVG content from a Kroki diagram URL

    This tool fetches the SVG content from a Kroki diagram URL so you don't have to
    access the URL directly. Useful for displaying diagrams inline.

    Args:
        diagram_url: Full Kroki diagram URL (e.g., http://localhost:8000/plantuml/svg/...)

    Returns:
        Dictionary with SVG content and metadata
    """
    try:
        logger.info(f"Fetching diagram from URL: {diagram_url}")
        response = requests.get(diagram_url, timeout=30)

        if response.status_code == 200:
            # Determine format from URL
            format_type = "svg" if "/svg/" in diagram_url else "unknown"

            return {
                "success": True,
                "content": response.text,
                "format": format_type,
                "url": diagram_url
            }
        else:
            return {
                "success": False,
                "error": f"Failed to fetch diagram: {response.status_code} - {response.text}"
            }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching diagram: {e}")
        return {
            "success": False,
            "error": f"Failed to fetch diagram: {str(e)}"
        }


@mcp.tool()
def save_diagram(diagram_url: str, output_path: str) -> dict:
    """Save a diagram from a Kroki URL to a local file

    This tool fetches the diagram from a Kroki URL and saves it to a local file.

    Args:
        diagram_url: Full Kroki diagram URL (e.g., http://localhost:8000/plantuml/svg/...)
        output_path: Local file path where the diagram should be saved

    Returns:
        Dictionary with operation result
    """
    try:
        logger.info(f"Saving diagram from URL: {diagram_url} to {output_path}")
        response = requests.get(diagram_url, timeout=30)

        if response.status_code == 200:
            # Determine if binary or text format
            if "/svg/" in diagram_url or "/txt/" in diagram_url:
                # Text format
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            else:
                # Binary format (png, pdf, jpeg)
                with open(output_path, 'wb') as f:
                    f.write(response.content)

            return {
                "success": True,
                "message": f"Diagram saved to {output_path}",
                "file_path": output_path,
                "url": diagram_url
            }
        else:
            return {
                "success": False,
                "error": f"Failed to fetch diagram: {response.status_code} - {response.text}"
            }

    except Exception as e:
        logger.error(f"Error saving diagram: {e}")
        return {
            "success": False,
            "error": f"Failed to save diagram: {str(e)}"
        }


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
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

# Create the MCP HTTP app with streaming support
mcp_app = mcp.http_app(middleware=middleware)

# Create FastAPI app with MCP lifespan
app = FastAPI(
    redirect_slashes=False,
    lifespan=mcp_app.lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def status(user: Optional[dict] = Depends(optional_authentication)):
    """Health check endpoint - public but provides extra info if authenticated"""
    response = {
        "status": "ok",
        "kroki_url": KROKI_URL,
        "supported_diagrams": len(DIAGRAM_TYPES),
        "validatable_diagrams": len(VALIDATABLE_TYPES),
        "oauth_enabled": oauth_validator.enabled
    }

    # Add user info if authenticated
    if user:
        response["authenticated"] = True
        response["user"] = {
            "sub": user.get("sub"),
            "scope": user.get("scope", "")
        }
    else:
        response["authenticated"] = False

    return response


@app.get("/oauth/info")
def oauth_info():
    """OAuth configuration information endpoint - public"""
    if not oauth_validator.enabled:
        return {
            "enabled": False,
            "message": "OAuth authentication is disabled"
        }

    return {
        "enabled": True,
        "issuer": oauth_validator.issuer,
        "client_id": oauth_validator.client_id,
        "audience": oauth_validator.audience,
        "validation_method": oauth_validator.validation_method,
        "jwks_url": oauth_validator.jwks_url if oauth_validator.validation_method == "jwks" else None,
        "introspection_url": oauth_validator.introspection_url if oauth_validator.validation_method == "introspection" else None
    }


@app.get("/protected")
def protected_endpoint(user: dict = Depends(get_current_user)):
    """
    Example protected endpoint - requires valid OAuth token if OAuth is enabled
    If OAuth is disabled, this endpoint is accessible without authentication
    """
    if user is None:
        # OAuth is disabled
        return {
            "message": "This endpoint is unprotected (OAuth disabled)",
            "oauth_enabled": False
        }

    # OAuth is enabled and user is authenticated
    return {
        "message": "Successfully authenticated!",
        "oauth_enabled": True,
        "user": {
            "sub": user.get("sub"),
            "scope": user.get("scope", ""),
            "client_id": user.get("client_id", user.get("azp", "")),
        }
    }


# Mount the MCP app at the root
app.mount("/", mcp_app)
