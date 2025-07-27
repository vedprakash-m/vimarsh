# 🔐 Vimarsh Frontend Environment Setup

## Custom Domain Configuration for `vimarsh.vedprakash.net`

This guide configures the Vimarsh frontend for proper Microsoft Entra ID authentication with the custom domain `vimarsh.vedprakash.net`.

---

## 📋 Required Environment Variables

### Development Environment (`.env.development`)

Create a `.env.development` file in the `frontend/` directory:

```bash
# Vimarsh Frontend - Development Environment Configuration
# Microsoft Entra ID Authentication for Vedprakash Domain
# Used for local development (npm start)

# Entra ID Configuration - Vedprakash Domain
REACT_APP_CLIENT_ID=your-vimarsh-app-client-id
REACT_APP_AUTHORITY=https://login.microsoftonline.com/vedid.onmicrosoft.com
REACT_APP_TENANT_ID=vedid.onmicrosoft.com

# Development URLs
REACT_APP_REDIRECT_URI=http://localhost:3000/auth/callback
REACT_APP_POST_LOGOUT_REDIRECT_URI=http://localhost:3000

# Development Settings
REACT_APP_ENVIRONMENT=development
REACT_APP_DEBUG_AUTH=true

# API Configuration (will be configured later)
REACT_APP_API_BASE_URL=http://localhost:7071/api
REACT_APP_API_SCOPES=openid,profile,email

# Feature Flags for Development
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_ENABLE_PWA=true
REACT_APP_ENABLE_VOICE=true
```

### Production Environment (`.env.production`)

Create a `.env.production` file in the `frontend/` directory:

```bash
# Vimarsh Frontend - Production Environment Configuration
# Microsoft Entra ID Authentication for Vedprakash Domain
# Used for production deployment (Static Web App)

# Entra ID Configuration - Vedprakash Domain
REACT_APP_CLIENT_ID=your-vimarsh-app-client-id
REACT_APP_AUTHORITY=https://login.microsoftonline.com/vedid.onmicrosoft.com
REACT_APP_TENANT_ID=vedid.onmicrosoft.com

# Production URLs - Custom Domain
REACT_APP_REDIRECT_URI=https://vimarsh.vedprakash.net/auth/callback
REACT_APP_POST_LOGOUT_REDIRECT_URI=https://vimarsh.vedprakash.net

# Production Settings
REACT_APP_ENVIRONMENT=production
REACT_APP_DEBUG_AUTH=false

# API Configuration
REACT_APP_API_BASE_URL=https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net/api
REACT_APP_API_SCOPES=openid,profile,email

# Feature Flags for Production
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_PWA=true
REACT_APP_ENABLE_VOICE=true
```

---

## 🏗️ Azure App Registration Setup

### Required Redirect URIs

Configure these redirect URIs in your Azure App Registration:

**Development:**
- `http://localhost:3000/auth/callback`

**Production:**
- `https://vimarsh.vedprakash.net/auth/callback`

### App Registration Configuration

```json
{
  "name": "Vimarsh - Vedprakash Domain",
  "clientId": "your-vimarsh-app-client-id",
  "tenantId": "vedid.onmicrosoft.com",
  "redirectUris": [
    "http://localhost:3000/auth/callback",
    "https://vimarsh.vedprakash.net/auth/callback"
  ],
  "postLogoutRedirectUris": [
    "http://localhost:3000",
    "https://vimarsh.vedprakash.net"
  ],
  "scopes": [
    "openid",
    "profile", 
    "email"
  ],
  "tokenConfiguration": {
    "accessTokenAcceptedVersion": 2,
    "optionalClaims": {
      "accessToken": [
        {"name": "given_name"},
        {"name": "family_name"},
        {"name": "email"}
      ]
    }
  }
}
```

---

## 🚀 Static Web App Configuration

### Application Settings

Configure these in your Azure Static Web App:

