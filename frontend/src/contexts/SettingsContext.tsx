import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import spiritualGuidanceAPI from '../utils/api';

export interface ExperiencePreferences {
  conversation_style: 'brief' | 'balanced' | 'detailed';
  language: 'en' | 'hi';
  formality: 'very_formal' | 'respectful' | 'friendly' | 'casual';
  favorite_personalities: string[];
  theme: 'light' | 'auto' | 'dark';
  text_size: 'small' | 'medium' | 'large';
  reduce_animations: boolean;
}

export interface NotificationPreferences {
  daily_wisdom_enabled: boolean;
  preferred_time: string;
  timezone: string;
  quiet_hours_enabled: boolean;
  quiet_start: string;
  quiet_end: string;
  types: {
    daily_wisdom: boolean;
    streak_reminders: boolean;
    achievements: boolean;
    weekly_summary: boolean;
  };
}

export interface MemoryPreferences {
  remember_conversations: boolean;
  connect_insights: boolean;
  track_emotions: boolean;
  suggest_topics: boolean;
  privacy_mode: 'standard' | 'private' | 'minimal';
  data_retention_days: number;
  analytics_consent: boolean;
  research_consent: boolean;
}

export interface UserSettings {
  user_id: string;
  experience_preferences: ExperiencePreferences;
  notification_preferences: NotificationPreferences;
  memory_preferences: MemoryPreferences;
  updated_at: string;
}

export interface JourneyStats {
  current_streak: number;
  total_conversations: number;
  achievements_unlocked: number;
  wisdom_level: string;
  domain_exploration: {
    spiritual: number;
    scientific: number;
    philosophical: number;
    leadership: number;
    literary: number;
    psychology: number;
  };
}

export interface AIUsage {
  monthly_cost: number;
  monthly_limit: number;
  status: 'well_within_limits' | 'approaching_limit' | 'at_limit';
  trend: 'similar_to_last_month' | 'slightly_higher' | 'much_higher';
}

export interface UserProfile {
  user: {
    user_id: string;
    name: string;
    email: string;
    profile_picture?: string;
    member_since: string;
  };
  journey_stats: JourneyStats;
  preferences: UserSettings;
  ai_usage: AIUsage;
}

// Default preference values
const defaultExperiencePrefs: ExperiencePreferences = {
  conversation_style: 'balanced',
  language: 'en',
  formality: 'respectful',
  favorite_personalities: [],
  theme: 'auto',
  text_size: 'medium',
  reduce_animations: false,
};

const defaultNotificationPrefs: NotificationPreferences = {
  daily_wisdom_enabled: false,
  preferred_time: '09:00',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  quiet_hours_enabled: false,
  quiet_start: '22:00',
  quiet_end: '07:00',
  types: {
    daily_wisdom: false,
    streak_reminders: false,
    achievements: false,
    weekly_summary: false,
  },
};

const defaultMemoryPrefs: MemoryPreferences = {
  remember_conversations: true,
  connect_insights: true,
  track_emotions: false,
  suggest_topics: true,
  privacy_mode: 'standard',
  data_retention_days: 365,
  analytics_consent: false,
  research_consent: false,
};

