import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import './styles/spiritual-design-system.css';

// Components
import LandingPage from './components/LandingPage';
import CleanSpiritualInterface from './components/CleanSpiritualInterface';
import AuthCallback from './components/AuthCallback';
import ProtectedRoute from './components/ProtectedRoute';

// Context Providers
import { LanguageProvider } from './contexts/LanguageContext';

// MSAL Configuration
import { msalConfig } from './auth/msalConfig';

// Create MSAL instance for Vedprakash domain
const msalInstance = new PublicClientApplication(msalConfig);

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
    return (
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
        <p style={{ marginTop: '16px', fontSize: '14px' }}>Initializing spiritual guidance...</p>
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
  }
  return (
    <div className="App">
      <MsalProvider instance={msalInstance}>
        <LanguageProvider>
          <Router>
            <Routes>
              {/* Landing Page - Public Route */}
              <Route path="/" element={<LandingPage />} />
              
              {/* Authentication Callback - Public Route */}
              <Route path="/auth/callback" element={<AuthCallback />} />
              
              {/* Spiritual Guidance Interface - Protected Route */}
              <Route 
                path="/guidance" 
                element={
                  <ProtectedRoute>
                    <CleanSpiritualInterface />
                  </ProtectedRoute>
                } 
              />
              
              {/* Fallback Route - Redirect to Landing */}
              <Route path="*" element={<LandingPage />} />
            </Routes>
          </Router>
        </LanguageProvider>
      </MsalProvider>
    </div>
  );
}

export default App;
