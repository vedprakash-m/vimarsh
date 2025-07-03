import React from 'react';
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
