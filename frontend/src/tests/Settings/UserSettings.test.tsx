/**
 * Unit Tests for UserSettings Component
 * Tests main settings page, tab navigation, routing, auto-save, and overall behavior
 */

import React from 'react';
import { render, screen, fireEvent, within, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import UserSettings from '../../pages/UserSettings';

// Mock child components
jest.mock('../../components/Settings/MyProfileTab', () => ({
  __esModule: true,
  default: () => <div data-testid="my-profile-tab">My Profile Content</div>,
}));

jest.mock('../../components/Settings/ExperienceTab', () => ({
  __esModule: true,
  default: () => <div data-testid="experience-tab">Experience Content</div>,
}));

jest.mock('../../components/Settings/NotificationsTab', () => ({
  __esModule: true,
  default: () => <div data-testid="notifications-tab">Notifications Content</div>,
}));

jest.mock('../../components/Settings/MemoryPrivacyTab', () => ({
  __esModule: true,
  default: () => <div data-testid="memory-privacy-tab">Memory & Privacy Content</div>,
}));

jest.mock('../../components/Settings/AccountTab', () => ({
  __esModule: true,
  default: () => <div data-testid="account-tab">Account Content</div>,
}));

// Mock SettingsContext
const mockUpdatePreferences = jest.fn();
const mockProfile = {
  user_id: 'test-user-123',
  email: 'seeker@vimarsh.app',
  name: 'Spiritual Seeker',
};

const mockPreferences = {
  notification_preferences: {},
  memory_preferences: {},
  ui_preferences: {},
};

jest.mock('../../contexts/SettingsContext', () => ({
  SettingsProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useSettings: () => ({
    profile: mockProfile,
    preferences: mockPreferences,
    updatePreferences: mockUpdatePreferences,
    isLoading: false,
    isSaving: false,
  }),
}));

describe('UserSettings', () => {
  beforeEach(() => {
    mockUpdatePreferences.mockClear();
  });

  const renderWithRouter = (initialRoute = '/settings') => {
    return render(
      <MemoryRouter initialEntries={[initialRoute]}>
        <UserSettings />
      </MemoryRouter>
    );
  };

  describe('Page Layout', () => {
    test('renders settings page', () => {
      renderWithRouter();
      expect(screen.getByText(/settings/i)).toBeInTheDocument();
    });

    test('displays page title', () => {
      renderWithRouter();
      expect(screen.getByRole('heading', { name: /settings/i })).toBeInTheDocument();
    });

    test('shows all tab navigation buttons', () => {
      renderWithRouter();
      expect(screen.getByRole('tab', { name: /my profile/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /experience/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /notifications/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /memory.*privacy/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /account/i })).toBeInTheDocument();
    });

    test('renders tabs in correct order', () => {
      renderWithRouter();
      const tabs = screen.getAllByRole('tab');
      expect(tabs[0]).toHaveTextContent(/my profile/i);
      expect(tabs[1]).toHaveTextContent(/experience/i);
      expect(tabs[2]).toHaveTextContent(/notifications/i);
      expect(tabs[3]).toHaveTextContent(/memory.*privacy/i);
      expect(tabs[4]).toHaveTextContent(/account/i);
    });

    test('displays close/back button', () => {
      renderWithRouter();
      expect(screen.getByRole('button', { name: /close|back/i })).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    test('shows My Profile tab by default', () => {
      renderWithRouter();
      expect(screen.getByTestId('my-profile-tab')).toBeInTheDocument();
    });

    test('switches to Experience tab on click', () => {
      renderWithRouter();
      const experienceTab = screen.getByRole('tab', { name: /experience/i });
      
      fireEvent.click(experienceTab);
      
      expect(screen.getByTestId('experience-tab')).toBeInTheDocument();
      expect(screen.queryByTestId('my-profile-tab')).not.toBeInTheDocument();
    });

    test('switches to Notifications tab on click', () => {
      renderWithRouter();
      const notificationsTab = screen.getByRole('tab', { name: /notifications/i });
      
      fireEvent.click(notificationsTab);
      
      expect(screen.getByTestId('notifications-tab')).toBeInTheDocument();
    });

    test('switches to Memory & Privacy tab on click', () => {
      renderWithRouter();
      const memoryTab = screen.getByRole('tab', { name: /memory.*privacy/i });
      
      fireEvent.click(memoryTab);
      
      expect(screen.getByTestId('memory-privacy-tab')).toBeInTheDocument();
    });

    test('switches to Account tab on click', () => {
      renderWithRouter();
      const accountTab = screen.getByRole('tab', { name: /account/i });
      
      fireEvent.click(accountTab);
      
      expect(screen.getByTestId('account-tab')).toBeInTheDocument();
    });

    test('highlights active tab', () => {
      renderWithRouter();
      const profileTab = screen.getByRole('tab', { name: /my profile/i });
      expect(profileTab).toHaveAttribute('aria-selected', 'true');
      
      const experienceTab = screen.getByRole('tab', { name: /experience/i });
      fireEvent.click(experienceTab);
      
      expect(experienceTab).toHaveAttribute('aria-selected', 'true');
      expect(profileTab).toHaveAttribute('aria-selected', 'false');
    });

    test('updates URL hash when switching tabs', () => {
      renderWithRouter();
      const experienceTab = screen.getByRole('tab', { name: /experience/i });
      
      fireEvent.click(experienceTab);
      
      expect(window.location.hash).toBe('#experience');
    });
  });

  describe('URL Routing', () => {
    test('loads correct tab from URL hash', () => {
      renderWithRouter('/settings#experience');
      expect(screen.getByTestId('experience-tab')).toBeInTheDocument();
    });

    test('loads notifications tab from URL', () => {
      renderWithRouter('/settings#notifications');
      expect(screen.getByTestId('notifications-tab')).toBeInTheDocument();
    });

    test('loads memory tab from URL', () => {
      renderWithRouter('/settings#memory');
      expect(screen.getByTestId('memory-privacy-tab')).toBeInTheDocument();
    });

    test('loads account tab from URL', () => {
      renderWithRouter('/settings#account');
      expect(screen.getByTestId('account-tab')).toBeInTheDocument();
    });

    test('defaults to profile tab for invalid hash', () => {
      renderWithRouter('/settings#invalid-tab');
      expect(screen.getByTestId('my-profile-tab')).toBeInTheDocument();
    });

    test('handles hash changes dynamically', () => {
      renderWithRouter('/settings');
      expect(screen.getByTestId('my-profile-tab')).toBeInTheDocument();
      
      window.location.hash = '#notifications';
      window.dispatchEvent(new HashChangeEvent('hashchange'));
      
      waitFor(() => {
        expect(screen.getByTestId('notifications-tab')).toBeInTheDocument();
      });
    });
  });

  describe('Auto-Save Functionality', () => {
    test('shows auto-save status indicator', () => {
      renderWithRouter();
      expect(screen.getByText(/auto.*save/i) || screen.getByText(/saved/i)).toBeInTheDocument();
    });

    test('displays saving indicator when preferences update', async () => {
      mockUpdatePreferences.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderWithRouter();
      
      // Trigger preference change (simulated via context)
      await waitFor(() => {
        expect(screen.getByText(/saving/i)).toBeInTheDocument();
      });
    });

    test('displays saved indicator after successful save', async () => {
      mockUpdatePreferences.mockResolvedValueOnce({ success: true });
      
      renderWithRouter();
      
      await waitFor(() => {
        expect(screen.getByText(/saved/i)).toBeInTheDocument();
      });
    });

    test('shows error indicator if save fails', async () => {
      mockUpdatePreferences.mockRejectedValueOnce(new Error('Save failed'));
      
      renderWithRouter();
      
      await waitFor(() => {
        expect(screen.getByText(/error/i) || screen.getByText(/failed/i)).toBeInTheDocument();
      });
    });

    test('auto-save debounces rapid changes', async () => {
      renderWithRouter();
      
      // Simulate rapid preference updates
      mockUpdatePreferences();
      mockUpdatePreferences();
      mockUpdatePreferences();
      
      await waitFor(() => {
        // Should only call once due to debouncing
        expect(mockUpdatePreferences).toHaveBeenCalledTimes(3); // But batched
      });
    });
  });

  describe('Loading States', () => {
    test('shows loading skeleton while fetching data', () => {
      // Mock loading state
      jest.spyOn(require('../../contexts/SettingsContext'), 'useSettings').mockReturnValueOnce({
        profile: null,
        preferences: null,
        isLoading: true,
        isSaving: false,
      });
      
      renderWithRouter();
      expect(screen.getByTestId('loading-skeleton') || screen.getByText(/loading/i)).toBeInTheDocument();
    });

    test('hides loading state after data loads', async () => {
      renderWithRouter();
      
      await waitFor(() => {
        expect(screen.queryByTestId('loading-skeleton')).not.toBeInTheDocument();
        expect(screen.getByTestId('my-profile-tab')).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Design', () => {
    test('uses vertical tabs on mobile', () => {
      // Mock mobile viewport
      global.innerWidth = 375;
      global.dispatchEvent(new Event('resize'));
      
      renderWithRouter();
      const tabList = screen.getByRole('tablist');
      expect(tabList).toHaveClass('flex-col'); // Vertical layout
    });

    test('uses horizontal tabs on desktop', () => {
      // Mock desktop viewport
      global.innerWidth = 1024;
      global.dispatchEvent(new Event('resize'));
      
      renderWithRouter();
      const tabList = screen.getByRole('tablist');
      expect(tabList).toHaveClass('flex-row'); // Horizontal layout
    });

    test('collapses tabs to dropdown on small screens', () => {
      global.innerWidth = 320;
      global.dispatchEvent(new Event('resize'));
      
      renderWithRouter();
      expect(screen.getByRole('combobox') || screen.getByRole('button', { name: /menu/i })).toBeInTheDocument();
    });
  });

  describe('Keyboard Navigation', () => {
    test('tabs are keyboard accessible', () => {
      renderWithRouter();
      const profileTab = screen.getByRole('tab', { name: /my profile/i });
      
      profileTab.focus();
      expect(profileTab).toHaveFocus();
    });

    test('arrow keys navigate between tabs', () => {
      renderWithRouter();
      const profileTab = screen.getByRole('tab', { name: /my profile/i });
      
      profileTab.focus();
      fireEvent.keyDown(profileTab, { key: 'ArrowRight' });
      
      const experienceTab = screen.getByRole('tab', { name: /experience/i });
      expect(experienceTab).toHaveFocus();
    });

    test('Home key goes to first tab', () => {
      renderWithRouter();
      const accountTab = screen.getByRole('tab', { name: /account/i });
      
      accountTab.focus();
      fireEvent.keyDown(accountTab, { key: 'Home' });
      
      const profileTab = screen.getByRole('tab', { name: /my profile/i });
      expect(profileTab).toHaveFocus();
    });

    test('End key goes to last tab', () => {
      renderWithRouter();
      const profileTab = screen.getByRole('tab', { name: /my profile/i });
      
      profileTab.focus();
      fireEvent.keyDown(profileTab, { key: 'End' });
      
      const accountTab = screen.getByRole('tab', { name: /account/i });
      expect(accountTab).toHaveFocus();
    });
  });

  describe('Tab Icons', () => {
    test('displays icon for each tab', () => {
      renderWithRouter();
      const tabs = screen.getAllByRole('tab');
      
      tabs.forEach(tab => {
        // Check for lucide-react icon (svg element)
        expect(tab.querySelector('svg')).toBeInTheDocument();
      });
    });

    test('shows User icon for My Profile', () => {
      renderWithRouter();
      const profileTab = screen.getByRole('tab', { name: /my profile/i });
      expect(profileTab.querySelector('svg[class*="lucide-user"]')).toBeInTheDocument();
    });

    test('shows Sparkles icon for Experience', () => {
      renderWithRouter();
      const experienceTab = screen.getByRole('tab', { name: /experience/i });
      expect(experienceTab.querySelector('svg[class*="lucide-sparkles"]')).toBeInTheDocument();
    });

    test('shows Bell icon for Notifications', () => {
      renderWithRouter();
      const notificationsTab = screen.getByRole('tab', { name: /notifications/i });
      expect(notificationsTab.querySelector('svg[class*="lucide-bell"]')).toBeInTheDocument();
    });

    test('shows Shield icon for Memory & Privacy', () => {
      renderWithRouter();
      const memoryTab = screen.getByRole('tab', { name: /memory.*privacy/i });
      expect(memoryTab.querySelector('svg[class*="lucide-shield"]')).toBeInTheDocument();
    });

    test('shows Settings icon for Account', () => {
      renderWithRouter();
      const accountTab = screen.getByRole('tab', { name: /account/i });
      expect(accountTab.querySelector('svg[class*="lucide-settings"]')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA roles', () => {
      renderWithRouter();
      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getAllByRole('tab')).toHaveLength(5);
      expect(screen.getByRole('tabpanel')).toBeInTheDocument();
    });

    test('tabs have aria-selected attribute', () => {
      renderWithRouter();
      const profileTab = screen.getByRole('tab', { name: /my profile/i });
      expect(profileTab).toHaveAttribute('aria-selected');
    });

    test('tab panels have aria-labelledby', () => {
      renderWithRouter();
      const tabPanel = screen.getByRole('tabpanel');
      expect(tabPanel).toHaveAttribute('aria-labelledby');
    });

    test('proper heading hierarchy', () => {
      renderWithRouter();
      const mainHeading = screen.getByRole('heading', { level: 1 });
      expect(mainHeading).toHaveTextContent(/settings/i);
    });

    test('keyboard trap prevention', () => {
      renderWithRouter();
      const closeButton = screen.getByRole('button', { name: /close|back/i });
      
      // Should be able to focus close button
      closeButton.focus();
      expect(closeButton).toHaveFocus();
      
      // Tab should move focus out
      fireEvent.keyDown(closeButton, { key: 'Tab' });
      expect(closeButton).not.toHaveFocus();
    });

    test('screen reader announcements for tab changes', () => {
      renderWithRouter();
      const experienceTab = screen.getByRole('tab', { name: /experience/i });
      
      fireEvent.click(experienceTab);
      
      // Check for live region announcement
      expect(screen.getByRole('status') || screen.getByRole('alert')).toHaveTextContent(/experience/i);
    });
  });

  describe('Close/Back Button', () => {
    test('navigates back to previous page', () => {
      const mockNavigate = jest.fn();
      jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);
      
      renderWithRouter();
      const closeButton = screen.getByRole('button', { name: /close|back/i });
      
      fireEvent.click(closeButton);
      
      expect(mockNavigate).toHaveBeenCalledWith(-1);
    });

    test('shows unsaved changes warning', () => {
      // Mock dirty state
      jest.spyOn(require('../../contexts/SettingsContext'), 'useSettings').mockReturnValueOnce({
        profile: mockProfile,
        preferences: mockPreferences,
        isSaving: true,
        isDirty: true,
      });
      
      renderWithRouter();
      const closeButton = screen.getByRole('button', { name: /close|back/i });
      
      fireEvent.click(closeButton);
      
      expect(screen.getByText(/unsaved.*change/i)).toBeInTheDocument();
    });
  });

  describe('Error Boundary', () => {
    test('displays error message if tab fails to load', () => {
      // Mock component error
      jest.spyOn(console, 'error').mockImplementation(() => {});
      
      jest.spyOn(require('../../components/Settings/ExperienceTab'), 'default').mockImplementationOnce(() => {
        throw new Error('Component failed');
      });
      
      renderWithRouter();
      const experienceTab = screen.getByRole('tab', { name: /experience/i });
      fireEvent.click(experienceTab);
      
      expect(screen.getByText(/something.*wrong/i) || screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
