/**
 * Unit Tests for AccountTab Component
 * Tests subscription display, account security, and account actions (matching actual implementation)
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AccountTab from '../../components/Settings/AccountTab';

// Mock functions
const mockLogout = jest.fn();
const mockNavigate = jest.fn();

// Mock useNavigate from react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Override the global AuthContext mock for this test file
jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'test-user-123', email: 'test@vimarsh.app', name: 'Test User' },
    logout: mockLogout,
    isAuthenticated: true,
    loading: false,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe('AccountTab', () => {
  beforeEach(() => {
    mockLogout.mockClear();
    mockNavigate.mockClear();
  });

  const renderComponent = () => render(<AccountTab />);

  describe('Subscription Section', () => {
    test('renders subscription heading', () => {
      renderComponent();
      expect(screen.getByText('Subscription')).toBeInTheDocument();
    });

    test('displays Free Tier plan', () => {
      renderComponent();
      expect(screen.getByText('Free Tier')).toBeInTheDocument();
      expect(screen.getByText("You're on the free tier")).toBeInTheDocument();
    });

    test('shows Active status badge', () => {
      renderComponent();
      const activeElements = screen.getAllByText('Active');
      expect(activeElements.length).toBeGreaterThan(0);
    });

    test('displays AI usage information', () => {
      renderComponent();
      expect(screen.getByText('AI Usage This Month')).toBeInTheDocument();
      const costElements = screen.getAllByText(/\$3\.20/);
      expect(costElements.length).toBeGreaterThan(0);
      expect(screen.getByText(/\$10 \/ month/)).toBeInTheDocument();
    });

    test('shows AI usage progress bar', () => {
      renderComponent();
      const progressBars = screen.getAllByRole('generic').filter(
        el => el.className.includes('bg-blue-600') && el.className.includes('h-2')
      );
      expect(progressBars.length).toBeGreaterThan(0);
    });

    test('displays upgrade to premium section', () => {
      renderComponent();
      expect(screen.getByText('Upgrade to Premium')).toBeInTheDocument();
      expect(screen.getByText('• Higher AI usage limits')).toBeInTheDocument();
      expect(screen.getByText('• Priority response times')).toBeInTheDocument();
      expect(screen.getByText('• Early access to new personalities')).toBeInTheDocument();
      expect(screen.getByText('• Advanced memory features')).toBeInTheDocument();
    });

    test('shows Coming Soon button for premium upgrade', () => {
      renderComponent();
      const comingSoonButton = screen.getByRole('button', { name: /coming soon/i });
      expect(comingSoonButton).toBeInTheDocument();
    });
  });

  describe('Account Security Section', () => {
    test('renders security heading', () => {
      renderComponent();
      expect(screen.getByText('Account Security')).toBeInTheDocument();
    });

    test('displays user email', () => {
      renderComponent();
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('test@vimarsh.app')).toBeInTheDocument();
    });

    test('shows email verified badge', () => {
      renderComponent();
      expect(screen.getByText('Verified')).toBeInTheDocument();
    });

    test('displays authentication provider', () => {
      renderComponent();
      expect(screen.getByText('Authentication')).toBeInTheDocument();
      expect(screen.getByText('Microsoft Entra ID')).toBeInTheDocument();
    });

    test('shows connected apps section', () => {
      renderComponent();
      expect(screen.getByText('Connected Apps')).toBeInTheDocument();
      expect(screen.getByText('No third-party apps connected')).toBeInTheDocument();
    });

    test('displays manage button for connected apps', () => {
      renderComponent();
      const manageButton = screen.getByRole('button', { name: /manage/i });
      expect(manageButton).toBeInTheDocument();
    });

    test('shows active sessions section', () => {
      renderComponent();
      expect(screen.getByText('Active Sessions')).toBeInTheDocument();
      expect(screen.getByText('This device only')).toBeInTheDocument();
    });

    test('displays view all button for sessions', () => {
      renderComponent();
      const viewAllButton = screen.getByRole('button', { name: /view all/i });
      expect(viewAllButton).toBeInTheDocument();
    });
  });

  describe('Account Actions Section', () => {
    test('renders account actions heading', () => {
      renderComponent();
      expect(screen.getByText('⚙️ Account Actions')).toBeInTheDocument();
    });

    test('displays sign out section', () => {
      renderComponent();
      const signOutElements = screen.getAllByText('Sign Out');
      expect(signOutElements.length).toBeGreaterThan(0);
      expect(screen.getByText('End your current session and return to login')).toBeInTheDocument();
    });

    test('shows sign out button', () => {
      renderComponent();
      const signOutButton = screen.getByRole('button', { name: /sign out/i });
      expect(signOutButton).toBeInTheDocument();
    });

    test('displays delete account section', () => {
      renderComponent();
      expect(screen.getByText('Delete My Account')).toBeInTheDocument();
      expect(screen.getByText('Permanently delete your account and all data')).toBeInTheDocument();
      expect(screen.getByText('This action cannot be undone!')).toBeInTheDocument();
    });

    test('shows delete account button', () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete account/i });
      expect(deleteButton).toBeInTheDocument();
    });
  });

  describe('Sign Out Flow', () => {
    test('calls logout when sign out button clicked', () => {
      renderComponent();
      const signOutButton = screen.getByRole('button', { name: /sign out/i });
      
      fireEvent.click(signOutButton);
      
      expect(mockLogout).toHaveBeenCalledTimes(1);
    });

    test('navigates to home after logout', () => {
      renderComponent();
      const signOutButton = screen.getByRole('button', { name: /sign out/i });
      
      fireEvent.click(signOutButton);
      
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('Delete Account Flow', () => {
    test('shows confirmation modal when delete account clicked', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete account/i });
      
      fireEvent.click(deleteButton);
      
      await waitFor(() => {
        expect(screen.getByText('Delete Account?')).toBeInTheDocument();
      });
    });

    test('displays warning message in modal', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete account/i });
      
      fireEvent.click(deleteButton);
      
      await waitFor(() => {
        expect(screen.getByText(/This will permanently delete:/i)).toBeInTheDocument();
        expect(screen.getByText(/profile and account information/i)).toBeInTheDocument();
        expect(screen.getByText(/conversation history/i)).toBeInTheDocument();
        expect(screen.getByText(/achievements and progress/i)).toBeInTheDocument();
        expect(screen.getByText(/bookmarks and saved wisdom/i)).toBeInTheDocument();
        expect(screen.getByText(/preferences and settings/i)).toBeInTheDocument();
      });
    });

    test('requires DELETE text confirmation', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete account/i });
      
      fireEvent.click(deleteButton);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('DELETE')).toBeInTheDocument();
      });
    });

    test('delete button disabled until DELETE typed', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete account/i });
      
      fireEvent.click(deleteButton);
      
      await waitFor(() => {
        const deleteInput = screen.getByPlaceholderText('DELETE');
        const confirmButton = screen.getByRole('button', { name: /delete forever/i });
        
        expect(confirmButton).toBeDisabled();
        
        fireEvent.change(deleteInput, { target: { value: 'WRONG' } });
        expect(confirmButton).toBeDisabled();
      });
    });

    test('delete button enabled when DELETE typed correctly', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete account/i });
      
      fireEvent.click(deleteButton);
      
      await waitFor(() => {
        const deleteInput = screen.getByPlaceholderText('DELETE');
        const confirmButton = screen.getByRole('button', { name: /delete forever/i });
        
        fireEvent.change(deleteInput, { target: { value: 'DELETE' } });
        expect(confirmButton).toBeEnabled();
      });
    });

    test('can cancel deletion', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete account/i });
      
      fireEvent.click(deleteButton);
      
      await waitFor(() => {
        const cancelButton = screen.getByRole('button', { name: /cancel/i });
        fireEvent.click(cancelButton);
      });
      
      await waitFor(() => {
        expect(screen.queryByText('Delete Account?')).not.toBeInTheDocument();
      });
    });

    test('closes modal after confirming deletion', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', { name: /delete account/i });
      
      fireEvent.click(deleteButton);
      
      await waitFor(async () => {
        const deleteInput = screen.getByPlaceholderText('DELETE');
        fireEvent.change(deleteInput, { target: { value: 'DELETE' } });
        
        const confirmButton = screen.getByRole('button', { name: /delete forever/i });
        fireEvent.click(confirmButton);
      });
      
      await waitFor(() => {
        expect(screen.queryByText('Delete Account?')).not.toBeInTheDocument();
      });
    });
  });

  describe('Help Section', () => {
    test('displays help information', () => {
      renderComponent();
      expect(screen.getByText(/Need help\?/)).toBeInTheDocument();
      expect(screen.getByText('Help Center')).toBeInTheDocument();
    });

    test('shows support email link', () => {
      renderComponent();
      const supportLink = screen.getByRole('link', { name: /support@vimarsh.app/i });
      expect(supportLink).toBeInTheDocument();
      expect(supportLink).toHaveAttribute('href', 'mailto:support@vimarsh.app');
    });
  });

  describe('Accessibility', () => {
    test('has proper heading hierarchy', () => {
      renderComponent();
      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);
    });

    test('all action buttons are accessible', () => {
      renderComponent();
      expect(screen.getByRole('button', { name: /sign out/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /delete account/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /manage/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /view all/i })).toBeInTheDocument();
    });
  });
});
