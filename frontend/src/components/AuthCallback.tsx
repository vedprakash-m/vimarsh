import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * AuthCallback Component
 * Handles Microsoft Entra ID OAuth callback
 * Redirects users to main app after successful authentication
 */
const AuthCallback: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Handle the authentication callback
    const handleCallback = async () => {
      try {
        // The MSAL library will automatically handle the callback
        // After successful authentication, redirect to the main guidance page
        console.log('🔐 Authentication callback processed');
        
        // Small delay to ensure auth state is updated
        setTimeout(() => {
          navigate('/guidance', { replace: true });
        }, 1000);
        
      } catch (error) {
        console.error('❌ Authentication callback error:', error);
        // Redirect to home page on error
        navigate('/', { replace: true });
      }
    };

    handleCallback();
  }, [navigate]);

  return (
    <div className="vimarsh-auth-callback">
      <div className="callback-container">
        <div className="callback-content">
          <div className="spiritual-loader">
            <div className="om-symbol">🕉️</div>
            <h2>Connecting you to divine wisdom...</h2>
            <p>Please wait while we complete your authentication.</p>
          </div>
        </div>
      </div>
      
      <style>{`
        .vimarsh-auth-callback {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, var(--sacred-saffron, #ff9933) 0%, var(--krishna-blue, #1e3a8a) 100%);
        }
        
        .callback-container {
          text-align: center;
          padding: 2rem;
          max-width: 400px;
        }
        
        .callback-content {
          background: rgba(255, 255, 255, 0.95);
          padding: 3rem 2rem;
          border-radius: 20px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
          backdrop-filter: blur(10px);
        }
        
        .spiritual-loader {
          color: var(--krishna-blue, #1e3a8a);
        }
        
        .om-symbol {
          font-size: 3rem;
          margin-bottom: 1rem;
          animation: pulse 2s infinite;
        }
        
        .spiritual-loader h2 {
          margin: 1rem 0;
          font-size: 1.5rem;
          font-weight: 600;
        }
        
        .spiritual-loader p {
          color: var(--text-secondary, #6b7280);
          font-size: 1rem;
        }
        
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.1); opacity: 0.8; }
        }
      `}</style>
    </div>
  );
};

export default AuthCallback; 