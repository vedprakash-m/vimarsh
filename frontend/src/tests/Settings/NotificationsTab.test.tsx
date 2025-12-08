/**
 * Unit Tests for NotificationsTab Component
 * Tests daily wisdom, quiet hours, timezone, notification types, and test notification
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import NotificationsTab from '../../components/Settings/NotificationsTab';

// Mock SettingsContext
const mockUpdatePreferences = jest.fn();
const mockPreferences = {
  notification_preferences: {
    daily_wisdom_enabled: true,
    preferred_time: '09:00',
    timezone: 'America/Los_Angeles',
    quiet_hours_enabled: true,
    quiet_start: '22:00',
    quiet_end: '07:00',
    types: {
      daily_wisdom: true,
      streak_reminders: true,
      achievements: true,
      weekly_summary: false,
    },
  },
};

jest.mock('../../contexts/SettingsContext', () => ({
  useSettings: () => ({
    settings: mockPreferences,
    profile: null,
    loading: false,
    error: null,
    updateSettings: mockUpdatePreferences,
    refreshProfile: jest.fn(),
  }),
  SettingsProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock Notification API
const mockNotification = {
  requestPermission: jest.fn().mockResolvedValue('granted'),
};
global.Notification = mockNotification as any;

describe('NotificationsTab', () => {
  beforeEach(() => {
    mockUpdatePreferences.mockClear();
    mockNotification.requestPermission.mockClear();
  });

  const renderComponent = () => {
    return render(<NotificationsTab />);
  };

  describe('Daily Wisdom Settings', () => {
    test('renders daily wisdom toggle', () => {
      renderComponent();
      expect(screen.getByText(/Daily Wisdom/i)).toBeInTheDocument();
    });

    test('shows daily wisdom enabled by default', () => {
      renderComponent();
      const toggle = screen.getByRole('checkbox', { name: /daily wisdom/i });
      expect(toggle).toBeChecked();
    });

    test('displays preferred time', () => {
      renderComponent();
      expect(screen.getByDisplayValue('09:00')).toBeInTheDocument();
    });

    test('calls updatePreferences when toggling daily wisdom', async () => {
      renderComponent();
      const toggle = screen.getByRole('checkbox', { name: /daily wisdom/i });
      
      fireEvent.click(toggle);

      await waitFor(() => {
        expect(mockUpdatePreferences).toHaveBeenCalledWith({
          notification_preferences: expect.objectContaining({
            daily_wisdom_enabled: false,
          }),
        });
      });
    });

    test('calls updatePreferences when changing preferred time', async () => {
      renderComponent();
      const timeInput = screen.getByDisplayValue('09:00');
      
      fireEvent.change(timeInput, { target: { value: '14:30' } });

      await waitFor(() => {
        expect(mockUpdatePreferences).toHaveBeenCalledWith({
          notification_preferences: expect.objectContaining({
            preferred_time: '14:30',
          }),
        });
      });
    });

    test('displays time presets', () => {
      renderComponent();
      expect(screen.getByText('Morning')).toBeInTheDocument();
      expect(screen.getByText('Afternoon')).toBeInTheDocument();
      expect(screen.getByText('Evening')).toBeInTheDocument();
    });

    test('clicking preset updates time', async () => {
      renderComponent();
      const morningButton = screen.getByRole('button', { name: /morning/i });
      
      fireEvent.click(morningButton);

      await waitFor(() => {
        expect(mockUpdatePreferences).toHaveBeenCalledWith({
          notification_preferences: expect.objectContaining({
            preferred_time: expect.stringMatching(/0[6-9]:00/), // Morning time
          }),
        });
      });
    });
  });

  describe('Timezone Selection', () => {
    test('renders timezone section', () => {
      renderComponent();
      expect(screen.getByText('Timezone')).toBeInTheDocument();
    });

    test('displays current timezone', () => {
      renderComponent();
      expect(screen.getByText(/Los Angeles/i)).toBeInTheDocument();
    });

    test('shows timezone options', () => {
      renderComponent();
      const timezoneSelect = screen.getByRole('combobox', { name: /timezone/i });
      expect(timezoneSelect).toBeInTheDocument();
    });

    test('calls updatePreferences when changing timezone', async () => {
      renderComponent();
      const timezoneSelect = screen.getByRole('combobox', { name: /timezone/i });
      
      fireEvent.change(timezoneSelect, { target: { value: 'America/New_York' } });

      await waitFor(() => {
        expect(mockUpdatePreferences).toHaveBeenCalledWith({
          notification_preferences: expect.objectContaining({
            timezone: 'America/New_York',
          }),
        });
      });
    });

    test('includes major timezone options', () => {
      renderComponent();
      // Check for presence of major timezones
      expect(screen.getByText(/Los Angeles/i)).toBeInTheDocument();
      // Could check for more if dropdown is expanded
    });
  });

  describe('Quiet Hours', () => {
    test('renders quiet hours section', () => {
      renderComponent();
      expect(screen.getByText('Quiet Hours')).toBeInTheDocument();
    });

    test('shows quiet hours toggle', () => {
      renderComponent();
      const toggle = screen.getByRole('checkbox', { name: /quiet hours/i });
      expect(toggle).toBeChecked();
    });

    test('displays quiet start time', () => {
      renderComponent();
      expect(screen.getByDisplayValue('22:00')).toBeInTheDocument();
    });

    test('displays quiet end time', () => {
      renderComponent();
      expect(screen.getByDisplayValue('07:00')).toBeInTheDocument();
    });

    test('calls updatePreferences when toggling quiet hours', async () => {
      renderComponent();
      const toggle = screen.getByRole('checkbox', { name: /quiet hours/i });
      
      fireEvent.click(toggle);

      await waitFor(() => {
        expect(mockUpdatePreferences).toHaveBeenCalledWith({
          notification_preferences: expect.objectContaining({
            quiet_hours_enabled: false,
          }),
        });
      });
    });

    test('calls updatePreferences when changing quiet start time', async () => {
      renderComponent();
      const startInput = screen.getByDisplayValue('22:00');
      
      fireEvent.change(startInput, { target: { value: '23:00' } });

      await waitFor(() => {
        expect(mockUpdatePreferences).toHaveBeenCalledWith({
          notification_preferences: expect.objectContaining({
            quiet_start: '23:00',
          }),
        });
      });
    });

    test('calls updatePreferences when changing quiet end time', async () => {
      renderComponent();
      const endInput = screen.getByDisplayValue('07:00');
      
      fireEvent.change(endInput, { target: { value: '08:00' } });

      await waitFor(() => {
        expect(mockUpdatePreferences).toHaveBeenCalledWith({
          notification_preferences: expect.objectContaining({
            quiet_end: '08:00',
          }),
        });
      });
    });

    test('shows helper text about quiet hours', () => {
      renderComponent();
      expect(screen.getByText(/no notifications during/i)).toBeInTheDocument();
    });
  });

  describe('Notification Types', () => {
    test('renders notification types section', () => {
      renderComponent();
      expect(screen.getByText('Notification Types')).toBeInTheDocument();
    });

    test('displays all notification type toggles', () => {
      renderComponent();
      expect(screen.getByText(/daily wisdom quote/i)).toBeInTheDocument();
      expect(screen.getByText(/streak reminders/i)).toBeInTheDocument();
      expect(screen.getByText(/achievements/i)).toBeInTheDocument();
      expect(screen.getByText(/weekly summary/i)).toBeInTheDocument();
    });

    test('shows daily wisdom enabled', () => {
      renderComponent();
      const toggle = screen.getByRole('checkbox', { name: /daily wisdom quote/i });
      expect(toggle).toBeChecked();
    });

    test('shows streak reminders enabled', () => {
      renderComponent();
      const toggle = screen.getByRole('checkbox', { name: /streak reminders/i });
      expect(toggle).toBeChecked();
    });

    test('shows achievements enabled', () => {
      renderComponent();
      const toggle = screen.getByRole('checkbox', { name: /achievements/i });
      expect(toggle).toBeChecked();
    });

    test('shows weekly summary disabled', () => {
      renderComponent();
      const toggle = screen.getByRole('checkbox', { name: /weekly summary/i });
      expect(toggle).not.toBeChecked();
    });

    test('calls updatePreferences when toggling notification type', async () => {
      renderComponent();
      const toggle = screen.getByRole('checkbox', { name: /weekly summary/i });
      
      fireEvent.click(toggle);

      await waitFor(() => {
        expect(mockUpdatePreferences).toHaveBeenCalledWith({
          notification_preferences: expect.objectContaining({
            types: expect.objectContaining({
              weekly_summary: true,
            }),
          }),
        });
      });
    });

    test('provides descriptions for each notification type', () => {
      renderComponent();
      // Check that descriptive text exists for notification types
      expect(screen.getByText(/wisdom quote/i)).toBeInTheDocument();
      expect(screen.getByText(/streak/i)).toBeInTheDocument();
      expect(screen.getByText(/achievement/i)).toBeInTheDocument();
      expect(screen.getByText(/weekly/i)).toBeInTheDocument();
    });
  });

  describe('Test Notification', () => {
    test('renders test notification button', () => {
      renderComponent();
      expect(screen.getByRole('button', { name: /send test notification/i })).toBeInTheDocument();
    });

    test('requests permission when testing notification', async () => {
      renderComponent();
      const testButton = screen.getByRole('button', { name: /send test notification/i });
      
      fireEvent.click(testButton);

      await waitFor(() => {
        expect(mockNotification.requestPermission).toHaveBeenCalled();
      });
    });

    test('shows success message after sending test notification', async () => {
      mockNotification.requestPermission.mockResolvedValueOnce('granted');
      
      renderComponent();
      const testButton = screen.getByRole('button', { name: /send test notification/i });
      
      fireEvent.click(testButton);

      await waitFor(() => {
        expect(screen.getByText(/test notification sent/i)).toBeInTheDocument();
      });
    });

    test('handles permission denied gracefully', async () => {
      mockNotification.requestPermission.mockResolvedValueOnce('denied');
      
      renderComponent();
      const testButton = screen.getByRole('button', { name: /send test notification/i });
      
      fireEvent.click(testButton);

      await waitFor(() => {
        expect(screen.getByText(/permission denied/i)).toBeInTheDocument();
      });
    });
  });

  describe('Section Headers', () => {
    test('renders all section headers', () => {
      renderComponent();
      expect(screen.getByText('Daily Wisdom')).toBeInTheDocument();
      expect(screen.getByText('Timezone')).toBeInTheDocument();
      expect(screen.getByText('Quiet Hours')).toBeInTheDocument();
      expect(screen.getByText('Notification Types')).toBeInTheDocument();
    });
  });

  describe('Helper Text', () => {
    test('displays helpful information about notifications', () => {
      renderComponent();
      expect(screen.getByText(/receive/i) || screen.getByText(/notification/i)).toBeInTheDocument();
    });

    test('shows timezone impact message', () => {
      renderComponent();
      expect(screen.getByText(/based on your timezone/i) || screen.getByText(/local time/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('all toggles have accessible labels', () => {
      renderComponent();
      const checkboxes = screen.getAllByRole('checkbox');
      checkboxes.forEach(checkbox => {
        expect(checkbox).toHaveAccessibleName();
      });
    });

    test('time inputs have labels', () => {
      renderComponent();
      const timeInputs = screen.getAllByRole('textbox', { name: /time/i });
      expect(timeInputs.length).toBeGreaterThan(0);
    });

    test('timezone select has label', () => {
      renderComponent();
      const select = screen.getByRole('combobox', { name: /timezone/i });
      expect(select).toHaveAccessibleName();
    });
  });

  describe('Auto-save Integration', () => {
    test('multiple changes trigger separate auto-saves', async () => {
      renderComponent();
      
      const dailyWisdomToggle = screen.getByRole('checkbox', { name: /daily wisdom/i });
      const streakToggle = screen.getByRole('checkbox', { name: /streak reminders/i });
      
      fireEvent.click(dailyWisdomToggle);
      fireEvent.click(streakToggle);

      await waitFor(() => {
        expect(mockUpdatePreferences).toHaveBeenCalledTimes(2);
      });
    });
  });
});
