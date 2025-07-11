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
 * Redirects to landing page if unauthenticated
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isLoading } = useAuth();
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

  // TODO: Add admin role checking when requireAdmin is true
  // For now, just allow access if authenticated
  
  return <>{children}</>;
};

export default ProtectedRoute; 