import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getApiBaseUrl } from '../config/environment';
import { getAuthHeaders } from '../auth/authService';

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

      const headers = await getAuthHeaders();
      const response = await fetch(`${getApiBaseUrl()}/user/profile`, {
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch profile: ${response.statusText}`);
      }

      const data: UserProfile = await response.json();
      setProfile(data);
      setSettings(data.preferences);
    } catch (err) {
      console.error('Failed to load user profile:', err);
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  }, []);

  // Load profile in background, don't block initial render
  useEffect(() => {
    // Delay profile loading slightly to prioritize critical data
    const timer = setTimeout(() => {
      refreshProfile().catch(err => {
        // Silently fail - profile is not critical for initial page load
        if (process.env.NODE_ENV === 'development') {
          console.warn('Profile loading deferred, will retry:', err.message);
        }
      });
    }, 500); // Load after 500ms to let critical contexts initialize first
    
    return () => clearTimeout(timer);
  }, [refreshProfile]);

  // Debounced save function
  const debouncedSave = useCallback(async (updates: Partial<UserSettings>) => {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${getApiBaseUrl()}/api/user/preferences`, {
        method: 'PATCH',
        headers: {
          ...headers,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Failed to update preferences: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Update settings with response from server
      if (data.updated_preferences) {
        setSettings(data.updated_preferences);
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
  }, [refreshProfile]);

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
