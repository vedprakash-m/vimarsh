import React, { useState } from 'react';
import { DollarSign, Users, Activity, Shield, Settings, ChevronDown, ChevronUp, Brain, FileText, UserCheck, Zap, TestTube } from 'lucide-react';
import { useAdmin } from '../../contexts/AdminContext';
import CostDashboard from './CostDashboard';
import UserManagement from './UserManagement';
import AdminHealth from './AdminHealth';
import PersonalityManager from './PersonalityManager';
import ContentManager from './ContentManager';
import ExpertReview from './ExpertReview';
import PerformanceDashboard from './PerformanceDashboard';
import TestingDashboard from './TestingDashboard';

type AdminTab = 'cost' | 'users' | 'health' | 'personalities' | 'content' | 'expert-review' | 'performance' | 'testing' | 'settings';

export default function AdminDashboard() {
  const { user } = useAdmin();
  const [activeTab, setActiveTab] = useState<AdminTab>('cost');
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (!user?.isAdmin) {
    return null;
  }

  const tabs = [
    { id: 'cost' as AdminTab, label: 'Cost Dashboard', icon: DollarSign },
    { id: 'users' as AdminTab, label: 'User Management', icon: Users },
    { id: 'health' as AdminTab, label: 'System Health', icon: Activity },
    { id: 'personalities' as AdminTab, label: 'Personalities', icon: Brain },
    { id: 'content' as AdminTab, label: 'Content', icon: FileText },
    { id: 'expert-review' as AdminTab, label: 'Expert Review', icon: UserCheck },
    { id: 'performance' as AdminTab, label: 'Performance', icon: Zap },
    { id: 'testing' as AdminTab, label: 'Testing', icon: TestTube },
    { id: 'settings' as AdminTab, label: 'Settings', icon: Settings },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'cost':
        return <CostDashboard />;
      case 'users':
        return <UserManagement />;
      case 'health':
        return <AdminHealth />;
      case 'personalities':
        return <PersonalityManager />;
      case 'content':
        return <ContentManager />;
      case 'expert-review':
        return <ExpertReview />;
      case 'performance':
        return <PerformanceDashboard />;
      case 'testing':
        return <TestingDashboard />;
      case 'settings':
        return (
          <div className="vimarsh-admin-dashboard">
            <div className="vimarsh-admin-header">
              <h1>⚙️ Admin Settings</h1>
            </div>
            <div className="vimarsh-admin-card">
              <h3>👑 Admin Information</h3>
              <div className="admin-info">
                <div className="info-item">
                  <span>Email:</span>
                  <span>{user.email}</span>
                </div>
                <div className="info-item">
                  <span>Role:</span>
                  <span className="role-badge">{user.role}</span>
                </div>
                <div className="info-item">
                  <span>Permissions:</span>
                  <div className="permissions-list">
                    {user.permissions.can_view_cost_dashboard && <span className="permission">View Cost Dashboard</span>}
                    {user.permissions.can_manage_users && <span className="permission">Manage Users</span>}
                    {user.permissions.can_configure_budgets && <span className="permission">Configure Budgets</span>}
                    {user.permissions.can_override_budget_limits && <span className="permission">Override Budget Limits</span>}
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      default:
        return <CostDashboard />;
    }
  };

  return (
    <div className="vimarsh-admin-container">
      <div className={`vimarsh-admin-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
        <div className="admin-sidebar-header">
          <Shield className="w-6 h-6 text-sacred-saffron" />
          {!isCollapsed && <h2>Admin Panel</h2>}
          <button 
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="collapse-button"
          >
            {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
        
        <nav className="admin-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`admin-nav-item ${activeTab === tab.id ? 'active' : ''}`}
            >
              <tab.icon className="w-5 h-5" />
              {!isCollapsed && <span>{tab.label}</span>}
            </button>
          ))}
        </nav>
      </div>
      
      <div className="vimarsh-admin-content">
        {renderContent()}
      </div>
    </div>
  );
}
