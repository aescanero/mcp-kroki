# MCP Kroki Helm Chart

A Helm chart for deploying MCP Kroki server - Streamable HTTP MCP server for Kroki diagrams on Kubernetes.

## Introduction

This chart bootstraps an MCP Kroki deployment on a Kubernetes cluster using the Helm package manager. It can optionally deploy a Kroki server alongside the MCP server.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+

## Installing the Chart

### Add the Helm repository

```bash
helm repo add mcp-kroki https://aescanero.github.io/mcp-kroki
helm repo update
```

### Install the chart

```bash
# Install with default values (includes Kroki server)
helm install my-mcp-kroki mcp-kroki/mcp-kroki

# Install with custom values
helm install my-mcp-kroki mcp-kroki/mcp-kroki -f values.yaml

# Install in a specific namespace
helm install my-mcp-kroki mcp-kroki/mcp-kroki --namespace mcp-kroki --create-namespace
```

## Uninstalling the Chart

```bash
helm uninstall my-mcp-kroki
```

## Configuration

The following table lists the configurable parameters of the MCP Kroki chart and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of MCP Kroki replicas | `1` |
| `image.repository` | MCP Kroki image repository | `aescanero/mcp-kroki` |
| `image.tag` | MCP Kroki image tag | `""` (defaults to chart appVersion) |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `nameOverride` | Override chart name | `""` |
| `fullnameOverride` | Override full name | `""` |

### Service Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8084` |
| `service.annotations` | Service annotations | `{}` |

### Ingress Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.annotations` | Ingress annotations | `{}` |
| `ingress.hosts` | Ingress hosts configuration | See values.yaml |
| `ingress.tls` | Ingress TLS configuration | `[]` |

### MCP Kroki Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `config.krokiUrl` | External Kroki server URL (used when kroki.enabled=false) | `http://kroki:8000` |
| `config.host` | Host to bind MCP server | `0.0.0.0` |
| `config.port` | Port to bind MCP server | `8084` |

### Kroki Server Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `kroki.enabled` | Deploy Kroki server alongside MCP Kroki | `true` |
| `kroki.image.repository` | Kroki image repository | `yuzutech/kroki` |
| `kroki.image.tag` | Kroki image tag | `latest` |
| `kroki.service.type` | Kroki service type | `ClusterIP` |
| `kroki.service.port` | Kroki service port | `8000` |
| `kroki.resources` | Kroki resource requests/limits | `{}` |

### Autoscaling Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable HPA | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `1` |
| `autoscaling.maxReplicas` | Maximum replicas | `100` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization | `80` |

## Examples

### Deploy with external Kroki server

```bash
helm install my-mcp-kroki mcp-kroki/mcp-kroki \
  --set kroki.enabled=false \
  --set config.krokiUrl=https://kroki.example.com
```

### Deploy with Ingress

```bash
helm install my-mcp-kroki mcp-kroki/mcp-kroki \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --set ingress.hosts[0].host=mcp-kroki.example.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix
```

### Deploy with resource limits

```bash
helm install my-mcp-kroki mcp-kroki/mcp-kroki \
  --set resources.limits.cpu=200m \
  --set resources.limits.memory=256Mi \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=128Mi
```

### Deploy with autoscaling enabled

```bash
helm install my-mcp-kroki mcp-kroki/mcp-kroki \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10 \
  --set autoscaling.targetCPUUtilizationPercentage=70
```

## Values File Example

Create a `my-values.yaml` file:

```yaml
replicaCount: 2

image:
  tag: "1.0.0"

service:
  type: LoadBalancer

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: mcp-kroki.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

kroki:
  enabled: true
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi
```

Then install:

```bash
helm install my-mcp-kroki mcp-kroki/mcp-kroki -f my-values.yaml
```

## Upgrading

```bash
# Upgrade to latest version
helm upgrade my-mcp-kroki mcp-kroki/mcp-kroki

# Upgrade with new values
helm upgrade my-mcp-kroki mcp-kroki/mcp-kroki -f my-values.yaml
```

## Accessing the Application

After installation, follow the instructions in the NOTES to access your MCP Kroki server:

```bash
# Port forward to access locally
export POD_NAME=$(kubectl get pods -l "app.kubernetes.io/name=mcp-kroki" -o jsonpath="{.items[0].metadata.name}")
kubectl port-forward $POD_NAME 8084:8084

# Check health
curl http://localhost:8084/health
```

## Supported Diagram Types

- **Block Diagram Family**: blockdiag, seqdiag, actdiag, nwdiag, packetdiag, rackdiag
- **General Purpose**: bpmn, bytefield, c4plantuml, d2, dbml, ditaa, erd, excalidraw
- **Code & Architecture**: graphviz, mermaid, nomnoml, pikchr, plantuml, structurizr
- **Specialized**: svgbob, symbolator, umlet, vega, vegalite, wavedrom, wireviz

## Troubleshooting

### Check pod status

```bash
kubectl get pods -l app.kubernetes.io/name=mcp-kroki
```

### View logs

```bash
kubectl logs -l app.kubernetes.io/name=mcp-kroki -f
```

### Describe deployment

```bash
kubectl describe deployment -l app.kubernetes.io/name=mcp-kroki
```

## License

See LICENSE file in the repository.

## Links

- **Source Code**: https://github.com/aescanero/mcp-kroki
- **Docker Hub**: https://hub.docker.com/r/aescanero/mcp-kroki
- **Kroki Documentation**: https://kroki.io/
