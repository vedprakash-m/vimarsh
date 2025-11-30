/**
 * NotificationSettings Component
 * 
 * User interface for managing push notification preferences.
 * Handles permission requests, time preferences, and notification types.
 * 
 * @module components/NotificationSettings
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Bell, 
  BellOff, 
  Clock, 
  Check, 
  X, 
  Loader2,
  Sun,
  Moon,
  Coffee,
  Sparkles,
  AlertCircle,
  Settings
} from 'lucide-react';
import { getApiBaseUrl } from '../config/environment';

// ============================================================================
// Types
// ============================================================================

interface NotificationPreferences {
  enabled: boolean;
  dailyWisdom: boolean;
  newPersonalities: boolean;
  weeklyDigest: boolean;
  preferredTime: string; // HH:mm format
  timezone: string;
}

interface NotificationSettingsProps {
  className?: string;
  onClose?: () => void;
  compact?: boolean;
}

// ============================================================================
// Time Presets
// ============================================================================

const TIME_PRESETS = [
  { id: 'morning', time: '06:00', label: 'Morning', icon: Coffee, description: 'Start your day with wisdom' },
  { id: 'midday', time: '12:00', label: 'Midday', icon: Sun, description: 'Midday inspiration' },
  { id: 'evening', time: '18:00', label: 'Evening', icon: Moon, description: 'Evening reflection' },
];

// ============================================================================
// Component
// ============================================================================

export const NotificationSettings: React.FC<NotificationSettingsProps> = ({
  className = '',
  onClose,
  compact = false
}) => {
  // State
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    enabled: false,
    dailyWisdom: true,
    newPersonalities: true,
    weeklyDigest: false,
    preferredTime: '06:00',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
  });
  const [showCustomTime, setShowCustomTime] = useState(false);

  // ============================================================================
  // Effects
  // ============================================================================

  // Check notification permission on mount
  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission);
    }
    
    // Load saved preferences from localStorage
    const saved = localStorage.getItem('vimarsh_notification_preferences');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setPreferences(prev => ({ ...prev, ...parsed }));
      } catch {
        console.warn('Failed to parse saved notification preferences');
      }
    }
  }, []);

  // Save preferences to localStorage when changed
  useEffect(() => {
    localStorage.setItem('vimarsh_notification_preferences', JSON.stringify(preferences));
  }, [preferences]);

  // ============================================================================
  // Handlers
  // ============================================================================

  /**
   * Request notification permission from browser
   */
  const requestPermission = useCallback(async () => {
    if (!('Notification' in window)) {
      setError('Your browser does not support notifications');
      return false;
    }

    if (!('serviceWorker' in navigator)) {
      setError('Service workers are not supported');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await Notification.requestPermission();
      setPermission(result);

      if (result === 'granted') {
        // Register for push notifications
        const registration = await navigator.serviceWorker.ready;
        
        // Get VAPID public key from API
        try {
          const apiBase = getApiBaseUrl();
          const response = await fetch(`${apiBase}/notification/vapid-key`);
          
          if (response.ok) {
            const data = await response.json();
            const subscription = await registration.pushManager.subscribe({
              userVisibleOnly: true,
              applicationServerKey: data.publicKey
            });

            // Send subscription to server
            await fetch(`${apiBase}/notification/subscribe`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                subscription: subscription.toJSON(),
                preferences
              })
            });
          }
        } catch (apiError) {
          console.warn('Push subscription API not available:', apiError);
          // Still allow local notifications even without push server
        }

        setSuccess('Notifications enabled! You\'ll receive daily wisdom updates.');
        setPreferences(prev => ({ ...prev, enabled: true }));
        return true;
      } else if (result === 'denied') {
        setError('Notification permission denied. Please enable in browser settings.');
        return false;
      }

      return false;
    } catch (err) {
      console.error('Error requesting notification permission:', err);
      setError('Failed to enable notifications. Please try again.');
      return false;
    } finally {
      setLoading(false);
    }
  }, [preferences]);

  /**
   * Toggle notifications on/off
   */
  const toggleNotifications = useCallback(async () => {
    if (preferences.enabled) {
      // Disable notifications
      setPreferences(prev => ({ ...prev, enabled: false }));
      setSuccess('Notifications disabled');
      
      // Unsubscribe from push
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        if (subscription) {
          await subscription.unsubscribe();
          
          // Notify server
          const apiBase = getApiBaseUrl();
          await fetch(`${apiBase}/notification/unsubscribe`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ endpoint: subscription.endpoint })
          });
        }
      } catch {
        // Ignore errors during unsubscribe
      }
    } else {
      // Enable notifications
      if (permission !== 'granted') {
        await requestPermission();
      } else {
        setPreferences(prev => ({ ...prev, enabled: true }));
        setSuccess('Notifications enabled!');
      }
    }
  }, [preferences.enabled, permission, requestPermission]);

  /**
   * Update notification type preference
   */
  const updatePreference = useCallback((key: keyof NotificationPreferences, value: boolean | string) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
    
    // Save to server if enabled
    if (preferences.enabled) {
      const apiBase = getApiBaseUrl();
      fetch(`${apiBase}/notification/preferences`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...preferences, [key]: value })
      }).catch(() => {
        // Ignore errors - local storage is the source of truth
      });
    }
  }, [preferences]);

  /**
   * Select a time preset
   */
  const selectTimePreset = useCallback((time: string) => {
    updatePreference('preferredTime', time);
    setShowCustomTime(false);
    setSuccess(`Notification time set to ${formatTime(time)}`);
  }, [updatePreference]);

  /**
   * Send a test notification
   */
  const sendTestNotification = useCallback(async () => {
    if (permission !== 'granted') {
      setError('Please enable notifications first');
      return;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.showNotification('🙏 Vimarsh Test Notification', {
        body: 'Your daily wisdom notifications are working! "Peace comes from within. Do not seek it without." - Buddha',
        icon: '/logo192.png',
        badge: '/logo192.png',
        tag: 'test-notification',
        data: {
          category: 'test',
          url: '/'
        }
      });
      setSuccess('Test notification sent! Check your notifications.');
    } catch {
      setError('Failed to send test notification');
    }
  }, [permission]);

  // ============================================================================
  // Helpers
  // ============================================================================

  const formatTime = (time: string): string => {
    const [hours, minutes] = time.split(':').map(Number);
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const hour12 = hours % 12 || 12;
    return `${hour12}:${minutes.toString().padStart(2, '0')} ${ampm}`;
  };

  const isTimePresetSelected = (preset: string): boolean => {
    return preferences.preferredTime === preset;
  };

  // Clear messages after delay
  useEffect(() => {
    if (success || error) {
      const timer = setTimeout(() => {
        setSuccess(null);
        setError(null);
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [success, error]);

  // ============================================================================
  // Render
  // ============================================================================

  // Check for browser support
  const isSupported = 'Notification' in window && 'serviceWorker' in navigator;

  if (!isSupported) {
    return (
      <div className={`notification-settings-unsupported ${className}`}>
        <AlertCircle className="w-6 h-6 text-yellow-500" />
        <p className="text-sm text-gray-600">
          Your browser doesn't support notifications. Please use a modern browser like Chrome, Firefox, or Edge.
        </p>
      </div>
    );
  }

  // Compact version for inline use
  if (compact) {
    return (
      <button
        onClick={toggleNotifications}
        disabled={loading}
        className={`notification-toggle-compact ${preferences.enabled ? 'enabled' : ''} ${className}`}
        title={preferences.enabled ? 'Notifications enabled' : 'Enable notifications'}
      >
        {loading ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : preferences.enabled ? (
          <Bell className="w-5 h-5 text-amber-500" />
        ) : (
          <BellOff className="w-5 h-5 text-gray-400" />
        )}
      </button>
    );
  }

  return (
    <div className={`notification-settings ${className}`} style={{
      backgroundColor: 'white',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
      maxWidth: '480px',
      width: '100%'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #FF9933 0%, #CC7A29 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Bell className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>
              Notification Settings
            </h3>
            <p style={{ margin: 0, fontSize: '13px', color: '#666' }}>
              Get daily wisdom delivered to you
            </p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '8px'
            }}
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        )}
      </div>

      {/* Status Messages */}
      {error && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '12px',
          borderRadius: '8px',
          backgroundColor: '#FEE2E2',
          marginBottom: '16px'
        }}>
          <AlertCircle className="w-4 h-4 text-red-500" />
          <span style={{ fontSize: '14px', color: '#B91C1C' }}>{error}</span>
        </div>
      )}
      
      {success && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '12px',
          borderRadius: '8px',
          backgroundColor: '#D1FAE5',
          marginBottom: '16px'
        }}>
          <Check className="w-4 h-4 text-green-600" />
          <span style={{ fontSize: '14px', color: '#065F46' }}>{success}</span>
        </div>
      )}

      {/* Main Toggle */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px',
        backgroundColor: preferences.enabled ? '#FEF3E2' : '#F3F4F6',
        borderRadius: '12px',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {preferences.enabled ? (
            <Bell className="w-5 h-5 text-amber-600" />
          ) : (
            <BellOff className="w-5 h-5 text-gray-400" />
          )}
          <div>
            <p style={{ margin: 0, fontWeight: 500, fontSize: '15px' }}>
              {preferences.enabled ? 'Notifications Enabled' : 'Notifications Disabled'}
            </p>
            <p style={{ margin: 0, fontSize: '12px', color: '#666' }}>
              {permission === 'denied' 
                ? 'Blocked in browser settings' 
                : 'Toggle to enable/disable all notifications'}
            </p>
          </div>
        </div>
        <button
          onClick={toggleNotifications}
          disabled={loading || permission === 'denied'}
          style={{
            width: '52px',
            height: '28px',
            borderRadius: '14px',
            backgroundColor: preferences.enabled ? '#FF9933' : '#D1D5DB',
            border: 'none',
            cursor: loading || permission === 'denied' ? 'not-allowed' : 'pointer',
            position: 'relative',
            transition: 'background-color 0.2s ease'
          }}
        >
          <div style={{
            width: '22px',
            height: '22px',
            borderRadius: '11px',
            backgroundColor: 'white',
            position: 'absolute',
            top: '3px',
            left: preferences.enabled ? '27px' : '3px',
            transition: 'left 0.2s ease',
            boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
          }}>
            {loading && (
              <Loader2 className="w-4 h-4 animate-spin absolute top-0.5 left-0.5" style={{ color: '#FF9933' }} />
            )}
          </div>
        </button>
      </div>

      {/* Notification Types */}
      {preferences.enabled && (
        <>
          <h4 style={{ fontSize: '14px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>
            Notification Types
          </h4>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
            {/* Daily Wisdom */}
            <label style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px',
              backgroundColor: '#F9FAFB',
              borderRadius: '8px',
              cursor: 'pointer'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Sparkles className="w-4 h-4 text-amber-500" />
                <span style={{ fontSize: '14px' }}>Daily Wisdom</span>
              </div>
              <input
                type="checkbox"
                checked={preferences.dailyWisdom}
                onChange={(e) => updatePreference('dailyWisdom', e.target.checked)}
                style={{ accentColor: '#FF9933', width: '18px', height: '18px' }}
              />
            </label>

            {/* New Personalities */}
            <label style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px',
              backgroundColor: '#F9FAFB',
              borderRadius: '8px',
              cursor: 'pointer'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Settings className="w-4 h-4 text-purple-500" />
                <span style={{ fontSize: '14px' }}>New Personalities</span>
              </div>
              <input
                type="checkbox"
                checked={preferences.newPersonalities}
                onChange={(e) => updatePreference('newPersonalities', e.target.checked)}
                style={{ accentColor: '#FF9933', width: '18px', height: '18px' }}
              />
            </label>

            {/* Weekly Digest */}
            <label style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px',
              backgroundColor: '#F9FAFB',
              borderRadius: '8px',
              cursor: 'pointer'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Sun className="w-4 h-4 text-blue-500" />
                <span style={{ fontSize: '14px' }}>Weekly Digest</span>
              </div>
              <input
                type="checkbox"
                checked={preferences.weeklyDigest}
                onChange={(e) => updatePreference('weeklyDigest', e.target.checked)}
                style={{ accentColor: '#FF9933', width: '18px', height: '18px' }}
              />
            </label>
          </div>

          {/* Time Preference */}
          {preferences.dailyWisdom && (
            <>
              <h4 style={{ fontSize: '14px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>
                <Clock className="w-4 h-4 inline mr-2" />
                Preferred Time for Daily Wisdom
              </h4>
              
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
                {TIME_PRESETS.map(preset => (
                  <button
                    key={preset.id}
                    onClick={() => selectTimePreset(preset.time)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      border: '2px solid',
                      borderColor: isTimePresetSelected(preset.time) ? '#FF9933' : '#E5E7EB',
                      backgroundColor: isTimePresetSelected(preset.time) ? '#FEF3E2' : 'white',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <preset.icon className="w-4 h-4" style={{
                      color: isTimePresetSelected(preset.time) ? '#FF9933' : '#6B7280'
                    }} />
                    <span style={{ fontSize: '13px', fontWeight: 500 }}>{preset.label}</span>
                  </button>
                ))}
                
                <button
                  onClick={() => setShowCustomTime(!showCustomTime)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '2px solid',
                    borderColor: showCustomTime ? '#FF9933' : '#E5E7EB',
                    backgroundColor: showCustomTime ? '#FEF3E2' : 'white',
                    cursor: 'pointer'
                  }}
                >
                  <Clock className="w-4 h-4" style={{ color: showCustomTime ? '#FF9933' : '#6B7280' }} />
                  <span style={{ fontSize: '13px', fontWeight: 500 }}>Custom</span>
                </button>
              </div>

              {showCustomTime && (
                <input
                  type="time"
                  value={preferences.preferredTime}
                  onChange={(e) => updatePreference('preferredTime', e.target.value)}
                  style={{
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '2px solid #FF9933',
                    fontSize: '14px',
                    marginBottom: '12px',
                    width: '140px'
                  }}
                />
              )}

              <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '8px' }}>
                Current time: {formatTime(preferences.preferredTime)} ({preferences.timezone})
              </p>
            </>
          )}

          {/* Test Notification */}
          <button
            onClick={sendTestNotification}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              width: '100%',
              padding: '12px',
              marginTop: '20px',
              borderRadius: '8px',
              border: '1px solid #E5E7EB',
              backgroundColor: 'white',
              cursor: 'pointer',
              fontSize: '14px',
              color: '#374151'
            }}
          >
            <Bell className="w-4 h-4" />
            Send Test Notification
          </button>
        </>
      )}

      {/* Permission Denied Warning */}
      {permission === 'denied' && (
        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px',
          padding: '16px',
          backgroundColor: '#FEF2F2',
          borderRadius: '8px',
          marginTop: '16px'
        }}>
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p style={{ margin: 0, fontSize: '14px', fontWeight: 500, color: '#B91C1C' }}>
              Notifications Blocked
            </p>
            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#7F1D1D' }}>
              You've blocked notifications for this site. To enable them:
            </p>
            <ol style={{ margin: '8px 0 0 0', paddingLeft: '20px', fontSize: '12px', color: '#7F1D1D' }}>
              <li>Click the lock icon in your browser's address bar</li>
              <li>Find "Notifications" setting</li>
              <li>Change from "Block" to "Allow"</li>
              <li>Refresh this page</li>
            </ol>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationSettings;
