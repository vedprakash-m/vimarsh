import React, { useEffect, useState, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import './styles/vimarsh-design-system.css';
import './styles/spiritual-design-system.css';
import './styles/domain-themes.css';

// PWA utilities
import { pwaManager } from './utils/pwa';

// Lazy load main components for better bundle splitting
const LandingPage = lazy(() => import('./components/LandingPage'));
const GuidanceInterface = lazy(() => import('./components/GuidanceInterface'));
const ShareView = lazy(() => import('./pages/ShareView'));
const WisdomArchive = lazy(() => import('./pages/WisdomArchive'));
const MemoryDashboard = lazy(() => import('./components/MemoryDashboard'));
const ProgressDashboard = lazy(() => import('./pages/ProgressDashboard'));
const UserSettings = lazy(() => import('./pages/UserSettings'));
const WisdomInterface = lazy(() => import('./components/WisdomInterface'));

// Check feature flag for rendering
const useGamification = process.env.REACT_APP_ENABLE_GAMIFICATION !== 'false';

// Memory Dashboard Page Wrapper (handles route-based rendering)
const MemoryDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  return <MemoryDashboard isOpen={true} onClose={() => navigate(-1)} />;
};

// Keep lightweight components as regular imports
import AuthCallback from './components/AuthCallback';
import ProtectedRoute from './components/ProtectedRoute';
import { DomainThemeManager } from './components/DomainThemeManager';

// Context Providers
import { LanguageProvider } from './contexts/LanguageContext';
import { PersonalityProvider } from './contexts/PersonalityContext';
import { MemoryProvider } from './contexts/MemoryContext';
import { EngagementProvider } from './contexts/EngagementContext';
import { SettingsProvider } from './contexts/SettingsContext';
import { AuthProvider } from './auth/AuthProvider';
import { AdminProvider } from './contexts/AdminProviderContext';
import { AppLoadingProvider } from './contexts/AppLoadingContext';
import AdminDashboard from './components/admin/AdminDashboard';

// Engagement Tour - now rendered inside GuidanceInterface only (auth-gated)
// import EngagementTour, { useEngagementTour } from './components/engagement/EngagementTour';

// EngagementTourWrapper removed from global scope — now rendered inside GuidanceInterface
// where it only shows for authenticated users on the /guidance route

// MSAL Configuration
import { msalConfig } from './auth/msalConfig';

// Create MSAL instance for Vedprakash domain
const msalInstance = new PublicClientApplication(msalConfig);

// Apple-inspired loading component for lazy-loaded routes
const AppleLoadingSpinner: React.FC = () => (
  <div style={{
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    background: '#ffffff',
    color: '#1d1d1f',
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
  }}>
    <div style={{
      width: '32px',
      height: '32px',
      border: '2px solid #f3f4f6',
      borderTop: '2px solid #f97316',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite'
    }}></div>
    <p style={{ 
      marginTop: '16px', 
      fontSize: '14px',
      color: '#6e6e73',
      fontWeight: 500
    }}>Loading wisdom guidance...</p>
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
        
        // Initialize PWA functionality after MSAL
        console.log('✅ PWA initialized successfully');
        
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
    return <AppleLoadingSpinner />;
  }
  
  return (
    <div className="App">
      <MsalProvider instance={msalInstance}>
        <AuthProvider>
          <AdminProvider>
            <PersonalityProvider>
              <MemoryProvider>
              <EngagementProvider>
              <SettingsProvider>
              <AppLoadingProvider>
                <LanguageProvider>
                <DomainThemeManager />
                <Router>
                  <Suspense fallback={<AppleLoadingSpinner />}>
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
                        {useGamification ? <GuidanceInterface /> : <WisdomInterface />}
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
                  
                  {/* Share View - Public Route for shared wisdom */}
                  <Route path="/share/:shareId" element={<ShareView />} />
                  <Route path="/share" element={<ShareView />} />
                  
                  {/* Wisdom Archive - Protected Route */}
                  <Route 
                    path="/wisdom/archive" 
                    element={
                      <ProtectedRoute>
                        <WisdomArchive />
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Memory Dashboard - Protected Route */}
                  <Route 
                    path="/memory" 
                    element={
                      <ProtectedRoute>
                        <MemoryDashboardPage />
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Progress Dashboard - Protected Route */}
                  <Route 
                    path="/progress" 
                    element={
                      <ProtectedRoute>
                        <ProgressDashboard />
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Settings Page - Protected Route */}
                  <Route 
                    path="/settings" 
                    element={
                      <ProtectedRoute>
                        <UserSettings />
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
        </SettingsProvider>
        </EngagementProvider>
        </MemoryProvider>
        </PersonalityProvider>
        </AdminProvider>
      </AuthProvider>
    </MsalProvider>
    </div>
  );
}

export default App;
