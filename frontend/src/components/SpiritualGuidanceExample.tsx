/**
 * Example React Component Integration with Vimarsh Authentication
 * 
 * This example shows how to integrate the unified authentication system
 * into React components for both authenticated and anonymous access.
 */

import React, { useState, useEffect } from 'react';
import { authService, AuthUser, getAuthHeaders } from '../auth/authService';

interface SpiritualGuidanceProps {
  question?: string;
}

export const SpiritualGuidanceComponent: React.FC<SpiritualGuidanceProps> = ({ question }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setIsLoading(true);
      const currentUser = await authService.getUser();
      setUser(currentUser);
    } catch (error: any) {
      console.error('Auth initialization failed:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const loggedInUser = await authService.login();
      setUser(loggedInUser);
    } catch (error: any) {
      console.error('Login failed:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      setUser(null);
    } catch (error: any) {
      console.error('Logout failed:', error);
      setError(error.message);
    }
  };

  const makeAuthenticatedAPICall = async (query: string) => {
    try {
      const headers = await getAuthHeaders();
      
      const response = await fetch('/api/spiritual-guidance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers // Includes Authorization: Bearer <token> if authenticated
        },
        body: JSON.stringify({ 
          query, 
          language: user?.vedProfile.preferences.language || 'English'
        })
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  };

  if (isLoading) {
    return (
      <div className="spiritual-loading">
        <div className="lotus-spinner">🪷</div>
        <p>Connecting to divine wisdom...</p>
      </div>
    );
  }

  return (
    <div className="spiritual-guidance-container">
      
      {/* Authentication Status */}
      <div className="auth-status">
        {user ? (
          <div className="authenticated-user">
            <div className="user-info">
              <span className="profile-picture">{user.profilePicture || '🙏'}</span>
              <span className="user-name">Welcome, {user.name}</span>
              <span className="subscription-tier">
                {user.vedProfile.subscriptionTier === 'premium' && '⭐'}
                {user.vedProfile.subscriptionTier === 'enterprise' && '👑'}
              </span>
            </div>
            <button onClick={handleLogout} className="logout-btn">
              Sign Out
            </button>
          </div>
        ) : (
          <div className="anonymous-user">
            <p>🕉️ Explore spiritual wisdom anonymously</p>
            <button onClick={handleLogin} className="login-btn">
              Sign In for Personalized Guidance
            </button>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="auth-error">
          <p>⚠️ {error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      {/* Feature Access Based on Authentication */}
      <div className="features">
        
        {/* Always Available: Basic Spiritual Guidance */}
        <section className="basic-features">
          <h2>🌟 Spiritual Guidance</h2>
          <p>Ask Lord Krishna for wisdom and guidance</p>
          {/* Basic spiritual guidance component here */}
        </section>

        {/* Authenticated Features */}
        {user && (
          <section className="authenticated-features">
            <h2>✨ Personalized Experience</h2>
            
            {/* User Preferences */}
            <div className="user-preferences">
              <p><strong>Language:</strong> {user.vedProfile.preferences.language}</p>
              <p><strong>Spiritual Interests:</strong> {user.spiritualInterests?.join(', ')}</p>
              <p><strong>Journey Since:</strong> {user.joinedDate}</p>
            </div>

            {/* Premium Features */}
            {user.vedProfile.subscriptionTier !== 'free' && (
              <div className="premium-features">
                <h3>🎁 Premium Features</h3>
                <ul>
                  <li>Extended conversation history</li>
                  <li>Priority spiritual guidance</li>
                  <li>Advanced meditation recommendations</li>
                  {user.vedProfile.subscriptionTier === 'enterprise' && (
                    <li>Expert review access</li>
                  )}
                </ul>
              </div>
            )}

            {/* Cross-App Integration */}
            <div className="cross-app-features">
              <h3>🔗 Your Vedprakash Journey</h3>
              <p>Connected Apps: {user.vedProfile.appsEnrolled.join(', ')}</p>
              <div className="app-links">
                {user.vedProfile.appsEnrolled.includes('sutra') && (
                  <a href="https://sutra.vedprakash.net" className="app-link">
                    📿 Continue in Sutra
                  </a>
                )}
                {user.vedProfile.appsEnrolled.includes('vigor') && (
                  <a href="https://vigor.vedprakash.net" className="app-link">
                    💪 Continue in Vigor
                  </a>
                )}
              </div>
            </div>
          </section>
        )}

        {/* Call-to-Action for Anonymous Users */}
        {!user && (
          <section className="cta-section">
            <div className="benefits">
              <h3>🌸 Join Your Spiritual Community</h3>
              <ul>
                <li>💾 Save your spiritual conversations</li>
                <li>📈 Track your spiritual growth</li>
                <li>🔄 Access across all Vedprakash apps</li>
                <li>🎯 Personalized guidance recommendations</li>
              </ul>
              <button onClick={handleLogin} className="cta-button">
                Begin Your Journey
              </button>
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

/**
 * Higher-Order Component for Authentication Requirements
 * 
 * Use this to wrap components that require authentication
 */
export const withAuth = <P extends object>(Component: React.ComponentType<P>) => {
  return (props: P) => {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
      const checkAuth = async () => {
        try {
          const currentUser = await authService.getUser();
          if (!currentUser) {
            await authService.login();
            const loggedInUser = await authService.getUser();
            setUser(loggedInUser);
          } else {
            setUser(currentUser);
          }
        } catch (error) {
          console.error('Authentication required:', error);
        } finally {
          setIsLoading(false);
        }
      };

      checkAuth();
    }, []);

    if (isLoading) {
      return <div>🪷 Authenticating...</div>;
    }

    if (!user) {
      return (
        <div className="auth-required">
          <h2>🔐 Authentication Required</h2>
          <p>Please sign in to access this feature</p>
          <button onClick={() => authService.login()}>
            Sign In
          </button>
        </div>
      );
    }

    return <Component {...props} user={user} />;
  };
};

/**
 * Custom Hook for Authentication State
 * 
 * Use this in functional components for authentication state management
 */
export const useAuth = () => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const currentUser = await authService.getUser();
        setUser(currentUser);
        setIsAuthenticated(!!currentUser);
      } catch (error) {
        console.error('Auth check failed:', error);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async () => {
    try {
      setIsLoading(true);
      const loggedInUser = await authService.login();
      setUser(loggedInUser);
      setIsAuthenticated(true);
      return loggedInUser;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  };

  const getToken = async () => {
    try {
      return await authService.getToken();
    } catch (error) {
      console.error('Token acquisition failed:', error);
      throw error;
    }
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    getToken
  };
};

export default SpiritualGuidanceComponent;
