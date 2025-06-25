# Vimarsh Authentication System

## Overview

The Vimarsh authentication system is designed to seamlessly switch between placeholder authentication for local development and Microsoft Entra External ID for production deployment.

## Architecture

### Development Mode (Placeholder Authentication)
- **File**: `src/auth/authService.ts` - PlaceholderAuthService
- **Storage**: localStorage for session persistence
- **Users**: Pre-configured mock users with different spiritual roles
- **Session**: 24-hour expiration for development convenience

### Production Mode (Microsoft Entra External ID)
- **File**: `src/auth/authService.ts` - MSALAuthService (TODO)
- **Provider**: Microsoft Entra External ID (vedid.onmicrosoft.com)
- **Configuration**: `src/auth/msalConfig.ts`
- **Security**: JWT token validation with Azure

## Configuration

### Environment Variables

```env
# Authentication Mode
REACT_APP_USE_MSAL=false          # true for production MSAL
REACT_APP_REQUIRE_AUTH=true       # false to allow guest access
REACT_APP_ENABLE_GUEST=false      # true to enable guest mode

# Microsoft Entra External ID
REACT_APP_CLIENT_ID=your-client-id
REACT_APP_AUTHORITY=https://vedid.onmicrosoft.com/vedid.onmicrosoft.com
REACT_APP_REDIRECT_URI=http://localhost:3000/auth/callback
REACT_APP_POST_LOGOUT_REDIRECT_URI=http://localhost:3000
```

### Authentication Service Selection

The system automatically selects the appropriate authentication service based on environment configuration:

```typescript
import { authService } from '../auth/authService';

// Automatically uses PlaceholderAuthService or MSALAuthService
const user = await authService.login();
```

## Mock Users (Development)

The system includes three pre-configured spiritual user personas for testing:

### 1. Arjuna Dev (Seeker) 🏹
- **Role**: Spiritual Seeker
- **Language**: English
- **Interests**: Bhagavad Gita, Dharma, Self-realization, Karma Yoga
- **Profile**: New to spiritual practice, asking foundational questions

### 2. Meera भक्त (Devotee) 🎶
- **Role**: Devotee
- **Language**: Hindi
- **Interests**: Krishna Bhakti, Devotional Songs, Temple Worship, Raas Leela
- **Profile**: Devoted practitioner focused on bhakti (devotional) path

### 3. Pandit सत्यार्थी (Scholar) 📚
- **Role**: Scholar
- **Language**: English
- **Interests**: Vedanta, Sanskrit Studies, Philosophical Inquiry, Upanishads
- **Profile**: Advanced practitioner with deep scriptural knowledge

## Usage

### React Components

#### Authentication Context
```typescript
import { useAuth } from '../components/AuthenticationWrapper';

const MyComponent = () => {
  const { isAuthenticated, user, login, logout, isLoading, error } = useAuth();
  
  if (!isAuthenticated) {
    return <LoginPrompt />;
  }
  
  return <AuthenticatedContent user={user} />;
};
```

#### Quick Development Login
```typescript
// Login as specific user type
await login('seeker');   // Arjuna Dev
await login('devotee');  // Meera भक्त
await login('scholar');  // Pandit सत्यार्थी
await login();           // Random user
```

### API Authentication

```typescript
import { getAuthHeaders } from '../auth/authService';

const response = await fetch('/api/spiritual-guidance', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    ...(await getAuthHeaders())
  },
  body: JSON.stringify(request)
});
```

## Development Quick Start

1. **Start Development Server**:
   ```bash
   npm start
   ```

2. **Login Options**:
   - Click "Sign In" for random user
   - Use emoji buttons (🏹🎶📚) for specific user types
   - Authentication state persists across browser refreshes

3. **Test Different Personas**:
   - **Seeker**: Test beginner-level spiritual questions
   - **Devotee**: Test Hindi language and devotional content
   - **Scholar**: Test advanced philosophical discussions

## Production Deployment

### Prerequisites
1. Azure subscription with Microsoft Entra External ID tenant
2. App registration in vedid.onmicrosoft.com tenant
3. Redirect URLs configured for production domain

### Configuration Steps

1. **Update Environment Variables**:
   ```env
   REACT_APP_USE_MSAL=true
   REACT_APP_CLIENT_ID=your-production-client-id
   REACT_APP_AUTHORITY=https://vedid.onmicrosoft.com/vedid.onmicrosoft.com
   REACT_APP_REDIRECT_URI=https://vimarsh.azurestaticapps.net/auth/callback
   ```

2. **Implement MSAL Service** (TODO):
   - Install `@azure/msal-browser` package
   - Complete MSALAuthService implementation
   - Add token refresh logic
   - Implement logout handling

### Security Considerations

- **Token Storage**: Tokens stored in localStorage (consider httpOnly cookies for production)
- **Session Management**: Configurable session timeout
- **Error Handling**: Graceful degradation for auth failures
- **Privacy**: User data only stored locally during development

## Files Structure

```
src/
├── auth/
│   ├── authService.ts          # Main auth service abstraction
│   ├── msalConfig.ts           # MSAL configuration
│   └── README.md               # This file
├── components/
│   ├── AuthenticationWrapper.tsx   # Auth context provider
│   └── LoginButton.tsx             # Login/logout UI component
└── hooks/
    └── useAuth.ts              # Auth hook (exported from wrapper)
```

## Spiritual Context

The authentication system respects the spiritual nature of Vimarsh:

- **Greeting**: "Namaste" instead of generic greetings
- **Language**: Culturally appropriate terminology
- **Privacy**: Respectful handling of spiritual journey data
- **Accessibility**: WCAG 2.1 AA compliance for inclusive access

## Future Enhancements

1. **Social Login**: Google, Facebook integration
2. **Spiritual Profile**: Extended user preferences
3. **Expert Access**: Special authentication for spiritual advisors
4. **Offline Mode**: Cached authentication for PWA
5. **Multi-Factor**: Enhanced security for sensitive spiritual data

## Support

For authentication issues:
1. Check browser console for error messages
2. Verify environment configuration
3. Test with different user personas
4. Review network requests in browser dev tools

---

*"सत्यमेव जयते" - Truth alone triumphs*
