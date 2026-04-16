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

// Cache admin role to prevent redundant backend calls
interface RoleCache {
  data: AdminUser;
  timestamp: number;
  email: string;
}

const ROLE_CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
let roleCache: RoleCache | null = null;

export function AdminProvider({ children }: AdminProviderProps): JSX.Element {
  const { isAuthenticated, account } = useAuth();
  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkAdminStatus = useCallback(async () => {
    if (!isAuthenticated || !account) {
      setUser(null);
      roleCache = null;
      return;
    }

    const userEmail = account.username || account.name || '';
    
    if (process.env.NODE_ENV === 'development') {
      console.log('🔍 AdminProvider: Checking admin status for:', userEmail);
    }

    // Check cache first to prevent redundant API calls
    if (roleCache && 
        roleCache.email === userEmail && 
        Date.now() - roleCache.timestamp < ROLE_CACHE_DURATION) {
      if (process.env.NODE_ENV === 'development') {
        console.log('✅ AdminProvider: Using cached admin role (age:', 
          Math.floor((Date.now() - roleCache.timestamp) / 1000), 'seconds)');
      }
      setUser(roleCache.data);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Parse admin emails from environment, merging with hardcoded list
      const envAdminEmailsStr = process.env.REACT_APP_ADMIN_EMAILS || '';
      const envAdminEmails = envAdminEmailsStr.split(',').map((e: string) => e.trim().toLowerCase()).filter(Boolean);
      const combinedEmails = ADMIN_EMAILS.map(e => e.toLowerCase()).concat(envAdminEmails);
      const allKnownAdminEmails = combinedEmails.filter((e, i, self) => self.indexOf(e) === i);
      const isKnownAdmin = allKnownAdminEmails.includes(userEmail.toLowerCase());
      
      let backendRole = UserRole.USER;
      let permissions: UserPermissions = {
        can_view_cost_dashboard: false,
        can_manage_users: false,
        can_block_users: false,
        can_view_system_costs: false,
        can_configure_budgets: false,
        can_access_admin_endpoints: false,
        can_override_budget_limits: false,
        can_manage_emergency_controls: false
      };

      // Always try to get role from backend first
      try {
        const apiBaseUrl = getApiBaseUrl();
        // Use try-catch for auth headers to prevent silent token failures from breaking the app
        let authHeaders = {};
        try {
          authHeaders = await getAuthHeaders();
        } catch (authErr) {
          console.warn('⚠️ AdminProvider: Could not get auth headers (token may be expired):', authErr);
        }
        
        const response = await fetch(`${apiBaseUrl}/vimarsh-admin/role`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders
          }
        });
        
        if (response.ok) {
          const roleData = await response.json();
          if (roleData.role) {
            backendRole = roleData.role === 'SUPER_ADMIN' ? UserRole.SUPER_ADMIN : 
                          (roleData.role === 'ADMIN' ? UserRole.ADMIN : UserRole.USER);
            if (roleData.permissions) {
               permissions = roleData.permissions;
            } else if (backendRole === UserRole.ADMIN || backendRole === UserRole.SUPER_ADMIN) {
               permissions = {
                  can_view_cost_dashboard: true,
                  can_manage_users: true,
                  can_block_users: true,
                  can_view_system_costs: true,
                  can_configure_budgets: true,
                  can_access_admin_endpoints: true,
                  can_override_budget_limits: true,
                  can_manage_emergency_controls: true
               };
            }
          }
        }
      } catch (error) {
        console.warn('⚠️ AdminProvider: Could not contact backend for role check:', error);
      }

      // Check if user is in predefined admin list or backend role is admin
      if (backendRole === UserRole.ADMIN || backendRole === UserRole.SUPER_ADMIN || isKnownAdmin) {
        if (process.env.NODE_ENV === 'development') {
          console.log(`✅ AdminProvider: User verified as admin (Backend: ${backendRole}, Known list: ${isKnownAdmin})`);
        }
        
        // If not retrieved from backend but in known list, populate default admin permissions
        if (permissions.can_manage_users === false) {
           permissions = {
            can_view_cost_dashboard: true,
            can_manage_users: true,
            can_block_users: true,
            can_view_system_costs: true,
            can_configure_budgets: true,
            can_access_admin_endpoints: true,
            can_override_budget_limits: true,
            can_manage_emergency_controls: true
          };
        }

        const adminUser: AdminUser = {
          id: account.homeAccountId || account.localAccountId || userEmail,
          email: userEmail,
          name: account.name || userEmail.split('@')[0],
          role: backendRole === UserRole.USER ? UserRole.ADMIN : backendRole,
          permissions,
          isAdmin: true,
          isSuperAdmin: backendRole === UserRole.SUPER_ADMIN
        };

        // Cache the role data
        roleCache = {
          data: adminUser,
          timestamp: Date.now(),
          email: userEmail
        };

        setUser(adminUser);
        
        if (process.env.NODE_ENV === 'development') {
          console.log('✅ AdminProvider: Admin user set and cached:', adminUser);
        }
      } else {
        if (process.env.NODE_ENV === 'development') {
          console.log('ℹ️ AdminProvider: User is not an admin');
        }
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
    // Clear cache to force fresh check
    roleCache = null;
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
