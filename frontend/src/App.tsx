import React, { useEffect, useState, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import './styles/spiritual-design-system.css';
import './styles/domain-themes.css';

// Lazy load main components for better bundle splitting
const LandingPage = lazy(() => import('./components/LandingPage'));
const GuidanceInterface = lazy(() => import('./components/GuidanceInterface'));

// Keep lightweight components as regular imports
import AuthCallback from './components/AuthCallback';
import ProtectedRoute from './components/ProtectedRoute';
import { DomainThemeManager } from './components/DomainThemeManager';

// Context Providers
import { LanguageProvider } from './contexts/LanguageContext';
import { PersonalityProvider } from './contexts/PersonalityContext';
import { AuthProvider } from './auth/AuthProvider';
import { AdminProvider } from './contexts/AdminProviderContext';
import { AppLoadingProvider } from './contexts/AppLoadingContext';
import AdminDashboard from './components/admin/AdminDashboard';

// MSAL Configuration
import { msalConfig } from './auth/msalConfig';

// Create MSAL instance for Vedprakash domain
const msalInstance = new PublicClientApplication(msalConfig);

// Lightweight loading component for lazy-loaded routes
const SpiritualLoadingSpinner: React.FC = () => (
  <div style={{
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    background: 'linear-gradient(135deg, #FFF8E1 0%, #FFE0B2 100%)',
    color: '#5D4037',
    fontFamily: 'Inter, system-ui, sans-serif'
  }}>
    <div style={{
      width: '40px',
      height: '40px',
      border: '3px solid #FF6B35',
      borderTop: '3px solid transparent',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite'
    }}></div>
    <p style={{ marginTop: '16px', fontSize: '14px' }}>Loading wisdom guidance...</p>
    <style dangerouslySetInnerHTML={{
      __html: `
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `
    }} />
  </div>
);

function App() {
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Initialize MSAL before rendering
    const initializeMsal = async () => {
      try {
        await msalInstance.initialize();
        console.log('✅ MSAL initialized successfully');
        setIsInitialized(true);
      } catch (error) {
        console.error('❌ MSAL initialization failed:', error);
        setIsInitialized(true); // Still render the app even if MSAL fails
      }
    };

    initializeMsal();
  }, []);

  // Don't render until MSAL is initialized
  if (!isInitialized) {
    return <SpiritualLoadingSpinner />;
  }
  
  return (
    <div className="App">
      <MsalProvider instance={msalInstance}>
        <AuthProvider>
          <AdminProvider>
            <PersonalityProvider>
              <AppLoadingProvider>
                <LanguageProvider>
                <DomainThemeManager />
                <Router>
                  <Suspense fallback={<SpiritualLoadingSpinner />}>
                    <Routes>
                    {/* Landing Page - Public Route */}
                    <Route path="/" element={<LandingPage />} />
                    
                    {/* Authentication Callback - Public Route */}
                    <Route path="/auth/callback" element={<AuthCallback />} />
                    
                                      {/* Guidance Interface - Protected Route */}
                    <Route 
                    path="/guidance" 
                    element={
                      <ProtectedRoute>
                        <GuidanceInterface />
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Admin Dashboard - Protected Route with Admin Requirement */}
                  <Route 
                    path="/admin" 
                    element={
                      <ProtectedRoute requireAdmin={true}>
                        <AdminDashboard />
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Fallback Route - Redirect to Landing */}
                  <Route path="*" element={<LandingPage />} />
                </Routes>
              </Suspense>
            </Router>
          </LanguageProvider>
        </AppLoadingProvider>
        </PersonalityProvider>
        </AdminProvider>
      </AuthProvider>
    </MsalProvider>
    </div>
  );
}

export default App;
