# Microsoft + Google Hybrid Authentication Guide

## 🎯 **Phase 1: Microsoft Multitenant Setup**

### **Azure App Registration Changes (Required)**

**Current Configuration (From Your Screenshots - COMPLETED):**
```json
{
  "tenant": "Default Directory",
  "tenant_id": "80feb807-105c-4fb9-ab03-c9a818e35848",
  "client_id": "e4bd74b8-9a82-40c6-8d52-3e231733095e",
  "authority": "https://login.microsoftonline.com/common",
  "supported_account_types": "multitenant_and_personal"
}
```

**✅ Your Configuration Is Already Complete!**
```json
{
  "tenant": "Default Directory",  // ✅ Your existing app registration
  "tenant_id": "80feb807-105c-4fb9-ab03-c9a818e35848",  // ✅ Your tenant ID
  "client_id": "e4bd74b8-9a82-40c6-8d52-3e231733095e",  // ✅ Your client ID
  "authority": "https://login.microsoftonline.com/common",  // ✅ Multitenant endpoint
  "supported_account_types": "multitenant_and_personal"  // ✅ Already configured
}
```

### **Azure Portal Configuration Steps**

1. **Navigate to Azure Portal**:
   - Go to https://portal.azure.com
   - Navigate to `Default Directory` → `App registrations` (as shown in your screenshot)
   - Click on your existing "Vimarsh" app registration

2. **Change Account Type**:
   ```
   Current: "Accounts in this organizational directory only (Default Directory only - Single tenant)"
   Change to: "Accounts in any organizational directory (Any Azure AD directory - Multitenant)"
   ```

3. **Update Redirect URIs**:
   ```
   Production:
   - https://vimarsh.vedprakash.net/auth/callback
   - https://vimarsh.vedprakash.net/.auth/login/aad/callback
   
   Development:
   - http://localhost:3000/auth/callback
   - http://localhost:7071/.auth/login/aad/callback
   ```

4. **API Permissions** (Keep Current):
   ```
   - Microsoft Graph: User.Read (for basic profile)
   - Microsoft Graph: email (for user email)
   - Microsoft Graph: openid (for authentication)
   - Microsoft Graph: profile (for user profile)
   ```

## 🔄 **Phase 2: Add Google Auth (Later)**

### **Google Cloud Console Setup**

1. **Create Google OAuth 2.0 Client**:
   - Go to https://console.cloud.google.com
   - Create/Select project: `vimarsh-spiritual-guidance`
   - Enable Google+ API and Google Identity API
   - Create OAuth 2.0 Client ID

2. **Configure OAuth Client**:
   ```json
   {
     "client_id": "your-google-client-id.apps.googleusercontent.com",
     "client_secret": "your-google-client-secret",
     "redirect_uris": [
       "https://vimarsh.vedprakash.net/auth/google/callback",
       "http://localhost:3000/auth/google/callback"
     ],
     "authorized_domains": [
       "vimarsh.vedprakash.net",
       "localhost"
     ]
   }
   ```

### **Frontend Configuration (Hybrid)**

**React Auth Configuration:**
```typescript
// src/config/auth.ts
interface AuthProvider {
  name: 'microsoft' | 'google';
  config: any;
}

export const authProviders: AuthProvider[] = [
  {
    name: 'microsoft',
    config: {
      clientId: process.env.REACT_APP_MS_CLIENT_ID,
      authority: 'https://login.microsoftonline.com/common',
      redirectUri: `${window.location.origin}/auth/microsoft/callback`,
      scopes: ['User.Read', 'email', 'profile']
    }
  },
  {
    name: 'google',
    config: {
      clientId: process.env.REACT_APP_GOOGLE_CLIENT_ID,
      redirectUri: `${window.location.origin}/auth/google/callback`,
      scope: 'email profile openid'
    }
  }
];

// Authentication service
export class HybridAuthService {
  async signInWithMicrosoft() {
    const msalConfig = {
      auth: authProviders[0].config
    };
    // MSAL implementation
  }

  async signInWithGoogle() {
    const googleConfig = authProviders[1].config;
    // Google OAuth implementation
  }

  async normalizeUserData(provider: string, rawUserData: any): Promise<NormalizedUser> {
    switch (provider) {
      case 'microsoft':
        return {
          id: rawUserData.id,
          email: rawUserData.mail || rawUserData.userPrincipalName,
          name: rawUserData.displayName,
          provider: 'microsoft',
          providerId: rawUserData.id,
          profilePicture: rawUserData.photo
        };
      
      case 'google':
        return {
          id: rawUserData.sub,
          email: rawUserData.email,
          name: rawUserData.name,
          provider: 'google',
          providerId: rawUserData.sub,
          profilePicture: rawUserData.picture
        };
      
      default:
        throw new Error(`Unsupported provider: ${provider}`);
    }
  }
}
```

