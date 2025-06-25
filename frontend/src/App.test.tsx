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
  const titleElement = screen.getByText(/Vimarsh/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders spiritual guidance interface', () => {
  render(<App />);
  const guidanceElement = screen.getByText(/Spiritual Guidance/i);
  expect(guidanceElement).toBeInTheDocument();
});

test('renders namaste greeting', () => {
  render(<App />);
  const namasteElement = screen.getByText(/Namaste/i);
  expect(namasteElement).toBeInTheDocument();
});
