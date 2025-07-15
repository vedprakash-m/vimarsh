/**
 * Environment Configuration for Vimarsh Frontend
 * Handles custom domain vimarsh.vedprakash.net
 * Provides proper Entra ID settings per Apps_Auth_Requirement.md
 */

// Environment detection
export const isProduction = process.env.NODE_ENV === 'production';
export const isDevelopment = process.env.NODE_ENV === 'development';

// Detect current runtime domain for Azure Static Web Apps support
export const getCurrentRuntimeDomain = (): string => {
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  
  // Fallback for SSR/build time - return placeholder, will be resolved at runtime
  return 'runtime-domain-placeholder';
};

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

// Get current domain configuration with Azure Static Web App support
export const getCurrentDomainConfig = () => {
  if (isDevelopment) {
    return DOMAIN_CONFIG.development;
  }
  
  // Production environment - check for Azure Static Web App deployment at runtime
  if (typeof window !== 'undefined') {
    const runtimeDomain = window.location.origin;
    if (runtimeDomain.includes('.azurestaticapps.net')) {
      console.info('🌐 Azure Static Web App deployment detected:', runtimeDomain);
      return {
        domain: runtimeDomain,
        redirectUri: `${runtimeDomain}/auth/callback`,
        postLogoutRedirectUri: runtimeDomain,
      };
    }
  }
  
  // Default to custom domain configuration
  return DOMAIN_CONFIG.production;
};

// Entra ID Configuration for Vedprakash Domain
export const ENTRA_ID_CONFIG = {
  tenantId: 'common', // Allow both personal and work accounts
  authority: process.env.REACT_APP_AUTHORITY || 'https://login.microsoftonline.com/common',
  clientId: process.env.REACT_APP_CLIENT_ID || 'your-vimarsh-app-client-id',
  scopes: ['openid', 'profile', 'email'],
};

// Environment-aware configuration
export const getAuthConfig = () => {
  const domainConfig = getCurrentDomainConfig();
  return {
    ...ENTRA_ID_CONFIG,
    ...domainConfig,
    enableDebugLogging: isDevelopment,
    usePlaceholder: isDevelopment && !process.env.REACT_APP_CLIENT_ID,
  };
};

// For backward compatibility - but this will use static config
export const AUTH_CONFIG = {
  ...ENTRA_ID_CONFIG,
  enableDebugLogging: isDevelopment,
  usePlaceholder: isDevelopment && !process.env.REACT_APP_CLIENT_ID,
};

// API Configuration
export const API_CONFIG = {
  baseUrl: process.env.REACT_APP_API_BASE_URL || (isProduction 
    ? 'https://vimarsh-backend-app.azurewebsites.net/api'
    : 'http://localhost:7071/api'),
  scopes: ENTRA_ID_CONFIG.scopes,
  timeout: 30000,
};

// Get API base URL with proper environment detection
export const getApiBaseUrl = (): string => {
  // Always prefer environment variable
  if (process.env.REACT_APP_API_BASE_URL) {
    return process.env.REACT_APP_API_BASE_URL;
  }
  
  // If we're on the production domain, force production API URL
  if (typeof window !== 'undefined' && window.location.hostname === 'vimarsh.vedprakash.net') {
    return 'https://vimarsh-backend-app.azurewebsites.net/api';
  }
  
  // Fallback based on environment
  return isProduction 
    ? 'https://vimarsh-backend-app.azurewebsites.net/api'
    : 'http://localhost:7071/api';
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
