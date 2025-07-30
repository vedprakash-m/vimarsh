# Google Auth + Azure Functions Integration Challenges

## Authentication Flow Complexity

### Current Entra ID Flow (Simple):
```
User -> Azure Static Web Apps -> Azure Functions
     ↳ MSAL token ----------------↳ Native validation ✅
```

### Google Auth Flow (Complex):
```
User -> Google OAuth -> SPA -> Azure Functions
     ↳ Google token ----↳ Custom CORS ----↳ Custom JWT validation
                        ↳ Token conversion
                        ↳ User mapping
                        ↳ Session management
```

## Technical Challenges

### 1. CORS Configuration
```json
// Current (Entra ID) - Works out of box
{
  "globalHeaders": {
    "connect-src": "https://login.microsoftonline.com"
  }
}

// Google Auth - Requires additional configuration
{
  "globalHeaders": {
    "connect-src": "https://accounts.google.com https://login.microsoftonline.com"
  }
}
```

### 2. Azure Functions Authentication
```python
# Current (Entra ID) - Native support
@auth_required  # Built-in Azure Functions authentication
def spiritual_guidance(req):
    user = req.user  # Automatically available
    
# Google Auth - Custom implementation required
@google_auth_required  # Custom middleware needed
def spiritual_guidance(req):
    user = validate_google_token(req.headers.get('Authorization'))
```

### 3. Token Validation Complexity
```python
# Entra ID (Current) - Built-in validation
def validate_entra_token(token):
    # Azure validates automatically
    return azure.validate_jwt(token)

# Google Auth - Custom validation needed
def validate_google_token(token):
    # Custom implementation required
    google_certs = fetch_google_certificates()
    decoded_token = jwt.decode(token, google_certs, algorithms=['RS256'])
    # Additional validation logic...
    return create_user_object(decoded_token)
```

## Integration Complexity Score

| Feature | Entra ID | Google Auth |
|---------|----------|-------------|
| SPA Integration | ⭐ (Native) | ⭐⭐ (Library) |
| Azure Functions | ⭐ (Built-in) | ⭐⭐⭐⭐ (Custom) |
| CORS Setup | ⭐ (Auto) | ⭐⭐⭐ (Manual) |
| Token Validation | ⭐ (Native) | ⭐⭐⭐⭐ (Custom) |
| Multi-App SSO | ⭐ (Built-in) | ⭐⭐⭐⭐⭐ (Impossible) |
| Enterprise Features | ⭐ (Native) | ⭐⭐⭐⭐⭐ (Not available) |

## Estimated Migration Effort

### Google Auth Implementation:
- Custom authentication middleware: 8-16 hours
- CORS reconfiguration: 2-4 hours  
- Token validation system: 4-8 hours
- User mapping logic: 4-6 hours
- Testing across environments: 4-8 hours
- **Total: 22-42 hours**

### Current Entra ID Fix:
- Debug current configuration: 2-4 hours
- **Total: 2-4 hours**
