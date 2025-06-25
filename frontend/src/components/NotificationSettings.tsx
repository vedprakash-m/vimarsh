import React, { useState } from 'react';
import { Bell, BellOff, Settings, TestTube, Clock, Globe, Volume2 } from 'lucide-react';
import { useNotifications, NotificationPreferences } from '../utils/notifications';
import { useLanguage } from '../contexts/LanguageContext';

interface NotificationSettingsProps {
  className?: string;
  onClose?: () => void;
}

export const NotificationSettings: React.FC<NotificationSettingsProps> = ({ 
  className = '', 
  onClose 
}) => {
  const { t } = useLanguage();
  const {
    preferences,
    permissionStatus,
    isSupported,
    enableNotifications,
    disableNotifications,
    updatePreferences,
    testNotification
  } = useNotifications();

  const [isLoading, setIsLoading] = useState(false);
  const [testingNotification, setTestingNotification] = useState(false);

  const handleEnableNotifications = async () => {
    setIsLoading(true);
    try {
      const success = await enableNotifications();
      if (!success) {
        alert(t('notificationPermissionDenied'));
      }
    } catch (error) {
      console.error('Failed to enable notifications:', error);
      alert(t('notificationError'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisableNotifications = () => {
    disableNotifications();
  };

  const handlePreferenceChange = (key: keyof NotificationPreferences, value: any) => {
    updatePreferences({ [key]: value });
  };

  const handleTestNotification = async () => {
    setTestingNotification(true);
    try {
      const success = await testNotification();
      if (!success) {
        alert(t('testNotificationFailed'));
      }
    } catch (error) {
      console.error('Test notification failed:', error);
      alert(t('testNotificationFailed'));
    } finally {
      setTestingNotification(false);
    }
  };

  if (!isSupported) {
    return (
      <div className={`notification-settings notification-settings--unsupported ${className}`}>
        <div className="notification-settings__header">
          <BellOff className="notification-settings__icon" size={24} />
          <h3 className="notification-settings__title">{t('notificationsNotSupported')}</h3>
        </div>
        <p className="notification-settings__description">
          {t('notificationsSupportDescription')}
        </p>
      </div>
    );
  }

  return (
    <div className={`notification-settings ${className}`}>
      <div className="notification-settings__header">
        <Bell className="notification-settings__icon" size={24} />
        <h3 className="notification-settings__title">{t('notificationSettings')}</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="notification-settings__close"
            aria-label={t('close')}
          >
            ×
          </button>
        )}
      </div>

      {/* Enable/Disable Notifications */}
      <div className="notification-settings__section">
        <div className="notification-settings__option">
          <div className="notification-settings__option-info">
            <label className="notification-settings__label">
              {t('enableNotifications')}
            </label>
            <p className="notification-settings__description">
              {t('notificationsDescription')}
            </p>
          </div>
          <div className="notification-settings__controls">
            {permissionStatus === 'default' && (
              <button
                onClick={handleEnableNotifications}
                disabled={isLoading}
                className="notification-settings__button notification-settings__button--primary"
              >
                {isLoading ? t('enabling') : t('enable')}
              </button>
            )}
            {permissionStatus === 'granted' && (
              <div className="notification-settings__toggle-group">
                <button
                  onClick={preferences.enabled ? handleDisableNotifications : handleEnableNotifications}
                  className={`notification-settings__toggle ${preferences.enabled ? 'notification-settings__toggle--enabled' : ''}`}
                  aria-label={preferences.enabled ? t('disableNotifications') : t('enableNotifications')}
                >
                  <span className="notification-settings__toggle-slider"></span>
                </button>
                <span className="notification-settings__status">
                  {preferences.enabled ? t('enabled') : t('disabled')}
                </span>
              </div>
            )}
            {permissionStatus === 'denied' && (
              <span className="notification-settings__status notification-settings__status--error">
                {t('notificationPermissionDenied')}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Notification Categories */}
      {preferences.enabled && (
        <>
          <div className="notification-settings__section">
            <h4 className="notification-settings__section-title">{t('notificationTypes')}</h4>
            
            <div className="notification-settings__option">
              <label className="notification-settings__checkbox-label">
                <input
                  type="checkbox"
                  checked={preferences.dailyWisdom}
                  onChange={(e) => handlePreferenceChange('dailyWisdom', e.target.checked)}
                  className="notification-settings__checkbox"
                />
                <span className="notification-settings__checkbox-custom"></span>
                <span>{t('dailyWisdom')}</span>
              </label>
            </div>

            <div className="notification-settings__option">
              <label className="notification-settings__checkbox-label">
                <input
                  type="checkbox"
                  checked={preferences.meditationReminders}
                  onChange={(e) => handlePreferenceChange('meditationReminders', e.target.checked)}
                  className="notification-settings__checkbox"
                />
                <span className="notification-settings__checkbox-custom"></span>
                <span>{t('meditationReminders')}</span>
              </label>
            </div>

            <div className="notification-settings__option">
              <label className="notification-settings__checkbox-label">
                <input
                  type="checkbox"
                  checked={preferences.spiritualQuotes}
                  onChange={(e) => handlePreferenceChange('spiritualQuotes', e.target.checked)}
                  className="notification-settings__checkbox"
                />
                <span className="notification-settings__checkbox-custom"></span>
                <span>{t('spiritualQuotes')}</span>
              </label>
            </div>

            <div className="notification-settings__option">
              <label className="notification-settings__checkbox-label">
                <input
                  type="checkbox"
                  checked={preferences.teachings}
                  onChange={(e) => handlePreferenceChange('teachings', e.target.checked)}
                  className="notification-settings__checkbox"
                />
                <span className="notification-settings__checkbox-custom"></span>
                <span>{t('teachings')}</span>
              </label>
            </div>
          </div>

          {/* Timing Settings */}
          <div className="notification-settings__section">
            <h4 className="notification-settings__section-title">{t('timingSettings')}</h4>
            
            <div className="notification-settings__option">
              <label className="notification-settings__label">
                <Clock size={16} />
                {t('preferredTime')}
              </label>
              <input
                type="time"
                value={preferences.preferredTime}
                onChange={(e) => handlePreferenceChange('preferredTime', e.target.value)}
                className="notification-settings__time-input"
              />
            </div>

            <div className="notification-settings__option">
              <label className="notification-settings__label">
                <Volume2 size={16} />
                {t('frequency')}
              </label>
              <select
                value={preferences.frequency}
                onChange={(e) => handlePreferenceChange('frequency', e.target.value)}
                className="notification-settings__select"
              >
                <option value="daily">{t('daily')}</option>
                <option value="every_other_day">{t('everyOtherDay')}</option>
                <option value="weekly">{t('weekly')}</option>
              </select>
            </div>

            <div className="notification-settings__option">
              <label className="notification-settings__label">
                <Globe size={16} />
                {t('notificationLanguage')}
              </label>
              <select
                value={preferences.language}
                onChange={(e) => handlePreferenceChange('language', e.target.value)}
                className="notification-settings__select"
              >
                <option value="en">{t('english')}</option>
                <option value="hi">{t('hindi')}</option>
              </select>
            </div>
          </div>

          {/* Test Notification */}
          <div className="notification-settings__section">
            <div className="notification-settings__option">
              <div className="notification-settings__option-info">
                <label className="notification-settings__label">
                  <TestTube size={16} />
                  {t('testNotification')}
                </label>
                <p className="notification-settings__description">
                  {t('testNotificationDescription')}
                </p>
              </div>
              <button
                onClick={handleTestNotification}
                disabled={testingNotification || !preferences.enabled}
                className="notification-settings__button notification-settings__button--secondary"
              >
                {testingNotification ? t('sending') : t('sendTest')}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default NotificationSettings;
