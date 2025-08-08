import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMsal } from '@azure/msal-react';
import { useAuth } from '../auth/AuthProvider';
import SmartAuthFlow from '../auth/SmartAuthFlow';

/**
 * AuthCallback Component
 * Handles Microsoft Entra ID OAuth callback with centralized state management
 * Only responsible for processing the redirect, AuthProvider manages state
 */
const AuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const { instance } = useMsal();
  const { refreshAuth } = useAuth();
  const [processing, setProcessing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [smartAuth] = useState(() => new SmartAuthFlow(instance));

  useEffect(() => {
    // Handle the multi-domain authentication callback using SmartAuthFlow
    const handleCallback = async () => {
      try {
        const currentDomain = window.location.origin;
        
        console.log('🔐 Processing multi-domain authentication callback');
        console.log('🌐 Current domain:', currentDomain);
        
        // Import domain validation function
        const { isValidProductionDomain } = require('../config/environment');
        
        // Validate we're on a supported domain
        if (!isValidProductionDomain(currentDomain) && !currentDomain.includes('localhost')) {
          throw new Error(`Authentication not supported on domain: ${currentDomain}`);
        }
        
        console.log('✅ Valid production domain confirmed:', currentDomain);
        
        // Use SmartAuthFlow to handle the redirect callback
        const result = await smartAuth.handleRedirectCallback();
        
        if (result.success) {
          if (result.account) {
            console.log('✅ AuthCallback: Account processed successfully');
            console.log('👤 Account:', result.account.username);
          } else if (result.noResult) {
            console.log('ℹ️ AuthCallback: No redirect result found');
          }
        } else {
          throw new Error(result.error || 'Multi-domain authentication callback failed');
        }

        console.log('✅ Callback processed successfully');

        // Refresh the centralized auth state
        await refreshAuth();
        console.log('✅ AuthCallback: Auth state refreshed');

        // Wait for state to settle, then validate authentication
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Validate final authentication state
        const accounts = instance.getAllAccounts();
        const activeAccount = instance.getActiveAccount();
        
        if (accounts.length === 0 || !activeAccount) {
          throw new Error('Authentication completed but no valid account found');
        }

        console.log('✅ Multi-domain authentication successful');
        console.log('👤 Authenticated user:', activeAccount.username);
        console.log('🔄 Redirecting to /guidance');
        
        setProcessing(false);
        
        // Navigate to guidance page after successful processing and validation
        // Add a longer delay to ensure all contexts have time to initialize
        setTimeout(() => {
          navigate('/guidance', { replace: true });
        }, 1200);

      } catch (error) {
        console.error('❌ Multi-domain authentication callback failed:', error);
        const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
        setError(errorMessage);
        setProcessing(false);
        
        // Redirect with error context after showing error for a moment
        setTimeout(() => {
          const errorParams = new URLSearchParams({
            auth_error: 'multi_domain_callback_failed',
            message: errorMessage,
            domain: window.location.origin
          });
          console.log('🔄 AuthCallback: Redirecting to home with error context');
          navigate(`/?${errorParams.toString()}`, { replace: true });
        }, 3000);
      }
    };

    handleCallback();
  }, [navigate, smartAuth, refreshAuth, instance]);

  return (
    <div className="vimarsh-auth-callback">
      <div className="callback-container">
        <div className="callback-content">
          {processing ? (
            <div className="spiritual-loader">
              <div className="om-symbol">🕉️</div>
              <h2>Connecting you to divine wisdom...</h2>
              <p>Please wait while we complete your authentication.</p>
              <div className="loading-spinner"></div>
            </div>
          ) : error ? (
            <div className="auth-error">
              <div className="error-symbol">⚠️</div>
              <h2>Authentication Issue</h2>
              <p>{error}</p>
              <p>Redirecting you back to the home page...</p>
            </div>
          ) : (
            <div className="auth-success">
              <div className="success-symbol">✅</div>
              <h2>Authentication Successful</h2>
              <p>Taking you to your spiritual guidance...</p>
            </div>
          )}
        </div>
      </div>
      
      <style>{`
        .vimarsh-auth-callback {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, var(--sacred-saffron, #ff9933) 0%, var(--krishna-blue, #1e3a8a) 100%);
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .callback-container {
          text-align: center;
          padding: 2rem;
          max-width: 500px;
          width: 100%;
        }
        
        .callback-content {
          background: rgba(255, 255, 255, 0.95);
          padding: 3rem 2rem;
          border-radius: 20px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
          backdrop-filter: blur(10px);
        }
        
        .spiritual-loader, .auth-error, .auth-success {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }
        
        .om-symbol, .error-symbol, .success-symbol {
          font-size: 3rem;
          margin-bottom: 0.5rem;
          animation: pulse 2s infinite;
        }
        
        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 3px solid #f3f3f3;
          border-top: 3px solid var(--krishna-blue, #1e3a8a);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-top: 1rem;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .spiritual-loader {
          color: var(--krishna-blue, #1e3a8a);
        }
        
        .auth-error {
          color: #dc2626;
        }
        
        .auth-success {
          color: #059669;
        }
        
        h2 {
          color: #374151;
          margin: 0;
          font-size: 1.5rem;
          font-weight: 600;
        }
        
        p {
          color: #6b7280;
          margin: 0;
          line-height: 1.5;
        }
        
        .auth-error h2 {
          color: #dc2626;
        }
        
        .auth-success h2 {
          color: #059669;
        }
      `}</style>
    </div>
  );
};

export default AuthCallback;
