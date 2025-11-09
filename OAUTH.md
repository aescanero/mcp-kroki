# OAuth 2.1 Authentication

This document describes how to configure and use OAuth 2.1 authentication with MCP Kroki server.

## Overview

MCP Kroki supports OAuth 2.1 authentication to secure access to the server. OAuth authentication can be:
- **Enabled**: Requires valid access tokens for all requests to protected endpoints
- **Disabled** (default): Allows unrestricted access to all endpoints

## Features

- **OAuth 2.1 compliant** authentication
- **Two validation methods**:
  - Token Introspection (RFC 7662)
  - JWKS-based validation (faster, local validation)
- **Optional**: Can be completely disabled for development or open access scenarios
- **Flexible**: Works with any OAuth 2.1 compliant provider (Auth0, Keycloak, Okta, Azure AD, etc.)

## Configuration

### Environment Variables

Configure OAuth through environment variables:

```bash
# Enable/Disable OAuth
OAUTH_ENABLED=true  # Set to "false" to disable

# OAuth Provider Configuration
OAUTH_ISSUER=https://auth.example.com
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUDIENCE=https://api.example.com  # Optional but recommended

# Token Validation Method
OAUTH_TOKEN_VALIDATION=introspection  # or "jwks"

# Introspection Method (if OAUTH_TOKEN_VALIDATION=introspection)
OAUTH_INTROSPECTION_URL=https://auth.example.com/oauth2/introspect

# JWKS Method (if OAUTH_TOKEN_VALIDATION=jwks)
OAUTH_JWKS_URL=https://auth.example.com/.well-known/jwks.json
```

### Validation Methods

#### 1. Token Introspection (Recommended for Production)

Token introspection validates tokens by calling the OAuth provider's introspection endpoint.

**Pros:**
- Most accurate - detects revoked tokens immediately
- Works with opaque tokens
- Provider handles all validation logic

**Cons:**
- Requires network call for each validation
- Slightly higher latency

**Configuration:**
```bash
OAUTH_TOKEN_VALIDATION=introspection
OAUTH_INTROSPECTION_URL=https://auth.example.com/oauth2/introspect
```

#### 2. JWKS Validation (Faster, Local Validation)

JWKS validates JWT tokens locally using the provider's public keys.

**Pros:**
- Very fast - no network calls
- Lower latency

**Cons:**
- Only works with JWT tokens
- May not detect recently revoked tokens
- Requires periodic JWKS refresh

**Configuration:**
```bash
OAUTH_TOKEN_VALIDATION=jwks
OAUTH_JWKS_URL=https://auth.example.com/.well-known/jwks.json
```

## Kubernetes/Helm Configuration

### Using values.yaml

```yaml
oauth:
  enabled: true
  issuer: "https://auth.example.com"
  clientId: "your-client-id"
  clientSecret: "your-client-secret"
  audience: "https://api.example.com"
  tokenValidation: "introspection"
  introspectionUrl: "https://auth.example.com/oauth2/introspect"
```

### Using Existing Secret (Recommended)

For better security, store OAuth credentials in an existing Kubernetes secret:

1. Create the secret:
```bash
kubectl create secret generic mcp-kroki-oauth \
  --from-literal=client-id=your-client-id \
  --from-literal=client-secret=your-client-secret
```

2. Reference it in values.yaml:
```yaml
oauth:
  enabled: true
  existingSecret: "mcp-kroki-oauth"
  issuer: "https://auth.example.com"
  # ... other config
```

### Helm Install with OAuth

```bash
helm install my-mcp-kroki mcp-kroki/mcp-kroki \
  --set oauth.enabled=true \
  --set oauth.issuer=https://auth.example.com \
  --set oauth.clientId=your-client-id \
  --set oauth.clientSecret=your-client-secret \
  --set oauth.audience=https://api.example.com \
  --set oauth.tokenValidation=introspection \
  --set oauth.introspectionUrl=https://auth.example.com/oauth2/introspect
```

## Usage

### Making Authenticated Requests

When OAuth is enabled, include a valid access token in the Authorization header:

```bash
# Get an access token from your OAuth provider
ACCESS_TOKEN="your-access-token"

# Make authenticated request
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8084/health
```

### Endpoints

#### Public Endpoints (No Auth Required)

- `/health` - Health check (shows OAuth status)
- `/oauth/info` - OAuth configuration information

#### Protected Endpoints (Require Auth when OAuth enabled)

- `/protected` - Example protected endpoint
- All MCP tool endpoints (when OAuth is enabled)

#### Example: Health Check

**Without OAuth:**
```bash
curl http://localhost:8084/health
```

**With OAuth:**
```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8084/health
```

Response includes authentication status:
```json
{
  "status": "ok",
  "kroki_url": "http://localhost:8000",
  "supported_diagrams": 27,
  "validatable_diagrams": 7,
  "oauth_enabled": true,
  "authenticated": true,
  "user": {
    "sub": "user-id-12345",
    "scope": "read write"
  }
}
```

## OAuth Provider Setup Examples

### Keycloak

