import React, { useState, useEffect, createContext, useContext } from 'react';
import { authService, type AuthUser, handleAuthError } from '../auth/authService';

// Note: Language context will be imported where needed since this component
// is wrapped within the LanguageProvider in App.tsx

// Authentication context for sharing auth state across components
interface AuthContextType {
  isAuthenticated: boolean;
  user: AuthUser | null;
  login: (userType?: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

// Custom hook to use authentication context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthenticationWrapper');
  }
  return context;
};

interface AuthenticationWrapperProps {
  children: React.ReactNode;
}

const AuthenticationWrapper: React.FC<AuthenticationWrapperProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check for existing authentication on component mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setIsLoading(true);
        const currentUser = await authService.getUser();
        if (currentUser) {
          setIsAuthenticated(true);
          setUser(currentUser);
          console.log('🕉️ Restored auth session for:', currentUser.name);
        }
      } catch (error) {
        console.warn('Failed to restore auth session:', error);
        setError(handleAuthError(error));
      } finally {
        setIsLoading(false);
      }
    };

    // Simulate network delay for realistic loading experience
    setTimeout(initializeAuth, 500);
  }, []);

  const handleLogin = async (userType?: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const loggedInUser = await authService.login({ userType });
      setIsAuthenticated(true);
      setUser(loggedInUser);
      
      console.log('🕉️ Authentication successful:', loggedInUser.name);
    } catch (error) {
      console.error('Authentication failed:', error);
      setError(handleAuthError(error));
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      await authService.logout();
      setIsAuthenticated(false);
      setUser(null);
      setError(null);
      console.log('🙏 Logout successful');
    } catch (error) {
      console.error('Logout failed:', error);
      setError(handleAuthError(error));
    } finally {
      setIsLoading(false);
    }
  };

  const authContextValue: AuthContextType = {
    isAuthenticated,
    user,
    login: handleLogin,
    logout: handleLogout,
    isLoading,
    error
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Login Button Component for Header
export const LoginButton: React.FC = () => {
  const { isAuthenticated, user, login, logout, isLoading, error } = useAuth();
  
  // Note: Language context would be used here if needed, but it's available 
  // through React context since this component is wrapped in LanguageProvider

  // Show loading state during auth operations
  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-neutral-600">
        <div className="animate-spin text-lg">🕉️</div>
        <span className="text-sm">Connecting...</span>
      </div>
    );
  }

  // Show error state if authentication failed
  if (error) {
    return (
      <div className="flex items-center gap-2 text-red-600">
        <span>⚠️</span>
        <span className="text-sm" title={error}>Auth Error</span>
        <button
          onClick={() => window.location.reload()}
          className="text-xs underline hover:no-underline"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center gap-2">
        <button
          onClick={() => login()}
          className="btn btn-primary flex items-center gap-2 px-4 py-2 transition-all hover:shadow-lg"
          aria-label="Sign in to Vimarsh for spiritual guidance"
        >
          <span>🙏</span>
          <span>Sign In</span>
        </button>
        
        {/* Quick access for development */}
        <div className="hidden md:flex items-center gap-1 ml-2">
          <span className="text-xs text-neutral-500">Dev:</span>
          <button
            onClick={() => login('seeker')}
            className="text-xs bg-neutral-100 hover:bg-neutral-200 px-2 py-1 rounded transition-colors"
            title="Quick login as Seeker"
          >
            🏹
          </button>
          <button
            onClick={() => login('devotee')}
            className="text-xs bg-neutral-100 hover:bg-neutral-200 px-2 py-1 rounded transition-colors"
            title="Quick login as Devotee"
          >
            🎶
          </button>
          <button
            onClick={() => login('scholar')}
            className="text-xs bg-neutral-100 hover:bg-neutral-200 px-2 py-1 rounded transition-colors"
            title="Quick login as Scholar"
          >
            📚
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <div className="text-sm">
        <span className="text-neutral-600">Namaste,</span>
        <span 
          className="font-medium text-earth-brown ml-1" 
          title={`${user?.email} • ${user?.sessionCount} sessions • Role: ${user?.role}`}
        >
          {user?.profilePicture} {user?.name}
        </span>
      </div>
      <button
        onClick={logout}
        className="btn btn-secondary text-sm px-3 py-1 transition-all hover:bg-neutral-200"
        aria-label="Sign out from Vimarsh"
      >
        Sign Out
      </button>
    </div>
  );
};

export default AuthenticationWrapper;
