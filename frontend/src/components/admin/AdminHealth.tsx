import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle, AlertCircle, RefreshCw, Database, Zap, DollarSign, Shield } from 'lucide-react';
import { useAdmin } from '../../contexts/AdminContext';
import { adminService, HealthData } from '../../services/adminService';
import { useMsal } from '@azure/msal-react';

export default function AdminHealth() {
  const { user } = useAdmin();
  const { instance, accounts } = useMsal();
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!accounts[0]) {
        throw new Error('No authenticated account found');
      }

      const tokenResponse = await instance.acquireTokenSilent({
        scopes: ['openid', 'profile', 'email'],
        account: accounts[0]
      });

      // Always pass the user's email for security verification
      const healthData = await adminService.getHealthStatus(tokenResponse.accessToken);
      setHealth(healthData);
    } catch (err) {
      console.error('❌ Health status fetch failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch health status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.isAdmin) {
      fetchHealth();
      // Auto-refresh every 30 seconds
      const interval = setInterval(fetchHealth, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const getStatusIcon = (status: string | undefined) => {
    if (!status) {
      return <Activity className="w-5 h-5 text-gray-500" />;
    }
    
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'online':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'error':
      case 'offline':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string | undefined) => {
    if (!status) {
      return 'text-gray-500';
    }
    
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'online':
        return 'text-green-500';
      case 'warning':
        return 'text-yellow-500';
      case 'error':
      case 'offline':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  if (!user?.isAdmin) {
    return (
      <div className="vimarsh-admin-error">
        <AlertCircle className="w-12 h-12 text-red-500" />
        <h2>Access Denied</h2>
        <p>You don't have permission to access system health.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="vimarsh-admin-loading">
        <RefreshCw className="w-8 h-8 animate-spin text-sacred-saffron" />
        <p>Loading system health...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="vimarsh-admin-error">
        <AlertCircle className="w-12 h-12 text-red-500" />
        <h2>Error Loading Health Status</h2>
        <p>{error}</p>
        <button onClick={fetchHealth} className="vimarsh-btn-primary">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>❤️ System Health</h1>
        <button onClick={fetchHealth} className="vimarsh-btn-secondary">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      {health && (
        <div className="vimarsh-admin-grid">
          {/* Overall Health Score */}
          <div className="vimarsh-admin-card vimarsh-admin-card-wide">
            <div className="card-header">
              <Activity className="w-6 h-6 text-krishna-blue" />
              <h3>Overall System Health</h3>
            </div>
            <div className={`system-status ${getStatusColor(health.health_status)}`}>
              {getStatusIcon(health.health_status)}
              <span className="status-text">{health.health_status?.toUpperCase() || 'UNKNOWN'}</span>
              <div className="health-score">
                Health Score: {health.health_score}/100
              </div>
            </div>
            <div className="status-timestamp">
              Last updated: {new Date(health.timestamp).toLocaleString()}
            </div>
          </div>

          {/* System Metrics */}
          <div className="vimarsh-admin-card">
            <h3>📊 System Metrics (7 Days)</h3>
            <div className="metrics-grid">
              <div className="metric">
                <span className="metric-label">Total Users</span>
                <span className="metric-value">{health.system_metrics.total_users}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Blocked Users</span>
                <span className="metric-value text-red-500">{health.system_metrics.blocked_users}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Active Alerts</span>
                <span className="metric-value text-yellow-500">{health.system_metrics.active_alerts}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Requests (7d)</span>
                <span className="metric-value">{health.system_metrics.total_requests_7d}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Cost (7d)</span>
                <span className="metric-value">${health.system_metrics.total_cost_7d.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Usage Statistics */}
          <div className="vimarsh-admin-card">
            <h3>📈 Usage Statistics</h3>
            <div className="metrics-grid">
              <div className="metric">
                <span className="metric-label">Total Requests</span>
                <span className="metric-value">{health.system_usage.total_requests}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Total Tokens</span>
                <span className="metric-value">{health.system_usage.total_tokens}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Total Cost</span>
                <span className="metric-value">${health.system_usage.total_cost_usd.toFixed(2)}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Avg Tokens/Request</span>
                <span className="metric-value">{health.system_usage.avg_tokens_per_request.toFixed(1)}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Cost per User</span>
                <span className="metric-value">${health.system_usage.cost_per_user.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Budget Summary */}
          <div className="vimarsh-admin-card">
            <h3>💰 Budget Health</h3>
            <div className="metrics-grid">
              <div className="metric">
                <span className="metric-label">Total Budgets</span>
                <span className="metric-value">{health.budget_summary.total_budgets}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Budget Alerts</span>
                <span className="metric-value text-yellow-500">{health.budget_summary.total_alerts}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Recent Alerts</span>
                <span className="metric-value">{health.budget_summary.recent_alerts}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Monthly Limit</span>
                <span className="metric-value">${health.budget_summary.default_limits.monthly_limit_usd}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Daily Limit</span>
                <span className="metric-value">${health.budget_summary.default_limits.daily_limit_usd}</span>
              </div>
            </div>
          </div>

          {/* System Activity */}
          <div className="vimarsh-admin-card">
            <h3>📈 System Activity</h3>
            <div className="metrics-grid">
              <div className="metric">
                <span className="metric-label">Total Users</span>
                <span className="metric-value">{health.system_usage.total_users}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Total Requests</span>
                <span className="metric-value">{health.system_usage.total_requests.toLocaleString()}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Total Tokens</span>
                <span className="metric-value">{health.system_usage.total_tokens.toLocaleString()}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Avg Tokens/Request</span>
                <span className="metric-value">{health.system_usage.avg_tokens_per_request.toFixed(1)}</span>
              </div>
            </div>
          </div>

          {/* System Alerts */}
          <div className="vimarsh-admin-card">
            <h3>⚠️ System Alerts</h3>
            <div className="system-alerts">
              {health.system_metrics.blocked_users > 0 && (
                <div className="alert alert-warning">
                  <AlertCircle className="w-4 h-4" />
                  {health.system_metrics.blocked_users} user(s) currently blocked
                </div>
              )}
              
              {health.system_metrics.active_alerts > 0 && (
                <div className="alert alert-warning">
                  <AlertCircle className="w-4 h-4" />
                  {health.system_metrics.active_alerts} active system alerts
                </div>
              )}
              
              {health.budget_summary.total_alerts > 0 && (
                <div className="alert alert-warning">
                  <AlertCircle className="w-4 h-4" />
                  {health.budget_summary.total_alerts} budget alerts active
                </div>
              )}
              
              {health.system_metrics.blocked_users === 0 && 
               health.system_metrics.active_alerts === 0 && 
               health.budget_summary.total_alerts === 0 && (
                <div className="alert alert-success">
                  <CheckCircle className="w-4 h-4" />
                  All systems operating normally
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
