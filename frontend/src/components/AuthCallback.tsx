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

        // Validate final authentication state (no artificial delays)
        const accounts = instance.getAllAccounts();
        const activeAccount = instance.getActiveAccount();
        
        if (accounts.length === 0 || !activeAccount) {
          throw new Error('Authentication completed but no valid account found');
        }

        console.log('✅ Multi-domain authentication successful');
        console.log('👤 Authenticated user:', activeAccount.username);
        console.log('🔄 Redirecting to /guidance');
        
        setProcessing(false);
        
        // Navigate immediately — no artificial delays needed
        navigate('/guidance', { replace: true });

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
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
      padding: '2rem'
    }}>
      <div style={{
        background: '#ffffff',
        borderRadius: '1.5rem',
        padding: '3rem',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
        border: '1px solid #e2e8f0',
        textAlign: 'center',
        maxWidth: '500px',
        width: '100%'
      }}>
        <div>
          {processing ? (
            <div>
              <div style={{
                fontSize: '4rem',
                marginBottom: '1.5rem',
                animation: 'pulse 2s ease-in-out infinite'
              }}>💭</div>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: '#1e293b',
                marginBottom: '1rem',
                margin: '0 0 1rem 0'
              }}>Connecting you to timeless wisdom...</h2>
              <p style={{
                color: '#64748b',
                marginBottom: '2rem',
                lineHeight: '1.6',
                margin: '0 0 2rem 0'
              }}>Preparing your personalized guidance experience.</p>
              <div style={{
                width: '40px',
                height: '40px',
                border: '3px solid #f1f5f9',
                borderTop: '3px solid #FF6B35',
                borderRadius: '50%',
                margin: '0 auto',
                animation: 'spin 1s linear infinite'
              }}></div>
            </div>
          ) : error ? (
            <div>
              <div style={{
                fontSize: '3rem',
                marginBottom: '1.5rem',
                color: '#ef4444'
              }}>⚠️</div>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: '#1e293b',
                marginBottom: '1rem',
                margin: '0 0 1rem 0'
              }}>Authentication Issue</h2>
              <p style={{
                color: '#64748b',
                marginBottom: '1rem',
                lineHeight: '1.6',
                margin: '0 0 1rem 0'
              }}>{error}</p>
              <p style={{
                color: '#64748b',
                lineHeight: '1.6',
                margin: 0
              }}>Redirecting you back to the home page...</p>
            </div>
          ) : (
            <div>
              <div style={{
                fontSize: '3rem',
                marginBottom: '1.5rem',
                color: '#10b981'
              }}>✅</div>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: '#1e293b',
                marginBottom: '1rem',
                margin: '0 0 1rem 0'
              }}>Authentication Successful</h2>
              <p style={{
                color: '#64748b',
                lineHeight: '1.6',
                margin: 0
              }}>Approaching Wisdom Without Boundaries...</p>
            </div>
          )}
        </div>
      </div>
      
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.7; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.05); }
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default AuthCallback;

