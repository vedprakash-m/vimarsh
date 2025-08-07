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
        // Use cache if less than 5 minutes old
        if (cacheAge < 5 * 60 * 1000) {
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
        return;
      }

      const userEmail = account.username;
      console.log('👤 AdminContext: Quick admin check for user:', userEmail);

      // Check cache first for instant admin button display
      const cachedUser = getCachedAdminStatus(userEmail);
      if (cachedUser) {
        setUser(cachedUser);
        setLoading(false);
        
        // Background refresh without blocking UI
        setTimeout(() => refreshAdminStatusInBackground(userEmail, account), 100);
        return;
      }

      // No cache, perform full check
      await performFullAdminCheck(userEmail, account);

    } catch (err) {
      console.error('❌ Admin status check failed:', err);
      setError('Failed to check admin status');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const performFullAdminCheck = async (userEmail: string, account: any) => {

      // In development mode, use direct API call but with actual user email
      if (process.env.NODE_ENV === 'development') {
        console.log('🔧 Development mode: Checking admin status for actual user');
        
        try {
          // Generate a development token for the specific logged-in user
          const devTokenResponse = await fetch(`${process.env.REACT_APP_API_BASE_URL}/vimarsh-admin/dev-token`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: userEmail })
          });
          
          let userSpecificToken = undefined;
          if (devTokenResponse.ok) {
            const tokenData = await devTokenResponse.json();
            userSpecificToken = tokenData.token;
            console.log('🔑 Generated user-specific dev token for', userEmail);
          } else {
            console.warn('⚠️ Could not generate user-specific token, using generic token');
          }
          
          // Use the user-specific token for admin check
          const roleResponse = await adminService.getUserRole(userSpecificToken);
          console.log('🔍 Raw role response for', userEmail, ':', roleResponse);
          
          const adminUser: AdminUser = {
            id: account.homeAccountId,
            email: userEmail,
            name: account.name || userEmail,
            role: roleResponse.role as UserRole,
            permissions: roleResponse.permissions,
            isAdmin: (roleResponse.role as string) === 'ADMIN' || (roleResponse.role as string) === 'SUPER_ADMIN' || roleResponse.role === UserRole.ADMIN || roleResponse.role === UserRole.SUPER_ADMIN,
            isSuperAdmin: (roleResponse.role as string) === 'SUPER_ADMIN' || roleResponse.role === UserRole.SUPER_ADMIN
          };

          console.log('🧑‍💼 Created user object:', adminUser);
          console.log('🔍 Role comparison:', {
            roleResponse: roleResponse.role,
            UserRoleADMIN: UserRole.ADMIN,
            UserRoleSUPER_ADMIN: UserRole.SUPER_ADMIN,
            isAdmin: adminUser.isAdmin,
            isSuperAdmin: adminUser.isSuperAdmin
          });

          setUser(adminUser);
          
          console.log('🔐 Admin status checked (dev mode):', {
            email: adminUser.email,
            role: adminUser.role,
            isAdmin: adminUser.isAdmin
          });
          
          return;
        } catch (err) {
          console.error('❌ Development admin check failed:', err);
          // In development mode, if admin check fails, set non-admin user with actual user info
          setUser({
            id: account.homeAccountId,
            email: userEmail,
            name: account.name || userEmail,
            role: UserRole.USER,
            permissions: {
              can_view_cost_dashboard: true,
              can_manage_users: true,
              can_block_users: true,
              can_view_system_costs: true,
              can_configure_budgets: true,
              can_access_admin_endpoints: true,
              can_override_budget_limits: true,
              can_manage_emergency_controls: true
            },
            isAdmin: true,
            isSuperAdmin: false
          });
          return;
        }
      }

      // Production mode - use MSAL with proper tokens
      try {
        console.log('🔐 Production mode: Acquiring MSAL token for', userEmail);
        
        // Try to get access token silently first
        let accessToken: string | undefined;
        
        try {
          console.log('🔄 Attempting silent token acquisition...');
          const tokenResponse = await instance.acquireTokenSilent({
            scopes: ['https://graph.microsoft.com/User.Read'],
            account
          });
          accessToken = tokenResponse.accessToken;
          console.log('✅ Successfully acquired access token silently');
          console.log('🔍 Token preview:', accessToken?.substring(0, 50) + '...');
        } catch (silentError) {
          console.warn('⚠️ Silent token acquisition failed, trying interactive:', silentError);
          
                    // If silent fails, try interactive token acquisition
          try {
            console.log('🔄 Attempting interactive token acquisition...');
            const interactiveResponse = await instance.acquireTokenPopup({
              scopes: ['https://graph.microsoft.com/User.Read'],
              account
            });
            accessToken = interactiveResponse.accessToken;
            console.log('✅ Successfully acquired access token interactively');
            console.log('🔍 Token preview:', accessToken?.substring(0, 50) + '...');
          } catch (interactiveError) {
            console.error('❌ Interactive token acquisition also failed:', interactiveError);
            throw interactiveError;
          }
        }

        // Check user role with backend using access token
        console.log('🔄 Calling backend with access token...');
        const roleResponse = await adminService.getUserRole(accessToken);
        console.log('✅ Backend response received:', roleResponse);
        
        const adminUser: AdminUser = {
          id: account.homeAccountId,
          email: userEmail,
          name: account.name || userEmail,
          role: roleResponse.role as UserRole,
          permissions: roleResponse.permissions,
          isAdmin: (roleResponse.role as string) === 'ADMIN' || (roleResponse.role as string) === 'SUPER_ADMIN' || roleResponse.role === UserRole.ADMIN || roleResponse.role === UserRole.SUPER_ADMIN,
          isSuperAdmin: (roleResponse.role as string) === 'SUPER_ADMIN' || roleResponse.role === UserRole.SUPER_ADMIN
        };

        setUser(adminUser);
        
        console.log('🔐 Admin status checked (production):', {
          email: adminUser.email,
          role: adminUser.role,
          isAdmin: adminUser.isAdmin
        });
      } catch (tokenError) {
        console.error('❌ Token acquisition failed:', tokenError);
        // Set user as non-admin if token acquisition fails
        setUser({
          id: account.homeAccountId,
          email: userEmail,
          name: account.name || userEmail,
          role: UserRole.USER,
          permissions: {
            can_view_cost_dashboard: true,
            can_manage_users: true,
            can_block_users: true,
            can_view_system_costs: true,
            can_configure_budgets: true,
            can_access_admin_endpoints: true,
            can_override_budget_limits: true,
            can_manage_emergency_controls: true
          },
          isAdmin: true,
          isSuperAdmin: false
        });
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
    await checkAdminStatus();
  };

  useEffect(() => {
    // Enhanced loading sequence: Check admin status immediately after authentication
    const initializeAdminStatus = async () => {
      if (accounts.length > 0) {
        // Start admin check immediately with priority
        console.log('🚀 AdminContext: Starting immediate admin status check');
        await checkAdminStatus();
      } else {
        setLoading(false);
      }
    };

    initializeAdminStatus();
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
