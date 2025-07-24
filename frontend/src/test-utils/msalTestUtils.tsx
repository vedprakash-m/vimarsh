import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { PublicClientApplication } from '@azure/msal-browser';
import { MsalProvider } from '@azure/msal-react';

// Mock MSAL instance for testing
export const mockMsalInstance = {
  initialize: jest.fn().mockResolvedValue(undefined),
  loginPopup: jest.fn().mockResolvedValue({
    account: {
      username: 'test@test.com',
      name: 'Test User',
      localAccountId: 'test-id'
    }
  }),
  logout: jest.fn().mockResolvedValue(undefined),
  getAllAccounts: jest.fn().mockReturnValue([]),
  getAccountByUsername: jest.fn().mockReturnValue(null),
  acquireTokenSilent: jest.fn().mockResolvedValue({
    accessToken: 'mock-token',
    account: {
      username: 'test@test.com'
    }
  }),
  addEventCallback: jest.fn(),
  removeEventCallback: jest.fn()
} as any;

// MSAL Provider wrapper for tests
interface MsalTestProviderProps {
  children: React.ReactNode;
  instance?: PublicClientApplication;
}

export const MsalTestProvider: React.FC<MsalTestProviderProps> = ({ 
  children, 
  instance = mockMsalInstance 
}) => {
  return (
    <MsalProvider instance={instance}>
      {children}
    </MsalProvider>
  );
};

// Custom render function with MSAL provider
export const renderWithMsal = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <MsalTestProvider>{children}</MsalTestProvider>
  );

  return render(ui, { wrapper: Wrapper, ...options });
};

// Mock hooks for testing
export const mockUseMsal = () => ({
  instance: mockMsalInstance,
  accounts: [],
  inProgress: 'None'
});

export const mockUseAccount = () => null;
export const mockUseIsAuthenticated = () => false;
