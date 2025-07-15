import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { AccountInfo } from '@azure/msal-browser';
import SmartAuthFlow from './SmartAuthFlow';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  account: AccountInfo | null;
  error: string | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [isLoading, setIsLoading] = useState(true);
  const [account, setAccount] = useState<AccountInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [smartAuth] = useState(() => new SmartAuthFlow(instance));

  // Centralized function to update account state with validation
  const updateAccountState = useCallback(() => {
    const accounts = instance.getAllAccounts();
    const activeAccount = instance.getActiveAccount();
    
    console.log('🔄 AuthProvider: Updating account state', {
      accountsFound: accounts.length,
      activeAccount: activeAccount?.username,
      isAuthenticated,
      msalInstanceReady: !!instance.getConfiguration()
    });

    if (accounts.length > 0) {
      // If we have accounts but no active account, set the first one as active
      if (!activeAccount) {
        try {
          instance.setActiveAccount(accounts[0]);
          setAccount(accounts[0]);
          console.log('✅ AuthProvider: Set active account to', accounts[0].username);
        } catch (err) {
          console.error('❌ AuthProvider: Failed to set active account:', err);
          setError('Failed to set active account');
        }
      } else {
        setAccount(activeAccount);
      }
    } else {
      setAccount(null);
      // Clear any existing errors if no accounts (user logged out)
      if (!isAuthenticated) {
        setError(null);
      }
    }
  }, [instance, isAuthenticated]);

  // Validate authentication state - ensures MSAL and AuthProvider are in sync
  const validateAuthenticationState = useCallback((): boolean => {
    const accounts = instance.getAllAccounts();
    const activeAccount = instance.getActiveAccount();
    const hasValidAccount = accounts.length > 0 && activeAccount;
    
    console.log('🔍 AuthProvider: Validating authentication state', {
      msalAuthenticated: isAuthenticated,
      hasAccounts: accounts.length > 0,
      hasActiveAccount: !!activeAccount,
      stateValid: hasValidAccount === isAuthenticated
    });

    // Return true if MSAL state matches our expected state
    return hasValidAccount === isAuthenticated;
  }, [instance, isAuthenticated]);

  // Initialize authentication state on mount with validation
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setIsLoading(true);
        
        // Wait for MSAL to be fully initialized
        let retries = 0;
        while (!instance.getConfiguration() && retries < 5) {
          console.log('⏳ AuthProvider: Waiting for MSAL initialization...', retries + 1);
          await new Promise(resolve => setTimeout(resolve, 500));
          retries++;
        }

        if (!instance.getConfiguration()) {
          throw new Error('MSAL instance failed to initialize');
        }

        updateAccountState();
        
        // Validate authentication state consistency
        if (!validateAuthenticationState()) {
          console.warn('⚠️ AuthProvider: Authentication state inconsistency detected');
          setError('Authentication state synchronization issue. Please try signing in again.');
        } else {
          setError(null);
        }
      } catch (err) {
        console.error('❌ AuthProvider: Initialization error:', err);
        setError(err instanceof Error ? err.message : 'Failed to initialize authentication');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, [instance, updateAccountState, validateAuthenticationState]);

  // Update account state when authentication status changes
  useEffect(() => {
    updateAccountState();
  }, [isAuthenticated, updateAccountState]);

  const login = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Use redirect authentication flow
      const result = await smartAuth.authenticate(['openid', 'profile', 'email']);
      
      if (result.success) {
        if (result.pending) {
          console.log('🔄 Redirect authentication initiated');
          // Don't set loading to false for redirect flow - user will be redirected
          return;
        } else {
          // For redirect flow, the account will be available after redirect callback
          console.log('✅ Authentication initiated via', result.method);
        }
      } else {
        console.error('❌ Authentication failed:', result.error);
        setError(result.error || 'Authentication failed');
      }
    } catch (err: any) {
      console.error('❌ AuthProvider: Login error:', err);
      setError(err.message || 'Login failed');
    } finally {
      // Only set loading false if we're not doing a redirect
      setIsLoading(false);
    }
  }, [smartAuth]);

  const logout = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const account = instance.getActiveAccount();
      if (account) {
        await instance.logoutRedirect({
          account,
          postLogoutRedirectUri: window.location.origin
        });
        console.log('✅ Logout redirect initiated');
      }
    } catch (err: any) {
      console.error('❌ AuthProvider: Logout error:', err);
      setError(err.message || 'Logout failed');
    } finally {
      setIsLoading(false);
    }
  }, [instance]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const refreshAuth = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      console.log('🔄 AuthProvider: Refreshing authentication state...');
      
      // Update account state first
      updateAccountState();
      
      // Validate authentication state consistency
      if (!validateAuthenticationState()) {
        console.warn('⚠️ AuthProvider: Authentication state inconsistency after refresh');
        setError('Authentication validation failed. Please sign in again.');
        return;
      }

      // If we have an account, try to refresh tokens to ensure they're valid
      const activeAccount = instance.getActiveAccount();
      if (activeAccount) {
        try {
          await instance.acquireTokenSilent({
            scopes: ['openid', 'profile', 'email'],
            account: activeAccount
          });
          console.log('✅ AuthProvider: Token refresh successful');
        } catch (tokenError) {
          console.warn('⚠️ AuthProvider: Token refresh failed (may require re-auth):', tokenError);
          // Don't set this as an error yet - the user might still be authenticated
        }
      }

      console.log('✅ AuthProvider: Authentication refresh completed');
    } catch (err: any) {
      console.error('❌ AuthProvider: Auth refresh error:', err);
      setError(err.message || 'Authentication refresh failed');
    } finally {
      setIsLoading(false);
    }
  }, [instance, updateAccountState, validateAuthenticationState]);

  const value: AuthContextType = {
    isAuthenticated,
    isLoading,
    account,
    error,
    login,
    logout,
    clearError,
    refreshAuth
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