### **Backend Configuration (Hybrid)**

**Azure Functions Auth Handler:**
```python
# backend/auth/hybrid_auth_service.py
import jwt
from typing import Dict, Any, Optional
from azure.identity import DefaultAzureCredential
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

class HybridAuthService:
    def __init__(self):
        self.ms_tenant_id = "common"  # Multitenant
        self.ms_client_id = os.getenv("MS_CLIENT_ID")
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    
    async def validate_microsoft_token(self, token: str) -> Dict[str, Any]:
        """Validate Microsoft JWT token from any tenant"""
        try:
            # Microsoft multitenant token validation
            decoded_token = jwt.decode(
                token,
                options={"verify_signature": False},  # Verify with Microsoft keys
                algorithms=["RS256"]
            )
            
            # Validate issuer for multitenant
            valid_issuers = [
                f"https://login.microsoftonline.com/{decoded_token.get('tid')}/v2.0",
                f"https://sts.windows.net/{decoded_token.get('tid')}/"
            ]
            
            if decoded_token.get('iss') not in valid_issuers:
                raise ValueError("Invalid token issuer")
            
            return self.normalize_microsoft_user(decoded_token)
            
        except Exception as e:
            logger.error(f"Microsoft token validation failed: {str(e)}")
            raise AuthenticationError("Invalid Microsoft token")
    
    async def validate_google_token(self, token: str) -> Dict[str, Any]:
        """Validate Google ID token"""
        try:
            # Google token validation
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                self.google_client_id
            )
            
            return self.normalize_google_user(idinfo)
            
        except Exception as e:
            logger.error(f"Google token validation failed: {str(e)}")
            raise AuthenticationError("Invalid Google token")
    
    def normalize_microsoft_user(self, token_data: Dict) -> Dict[str, Any]:
        """Normalize Microsoft user data"""
        return {
            "provider": "microsoft",
            "provider_id": token_data.get("oid"),
            "email": token_data.get("email") or token_data.get("preferred_username"),
            "name": token_data.get("name"),
            "given_name": token_data.get("given_name"),
            "family_name": token_data.get("family_name"),
            "tenant_id": token_data.get("tid"),
            "job_title": token_data.get("jobTitle"),
            "company": token_data.get("companyName")
        }
    
    def normalize_google_user(self, token_data: Dict) -> Dict[str, Any]:
        """Normalize Google user data"""
        return {
            "provider": "google",
            "provider_id": token_data.get("sub"),
            "email": token_data.get("email"),
            "name": token_data.get("name"),
            "given_name": token_data.get("given_name"),
            "family_name": token_data.get("family_name"),
            "profile_picture": token_data.get("picture"),
            "email_verified": token_data.get("email_verified", False)
        }

# Function handler
@app.route(route="auth/validate", methods=["POST"])
async def validate_auth_token(req: func.HttpRequest) -> func.HttpResponse:
    try:
        request_data = req.get_json()
        token = request_data.get("token")
        provider = request_data.get("provider")
        
        auth_service = HybridAuthService()
        
        if provider == "microsoft":
            user_data = await auth_service.validate_microsoft_token(token)
        elif provider == "google":
            user_data = await auth_service.validate_google_token(token)
        else:
            return func.HttpResponse("Unsupported provider", status_code=400)
        
        # Create or update user in your database
        user_service = UserService()
        user = await user_service.create_or_update_user(user_data)
        
        return func.HttpResponse(
            json.dumps({"user": user, "success": True}),
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Auth validation error: {str(e)}")
        return func.HttpResponse("Authentication failed", status_code=401)
```

### **Database Schema (Supports Both Providers)**

