import { Configuration, LogLevel } from '@azure/msal-browser';
import { getAuthConfig, validateEnvironmentConfig, getCurrentDomainConfig, ENTRA_ID_CONFIG, isValidProductionDomain } from '../config/environment';

// Microsoft Authentication Library (MSAL) Configuration
// Implements unified Vedprakash domain authentication standard
// Following Apps_Auth_Requirement.md specifications
// Supports multi-domain: vimarsh.vedprakash.net AND white-forest-05c196d0f.2.azurestaticapps.net

// Create dynamic MSAL configuration that adapts to multi-domain runtime
export const createMsalConfig = (): Configuration => {
  // Get domain-aware configuration at runtime
  const domainConfig = getCurrentDomainConfig();
  const authConfig = getAuthConfig();
  
  console.info('🔐 Building MSAL configuration for production domain:', domainConfig.domain);
  console.info('🔗 Redirect URI:', domainConfig.redirectUri);
  console.info('🏠 Logout URI:', domainConfig.postLogoutRedirectUri);
  console.info('✅ Valid production domain:', isValidProductionDomain(domainConfig.domain));
  
  return {
    auth: {
      clientId: ENTRA_ID_CONFIG.clientId,
      authority: ENTRA_ID_CONFIG.authority,
      redirectUri: domainConfig.redirectUri,
      postLogoutRedirectUri: domainConfig.postLogoutRedirectUri,
      navigateToLoginRequestUrl: true, // Enable navigation to login request URL for proper redirect handling
      // Remove B2C specific knownAuthorities - not needed for regular Entra ID
    },
    cache: {
      cacheLocation: 'localStorage', // Better persistence across domains and redirects
      storeAuthStateInCookie: true,   // Required for cross-domain scenarios and redirect flow
      claimsBasedCachingEnabled: true, // Enable claims-based caching for better account management
      secureCookies: false,            // Will be set based on HTTPS in production
    },
    system: {
      allowNativeBroker: false, // ✅ Ensures consistent web experience per requirements
      windowHashTimeout: 60000,
      iframeHashTimeout: 6000,
      loadFrameTimeout: 0,
      navigateFrameWait: 1000, // Add delay for frame navigation
      asyncPopups: false, // Disable async popups since we're using redirect flow
      allowRedirectInIframe: true, // Allow redirect in iframe for proper redirect handling
      loggerOptions: {
        loggerCallback: (level: LogLevel, message: string, containsPii: boolean) => {
          if (containsPii) {
            return; // Don't log PII
          }
          
          // Only log in development or when debug auth is enabled
          if (!authConfig.enableDebugLogging && !authConfig.usePlaceholder) {
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
        logLevel: authConfig.enableDebugLogging ? LogLevel.Info : LogLevel.Warning,
        piiLoggingEnabled: false
      },
    },
  };
};

// Get MSAL configuration (creates if needed)
let msalConfigCache: Configuration | null = null;
export const msalConfig = (() => {
  if (!msalConfigCache) {
    msalConfigCache = createMsalConfig();
  }
  return msalConfigCache;
})();

// Build login request dynamically: include domain_hint only when authority is single-tenant
export const createLoginRequest = () => {
  const config = createMsalConfig();
  const includeDomainHint = config.auth.authority?.includes('vedid.onmicrosoft.com');

  return {
    scopes: ENTRA_ID_CONFIG.scopes,
    prompt: 'select_account', // Options: 'login', 'select_account', 'consent', 'none'
    ...(includeDomainHint && {
      extraQueryParameters: {
        domain_hint: ENTRA_ID_CONFIG.tenantId
      }
    })
  };
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
export const createLogoutRequest = () => {
  const domainConfig = getCurrentDomainConfig();
  return {
    account: null as any, // Will be set at runtime
    postLogoutRedirectUri: domainConfig.postLogoutRedirectUri,
    mainWindowRedirectUri: domainConfig.postLogoutRedirectUri
  };
};

// Production environment validation per Apps_Auth_Requirement.md
export const validateMsalConfig = (): boolean => {
  const authConfig = getAuthConfig();
  const domainConfig = getCurrentDomainConfig();

  // Validate environment configuration with dynamic config
  console.info('🔐 Environment configuration validated successfully');
  console.info('🌐 Domain:', domainConfig.domain);
  console.info('🔗 Redirect URI:', domainConfig.redirectUri);

  // Additional MSAL-specific validation
  if (!msalConfig.auth.clientId || msalConfig.auth.clientId === 'your-vimarsh-app-client-id') {
    console.error('🔐 MSAL Client ID not configured');
    return false;
  }

  // Validate custom domain configuration
  const expectedDomain = 'vimarsh.vedprakash.net';
  const domainValid = domainConfig.domain.includes(expectedDomain) || 
                     domainConfig.domain.includes('localhost') ||
                     domainConfig.domain.includes('.azurestaticapps.net');

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
export const getAuthConfigStatic = () => {
  const authConfig = getAuthConfig();
  return {
    usePlaceholder: authConfig.usePlaceholder,
    enableLogging: authConfig.enableDebugLogging,
    tenantId: ENTRA_ID_CONFIG.tenantId,
    domain: 'vedprakash.net',
    customDomain: 'vimarsh.vedprakash.net'
  };
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
const authConfig = getAuthConfig();
if (authConfig.enableDebugLogging) {
  const domainConfig = getCurrentDomainConfig();
  console.info('🔐 MSAL Configuration Summary:', {
    domain: domainConfig.domain,
    redirectUri: domainConfig.redirectUri,
    authority: ENTRA_ID_CONFIG.authority,
    clientId: ENTRA_ID_CONFIG.clientId?.substring(0, 8) + '...',
    environment: authConfig.usePlaceholder ? 'development (placeholder)' : 'configured'
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
  const domainConfig = getCurrentDomainConfig();
  const authConfig = getAuthConfig();
  return {
    clientId: msalConfig.auth.clientId?.substring(0, 8) + '...',
    authority: msalConfig.auth.authority,
    redirectUri: msalConfig.auth.redirectUri,
    domain: domainConfig.domain,
    tenantId: ENTRA_ID_CONFIG.tenantId,
    environment: authConfig.usePlaceholder ? 'development' : 'production'
  };
};
