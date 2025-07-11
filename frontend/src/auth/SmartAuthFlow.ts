import { IPublicClientApplication } from '@azure/msal-browser';

/**
 * Smart Authentication Flow Handler
 * Uses popup-only mode to avoid CORS issues completely
 */
export class SmartAuthFlow {
  private msalInstance: IPublicClientApplication;
  private usePopupOnly: boolean = true; // Force popup-only mode

  constructor(msalInstance: IPublicClientApplication) {
    this.msalInstance = msalInstance;
  }

  /**
   * Attempt authentication using popup-only flow (no CORS issues)
   */
  async authenticate(scopes: string[] = ['openid', 'profile', 'email']) {
    // Always try popup first (better for CORS avoidance)
    if (this.canUsePopup()) {
      try {
        console.log('🪟 Attempting popup authentication...');
        const result = await this.msalInstance.loginPopup({
          scopes,
          prompt: 'select_account'
        });
        
        if (result.account) {
          this.msalInstance.setActiveAccount(result.account);
          console.log('✅ Popup authentication successful');
          return { success: true, method: 'popup', account: result.account };
        }
      } catch (popupError: any) {
        console.warn('⚠️ Popup authentication failed:', popupError.errorCode);
        
        // Don't fall back to redirect for user cancellation
        if (popupError.errorCode === 'user_cancelled') {
          return { success: false, method: 'popup', error: 'User cancelled authentication' };
        }
        
        // For popup-only mode, don't fall back to redirect
        if (this.usePopupOnly) {
          return { success: false, method: 'popup', error: `Popup authentication failed: ${popupError.errorCode}` };
        }
      }
    }

    // Only fall back to redirect if popup-only mode is disabled
    if (!this.usePopupOnly) {
      console.log('🔄 Falling back to redirect authentication...');
      try {
        await this.msalInstance.loginRedirect({
          scopes,
          prompt: 'select_account'
        });
        // Redirect flow doesn't return immediately
        return { success: true, method: 'redirect', pending: true };
      } catch (redirectError: any) {
        console.error('❌ Redirect authentication failed:', redirectError);
        return { success: false, method: 'redirect', error: redirectError.message };
      }
    }

    // If we get here, popup failed and redirect is disabled
    return { success: false, method: 'popup', error: 'Popup authentication failed and redirect is disabled to avoid CORS' };
  }

  /**
   * Check if popup authentication is supported
   */
  private canUsePopup(): boolean {
    // Check if we're in a popup-friendly environment
    if (typeof window === 'undefined') return false;
    
    // Check if popups are blocked
    try {
      const testPopup = window.open('', '', 'width=1,height=1');
      if (testPopup) {
        testPopup.close();
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }

  /**
   * Handle the redirect callback (disabled in popup-only mode to avoid CORS)
   */
  async handleRedirectCallback() {
    // Skip redirect handling in popup-only mode to avoid CORS errors
    if (this.usePopupOnly) {
      console.log('ℹ️ Skipping redirect handling (popup-only mode)');
      return { success: true, skipped: true, reason: 'popup-only mode' };
    }

    try {
      console.log('🔄 Processing redirect callback...');
      const result = await this.msalInstance.handleRedirectPromise();
      
      if (result && result.account) {
        this.msalInstance.setActiveAccount(result.account);
        console.log('✅ Redirect callback processed successfully');
        return { success: true, account: result.account };
      }
      
      return { success: true, noResult: true };
    } catch (error: any) {
      console.error('❌ Redirect callback error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get current authentication state
   */
  getAuthState() {
    const accounts = this.msalInstance.getAllAccounts();
    const activeAccount = this.msalInstance.getActiveAccount();
    
    return {
      isAuthenticated: accounts.length > 0 && !!activeAccount,
      account: activeAccount,
      accountCount: accounts.length
    };
  }
}

export default SmartAuthFlow;
