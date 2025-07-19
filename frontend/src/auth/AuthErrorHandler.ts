/**
 * Specialized error handler for authentication and CORS-related issues
 * Provides fallback mechanisms and detailed error diagnostics
 */

import { IPublicClientApplication, BrowserAuthError, AuthenticationResult } from '@azure/msal-browser';

export interface AuthErrorInfo {
  errorCode: string;
  errorMessage: string;
  isCorsRelated: boolean;
  isNetworkError: boolean;
  suggestedAction: string;
  canRetryWithPopup: boolean;
}

export class AuthErrorHandler {
  private static readonly CORS_ERROR_CODES = [
    'post_request_failed',
    'network_error',
    'user_login_error',
    'token_renewal_error'
  ];

  private static readonly NETWORK_ERROR_PATTERNS = [
    'CORS',
    'cors',
    'Network request failed',
    'fetch',
    'XMLHttpRequest'
  ];

  /**
   * Analyzes an authentication error and provides structured information
   */
  static analyzeError(error: any): AuthErrorInfo {
    const errorCode = error?.errorCode || error?.code || 'unknown_error';
    const errorMessage = error?.message || error?.errorMessage || 'Unknown authentication error';
    
    const isCorsRelated = this.isCorsError(error);
    const isNetworkError = this.isNetworkError(error);
    
    return {
      errorCode,
      errorMessage,
      isCorsRelated,
      isNetworkError,
      suggestedAction: this.getSuggestedAction(errorCode, isCorsRelated),
      canRetryWithPopup: this.canRetryWithPopup(errorCode, isCorsRelated)
    };
  }

  /**
   * Determines if an error is CORS-related
   */
  private static isCorsError(error: any): boolean {
    const errorCode = error?.errorCode || error?.code || '';
    const errorMessage = error?.message || '';
    
    // Check for known CORS error codes
    if (this.CORS_ERROR_CODES.includes(errorCode)) {
      return true;
    }
    
    // Check for CORS-related patterns in error message
    return this.NETWORK_ERROR_PATTERNS.some(pattern => 
      errorMessage.toLowerCase().includes(pattern.toLowerCase())
    );
  }

  /**
   * Determines if an error is network-related
   */
  private static isNetworkError(error: any): boolean {
    const errorCode = error?.errorCode || error?.code || '';
    return errorCode.includes('network') || errorCode.includes('request_failed');
  }

  /**
   * Provides suggested action based on error type
   */
  private static getSuggestedAction(errorCode: string, isCorsRelated: boolean): string {
    if (isCorsRelated) {
      return 'Try using popup authentication or clear browser cache and cookies';
    }
    
    switch (errorCode) {
      case 'user_cancelled':
        return 'User cancelled authentication - try again when ready';
      case 'consent_required':
        return 'Additional consent required - use prompt: "consent"';
      case 'interaction_required':
        return 'Interactive authentication required - use popup or redirect';
      case 'login_required':
        return 'Login required - clear cache and authenticate again';
      default:
        return 'Check network connection and try again';
    }
  }

  /**
   * Determines if popup retry is recommended for this error
   */
  private static canRetryWithPopup(errorCode: string, isCorsRelated: boolean): boolean {
    // Don't retry with popup for user cancellation
    if (errorCode === 'user_cancelled') {
      return false;
    }
    
    // Popup is good for CORS issues and network errors
    return isCorsRelated || errorCode.includes('network') || errorCode.includes('request_failed');
  }

  /**
   * Attempts popup authentication as a fallback for CORS issues
   */
  static async attemptPopupFallback(
    msalInstance: IPublicClientApplication,
    scopes: string[] = ['openid', 'profile', 'email']
  ): Promise<AuthenticationResult | null> {
    try {
      console.log('🔄 AuthErrorHandler: Attempting popup fallback...');
      
      const result = await msalInstance.loginPopup({
        scopes,
        prompt: 'select_account'
      });
      
      if (result.account) {
        msalInstance.setActiveAccount(result.account);
        console.log('✅ AuthErrorHandler: Popup fallback successful');
        return result;
      }
      
      return null;
    } catch (popupError) {
      console.error('❌ AuthErrorHandler: Popup fallback failed:', popupError);
      throw popupError;
    }
  }

  /**
   * Provides user-friendly error messages
   */
  static getUserFriendlyMessage(errorInfo: AuthErrorInfo): string {
    if (errorInfo.isCorsRelated) {
      return 'Authentication server temporarily unavailable due to network configuration. You can try the manual recovery option or refresh the page.';
    }
    
    switch (errorInfo.errorCode) {
      case 'user_cancelled':
        return 'Authentication was cancelled. Click "Sign In" to try again.';
      case 'popup_window_error':
        return 'Popup was blocked or closed. Please allow popups for this site and try again.';
      case 'consent_required':
        return 'Additional permissions required. You will be prompted to grant consent.';
      case 'interaction_required':
        return 'Please complete the authentication process.';
      default:
        return `Authentication error: ${errorInfo.errorMessage}`;
    }
  }

  /**
   * Logs detailed error information for debugging
   */
  static logDetailedError(error: any, context: string = 'unknown'): void {
    const errorInfo = this.analyzeError(error);
    
    console.group(`🚨 Auth Error in ${context}`);
    console.error('Original Error:', error);
    console.log('Error Analysis:', errorInfo);
    console.log('User-Friendly Message:', this.getUserFriendlyMessage(errorInfo));
    console.log('Browser Info:', {
      userAgent: navigator.userAgent,
      cookieEnabled: navigator.cookieEnabled,
      onLine: navigator.onLine
    });
    console.groupEnd();
  }
}

export default AuthErrorHandler;
