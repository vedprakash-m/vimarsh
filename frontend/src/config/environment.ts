/**
 * Environment Configuration for Vimarsh Frontend
 * Handles custom domain vimarsh.vedprakash.net
 * Provides proper Entra ID settings per Apps_Auth_Requirement.md
 */

// Environment detection
export const isProduction = process.env.NODE_ENV === 'production';
export const isDevelopment = process.env.NODE_ENV === 'development';

// Custom domain configuration for vimarsh.vedprakash.net
export const DOMAIN_CONFIG = {
  production: {
    domain: 'https://vimarsh.vedprakash.net',
    redirectUri: 'https://vimarsh.vedprakash.net/auth/callback',
    postLogoutRedirectUri: 'https://vimarsh.vedprakash.net',
  },
  development: {
    domain: 'http://localhost:3000',
    redirectUri: 'http://localhost:3000/auth/callback',
    postLogoutRedirectUri: 'http://localhost:3000',
  }
};

// Get current domain configuration
export const getCurrentDomainConfig = () => {
  return isProduction ? DOMAIN_CONFIG.production : DOMAIN_CONFIG.development;
};

// Entra ID Configuration for Vedprakash Domain
export const ENTRA_ID_CONFIG = {
  tenantId: 'vedid.onmicrosoft.com',
  authority: process.env.REACT_APP_AUTHORITY || 'https://login.microsoftonline.com/vedid.onmicrosoft.com',
  clientId: process.env.REACT_APP_CLIENT_ID || 'your-vimarsh-app-client-id',
  scopes: ['openid', 'profile', 'email'],
};

// Environment-aware configuration
export const AUTH_CONFIG = {
  ...ENTRA_ID_CONFIG,
  ...getCurrentDomainConfig(),
  enableDebugLogging: isDevelopment,
  usePlaceholder: isDevelopment && !process.env.REACT_APP_CLIENT_ID,
};

// API Configuration
export const API_CONFIG = {
  baseUrl: isProduction 
    ? 'https://vimarsh-backend.azurewebsites.net/api'
    : process.env.REACT_APP_API_BASE_URL || 'http://localhost:7071/api',
  scopes: ENTRA_ID_CONFIG.scopes,
  timeout: 30000,
};

// Feature Flags
export const FEATURE_FLAGS = {
  enableAnalytics: isProduction || process.env.REACT_APP_ENABLE_ANALYTICS === 'true',
  enablePWA: process.env.REACT_APP_ENABLE_PWA !== 'false',
  enableVoice: process.env.REACT_APP_ENABLE_VOICE !== 'false',
  enableOfflineMode: process.env.REACT_APP_ENABLE_OFFLINE !== 'false',
  debugAuth: isDevelopment && process.env.REACT_APP_DEBUG_AUTH === 'true',
};

// Application Information
export const APP_CONFIG = {
  name: 'Vimarsh',
  description: 'AI-powered spiritual guidance from Lord Krishna',
  version: process.env.REACT_APP_VERSION || '1.0.0',
  domain: 'vimarsh.vedprakash.net',
  supportEmail: 'support@vedprakash.net',
  environment: process.env.NODE_ENV || 'development',
};

// Validation function for environment configuration
export const validateEnvironmentConfig = (): boolean => {
  const issues: string[] = [];

  // Check required environment variables in production
  if (isProduction) {
    if (!process.env.REACT_APP_CLIENT_ID || process.env.REACT_APP_CLIENT_ID === 'your-vimarsh-app-client-id') {
      issues.push('REACT_APP_CLIENT_ID is not properly configured for production');
    }
  }

  // Validate domain configuration
  const domainConfig = getCurrentDomainConfig();
  if (!domainConfig.redirectUri.includes('/auth/callback')) {
    issues.push('Redirect URI must include /auth/callback path');
  }

  // Validate authority URL
  const validAuthorities = [
    'vedid.onmicrosoft.com',
    'common',
    'consumers'
  ];
  const authorityValid = validAuthorities.some(part => ENTRA_ID_CONFIG.authority.includes(part));
  if (!authorityValid) {
    issues.push('Authority must be vedid.onmicrosoft.com, common, or consumers');
  }

  if (issues.length > 0) {
    console.error('🔐 Environment configuration issues:', issues);
    return false;
  }

  console.info('🔐 Environment configuration validated successfully');
  console.info('🌐 Domain:', domainConfig.domain);
  console.info('🔗 Redirect URI:', domainConfig.redirectUri);
  return true;
};

// Export environment-specific configuration
export default AUTH_CONFIG;

// Export commonly used values for compatibility
export const API_BASE_URL = API_CONFIG.baseUrl;
