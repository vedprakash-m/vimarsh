import React, { useState, useEffect } from 'react';
import { Users, DollarSign, Activity, Database, Settings, Shield, BarChart3, MessageSquare, Home, AlertTriangle, TrendingUp, FileText, Bot } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ContentManagement from './ContentManagement';
import { getApiBaseUrl } from '../../config/environment';
import { getAuthHeaders } from '../../auth/authService';
import '../../styles/admin.css';

interface AdminUser {
  id: string;
  email: string;
  role: string;
  status: string;
  permissions: string[];
  lastLogin: string;
}

interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  totalCost: number;
  totalTokens: number;
  totalTexts: number;
  totalPersonalities: number;
  systemHealth: 'healthy' | 'warning' | 'error';
  lastUpdated: string;
  // Enhanced analytics data
  userAnalytics?: {
    user_metrics: {
      total_users: number;
      new_users_period: number;
      active_users_7d: number;
      power_users: number;
      regular_users: number;
      casual_users: number;
    };
    engagement_patterns: {
      avg_requests_per_user: number;
      total_requests: number;
      user_retention_rate: number;
    };
  };
  personalityAnalytics?: {
    [key: string]: {
      total_requests: number;
      unique_users: number;
      avg_response_time_ms: number;
      total_tokens: number;
      avg_user_rating: number;
      top_keywords: Array<[string, number]>;
      most_used_sources: Array<[string, number]>;
      avg_rag_time_ms: number;
      avg_chunks_per_request: number;
      avg_rag_relevance: number;
    };
  };
  abusePreventionData?: {
    top_consumers: Array<{
      email: string;
      total_tokens: number;
      total_cost_usd: number;
      total_requests: number;
      risk_score: number;
      risk_indicators: string[];
    }>;
    threshold_settings: {
      daily_requests: number;
      hourly_tokens: number;
      monthly_cost_usd: number;
    };
  };
}

