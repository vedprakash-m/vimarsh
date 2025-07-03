import { Configuration, LogLevel } from '@azure/msal-browser';
import { AUTH_CONFIG, validateEnvironmentConfig, getCurrentDomainConfig, ENTRA_ID_CONFIG } from '../config/environment';

// Microsoft Authentication Library (MSAL) Configuration
// Implements unified Vedprakash domain authentication standard
// Following Apps_Auth_Requirement.md specifications
// Handles custom domain: vimarsh.vedprakash.net

// Validate environment configuration on load
validateEnvironmentConfig();

// Get domain-aware configuration
const domainConfig = getCurrentDomainConfig();

// Environment-aware MSAL Configuration for Vedprakash Domain
export const msalConfig: Configuration = {
  auth: {
    clientId: ENTRA_ID_CONFIG.clientId,
    authority: ENTRA_ID_CONFIG.authority,
    redirectUri: domainConfig.redirectUri,
    postLogoutRedirectUri: domainConfig.postLogoutRedirectUri,
    navigateToLoginRequestUrl: false,
    // Remove B2C specific knownAuthorities - not needed for regular Entra ID
  },
  cache: {
    cacheLocation: 'sessionStorage', // ✅ Required for SSO per Apps_Auth_Requirement.md
    storeAuthStateInCookie: true,    // ✅ Required for Safari/iOS per Apps_Auth_Requirement.md
  },
  system: {
    allowNativeBroker: false, // ✅ Ensures consistent web experience per requirements
    windowHashTimeout: 60000,
    iframeHashTimeout: 6000,
    loadFrameTimeout: 0,
    loggerOptions: {
      loggerCallback: (level: LogLevel, message: string, containsPii: boolean) => {
        if (containsPii) {
          return; // Don't log PII
        }
        
        // Only log in development or when debug auth is enabled
        if (!AUTH_CONFIG.enableDebugLogging && !AUTH_CONFIG.usePlaceholder) {
          return;
        }
        
        const prefix = `🔐 MSAL [${domainConfig.domain}]`;
        switch (level) {
          case LogLevel.Error:
            console.error(`${prefix} Error:`, message);
            break;
          case LogLevel.Warning:
            console.warn(`${prefix} Warning:`, message);
            break;
          case LogLevel.Info:
            console.info(`${prefix} Info:`, message);
            break;
          case LogLevel.Verbose:
            console.debug(`${prefix} Debug:`, message);
            break;
          default:
            console.log(`${prefix}:`, message);
            break;
        }
      },
      logLevel: AUTH_CONFIG.enableDebugLogging ? LogLevel.Info : LogLevel.Warning,
      piiLoggingEnabled: false
    },
  },
};

// Build login request dynamically: include domain_hint only when authority is single-tenant
const includeDomainHint = msalConfig.auth.authority?.includes('vedid.onmicrosoft.com');

export const loginRequest = {
  scopes: ENTRA_ID_CONFIG.scopes,
  prompt: 'select_account', // Options: 'login', 'select_account', 'consent', 'none'
  ...(includeDomainHint && {
    extraQueryParameters: {
      domain_hint: ENTRA_ID_CONFIG.tenantId
    }
  })
};

// Token request for accessing Vimarsh API
export const apiTokenRequest = {
  scopes: ENTRA_ID_CONFIG.scopes,
  account: null as any, // Will be set at runtime
};

// Silent token refresh request
export const silentRequest = {
  scopes: ENTRA_ID_CONFIG.scopes,
  account: null as any, // Will be set at runtime
  forceRefresh: false
};

// Logout request configuration
export const logoutRequest = {
  account: null as any, // Will be set at runtime
  postLogoutRedirectUri: domainConfig.postLogoutRedirectUri,
  mainWindowRedirectUri: domainConfig.postLogoutRedirectUri
};

// Production environment validation per Apps_Auth_Requirement.md
export const validateMsalConfig = (): boolean => {
  // Use the environment validation from our config
  if (!validateEnvironmentConfig()) {
    return false;
  }

  // Additional MSAL-specific validation
  if (!msalConfig.auth.clientId || msalConfig.auth.clientId === 'your-vimarsh-app-client-id') {
    console.error('🔐 MSAL Client ID not configured');
    return false;
  }

  // Validate custom domain configuration
  const expectedDomain = 'vimarsh.vedprakash.net';
  const domainValid = AUTH_CONFIG.domain.includes(expectedDomain) || AUTH_CONFIG.domain.includes('localhost');

  const authorityValid = [
    'vedid.onmicrosoft.com',
    '/common',
    '/consumers'
  ].some(part => msalConfig.auth.authority?.includes(part));

  if (domainValid && authorityValid) {
    console.info('🔐 MSAL configuration validated (multi-tenant allowed)');
    return true;
  }

  console.error('🔐 MSAL validation failed – check domain or authority');
  return false;
};

// Environment-specific configuration per Vedprakash domain standards
export const authConfig = {
  usePlaceholder: AUTH_CONFIG.usePlaceholder,
  enableLogging: AUTH_CONFIG.enableDebugLogging,
  tenantId: ENTRA_ID_CONFIG.tenantId,
  domain: 'vedprakash.net',
  customDomain: 'vimarsh.vedprakash.net'
};

// Error messages for authentication failures
export const AUTH_ERROR_MESSAGES = {
  NO_ACCOUNT: 'No user account found. Please sign in.',
  TOKEN_EXPIRED: 'Your session has expired. Please sign in again.',
  NETWORK_ERROR: 'Network error during authentication. Please try again.',
  INVALID_TOKEN: 'Invalid authentication token. Please sign in again.',
  PERMISSION_DENIED: 'You do not have permission to access this resource.',
  GENERAL_ERROR: 'Authentication error occurred. Please try again.',
  DOMAIN_ERROR: 'Invalid domain configuration. Please contact support.',
  TENANT_ERROR: 'Unable to connect to Vedprakash domain. Please try again.'
};

// Log configuration summary in development
if (AUTH_CONFIG.enableDebugLogging) {
  console.info('🔐 MSAL Configuration Summary:', {
    domain: domainConfig.domain,
    redirectUri: domainConfig.redirectUri,
    authority: ENTRA_ID_CONFIG.authority,
    clientId: ENTRA_ID_CONFIG.clientId?.substring(0, 8) + '...',
    environment: AUTH_CONFIG.usePlaceholder ? 'development (placeholder)' : 'configured'
  });
}

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

// MSAL instance helper for debugging
export const getMsalConfigSummary = () => {
  return {
    clientId: msalConfig.auth.clientId?.substring(0, 8) + '...',
    authority: msalConfig.auth.authority,
    redirectUri: msalConfig.auth.redirectUri,
    domain: domainConfig.domain,
    tenantId: ENTRA_ID_CONFIG.tenantId,
    environment: authConfig.usePlaceholder ? 'development' : 'production'
  };
};
