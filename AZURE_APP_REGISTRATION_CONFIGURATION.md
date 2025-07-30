# Azure App Registration Configuration Checklist

## 🔧 **CRITICAL: Configure Multi-Tenant Support**

### Your App Details:
- **App Name**: Vimarsh
- **Client ID**: `52747449-829f-4fbe-bb5e-b4c54c9b1fbe`
- **Tenant**: vedid.onmicrosoft.com

### ⚠️ **IMMEDIATE ACTION REQUIRED**

1. **Go to Azure Portal** → **App Registrations** → **All applications**
2. **Find your "Vimarsh" app** (Client ID: `52747449-829f-4fbe-bb5e-b4c54c9b1fbe`)
3. **Click on the app** to open its configuration

### 🔄 **Change Account Types (CRITICAL)**
4. **Click "Authentication"** in the left sidebar
5. **Under "Supported account types"** you'll see:
   - ❌ Current: "Accounts in this organizational directory only (vedid.onmicrosoft.com only - Single tenant)"
   
6. **Change to**:
   - ✅ Select: **"Accounts in any organizational directory (Any Azure AD directory - Multitenant)"**

### 🔗 **Verify Redirect URIs**
7. **In the same Authentication page**, verify these Redirect URIs are present:
   - ✅ `https://vimarsh.vedprakash.net/auth/callback` (Production)
   - ✅ `https://localhost:3000/auth/callback` (Development)
   - ✅ `http://localhost:3000/auth/callback` (Development HTTP)

8. **If missing**, click **"Add URI"** and add them

### 💾 **Save Changes**
9. **Click "Save"** at the top of the Authentication page

### ✅ **Verification**
After saving, you should see:
- **Supported account types**: "Multitenant"
- **Redirect URIs**: All three URIs listed above
- **Status**: No error messages

## 🎯 **Why This Change Is Critical**

### Before (Single Tenant):
- ❌ Only users from `vedid.onmicrosoft.com` can authenticate
- ❌ Requires tenant management for each organization
- ❌ Limits adoption to your specific tenant

### After (Multi-Tenant):
- ✅ **Any Microsoft user** from **any organization** can authenticate
- ✅ Users from `microsoft.com`, `contoso.com`, `outlook.com`, etc. can sign in
- ✅ No tenant management overhead
- ✅ Enterprise-ready for global adoption

## 🧪 **Testing After Configuration**

Once you make this change, you can test with:
1. **Your vedid.onmicrosoft.com account** (should still work)
2. **Personal Microsoft account** (user@outlook.com, user@hotmail.com)
3. **Other organization accounts** (user@microsoft.com, user@company.com)

## 🚨 **Security Note**
Multi-tenant apps are slightly more complex to secure, but our implementation handles this properly by:
- Validating tokens against the actual tenant from the JWT claims
- Using the common endpoint for JWKS discovery
- Properly validating the issuer for each tenant

This change is **essential** for the Vimarsh platform to achieve its goal of providing spiritual guidance to **any Microsoft user** worldwide without administrative overhead.
