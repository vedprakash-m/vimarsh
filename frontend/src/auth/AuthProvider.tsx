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

  // Centralized function to update account state
  const updateAccountState = useCallback(() => {
    const accounts = instance.getAllAccounts();
    const activeAccount = instance.getActiveAccount();
    
    console.log('🔄 AuthProvider: Updating account state', {
      accountsFound: accounts.length,
      activeAccount: activeAccount?.username,
      isAuthenticated
    });

    if (accounts.length > 0) {
      // If we have accounts but no active account, set the first one as active
      if (!activeAccount) {
        instance.setActiveAccount(accounts[0]);
        setAccount(accounts[0]);
        console.log('✅ AuthProvider: Set active account to', accounts[0].username);
      } else {
        setAccount(activeAccount);
      }
    } else {
      setAccount(null);
    }
  }, [instance, isAuthenticated]);

  // Initialize authentication state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setIsLoading(true);
        
        // Wait for MSAL to be fully initialized
        if (!instance.getConfiguration()) {
          console.log('⏳ AuthProvider: Waiting for MSAL initialization...');
          await new Promise(resolve => setTimeout(resolve, 1000));
        }

        updateAccountState();
        setError(null);
      } catch (err) {
        console.error('❌ AuthProvider: Initialization error:', err);
        setError('Failed to initialize authentication');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, [instance, updateAccountState]);

  // Update account state when authentication status changes
  useEffect(() => {
    updateAccountState();
  }, [isAuthenticated, updateAccountState]);

  const login = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Use smart authentication flow to avoid CORS issues
      const result = await smartAuth.authenticate(['openid', 'profile', 'email']);
      
      if (result.success) {
        if (result.account) {
          setAccount(result.account);
          console.log('✅ Authentication successful via', result.method);
        } else if (result.pending) {
          console.log('🔄 Redirect authentication initiated');
          // Don't set loading to false for redirect flow
          return;
        }
      } else {
        setError(result.error || 'Authentication failed');
      }
    } catch (err: any) {
      console.error('❌ AuthProvider: Login error:', err);
      setError(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  }, [smartAuth]);

  const logout = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const account = instance.getActiveAccount();
      if (account) {
        // Use popup logout to avoid redirect-related CORS issues
        try {
          await instance.logoutPopup({
            account,
            postLogoutRedirectUri: window.location.origin
          });
          console.log('✅ Popup logout successful');
        } catch (popupError) {
          console.warn('⚠️ Popup logout failed, falling back to local logout:', popupError);
          // Fall back to local logout if popup fails
          instance.setActiveAccount(null);
          setAccount(null);
        }
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
      updateAccountState();
      
      // Force a token refresh to validate the current account
      const account = instance.getActiveAccount();
      if (account) {
        try {
          await instance.acquireTokenSilent({
            scopes: ['openid', 'profile', 'email'],
            account
          });
          console.log('✅ AuthProvider: Token refresh successful');
        } catch (tokenError) {
          console.warn('⚠️ AuthProvider: Token refresh failed, account may be stale');
        }
      }
    } catch (err: any) {
      console.error('❌ AuthProvider: Refresh error:', err);
      setError(err.message || 'Failed to refresh authentication');
    } finally {
      setIsLoading(false);
    }
  }, [instance, updateAccountState]);

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
