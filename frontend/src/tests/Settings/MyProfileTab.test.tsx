/**
 * Unit Tests for MyProfileTab Component
 * Tests profile display, journey stats, AI usage, and navigation
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import MyProfileTab from '../../components/Settings/MyProfileTab';
import { SettingsProvider } from '../../contexts/SettingsContext';

// Mock react-router-dom navigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock profile data
const mockProfile = {
  user: {
    user_id: 'test_user_123',
    name: 'Test User',
    email: 'test@example.com',
    member_since: '2025-01-01T00:00:00Z',
    profile_picture: null,
  },
  journey_stats: {
    current_streak: 5,
    longest_streak: 10,
    total_conversations: 50,
    achievements_unlocked: 3,
    wisdom_level: 'Student',
    domain_exploration: {
      spiritual: 20,
      philosophical: 15,
      leadership: 10,
      scientific: 5,
      literary: 0,
      psychology: 0,
    },
  },
  ai_usage: {
    monthly_cost_usd: 1.50,
    usage_percentage: 15.0,
    status: 'well_within_limits',
    total_conversations: 50,
    total_tokens: 100000,
    monthly_limit: 10.0,
    trend: 'similar_to_last_month',
  },
};

// Mock SettingsContext
jest.mock('../../contexts/SettingsContext', () => ({
  useSettings: () => ({
    settings: {},
    profile: mockProfile,
    loading: false,
    error: null,
    updateSettings: jest.fn(),
    refreshProfile: jest.fn(),
  }),
  SettingsProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe('MyProfileTab', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <SettingsProvider>
          <MyProfileTab />
        </SettingsProvider>
      </BrowserRouter>
    );
  };

  describe('Profile Display', () => {
    test('renders user name and email', () => {
      renderComponent();
      expect(screen.getByText('Test User')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });

    test('shows member since date', () => {
      renderComponent();
      expect(screen.getByText(/Member since/i)).toBeInTheDocument();
    });

    test('displays profile picture placeholder when no image', () => {
      renderComponent();
      const placeholder = screen.getByText('T'); // First letter of name
      expect(placeholder).toBeInTheDocument();
    });

    test('renders Account Information header', () => {
      renderComponent();
      expect(screen.getByText('Account Information')).toBeInTheDocument();
    });
  });

  describe('Journey Stats', () => {
    test('displays current streak', () => {
      renderComponent();
      expect(screen.getByText(/5/)).toBeInTheDocument(); // Current streak
    });

    test('displays longest streak', () => {
      renderComponent();
      expect(screen.getByText(/10/)).toBeInTheDocument(); // Longest streak
    });

    test('displays total conversations', () => {
      renderComponent();
      expect(screen.getByText(/50/)).toBeInTheDocument(); // Total conversations
    });

    test('displays achievements unlocked', () => {
      renderComponent();
      expect(screen.getByText(/3/)).toBeInTheDocument(); // Achievements
    });

    test('displays wisdom level', () => {
      renderComponent();
      expect(screen.getByText('Student')).toBeInTheDocument();
    });

    test('renders journey stats header', () => {
      renderComponent();
      expect(screen.getByText(/Your Journey/i)).toBeInTheDocument();
    });
  });

  describe('AI Usage Display', () => {
    test('displays monthly cost in user-friendly language', () => {
      renderComponent();
      expect(screen.getByText(/covered costs/i)).toBeInTheDocument();
    });

    test('shows usage percentage', () => {
      renderComponent();
      expect(screen.getByText(/15/)).toBeInTheDocument(); // Usage percentage
    });

    test('displays well within limits status', () => {
      renderComponent();
      expect(screen.getByText(/Well within limits/i)).toBeInTheDocument();
    });

    test('renders AI usage header', () => {
      renderComponent();
      expect(screen.getByText(/AI Usage/i)).toBeInTheDocument();
    });
  });

  describe('Status Colors', () => {
    test('uses green color for well within limits', () => {
      renderComponent();
      const statusElement = screen.getByText(/Well within limits/i);
      expect(statusElement).toHaveClass('text-green-600');
    });
  });

  describe('Domain Exploration', () => {
    test('displays domain exploration section', () => {
      renderComponent();
      expect(screen.getByText(/Domain Exploration/i)).toBeInTheDocument();
    });

    test('shows spiritual domain progress', () => {
      renderComponent();
      expect(screen.getByText('Spiritual')).toBeInTheDocument();
    });

    test('shows philosophical domain progress', () => {
      renderComponent();
      expect(screen.getByText('Philosophical')).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    test('shows loading message when profile is null', () => {
      // Override mock to return null profile
      jest.spyOn(require('../../contexts/SettingsContext'), 'useSettings').mockReturnValue({
        profile: null,
        preferences: {},
        updatePreferences: jest.fn(),
      });

      renderComponent();
      expect(screen.getByText(/Loading profile/i)).toBeInTheDocument();
    });
  });

  describe('Quick Access Links', () => {
    test('renders quick access section', () => {
      renderComponent();
      expect(screen.getByText(/Quick Access/i)).toBeInTheDocument();
    });
  });
});
