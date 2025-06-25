// Microsoft Authentication Library (MSAL) Configuration
// This will be used in production with Microsoft Entra External ID

// Environment variables for MSAL configuration
export const msalConfig = {
  auth: {
    clientId: process.env.REACT_APP_CLIENT_ID || 'your-vimarsh-app-client-id',
    authority: process.env.REACT_APP_AUTHORITY || 'https://vedid.onmicrosoft.com/vedid.onmicrosoft.com',
    redirectUri: process.env.REACT_APP_REDIRECT_URI || window.location.origin + '/auth/callback',
    postLogoutRedirectUri: process.env.REACT_APP_POST_LOGOUT_REDIRECT_URI || window.location.origin,
    navigateToLoginRequestUrl: false,
  },
  cache: {
    cacheLocation: 'localStorage', // Options: 'localStorage', 'sessionStorage'
    storeAuthStateInCookie: false, // Set to true for IE11 support
  },
  system: {
    loggerOptions: {
      loggerCallback: (level: any, message: string, containsPii: boolean) => {
        if (containsPii) {
          return;
        }
        switch (level) {
          case 'error':
            console.error('MSAL Error:', message);
            break;
          case 'warning':
            console.warn('MSAL Warning:', message);
            break;
          case 'info':
            console.info('MSAL Info:', message);
            break;
          default:
            console.log('MSAL:', message);
            break;
        }
      },
    },
  },
};

// Login request configuration
export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
  prompt: 'select_account' // Options: 'login', 'select_account', 'consent', 'none'
};

// Token request for API calls
export const tokenRequest = {
  scopes: [`https://vedid.onmicrosoft.com/vimarsh-api/access_as_user`],
  account: null, // Will be set dynamically
};

// Graph API endpoint for user profile (optional)
export const graphConfig = {
  graphMeEndpoint: 'https://graph.microsoft.com/v1.0/me',
};

// Environment configuration
export const isDevelopment = process.env.NODE_ENV === 'development';
export const isProduction = process.env.NODE_ENV === 'production';

// Feature flags for authentication
export const authConfig = {
  // Use placeholder auth in development, MSAL in production
  usePlaceholder: isDevelopment && !process.env.REACT_APP_USE_MSAL,
  requireAuth: process.env.REACT_APP_REQUIRE_AUTH !== 'false',
  enableGuest: process.env.REACT_APP_ENABLE_GUEST === 'true',
};

// Spiritual user roles and permissions
export const spiritualRoles = {
  SEEKER: 'seeker',
  DEVOTEE: 'devotee',
  SCHOLAR: 'scholar',
  EXPERT: 'expert',
  ADMIN: 'admin'
} as const;

export type SpiritualRole = typeof spiritualRoles[keyof typeof spiritualRoles];

// Default user profile for new registrations
export const defaultSpiritualProfile = {
  role: spiritualRoles.SEEKER,
  preferredLanguage: 'English' as const,
  spiritualInterests: [] as string[],
  studyPreferences: {
    scripture: 'bhagavad_gita',
    studyTime: 'morning',
    difficulty: 'beginner'
  },
  privacy: {
    shareProgress: false,
    publicProfile: false,
    allowReminders: true
  }
};

// Error messages for authentication flows
export const authErrors = {
  NETWORK_ERROR: 'Unable to connect to authentication service. Please check your internet connection.',
  INVALID_CREDENTIALS: 'Invalid credentials provided. Please try again.',
  SESSION_EXPIRED: 'Your session has expired. Please sign in again.',
  UNAUTHORIZED: 'You do not have permission to access this resource.',
  SERVICE_UNAVAILABLE: 'Authentication service is temporarily unavailable. Please try again later.',
  UNKNOWN_ERROR: 'An unexpected error occurred during authentication. Please contact support if this persists.'
};

// MSAL instance will be created when needed in production
// For now, this serves as configuration documentation
export const createMsalInstance = () => {
  if (authConfig.usePlaceholder) {
    console.log('🕉️ Using placeholder authentication for development');
    return null;
  }

  // In production, this would import and create the actual MSAL instance
  console.log('🔐 Initializing Microsoft Entra External ID authentication');
  
  // TODO: Import and configure actual MSAL instance
  // import { PublicClientApplication } from '@azure/msal-browser';
  // return new PublicClientApplication(msalConfig);
  
  return null;
};
