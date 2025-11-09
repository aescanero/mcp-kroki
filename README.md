# mcp-kroki

Streamable HTTP MCP server for usage with local or remote Kroki instances.

## Overview

This MCP (Model Context Protocol) server provides tools to generate, validate, and manage diagrams using Kroki. It supports all diagram types available in Kroki and provides a streamable HTTP interface.

## Features

- **27+ Diagram Types Supported**: Including PlantUML, Mermaid, GraphViz, D2, BPMN, and many more
- **4 Tool Categories per Diagram Type**:
  - `generate_diagram_xxx`: Generate diagrams in various formats (SVG, PNG, PDF, JPEG)
  - `validate_diagram_xxx`: Validate diagram syntax (available for diagram types with schema support)
  - `obtain_svg_from_diagram`: Fetch diagram content from a Kroki URL
  - `save_diagram`: Save diagram from URL to a local file

## Supported Diagram Types

- **Block Diagram Family**: blockdiag, seqdiag, actdiag, nwdiag, packetdiag, rackdiag
- **General Purpose**: bpmn, bytefield, c4plantuml, d2, dbml, ditaa, erd, excalidraw
- **Code & Architecture**: graphviz, mermaid, nomnoml, pikchr, plantuml, structurizr
- **Specialized**: svgbob, symbolator, umlet, vega, vegalite, wavedrom, wireviz

## Quick Start with Docker

The easiest way to run mcp-kroki is using the pre-built Docker image from Docker Hub:

```bash
# Pull the latest image
docker pull aescanero/mcp-kroki:latest

# Run the container
docker run -d -p 8084:8084 \
  -e KROKI_URL=http://your-kroki-server:8000 \
  aescanero/mcp-kroki:latest
```

### Docker Hub

**Repository:** https://hub.docker.com/r/aescanero/mcp-kroki

**Available Tags:**
- `latest` - Most recent stable release
- `1.0.0` - Specific version (example)
- `1.0` - Latest patch in version 1.0
- `1` - Latest release in major version 1

### Using Docker Compose

Create a `docker-compose.yml`:

```yaml
version: "3.8"

services:
  kroki:
    image: yuzutech/kroki
    ports:
      - "8000:8000"

  mcp-kroki:
    image: aescanero/mcp-kroki:latest
    ports:
      - "8084:8084"
    environment:
      - KROKI_URL=http://kroki:8000
      - HOST=0.0.0.0
      - PORT=8084
    depends_on:
      - kroki
```

Then run:
```bash
docker-compose up -d
```

## Installation from Source

1. Clone the repository:
```bash
git clone https://github.com/aescanero/mcp-kroki.git
cd mcp-kroki
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env to set your Kroki server URL
```

## Configuration

Create a `.env` file with the following variables:

```env
# Kroki server URL (local or remote instance)
KROKI_URL=http://localhost:8000

# Server configuration
HOST=0.0.0.0
PORT=8084
```

## Running the Server

### Using Python directly:
```bash
python mcp_kroki_server.py
```

### Using uvicorn:
```bash
uvicorn mcp_kroki_server:app --host 0.0.0.0 --port 8084
```

The server will be available at `http://localhost:8084`

## Usage Examples

### Generate a PlantUML Diagram

```json
{
  "tool": "generate_diagram_plantuml",
  "arguments": {
    "diagram_source": "@startuml\nAlice -> Bob: Hello\n@enduml",
    "output_format": "svg"
  }
}
```

### Validate a Mermaid Diagram

```json
{
  "tool": "validate_diagram_mermaid",
  "arguments": {
    "diagram_source": "graph TD\n  A-->B"
  }
}
```

### Obtain SVG from URL

```json
{
  "tool": "obtain_svg_from_diagram",
  "arguments": {
    "diagram_url": "http://localhost:8000/plantuml/svg/SyfFKj2rKt3CoKnELR1Io4ZDoSa70000"
  }
}
```

### Save Diagram to File

```json
{
  "tool": "save_diagram",
  "arguments": {
    "diagram_url": "http://localhost:8000/mermaid/svg/...",
    "output_path": "/path/to/diagram.svg"
  }
}
```

## Available Tools

### Generation Tools (27 types)
Each diagram type has a `generate_diagram_{type}` tool that accepts:
- `diagram_source` (string): The diagram source code
- `output_format` (string, optional): Output format (svg, png, pdf, jpeg, base64). Default: svg

### Validation Tools (7 types)
Validation is available for diagram types with schema or parser validation support:
- `validate_diagram_vega`
- `validate_diagram_vegalite`
- `validate_diagram_dbml`
- `validate_diagram_mermaid`
- `validate_diagram_plantuml`
- `validate_diagram_bpmn`
- `validate_diagram_graphviz`

Each validation tool accepts:
- `diagram_source` (string): The diagram source code to validate

### Utility Tools
- `obtain_svg_from_diagram`: Fetch diagram content from a Kroki URL
  - `diagram_url` (string): Full Kroki diagram URL

- `save_diagram`: Save diagram from URL to local file
  - `diagram_url` (string): Full Kroki diagram URL
  - `output_path` (string): Local file path for saving

## Health Check

Check server status:
```bash
curl http://localhost:8084/health
```

Response:
```json
{
  "status": "ok",
  "kroki_url": "http://localhost:8000",
  "supported_diagrams": 27,
  "validatable_diagrams": 7
}
```

## Requirements

- Python 3.8+
- Kroki server (local or remote)
- See `requirements.txt` for Python dependencies

## Setting up a Local Kroki Server

Using Docker:
```bash
docker run -d -p 8000:8000 yuzutech/kroki
```

Using Docker Compose:
```yaml
version: "3"
services:
  kroki:
    image: yuzutech/kroki
    ports:
      - "8000:8000"
```

## Deployment

### Automated Releases

This project uses GitHub Actions to automatically build and publish Docker images when a new version tag is pushed.

**To create a new release:**

```bash
# Create a version tag (following semantic versioning)
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push the tag to GitHub
git push origin v1.0.0
```

The GitHub Action will automatically:
1. Build the Docker image for multiple platforms (linux/amd64, linux/arm64)
2. Tag the image with multiple versions (latest, 1.0.0, 1.0, 1)
3. Push to Docker Hub at https://hub.docker.com/r/aescanero/mcp-kroki

For detailed information about the release process, see [RELEASE.md](RELEASE.md).

## Development

### Running Locally for Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn mcp_kroki_server:app --reload --host 0.0.0.0 --port 8084
```

### Building Docker Image Locally

```bash
# Build the image
docker build -t mcp-kroki:dev .

# Run the image
docker run -p 8084:8084 -e KROKI_URL=http://localhost:8000 mcp-kroki:dev
```

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Issues**: https://github.com/aescanero/mcp-kroki/issues
- **Docker Hub**: https://hub.docker.com/r/aescanero/mcp-kroki
- **Kroki Documentation**: https://kroki.io/
