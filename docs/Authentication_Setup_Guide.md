# Vimarsh Authentication Configuration Guide

## Overview

Vimarsh implements the unified Vedprakash domain authentication standard using Microsoft Entra ID. This document provides configuration guidance for development and production environments.

## Environment Variables

### Frontend Configuration (.env.local or environment)

```bash
# Microsoft Entra ID Configuration
REACT_APP_CLIENT_ID=your-vimarsh-app-client-id
REACT_APP_AUTHORITY=https://login.microsoftonline.com/vedid.onmicrosoft.com
REACT_APP_REDIRECT_URI=https://vimarsh.vedprakash.net/auth/callback
REACT_APP_POST_LOGOUT_REDIRECT_URI=https://vimarsh.vedprakash.net

# Development Configuration
NODE_ENV=development  # Use placeholder auth
# NODE_ENV=production  # Use real MSAL auth
```

### Backend Configuration

```bash
# Microsoft Entra ID Configuration
ENTRA_TENANT_ID=vedid.onmicrosoft.com
ENTRA_CLIENT_ID=your-vimarsh-app-client-id

# Optional: For client secret flow (if using confidential client)
ENTRA_CLIENT_SECRET=your-app-client-secret

# Azure Function Configuration
AZURE_FUNCTIONS_ENVIRONMENT=Development
```

## Authentication Modes

### Development Mode (Placeholder Authentication)

**When**: `NODE_ENV=development` and missing required REACT_APP_CLIENT_ID
**Behavior**: Uses PlaceholderAuthService with mock users
**Benefits**: No external dependencies, fast development iteration

**Mock Users Available**:
- **Arjuna Dev** (`arjuna@vimarsh.dev`) - Seeker role
- **Meera भक्त** (`meera@vimarsh.dev`) - Devotee role  
- **Pandit सत्यार्थी** (`scholar@vimarsh.dev`) - Scholar role

### Production Mode (Microsoft Entra ID)

**When**: Valid REACT_APP_CLIENT_ID provided
**Behavior**: Uses MSALAuthService with real Microsoft authentication
**Requirements**: 
- Valid app registration in vedid.onmicrosoft.com tenant
- Proper redirect URIs configured
- Required API permissions granted

## App Registration Requirements

### Azure AD App Registration Settings

```json
{
  "name": "Vimarsh - Vedprakash Spiritual Guidance",
  "clientId": "your-vimarsh-app-client-id",
  "tenantId": "vedid.onmicrosoft.com",
  "redirectUris": [
    "https://vimarsh.vedprakash.net",
    "https://vimarsh.vedprakash.net/auth/callback",
    "http://localhost:3000",
    "http://localhost:3000/auth/callback"
  ],
  "publicClient": true,
  "requiredScopes": [
    "openid",
    "profile", 
    "email"
  ]
}
```

### Required API Permissions

- **Microsoft Graph**:
  - `openid` (Sign users in)
  - `profile` (View users' basic profile)
  - `email` (View users' email address)

## Security Configuration

### CORS Settings (Backend)

```python
# Azure Functions CORS configuration
ALLOWED_ORIGINS = [
    "https://vimarsh.vedprakash.net",
    "http://localhost:3000",  # Development only
]
```

### Security Headers

The backend automatically adds these security headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; connect-src 'self' https://login.microsoftonline.com https://vedid.b2clogin.com; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

## Testing Configuration

### Unit Tests

Tests automatically use placeholder authentication via mocked dependencies:

```typescript
// Authentication tests run with mock MSAL
jest.mock('@azure/msal-browser');
jest.mock('./msalConfig', () => ({
  authConfig: { usePlaceholder: true }
}));
```

### Integration Tests

For end-to-end testing with real authentication:

```bash
# Test environment variables
REACT_APP_CLIENT_ID=test-app-client-id
REACT_APP_AUTHORITY=https://login.microsoftonline.com/vedid.onmicrosoft.com
E2E_TEST_USER=test@vedprakash.net
E2E_TEST_PASSWORD=TestPassword123!
```

## Troubleshooting

### Common Issues

#### 1. "MSAL authentication not yet implemented" error
**Cause**: Missing REACT_APP_CLIENT_ID in production
**Solution**: Set proper environment variables

#### 2. CORS errors in browser
**Cause**: Frontend domain not in Azure AD redirect URIs
**Solution**: Add your domain to app registration redirect URIs

#### 3. "Invalid audience" JWT error
**Cause**: Token audience doesn't match backend client ID
**Solution**: Verify ENTRA_CLIENT_ID matches frontend client ID

#### 4. Silent token refresh failures
**Cause**: User session expired or permissions changed
**Solution**: Automatic fallback to interactive authentication

### Development Debugging

Enable verbose MSAL logging:

```typescript
// In msalConfig.ts
system: {
  loggerOptions: {
    logLevel: LogLevel.Verbose, // Change from Info to Verbose
    piiLoggingEnabled: false
  }
}
```

## Deployment Checklist

### Pre-Production

- [ ] Azure AD app registration created
- [ ] Redirect URIs configured for production domain
- [ ] Environment variables set in deployment platform
- [ ] CORS settings updated for production domain
- [ ] SSL certificate configured (required for MSAL)

### Production

- [ ] Monitor authentication success rates
- [ ] Set up alerts for authentication failures
- [ ] Test SSO across Vedprakash applications
- [ ] Verify security headers in production
- [ ] Test token refresh functionality

## Monitoring

### Key Metrics

- Authentication success rate
- Token refresh failure rate
- Cross-app SSO usage
- User session duration

### Logging

All authentication events are logged with:
- User ID (when available)
- Operation type (login, logout, token refresh)
- Success/failure status
- Error details (sanitized)
- Performance metrics

### Error Tracking

Monitor these error patterns:
- MSAL initialization failures
- Token validation errors
- JWKS fetch failures
- Cross-origin request issues

---

For additional support, refer to:
- [Microsoft Entra ID Documentation](https://docs.microsoft.com/en-us/azure/active-directory/)
- [MSAL.js Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-js-initializing-client-applications)
- Apps_Auth_Requirement.md (Vedprakash domain standard)
