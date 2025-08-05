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
      console.log('👤 Current logged in user:', userEmail);

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
    if (process.env.NODE_ENV === 'development') {
      // In development mode, always check admin status
      checkAdminStatus();
    } else if (accounts.length > 0) {
      // In production mode, only check if user is authenticated
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
