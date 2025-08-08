import React, { ReactNode, createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from '../auth/AuthProvider';
import { getApiBaseUrl } from '../config/environment';
import { getAuthHeaders } from '../auth/authService';

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

// Known admin emails - this should eventually come from backend config
const ADMIN_EMAILS = [
  'vedprakash.m@outlook.com',
  'admin@vimarsh.com',
  'vedprakash@outlook.com'
];

export function AdminProvider({ children }: AdminProviderProps): JSX.Element {
  const { isAuthenticated, account } = useAuth();
  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkAdminStatus = useCallback(async () => {
    if (!isAuthenticated || !account) {
      setUser(null);
      return;
    }

    const userEmail = account.username || account.name || '';
    console.log('🔍 AdminProvider: Checking admin status for:', userEmail);

    try {
      setLoading(true);
      setError(null);

      // Check if user is in predefined admin list
      const isKnownAdmin = ADMIN_EMAILS.includes(userEmail.toLowerCase());
      
      if (isKnownAdmin) {
        console.log('✅ AdminProvider: User is a known admin');
        
        // Try to get role from backend, fallback to local admin detection
        let backendRole = UserRole.ADMIN;
        let permissions: UserPermissions = {
          can_view_cost_dashboard: true,
          can_manage_users: true,
          can_block_users: true,
          can_view_system_costs: true,
          can_configure_budgets: true,
          can_access_admin_endpoints: true,
          can_override_budget_limits: true,
          can_manage_emergency_controls: true
        };

        try {
          const apiBaseUrl = getApiBaseUrl();
          const authHeaders = await getAuthHeaders();
          
          const response = await fetch(`${apiBaseUrl}/vimarsh-admin/role`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              ...authHeaders
            }
          });
          
          if (response.ok) {
            const roleData = await response.json();
            console.log('📋 AdminProvider: Backend role data:', roleData);
            
            if (roleData.role) {
              backendRole = roleData.role === 'SUPER_ADMIN' ? UserRole.SUPER_ADMIN : UserRole.ADMIN;
              permissions = roleData.permissions || permissions;
            }
          } else {
            console.warn('⚠️ AdminProvider: Backend role check failed, using local admin detection');
          }
        } catch (backendError) {
          console.warn('⚠️ AdminProvider: Backend unreachable, using local admin detection:', backendError);
        }

        const adminUser: AdminUser = {
          id: account.homeAccountId || account.localAccountId || userEmail,
          email: userEmail,
          name: account.name || userEmail.split('@')[0],
          role: backendRole,
          permissions,
          isAdmin: true,
          isSuperAdmin: backendRole === UserRole.SUPER_ADMIN
        };

        setUser(adminUser);
        console.log('✅ AdminProvider: Admin user set:', adminUser);
      } else {
        console.log('ℹ️ AdminProvider: User is not an admin');
        setUser(null);
      }
    } catch (err) {
      console.error('❌ AdminProvider: Error checking admin status:', err);
      setError(err instanceof Error ? err.message : 'Failed to check admin status');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, account]);

  const refreshUserData = useCallback(async () => {
    await checkAdminStatus();
  }, [checkAdminStatus]);

  // Check admin status when authentication state changes
  useEffect(() => {
    checkAdminStatus();
  }, [checkAdminStatus]);

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
