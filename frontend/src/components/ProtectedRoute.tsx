import React, { useRef, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import { useAdmin } from '../contexts/AdminProviderContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

// Circuit breaker to prevent rapid-fire redirects during auth transitions
let lastRedirectTime = 0;
let redirectCount = 0;
const REDIRECT_COOLDOWN_MS = 1000; // 1 second between redirects
const MAX_REDIRECTS_PER_MINUTE = 3;
const REDIRECT_WINDOW_MS = 60000; // 1 minute

/**
 * ProtectedRoute Component
 * Ensures user is authenticated via centralized AuthProvider before accessing protected content
 * Redirects to landing page if unauthenticated or unauthorized
 * Includes circuit breaker to prevent infinite redirect loops during auth state transitions
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isLoading, account } = useAuth();
  const { user: adminUser, loading: adminLoading } = useAdmin();
  const location = useLocation();
  const mountTimeRef = useRef(Date.now());

  // Show loading while authentication state is being determined
  if (isLoading || (requireAdmin && adminLoading)) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
      }}>
        <div style={{
          textAlign: 'center',
          background: '#ffffff',
          padding: '2rem',
          borderRadius: '1rem',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{
            fontSize: '3rem',
            marginBottom: '1rem',
            animation: 'pulse 2s ease-in-out infinite'
          }}>🕉️</div>
          <div style={{
            fontSize: '1rem',
            color: '#64748b',
            fontWeight: '500'
          }}>Loading sacred wisdom...</div>
          <style>{`
            @keyframes pulse {
              0%, 100% { opacity: 0.7; transform: scale(1); }
              50% { opacity: 1; transform: scale(1.05); }
            }
          `}</style>
        </div>
      </div>
    );
  }

  // Circuit breaker: Prevent rapid-fire redirects during auth state transitions
  useEffect(() => {
    const now = Date.now();
    if (now - mountTimeRef.current < 500) {
      // Component just mounted, give auth state time to stabilize
      return;
    }
  }, []);

  if (!isAuthenticated) {
    const now = Date.now();
    const timeSinceLastRedirect = now - lastRedirectTime;
    
    // Reset counter if outside window
    if (timeSinceLastRedirect > REDIRECT_WINDOW_MS) {
      redirectCount = 0;
    }
    
    // Circuit breaker: Prevent redirect loops
    if (timeSinceLastRedirect < REDIRECT_COOLDOWN_MS) {
      console.warn('⚠️ ProtectedRoute: Redirect cooldown active, waiting for auth state to stabilize...');
      return (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
        }}>
          <div style={{
            textAlign: 'center',
            background: '#ffffff',
            padding: '2rem',
            borderRadius: '1rem',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{
              fontSize: '3rem',
              marginBottom: '1rem',
              animation: 'pulse 2s ease-in-out infinite'
            }}>🕉️</div>
            <div style={{
              fontSize: '1rem',
              color: '#64748b',
              fontWeight: '500'
            }}>Synchronizing authentication...</div>
            <style>{`
              @keyframes pulse {
                0%, 100% { opacity: 0.7; transform: scale(1); }
                50% { opacity: 1; transform: scale(1.05); }
              }
            `}</style>
          </div>
        </div>
      );
    }
    
    // Track redirects
    redirectCount++;
    lastRedirectTime = now;
    
    if (redirectCount > MAX_REDIRECTS_PER_MINUTE) {
      console.error('🚨 ProtectedRoute: Excessive redirects detected! Circuit breaker triggered.');
      return (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
        }}>
          <div style={{
            textAlign: 'center',
            background: '#ffffff',
            padding: '2rem',
            borderRadius: '1rem',
            boxShadow: '0 10px 30px rgba(239, 68, 68, 0.2)',
            border: '1px solid #fecaca',
            maxWidth: '400px'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
            <div style={{
              fontSize: '1.25rem',
              color: '#dc2626',
              fontWeight: '600',
              marginBottom: '0.5rem'
            }}>Authentication Loop Detected</div>
            <div style={{
              fontSize: '0.875rem',
              color: '#64748b',
              marginBottom: '1rem'
            }}>Please refresh the page or clear your browser cache and try again.</div>
            <button
              onClick={() => window.location.href = '/'}
              style={{
                padding: '0.75rem 1.5rem',
                background: '#dc2626',
                color: '#ffffff',
                border: 'none',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = '#b91c1c'}
              onMouseLeave={(e) => e.currentTarget.style.background = '#dc2626'}
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }
    
    // Store the attempted location for post-login redirect
    console.log('🔐 ProtectedRoute: User not authenticated, redirecting to landing page');
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  // Check admin requirements using AdminProvider
  if (requireAdmin) {
    console.log('🔍 ProtectedRoute: Checking admin requirements', { adminUser: adminUser?.email, isAdmin: adminUser?.isAdmin });
    
    if (!adminUser || !adminUser.isAdmin) {
      console.warn('⚠️ ProtectedRoute: Admin access denied for user:', account?.username);
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
          padding: '2rem'
        }}>
          <div style={{
            textAlign: 'center',
            background: '#ffffff',
            padding: '3rem',
            borderRadius: '1.5rem',
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e2e8f0',
            maxWidth: '500px',
            width: '100%'
          }}>
            <div style={{
              fontSize: '4rem',
              marginBottom: '1.5rem'
            }}>🚫</div>
            <h2 style={{
              fontSize: '1.5rem',
              fontWeight: '700',
              color: '#1e293b',
              marginBottom: '1rem',
              margin: '0 0 1rem 0'
            }}>Access Denied</h2>
            <p style={{
              color: '#64748b',
              marginBottom: '1rem',
              lineHeight: '1.6',
              margin: '0 0 1rem 0'
            }}>You need administrator privileges to access this page.</p>
            <p style={{
              color: '#64748b',
              marginBottom: '2rem',
              lineHeight: '1.6',
              margin: '0 0 2rem 0'
            }}>Contact support if you believe this is an error.</p>
            <button 
              onClick={() => window.history.back()}
              style={{
                padding: '0.75rem 2rem',
                background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '0.75rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '600',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 12px rgba(255, 107, 53, 0.3)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 16px rgba(255, 107, 53, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(255, 107, 53, 0.3)';
              }}
            >
              Go Back
            </button>
          </div>
        </div>
      );
    }
    
    console.log('✅ ProtectedRoute: Admin access granted for:', adminUser.email);
  }
  
  return <>{children}</>;
};

export default ProtectedRoute; 