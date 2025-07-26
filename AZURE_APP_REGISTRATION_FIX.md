# 🔧 Azure App Registration Configuration Fix

## Issue
**Error**: "You can't sign in here with a personal account. Use your work or school account instead."

**Root Cause**: The Azure App Registration is configured to only allow organizational accounts from a specific tenant, but Vimarsh needs to support both personal Microsoft accounts and work/school accounts.

## ✅ Code Changes Made

### 1. Updated Environment Configuration
Changed from single-tenant to multi-tenant configuration:

**Before**:
```bash
REACT_APP_TENANT_ID=vedid.onmicrosoft.com
REACT_APP_AUTHORITY=https://login.microsoftonline.com/vedid.onmicrosoft.com
```

**After**:
```bash
REACT_APP_TENANT_ID=common
REACT_APP_AUTHORITY=https://login.microsoftonline.com/common
```

### 2. Updated Scopes
Changed from custom API scopes to standard Microsoft Graph scopes:
```typescript
scopes: ['openid', 'profile', 'email', 'User.Read']
```

## 🔧 Azure Portal Changes Required

### Step 1: Update App Registration - Supported Account Types

1. **Go to Azure Portal** → **Entra ID** → **App registrations**
2. **Find your Vimarsh app registration**
3. **Go to Authentication** tab
4. **Under "Supported account types"**, change from:
   - ❌ `Accounts in this organizational directory only (Single tenant)`
   
   **To**:
   - ✅ `Accounts in any organizational directory and personal Microsoft accounts (Multitenant and personal accounts)`

### Step 2: Update Redirect URIs (if needed)

Ensure these redirect URIs are configured:
```
https://vimarsh.vedprakash.net/auth/callback
https://white-forest-05c196d0f.2.azurestaticapps.net/auth/callback
```

### Step 3: Update API Permissions

1. **Go to API permissions** tab
2. **Remove any custom API permissions** (if present)
3. **Ensure these Microsoft Graph permissions are granted**:
   - ✅ `openid` (Sign users in)
   - ✅ `profile` (View users' basic profile)
   - ✅ `email` (View users' email address)
   - ✅ `User.Read` (Sign in and read user profile)

### Step 4: Grant Admin Consent (if required)

If you see any permissions requiring admin consent:
1. **Click "Grant admin consent for [Your Organization]"**
2. **Confirm the consent**

## 🧪 Testing After Changes

### Expected Behavior:
1. **Visit**: https://white-forest-05c196d0f.2.azurestaticapps.net
2. **Click**: "Begin Your Journey"
3. **Expected**: Microsoft login page with options for:
   - ✅ **Personal Microsoft accounts** (outlook.com, hotmail.com, live.com)
   - ✅ **Work or school accounts** (any organization)
4. **Expected**: Successful authentication and redirect to spiritual interface

### Signs of Success:
- Login page shows both personal and work account options
- No "You can't sign in here with a personal account" error
- Successful authentication with any Microsoft account type

## 📋 Alternative: Create New App Registration

If updating the existing registration is problematic, create a new one:

### New App Registration Settings:
```
Name: Vimarsh - Multi-Tenant Auth
Supported account types: Accounts in any organizational directory and personal Microsoft accounts
Redirect URI: https://vimarsh.vedprakash.net/auth/callback
```

### After Creation:
1. **Copy the new Client ID**
2. **Update `.env.production`**:
   ```bash
   REACT_APP_CLIENT_ID=new-client-id-here
   ```
3. **Rebuild and redeploy**

## 🔄 Deployment Process

After making Azure Portal changes:

1. **Rebuild the frontend** (if Client ID changed):
   ```bash
   npm run build
   ```

2. **Redeploy** (if needed):
   ```bash
   swa deploy build --env production --resource-group vimarsh-compute-rg --app-name vimarsh-frontend
   ```

## 🎯 Key Benefits of Multi-Tenant Configuration

### ✅ **User Experience**:
- Users can sign in with any Microsoft account
- No need to create organizational accounts
- Supports personal gmail users with Microsoft accounts

### ✅ **Compliance**:
- Still follows Vedprakash domain authentication standards
- Uses Microsoft Entra ID as the identity provider
- Maintains single sign-on capabilities

### ✅ **Flexibility**:
- Supports both individual users and organizations
- Future-proof for enterprise customers
- Easier user onboarding

## 🚨 Important Notes

1. **The code changes are already deployed** - only Azure Portal configuration is needed
2. **Multi-tenant apps require verification** for certain permissions in production
3. **Test thoroughly** with both personal and work accounts
4. **Monitor authentication logs** for any issues

## 📞 Next Steps

1. **Make the Azure Portal changes** described above
2. **Test authentication** with both personal and work accounts  
3. **Verify** that the "Begin Your Journey" button works correctly
4. **Report back** if you encounter any other authentication issues

The authentication should work immediately after updating the App Registration settings in Azure Portal! 🔐✅
