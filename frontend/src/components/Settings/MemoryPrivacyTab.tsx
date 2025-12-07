import React, { useState } from 'react';
import { Shield, Download, Trash2 } from 'lucide-react';
import { useSettings } from '../../contexts/SettingsContext';

const MemoryPrivacyTab: React.FC = () => {
  const { settings, updateSettings } = useSettings();
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [clearConfirmText, setClearConfirmText] = useState('');

  if (!settings) {
    return <div className="text-gray-500">Loading preferences...</div>;
  }

  const { memory_preferences } = settings;

  const privacyModes = [
    {
      value: 'standard' as const,
      label: 'Standard (Recommended)',
      description: 'Full memory for personalized wisdom',
      detail: 'Conversations help build tailored guidance',
    },
    {
      value: 'private' as const,
      label: 'Private',
      description: 'Limited memory, enhanced privacy',
      detail: 'Basic context only, reduced personalization',
    },
    {
      value: 'minimal' as const,
      label: 'Minimal',
      description: 'No persistent memory',
      detail: 'Fresh start each session, maximum privacy',
    },
  ];

  const retentionOptions = [
    { value: 30, label: '30 days' },
    { value: 90, label: '90 days (default)' },
    { value: 180, label: '180 days' },
    { value: 365, label: '1 year' },
  ];

  const handleClearHistory = () => {
    if (clearConfirmText === 'DELETE') {
      // TODO: Implement clear history API call
      console.log('Clearing conversation history...');
      setShowClearConfirm(false);
      setClearConfirmText('');
      alert('This feature will be implemented with the backend API');
    }
  };

  return (
    <div className="space-y-8">
      {/* Memory Features */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">🧠 Memory Features</h2>
        <p className="text-sm text-gray-600 mb-4">
          These help personalities provide personalized guidance across sessions
        </p>

        <div className="space-y-3">
          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={memory_preferences.remember_conversations}
              onChange={(e) =>
                updateSettings({
                  memory_preferences: {
                    ...memory_preferences,
                    remember_conversations: e.target.checked,
                  },
                })
              }
              className="mt-1 rounded text-blue-500 focus:ring-blue-500"
            />
            <div>
              <div className="font-medium text-gray-900">Remember my conversations</div>
              <div className="text-sm text-gray-600">Personalities recall previous discussions</div>
            </div>
          </label>

          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={memory_preferences.connect_insights}
              onChange={(e) =>
                updateSettings({
                  memory_preferences: {
                    ...memory_preferences,
                    connect_insights: e.target.checked,
                  },
                })
              }
              className="mt-1 rounded text-purple-500 focus:ring-purple-500"
            />
            <div>
              <div className="font-medium text-gray-900">Connect insights across personalities</div>
              <div className="text-sm text-gray-600">Krishna can reference Einstein conversations</div>
            </div>
          </label>

          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={memory_preferences.track_emotions}
              onChange={(e) =>
                updateSettings({
                  memory_preferences: {
                    ...memory_preferences,
                    track_emotions: e.target.checked,
                  },
                })
              }
              className="mt-1 rounded text-pink-500 focus:ring-pink-500"
            />
            <div>
              <div className="font-medium text-gray-900">Track my emotional journey</div>
              <div className="text-sm text-gray-600">Understand your mood patterns over time</div>
            </div>
          </label>

          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={memory_preferences.suggest_topics}
              onChange={(e) =>
                updateSettings({
                  memory_preferences: {
                    ...memory_preferences,
                    suggest_topics: e.target.checked,
                  },
                })
              }
              className="mt-1 rounded text-green-500 focus:ring-green-500"
            />
            <div>
              <div className="font-medium text-gray-900">Suggest topics based on my interests</div>
              <div className="text-sm text-gray-600">Recommend relevant wisdom paths</div>
            </div>
          </label>
        </div>
      </div>

      {/* Privacy Mode */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Shield className="w-6 h-6" />
          Privacy Mode
        </h2>

        <div className="space-y-3">
          {privacyModes.map((mode) => (
            <label
              key={mode.value}
              className={`
                block p-4 border-2 rounded-lg cursor-pointer transition-all
                ${memory_preferences.privacy_mode === mode.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-start gap-3">
                <input
                  type="radio"
                  name="privacy_mode"
                  value={mode.value}
                  checked={memory_preferences.privacy_mode === mode.value}
                  onChange={(e) =>
                    updateSettings({
                      memory_preferences: {
                        ...memory_preferences,
                        privacy_mode: e.target.value as any,
                      },
                    })
                  }
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{mode.label}</div>
                  <div className="text-sm text-gray-600 mt-1">{mode.description}</div>
                  <div className="text-xs text-gray-500 mt-1 italic">"{mode.detail}"</div>
                </div>
              </div>
            </label>
          ))}
        </div>

        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-700">
            💡 Current: {memory_preferences.privacy_mode === 'standard' 
              ? 'All memory features enabled' 
              : memory_preferences.privacy_mode === 'private'
              ? 'Limited memory, enhanced privacy'
              : 'No persistent memory, maximum privacy'}
          </p>
        </div>
      </div>

      {/* Data & Privacy */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Data & Privacy</h2>

        <div className="space-y-3">
          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={memory_preferences.analytics_consent}
              onChange={(e) =>
                updateSettings({
                  memory_preferences: {
                    ...memory_preferences,
                    analytics_consent: e.target.checked,
                  },
                })
              }
              className="mt-1 rounded text-blue-500 focus:ring-blue-500"
            />
            <div>
              <div className="font-medium text-gray-900">Anonymous analytics</div>
              <div className="text-sm text-gray-600">Helps improve Vimarsh for everyone</div>
            </div>
          </label>

          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={memory_preferences.remember_conversations}
              onChange={(e) =>
                updateSettings({
                  memory_preferences: {
                    ...memory_preferences,
                    remember_conversations: e.target.checked,
                  },
                })
              }
              className="mt-1 rounded text-green-500 focus:ring-green-500"
            />
            <div>
              <div className="font-medium text-gray-900">Store my conversations</div>
              <div className="text-sm text-gray-600">Required for memory features</div>
            </div>
          </label>

          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={memory_preferences.research_consent}
              onChange={(e) =>
                updateSettings({
                  memory_preferences: {
                    ...memory_preferences,
                    research_consent: e.target.checked,
                  },
                })
              }
              className="mt-1 rounded text-purple-500 focus:ring-purple-500"
            />
            <div>
              <div className="font-medium text-gray-900">Share anonymized data for research</div>
              <div className="text-sm text-gray-600">Help advance AI wisdom research (opt-in)</div>
            </div>
          </label>
        </div>

        {/* Data Retention */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Data Retention
          </label>
          <select
            value={memory_preferences.data_retention_days}
            onChange={(e) =>
              updateSettings({
                memory_preferences: {
                  ...memory_preferences,
                  data_retention_days: parseInt(e.target.value),
                },
              })
            }
            className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {retentionOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">
            Conversations older than {memory_preferences.data_retention_days} days will be automatically deleted
          </p>
        </div>
      </div>

      {/* Data Management */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">🗂️ Manage Your Data</h2>

        <div className="space-y-4">
          {/* Export Data */}
          <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border border-blue-200">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Download className="w-5 h-5 text-blue-600" />
                  <h3 className="font-medium text-gray-900">Export My Data</h3>
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  Download all conversations, bookmarks, preferences
                </p>
                <p className="text-xs text-gray-500">
                  Format: JSON (GDPR compliant)
                </p>
              </div>
              <button
                onClick={() => {
                  // TODO: Implement export API call
                  alert('This feature will be implemented with the backend API');
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium whitespace-nowrap"
              >
                Export Data
              </button>
            </div>
          </div>

          {/* Clear History */}
          <div className="p-4 bg-gradient-to-br from-red-50 to-pink-50 rounded-lg border border-red-200">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Trash2 className="w-5 h-5 text-red-600" />
                  <h3 className="font-medium text-gray-900">Clear My History</h3>
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  Start fresh (cannot be undone)
                </p>
                <p className="text-xs text-red-600 font-medium">
                  ⚠️ Warning: This deletes all conversation history
                </p>
              </div>
              <button
                onClick={() => setShowClearConfirm(true)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium whitespace-nowrap"
              >
                Clear History
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Clear History Confirmation Modal */}
      {showClearConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-red-600 mb-4">⚠️ Clear All Conversation History?</h3>
            <div className="space-y-3 mb-6 text-sm text-gray-700">
              <p>This will permanently delete:</p>
              <ul className="list-disc ml-5 space-y-1">
                <li>All your conversations</li>
                <li>Your achievements and progress</li>
                <li>Memory features will start fresh</li>
              </ul>
              <p className="font-medium text-red-600">This action cannot be undone!</p>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type <span className="font-mono font-bold">DELETE</span> to confirm
              </label>
              <input
                type="text"
                value={clearConfirmText}
                onChange={(e) => setClearConfirmText(e.target.value)}
                className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="DELETE"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowClearConfirm(false);
                  setClearConfirmText('');
                }}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleClearHistory}
                disabled={clearConfirmText !== 'DELETE'}
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

export default MemoryPrivacyTab;
