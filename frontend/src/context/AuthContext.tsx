// Authentication Context Provider
// Provides authentication state and methods throughout the app

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authConfig } from '../auth/msalConfig';
import { createAuthService, AuthUser, AuthState, AuthService } from '../auth/authService';

interface AuthContextType extends AuthState {
  authService: AuthService;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
  enableMSAL?: boolean; // Flag to switch between placeholder and MSAL
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ 
  children, 
  enableMSAL = false // Default to placeholder auth for development
}) => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    isLoading: true,
    error: null
  });

  // Initialize appropriate auth service based on environment
  const authService: AuthService = React.useMemo(() => {
    // Override authConfig for testing purposes if needed
    if (enableMSAL && !authConfig.usePlaceholder) {
      try {
        const { MSALAuthService } = require('../auth/msalAuthService');
        return new MSALAuthService();
      } catch (error) {
        console.warn('MSAL service not available, falling back to placeholder:', error);
        return createAuthService();
      }
    } else {
      return createAuthService();
    }
  }, [enableMSAL]);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
      
      // Check if user is already authenticated
      const user = await authService.getUser();
      
      setAuthState({
        isAuthenticated: !!user,
        user,
        isLoading: false,
        error: null
      });
    } catch (error) {
      console.error('Auth initialization error:', error);
      setAuthState({
        isAuthenticated: false,
        user: null,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Authentication initialization failed'
      });
    }
  };

  const login = async () => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const user = await authService.login();
      
      setAuthState({
        isAuthenticated: true,
        user,
        isLoading: false,
        error: null
      });
    } catch (error) {
      console.error('Login error:', error);
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed'
      }));
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      
      setAuthState({
        isAuthenticated: false,
        user: null,
        isLoading: false,
        error: null
      });
    } catch (error) {
      console.error('Logout error:', error);
      setAuthState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Logout failed'
      }));
    }
  };

  const refreshAuth = async () => {
    await initializeAuth();
  };

  const contextValue: AuthContextType = {
    ...authState,
    authService,
    login,
    logout,
    refreshAuth
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
