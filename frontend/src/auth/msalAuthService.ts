import { 
  PublicClientApplication, 
  AuthenticationResult, 
  AccountInfo,
  SilentRequest,
  EndSessionRequest
} from '@azure/msal-browser';
import { 
  msalConfig, 
  loginRequest, 
  apiTokenRequest, 
  silentRequest,
  logoutRequest,
  AUTH_ERROR_MESSAGES 
} from './msalConfig';
import { AuthService, AuthUser } from './authService';

/**
 * MSAL Authentication Service implementing unified Vedprakash domain authentication
 * 
 * This service provides secure authentication using Microsoft Entra ID
 * and implements the standardized VedUser interface for cross-app compatibility.
 */
export class MSALAuthService implements AuthService {
  private msalInstance: PublicClientApplication;
  private accounts: AccountInfo[] = [];

  constructor() {
    this.msalInstance = new PublicClientApplication(msalConfig);
    this.initialize();
  }

  private async initialize(): Promise<void> {
    try {
      await this.msalInstance.initialize();
      this.accounts = this.msalInstance.getAllAccounts();
      console.info('🔐 MSAL initialized successfully');
    } catch (error) {
      console.error('🔐 MSAL initialization failed:', error);
      throw new Error('Authentication system initialization failed');
    }
  }

  async login(): Promise<AuthUser> {
    try {
      console.info('🔐 Starting MSAL login process');
      
      // Use redirect flow for better mobile support
      await this.msalInstance.loginRedirect(loginRequest);
      
      // After redirect, this won't execute immediately
      // The user will be redirected and come back to the app
      // We need to handle this in the callback or when checking auth state
      throw new Error('Login redirect initiated. User will return after authentication.');

    } catch (error: any) {
      console.error('🔐 Login failed:', error);
      
      // Map MSAL errors to user-friendly messages
      if (error.errorCode === 'user_cancelled') {
        throw new Error('Sign-in was cancelled. Please try again.');
      } else if (error.errorCode === 'network_error') {
        throw new Error(AUTH_ERROR_MESSAGES.NETWORK_ERROR);
      } else {
        throw new Error(AUTH_ERROR_MESSAGES.GENERAL_ERROR);
      }
    }
  }

  async logout(): Promise<void> {
    try {
      if (this.accounts.length === 0) {
        console.warn('🔐 No account to logout');
        return;
      }

      const logoutRequestWithAccount: EndSessionRequest = {
        ...logoutRequest,
        account: this.accounts[0]
      };

      console.info('🔐 Starting logout process');
      await this.msalInstance.logoutRedirect(logoutRequestWithAccount);
      
      this.accounts = [];
      console.info('🔐 Logout successful');

    } catch (error) {
      console.error('🔐 Logout failed:', error);
      throw new Error('Logout failed. Please try again.');
    }
  }

  async getUser(): Promise<AuthUser | null> {
    try {
      this.accounts = this.msalInstance.getAllAccounts();
      
      if (this.accounts.length === 0) {
        return null;
      }

      const vedUser = this.extractVedUser(this.accounts[0]);
      return vedUser;

    } catch (error) {
      console.error('🔐 Failed to get user:', error);
      return null;
    }
  }

  async getToken(): Promise<string> {
    try {
      if (this.accounts.length === 0) {
        throw new Error(AUTH_ERROR_MESSAGES.NO_ACCOUNT);
      }

      const tokenRequest: SilentRequest = {
        ...silentRequest,
        account: this.accounts[0]
      };

      // Try silent token acquisition first
      const response = await this.msalInstance.acquireTokenSilent(tokenRequest);
      
      console.debug('🔐 Token acquired silently');
      return response.accessToken;

    } catch (error: any) {
      console.warn('🔐 Silent token acquisition failed:', error);

      // If silent fails, we need to trigger interactive flow
      // For redirect flow, we can't return a token immediately
      try {
        const interactiveRequest = {
          ...apiTokenRequest,
          account: this.accounts[0]
        };

        // This will redirect the user, so we can't return a token here
        await this.msalInstance.acquireTokenRedirect(interactiveRequest);
        
        // This line won't be reached in redirect flow
        throw new Error('Token acquisition requires user interaction. Please try again.');

      } catch (interactiveError) {
        console.error('🔐 Interactive token acquisition failed:', interactiveError);
        throw new Error(AUTH_ERROR_MESSAGES.TOKEN_EXPIRED);
      }
    }
  }

  async refreshToken(): Promise<string> {
    try {
      if (this.accounts.length === 0) {
        throw new Error(AUTH_ERROR_MESSAGES.NO_ACCOUNT);
      }

      const tokenRequest: SilentRequest = {
        ...silentRequest,
        account: this.accounts[0],
        forceRefresh: true // Force refresh
      };

      const response = await this.msalInstance.acquireTokenSilent(tokenRequest);
      console.info('🔐 Token refreshed successfully');
      
      return response.accessToken;

    } catch (error) {
      console.error('🔐 Token refresh failed:', error);
      throw new Error(AUTH_ERROR_MESSAGES.TOKEN_EXPIRED);
    }
  }

  /**
   * Extract standardized VedUser from Microsoft account information
   * 
   * This ensures compatibility with the unified Vedprakash domain user interface
   */
  private extractVedUser(account: AccountInfo): AuthUser {
    const claims = account.idTokenClaims as any;
    
    return {
      // ✅ Core VedUser interface compliance (required fields)
      id: account.homeAccountId,
      email: account.username,
      name: account.name || claims?.name || '',
      givenName: claims?.given_name || '',
      familyName: claims?.family_name || '',
      permissions: claims?.roles || [],
      
      // ✅ VedProfile for unified domain experience
      vedProfile: {
        profileId: account.homeAccountId,
        subscriptionTier: 'free', // Default tier
        appsEnrolled: ['vimarsh'],
        preferences: {
          language: 'English', // Default language
          spiritualInterests: [],
          communicationStyle: 'reverent'
        }
      },

      // ✅ Vimarsh-specific spiritual context (backward compatibility - optional)
      preferredLanguage: 'English',
      spiritualInterests: [],
      role: 'seeker', // Default spiritual role
      joinedDate: new Date().toISOString(),
      sessionCount: 1,
      lastActiveDate: new Date().toISOString(),
      profilePicture: '🙏'
    };
  }

  /**
   * Check if user is currently authenticated
   */
  isAuthenticated(): boolean {
    this.accounts = this.msalInstance.getAllAccounts();
    return this.accounts.length > 0;
  }

  /**
   * Get current account information
   */
  getCurrentAccount(): AccountInfo | null {
    this.accounts = this.msalInstance.getAllAccounts();
    return this.accounts.length > 0 ? this.accounts[0] : null;
  }

  /**
   * Handle authentication callback after redirect
   */
  async handleRedirectCallback(): Promise<AuthenticationResult | null> {
    try {
      const response = await this.msalInstance.handleRedirectPromise();
      
      if (response) {
        this.accounts = this.msalInstance.getAllAccounts();
        console.info('🔐 Redirect callback handled successfully');
        return response;
      }

      return null;

    } catch (error) {
      console.error('🔐 Redirect callback handling failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const msalAuthService = new MSALAuthService();

// Export utility functions
export const createMSALAuthService = (): MSALAuthService => {
  return new MSALAuthService();
};

export default MSALAuthService;
