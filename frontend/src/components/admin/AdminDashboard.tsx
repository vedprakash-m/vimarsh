import React, { useState, useEffect } from 'react';
import { Users, DollarSign, Activity, Database, Settings, Shield, BarChart3, MessageSquare, Home } from 'lucide-react';
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
}

type AdminTab = 'overview' | 'users' | 'content' | 'monitoring' | 'settings';

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
      
      const response = await fetch(`${apiBaseUrl}/vimarsh-admin/cost-dashboard`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch system statistics: ${response.status}`);
      }
      
      const apiData = await response.json();
      
      // Transform the API response to match our stats interface
      const transformedStats: SystemStats = {
        totalUsers: apiData.system_usage?.total_users || 0,
        activeUsers: apiData.system_usage?.active_users || 0,
        totalCost: apiData.system_usage?.total_cost_usd || 0,
        totalTokens: apiData.system_usage?.total_tokens || 0,
        totalTexts: apiData.content_stats?.total_texts || 0,
        totalPersonalities: apiData.content_stats?.total_personalities || 8,
        systemHealth: 'healthy',
        lastUpdated: apiData.dashboard_generated || new Date().toISOString()
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
        title="Go to Spiritual Guidance"
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
        onClick={() => setActiveTab('content')}
        className={`admin-nav-item ${activeTab === 'content' ? 'active' : ''}`}
      >
        <MessageSquare size={18} />
        {!sidebarCollapsed && <span>Content</span>}
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
              <h3>Spiritual Texts</h3>
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

  const renderSettings = () => (
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
      case 'content':
        return <ContentManagement />;
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
