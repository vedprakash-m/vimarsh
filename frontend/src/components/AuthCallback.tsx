import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMsal } from '@azure/msal-react';

/**
 * AuthCallback Component
 * Handles Microsoft Entra ID OAuth callback
 * Redirects users to main app after successful authentication
 */
const AuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const { instance } = useMsal();

  useEffect(() => {
    // Handle the authentication callback
    const handleCallback = async () => {
      try {
        // Explicitly process the redirect and acquire the auth result
        const accountsBefore = instance.getAllAccounts();
        console.log('🛠️ MSAL Debug → Accounts BEFORE handleRedirectPromise:', accountsBefore);

        const authResult = await instance.handleRedirectPromise();
        console.log('🛠️ MSAL Debug → Auth result from handleRedirectPromise:', authResult);

        const accountsAfter = instance.getAllAccounts();
        console.log('🛠️ MSAL Debug → Accounts AFTER handleRedirectPromise:', accountsAfter);

        // Determine account either from redirect result or existing cache
        let activeAccount = authResult?.account;
        if (!activeAccount) {
          const cached = instance.getAllAccounts();
          if (cached.length > 0) {
            activeAccount = cached[0];
          }
        }

        if (activeAccount) {
          instance.setActiveAccount(activeAccount);
          console.info('🔐 Authentication successful for', activeAccount.username);

          // Allow msal-react context to propagate account state before routing
          setTimeout(() => {
            navigate('/guidance', { replace: true });
          }, 250);
        } else {
          console.error('❌ Authentication completed but no account found');
          navigate('/', { replace: true });
        }
      } catch (error) {
        console.error('❌ MSAL handleRedirectPromise error:', error);
        navigate('/', { replace: true });
      }
    };

    handleCallback();
  }, [navigate, instance]);

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