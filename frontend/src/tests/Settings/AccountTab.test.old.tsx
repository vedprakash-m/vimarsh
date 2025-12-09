/**
 * Unit Tests for AccountTab Component
 * Tests subscription display, usage tracking, account security, and account actions
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AccountTab from '../../components/Settings/AccountTab';

// Mock SettingsContext
const mockLogout = jest.fn();
const mockDeleteAccount = jest.fn();

const mockProfile = {
  user_id: 'test-user-123',
  email: 'seeker@vimarsh.app',
  name: 'Spiritual Seeker',
  created_at: '2024-01-01T00:00:00Z',
  subscription_tier: 'free',
  subscription_status: 'active',
  subscription_expires: null,
};

const mockUsageSummary = {
  total_conversations: 87,
  total_messages: 456,
  guidance_received: 125,
  streak_days: 14,
  monthly_conversations: 28,
  monthly_limit: 50,
  daily_messages: 12,
  daily_limit: 20,
};

jest.mock('../../contexts/SettingsContext', () => ({
  useSettings: () => ({
    settings: null,
    profile: mockProfile,
    loading: false,
    error: null,
    updateSettings: jest.fn(),
    refreshProfile: jest.fn(),
  }),
  SettingsProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock useNavigate from react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

describe('AccountTab', () => {
  beforeEach(() => {
    mockLogout.mockClear();
    mockDeleteAccount.mockClear();
    mockNavigate.mockClear();
  });

  const renderComponent = () => {
    return render(<AccountTab />);
  };

  describe('Subscription Information', () => {
    test('renders subscription section', () => {
      renderComponent();
      expect(screen.getByText('Subscription')).toBeInTheDocument();
    });

    test('displays current subscription tier', () => {
      renderComponent();
      expect(screen.getByText(/free tier/i)).toBeInTheDocument();
    });

    test('shows subscription status', () => {
      renderComponent();
      expect(screen.getByText(/active/i)).toBeInTheDocument();
    });

    test('displays tier features', () => {
      renderComponent();
      expect(screen.getByText(/50.*conversations.*month/i)).toBeInTheDocument();
      expect(screen.getByText(/20.*messages.*day/i)).toBeInTheDocument();
    });

    test('shows upgrade button for free tier', () => {
      renderComponent();
      expect(screen.getByRole('button', { name: /upgrade/i })).toBeInTheDocument();
    });

    test('displays member since date', () => {
      renderComponent();
      expect(screen.getByText(/member since/i)).toBeInTheDocument();
      expect(screen.getByText(/january.*2024/i)).toBeInTheDocument();
    });
  });

  describe('Usage Tracking', () => {
    test('renders usage section', () => {
      renderComponent();
      expect(screen.getByText(/usage/i)).toBeInTheDocument();
    });

    test('displays monthly conversation usage', () => {
      renderComponent();
      expect(screen.getByText(/28.*50/i)).toBeInTheDocument();
    });

    test('displays daily message usage', () => {
      renderComponent();
      expect(screen.getByText(/12.*20/i)).toBeInTheDocument();
    });

    test('shows progress bar for monthly conversations', () => {
      renderComponent();
      const progressBar = screen.getByRole('progressbar', { name: /monthly.*conversation/i });
      expect(progressBar).toBeInTheDocument();
      // 28/50 = 56%
      expect(progressBar).toHaveAttribute('aria-valuenow', '28');
      expect(progressBar).toHaveAttribute('aria-valuemax', '50');
    });

    test('shows progress bar for daily messages', () => {
      renderComponent();
      const progressBar = screen.getByRole('progressbar', { name: /daily.*message/i });
      expect(progressBar).toBeInTheDocument();
      // 12/20 = 60%
      expect(progressBar).toHaveAttribute('aria-valuenow', '12');
      expect(progressBar).toHaveAttribute('aria-valuemax', '20');
    });

    test('calculates percentage correctly', () => {
      renderComponent();
      expect(screen.getByText(/56%/i)).toBeInTheDocument(); // Monthly: 28/50
      expect(screen.getByText(/60%/i)).toBeInTheDocument(); // Daily: 12/20
    });

    test('shows warning when approaching limit (>80%)', () => {
      // Mock high usage
      mockUsageSummary.monthly_conversations = 45; // 90%
      
      renderComponent();
      expect(screen.getByText(/approaching.*limit/i) || screen.getByText(/warning/i)).toBeInTheDocument();
    });

    test('displays total statistics', () => {
      renderComponent();
      expect(screen.getByText(/87.*total.*conversation/i)).toBeInTheDocument();
      expect(screen.getByText(/456.*total.*message/i)).toBeInTheDocument();
    });

    test('shows current streak', () => {
      renderComponent();
      expect(screen.getByText(/14.*day.*streak/i)).toBeInTheDocument();
    });
  });

  describe('Account Security', () => {
    test('renders security section', () => {
      renderComponent();
      expect(screen.getByText('Account Security')).toBeInTheDocument();
    });

    test('displays email address', () => {
      renderComponent();
      expect(screen.getByText('seeker@vimarsh.app')).toBeInTheDocument();
    });

    test('shows change email button', () => {
      renderComponent();
      expect(screen.getByRole('button', { name: /change.*email/i })).toBeInTheDocument();
    });

    test('shows change password button', () => {
      renderComponent();
      expect(screen.getByRole('button', { name: /change.*password/i })).toBeInTheDocument();
    });

    test('displays two-factor authentication status', () => {
      renderComponent();
      expect(screen.getByText(/two.*factor/i)).toBeInTheDocument();
    });

    test('shows enable 2FA button when disabled', () => {
      renderComponent();
      expect(screen.getByRole('button', { name: /enable.*2fa/i })).toBeInTheDocument();
    });

    test('displays connected accounts section', () => {
      renderComponent();
      expect(screen.getByText(/connected.*account/i)).toBeInTheDocument();
    });

    test('shows Microsoft Entra ID connection', () => {
      renderComponent();
      expect(screen.getByText(/microsoft/i)).toBeInTheDocument();
      expect(screen.getByText(/connected/i)).toBeInTheDocument();
    });
  });

  describe('Account Actions', () => {
    test('renders account actions section', () => {
      renderComponent();
      expect(screen.getByText('Account Actions')).toBeInTheDocument();
    });

    test('displays logout button', () => {
      renderComponent();
      expect(screen.getByRole('button', { name: /log.*out/i })).toBeInTheDocument();
    });

    test('displays delete account button', () => {
      renderComponent();
      expect(screen.getByRole('button', { name: /delete.*account/i })).toBeInTheDocument();
    });

    test('logout button has warning style', () => {
      renderComponent();
      const logoutButton = screen.getByRole('button', { name: /log.*out/i });
      expect(logoutButton).toHaveClass('text-amber-600'); // Warning color
    });

    test('delete button has danger style', () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      expect(deleteButton).toHaveClass('text-red-600'); // Danger color
    });
  });

  describe('Logout Flow', () => {
    test('shows confirmation modal when clicking logout', async () => {
      renderComponent();
      const logoutButton = screen.getByRole('button', { name: /log.*out/i });
      
      fireEvent.click(logoutButton);

      await waitFor(() => {
        expect(screen.getByText(/confirm.*logout/i)).toBeInTheDocument();
      });
    });

    test('displays logout confirmation message', async () => {
      renderComponent();
      const logoutButton = screen.getByRole('button', { name: /log.*out/i });
      
      fireEvent.click(logoutButton);

      await waitFor(() => {
        expect(screen.getByText(/sure.*log.*out/i)).toBeInTheDocument();
      });
    });

    test('calls logout when confirming', async () => {
      renderComponent();
      const logoutButton = screen.getByRole('button', { name: /log.*out/i });
      
      fireEvent.click(logoutButton);

      await waitFor(() => {
        const confirmButton = screen.getByRole('button', { name: /confirm/i });
        fireEvent.click(confirmButton);
        
        expect(mockLogout).toHaveBeenCalled();
      });
    });

    test('navigates to login after successful logout', async () => {
      mockLogout.mockResolvedValueOnce({ success: true });
      
      renderComponent();
      const logoutButton = screen.getByRole('button', { name: /log.*out/i });
      
      fireEvent.click(logoutButton);

      await waitFor(() => {
        const confirmButton = screen.getByRole('button', { name: /confirm/i });
        fireEvent.click(confirmButton);
      });

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });

    test('can cancel logout', async () => {
      renderComponent();
      const logoutButton = screen.getByRole('button', { name: /log.*out/i });
      
      fireEvent.click(logoutButton);

      await waitFor(() => {
        const cancelButton = screen.getByRole('button', { name: /cancel/i });
        fireEvent.click(cancelButton);
        
        expect(mockLogout).not.toHaveBeenCalled();
      });
    });
  });

  describe('Delete Account Flow', () => {
    test('shows warning modal when clicking delete account', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText(/delete.*account/i)).toBeInTheDocument();
      });
    });

    test('displays severe warning message', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText(/permanent/i)).toBeInTheDocument();
        expect(screen.getByText(/cannot.*undo/i)).toBeInTheDocument();
      });
    });

    test('requires typing email for confirmation', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/delete/i)).toBeInTheDocument();
      });
    });

    test('confirm button disabled until email matches', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        const confirmButton = screen.getByRole('button', { name: /delete/i });
        expect(confirmButton).toBeDisabled();
        
        const deleteInput = screen.getByPlaceholderText(/delete/i);
        fireEvent.change(deleteInput, { target: { value: 'WRONG' } });
        
        expect(confirmButton).toBeDisabled();
      });
    });

    test('confirm button enabled when email matches', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        const deleteInput = screen.getByPlaceholderText(/delete/i);
        fireEvent.change(deleteInput, { target: { value: 'DELETE' } });
        
        const confirmButton = screen.getByRole('button', { name: /delete/i });
        expect(confirmButton).toBeEnabled();
      });
    });

    test('calls deleteAccount when confirmed with correct email', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        const deleteInput = screen.getByPlaceholderText(/delete/i);
        fireEvent.change(deleteInput, { target: { value: 'DELETE' } });
        
        const confirmButton = screen.getByRole('button', { name: /delete/i });
        fireEvent.click(confirmButton);
        
        expect(mockDeleteAccount).toHaveBeenCalled();
      });
    });

    test('shows what will be deleted', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText(/conversation.*history/i)).toBeInTheDocument();
        expect(screen.getByText(/preference/i)).toBeInTheDocument();
        expect(screen.getByText(/personal.*data/i)).toBeInTheDocument();
      });
    });

    test('navigates to goodbye page after successful deletion', async () => {
      mockDeleteAccount.mockResolvedValueOnce({ success: true });
      
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        const deleteInput = screen.getByPlaceholderText(/delete/i);
        fireEvent.change(deleteInput, { target: { value: 'DELETE' } });
        
        const deleteButton = screen.getByRole('button', { name: /delete/i });
        fireEvent.click(deleteButton);
      });

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/goodbye');
      });
    });

    test('can cancel deletion', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        const cancelButton = screen.getByRole('button', { name: /cancel/i });
        fireEvent.click(cancelButton);
        
        expect(mockDeleteAccount).not.toHaveBeenCalled();
      });
    });
  });

  describe('Premium Features Teaser', () => {
    test('shows premium features for free tier users', () => {
      renderComponent();
      expect(screen.getByText(/upgrade.*premium/i) || screen.getByText(/premium.*feature/i)).toBeInTheDocument();
    });

    test('displays premium benefits', () => {
      renderComponent();
      expect(screen.getByText(/unlimited.*conversation/i)).toBeInTheDocument();
      expect(screen.getByText(/advanced.*insight/i)).toBeInTheDocument();
    });

    test('shows pricing information', () => {
      renderComponent();
      expect(screen.getByText(/\$9\.99/i) || screen.getByText(/month/i)).toBeInTheDocument();
    });

    test('upgrade button navigates to pricing', () => {
      renderComponent();
      const upgradeButton = screen.getByRole('button', { name: /upgrade/i });
      
      fireEvent.click(upgradeButton);
      
      expect(mockNavigate).toHaveBeenCalledWith('/pricing');
    });
  });

  describe('Accessibility', () => {
    test('all buttons have accessible labels', () => {
      renderComponent();
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toHaveAccessibleName();
      });
    });

    test('progress bars have accessible labels', () => {
      renderComponent();
      const progressBars = screen.getAllByRole('progressbar');
      progressBars.forEach(bar => {
        expect(bar).toHaveAccessibleName();
      });
    });

    test('sections have proper heading hierarchy', () => {
      renderComponent();
      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);
    });

    test('dangerous actions have aria-describedby warnings', () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      expect(deleteButton).toHaveAttribute('aria-describedby');
    });
  });

  describe('Error Handling', () => {
    test('shows error if logout fails', async () => {
      mockLogout.mockRejectedValueOnce(new Error('Logout failed'));
      
      renderComponent();
      const logoutButton = screen.getByRole('button', { name: /log.*out/i });
      
      fireEvent.click(logoutButton);

      await waitFor(() => {
        const confirmButton = screen.getByRole('button', { name: /confirm/i });
        fireEvent.click(confirmButton);
      });

      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });
    });

    test('shows error if deletion fails', async () => {
      mockDeleteAccount.mockRejectedValueOnce(new Error('Deletion failed'));
      
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        const deleteInput = screen.getByPlaceholderText(/delete/i);
        fireEvent.change(deleteInput, { target: { value: 'DELETE' } });
        
        const confirmButton = screen.getByRole('button', { name: /delete/i });
        fireEvent.click(confirmButton);
      });

      await waitFor(() => {
        expect(screen.getByText(/error/i) || screen.getByText(/failed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    test('shows loading state during logout', async () => {
      mockLogout.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderComponent();
      const logoutButton = screen.getByRole('button', { name: /log.*out/i });
      
      fireEvent.click(logoutButton);

      await waitFor(() => {
        const confirmButton = screen.getByRole('button', { name: /confirm/i });
        fireEvent.click(confirmButton);
        
        expect(screen.getByText(/logging.*out/i) || confirmButton).toHaveAttribute('disabled');
      });
    });

    test('shows loading state during deletion', async () => {
      mockDeleteAccount.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete.*account/i });
      
      fireEvent.click(deleteButton);

      await waitFor(() => {
        const deleteInput = screen.getByPlaceholderText(/delete/i);
        fireEvent.change(deleteInput, { target: { value: 'DELETE' } });
        
        const confirmButton = screen.getByRole('button', { name: /delete/i });
        fireEvent.click(confirmButton);
        
        expect(screen.getByText(/deleting/i) || confirmButton).toHaveAttribute('disabled');
      });
    });
  });
});
