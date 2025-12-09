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

// Comprehensive test wrapper with all providers
interface AllProvidersProps {
  children: React.ReactNode;
}

export const AllProviders: React.FC<AllProvidersProps> = ({ children }) => {
  return (
    <BrowserRouter>
      <MsalTestProvider instance={mockMsalInstance}>
        <MockAuthProvider>
          {children}
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
export { MockAuthContext };
