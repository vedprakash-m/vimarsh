/**
 * NotificationPreferencesPanel Component
 * Full preferences panel for notification settings
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Divider,
  Alert,
  CircularProgress,
  Skeleton,
  useTheme,
  alpha
} from '@mui/material';
import { Bell, Clock, Moon, Send, RefreshCw } from 'lucide-react';
import { useNotifications } from './useNotifications';
import type { NotificationPreferencesUpdate } from './types';

// Common timezones
const TIMEZONES = [
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
  { value: 'America/Chicago', label: 'Central Time (CT)' },
  { value: 'America/Denver', label: 'Mountain Time (MT)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
  { value: 'Europe/London', label: 'London (GMT/BST)' },
  { value: 'Europe/Paris', label: 'Paris (CET)' },
  { value: 'Asia/Kolkata', label: 'India (IST)' },
  { value: 'Asia/Tokyo', label: 'Tokyo (JST)' },
  { value: 'Australia/Sydney', label: 'Sydney (AEST)' },
  { value: 'UTC', label: 'UTC' }
];

interface NotificationPreferencesPanelProps {
  onSave?: () => void;
}

const NotificationPreferencesPanel: React.FC<NotificationPreferencesPanelProps> = ({ onSave }) => {
  const theme = useTheme();
  const {
    isSupported,
    isSubscribed,
    isLoading,
    error,
    preferences,
    subscribe,
    unsubscribe,
    updatePreferences,
    sendTest,
    refresh
  } = useNotifications();

  // Local state for form
  const [formState, setFormState] = useState<NotificationPreferencesUpdate>({
    enabled: true,
    daily_wisdom_enabled: true,
    streak_reminders_enabled: true,
    achievement_notifications_enabled: true,
    weekly_summary_enabled: true,
    preferred_time_hour: 9,
    preferred_time_minute: 0,
    timezone: 'America/New_York',
    quiet_hours_start: 22,
    quiet_hours_end: 7
  });

  const [saving, setSaving] = useState(false);
  const [sendingTest, setSendingTest] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Load preferences into form
  useEffect(() => {
    if (preferences) {
      setFormState({
        enabled: preferences.enabled,
        daily_wisdom_enabled: preferences.daily_wisdom_enabled,
        streak_reminders_enabled: preferences.streak_reminders_enabled,
        achievement_notifications_enabled: preferences.achievement_notifications_enabled,
        weekly_summary_enabled: preferences.weekly_summary_enabled,
        preferred_time_hour: preferences.preferred_time_hour,
        preferred_time_minute: preferences.preferred_time_minute,
        timezone: preferences.timezone,
        quiet_hours_start: preferences.quiet_hours_start,
        quiet_hours_end: preferences.quiet_hours_end
      });
    }
  }, [preferences]);

  const handleToggle = (field: keyof NotificationPreferencesUpdate) => {
    setFormState(prev => ({ ...prev, [field]: !prev[field] }));
    setSaveSuccess(false);
  };

  const handleChange = (field: keyof NotificationPreferencesUpdate, value: unknown) => {
    setFormState(prev => ({ ...prev, [field]: value }));
    setSaveSuccess(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveSuccess(false);
    try {
      await updatePreferences(formState);
      setSaveSuccess(true);
      onSave?.();
    } catch (err) {
      console.error('Save error:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleSubscribeToggle = async () => {
    if (isSubscribed) {
      await unsubscribe();
    } else {
      await subscribe();
    }
  };

  const handleSendTest = async () => {
    setSendingTest(true);
    try {
      await sendTest();
    } finally {
      setSendingTest(false);
    }
  };

  // Not supported
  if (!isSupported) {
    return (
      <Alert severity="info">
        Push notifications are not supported in this browser.
      </Alert>
    );
  }

  // Loading state
  if (isLoading && !preferences) {
    return (
      <Paper sx={{ p: 3 }}>
        <Skeleton variant="text" width={200} height={32} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={56} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={56} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={56} />
      </Paper>
    );
  }

  const formatTime = (hour: number, minute: number) => {
    const h = hour % 12 || 12;
    const ampm = hour < 12 ? 'AM' : 'PM';
    return `${h}:${minute.toString().padStart(2, '0')} ${ampm}`;
  };

  return (
    <Paper sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <Bell size={24} color={theme.palette.primary.main} />
        <Typography variant="h6">Notification Settings</Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Button
          size="small"
          startIcon={<RefreshCw size={16} />}
          onClick={refresh}
          disabled={isLoading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Settings saved successfully!
        </Alert>
      )}

      {/* Master Toggle */}
      <Box
        sx={{
          p: 2,
          mb: 3,
          borderRadius: 2,
          bgcolor: isSubscribed 
            ? alpha(theme.palette.success.main, 0.1) 
            : alpha(theme.palette.grey[500], 0.1)
        }}
      >
        <FormControlLabel
          control={
            <Switch
              checked={isSubscribed}
              onChange={handleSubscribeToggle}
              disabled={isLoading}
            />
          }
          label={
            <Box>
              <Typography variant="subtitle1" fontWeight="bold">
                Push Notifications
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {isSubscribed 
                  ? 'Enabled - You will receive notifications' 
                  : 'Disabled - Enable to receive notifications'}
              </Typography>
            </Box>
          }
        />
      </Box>

      {/* Notification Types */}
      {isSubscribed && (
        <>
          <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
            NOTIFICATION TYPES
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={formState.daily_wisdom_enabled}
                onChange={() => handleToggle('daily_wisdom_enabled')}
              />
            }
            label="Daily Wisdom Reminders"
            sx={{ display: 'block', mb: 1 }}
          />

          <FormControlLabel
            control={
              <Switch
                checked={formState.streak_reminders_enabled}
                onChange={() => handleToggle('streak_reminders_enabled')}
              />
            }
            label="Streak Reminders"
            sx={{ display: 'block', mb: 1 }}
          />

          <FormControlLabel
            control={
              <Switch
                checked={formState.achievement_notifications_enabled}
                onChange={() => handleToggle('achievement_notifications_enabled')}
              />
            }
            label="Achievement Unlocks"
            sx={{ display: 'block', mb: 1 }}
          />

          <FormControlLabel
            control={
              <Switch
                checked={formState.weekly_summary_enabled}
                onChange={() => handleToggle('weekly_summary_enabled')}
              />
            }
            label="Weekly Summary"
            sx={{ display: 'block', mb: 3 }}
          />

          <Divider sx={{ my: 3 }} />

          {/* Time Settings */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Clock size={20} color={theme.palette.text.secondary} />
            <Typography variant="subtitle2" color="text.secondary">
              PREFERRED TIME
            </Typography>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Daily wisdom notifications will be sent at: <strong>{formatTime(formState.preferred_time_hour || 9, formState.preferred_time_minute || 0)}</strong>
          </Typography>

          <Box sx={{ px: 2, mb: 3 }}>
            <Typography variant="caption" color="text.secondary">
              Hour of day
            </Typography>
            <Slider
              value={formState.preferred_time_hour || 9}
              min={0}
              max={23}
              step={1}
              marks={[
                { value: 6, label: '6AM' },
                { value: 12, label: '12PM' },
                { value: 18, label: '6PM' }
              ]}
              valueLabelDisplay="auto"
              valueLabelFormat={(v) => formatTime(v, 0)}
              onChange={(_, value) => handleChange('preferred_time_hour', value as number)}
            />
          </Box>

          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Timezone</InputLabel>
            <Select
              value={formState.timezone || 'UTC'}
              label="Timezone"
              onChange={(e) => handleChange('timezone', e.target.value)}
            >
              {TIMEZONES.map((tz) => (
                <MenuItem key={tz.value} value={tz.value}>
                  {tz.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Divider sx={{ my: 3 }} />

          {/* Quiet Hours */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Moon size={20} color={theme.palette.text.secondary} />
            <Typography variant="subtitle2" color="text.secondary">
              QUIET HOURS
            </Typography>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            No notifications between <strong>{formatTime(formState.quiet_hours_start || 22, 0)}</strong> and <strong>{formatTime(formState.quiet_hours_end || 7, 0)}</strong>
          </Typography>

          <Box sx={{ px: 2, mb: 3 }}>
            <Typography variant="caption" color="text.secondary">
              Start quiet hours
            </Typography>
            <Slider
              value={formState.quiet_hours_start || 22}
              min={18}
              max={23}
              step={1}
              valueLabelDisplay="auto"
              valueLabelFormat={(v) => formatTime(v, 0)}
              onChange={(_, value) => handleChange('quiet_hours_start', value as number)}
            />
          </Box>

          <Box sx={{ px: 2, mb: 3 }}>
            <Typography variant="caption" color="text.secondary">
              End quiet hours
            </Typography>
            <Slider
              value={formState.quiet_hours_end || 7}
              min={5}
              max={10}
              step={1}
              valueLabelDisplay="auto"
              valueLabelFormat={(v) => formatTime(v, 0)}
              onChange={(_, value) => handleChange('quiet_hours_end', value as number)}
            />
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Actions */}
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              onClick={handleSave}
              disabled={saving}
              startIcon={saving ? <CircularProgress size={18} /> : undefined}
            >
              {saving ? 'Saving...' : 'Save Preferences'}
            </Button>

            <Button
              variant="outlined"
              onClick={handleSendTest}
              disabled={sendingTest}
              startIcon={sendingTest ? <CircularProgress size={18} /> : <Send size={18} />}
            >
              {sendingTest ? 'Sending...' : 'Send Test'}
            </Button>
          </Box>
        </>
      )}
    </Paper>
  );
};

export default NotificationPreferencesPanel;
