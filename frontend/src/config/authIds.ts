/**
 * Centralized Authentication Configuration
 * Single source of truth for all Entra ID settings
 * 
 * ⚠️  IMPORTANT: This file contains the actual Client ID values
 * ⚠️  Do not commit actual production values to version control
 * ⚠️  Use environment variables for production deployment
 */

// Environment-specific Client ID mapping
const CLIENT_ID_MAP = {
  // Production - multitenant + personal accounts (matches Azure app registration)
  production: {
    clientId: '52747449-829f-4fbe-bb5e-b4c54c9b1fbe',
    tenantId: 'common', // 'common' supports multitenant + personal Microsoft accounts
    environment: 'multitenant-production',
    accountType: 'multitenant-personal' // Any Microsoft Entra ID tenant + personal accounts
  },
  
  // Development - same configuration for consistency
  development: {
    clientId: '52747449-829f-4fbe-bb5e-b4c54c9b1fbe', // Use same client ID
    tenantId: 'common', // 'common' supports multitenant + personal Microsoft accounts
    environment: 'multitenant-development',
    accountType: 'multitenant-personal' // Any Microsoft Entra ID tenant + personal accounts
  }
};

/**
 * Get the appropriate Client ID based on environment
 * Priority: Environment Variable > Production Config > Development Fallback
 */
export const getClientId = (): string => {
  // 1st Priority: Environment variable (production deployment)
  if (process.env.REACT_APP_CLIENT_ID) {
    return process.env.REACT_APP_CLIENT_ID;
  }
  
  // 2nd Priority: Production config (for builds)
  if (process.env.NODE_ENV === 'production') {
    return CLIENT_ID_MAP.production.clientId;
  }
  
  // 3rd Priority: Development fallback
  return CLIENT_ID_MAP.development.clientId;
};

/**
 * Get the appropriate tenant configuration
 */
export const getTenantConfig = () => {
  const isProduction = process.env.NODE_ENV === 'production';
  const config = isProduction ? CLIENT_ID_MAP.production : CLIENT_ID_MAP.development;
  
  return {
    clientId: getClientId(),
    tenantId: process.env.REACT_APP_TENANT_ID || config.tenantId,
    authority: process.env.REACT_APP_AUTHORITY || `https://login.microsoftonline.com/${config.tenantId}`,
    environment: config.environment
  };
};

/**
 * Validate that we have a proper Client ID configured
 */
export const validateClientId = (): boolean => {
  const clientId = getClientId();
  
  // Check for placeholder values
  const placeholders = [
    'your-client-id',
    'your-vimarsh-app-client-id',
    'placeholder-client-id'
    // Removed old default directory ID since we're using vedid tenant consistently
  ];
  
  if (placeholders.includes(clientId)) {
    console.error('🚨 Client ID is still a placeholder value:', clientId);
    return false;
  }
  
  // Check for proper GUID format
  const guidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!guidRegex.test(clientId)) {
    console.error('🚨 Client ID is not a valid GUID format:', clientId);
    return false;
  }
  
  console.log('✅ Client ID validation passed:', clientId.substring(0, 8) + '...');
  return true;
};

// Export the centralized configuration
export const AUTH_IDS = {
  getClientId,
  getTenantConfig,
  validateClientId,
  
  // For debugging/logging only
  getConfigSummary: () => {
    const config = getTenantConfig();
    return {
      clientId: config.clientId.substring(0, 8) + '...',
      tenantId: config.tenantId,
      authority: config.authority,
      environment: config.environment,
      source: process.env.REACT_APP_CLIENT_ID ? 'env-var' : 'default-config'
    };
  }
};

export default AUTH_IDS;
