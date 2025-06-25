import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ABTestingProvider, useABTesting } from '../contexts/ABTestingContext';

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

// Test component to access A/B testing context
const TestComponent: React.FC = () => {
  const {
    activeTests,
    getVariant,
    getVariantConfig,
    isInTest,
    trackEvent,
    isOptedOut,
    setOptOut
  } = useABTesting();

  return (
    <div>
      <div data-testid="active-tests-count">{activeTests.length}</div>
      <div data-testid="guidance-variant">{getVariant('guidance-interface-layout')}</div>
      <div data-testid="response-variant">{getVariant('response-formatting')}</div>
      <div data-testid="is-in-guidance-test">{isInTest('guidance-interface-layout').toString()}</div>
      <div data-testid="opt-out-status">{isOptedOut.toString()}</div>
      
      <button
        data-testid="track-event-btn"
        onClick={() => trackEvent('guidance-interface-layout', 'interaction', { test: 'data' })}
      >
        Track Event
      </button>
      
      <button
        data-testid="opt-out-btn"
        onClick={() => setOptOut(true)}
      >
        Opt Out
      </button>
      
      <button
        data-testid="opt-in-btn"
        onClick={() => setOptOut(false)}
      >
        Opt In
      </button>
      
      {/* Display variant config */}
      <div data-testid="guidance-config">
        {JSON.stringify(getVariantConfig('guidance-interface-layout'))}
      </div>
    </div>
  );
};

const renderWithProvider = () => {
  return render(
    <ABTestingProvider>
      <TestComponent />
    </ABTestingProvider>
  );
};

