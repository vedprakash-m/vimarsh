import React, { ReactNode, createContext, useContext } from 'react';

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
  // Minimal implementation for build success
  const value: AdminContextType = {
    user: null,
    loading: false,
    error: null,
    checkAdminStatus: async () => {},
    refreshUserData: async () => {}
  };

  return (
    <AdminContext.Provider value={value}>
      {children}
    </AdminContext.Provider>
  );
}
