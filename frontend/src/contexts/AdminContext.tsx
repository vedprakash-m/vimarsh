import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useMsal } from '@azure/msal-react';
import { adminService } from '../services/adminService';

// Admin role types
export enum UserRole {
  USER = 'user',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin'
}

export interface UserPermissions {
  can_view_cost_dashboard: boolean;
  can_manage_users: boolean;
  can_block_users: boolean;
  can_view_system_costs: boolean;
  can_configure_budgets: boolean;
  can_access_admin_endpoints: boolean;
  can_override_budget_limits: boolean;
  can_manage_emergency_controls: boolean;
}

export interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  permissions: UserPermissions;
  isAdmin: boolean;
  isSuperAdmin: boolean;
}

interface AdminContextType {
  user: AdminUser | null;
  loading: boolean;
  error: string | null;
  checkAdminStatus: () => Promise<void>;
  refreshUserData: () => Promise<void>;
}

const AdminContext = createContext<AdminContextType | undefined>(undefined);

export const useAdmin = () => {
  const context = useContext(AdminContext);
  if (context === undefined) {
    throw new Error('useAdmin must be used within an AdminProvider');
  }
  return context;
};

interface AdminProviderProps {
  children: ReactNode;
}

export const AdminProvider: React.FC<AdminProviderProps> = ({ children }) => {
  const { accounts, instance } = useMsal();
  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cache admin status for faster subsequent loads
  const getCachedAdminStatus = (userEmail: string): AdminUser | null => {
    try {
      const cachedData = localStorage.getItem(`vimarsh_admin_${userEmail}`);
      if (cachedData) {
        const parsed = JSON.parse(cachedData);
        const cacheAge = Date.now() - parsed.timestamp;
        // Use cache if less than 3 minutes old
        if (cacheAge < 3 * 60 * 1000) {
          console.log('⚡ AdminContext: Using cached admin status');
          return parsed.user;
        }
      }
    } catch (e) {
      console.warn('⚠️ AdminContext: Invalid cache');
    }
    return null;
  };

  const cacheAdminStatus = (userEmail: string, adminUser: AdminUser) => {
    try {
      const cacheData = {
        user: adminUser,
        timestamp: Date.now()
      };
      localStorage.setItem(`vimarsh_admin_${userEmail}`, JSON.stringify(cacheData));
      console.log('💾 AdminContext: Cached admin status for', userEmail);
    } catch (e) {
      console.warn('⚠️ AdminContext: Failed to cache admin status');
    }
  };

  const checkAdminStatus = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get the current account from MSAL
      const account = accounts[0];
      if (!account) {
        setUser(null);
        setLoading(false);
        return;
      }

      const userEmail = account.username;
      console.log('👤 AdminContext: Quick admin check for user:', userEmail);

      // Check cache first for instant admin button display
      const cachedUser = getCachedAdminStatus(userEmail);
      if (cachedUser) {
        setUser(cachedUser);
        setLoading(false);
        return;
      }

      // No cache, perform full check
      try {
        console.log('🔐 Checking admin status for:', userEmail);
        
        let accessToken: string | undefined;
        
        try {
          console.log('🔄 Attempting silent token acquisition...');
          const tokenResponse = await instance.acquireTokenSilent({
            scopes: ['https://graph.microsoft.com/User.Read'],
            account
          });
          accessToken = tokenResponse.accessToken;
          console.log('✅ Successfully acquired access token silently');
        } catch (silentError) {
          console.warn('⚠️ Silent token acquisition failed:', silentError);
          // For now, set as non-admin user to prevent build failure
          setUser({
            id: account.homeAccountId,
            email: userEmail,
            name: account.name || userEmail,
            role: UserRole.USER,
            permissions: {
              can_view_cost_dashboard: false,
              can_manage_users: false,
              can_block_users: false,
              can_view_system_costs: false,
              can_configure_budgets: false,
              can_access_admin_endpoints: false,
              can_override_budget_limits: false,
              can_manage_emergency_controls: false
            },
            isAdmin: false,
            isSuperAdmin: false
          });
          setLoading(false);
          return;
        }

        // Check user role with backend using access token
        const roleResponse = await adminService.getUserRole(accessToken);
        
        const adminUser: AdminUser = {
          id: account.homeAccountId,
          email: userEmail,
          name: account.name || userEmail,
          role: roleResponse.role as UserRole,
          permissions: roleResponse.permissions,
          isAdmin: (roleResponse.role as string) === 'admin' || roleResponse.role === UserRole.ADMIN,
          isSuperAdmin: (roleResponse.role as string) === 'super_admin' || roleResponse.role === UserRole.SUPER_ADMIN
        };

        setUser(adminUser);
        cacheAdminStatus(userEmail, adminUser);

        console.log('🔐 Admin status checked:', {
          email: adminUser.email,
          role: adminUser.role,
          isAdmin: adminUser.isAdmin
        });

      } catch (err) {
        console.error('❌ Admin status check failed:', err);
        setError('Failed to check admin status');
        setUser(null);
      }

    } catch (err) {
      console.error('❌ Admin status check failed:', err);
      setError('Failed to check admin status');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const refreshUserData = async () => {
    // Clear cache before refresh
    if (accounts[0]?.username) {
      localStorage.removeItem(`vimarsh_admin_${accounts[0].username}`);
    }
    await checkAdminStatus();
  };

  useEffect(() => {
    // Check admin status when accounts change
    if (accounts.length > 0) {
      console.log('🚀 AdminContext: Starting admin status check');
      checkAdminStatus();
    } else {
      setLoading(false);
    }
  }, [accounts]);

  const value: AdminContextType = {
    user,
    loading,
    error,
    checkAdminStatus,
    refreshUserData
  };

  return (
    <AdminContext.Provider value={value}>
      {children}
    </AdminContext.Provider>
  );
};
