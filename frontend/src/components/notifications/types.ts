/**
 * Notification Types
 * Type definitions for push notifications and preferences
 */

export interface PushSubscription {
  endpoint: string;
  keys: {
    p256dh: string;
    auth: string;
  };
}

export interface NotificationPreferences {
  user_id: string;
  enabled: boolean;
  daily_wisdom_enabled: boolean;
  streak_reminders_enabled: boolean;
  achievement_notifications_enabled: boolean;
  weekly_summary_enabled: boolean;
  preferred_time_hour: number;
  preferred_time_minute: number;
  timezone: string;
  max_notifications_per_day: number;
  quiet_hours_start: number;
  quiet_hours_end: number;
  last_daily_wisdom_at: string | null;
  last_streak_reminder_at: string | null;
  notifications_sent_today: number;
}

export interface NotificationStatus {
  is_subscribed: boolean;
  subscription_count: number;
  notifications_enabled: boolean;
  daily_wisdom_enabled: boolean;
  streak_reminders_enabled: boolean;
  preferred_time: string;
  timezone: string;
  notifications_sent_today: number;
}

export interface NotificationPreferencesUpdate {
  enabled?: boolean;
  daily_wisdom_enabled?: boolean;
  streak_reminders_enabled?: boolean;
  achievement_notifications_enabled?: boolean;
  weekly_summary_enabled?: boolean;
  preferred_time_hour?: number;
  preferred_time_minute?: number;
  timezone?: string;
  quiet_hours_start?: number;
  quiet_hours_end?: number;
  max_notifications_per_day?: number;
}

export type NotificationType = 
  | 'daily_wisdom'
  | 'streak_reminder'
  | 'streak_at_risk'
  | 'streak_broken'
  | 'streak_milestone'
  | 'achievement_unlocked'
  | 'new_personality'
  | 'weekly_summary'
  | 'welcome_back'
  | 'engagement_nudge';

export interface NotificationPayload {
  title: string;
  body: string;
  icon?: string;
  badge?: string;
  tag?: string;
  requireInteraction?: boolean;
  data?: {
    type: NotificationType;
    url?: string;
    [key: string]: unknown;
  };
  actions?: Array<{
    action: string;
    title: string;
  }>;
}
