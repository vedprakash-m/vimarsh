import React, { useEffect } from 'react';
import { ArrowRight, LogIn } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useIsAuthenticated, useMsal } from '@azure/msal-react';
import { useLanguage } from '../contexts/LanguageContext';

const LandingPage: React.FC = () => {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const navigate = useNavigate();
  const { t } = useLanguage();

  // Redirect authenticated users to guidance page
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/guidance');
    }
  }, [isAuthenticated, navigate]);

  // Handle sign-in with MSAL
  const handleSignIn = async () => {
    try {
      await instance.loginRedirect({
        scopes: ['openid', 'profile', 'email'],
        prompt: 'select_account'
      });
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
            </div>
          ) : (
            <button 
              className="primary-cta"
              onClick={handleBeginJourney}
            >
              Begin Your Spiritual Journey
              <ArrowRight size={20} />
            </button>
          )}
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