1. Create a client in Keycloak
2. Set Access Type to "confidential"
3. Enable "Service Accounts"
4. Configure:
```bash
OAUTH_ISSUER=https://keycloak.example.com/realms/myrealm
OAUTH_CLIENT_ID=mcp-kroki
OAUTH_CLIENT_SECRET=<client-secret>
OAUTH_INTROSPECTION_URL=https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token/introspect
OAUTH_JWKS_URL=https://keycloak.example.com/realms/myrealm/protocol/openid-connect/certs
```

### Auth0

1. Create an API in Auth0 dashboard
2. Create a Machine-to-Machine application
3. Configure:
```bash
OAUTH_ISSUER=https://your-domain.auth0.com/
OAUTH_CLIENT_ID=<client-id>
OAUTH_CLIENT_SECRET=<client-secret>
OAUTH_AUDIENCE=https://your-api-identifier
OAUTH_INTROSPECTION_URL=https://your-domain.auth0.com/oauth/token/introspection
```

### Azure AD

1. Register an application in Azure AD
2. Create a client secret
3. Configure:
```bash
OAUTH_ISSUER=https://login.microsoftonline.com/<tenant-id>/v2.0
OAUTH_CLIENT_ID=<application-id>
OAUTH_CLIENT_SECRET=<client-secret>
OAUTH_AUDIENCE=api://<application-id>
OAUTH_JWKS_URL=https://login.microsoftonline.com/<tenant-id>/discovery/v2.0/keys
```

### Okta

1. Create an API in Okta
2. Create a service application
3. Configure:
```bash
OAUTH_ISSUER=https://<your-domain>.okta.com/oauth2/default
OAUTH_CLIENT_ID=<client-id>
OAUTH_CLIENT_SECRET=<client-secret>
OAUTH_AUDIENCE=api://default
OAUTH_INTROSPECTION_URL=https://<your-domain>.okta.com/oauth2/default/v1/introspect
OAUTH_JWKS_URL=https://<your-domain>.okta.com/oauth2/default/v1/keys
```

## Disabling OAuth

To disable OAuth authentication:

### Environment Variable
```bash
OAUTH_ENABLED=false
```

### Helm
```bash
helm install my-mcp-kroki mcp-kroki/mcp-kroki \
  --set oauth.enabled=false
```

When disabled:
- All endpoints are publicly accessible
- No authentication checks are performed
- `/oauth/info` endpoint reports OAuth as disabled

## Troubleshooting

### Common Issues

#### 1. "Missing authentication token"

**Cause:** OAuth is enabled but no token was provided

**Solution:** Include Authorization header:
```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8084/endpoint
```

#### 2. "Token is not active or has been revoked"

**Cause:** Token is expired or revoked

**Solution:** Obtain a new access token from your OAuth provider

#### 3. "Invalid audience"

**Cause:** Token's audience doesn't match `OAUTH_AUDIENCE`

**Solution:** Ensure your OAuth provider issues tokens with the correct audience, or remove `OAUTH_AUDIENCE` if not needed

#### 4. "Authentication service unavailable"

**Cause:** Cannot reach OAuth introspection endpoint

**Solution:**
- Check `OAUTH_INTROSPECTION_URL` is correct
- Verify network connectivity to OAuth provider
- Consider using JWKS validation method for better availability

### Debug Logging

Enable debug logging to see authentication details:

```bash
# Set Python logging to DEBUG
export PYTHONUNBUFFERED=1
python mcp_kroki_server.py
```

Check logs for OAuth-related messages:
```
INFO - OAuth 2.1 authentication is ENABLED
INFO - Issuer: https://auth.example.com
INFO - Validation method: introspection
```

### Testing OAuth Configuration

1. Check OAuth info endpoint:
```bash
curl http://localhost:8084/oauth/info
```

2. Test with invalid token:
```bash
curl -H "Authorization: Bearer invalid-token" \
  http://localhost:8084/protected
```

Expected: 401 Unauthorized

3. Test with valid token:
```bash
curl -H "Authorization: Bearer $VALID_TOKEN" \
  http://localhost:8084/protected
```

Expected: 200 OK with user info

## Security Best Practices

1. **Always use HTTPS** in production
2. **Store client secrets securely**:
   - Use Kubernetes secrets
   - Never commit secrets to git
   - Use secret management systems (Vault, AWS Secrets Manager, etc.)
3. **Validate tokens strictly**:
   - Always set `OAUTH_AUDIENCE` in production
   - Use introspection for critical applications
4. **Monitor token usage**:
   - Log authentication attempts
   - Monitor for suspicious patterns
5. **Rotate credentials regularly**:
   - Update client secrets periodically
   - Revoke old credentials after rotation

## Performance Considerations

### Token Introspection
- Adds ~50-200ms latency per request
- Creates dependency on OAuth provider availability
- Scales with OAuth provider capacity

### JWKS Validation
- Adds ~1-10ms latency per request
- No dependency on OAuth provider for validation
- Scales independently

**Recommendation:**
- Use introspection for critical, low-traffic applications
- Use JWKS for high-traffic, performance-sensitive applications
- Consider caching strategies for introspection results

## Additional Resources

- [OAuth 2.1 Specification](https://oauth.net/2.1/)
- [RFC 7662 - Token Introspection](https://datatracker.ietf.org/doc/html/rfc7662)
- [RFC 7517 - JSON Web Key (JWK)](https://datatracker.ietf.org/doc/html/rfc7517)
- [OAuth Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
