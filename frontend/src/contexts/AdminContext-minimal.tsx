import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useMsal } from '@azure/msal-react';

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

export function AdminProvider({ children }: AdminProviderProps): JSX.Element {
  const { accounts } = useMsal();
  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkAdminStatus = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);

      // Get the current account from MSAL
      const account = accounts[0];
      if (!account) {
        setUser(null);
        return;
      }

      // For now, set a basic user to fix build issues
      const basicUser: AdminUser = {
        id: account.homeAccountId,
        email: account.username,
        name: account.name || account.username,
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
      };

      setUser(basicUser);
    } catch (err) {
      console.error('❌ Admin status check failed:', err);
      setError('Failed to check admin status');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const refreshUserData = async (): Promise<void> => {
    await checkAdminStatus();
  };

  useEffect(() => {
    if (accounts.length > 0) {
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
}
