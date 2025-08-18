import React from 'react';
import { useAuth } from '../auth/AuthProvider';
import { useAdmin } from '../contexts/AdminProviderContext';
import { useMsal } from '@azure/msal-react';

/**
 * Debug component to help troubleshoot authentication and admin issues
 * This component can be temporarily added to any route to display auth state
 */
const DebugAuth: React.FC = () => {
  const { isAuthenticated, isLoading, account, error } = useAuth();
  const { user: adminUser, loading: adminLoading, error: adminError } = useAdmin();
  const { instance } = useMsal();
  
  const accounts = instance.getAllAccounts();
  const activeAccount = instance.getActiveAccount();

  return (
    <div style={{
      position: 'fixed',
      top: '1rem',
      right: '1rem',
      background: 'rgba(30, 41, 59, 0.95)',
      backdropFilter: 'blur(8px)',
      color: '#ffffff',
      padding: '1.5rem',
      borderRadius: '1rem',
      fontSize: '0.75rem',
      maxWidth: '320px',
      zIndex: 9999,
      border: '1px solid rgba(255, 255, 255, 0.1)',
      boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
      fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", monospace'
    }}>
      <h4 style={{ 
        margin: '0 0 1rem 0', 
        color: '#FF6B35',
        fontSize: '0.875rem',
        fontWeight: '600',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}>🔍 Auth Debug</h4>
      
      <div style={{ marginBottom: '1rem' }}>
        <strong style={{ color: '#F7931E' }}>Auth Provider:</strong><br/>
        • Authenticated: {isAuthenticated ? '✅' : '❌'}<br/>
        • Loading: {isLoading ? '⏳' : '✅'}<br/>
        • Account Email: <span style={{ color: '#94a3b8' }}>{account?.username || 'None'}</span><br/>
        • Error: <span style={{ color: error ? '#ef4444' : '#10b981' }}>{error || 'None'}</span>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <strong style={{ color: '#F7931E' }}>MSAL Instance:</strong><br/>
        • Total Accounts: <span style={{ color: '#94a3b8' }}>{accounts.length}</span><br/>
        • Active Account: <span style={{ color: '#94a3b8' }}>{activeAccount?.username || 'None'}</span><br/>
        • Home Account ID: <span style={{ color: '#94a3b8', fontSize: '0.6rem' }}>{activeAccount?.homeAccountId || 'None'}</span>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <strong style={{ color: '#F7931E' }}>Admin Provider:</strong><br/>
        • Admin User: <span style={{ color: '#94a3b8' }}>{adminUser?.email || 'None'}</span><br/>
        • Is Admin: {adminUser?.isAdmin ? '✅' : '❌'}<br/>
        • Role: <span style={{ color: '#94a3b8' }}>{adminUser?.role || 'None'}</span><br/>
        • Loading: {adminLoading ? '⏳' : '✅'}<br/>
        • Error: <span style={{ color: adminError ? '#ef4444' : '#10b981' }}>{adminError || 'None'}</span>
      </div>

      <div>
        <strong style={{ color: '#F7931E' }}>Current Domain:</strong><br/>
        <span style={{ color: '#94a3b8', fontSize: '0.7rem' }}>{window.location.origin}</span>
      </div>
    </div>
  );
};

export default DebugAuth;
