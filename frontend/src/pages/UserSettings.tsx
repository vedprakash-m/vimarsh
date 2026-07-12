import React, { useState, useEffect } from 'react';
import { X, User, Sparkles, Bell, Shield, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { SettingsProvider, useSettings } from '../contexts/SettingsContext';
import MyProfileTab from '../components/Settings/MyProfileTab';
import ExperienceTab from '../components/Settings/ExperienceTab';
import NotificationsTab from '../components/Settings/NotificationsTab';
import MemoryPrivacyTab from '../components/Settings/MemoryPrivacyTab';
import AccountTab from '../components/Settings/AccountTab';


type TabType = 'profile' | 'experience' | 'notifications' | 'memory' | 'account';

interface Tab {
  id: TabType;
  label: string;
  icon: React.ReactNode;
}

const tabs: Tab[] = [
  { id: 'profile', label: 'My Profile', icon: <User className="w-4 h-4" /> },
  { id: 'experience', label: 'Experience', icon: <Sparkles className="w-4 h-4" /> },
  { id: 'notifications', label: 'Notifications', icon: <Bell className="w-4 h-4" /> },
  { id: 'memory', label: 'Memory & Privacy', icon: <Shield className="w-4 h-4" /> },
  { id: 'account', label: 'Account', icon: <Settings className="w-4 h-4" /> },
];

const UserSettingsContent: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('profile');
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState<'success' | 'error'>('success');
  const { loading } = useSettings();

  // Listen for save events
  useEffect(() => {
    const handleSaved = () => {
      setToastMessage('✓ Saved');
      setToastType('success');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 2000);
    };

    const handleError = (event: CustomEvent) => {
      setToastMessage(event.detail?.message || 'Failed to save');
      setToastType('error');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    };

    window.addEventListener('settings-saved', handleSaved as EventListener);
    window.addEventListener('settings-error', handleError as EventListener);

    return () => {
      window.removeEventListener('settings-saved', handleSaved as EventListener);
      window.removeEventListener('settings-error', handleError as EventListener);
    };
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return <MyProfileTab />;
      case 'experience':
        return <ExperienceTab />;
      case 'notifications':
        return <NotificationsTab />;
      case 'memory':
        return <MemoryPrivacyTab />;
      case 'account':
        return <AccountTab />;
      default:
        return <MyProfileTab />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Settings className="w-6 h-6 text-gray-600" />
            <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
          </div>
          <button
            onClick={() => navigate('/guidance')}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            aria-label="Close Settings"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="max-w-6xl mx-auto px-4 overflow-x-auto">
          <div className="flex gap-1 min-w-max">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  px-4 py-3 text-sm font-medium rounded-t-lg transition-all
                  whitespace-nowrap flex items-center gap-2
                  ${activeTab === tab.id
                    ? 'bg-white text-saffron-600 border-b-2 border-saffron-500'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }
                `}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-saffron-500"></div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            {renderTabContent()}
          </div>
        )}
      </div>

      {/* Toast Notification */}
      {showToast && (
        <div className="fixed bottom-4 right-4 z-50 animate-slide-up">
          <div
            className={`
              px-4 py-3 rounded-lg shadow-lg flex items-center gap-2
              ${toastType === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}
            `}
          >
            {toastMessage}
          </div>
        </div>
      )}
    </div>
  );
};

const UserSettings: React.FC = () => {
  return (
    <SettingsProvider>
      <UserSettingsContent />
    </SettingsProvider>
  );
};

export default UserSettings;