```bash
REACT_APP_CLIENT_ID=your-vimarsh-app-client-id
REACT_APP_AUTHORITY=https://login.microsoftonline.com/vedid.onmicrosoft.com
REACT_APP_TENANT_ID=vedid.onmicrosoft.com
REACT_APP_REDIRECT_URI=https://vimarsh.vedprakash.net/auth/callback
REACT_APP_POST_LOGOUT_REDIRECT_URI=https://vimarsh.vedprakash.net
REACT_APP_ENVIRONMENT=production
REACT_APP_API_BASE_URL=https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net/api
```

### Custom Domain Configuration

1. **Add Custom Domain:** `vimarsh.vedprakash.net`
2. **SSL Certificate:** Auto-managed by Azure
3. **DNS Configuration:** CNAME record pointing to your Static Web App

---

## 🧪 Testing the Configuration

### Development Testing

```bash
# Start development server
cd frontend
npm start

# Should open: http://localhost:3000
# Authentication should redirect to: https://login.microsoftonline.com/vedid.onmicrosoft.com
# Callback should return to: http://localhost:3000/auth/callback
```

### Production Testing

```bash
# Access production site
# URL: https://vimarsh.vedprakash.net
# Authentication should redirect to: https://login.microsoftonline.com/vedid.onmicrosoft.com
# Callback should return to: https://vimarsh.vedprakash.net/auth/callback
```

---

## 🔍 Verification Checklist

### Environment Configuration ✅
- [ ] `.env.development` file exists with safe development defaults
- [ ] `.env.production` file exists as build template (no secrets)
- [ ] `.env.local` created for personal overrides (optional)
- [ ] Production secrets configured in Azure Key Vault
- [ ] `REACT_APP_CLIENT_ID` configured with actual Azure App Registration ID
- [ ] All redirect URIs point to correct domains

### Azure App Registration ✅
- [ ] App registered in `vedid.onmicrosoft.com` tenant
- [ ] Both development and production redirect URIs configured
- [ ] Optional claims configured for user information
- [ ] Client ID copied to environment variables

### Domain Configuration ✅
- [ ] Custom domain `vimarsh.vedprakash.net` attached to Static Web App
- [ ] DNS CNAME record configured
- [ ] SSL certificate auto-generated and active
- [ ] All URLs in configuration use the custom domain

### Authentication Flow ✅
- [ ] Sign-in redirects to correct Entra ID tenant
- [ ] After authentication, returns to correct callback URL
- [ ] User can access protected routes in `/guidance`
- [ ] Sign-out redirects to correct landing page
- [ ] SSO works across `.vedprakash.net` domain

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** Authentication fails with "AADB2C90006" error
**Solution:** Ensure you're using regular Entra ID, not B2C. Authority should be `login.microsoftonline.com/vedid.onmicrosoft.com`

**Issue:** Redirect URI mismatch
**Solution:** Verify redirect URIs in Azure App Registration exactly match environment variables

**Issue:** Custom domain not working
**Solution:** Ensure CNAME record is configured and SSL certificate is active

**Issue:** Cross-domain authentication issues
**Solution:** Verify `storeAuthStateInCookie: true` in MSAL configuration

### Debug Mode

Enable debug logging in development:

```bash
REACT_APP_DEBUG_AUTH=true
```

This will show detailed MSAL logs in browser console.

---

## 📚 References

- [Apps_Auth_Requirement.md](../docs/Apps_Auth_Requirement.md) - Vedprakash domain authentication standards
- [Microsoft MSAL.js Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-js-initializing-client-applications)
- [Azure Static Web Apps Custom Domains](https://docs.microsoft.com/en-us/azure/static-web-apps/custom-domain)

---

## 🆘 Support

If you encounter issues:

1. Check browser console for detailed error messages
2. Verify all environment variables are correctly set
3. Ensure Azure App Registration configuration matches
4. Test authentication flow in incognito mode
5. Contact development team with specific error details 