import React, { useState } from 'react';
import { CreditCard, Lock, LogOut, Trash2, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AccountTab: React.FC = () => {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');

  // Mock data - will be replaced with actual API calls
  const subscription = {
    plan: 'Free Tier',
    aiUsage: 32, // Percentage
    aiLimit: '$10 / month',
    aiUsed: '$3.20',
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleDeleteAccount = () => {
    if (deleteConfirmText === 'DELETE') {
      // TODO: Implement delete account API call
      console.log('Deleting account...');
      setShowDeleteConfirm(false);
      setDeleteConfirmText('');
      alert('This feature will be implemented with the backend API');
    }
  };

  return (
    <div className="space-y-8">
      {/* Subscription */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <CreditCard className="w-6 h-6" />
          Subscription
        </h2>

        <div className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-gray-900">{subscription.plan}</h3>
              <p className="text-sm text-gray-600">You're on the free tier</p>
            </div>
            <div className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium">
              Active
            </div>
          </div>

          {/* AI Usage */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">AI Usage This Month</span>
              <span className="text-sm font-medium text-gray-900">
                {subscription.aiUsed} / {subscription.aiLimit}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${subscription.aiUsage}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              We've covered {subscription.aiUsed} in AI costs for your wisdom journey
            </p>
          </div>

          {/* Upgrade CTA */}
          <div className="p-4 bg-white rounded-lg border border-gray-200">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Upgrade to Premium</h4>
                <ul className="text-sm text-gray-600 space-y-1 mb-3">
                  <li>• Higher AI usage limits</li>
                  <li>• Priority response times</li>
                  <li>• Early access to new personalities</li>
                  <li>• Advanced memory features</li>
                </ul>
              </div>
            </div>
            <button
              onClick={() => alert('Premium plans coming soon!')}
              className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-medium"
            >
              Coming Soon
            </button>
          </div>
        </div>
      </div>

      {/* Account Security */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Lock className="w-6 h-6" />
          Account Security
        </h2>

        <div className="space-y-3">
          {/* Email */}
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-700">Email</div>
                <div className="text-sm text-gray-900 mt-1">{user?.email || 'Not available'}</div>
              </div>
              <div className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                Verified
              </div>
            </div>
          </div>

          {/* Authentication Provider */}
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-700">Authentication</div>
                <div className="text-sm text-gray-900 mt-1">Microsoft Entra ID</div>
              </div>
              <div className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                Active
              </div>
            </div>
          </div>

          {/* Connected Apps */}
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-700">Connected Apps</div>
                <div className="text-sm text-gray-600 mt-1">No third-party apps connected</div>
              </div>
              <button
                onClick={() => alert('This feature will be available soon')}
                className="px-4 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
              >
                Manage
              </button>
            </div>
          </div>

          {/* Active Sessions */}
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-700">Active Sessions</div>
                <div className="text-sm text-gray-600 mt-1">This device only</div>
              </div>
              <button
                onClick={() => alert('This feature will be available soon')}
                className="px-4 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
              >
                View All
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Account Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">⚙️ Account Actions</h2>

        <div className="space-y-3">
          {/* Logout */}
          <div className="p-4 bg-gradient-to-br from-gray-50 to-blue-50 rounded-lg border border-gray-200">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <LogOut className="w-5 h-5 text-gray-600" />
                  <h3 className="font-medium text-gray-900">Sign Out</h3>
                </div>
                <p className="text-sm text-gray-600">
                  End your current session and return to login
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium whitespace-nowrap ml-4"
              >
                Sign Out
              </button>
            </div>
          </div>

          {/* Delete Account */}
          <div className="p-4 bg-gradient-to-br from-red-50 to-pink-50 rounded-lg border border-red-200">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Trash2 className="w-5 h-5 text-red-600" />
                  <h3 className="font-medium text-gray-900">Delete My Account</h3>
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  Permanently delete your account and all data
                </p>
                <div className="flex items-center gap-2 text-xs text-red-600 font-medium">
                  <AlertTriangle className="w-4 h-4" />
                  <span>This action cannot be undone!</span>
                </div>
              </div>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium whitespace-nowrap ml-4"
              >
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Account Information */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-700">
          💡 <strong>Need help?</strong> Visit our{' '}
          <button
            onClick={() => alert('Help Center coming soon')}
            className="text-blue-800 underline hover:no-underline"
          >
            Help Center
          </button>{' '}
          or contact{' '}
          <a href="mailto:support@vimarsh.app" className="text-blue-800 underline hover:no-underline">
            support@vimarsh.app
          </a>
        </p>
      </div>

      {/* Delete Account Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-red-100 rounded-full">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-xl font-bold text-red-600">Delete Account?</h3>
            </div>

            <div className="space-y-3 mb-6 text-sm text-gray-700">
              <p className="font-medium">This will permanently delete:</p>
              <ul className="list-disc ml-5 space-y-1">
                <li>Your profile and account information</li>
                <li>All conversation history</li>
                <li>Your achievements and progress</li>
                <li>All bookmarks and saved wisdom</li>
                <li>Your preferences and settings</li>
              </ul>
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="font-bold text-red-700">⚠️ This action cannot be undone!</p>
                <p className="text-red-600 mt-1">All your data will be permanently lost.</p>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type <span className="font-mono font-bold">DELETE</span> to confirm
              </label>
              <input
                type="text"
                value={deleteConfirmText}
                onChange={(e) => setDeleteConfirmText(e.target.value)}
                className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="DELETE"
                autoFocus
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setDeleteConfirmText('');
                }}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAccount}
                disabled={deleteConfirmText !== 'DELETE'}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Delete Forever
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AccountTab;
