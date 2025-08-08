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
      top: '10px',
      right: '10px',
      background: 'rgba(0, 0, 0, 0.8)',
      color: 'white',
      padding: '1rem',
      borderRadius: '8px',
      fontSize: '12px',
      maxWidth: '300px',
      zIndex: 9999
    }}>
      <h4 style={{ margin: '0 0 8px 0', color: '#fbbf24' }}>🔍 Auth Debug</h4>
      
      <div style={{ marginBottom: '8px' }}>
        <strong>Auth Provider:</strong><br/>
        • Authenticated: {isAuthenticated ? '✅' : '❌'}<br/>
        • Loading: {isLoading ? '⏳' : '✅'}<br/>
        • Account Email: {account?.username || 'None'}<br/>
        • Error: {error || 'None'}
      </div>

      <div style={{ marginBottom: '8px' }}>
        <strong>MSAL Instance:</strong><br/>
        • Total Accounts: {accounts.length}<br/>
        • Active Account: {activeAccount?.username || 'None'}<br/>
        • Home Account ID: {activeAccount?.homeAccountId || 'None'}
      </div>

      <div style={{ marginBottom: '8px' }}>
        <strong>Admin Provider:</strong><br/>
        • Admin User: {adminUser?.email || 'None'}<br/>
        • Is Admin: {adminUser?.isAdmin ? '✅' : '❌'}<br/>
        • Role: {adminUser?.role || 'None'}<br/>
        • Loading: {adminLoading ? '⏳' : '✅'}<br/>
        • Error: {adminError || 'None'}
      </div>

      <div>
        <strong>Current Domain:</strong><br/>
        {window.location.origin}
      </div>
    </div>
  );
};

export default DebugAuth;