interface SettingsContextType {
  settings: UserSettings | null;
  profile: UserProfile | null;
  loading: boolean;
  error: string | null;
  updateSettings: (updates: Partial<UserSettings>) => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

let saveTimeout: NodeJS.Timeout | null = null;

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingUpdates, setPendingUpdates] = useState<Partial<UserSettings> | null>(null);

  // Fetch user profile on mount
  const refreshProfile = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await spiritualGuidanceAPI.getUserProfile();
      
      // Map API response to UserProfile structure
      // Using type assertions through unknown for API responses
      const mappedProfile: UserProfile = {
        user: {
          user_id: data.user_id,
          name: data.name,
          email: data.email,
          member_since: data.member_since || new Date().toISOString(),
        },
        journey_stats: (data.journey_stats as unknown as JourneyStats) || {
          current_streak: 0,
          total_conversations: 0,
          achievements_unlocked: 0,
          wisdom_level: 1,
          domain_exploration: { spiritual: 0, scientific: 0, philosophical: 0, leadership: 0, literary: 0, psychology: 0 },
        },
        preferences: {
          user_id: data.user_id,
          experience_preferences: (data.preferences?.experience_preferences as unknown as ExperiencePreferences) || defaultExperiencePrefs,
          notification_preferences: (data.preferences?.notification_preferences as unknown as NotificationPreferences) || defaultNotificationPrefs,
          memory_preferences: (data.preferences?.memory_preferences as unknown as MemoryPreferences) || defaultMemoryPrefs,
          updated_at: data.last_updated || new Date().toISOString(),
        },
        ai_usage: (data.ai_usage as unknown as AIUsage) || { monthly_cost: 0, monthly_limit: 10, status: 'well_within_limits', trend: 'similar_to_last_month' },
      };
      
      setProfile(mappedProfile);
      setSettings(mappedProfile.preferences);
    } catch (err) {
      console.error('Failed to load user profile:', err);
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  }, []);

  // Load profile in background after critical contexts are ready - completely non-blocking
  useEffect(() => {
    // Defer profile loading to prevent blocking critical paths
    const timer = setTimeout(() => {
      refreshProfile().catch(err => {
        // Silently fail - profile is not critical for initial page load
        if (process.env.NODE_ENV === 'development') {
          console.log('📊 SettingsContext: Profile load deferred (non-critical), will retry on-demand');
        }
        // Don't set error to prevent UI disruption
      });
    }, 2000); // Load after 2s to allow all critical contexts to initialize first
    
    return () => clearTimeout(timer);
  }, [refreshProfile]);

  // Debounced save function
  const debouncedSave = useCallback(async (updates: Partial<UserSettings>) => {
    try {
      const data = await spiritualGuidanceAPI.updatePreferences(updates);
      
      // Update settings with response from server
      if (data.preferences) {
        // Merge with existing settings to preserve user_id and updated_at
        if (settings) {
          setSettings({
            ...settings,
            ...data.preferences,
            updated_at: new Date().toISOString(),
          } as UserSettings);
        }
      }

      // Show success toast
      const event = new CustomEvent('settings-saved');
      window.dispatchEvent(event);
    } catch (err) {
      console.error('Failed to save preferences:', err);
      
      // Show error toast
      const event = new CustomEvent('settings-error', {
        detail: { message: err instanceof Error ? err.message : 'Failed to save' }
      });
      window.dispatchEvent(event);
      
      // Revert optimistic update by refreshing
      await refreshProfile();
    }
  }, [refreshProfile, settings]);

  // Update settings with optimistic UI and debounced save
  const updateSettings = useCallback(async (updates: Partial<UserSettings>) => {
    if (!settings) return;

    // Optimistic update
    const mergedSettings = deepMerge(settings, updates);
    setSettings(mergedSettings);

    // Accumulate pending updates
    setPendingUpdates(prev => prev ? deepMerge(prev, updates) : updates);

    // Clear existing timeout
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }

    // Debounce save by 500ms
    saveTimeout = setTimeout(() => {
      if (pendingUpdates) {
        debouncedSave(deepMerge(updates, pendingUpdates));
        setPendingUpdates(null);
      } else {
        debouncedSave(updates);
      }
    }, 500);
  }, [settings, pendingUpdates, debouncedSave]);

  // Deep merge helper for nested objects
  const deepMerge = (target: any, source: any): any => {
    const result = { ...target };
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = deepMerge(target[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    }
    return result;
  };

  return (
    <SettingsContext.Provider
      value={{
        settings,
        profile,
        loading,
        error,
        updateSettings,
        refreshProfile,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};