describe('ABTestingContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  describe('Basic Functionality', () => {
    it('should render without crashing', () => {
      renderWithProvider();
      expect(screen.getByTestId('active-tests-count')).toBeInTheDocument();
    });

    it('should load active tests', () => {
      renderWithProvider();
      
      // Should have the default tests
      expect(screen.getByTestId('active-tests-count')).toHaveTextContent('2');
    });

    it('should assign users to tests', () => {
      renderWithProvider();
      
      // User should be assigned to one of the variants
      const guidanceVariant = screen.getByTestId('guidance-variant').textContent;
      expect(['control', 'enhanced']).toContain(guidanceVariant);
      
      const responseVariant = screen.getByTestId('response-variant').textContent;
      expect(['traditional', 'modern']).toContain(responseVariant);
    });

    it('should return variant configuration', () => {
      renderWithProvider();
      
      const configText = screen.getByTestId('guidance-config').textContent;
      const config = JSON.parse(configText || '{}');
      
      // Should have layout configuration
      expect(config).toHaveProperty('layout');
      expect(config).toHaveProperty('citationPosition');
      expect(config).toHaveProperty('voiceButtonSize');
    });

    it('should track test participation', () => {
      renderWithProvider();
      
      // Should show participation in tests
      expect(screen.getByTestId('is-in-guidance-test')).toHaveTextContent('true');
    });
  });

  describe('Event Tracking', () => {
    it('should track events when user is in test', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      renderWithProvider();
      
      const trackButton = screen.getByTestId('track-event-btn');
      fireEvent.click(trackButton);
      
      // Should log the event (in production, this would send to analytics)
      expect(consoleSpy).toHaveBeenCalledWith(
        'A/B Test Event:',
        expect.objectContaining({
          testId: 'guidance-interface-layout',
          eventType: 'interaction',
          eventData: { test: 'data' }
        })
      );
      
      consoleSpy.mockRestore();
    });

    it('should not track events when opted out', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      renderWithProvider();
      
      // Opt out first
      const optOutButton = screen.getByTestId('opt-out-btn');
      fireEvent.click(optOutButton);
      
      // Try to track event
      const trackButton = screen.getByTestId('track-event-btn');
      fireEvent.click(trackButton);
      
      // Should not log any A/B test events
      expect(consoleSpy).not.toHaveBeenCalledWith(
        'A/B Test Event:',
        expect.any(Object)
      );
      
      consoleSpy.mockRestore();
    });
  });

  describe('Opt-out Functionality', () => {
    it('should allow users to opt out of A/B testing', () => {
      renderWithProvider();
      
      // Initially opted in
      expect(screen.getByTestId('opt-out-status')).toHaveTextContent('false');
      
      // Opt out
      const optOutButton = screen.getByTestId('opt-out-btn');
      fireEvent.click(optOutButton);
      
      // Should be opted out
      expect(screen.getByTestId('opt-out-status')).toHaveTextContent('true');
      
      // Should save to localStorage
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'vimarsh_ab_optout',
        'true'
      );
    });

    it('should clear assignments when opting out', () => {
      renderWithProvider();
      
      // Opt out
      const optOutButton = screen.getByTestId('opt-out-btn');
      fireEvent.click(optOutButton);
      
      // Should remove assignments from localStorage
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith(
        'vimarsh_ab_assignments'
      );
    });

    it('should allow users to opt back in', () => {
      renderWithProvider();
      
      // Opt out first
      const optOutButton = screen.getByTestId('opt-out-btn');
      fireEvent.click(optOutButton);
      
      // Then opt back in
      const optInButton = screen.getByTestId('opt-in-btn');
      fireEvent.click(optInButton);
      
      // Should be opted in
      expect(screen.getByTestId('opt-out-status')).toHaveTextContent('false');
    });
  });

  describe('Persistence', () => {
    it('should load opt-out preference from localStorage', () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === 'vimarsh_ab_optout') return 'true';
        return null;
      });
      
      renderWithProvider();
      
      // Should respect saved opt-out preference
      expect(screen.getByTestId('opt-out-status')).toHaveTextContent('true');
    });

    it('should load test assignments from localStorage', () => {
      const savedAssignments = {
        'guidance-interface-layout': {
          testId: 'guidance-interface-layout',
          variantId: 'enhanced',
          assignedAt: new Date(),
          isControl: false
        }
      };
      
      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === 'vimarsh_ab_assignments') {
          return JSON.stringify(savedAssignments);
        }
        return null;
      });
      
      renderWithProvider();
      
      // Should use saved assignment
      expect(screen.getByTestId('guidance-variant')).toHaveTextContent('enhanced');
    });

    it('should handle localStorage errors gracefully', () => {
      mockLocalStorage.getItem.mockImplementation(() => {
        throw new Error('localStorage error');
      });
      
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      // Should still render without crashing
      renderWithProvider();
      expect(screen.getByTestId('active-tests-count')).toBeInTheDocument();
      
      // Should log warning
      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to load A/B testing preferences:',
        expect.any(Error)
      );
      
      consoleSpy.mockRestore();
    });
  });

  describe('Test Assignment Logic', () => {
    it('should provide consistent assignments based on user ID', () => {
      // Mock a specific user ID
      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === 'vimarsh_user_id') return 'test-user-123';
        return null;
      });
      
      const { unmount } = renderWithProvider();
      const firstVariant = screen.getByTestId('guidance-variant').textContent;
      
      // Unmount and render again
      unmount();
      renderWithProvider();
      const secondVariant = screen.getByTestId('guidance-variant').textContent;
      
      // Should get the same variant
      expect(firstVariant).toBe(secondVariant);
    });

    it('should respect test target percentage', () => {
      // This is harder to test deterministically, but we can check that
      // the assignment logic doesn't crash and provides valid variants
      renderWithProvider();
      
      const variant = screen.getByTestId('guidance-variant').textContent;
      expect(['control', 'enhanced', '']).toContain(variant);
    });
  });

  describe('Error Handling', () => {
    it('should handle missing tests gracefully', () => {
      render(
        <ABTestingProvider>
          <div data-testid="test">
            {(() => {
              const { getVariant } = useABTesting();
              return getVariant('non-existent-test');
            })()}
          </div>
        </ABTestingProvider>
      );
      
      // Should return null for non-existent test
      expect(screen.getByTestId('test')).toHaveTextContent('');
    });

    it('should handle invalid localStorage data', () => {
      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === 'vimarsh_ab_assignments') return 'invalid-json';
        return null;
      });
      
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      // Should still work
      renderWithProvider();
      expect(screen.getByTestId('active-tests-count')).toBeInTheDocument();
      
      consoleSpy.mockRestore();
    });
  });
});

describe('A/B Testing Integration', () => {
  it('should provide context throughout the app', () => {
    const { container } = renderWithProvider();
    
    // Should render without errors
    expect(container).toBeInTheDocument();
    
    // Should have test assignments
    const guidanceVariant = screen.getByTestId('guidance-variant').textContent;
    expect(guidanceVariant).toBeTruthy();
  });

  it('should maintain user experience quality', () => {
    renderWithProvider();
    
    // All test configurations should be valid
    const configText = screen.getByTestId('guidance-config').textContent;
    const config = JSON.parse(configText || '{}');
    
    // Layout should be valid
    expect(['standard', 'enhanced']).toContain(config.layout);
    
    // Citation position should be valid
    expect(['bottom', 'inline']).toContain(config.citationPosition);
    
    // Voice button size should be valid
    expect(['small', 'medium', 'large']).toContain(config.voiceButtonSize);
  });
});
