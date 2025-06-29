import { Configuration, LogLevel } from '@azure/msal-browser';

// Microsoft Authentication Library (MSAL) Configuration
// Implements unified Vedprakash domain authentication standard

// ✅ Corrected MSAL Configuration
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.REACT_APP_CLIENT_ID || 'your-vimarsh-app-client-id',
    authority: process.env.REACT_APP_AUTHORITY || 'https://login.microsoftonline.com/vedid.onmicrosoft.com', // ✅ Fixed authority
    redirectUri: process.env.REACT_APP_REDIRECT_URI || `${window.location.origin}/auth/callback`,
    postLogoutRedirectUri: process.env.REACT_APP_POST_LOGOUT_REDIRECT_URI || window.location.origin,
    navigateToLoginRequestUrl: false,
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false, // Set to true for IE11 support
  },
  system: {
    allowNativeBroker: false, // Disable native broker for web
    windowHashTimeout: 60000,
    iframeHashTimeout: 6000,
    loadFrameTimeout: 0,
    loggerOptions: {
      loggerCallback: (level: LogLevel, message: string, containsPii: boolean) => {
        if (containsPii) {
          return; // Don't log PII
        }
        switch (level) {
          case LogLevel.Error:
            console.error('🔐 MSAL Error:', message);
            break;
          case LogLevel.Warning:
            console.warn('🔐 MSAL Warning:', message);
            break;
          case LogLevel.Info:
            console.info('🔐 MSAL Info:', message);
            break;
          case LogLevel.Verbose:
            console.debug('🔐 MSAL Debug:', message);
            break;
          default:
            console.log('🔐 MSAL:', message);
            break;
        }
      },
      logLevel: LogLevel.Info,
      piiLoggingEnabled: false
    },
  },
};

// Login request configuration for initial authentication
export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
  prompt: 'select_account', // Options: 'login', 'select_account', 'consent', 'none'
  extraQueryParameters: {
    domain_hint: 'vedid.onmicrosoft.com' // Help with tenant routing
  }
};

// Token request for accessing Vimarsh API
export const apiTokenRequest = {
  scopes: ['openid', 'profile', 'email'], // Basic scopes for now
  account: null as any, // Will be set at runtime
};

// Silent token refresh request
export const silentRequest = {
  scopes: ['openid', 'profile', 'email'],
  account: null as any, // Will be set at runtime
  forceRefresh: false
};

// Logout request configuration
export const logoutRequest = {
  account: null as any, // Will be set at runtime
  postLogoutRedirectUri: window.location.origin,
  mainWindowRedirectUri: window.location.origin
};

// Production environment validation
export const validateMsalConfig = (): boolean => {
  const requiredEnvVars = [
    'REACT_APP_CLIENT_ID',
    'REACT_APP_AUTHORITY'
  ];

  const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
  
  if (missingVars.length > 0) {
    console.error('🔐 Missing required environment variables:', missingVars);
    return false;
  }

  // Validate authority format
  const authority = process.env.REACT_APP_AUTHORITY;
  if (authority && !authority.includes('login.microsoftonline.com')) {
    console.error('🔐 Invalid authority format. Should use login.microsoftonline.com');
    return false;
  }

  console.info('🔐 MSAL configuration validated successfully');
  return true;
};

// Environment-specific configuration
export const authConfig = {
  usePlaceholder: process.env.NODE_ENV === 'development' && !validateMsalConfig(),
  enableLogging: process.env.NODE_ENV === 'development',
  tenantId: 'vedid.onmicrosoft.com',
  domain: 'vedprakash.net'
};

// Error messages for authentication failures
export const AUTH_ERROR_MESSAGES = {
  NO_ACCOUNT: 'No user account found. Please sign in.',
  TOKEN_EXPIRED: 'Your session has expired. Please sign in again.',
  NETWORK_ERROR: 'Network error during authentication. Please try again.',
  INVALID_TOKEN: 'Invalid authentication token. Please sign in again.',
  PERMISSION_DENIED: 'You do not have permission to access this resource.',
  GENERAL_ERROR: 'Authentication error occurred. Please try again.'
};

export default msalConfig;

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
