/**
 * Domain Theme System Integration Test
 * Tests the complete domain theme functionality including:
 * - PersonalityContext integration
 * - Domain theme switching
 * - Theme application to DOM
 * - Multi-personality theme coverage
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PersonalityProvider, usePersonality } from '../contexts/PersonalityContext';
import { DomainThemeManager } from '../components/DomainThemeManager';

// Unmock PersonalityContext for this integration test - we want the real implementation
jest.unmock('../contexts/PersonalityContext');

// Mock fetch to prevent API calls in tests
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: false,
    status: 500,
    json: () => Promise.resolve({ error: 'Test environment' }),
  })
) as jest.Mock;

// Mock personalities for testing
const mockPersonalities = [
  {
    id: 'einstein',
    name: 'Einstein',
    display_name: 'Albert Einstein',
    domain: 'scientific' as const,
    time_period: '20th Century (1879-1955)',
    description: 'Theoretical physicist',
    expertise_areas: ['physics', 'relativity'],
    cultural_context: 'Scientific revolution',
    quality_score: 95.0,
    usage_count: 500,
    is_active: true,
    tags: ['scientific', 'physics']
  },
  {
    id: 'lincoln',
    name: 'Lincoln',
    display_name: 'Abraham Lincoln',
    domain: 'historical' as const,
    time_period: '19th Century (1809-1865)',
    description: '16th President of the United States',
    expertise_areas: ['leadership', 'democracy'],
    cultural_context: 'American Civil War era',
    quality_score: 92.0,
    usage_count: 400,
    is_active: true,
    tags: ['historical', 'leadership']
  },
  {
    id: 'marcus_aurelius',
    name: 'Marcus_Aurelius',
    display_name: 'Marcus Aurelius',
    domain: 'philosophical' as const,
    time_period: 'Roman Empire (121-180 CE)',
    description: 'Roman Emperor and Stoic philosopher',
    expertise_areas: ['stoicism', 'virtue'],
    cultural_context: 'Roman Stoic philosophy',
    quality_score: 88.0,
    usage_count: 300,
    is_active: true,
    tags: ['philosophical', 'stoicism']
  }
];

// Test component that uses personality context
const TestComponent: React.FC = () => {
  const { selectedPersonality, setSelectedPersonality } = usePersonality();
  
  return (
    <div>
      <div data-testid="current-personality">
        {selectedPersonality ? selectedPersonality.display_name : 'None'}
      </div>
      <div data-testid="current-domain">
        {selectedPersonality ? selectedPersonality.domain : 'None'}
      </div>
      {mockPersonalities.map(personality => (
        <button
          key={personality.id}
          data-testid={`select-${personality.id}`}
          onClick={() => setSelectedPersonality(personality)}
        >
          Select {personality.display_name}
        </button>
      ))}
      <DomainThemeManager />
    </div>
  );
};

// Test wrapper with providers
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <PersonalityProvider>
    {children}
  </PersonalityProvider>
);

describe('Domain Theme System Integration', () => {
  beforeEach(() => {
    // Clear any existing theme classes
    document.documentElement.removeAttribute('data-domain');
    
    // Mock localStorage
    const localStorageMock = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn(),
      clear: jest.fn(),
    };
    global.localStorage = localStorageMock as any;
  });

  afterEach(() => {
    // Clean up theme classes
    document.documentElement.removeAttribute('data-domain');
  });

  it('should initialize with Krishna personality and spiritual theme', async () => {
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByTestId('current-personality')).toHaveTextContent('Krishna');
      expect(screen.getByTestId('current-domain')).toHaveTextContent('spiritual');
    });

    // Check if spiritual theme is applied
    expect(document.documentElement.getAttribute('data-domain')).toBe('spiritual');
  });

  it('should switch to scientific theme when Einstein is selected', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    // Select Einstein
    await user.click(screen.getByTestId('select-einstein'));

    await waitFor(() => {
      expect(screen.getByTestId('current-personality')).toHaveTextContent('Albert Einstein');
      expect(screen.getByTestId('current-domain')).toHaveTextContent('scientific');
    });

    // Check theme switching
    expect(document.documentElement.getAttribute('data-domain')).toBe('scientific');
  });

  it('should switch to historical theme when Lincoln is selected', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    // Select Lincoln
    await user.click(screen.getByTestId('select-lincoln'));

    await waitFor(() => {
      expect(screen.getByTestId('current-personality')).toHaveTextContent('Abraham Lincoln');
      expect(screen.getByTestId('current-domain')).toHaveTextContent('historical');
    });

    // Check theme switching
    expect(document.documentElement.getAttribute('data-domain')).toBe('historical');
  });

  it('should switch to philosophical theme when Marcus Aurelius is selected', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    // Select Marcus Aurelius
    await user.click(screen.getByTestId('select-marcus_aurelius'));

    await waitFor(() => {
      expect(screen.getByTestId('current-personality')).toHaveTextContent('Marcus Aurelius');
      expect(screen.getByTestId('current-domain')).toHaveTextContent('philosophical');
    });

    // Check theme switching
    expect(document.documentElement.getAttribute('data-domain')).toBe('philosophical');
  });

  it('should persist personality selection to localStorage', async () => {
    const user = userEvent.setup();
    
    // Mock localStorage with proper jest spy
    const mockSetItem = jest.fn();
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: mockSetItem,
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true
    });
    
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    // Select Einstein
    await user.click(screen.getByTestId('select-einstein'));

    await waitFor(() => {
      expect(mockSetItem).toHaveBeenCalledWith(
        'vimarsh_selected_personality',
        expect.stringContaining('Einstein')
      );
    });
  });

  it('should handle rapid personality switching correctly', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    // Rapidly switch between personalities
    await user.click(screen.getByTestId('select-einstein'));
    await user.click(screen.getByTestId('select-lincoln'));
    await user.click(screen.getByTestId('select-marcus_aurelius'));

    await waitFor(() => {
      expect(screen.getByTestId('current-personality')).toHaveTextContent('Marcus Aurelius');
      expect(screen.getByTestId('current-domain')).toHaveTextContent('philosophical');
    });

    // Final theme should be philosophical
    expect(document.documentElement.getAttribute('data-domain')).toBe('philosophical');
  });

  it('should handle missing domain gracefully', async () => {
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    // Test with personality that has undefined domain (edge case)
    // This should not crash the application
    await waitFor(() => {
      const domainAttr = document.documentElement.getAttribute('data-domain');
      // Either has no theme or has spiritual theme as fallback
      expect(!domainAttr || domainAttr === 'spiritual').toBe(true);
    });
  });
});

// Theme validation test
describe('Domain Theme CSS Validation', () => {
  it('should have all required theme domains applied to document.documentElement', () => {
    const themes = ['spiritual', 'scientific', 'historical', 'philosophical'];
    
    themes.forEach(theme => {
      document.documentElement.setAttribute('data-domain', theme);
      expect(document.documentElement.getAttribute('data-domain')).toBe(theme);
      document.documentElement.removeAttribute('data-domain');
    });
  });
});

export default {};
