// Debug logging for build-time debugging
console.log('Environment debug info:', {
  NODE_ENV: process.env.NODE_ENV,
  REACT_APP_ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT,
  REACT_APP_API_BASE_URL: process.env.REACT_APP_API_BASE_URL,
  buildTime: new Date().toISOString()
});

// Environment Configuration Manager for React Frontend
// This module provides type-safe access to environment variables

export interface EnvironmentConfig {
  environment: string;
  apiBaseUrl: string;
  authConfig: {
    clientId: string;
    tenantId: string;
    redirectUri: string;
  };
  features: {
    analytics: boolean;
    voiceInterface: boolean;
    expertReview: boolean;
    pwaFeatures: boolean;
  };
  settings: {
    defaultLanguage: string;
    maxQueryLength: number;
    rateLimitPerMinute: number;
  };
  debug: {
    debugMode: boolean;
    showDetailedErrors: boolean;
  };
}

class EnvironmentConfigManager {
  private config: EnvironmentConfig;

  constructor() {
    this.config = this.loadConfiguration();
    this.validateConfiguration();
  }

  private loadConfiguration(): EnvironmentConfig {
    // Debug logging for environment variables - Build v2.0
    console.log('Environment variables loaded:', {
      REACT_APP_ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT,
      REACT_APP_API_BASE_URL: process.env.REACT_APP_API_BASE_URL,
      NODE_ENV: process.env.NODE_ENV
    });
    
    return {
      environment: process.env.REACT_APP_ENVIRONMENT || 'development',
      apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:7071',
      authConfig: {
        clientId: process.env.REACT_APP_AUTH_CLIENT_ID || '',
        tenantId: process.env.REACT_APP_AUTH_TENANT_ID || '',
        redirectUri: process.env.REACT_APP_AUTH_REDIRECT_URI || 'http://localhost:3000/auth/callback',
      },
      features: {
        analytics: process.env.REACT_APP_ENABLE_ANALYTICS === 'true',
        voiceInterface: process.env.REACT_APP_ENABLE_VOICE_INTERFACE === 'true',
        expertReview: process.env.REACT_APP_ENABLE_EXPERT_REVIEW === 'true',
        pwaFeatures: process.env.REACT_APP_ENABLE_PWA_FEATURES === 'true',
      },
      settings: {
        defaultLanguage: process.env.REACT_APP_DEFAULT_LANGUAGE || 'en',
        maxQueryLength: parseInt(process.env.REACT_APP_MAX_QUERY_LENGTH || '1000'),
        rateLimitPerMinute: parseInt(process.env.REACT_APP_RATE_LIMIT_PER_MINUTE || '60'),
      },
      debug: {
        debugMode: process.env.REACT_APP_DEBUG_MODE === 'true',
        showDetailedErrors: process.env.REACT_APP_SHOW_DETAILED_ERRORS === 'true',
      },
    };
  }

  private validateConfiguration(): void {
    const { environment, authConfig, apiBaseUrl } = this.config;

    // Validate required configuration
    if (!apiBaseUrl) {
      throw new Error('API base URL is required');
    }

    // Validate authentication configuration for non-development environments
    if (environment !== 'development') {
      if (!authConfig.clientId || !authConfig.tenantId) {
        throw new Error('Authentication configuration is required for non-development environments');
      }
    }

    // Validate URLs
    try {
      new URL(apiBaseUrl);
      new URL(authConfig.redirectUri);
    } catch (error) {
      throw new Error('Invalid URL configuration');
    }

    console.log(`✅ Environment configuration validated for: ${environment}`);
  }

  // Public getters
  public get(): EnvironmentConfig {
    return { ...this.config };
  }

  public getEnvironment(): string {
    return this.config.environment;
  }

  public getApiBaseUrl(): string {
    return this.config.apiBaseUrl;
  }

  public getAuthConfig(): EnvironmentConfig['authConfig'] {
    return { ...this.config.authConfig };
  }

  public getFeatures(): EnvironmentConfig['features'] {
    return { ...this.config.features };
  }

  public getSettings(): EnvironmentConfig['settings'] {
    return { ...this.config.settings };
  }

  public isDebugMode(): boolean {
    return this.config.debug.debugMode;
  }

  public isProduction(): boolean {
    return this.config.environment === 'production';
  }

  public isDevelopment(): boolean {
    return this.config.environment === 'development';
  }

  public isStaging(): boolean {
    return this.config.environment === 'staging';
  }

  // Feature flags
  public isFeatureEnabled(feature: keyof EnvironmentConfig['features']): boolean {
    return this.config.features[feature];
  }

  // Environment-specific configurations
  public getApiEndpoint(path: string): string {
    const baseUrl = this.config.apiBaseUrl.replace(/\/$/, '');
    const cleanPath = path.replace(/^\//, '');
    return `${baseUrl}/${cleanPath}`;
  }

  public getLogLevel(): 'debug' | 'info' | 'warn' | 'error' {
    if (this.config.debug.debugMode) {
      return 'debug';
    }
    return this.config.environment === 'development' ? 'debug' : 'info';
  }

  // Configuration summary for debugging
  public getSummary(): Record<string, any> {
    return {
      environment: this.config.environment,
      apiBaseUrl: this.config.apiBaseUrl,
      authConfigured: !!(this.config.authConfig.clientId && this.config.authConfig.tenantId),
      featuresEnabled: Object.entries(this.config.features)
        .filter(([, enabled]) => enabled)
        .map(([feature]) => feature),
      debugMode: this.config.debug.debugMode,
    };
  }
}

// Create singleton instance
const environmentConfig = new EnvironmentConfigManager();

// Export singleton instance and class for testing
export default environmentConfig;
export { EnvironmentConfigManager };

// Export configuration constants
export const ENV = environmentConfig.get();
export const API_BASE_URL = environmentConfig.getApiBaseUrl();
export const AUTH_CONFIG = environmentConfig.getAuthConfig();
export const FEATURES = environmentConfig.getFeatures();
export const SETTINGS = environmentConfig.getSettings();
export const IS_DEVELOPMENT = environmentConfig.isDevelopment();
export const IS_PRODUCTION = environmentConfig.isProduction();
export const IS_STAGING = environmentConfig.isStaging();
export const DEBUG_MODE = environmentConfig.isDebugMode();

// Utility functions
export const getApiEndpoint = (path: string): string => environmentConfig.getApiEndpoint(path);
export const isFeatureEnabled = (feature: keyof EnvironmentConfig['features']): boolean => 
  environmentConfig.isFeatureEnabled(feature);
export const getLogLevel = (): 'debug' | 'info' | 'warn' | 'error' => environmentConfig.getLogLevel();

// Development utilities
if (IS_DEVELOPMENT && DEBUG_MODE) {
  console.log('🔧 Environment Configuration:', environmentConfig.getSummary());
}
