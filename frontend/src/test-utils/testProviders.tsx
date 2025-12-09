import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { MsalTestProvider, mockMsalInstance } from './msalTestUtils';

// Mock AuthContext
const MockAuthContext = React.createContext({
  isAuthenticated: true,
  user: {
    id: 'test-user-123',
    email: 'test@vimarsh.app',
    name: 'Test User'
  },
  login: jest.fn(),
  logout: jest.fn(),
  loading: false
});

// Mock SettingsContext
const mockSettings = {
  user_id: 'test-user-123',
  experience_preferences: {
    conversation_style: 'balanced' as const,
    language: 'en' as const,
    formality: 'respectful' as const,
    favorite_personalities: ['krishna', 'buddha'],
    theme: 'auto' as const,
    text_size: 'medium' as const,
    reduce_animations: false
  },
  notification_preferences: {
    daily_wisdom_enabled: true,
    preferred_time: '09:00',
    timezone: 'UTC',
    quiet_hours_enabled: false,
    quiet_start: '22:00',
    quiet_end: '07:00',
    types: {
      daily_wisdom: true,
      streak_reminders: true,
      achievements: true,
      weekly_summary: false
    }
  },
  memory_preferences: {
    remember_conversations: true,
    connect_insights: true,
    track_emotions: false,
    suggest_topics: true,
    privacy_mode: 'standard' as const,
    data_retention_days: 90,
    analytics_consent: true,
    research_consent: false
  },
  updated_at: '2024-01-01T00:00:00Z'
};

const mockProfile = {
  user: {
    user_id: 'test-user-123',
    email: 'test@vimarsh.app',
    name: 'Test User',
    member_since: '2024-01-01T00:00:00Z'
  },
  journey_stats: {
    current_streak: 14,
    total_conversations: 87,
    achievements_unlocked: 5,
    wisdom_level: 'Seeker',
    domain_exploration: {
      spiritual: 45,
      scientific: 12,
      philosophical: 20,
      leadership: 8,
      literary: 2,
      psychology: 0
    }
  },
  preferences: mockSettings,
  ai_usage: {
    monthly_cost: 2.34,
    monthly_limit: 10.00,
    status: 'well_within_limits' as const,
    trend: 'similar_to_last_month' as const
  }
};

const MockSettingsContext = React.createContext({
  settings: mockSettings,
  profile: mockProfile,
  loading: false,
  error: null as string | null,
  updateSettings: jest.fn(),
  refreshProfile: jest.fn()
});

// Mock AuthProvider for tests
export const MockAuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const mockAuthValue = {
    isAuthenticated: true,
    user: {
      id: 'test-user-123',
      email: 'test@vimarsh.app',
      name: 'Test User'
    },
    login: jest.fn(),
    logout: jest.fn(),
    loading: false
  };

  return (
    <MockAuthContext.Provider value={mockAuthValue}>
      {children}
    </MockAuthContext.Provider>
  );
};

// Mock SettingsProvider for tests
export const MockSettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const mockSettingsValue = {
    settings: mockSettings,
    profile: mockProfile,
    loading: false,
    error: null,
    updateSettings: jest.fn().mockResolvedValue(undefined),
    refreshProfile: jest.fn().mockResolvedValue(undefined)
  };

  return (
    <MockSettingsContext.Provider value={mockSettingsValue}>
      {children}
    </MockSettingsContext.Provider>
  );
};

// Comprehensive test wrapper with all providers
interface AllProvidersProps {
  children: React.ReactNode;
}

export const AllProviders: React.FC<AllProvidersProps> = ({ children }) => {
  return (
    <BrowserRouter>
      <MsalTestProvider instance={mockMsalInstance}>
        <MockAuthProvider>
          <MockSettingsProvider>
            {children}
          </MockSettingsProvider>
        </MockAuthProvider>
      </MsalTestProvider>
    </BrowserRouter>
  );
};

// Custom render function with all providers
export const renderWithProviders = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  return render(ui, { wrapper: AllProviders, ...options });
};

// Export for tests that need to mock specific values
export { MockAuthContext, MockSettingsContext, mockSettings, mockProfile };