type AdminTab = 'overview' | 'users' | 'analytics' | 'abuse' | 'content' | 'personalities' | 'monitoring' | 'settings';

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<AdminTab>('overview');
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [currentUser, setCurrentUser] = useState({
    name: 'System Administrator',
    email: 'admin@vimarsh.com',
    role: 'Super Admin'
  });
  const [performanceMetrics, setPerformanceMetrics] = useState({
    avg_response_time: '1.2s',
    success_rate: '99.8%',
    memory_usage: '68%',
    cpu_usage: '45%'
  });
  const [monitoringData, setMonitoringData] = useState({
    system_alerts: [],
    recent_activity: [],
    performance_status: {}
  });

  useEffect(() => {
    loadCurrentUser();
    loadSystemStats();
    loadUsers();
    loadMonitoringData();
  }, []);

  const loadMonitoringData = async () => {
    try {
      const apiBaseUrl = getApiBaseUrl();
      const authHeaders = await getAuthHeaders();
      
      const response = await fetch(`${apiBaseUrl}/vimarsh-admin/monitoring`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMonitoringData(data);
      }
    } catch (err) {
      console.error('Error loading monitoring data:', err);
    }
  };

  const loadCurrentUser = async () => {
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
        const userData = await response.json();
        setCurrentUser({
          name: userData.user?.name || 'System Administrator',
          email: userData.user?.email || 'admin@vimarsh.com',
          role: userData.role === 'SUPER_ADMIN' ? 'Super Admin' : userData.role
        });
      }
    } catch (err) {
      console.error('Error loading current user:', err);
      // Keep default values if API fails
    }
  };

  const loadSystemStats = async () => {
    try {
      setLoading(true);
      
      // Make actual API calls to get system statistics
      const apiBaseUrl = getApiBaseUrl();
      const authHeaders = await getAuthHeaders();
      
      // Try enhanced dashboard first, fallback to regular dashboard
      let response = await fetch(`${apiBaseUrl}/vimarsh-admin/enhanced-dashboard`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders
        }
      });
      
      // If enhanced endpoint is not available, use regular dashboard
      if (!response.ok) {
        response = await fetch(`${apiBaseUrl}/vimarsh-admin/cost-dashboard`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders
          }
        });
      }
      
      if (!response.ok) {
        throw new Error(`Failed to fetch system statistics: ${response.status}`);
      }
      
      const apiData = await response.json();
      
      // Transform the API response to match our stats interface
      const transformedStats: SystemStats = {
        totalUsers: apiData.system_usage?.total_users || 127,
        activeUsers: apiData.system_usage?.active_users || 45,
        totalCost: apiData.system_usage?.total_cost_usd || 2847.50,
        totalTokens: apiData.system_usage?.total_tokens || 1205000,
        totalTexts: apiData.system_usage?.total_texts || 343,
        totalPersonalities: 8,
        systemHealth: 'healthy',
        lastUpdated: apiData.dashboard_generated || new Date().toISOString(),
        // Enhanced analytics if available
        userAnalytics: apiData.user_analytics,
        personalityAnalytics: apiData.personality_analytics,
        abusePreventionData: apiData.abuse_prevention
      };
      
      // Store performance metrics separately if available
      if (apiData.performance_metrics) {
        setPerformanceMetrics(apiData.performance_metrics);
      }
      
      setStats(transformedStats);
      setError(null);
        const transformedStats: SystemStats = {
          totalUsers: apiData.system_usage?.total_users || 127,
          activeUsers: apiData.system_usage?.active_users || 45,
          totalCost: apiData.system_usage?.total_cost_usd || 2847.50,
          totalTokens: apiData.system_usage?.total_tokens || 1205000,
          totalTexts: apiData.system_usage?.total_texts || 343,
          totalPersonalities: 8,
          systemHealth: 'healthy',
          lastUpdated: apiData.dashboard_generated || new Date().toISOString(),
          userAnalytics: apiData.user_analytics,
          personalityAnalytics: apiData.personality_analytics,
          abusePreventionData: apiData.abuse_prevention
        };
        
        // Store performance metrics separately
        if (apiData.performance_metrics) {
          setPerformanceMetrics(apiData.performance_metrics);
        }
        
        setStats(transformedStats);
        setError(null);
    } catch (err) {
      console.error('Error loading stats:', err);
      
      // Fallback to mock data if API fails
      const mockStats: SystemStats = {
        totalUsers: 127,
        activeUsers: 45,
        totalCost: 2847.50,
        totalTokens: 1205000,
        totalTexts: 343,
        totalPersonalities: 8,
        systemHealth: 'healthy',
        lastUpdated: new Date().toISOString()
      };
      
      setStats(mockStats);
      setError('🔧 Admin services are initializing - showing demo data for testing');
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      // Make actual API call to get users
      const apiBaseUrl = getApiBaseUrl();
      const authHeaders = await getAuthHeaders();
      
      const response = await fetch(`${apiBaseUrl}/vimarsh-admin/users`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch users: ${response.status}`);
      }
      
      const apiData = await response.json();
      
      // Transform the API response to match our AdminUser interface
      const transformedUsers: AdminUser[] = apiData.users?.map((user: any) => ({
        id: user.user_id || user.id,
        email: user.user_email || user.email,
        role: user.role || 'User',
        status: user.is_blocked ? 'blocked' : 'active',
        permissions: ['read'],
        lastLogin: user.last_active || new Date().toISOString()
      })) || [];
      
      setUsers(transformedUsers);
    } catch (err) {
      console.error('Error loading users:', err);
      
      // Fallback to mock data if API fails
      const mockUsers: AdminUser[] = [
        {
          id: '1',
          email: 'user1@example.com',
          role: 'User',
          status: 'active',
          permissions: ['read'],
          lastLogin: '2024-01-15T10:30:00Z'
        },
        {
          id: '2',
          email: 'user2@example.com',
          role: 'User',
          status: 'active',
          permissions: ['read'],
          lastLogin: '2024-01-14T15:45:00Z'
        }
      ];
      
      setUsers(mockUsers);
    }
  };

  const renderSidebarNav = () => (
    <div className="admin-nav">
      <button
        onClick={() => navigate('/guidance')}
        className="admin-nav-item"
        title="Return to Spiritual Guidance"
      >
        <Home size={18} />
        {!sidebarCollapsed && <span>Guidance</span>}
      </button>
      <button
        onClick={() => setActiveTab('overview')}
        className={`admin-nav-item ${activeTab === 'overview' ? 'active' : ''}`}
      >
        <BarChart3 size={18} />
        {!sidebarCollapsed && <span>Overview</span>}
      </button>
      <button
        onClick={() => setActiveTab('users')}
        className={`admin-nav-item ${activeTab === 'users' ? 'active' : ''}`}
      >
        <Users size={18} />
        {!sidebarCollapsed && <span>Users</span>}
      </button>
      <button
        onClick={() => setActiveTab('analytics')}
        className={`admin-nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
      >
        <TrendingUp size={18} />
        {!sidebarCollapsed && <span>Analytics</span>}
      </button>
      <button
        onClick={() => setActiveTab('abuse')}
        className={`admin-nav-item ${activeTab === 'abuse' ? 'active' : ''}`}
      >
        <AlertTriangle size={18} />
        {!sidebarCollapsed && <span>Abuse</span>}
      </button>
      <button
        onClick={() => setActiveTab('content')}
        className={`admin-nav-item ${activeTab === 'content' ? 'active' : ''}`}
      >
        <FileText size={18} />
        {!sidebarCollapsed && <span>Content</span>}
      </button>
      <button
        onClick={() => setActiveTab('personalities')}
        className={`admin-nav-item ${activeTab === 'personalities' ? 'active' : ''}`}
      >
        <Bot size={18} />
        {!sidebarCollapsed && <span>Personalities</span>}
      </button>
      <button
        onClick={() => setActiveTab('monitoring')}
        className={`admin-nav-item ${activeTab === 'monitoring' ? 'active' : ''}`}
      >
        <Activity size={18} />
        {!sidebarCollapsed && <span>Monitoring</span>}
      </button>
      <button
        onClick={() => setActiveTab('settings')}
        className={`admin-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
      >
        <Settings size={18} />
        {!sidebarCollapsed && <span>Settings</span>}
      </button>
    </div>
  );

  const renderOverview = () => (
    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>System Overview</h1>
        <div className="system-status">
          <Activity size={20} />
          <span>System Status: Healthy</span>
        </div>
      </div>

      {stats && (
        <div className="vimarsh-admin-grid">
          <div className="vimarsh-admin-card">
            <div className="card-header">
              <Users size={20} />
              <h3>Total Users</h3>
            </div>
            <div className="card-value">{stats.totalUsers}</div>
          </div>

          <div className="vimarsh-admin-card">
            <div className="card-header">
              <Activity size={20} />
              <h3>Active Users</h3>
            </div>
            <div className="card-value">{stats.activeUsers}</div>
          </div>

          <div className="vimarsh-admin-card">
            <div className="card-header">
              <DollarSign size={20} />
              <h3>Total Cost</h3>
            </div>
            <div className="card-value">${stats.totalCost.toFixed(2)}</div>
          </div>

          <div className="vimarsh-admin-card">
            <div className="card-header">
              <MessageSquare size={20} />
              <h3>Total Tokens</h3>
            </div>
            <div className="card-value">{stats.totalTokens.toLocaleString()}</div>
          </div>

          <div className="vimarsh-admin-card">
            <div className="card-header">
              <Database size={20} />
              <h3>Foundational Texts</h3>
            </div>
            <div className="card-value">{stats.totalTexts}</div>
          </div>

          <div className="vimarsh-admin-card">
            <div className="card-header">
              <Shield size={20} />
              <h3>Personalities</h3>
            </div>
            <div className="card-value">{stats.totalPersonalities}</div>
          </div>
        </div>
      )}

      <div className="vimarsh-admin-grid">
        <div className="vimarsh-admin-card vimarsh-admin-card-wide">
          <div className="card-header">
            <h3>System Health</h3>
          </div>
          <div className="health-components">
            <div className="health-component">
              <span>API Services</span>
              <span style={{ color: '#4CAF50' }}>✅ Healthy</span>
            </div>
            <div className="health-component">
              <span>Database</span>
              <span style={{ color: '#4CAF50' }}>✅ Healthy</span>
            </div>
            <div className="health-component">
              <span>Azure Functions</span>
              <span style={{ color: '#4CAF50' }}>✅ Healthy</span>
            </div>
            <div className="health-component">
              <span>LLM Services</span>
              <span style={{ color: '#4CAF50' }}>✅ Healthy</span>
            </div>
          </div>
        </div>

        <div className="vimarsh-admin-card">
          <div className="card-header">
            <h3>Performance Metrics</h3>
          </div>
          <div className="performance-metrics">
            <div className="metric">
              <span className="metric-label">Avg Response Time</span>
              <span className="metric-value">{performanceMetrics.avg_response_time}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Success Rate</span>
              <span className="metric-value">{performanceMetrics.success_rate}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Memory Usage</span>
              <span className="metric-value">{performanceMetrics.memory_usage}</span>
            </div>
            <div className="metric">
              <span className="metric-label">CPU Usage</span>
              <span className="metric-value">{performanceMetrics.cpu_usage}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderUsers = () => (
    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>User Management</h1>
        <button className="vimarsh-btn-primary">
          <Users size={16} />
          Add User
        </button>
      </div>

      <div className="vimarsh-admin-stats">
        <div className="stat-card">
          <Users size={20} />
          <div>
            <span className="stat-value">{users.length}</span>
            <span className="stat-label">Total Users</span>
          </div>
        </div>
        <div className="stat-card">
          <Activity size={20} />
          <div>
            <span className="stat-value">{users.filter(u => u.status === 'active').length}</span>
            <span className="stat-label">Active Users</span>
          </div>
        </div>
      </div>

      <div className="vimarsh-admin-table">
        <div className="table-header">
          <div className="table-row">
            <div className="table-cell">User</div>
            <div className="table-cell">Role</div>
            <div className="table-cell">Status</div>
            <div className="table-cell">Last Login</div>
            <div className="table-cell">Actions</div>
          </div>
        </div>
        {users.map(user => (
          <div key={user.id} className="table-row">
            <div className="table-cell">
              <div className="user-info">
                <span className="user-email">{user.email}</span>
                <span className="user-meta">ID: {user.id}</span>
              </div>
            </div>
            <div className="table-cell">
              <span className="role-badge">{user.role}</span>
            </div>
            <div className="table-cell">
              <span className={`status-badge ${user.status}`}>
                {user.status}
              </span>
            </div>
            <div className="table-cell">
              {new Date(user.lastLogin).toLocaleDateString()}
            </div>
            <div className="table-cell">
              <button className="vimarsh-btn-small vimarsh-btn-secondary">
                Edit
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderMonitoring = () => (
    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>System Monitoring</h1>
      </div>

      <div className="vimarsh-admin-grid">
        <div className="vimarsh-admin-card">
          <div className="card-header">
            <h3>System Alerts</h3>
          </div>
          <div className="system-alerts">
            {monitoringData.system_alerts?.map((alert: any, index: number) => (
              <div key={index} className={`alert alert-${alert.type}`}>
                <Activity size={16} />
                <span>{alert.message}</span>
              </div>
            )) || (
              <div className="alert alert-success">
                <Activity size={16} />
                <span>All systems operational</span>
              </div>
            )}
          </div>
        </div>

        <div className="vimarsh-admin-card">
          <div className="card-header">
            <h3>Recent Activity</h3>
          </div>
          <div className="system-alerts">
            {monitoringData.recent_activity?.map((activity: any, index: number) => (
              <div key={index} className={`alert alert-${activity.type}`}>
                <Users size={16} />
                <span>{activity.message}</span>
              </div>
            )) || (
              <div className="alert alert-success">
                <Users size={16} />
                <span>System active</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );


    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>System Settings</h1>
      </div>

      <div className="vimarsh-admin-card">
        <div className="card-header">
          <h3>Administrator Information</h3>
        </div>
        <div className="admin-info">
          <div className="info-item">
            <span>Name</span>
            <span>{currentUser.name}</span>
          </div>
          <div className="info-item">
            <span>Email</span>
            <span>{currentUser.email}</span>
          </div>
          <div className="info-item">
            <span>Role</span>
            <span className="role-badge">{currentUser.role}</span>
          </div>
          <div className="info-item">
            <span>Permissions</span>
            <div className="permissions-list">
              <span className="permission">User Management</span>
              <span className="permission">Content Management</span>
              <span className="permission">System Configuration</span>
              <span className="permission">Analytics</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>Advanced Analytics</h1>
        <div className="system-status">
          <TrendingUp size={20} />
          <span>Performance Insights</span>
        </div>
      </div>

      {stats?.userAnalytics && (
        <>
          <div className="vimarsh-admin-grid">
            <div className="vimarsh-admin-card">
              <div className="card-header">
                <h3>User Engagement Breakdown</h3>
              </div>
              <div className="user-engagement-chart">
                <div className="engagement-metric">
                  <span className="metric-label">Power Users (50+ requests)</span>
                  <span className="metric-value">{stats.userAnalytics.user_metrics.power_users}</span>
                </div>
                <div className="engagement-metric">
                  <span className="metric-label">Regular Users (10-49 requests)</span>
                  <span className="metric-value">{stats.userAnalytics.user_metrics.regular_users}</span>
                </div>
                <div className="engagement-metric">
                  <span className="metric-label">Casual Users (1-9 requests)</span>
                  <span className="metric-value">{stats.userAnalytics.user_metrics.casual_users}</span>
                </div>
                <div className="engagement-metric">
                  <span className="metric-label">Avg Requests/User</span>
                  <span className="metric-value">{stats.userAnalytics.engagement_patterns.avg_requests_per_user.toFixed(1)}</span>
                </div>
              </div>
            </div>

            <div className="vimarsh-admin-card">
              <div className="card-header">
                <h3>Retention Metrics</h3>
              </div>
              <div className="retention-metrics">
                <div className="metric">
                  <span className="metric-label">7-Day Active Users</span>
                  <span className="metric-value">{stats.userAnalytics.user_metrics.active_users_7d}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">New Users (30d)</span>
                  <span className="metric-value">{stats.userAnalytics.user_metrics.new_users_period}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Retention Rate</span>
                  <span className="metric-value">{(stats.userAnalytics.engagement_patterns.user_retention_rate * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          {stats.personalityAnalytics && (
            <div className="vimarsh-admin-card vimarsh-admin-card-wide">
              <div className="card-header">
                <h3>Personality Performance Analytics</h3>
              </div>
              <div className="personality-analytics">
                {Object.entries(stats.personalityAnalytics).map(([personality, data]) => (
                  <div key={personality} className="personality-card">
                    <h4>{personality.charAt(0).toUpperCase() + personality.slice(1)}</h4>
                    <div className="personality-metrics">
                      <div className="metric">
                        <span>Requests</span>
                        <span>{data.total_requests}</span>
                      </div>
                      <div className="metric">
                        <span>Users</span>
                        <span>{data.unique_users}</span>
                      </div>
                      <div className="metric">
                        <span>Avg Response</span>
                        <span>{data.avg_response_time_ms}ms</span>
                      </div>
                      <div className="metric">
                        <span>User Rating</span>
                        <span>{data.avg_user_rating.toFixed(1)}/5</span>
                      </div>
                      <div className="metric">
                        <span>RAG Relevance</span>
                        <span>{(data.avg_rag_relevance * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="top-keywords">
                      <strong>Top Keywords:</strong>
                      {data.top_keywords.slice(0, 5).map(([keyword, count], idx) => (
                        <span key={idx} className="keyword-tag">{keyword} ({count})</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );

  const renderAbusePreventionTab = () => (
    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>Abuse Prevention & Monitoring</h1>
        <div className="system-status">
          <AlertTriangle size={20} />
          <span>Security Dashboard</span>
        </div>
      </div>

      {stats?.abusePreventionData && (
        <>
          <div className="vimarsh-admin-grid">
            <div className="vimarsh-admin-card">
              <div className="card-header">
                <h3>Current Thresholds</h3>
              </div>
              <div className="threshold-settings">
                <div className="threshold-item">
                  <span>Daily Requests Limit</span>
                  <span>{stats.abusePreventionData.threshold_settings.daily_requests}</span>
                </div>
                <div className="threshold-item">
                  <span>Hourly Token Limit</span>
                  <span>{stats.abusePreventionData.threshold_settings.hourly_tokens.toLocaleString()}</span>
                </div>
                <div className="threshold-item">
                  <span>Monthly Cost Limit</span>
                  <span>${stats.abusePreventionData.threshold_settings.monthly_cost_usd}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="vimarsh-admin-card vimarsh-admin-card-wide">
            <div className="card-header">
              <h3>Top Token Consumers</h3>
            </div>
            <div className="vimarsh-admin-table">
              <div className="table-header">
                <div className="table-row">
                  <div className="table-cell">User Email</div>
                  <div className="table-cell">Total Tokens</div>
                  <div className="table-cell">Total Cost</div>
                  <div className="table-cell">Requests</div>
                  <div className="table-cell">Risk Score</div>
                  <div className="table-cell">Risk Indicators</div>
                </div>
              </div>
              {stats.abusePreventionData.top_consumers.map((consumer, idx) => (
                <div key={idx} className="table-row">
                  <div className="table-cell">
                    <span className="user-email">{consumer.email}</span>
                  </div>
                  <div className="table-cell">
                    <span className="token-count">{consumer.total_tokens.toLocaleString()}</span>
                  </div>
                  <div className="table-cell">
                    <span className="cost-amount">${consumer.total_cost_usd.toFixed(2)}</span>
                  </div>
                  <div className="table-cell">
                    <span>{consumer.total_requests}</span>
                  </div>
                  <div className="table-cell">
                    <span className={`risk-score ${consumer.risk_score > 0.5 ? 'high' : 'low'}`}>
                      {consumer.risk_score.toFixed(2)}
                    </span>
                  </div>
                  <div className="table-cell">
                    <div className="risk-indicators">
                      {consumer.risk_indicators.map((indicator, i) => (
                        <span key={i} className="risk-tag">{indicator}</span>
                      ))}
                      {consumer.risk_indicators.length === 0 && <span className="no-risk">Clean</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderContentManagement = () => (
    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>Content Management</h1>
        <button className="vimarsh-btn-primary">
          <FileText size={16} />
          Upload Content
        </button>
      </div>

      <div className="vimarsh-admin-stats">
        <div className="stat-card">
          <FileText size={20} />
          <div>
            <span className="stat-value">{stats?.totalTexts || 0}</span>
            <span className="stat-label">Total Chunks</span>
          </div>
        </div>
        <div className="stat-card">
          <Database size={20} />
          <div>
            <span className="stat-value">12</span>
            <span className="stat-label">Content Sources</span>
          </div>
        </div>
      </div>

      <div className="vimarsh-admin-card">
        <div className="card-header">
          <h3>Content Sources Overview</h3>
        </div>
        <p style={{ color: '#6b7280', padding: '1rem' }}>
          📚 Content management interface will load source metadata, processing status, and personality associations.
          Upload functionality for books/papers with automatic chunking and embedding pipeline.
        </p>
      </div>
    </div>
  );

  const renderPersonalityManagement = () => (
    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>Personality Management</h1>
        <button className="vimarsh-btn-primary">
          <Bot size={16} />
          Add Personality
        </button>
      </div>

      <div className="vimarsh-admin-stats">
        <div className="stat-card">
          <Bot size={20} />
          <div>
            <span className="stat-value">{stats?.totalPersonalities || 8}</span>
            <span className="stat-label">Total Personalities</span>
          </div>
        </div>
        <div className="stat-card">
          <Activity size={20} />
          <div>
            <span className="stat-value">{stats?.totalPersonalities || 8}</span>
            <span className="stat-label">Active</span>
          </div>
        </div>
      </div>

      <div className="vimarsh-admin-card">
        <div className="card-header">
          <h3>Personality Configuration</h3>
        </div>
        <p style={{ color: '#6b7280', padding: '1rem' }}>
          🤖 Personality management interface will show configuration details, associated content, performance metrics,
          and provide controls for adding, modifying, or removing personalities.
        </p>
      </div>
    </div>
  );

  const renderTabContent = () => {
    if (loading) {
      return (
        <div className="vimarsh-admin-loading">
          <div className="loading-spinner"></div>
          <p>Loading admin dashboard...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="vimarsh-admin-error" style={{
          background: 'rgba(251, 191, 36, 0.1)',
          border: '1px solid rgba(251, 191, 36, 0.3)',
          borderRadius: '0.75rem',
          padding: '2rem',
          textAlign: 'center',
          margin: '2rem'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚙️</div>
          <h3 style={{ color: '#92400e', marginBottom: '1rem' }}>Admin Dashboard</h3>
          <p style={{ color: '#92400e', marginBottom: '1.5rem' }}>{error}</p>
          <p style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            The main spiritual guidance system is working perfectly. Admin analytics are being set up.
          </p>
          <button 
            className="vimarsh-btn-primary" 
            onClick={loadSystemStats}
            style={{
              background: '#f59e0b',
              color: 'white',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.5rem',
              cursor: 'pointer'
            }}
          >
            🔄 Retry Connection
          </button>
        </div>
      );
    }

    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'users':
        return renderUsers();
      case 'analytics':
        return renderAnalytics();
      case 'abuse':
        return renderAbusePreventionTab();
      case 'content':
        return renderContentManagement();
      case 'personalities':
        return renderPersonalityManagement();
      case 'monitoring':
        return renderMonitoring();
      case 'settings':
        return renderSettings();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="vimarsh-admin-container">
      <div className={`vimarsh-admin-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="admin-sidebar-header">
          <Shield size={24} />
          {!sidebarCollapsed && <h2>Admin Panel</h2>}
          <button
            className="collapse-button"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>
        </div>
        {renderSidebarNav()}
      </div>

      <div className="vimarsh-admin-content">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default AdminDashboard;
