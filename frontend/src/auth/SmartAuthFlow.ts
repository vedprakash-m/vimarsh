import { IPublicClientApplication } from '@azure/msal-browser';

/**
 * Smart Authentication Flow Handler
 * Uses redirect flow with proper SPA configuration to avoid CORS issues
 */
export class SmartAuthFlow {
  private msalInstance: IPublicClientApplication;

  constructor(msalInstance: IPublicClientApplication) {
    this.msalInstance = msalInstance;
  }

  /**
   * Attempt authentication using redirect flow (proper SPA configuration)
   */
  async authenticate(scopes: string[] = ['openid', 'profile', 'email']) {
    try {
      console.log('🔄 Starting redirect authentication...');
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

  /**
   * Handle the redirect callback
   */
  async handleRedirectCallback() {
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
