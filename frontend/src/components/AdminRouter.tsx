import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';

// Lazy load admin components for better bundle splitting
const AdminDashboard = lazy(() => import('./admin/AdminDashboard'));
const AdminHealth = lazy(() => import('./admin/AdminHealth'));

// Lightweight loading component
const AdminLoadingSpinner: React.FC = () => (
  <div className="vimarsh-admin-loading">
    <div className="loading-spinner" />
    <p>Loading admin interface...</p>
    <style dangerouslySetInnerHTML={{
      __html: `
        .vimarsh-admin-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 200px;
          color: var(--sacred-saffron, #FF6B35);
          font-family: 'Inter', system-ui, sans-serif;
        }
        
        .loading-spinner {
          width: 32px;
          height: 32px;
          border: 3px solid transparent;
          border-top: 3px solid var(--sacred-saffron, #FF6B35);
          border-radius: 50%;
          animation: vimarsh-spin 1s linear infinite;
        }
        
        .vimarsh-admin-loading p {
          margin-top: 12px;
          font-size: 14px;
          opacity: 0.8;
        }
        
        @keyframes vimarsh-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `
    }} />
  </div>
);

/**
 * Optimized Admin Router with lazy loading for better performance
 * This component implements code splitting to reduce initial bundle size
 */
const AdminRouter: React.FC = () => {
  return (
    <Suspense fallback={<AdminLoadingSpinner />}>
      <Routes>
        {/* Admin Dashboard - Lazy loaded */}
        <Route 
          path="/dashboard" 
          element={<AdminDashboard />} 
        />
        
        {/* Admin Health Monitoring - Lazy loaded */}
        <Route 
          path="/health" 
          element={<AdminHealth />} 
        />
        
        {/* Default admin route */}
        <Route 
          path="/" 
          element={<AdminDashboard />} 
        />
      </Routes>
    </Suspense>
  );
};

export default AdminRouter;
