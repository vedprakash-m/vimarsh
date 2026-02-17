import React from 'react';
import { Bell } from 'lucide-react';
import { useSettings } from '../../contexts/SettingsContext';
import '../../styles/settings-utilities.css';

const NotificationsTab: React.FC = () => {
  const { settings, updateSettings } = useSettings();

  if (!settings) {
    return <div className="text-gray-500">Loading preferences...</div>;
  }

  const { notification_preferences } = settings;

  const timezones = [
    'America/Los_Angeles',
    'America/New_York',
    'America/Chicago',
    'America/Denver',
    'Europe/London',
    'Europe/Paris',
    'Asia/Kolkata',
    'Asia/Tokyo',
    'Australia/Sydney',
  ];

  const timePresets = [
    { value: '07:00', label: 'Morning (7:00 AM)' },
    { value: '12:00', label: 'Midday (12:00 PM)' },
    { value: '18:00', label: 'Evening (6:00 PM)' },
  ];

  return (
    <div className="space-y-8">
      {/* Daily Wisdom */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Bell className="w-6 h-6" />
          Daily Wisdom
        </h2>
        
        <div className="space-y-4">
          {/* Master Toggle */}
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-saffron-50 to-amber-50 rounded-lg border border-saffron-200">
            <div>
              <div className="font-medium text-gray-900">Enable Daily Wisdom</div>
              <div className="text-sm text-gray-600 mt-1">
                Receive daily inspiration from your wisdom journey
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notification_preferences.daily_wisdom_enabled}
                onChange={(e) =>
                  updateSettings({
                    notification_preferences: {
                      ...notification_preferences,
                      daily_wisdom_enabled: e.target.checked,
                    },
                  })
                }
                className="sr-only"
              />
              <div className="settings-toggle"></div>
            </label>
          </div>

          {notification_preferences.daily_wisdom_enabled && (
            <>
              {/* Time Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  🕐 Preferred Time
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-2">
                  {timePresets.map((preset) => (
                    <button
                      key={preset.value}
                      onClick={() =>
                        updateSettings({
                          notification_preferences: {
                            ...notification_preferences,
                            preferred_time: preset.value,
                          },
                        })
                      }
                      className={`
                        px-4 py-2 rounded-lg font-medium transition-all
                        ${notification_preferences.preferred_time === preset.value
                          ? 'bg-saffron-500 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }
                      `}
                    >
                      {preset.label}
                    </button>
                  ))}
                </div>
                <input
                  type="time"
                  value={notification_preferences.preferred_time}
                  onChange={(e) =>
                    updateSettings({
                      notification_preferences: {
                        ...notification_preferences,
                        preferred_time: e.target.value,
                      },
                    })
                  }
                  className="w-full md:w-48 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-saffron-500 focus:border-transparent"
                />
              </div>

              {/* Timezone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  🌍 Timezone
                </label>
                <select
                  value={notification_preferences.timezone}
                  onChange={(e) =>
                    updateSettings({
                      notification_preferences: {
                        ...notification_preferences,
                        timezone: e.target.value,
                      },
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-saffron-500 focus:border-transparent"
                >
                  {timezones.map((tz) => (
                    <option key={tz} value={tz}>
                      {tz}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Current selection: {notification_preferences.timezone}
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Quiet Hours */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">🌙 Quiet Hours</h2>
        
        <div className="space-y-4">
          {/* Enable Quiet Hours */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <div className="font-medium text-gray-900">Enable Quiet Hours</div>
              <div className="text-sm text-gray-600 mt-1">
                No notifications during sleep hours
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notification_preferences.quiet_hours_enabled}
                onChange={(e) =>
                  updateSettings({
                    notification_preferences: {
                      ...notification_preferences,
                      quiet_hours_enabled: e.target.checked,
                    },
                  })
                }
                className="sr-only"
              />
              <div className="settings-toggle settings-toggle--blue"></div>
            </label>
          </div>

          {notification_preferences.quiet_hours_enabled && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Time
                </label>
                <input
                  type="time"
                  value={notification_preferences.quiet_start}
                  onChange={(e) =>
                    updateSettings({
                      notification_preferences: {
                        ...notification_preferences,
                        quiet_start: e.target.value,
                      },
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Time
                </label>
                <input
                  type="time"
                  value={notification_preferences.quiet_end}
                  onChange={(e) =>
                    updateSettings({
                      notification_preferences: {
                        ...notification_preferences,
                        quiet_end: e.target.value,
                      },
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          )}

          {notification_preferences.quiet_hours_enabled && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700">
                💡 Notifications paused from {notification_preferences.quiet_start} to {notification_preferences.quiet_end}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Notification Types */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">🔔 What to Notify About</h2>
        
        <div className="space-y-3">
          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={notification_preferences.types.daily_wisdom}
              onChange={(e) =>
                updateSettings({
                  notification_preferences: {
                    ...notification_preferences,
                    types: {
                      ...notification_preferences.types,
                      daily_wisdom: e.target.checked,
                    },
                  },
                })
              }
              className="mt-1 rounded text-saffron-500 focus:ring-saffron-500"
            />
            <div>
              <div className="font-medium text-gray-900">Daily wisdom quote</div>
              <div className="text-sm text-gray-600">Receive daily inspiration from personalities</div>
            </div>
          </label>

          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={notification_preferences.types.streak_reminders}
              onChange={(e) =>
                updateSettings({
                  notification_preferences: {
                    ...notification_preferences,
                    types: {
                      ...notification_preferences.types,
                      streak_reminders: e.target.checked,
                    },
                  },
                })
              }
              className="mt-1 rounded text-orange-500 focus:ring-orange-500"
            />
            <div>
              <div className="font-medium text-gray-900">Streak reminders</div>
              <div className="text-sm text-gray-600">Get notified when you might miss a day</div>
            </div>
          </label>

          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={notification_preferences.types.achievements}
              onChange={(e) =>
                updateSettings({
                  notification_preferences: {
                    ...notification_preferences,
                    types: {
                      ...notification_preferences.types,
                      achievements: e.target.checked,
                    },
                  },
                })
              }
              className="mt-1 rounded text-purple-500 focus:ring-purple-500"
            />
            <div>
              <div className="font-medium text-gray-900">Achievement unlocks</div>
              <div className="text-sm text-gray-600">Celebrate your wisdom journey milestones</div>
            </div>
          </label>

          <label className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={notification_preferences.types.weekly_summary}
              onChange={(e) =>
                updateSettings({
                  notification_preferences: {
                    ...notification_preferences,
                    types: {
                      ...notification_preferences.types,
                      weekly_summary: e.target.checked,
                    },
                  },
                })
              }
              className="mt-1 rounded text-blue-500 focus:ring-blue-500"
            />
            <div>
              <div className="font-medium text-gray-900">Weekly summary email</div>
              <div className="text-sm text-gray-600">Get a weekly recap of your wisdom journey</div>
            </div>
          </label>
        </div>
      </div>

      {/* Test Notification */}
      <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
        <h3 className="font-medium text-gray-900 mb-2">Test Your Notifications</h3>
        <p className="text-sm text-gray-600 mb-3">
          Make sure you can receive notifications from Vimarsh
        </p>
        <button
          onClick={() => {
            if ('Notification' in window && Notification.permission === 'granted') {
              new Notification('Vimarsh Test', {
                body: 'Your notifications are working perfectly! 🙏',
                icon: '/logo192.png',
              });
            } else if ('Notification' in window && Notification.permission !== 'denied') {
              Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                  new Notification('Vimarsh Test', {
                    body: 'Your notifications are working perfectly! 🙏',
                    icon: '/logo192.png',
                  });
                }
              });
            } else {
              alert('Notifications are blocked. Please enable them in your browser settings.');
            }
          }}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
        >
          Send Test Notification
        </button>
        <p className="text-xs text-gray-500 mt-2">
          Permission Status: {typeof window !== 'undefined' && 'Notification' in window 
            ? Notification.permission === 'granted' 
              ? '✅ Enabled' 
              : Notification.permission === 'denied'
              ? '🚫 Blocked - Enable in browser settings'
              : '⚠️ Not yet requested'
            : '❌ Not supported'}
        </p>
      </div>
    </div>
  );
};

export default NotificationsTab;
