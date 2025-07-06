import React, { useState, useEffect } from 'react';
import { DollarSign, Users, TrendingUp, AlertCircle, RefreshCw } from 'lucide-react';
import { useAdmin } from '../../contexts/AdminContext';
import { adminService, CostDashboardData } from '../../services/adminService';
import { useMsal } from '@azure/msal-react';

export default function CostDashboard() {
  const { user } = useAdmin();
  const { instance, accounts } = useMsal();
  const [data, setData] = useState<CostDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      let accessToken = '';

      // In development mode, don't require authentication
      if (process.env.NODE_ENV === 'development') {
        console.log('🔧 Development mode: Fetching cost dashboard without auth');
        // Use empty token, backend will handle dev mode
      } else {
        if (!accounts[0]) {
          throw new Error('No authenticated account found');
        }

        const tokenResponse = await instance.acquireTokenSilent({
          scopes: ['openid', 'profile', 'email'],
          account: accounts[0]
        });
        accessToken = tokenResponse.accessToken;
      }

      // Always pass the user's email for security verification
      const dashboardData = await adminService.getCostDashboard(accessToken);
      setData(dashboardData);
    } catch (err) {
      console.error('❌ Cost dashboard fetch failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch cost dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.isAdmin) {
      fetchData();
    }
  }, [user]);

  if (!user?.isAdmin) {
    return (
      <div className="vimarsh-admin-error">
        <AlertCircle className="w-12 h-12 text-red-500" />
        <h2>Access Denied</h2>
        <p>You don't have permission to access the cost dashboard.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="vimarsh-admin-loading">
        <RefreshCw className="w-8 h-8 animate-spin text-sacred-saffron" />
        <p>Loading cost dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="vimarsh-admin-error">
        <AlertCircle className="w-12 h-12 text-red-500" />
        <h2>Error Loading Dashboard</h2>
        <p>{error}</p>
        <button onClick={fetchData} className="vimarsh-btn-primary">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>💰 Cost Dashboard</h1>
        <button onClick={fetchData} className="vimarsh-btn-secondary">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      {data && (
        <div className="vimarsh-admin-grid">
          {/* Summary Cards */}
          <div className="vimarsh-admin-card">
            <div className="card-header">
              <DollarSign className="w-6 h-6 text-sacred-saffron" />
              <h3>Total Cost</h3>
            </div>
            <div className="card-value">${(data.total_cost || 0).toFixed(4)}</div>
          </div>

          <div className="vimarsh-admin-card">
            <div className="card-header">
              <TrendingUp className="w-6 h-6 text-krishna-blue" />
              <h3>Total Tokens</h3>
            </div>
            <div className="card-value">{(data.total_tokens || 0).toLocaleString()}</div>
          </div>

          <div className="vimarsh-admin-card">
            <div className="card-header">
              <Users className="w-6 h-6 text-green-600" />
              <h3>Active Users</h3>
            </div>
            <div className="card-value">{data.active_users || 0}</div>
          </div>

          <div className="vimarsh-admin-card">
            <div className="card-header">
              <AlertCircle className="w-6 h-6 text-red-500" />
              <h3>Users Over Budget</h3>
            </div>
            <div className="card-value">{data.budget_summary?.users_over_budget || 0}</div>
          </div>

          {/* Budget Summary */}
          <div className="vimarsh-admin-card vimarsh-admin-card-wide">
            <h3>💸 Budget Summary</h3>
            <div className="budget-stats">
              <div className="budget-item">
                <span>Total Allocated:</span>
                <span>${(data.budget_summary?.total_allocated || 0).toFixed(2)}</span>
              </div>
              <div className="budget-item">
                <span>Total Used:</span>
                <span>${(data.budget_summary?.total_used || 0).toFixed(4)}</span>
              </div>
              <div className="budget-item">
                <span>Remaining:</span>
                <span>${((data.budget_summary?.total_allocated || 0) - (data.budget_summary?.total_used || 0)).toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Top Users */}
          <div className="vimarsh-admin-card vimarsh-admin-card-wide">
            <h3>🏆 Top Users by Usage</h3>
            <div className="top-users">
              {(data.top_users || []).map((user, index) => (
                <div key={user.user_id} className="user-row">
                  <span className="user-rank">#{index + 1}</span>
                  <span className="user-email">{user.user_id}</span>
                  <span className="user-tokens">{user.tokens || 0} tokens</span>
                  <span className="user-cost">${(user.cost || 0).toFixed(4)}</span>
                </div>
              ))}
              {(!data.top_users || data.top_users.length === 0) && (
                <div className="no-data">No user data available</div>
              )}
            </div>
          </div>

          {/* System Usage Chart */}
          <div className="vimarsh-admin-card vimarsh-admin-card-full">
            <h3>📊 Usage Over Time (Last 7 Days)</h3>
            <div className="usage-chart">
              {(data.system_usage?.last_7_days || []).map((day) => {
                const maxTokens = Math.max(...(data.system_usage?.last_7_days || []).map(d => d.tokens || 0));
                const height = maxTokens > 0 ? (day.tokens || 0) / maxTokens * 100 : 0;
                
                return (
                  <div key={day.date} className="chart-bar">
                    <div 
                      className="bar" 
                      style={{ height: `${height}%` }}
                    ></div>
                    <span className="bar-label">{new Date(day.date).toLocaleDateString()}</span>
                    <span className="bar-value">{day.tokens || 0} tokens</span>
                  </div>
                );
              })}
              {(!data.system_usage?.last_7_days || data.system_usage.last_7_days.length === 0) && (
                <div className="no-data">No usage data available</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
