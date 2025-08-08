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
        height: '100vh',
        fontSize: '16px'
      }}>
        <div>🕉️ Loading...</div>
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
          height: '100vh',
          fontSize: '16px',
          textAlign: 'center',
          padding: '20px'
        }}>
          <h2>Access Denied</h2>
          <p>You need administrator privileges to access this page.</p>
          <p>Contact support if you believe this is an error.</p>
          <button 
            onClick={() => window.history.back()}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              background: '#FF6B35',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Go Back
          </button>
        </div>
      );
    }
    
    console.log('✅ ProtectedRoute: Admin access granted for:', adminUser.email);
  }
  
  return <>{children}</>;
};

export default ProtectedRoute; 