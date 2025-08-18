import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import { useAdmin } from '../contexts/AdminProviderContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

/**
 * ProtectedRoute Component
 * Ensures user is authenticated via centralized AuthProvider before accessing protected content
 * Redirects to landing page if unauthenticated or unauthorized
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isLoading, account } = useAuth();
  const { user: adminUser, loading: adminLoading } = useAdmin();
  const location = useLocation();

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

  if (!isAuthenticated) {
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