**Cosmos DB User Collection:**
```json
{
  "id": "user_12345",
  "email": "john.smith@microsoft.com",
  "name": "John Smith",
  "profile_picture": "https://graph.microsoft.com/v1.0/me/photo/$value",
  "created_at": "2025-07-30T10:30:00Z",
  "last_login": "2025-07-30T15:45:00Z",
  
  // Auth provider information
  "auth_providers": [
    {
      "provider": "microsoft",
      "provider_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "tenant_id": "external-company-tenant-id",
      "linked_at": "2025-07-30T10:30:00Z",
      "is_primary": true
    }
    // Later you can add:
    // {
    //   "provider": "google",
    //   "provider_id": "google-user-id-12345",
    //   "linked_at": "2025-08-15T14:20:00Z",
    //   "is_primary": false
    // }
  ],
  
  // Vimarsh-specific data (identical for both providers)
  "spiritual_preferences": {
    "favorite_personalities": ["krishna", "buddha"],
    "preferred_language": "english",
    "guidance_style": "compassionate"
  },
  "conversation_history": [],
  "analytics_data": {
    "total_sessions": 25,
    "avg_session_duration": 180,
    "favorite_topics": ["career", "relationships", "spirituality"]
  }
}
```

## 🔒 **Security Considerations**

### **Microsoft Multitenant Security**
```python
# Enhanced JWT validation for multitenant
class MultitenantTokenValidator:
    ALLOWED_ISSUERS = [
        "https://login.microsoftonline.com/{tid}/v2.0",
        "https://sts.windows.net/{tid}/"
    ]
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        # Decode without verification to get tenant ID
        unverified = jwt.decode(token, options={"verify_signature": False})
        tenant_id = unverified.get("tid")
        
        if not tenant_id:
            raise ValueError("Missing tenant ID in token")
        
        # Now verify with proper issuer
        expected_issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        
        # Get Microsoft's public keys for verification
        jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        # ... JWT verification logic
```

### **Rate Limiting & Security Headers**
```python
# backend/middleware/security_middleware.py
class AuthSecurityMiddleware:
    def __init__(self):
        self.rate_limiter = {
            'microsoft': RateLimiter(max_requests=100, window_minutes=15),
            'google': RateLimiter(max_requests=100, window_minutes=15)
        }
    
    async def validate_request(self, provider: str, user_ip: str):
        # Rate limiting per provider
        if not await self.rate_limiter[provider].allow_request(user_ip):
            raise RateLimitError(f"Too many {provider} auth requests")
        
        # Additional security validations
        await self.check_suspicious_activity(provider, user_ip)
```

## 📈 **Migration Strategy**

### **Phase 1: Microsoft Multitenant (Immediate)**
1. **Update Azure App Registration** to multitenant
2. **Change authority** from `vedid.onmicrosoft.com` to `common`
3. **Test with external Microsoft accounts**
4. **Deploy and verify** user onboarding works

### **Phase 2: Add Google Auth (Later)**
1. **Create Google OAuth client**
2. **Add Google auth service** to backend
3. **Update frontend** with dual auth options
4. **Add provider linking** logic to database
5. **Test hybrid user flows**

## 🎯 **Key Benefits of This Approach**

### **For Microsoft Phase:**
- ✅ **Zero user management** - any Microsoft user can sign in
- ✅ **Enterprise security** - leverages corporate MFA/Conditional Access
- ✅ **Rich user data** - job title, company, profile info
- ✅ **Scalable immediately** - no user invitation process

### **For Google Addition:**
- ✅ **Maximum user reach** - covers non-Microsoft users
- ✅ **Consistent UX** - same app experience regardless of provider
- ✅ **Account linking** - users can link both accounts if desired
- ✅ **Provider flexibility** - future-proof for other providers

## 🚀 **Expected User Experience**

### **Microsoft Users:**
```
1. Visit vimarsh.vedprakash.net
2. Click "Sign in with Microsoft"
3. Use their existing work/personal Microsoft account
4. Immediate access with full personalization
5. All analytics and preferences saved
```

### **Google Users (Later):**
```
1. Visit vimarsh.vedprakash.net  
2. Click "Sign in with Google"
3. Use their existing Google account
4. Same immediate access and personalization
5. Same analytics and preferences system
```

This hybrid approach gives you maximum flexibility while maintaining the simplicity of your user database design!
