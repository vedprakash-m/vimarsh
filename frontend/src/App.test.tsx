import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock React Router
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Routes: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Route: ({ element }: { element: React.ReactNode }) => <div>{element}</div>
}));

test('renders Vimarsh application', () => {
  render(<App />);
  // App shows loading state initially
  const loadingElement = screen.getByText(/Loading wisdom guidance/i);
  expect(loadingElement).toBeInTheDocument();
});

test('renders wisdom guidance interface', () => {
  render(<App />);
  // Check for loading state which contains "wisdom guidance"
  const guidanceElement = screen.getByText(/wisdom guidance/i);
  expect(guidanceElement).toBeInTheDocument();
});

test('shows loading state', () => {
  render(<App />);
  // Check for the loading spinner and text
  const loadingText = screen.getByText(/Loading wisdom guidance/i);
  expect(loadingText).toBeInTheDocument();
});
