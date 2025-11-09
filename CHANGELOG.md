# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Streamable HTTP MCP server for Kroki diagrams
- Support for 27+ diagram types from Kroki
- Generate tools for all diagram types with multiple output formats (SVG, PNG, PDF, JPEG)
- Validation tools for 7 diagram types with schema/parser support
- Utility tools: `obtain_svg_from_diagram` and `save_diagram`
- Docker support with Dockerfile and docker-compose.yml
- GitHub Actions workflow for automated Docker builds and publishing
- Comprehensive documentation (README.md, RELEASE.md)
- Health check endpoint
- Multi-platform Docker images (linux/amd64, linux/arm64)

### Supported Diagram Types
- Block Diagram Family: blockdiag, seqdiag, actdiag, nwdiag, packetdiag, rackdiag
- General Purpose: bpmn, bytefield, c4plantuml, d2, dbml, ditaa, erd, excalidraw
- Code & Architecture: graphviz, mermaid, nomnoml, pikchr, plantuml, structurizr
- Specialized: svgbob, symbolator, umlet, vega, vegalite, wavedrom, wireviz

### Validation Support
- vega (JSON Schema)
- vegalite (JSON Schema)
- dbml (Parser validation)
- mermaid (Parser validation)
- plantuml (Parser validation)
- bpmn (XML Schema)
- graphviz (Parser validation)

## [0.1.0] - YYYY-MM-DD (Template)

### Added
- Initial release
- Basic functionality

### Changed
- Updated dependencies

### Fixed
- Bug fixes

### Removed
- Deprecated features

---

**Note:** Replace YYYY-MM-DD with actual release dates. Update this file before each release.
