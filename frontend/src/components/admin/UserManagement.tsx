import React, { useState, useEffect } from 'react';
import { Users, Shield, Ban, CheckCircle, RefreshCw, AlertCircle } from 'lucide-react';
import { useAdmin } from '../../contexts/AdminContext';
import { adminService, UserData } from '../../services/adminService';
import { useMsal } from '@azure/msal-react';

export default function UserManagement() {
  const { user } = useAdmin();
  const { instance, accounts } = useMsal();
  const [users, setUsers] = useState<UserData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchUsers = async () => {
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

      const usersData = await adminService.getUserList(tokenResponse.accessToken);
      setUsers(usersData.users);
    } catch (err) {
      console.error('❌ User list fetch failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const toggleUserBlock = async (userId: string, isBlocked: boolean) => {
    try {
      setActionLoading(userId);

      if (!accounts[0]) {
        throw new Error('No authenticated account found');
      }

      const tokenResponse = await instance.acquireTokenSilent({
        scopes: ['openid', 'profile', 'email'],
        account: accounts[0]
      });

      if (isBlocked) {
        await adminService.unblockUser(userId, tokenResponse.accessToken);
      } else {
        await adminService.blockUser(userId, tokenResponse.accessToken);
      }

      // Refresh user list
      await fetchUsers();
    } catch (err) {
      console.error('❌ User block/unblock failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to update user status');
    } finally {
      setActionLoading(null);
    }
  };

  useEffect(() => {
    if (user?.isAdmin) {
      fetchUsers();
    }
  }, [user]);

  if (!user?.isAdmin) {
    return (
      <div className="vimarsh-admin-error">
        <AlertCircle className="w-12 h-12 text-red-500" />
        <h2>Access Denied</h2>
        <p>You don't have permission to access user management.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="vimarsh-admin-loading">
        <RefreshCw className="w-8 h-8 animate-spin text-sacred-saffron" />
        <p>Loading users...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="vimarsh-admin-error">
        <AlertCircle className="w-12 h-12 text-red-500" />
        <h2>Error Loading Users</h2>
        <p>{error}</p>
        <button onClick={fetchUsers} className="vimarsh-btn-primary">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="vimarsh-admin-dashboard">
      <div className="vimarsh-admin-header">
        <h1>👥 User Management</h1>
        <button onClick={fetchUsers} className="vimarsh-btn-secondary">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      <div className="vimarsh-admin-stats">
        <div className="stat-card">
          <Users className="w-6 h-6 text-krishna-blue" />
          <div>
            <span className="stat-value">{users.length}</span>
            <span className="stat-label">Total Users</span>
          </div>
        </div>
        <div className="stat-card">
          <Ban className="w-6 h-6 text-red-500" />
          <div>
            <span className="stat-value">{users.filter(u => u.is_blocked).length}</span>
            <span className="stat-label">Blocked Users</span>
          </div>
        </div>
        <div className="stat-card">
          <CheckCircle className="w-6 h-6 text-green-600" />
          <div>
            <span className="stat-value">{users.filter(u => !u.is_blocked).length}</span>
            <span className="stat-label">Active Users</span>
          </div>
        </div>
      </div>

      <div className="vimarsh-admin-table">
        <div className="table-header">
          <div className="table-row">
            <div className="table-cell">User</div>
            <div className="table-cell">Usage</div>
            <div className="table-cell">Budget</div>
            <div className="table-cell">Status</div>
            <div className="table-cell">Actions</div>
          </div>
        </div>
        
        <div className="table-body">
          {users.map((userData) => (
            <div key={userData.user_id} className="table-row">
              <div className="table-cell">
                <div className="user-info">
                  <div className="user-email">{userData.user_id}</div>
                  <div className="user-meta">
                    {userData.tokens} tokens • ${userData.cost.toFixed(4)}
                  </div>
                </div>
              </div>
              
              <div className="table-cell">
                <div className="usage-info">
                  <div className="usage-bar">
                    <div 
                      className="usage-fill"
                      style={{ 
                        width: `${Math.min((userData.budget_status.monthly_usage / userData.budget_status.monthly_budget) * 100, 100)}%` 
                      }}
                    ></div>
                  </div>
                  <span className="usage-text">
                    ${userData.budget_status.monthly_usage.toFixed(2)} / ${userData.budget_status.monthly_budget.toFixed(2)}
                  </span>
                </div>
              </div>
              
              <div className="table-cell">
                <div className="budget-info">
                  <div>Monthly: ${userData.budget_status.monthly_budget.toFixed(2)}</div>
                  <div>Daily: ${userData.budget_status.daily_budget.toFixed(2)}</div>
                  <div>Remaining: ${userData.budget_status.remaining_budget.toFixed(2)}</div>
                </div>
              </div>
              
              <div className="table-cell">
                <div className={`status-badge ${userData.is_blocked ? 'blocked' : 'active'}`}>
                  {userData.is_blocked ? (
                    <>
                      <Ban className="w-4 h-4" />
                      Blocked
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      Active
                    </>
                  )}
                </div>
              </div>
              
              <div className="table-cell">
                <button
                  onClick={() => toggleUserBlock(userData.user_id, userData.is_blocked)}
                  disabled={actionLoading === userData.user_id}
                  className={`vimarsh-btn-small ${userData.is_blocked ? 'vimarsh-btn-success' : 'vimarsh-btn-danger'}`}
                >
                  {actionLoading === userData.user_id ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : userData.is_blocked ? (
                    <>
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Unblock
                    </>
                  ) : (
                    <>
                      <Ban className="w-4 h-4 mr-1" />
                      Block
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {users.length === 0 && (
        <div className="vimarsh-admin-empty">
          <Users className="w-12 h-12 text-gray-400" />
          <h3>No Users Found</h3>
          <p>There are no users in the system yet.</p>
        </div>
      )}
    </div>
  );
}
