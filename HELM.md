# Helm Chart Documentation

This document provides comprehensive information about deploying MCP Kroki using Helm.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Upgrading](#upgrading)
- [Uninstallation](#uninstallation)
- [Troubleshooting](#troubleshooting)

## Quick Start

```bash
# Add the Helm repository
helm repo add mcp-kroki https://aescanero.github.io/mcp-kroki
helm repo update

# Install the chart
helm install my-mcp-kroki mcp-kroki/mcp-kroki

# Check the installation
kubectl get pods -l app.kubernetes.io/name=mcp-kroki
```

## Prerequisites

- Kubernetes cluster 1.19+
- Helm 3.0+
- kubectl configured to communicate with your cluster

## Installation

### Add Helm Repository

```bash
helm repo add mcp-kroki https://aescanero.github.io/mcp-kroki
helm repo update
```

### Install with Default Values

This will deploy both MCP Kroki and a Kroki server:

```bash
helm install my-mcp-kroki mcp-kroki/mcp-kroki
```

### Install in Specific Namespace

```bash
helm install my-mcp-kroki mcp-kroki/mcp-kroki \
  --namespace mcp-kroki \
  --create-namespace
```

### Install with Custom Values

Create a `values.yaml` file:

```yaml
replicaCount: 2

service:
  type: LoadBalancer

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
```

Install with custom values:

```bash
helm install my-mcp-kroki mcp-kroki/mcp-kroki -f values.yaml
```

## Configuration

### Key Configuration Options

#### MCP Kroki Server

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Docker image repository | `aescanero/mcp-kroki` |
| `image.tag` | Image tag | Chart appVersion |
| `replicaCount` | Number of replicas | `1` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8084` |

#### Kroki Server

| Parameter | Description | Default |
|-----------|-------------|---------|
| `kroki.enabled` | Deploy Kroki server | `true` |
| `kroki.image.repository` | Kroki image | `yuzutech/kroki` |
| `kroki.service.port` | Kroki service port | `8000` |

#### Ingress

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class | `""` |
| `ingress.hosts` | Ingress hosts | See values.yaml |

### Full Configuration Reference

For a complete list of configuration options, see:
- [charts/mcp-kroki/values.yaml](charts/mcp-kroki/values.yaml)
- [charts/mcp-kroki/README.md](charts/mcp-kroki/README.md)

## Usage Examples

### Example 1: Basic Deployment

Deploy with all defaults (includes Kroki server):

```bash
helm install mcp-kroki mcp-kroki/mcp-kroki
```

### Example 2: Use External Kroki Server

If you have an existing Kroki server:

```bash
helm install mcp-kroki mcp-kroki/mcp-kroki \
  --set kroki.enabled=false \
  --set config.krokiUrl=https://kroki.mycompany.com
```

### Example 3: Deploy with Ingress (NGINX)

```bash
helm install mcp-kroki mcp-kroki/mcp-kroki \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --set ingress.hosts[0].host=mcp-kroki.example.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix
```

### Example 4: Deploy with Ingress and TLS

First, create a TLS secret:

```bash
kubectl create secret tls mcp-kroki-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

Then install with TLS:

```bash
helm install mcp-kroki mcp-kroki/mcp-kroki \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --set ingress.hosts[0].host=mcp-kroki.example.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.tls[0].secretName=mcp-kroki-tls \
  --set ingress.tls[0].hosts[0]=mcp-kroki.example.com
```

### Example 5: Production Deployment with Resources

Create `production-values.yaml`:

```yaml
replicaCount: 3

image:
  pullPolicy: Always

service:
  type: ClusterIP
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

kroki:
  enabled: true
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: mcp-kroki.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: mcp-kroki-tls
      hosts:
        - mcp-kroki.example.com
```

Deploy:

```bash
helm install mcp-kroki mcp-kroki/mcp-kroki \
  -f production-values.yaml \
  --namespace production \
  --create-namespace
```

### Example 6: Development/Testing with NodePort

```bash
helm install mcp-kroki mcp-kroki/mcp-kroki \
  --set service.type=NodePort \
  --namespace dev \
  --create-namespace

# Get the NodePort
kubectl get svc -n dev
```

## Upgrading

### Upgrade to Latest Version

```bash
helm repo update
helm upgrade mcp-kroki mcp-kroki/mcp-kroki
```

### Upgrade to Specific Version

```bash
helm upgrade mcp-kroki mcp-kroki/mcp-kroki --version 1.0.0
```

### Upgrade with New Values

```bash
helm upgrade mcp-kroki mcp-kroki/mcp-kroki -f new-values.yaml
```

### Check Upgrade Diff

```bash
helm diff upgrade mcp-kroki mcp-kroki/mcp-kroki -f new-values.yaml
```

## Uninstallation

### Uninstall Release

```bash
helm uninstall mcp-kroki
```

### Uninstall from Specific Namespace

```bash
helm uninstall mcp-kroki --namespace mcp-kroki
```

## Troubleshooting

### Check Helm Release Status

```bash
helm status mcp-kroki
helm list
```

### Check Pod Status

```bash
kubectl get pods -l app.kubernetes.io/name=mcp-kroki
```

### View Pod Logs

```bash
# MCP Kroki logs
kubectl logs -l app.kubernetes.io/name=mcp-kroki -f

# Kroki server logs
kubectl logs -l app.kubernetes.io/component=kroki -f
```

### Describe Resources

```bash
kubectl describe deployment -l app.kubernetes.io/name=mcp-kroki
kubectl describe service -l app.kubernetes.io/name=mcp-kroki
```

### Test Connectivity

```bash
# Port forward to test locally
kubectl port-forward svc/mcp-kroki 8084:8084

# In another terminal
curl http://localhost:8084/health
```

### Common Issues

#### Pods Not Starting

Check pod events:
```bash
kubectl describe pod <pod-name>
```

Check resource constraints:
```bash
kubectl top nodes
kubectl top pods
```

#### Image Pull Errors

Check if the image exists:
```bash
docker pull aescanero/mcp-kroki:latest
```

Verify image pull secrets if using private registry:
```bash
kubectl get secrets
```

#### Service Not Accessible

Check service endpoints:
```bash
kubectl get endpoints -l app.kubernetes.io/name=mcp-kroki
```

Check network policies:
```bash
kubectl get networkpolicies
```

#### Kroki Connection Issues

If MCP Kroki can't connect to Kroki:

```bash
# Check Kroki service
kubectl get svc -l app.kubernetes.io/component=kroki

# Test Kroki connectivity from MCP pod
kubectl exec -it <mcp-kroki-pod> -- curl http://kroki:8000
```

### Debug Mode

Enable debug logging:

```bash
helm upgrade mcp-kroki mcp-kroki/mcp-kroki \
  --set podAnnotations.debug=true
```

### Rollback

If an upgrade fails, rollback to previous version:

```bash
helm rollback mcp-kroki
```

Rollback to specific revision:

```bash
helm history mcp-kroki
helm rollback mcp-kroki <revision>
```

## Additional Resources

- **Chart Repository**: https://aescanero.github.io/mcp-kroki
- **Source Code**: https://github.com/aescanero/mcp-kroki
- **Docker Hub**: https://hub.docker.com/r/aescanero/mcp-kroki
- **Kroki Documentation**: https://kroki.io/
- **Helm Documentation**: https://helm.sh/docs/

## Support

For issues and questions:
- GitHub Issues: https://github.com/aescanero/mcp-kroki/issues
- Chart Issues: Label with `helm-chart`
