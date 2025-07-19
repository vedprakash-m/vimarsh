import React, { useEffect } from 'react';
import { ArrowRight, LogIn } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import { useLanguage } from '../contexts/LanguageContext';

const LandingPage: React.FC = () => {
  const { isAuthenticated, account, login, error, clearError, refreshAuth } = useAuth();
  const navigate = useNavigate();
  const { t } = useLanguage();

  // Debug authentication state
  useEffect(() => {
    console.log('🔍 LandingPage Debug:', {
      isAuthenticated,
      account: account?.username,
      error
    });
    
    // Clear any auth errors on mount
    if (error) {
      console.warn('⚠️ Auth error detected:', error);
      clearError();
    }
  }, [isAuthenticated, account, error, clearError]);

  // Redirect authenticated users to guidance page
  useEffect(() => {
    console.log('🔄 LandingPage useEffect: isAuthenticated =', isAuthenticated);
    if (isAuthenticated && account) {
      console.log('✅ User is authenticated, redirecting to /guidance');
      navigate('/guidance');
    }
  }, [isAuthenticated, account, navigate]);

  // Handle sign-in with centralized auth
  const handleSignIn = async () => {
    try {
      await login();
    } catch (error) {
      console.error('❌ Sign-in error:', error);
    }
  };

  // Handle direct access for authenticated users
  const handleBeginJourney = () => {
    if (isAuthenticated) {
      navigate('/guidance');
    } else {
      handleSignIn();
    }
  };

  // Enhanced debug function using centralized auth
  const handleDebugAuth = async () => {
    console.log('🔧 Manual Auth Debug:', {
      isAuthenticated,
      account: account?.username,
      error,
      timestamp: new Date().toISOString()
    });

    // Try to refresh authentication state
    try {
      await refreshAuth();
      console.log('🔧 Auth state refreshed');
    } catch (refreshError) {
      console.error('🔧 Auth refresh failed:', refreshError);
    }
  };

  return (
    <div className="landing-page">
      {/* Minimal Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          {/* Sacred Symbol */}
          <div className="sacred-symbol">
            🕉
          </div>
          
          {/* Main Title */}
          <h1 className="main-title">
            Vimarsh
          </h1>
          
          {/* Subtitle */}
          <p className="subtitle">
            {t('welcomeMessage')}
          </p>
          
          {/* Sacred Quote */}
          <div className="sacred-quote">
            <p className="sanskrit">
              "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत"
            </p>
            <p className="translation">
              Whenever dharma declines, O Bharata...
            </p>
          </div>
          
          {/* Authentication-aware CTA */}
          {!isAuthenticated ? (
            <div className="auth-section">
              <p className="auth-message">
                {t('pleaseSignIn')}
              </p>
              <button 
                className="primary-cta"
                onClick={handleSignIn}
              >
                <LogIn size={20} />
                {t('signIn')}
              </button>
              
              {/* Debug button for development */}
              <button 
                className="debug-button"
                onClick={handleDebugAuth}
                style={{ marginTop: '10px', padding: '8px 16px', background: '#f0f0f0', border: '1px solid #ccc', borderRadius: '4px', fontSize: '12px' }}
              >
                🔧 Debug Auth State
              </button>
            </div>
          ) : (
            <div>
              <button 
                className="primary-cta"
                onClick={handleBeginJourney}
              >
                Begin Your Spiritual Journey
                <ArrowRight size={20} />
              </button>
              
              <button 
                className="debug-button"
                onClick={handleDebugAuth}
                style={{ marginTop: '10px', padding: '8px 16px', background: '#f0f0f0', border: '1px solid #ccc', borderRadius: '4px', fontSize: '12px' }}
              >
                🔧 Debug Auth State
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
