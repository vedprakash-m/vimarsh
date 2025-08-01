import { UserRole, UserPermissions } from '../contexts/AdminContext';

export interface CostDashboardData {
  total_tokens: number;
  total_cost: number;
  active_users: number;
  current_user: string;
  timestamp: string;
  system_usage: {
    last_7_days: Array<{
      date: string;
      tokens: number;
      cost: number;
    }>;
  };
  budget_summary: {
    total_allocated: number;
    total_used: number;
    users_over_budget: number;
  };
  top_users: Array<{
    user_id: string;
    tokens: number;
    cost: number;
  }>;
}

export interface UserData {
  user_id: string;
  tokens: number;
  cost: number;
  budget_status: {
    monthly_budget: number;
    daily_budget: number;
    monthly_usage: number;
    daily_usage: number;
    remaining_budget: number;
  };
  is_blocked: boolean;
}

export interface BudgetData {
  user_id: string;
  monthly_budget: number;
  daily_budget: number;
  request_budget: number;
}

export interface HealthData {
  health_score: number;
  health_status: string;
  system_metrics: {
    total_users: number;
    blocked_users: number;
    active_alerts: number;
    total_requests_7d: number;
    total_cost_7d: number;
  };
  system_usage: {
    total_users: number;
    total_requests: number;
    total_tokens: number;
    total_cost_usd: number;
    avg_tokens_per_request: number;
    cost_per_user: number;
    model_breakdown: Record<string, number>;
    quality_breakdown: Record<string, number>;
    daily_usage: Array<any>;
  };
  budget_summary: {
    total_budgets: number;
    total_alerts: number;
    blocked_users: number;
    recent_alerts: number;
    alert_breakdown: Record<string, number>;
    default_limits: {
      monthly_limit_usd: number;
      daily_limit_usd: number;
      per_request_limit_usd: number;
    };
  };
  timestamp: string;
}

export interface RoleData {
  role: UserRole;
  permissions: UserPermissions;
}

import { getApiBaseUrl } from '../config/environment';

/**
 * AdminService - Enhanced authentication admin API service
 * 
 * SECURITY PRINCIPLES:
 * 1. Uses enhanced authentication middleware
 * 2. Supports development tokens for testing
 * 3. Production requires valid JWT tokens
 * 4. Zero-trust admin validation
 */
class AdminService {
  private baseUrl = getApiBaseUrl();
  
  // Development mode tokens for testing
  private devTokens: { [key: string]: string } = {};
  
  constructor() {
    // Load development tokens if in development mode
    if (process.env.NODE_ENV === 'development') {
      this.loadDevTokens();
    }
  }
  
  private loadDevTokens() {
    // These would be generated by the backend test script
    // In a real implementation, these would be fetched from a secure dev endpoint
    this.devTokens = {
      admin: process.env.REACT_APP_DEV_ADMIN_TOKEN || '',
      superAdmin: process.env.REACT_APP_DEV_SUPER_ADMIN_TOKEN || ''
    };
  }
  
  getDevAdminToken(): string {
    return this.devTokens.admin;
  }
  
  getDevSuperAdminToken(): string {
    return this.devTokens.superAdmin;
  }

  private async makeRequest<T>(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    body?: any,
    accessToken?: string
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Enhanced authentication - always require a token
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    } else if (process.env.NODE_ENV === 'development') {
      // In development, use dev admin token as fallback
      const devToken = this.getDevAdminToken();
      if (devToken) {
        headers['Authorization'] = `Bearer ${devToken}`;
      }
    }

    const options: RequestInit = {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      credentials: 'include',
    };

    const response = await fetch(url, options);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error ${response.status}: ${errorText}`);
    }

    return response.json();
  }

  // ADMIN ENDPOINTS - Enhanced authentication implementation
  
  async getCostDashboard(accessToken?: string): Promise<CostDashboardData> {
    return this.makeRequest<CostDashboardData>('/vimarsh-admin/cost-dashboard', 'GET', null, accessToken);
  }

  async getUserList(accessToken?: string): Promise<{ users: UserData[]; total_users: number; blocked_users: number }> {
    return this.makeRequest('/vimarsh-admin/users', 'GET', null, accessToken);
  }

  async updateUserBudget(userId: string, budgetData: BudgetData, accessToken?: string): Promise<{ success: boolean }> {
    return this.makeRequest(`/vimarsh-admin/budget/${userId}`, 'PUT', budgetData, accessToken);
  }

  async blockUser(userId: string, accessToken?: string): Promise<{ success: boolean }> {
    return this.makeRequest(`/vimarsh-admin/users/${userId}/block`, 'POST', null, accessToken);
  }

  async unblockUser(userId: string, accessToken?: string): Promise<{ success: boolean }> {
    return this.makeRequest(`/vimarsh-admin/users/${userId}/unblock`, 'POST', null, accessToken);
  }

  async getHealthStatus(accessToken?: string): Promise<HealthData> {
    return this.makeRequest<HealthData>('/vimarsh-admin/health', 'GET', null, accessToken);
  }

  async getUserRole(accessToken?: string): Promise<RoleData> {
    return this.makeRequest<RoleData>('/vimarsh-admin/role', 'GET', null, accessToken);
  }

  // USER ENDPOINTS - Standard user functionality
  async getUserBudgetStatus(accessToken: string): Promise<BudgetData> {
    return this.makeRequest<BudgetData>('/user/budget', 'GET', null, accessToken);
  }

  async getSpiritualGuidance(accessToken: string, query: string, language: string = 'English'): Promise<any> {
    return this.makeRequest('/guidance', 'POST', { query, language }, accessToken);
  }
}

export const adminService = new AdminService();
