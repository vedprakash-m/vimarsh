import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';

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
  const location = useLocation();

  // Show loading while authentication state is being determined
  if (isLoading) {
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
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  // Check admin requirements
  if (requireAdmin) {
    const userEmail = account?.username || account?.name || '';
    const isAdmin = userEmail.includes('admin') || userEmail.includes('vedprakash@outlook.com');
    
    if (!isAdmin) {
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
  }
  
  return <>{children}</>;
};

export default ProtectedRoute; 