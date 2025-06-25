import React, { useState, useEffect } from 'react';
import { useAnalytics } from '../contexts/AnalyticsContext';
import './PrivacySettings.css';

interface PrivacySettingsProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

interface PrivacyPreferences {
  analyticsEnabled: boolean;
  behaviorTracking: boolean;
  performanceMetrics: boolean;
  errorReporting: boolean;
  dataRetentionDays: number;
}

const PrivacySettings: React.FC<PrivacySettingsProps> = ({
  isOpen,
  onClose,
  className = ''
}) => {
  const analytics = useAnalytics();
  
  const [preferences, setPreferences] = useState<PrivacyPreferences>({
    analyticsEnabled: analytics?.isEnabled ?? false,
    behaviorTracking: true,
    performanceMetrics: true,
    errorReporting: true,
    dataRetentionDays: 30
  });

  const [showDataSummary, setShowDataSummary] = useState(false);
  const [dataSummary, setDataSummary] = useState<any>(null);

  // Load preferences from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('vimarsh_privacy_preferences');
      if (saved) {
        const savedPreferences = JSON.parse(saved);
        setPreferences(prev => ({ ...prev, ...savedPreferences }));
      }
    } catch (error) {
      console.warn('Failed to load privacy preferences:', error);
    }
  }, []);

  // Save preferences to localStorage when they change
  useEffect(() => {
    try {
      localStorage.setItem('vimarsh_privacy_preferences', JSON.stringify(preferences));
      analytics?.setEnabled(preferences.analyticsEnabled);
    } catch (error) {
      console.warn('Failed to save privacy preferences:', error);
    }
  }, [preferences, analytics]);

  const handlePreferenceChange = (key: keyof PrivacyPreferences, value: boolean | number) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }));

    // Track the privacy setting change
    analytics?.trackEvent('privacy_setting_changed', 'interaction', {
      setting: key,
      value,
      feature: 'privacy_controls'
    });
  };

  const handleViewDataSummary = () => {
    const summary = analytics?.getAnalyticsSummary();
    setDataSummary(summary);
    setShowDataSummary(true);
    
    analytics?.trackEvent('data_summary_viewed', 'interaction', {
      feature: 'privacy_controls'
    });
  };

  const handleExportData = () => {
    analytics?.exportUserData();
    
    analytics?.trackEvent('data_exported', 'interaction', {
      feature: 'privacy_controls'
    });
  };

  const handleClearData = () => {
    if (window.confirm('Are you sure you want to clear all analytics data? This action cannot be undone.')) {
      analytics?.clearAnalyticsData();
      setDataSummary(null);
      
      analytics?.trackEvent('data_cleared', 'interaction', {
        feature: 'privacy_controls'
      });
      
      alert('Analytics data has been cleared.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className={`privacy-settings-overlay ${className}`}>
      <div className="privacy-settings-modal">
        <div className="privacy-settings-header">
          <h2>Privacy & Analytics Settings</h2>
          <button 
            className="close-button"
            onClick={onClose}
            aria-label="Close privacy settings"
          >
            ✕
          </button>
        </div>

        <div className="privacy-settings-content">
          {/* Analytics Preferences */}
          <section className="privacy-section">
            <h3>Analytics Preferences</h3>
            <p className="privacy-description">
              Vimarsh uses privacy-respecting analytics to improve your spiritual guidance experience. 
              All data is anonymized and stored locally on your device.
            </p>

            <div className="privacy-option">
              <label className="privacy-toggle">
                <input
                  type="checkbox"
                  checked={preferences.analyticsEnabled}
                  onChange={(e) => handlePreferenceChange('analyticsEnabled', e.target.checked)}
                />
                <span className="toggle-slider"></span>
                <span className="toggle-label">Enable Analytics</span>
              </label>
              <p className="option-description">
                Allow Vimarsh to collect anonymous usage data to improve spiritual guidance quality.
              </p>
            </div>

            <div className="privacy-option">
              <label className="privacy-toggle">
                <input
                  type="checkbox"
                  checked={preferences.behaviorTracking}
                  onChange={(e) => handlePreferenceChange('behaviorTracking', e.target.checked)}
                  disabled={!preferences.analyticsEnabled}
                />
                <span className="toggle-slider"></span>
                <span className="toggle-label">Behavior Insights</span>
              </label>
              <p className="option-description">
                Track spiritual topics and interaction patterns to provide personalized guidance.
              </p>
            </div>

            <div className="privacy-option">
              <label className="privacy-toggle">
                <input
                  type="checkbox"
                  checked={preferences.performanceMetrics}
                  onChange={(e) => handlePreferenceChange('performanceMetrics', e.target.checked)}
                  disabled={!preferences.analyticsEnabled}
                />
                <span className="toggle-slider"></span>
                <span className="toggle-label">Performance Metrics</span>
              </label>
              <p className="option-description">
                Collect performance data to optimize response times and voice quality.
              </p>
            </div>

            <div className="privacy-option">
              <label className="privacy-toggle">
                <input
                  type="checkbox"
                  checked={preferences.errorReporting}
                  onChange={(e) => handlePreferenceChange('errorReporting', e.target.checked)}
                  disabled={!preferences.analyticsEnabled}
                />
                <span className="toggle-slider"></span>
                <span className="toggle-label">Error Reporting</span>
              </label>
              <p className="option-description">
                Automatically report errors to help improve the spiritual guidance experience.
              </p>
            </div>
          </section>

          {/* Data Management */}
          <section className="privacy-section">
            <h3>Data Management</h3>
            
            <div className="data-controls">
              <button 
                className="data-control-button"
                onClick={handleViewDataSummary}
              >
                View Data Summary
              </button>
              
              <button 
                className="data-control-button"
                onClick={handleExportData}
              >
                Export My Data
              </button>
              
              <button 
                className="data-control-button danger"
                onClick={handleClearData}
              >
                Clear All Data
              </button>
            </div>

            <div className="data-retention">
              <label>
                Data Retention Period:
                <select
                  value={preferences.dataRetentionDays}
                  onChange={(e) => handlePreferenceChange('dataRetentionDays', parseInt(e.target.value))}
                >
                  <option value={7}>7 days</option>
                  <option value={30}>30 days</option>
                  <option value={90}>90 days</option>
                  <option value={365}>1 year</option>
                </select>
              </label>
            </div>
          </section>

          {/* Current Session Info */}
          <section className="privacy-section">
            <h3>Current Session</h3>
            <div className="session-info">
              <p><strong>Session ID:</strong> {analytics?.sessionId || 'N/A'}</p>
              <p><strong>Questions Asked:</strong> {analytics?.userBehavior?.questionsAsked || 0}</p>
              <p><strong>Session Duration:</strong> {Math.round((analytics?.userBehavior?.sessionDuration || 0) / 60000)} minutes</p>
              <p><strong>Language:</strong> {analytics?.userBehavior?.languagePreference || 'en'}</p>
            </div>
          </section>

          {/* Data Summary Modal */}
          {showDataSummary && dataSummary && (
            <div className="data-summary-modal">
              <div className="data-summary-content">
                <h4>Your Analytics Data Summary</h4>
                <div className="summary-stats">
                  <p><strong>Total Events:</strong> {dataSummary.totalEvents}</p>
                  <p><strong>Sessions:</strong> {dataSummary.sessionCount}</p>
                  <p><strong>Spiritual Topics:</strong> {analytics?.userBehavior?.spiritualTopics?.join(', ') || 'None'}</p>
                  <p><strong>Voice Usage:</strong> {analytics?.userBehavior?.voiceUsage || 0} times</p>
                  <p><strong>Text Usage:</strong> {analytics?.userBehavior?.textUsage || 0} times</p>
                  <p><strong>Features Used:</strong> {analytics?.userBehavior?.featuresUsed?.join(', ') || 'None'}</p>
                </div>
                <div className="category-breakdown">
                  <h5>Event Categories:</h5>
                  {Object.entries(dataSummary.categories).map(([category, count]) => (
                    <p key={category}><strong>{category}:</strong> {count as number}</p>
                  ))}
                </div>
                <button 
                  className="close-summary-button"
                  onClick={() => setShowDataSummary(false)}
                >
                  Close
                </button>
              </div>
            </div>
          )}

          {/* Privacy Notice */}
          <section className="privacy-notice">
            <h4>Privacy Commitment</h4>
            <ul>
              <li>All analytics data is stored locally on your device</li>
              <li>No personal information is collected or transmitted</li>
              <li>Spiritual guidance content is not stored or analyzed</li>
              <li>You can export or delete your data at any time</li>
              <li>All processing respects your cultural and spiritual privacy</li>
            </ul>
          </section>
        </div>

        <div className="privacy-settings-footer">
          <button className="save-button" onClick={onClose}>
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default PrivacySettings;
