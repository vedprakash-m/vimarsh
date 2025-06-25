import { renderHook, act } from '@testing-library/react';
import React from 'react';
import { ABTestingProvider } from '../contexts/ABTestingContext';
import { useABTest, useSpiritualGuidanceTest, useVoiceInterfaceTest } from './useABTest';

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

const wrapper = ({ children }: { children: React.ReactNode }) => (
  React.createElement(ABTestingProvider, null, children)
);

describe('useABTest Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  describe('Basic Functionality', () => {
    it('should return test variant and configuration', () => {
      const { result } = renderHook(
        () => useABTest('guidance-interface-layout'),
        { wrapper }
      );

      // Should have variant assignment
      expect(['control', 'enhanced']).toContain(result.current.variant);
      
      // Should have configuration
      expect(result.current.config).toBeTruthy();
      expect(result.current.config).toHaveProperty('layout');
      
      // Should show test participation
      expect(result.current.isInTest).toBe(true);
    });

    it('should track impression on mount', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      renderHook(
        () => useABTest('guidance-interface-layout'),
        { wrapper }
      );

      // Should track impression event
      expect(consoleSpy).toHaveBeenCalledWith(
        'A/B Test Event:',
        expect.objectContaining({
          eventType: 'impression',
          testId: 'guidance-interface-layout'
        })
      );
      
      consoleSpy.mockRestore();
    });

    it('should provide event tracking functions', () => {
      const { result } = renderHook(
        () => useABTest('guidance-interface-layout'),
        { wrapper }
      );

      // Should have tracking functions
      expect(typeof result.current.trackInteraction).toBe('function');
      expect(typeof result.current.trackConversion).toBe('function');
      expect(typeof result.current.trackCompletion).toBe('function');
    });
  });

  describe('Event Tracking', () => {
    it('should track interaction events', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      const { result } = renderHook(
        () => useABTest('guidance-interface-layout'),
        { wrapper }
      );

      act(() => {
        result.current.trackInteraction({ action: 'button_click' });
      });

      expect(consoleSpy).toHaveBeenCalledWith(
        'A/B Test Event:',
        expect.objectContaining({
          eventType: 'interaction',
          eventData: { action: 'button_click' }
        })
      );
      
      consoleSpy.mockRestore();
    });

    it('should track conversion events', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      const { result } = renderHook(
        () => useABTest('guidance-interface-layout'),
        { wrapper }
      );

      act(() => {
        result.current.trackConversion({ type: 'form_submit' });
      });

      expect(consoleSpy).toHaveBeenCalledWith(
        'A/B Test Event:',
        expect.objectContaining({
          eventType: 'conversion',
          eventData: { type: 'form_submit' }
        })
      );
      
      consoleSpy.mockRestore();
    });

    it('should track completion events', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      const { result } = renderHook(
        () => useABTest('guidance-interface-layout'),
        { wrapper }
      );

      act(() => {
        result.current.trackCompletion({ duration: 120 });
      });

      expect(consoleSpy).toHaveBeenCalledWith(
        'A/B Test Event:',
        expect.objectContaining({
          eventType: 'completion',
          eventData: { duration: 120 }
        })
      );
      
      consoleSpy.mockRestore();
    });
  });

  describe('Non-existent Test', () => {
    it('should handle non-existent tests gracefully', () => {
      const { result } = renderHook(
        () => useABTest('non-existent-test'),
        { wrapper }
      );

      // Should return null values for non-existent test
      expect(result.current.variant).toBeNull();
      expect(result.current.config).toBeNull();
      expect(result.current.isInTest).toBe(false);
    });

    it('should not track events for non-existent tests', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      const { result } = renderHook(
        () => useABTest('non-existent-test'),
        { wrapper }
      );

      act(() => {
        result.current.trackInteraction({ action: 'test' });
      });

      // Should not track events for non-existent tests
      expect(consoleSpy).not.toHaveBeenCalledWith(
        'A/B Test Event:',
        expect.any(Object)
      );
      
      consoleSpy.mockRestore();
    });
  });
});

describe('useSpiritualGuidanceTest Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  it('should provide interface and response configurations', () => {
    const { result } = renderHook(
      () => useSpiritualGuidanceTest(),
      { wrapper }
    );

    // Should have interface configuration
    expect(result.current.interfaceConfig).toBeTruthy();
    expect(result.current.interfaceConfig).toHaveProperty('layout');
    expect(result.current.interfaceConfig).toHaveProperty('citationPosition');
    expect(result.current.interfaceConfig).toHaveProperty('voiceButtonSize');

    // Should have response configuration
    expect(result.current.responseConfig).toBeTruthy();
    expect(result.current.responseConfig).toHaveProperty('responseStyle');
    expect(result.current.responseConfig).toHaveProperty('showDivineIcon');
    expect(result.current.responseConfig).toHaveProperty('quoteStyle');
  });

  it('should provide guidance-specific tracking functions', () => {
    const { result } = renderHook(
      () => useSpiritualGuidanceTest(),
      { wrapper }
    );

    // Should have guidance-specific tracking functions
    expect(typeof result.current.trackGuidanceInteraction).toBe('function');
    expect(typeof result.current.trackGuidanceConversion).toBe('function');
  });

  it('should track guidance interactions across multiple tests', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    
    const { result } = renderHook(
      () => useSpiritualGuidanceTest(),
      { wrapper }
    );

    act(() => {
      result.current.trackGuidanceInteraction('message_sent', { length: 50 });
    });

    // Should track events for both interface and response tests
    expect(consoleSpy).toHaveBeenCalledTimes(2); // impression + interaction
    
    consoleSpy.mockRestore();
  });

  it('should merge configurations with defaults', () => {
    const { result } = renderHook(
      () => useSpiritualGuidanceTest(),
      { wrapper }
    );

    // Should have default values merged with test configurations
    const { interfaceConfig, responseConfig } = result.current;
    
    // Interface config should have all required properties
    expect(interfaceConfig.layout).toBeDefined();
    expect(interfaceConfig.citationPosition).toBeDefined();
    expect(interfaceConfig.voiceButtonSize).toBeDefined();
    
    // Response config should have all required properties
    expect(responseConfig.responseStyle).toBeDefined();
    expect(responseConfig.showDivineIcon).toBeDefined();
    expect(responseConfig.quoteStyle).toBeDefined();
  });

  it('should validate configuration values', () => {
    const { result } = renderHook(
      () => useSpiritualGuidanceTest(),
      { wrapper }
    );

    const { interfaceConfig, responseConfig } = result.current;
    
    // Should have valid layout values
    expect(['standard', 'enhanced']).toContain(interfaceConfig.layout);
    
    // Should have valid citation position values
    expect(['bottom', 'inline']).toContain(interfaceConfig.citationPosition);
    
    // Should have valid voice button size values
    expect(['small', 'medium', 'large']).toContain(interfaceConfig.voiceButtonSize);
    
    // Should have valid response style values
    expect(['traditional', 'modern']).toContain(responseConfig.responseStyle);
    
    // Should have valid quote style values
    expect(['italic', 'highlighted']).toContain(responseConfig.quoteStyle);
    
    // Should have valid boolean values
    expect(typeof responseConfig.showDivineIcon).toBe('boolean');
  });
});

describe('useVoiceInterfaceTest Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  it('should provide voice interface configuration', () => {
    const { result } = renderHook(
      () => useVoiceInterfaceTest(),
      { wrapper }
    );

    // Should have default voice configuration
    expect(result.current.config).toBeTruthy();
    expect(result.current.config).toHaveProperty('buttonStyle');
    expect(result.current.config).toHaveProperty('feedbackType');
    expect(result.current.config).toHaveProperty('autoStart');
    expect(result.current.config).toHaveProperty('sensitivityLevel');
  });

  it('should provide voice-specific tracking functions', () => {
    const { result } = renderHook(
      () => useVoiceInterfaceTest(),
      { wrapper }
    );

    // Should have voice-specific tracking functions
    expect(typeof result.current.trackVoiceStart).toBe('function');
    expect(typeof result.current.trackVoiceComplete).toBe('function');
    expect(typeof result.current.trackVoiceError).toBe('function');
  });

  it('should track voice events with appropriate data', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    
    const { result } = renderHook(
      () => useVoiceInterfaceTest(),
      { wrapper }
    );

    act(() => {
      result.current.trackVoiceStart();
    });

    act(() => {
      result.current.trackVoiceComplete(1500);
    });

    act(() => {
      result.current.trackVoiceError('microphone_denied');
    });

    // Should track voice-specific events
    expect(consoleSpy).toHaveBeenCalledWith(
      'A/B Test Event:',
      expect.objectContaining({
        eventType: 'interaction',
        eventData: { action: 'voice_start' }
      })
    );

    expect(consoleSpy).toHaveBeenCalledWith(
      'A/B Test Event:',
      expect.objectContaining({
        eventType: 'completion',
        eventData: { duration: 1500 }
      })
    );

    expect(consoleSpy).toHaveBeenCalledWith(
      'A/B Test Event:',
      expect.objectContaining({
        eventType: 'interaction',
        eventData: { action: 'voice_error', error: 'microphone_denied' }
      })
    );
    
    consoleSpy.mockRestore();
  });

  it('should handle non-existent voice test gracefully', () => {
    // The voice test doesn't exist in our default tests, so it should return defaults
    const { result } = renderHook(
      () => useVoiceInterfaceTest(),
      { wrapper }
    );

    // Should have default configuration
    expect(result.current.config.buttonStyle).toBe('circular');
    expect(result.current.config.feedbackType).toBe('visual');
    expect(result.current.config.autoStart).toBe(false);
    expect(result.current.config.sensitivityLevel).toBe('medium');
    
    // Should not be in test
    expect(result.current.isInTest).toBe(false);
  });
});

describe('Hook Error Handling', () => {
  it('should handle context provider absence gracefully', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    try {
      renderHook(() => useABTest('test'));
    } catch (error) {
      expect(error).toBeInstanceOf(Error);
      expect((error as Error).message).toContain('useABTesting must be used within an ABTestingProvider');
    }
    
    consoleSpy.mockRestore();
  });

  it('should handle localStorage errors in hooks', () => {
    mockLocalStorage.getItem.mockImplementation(() => {
      throw new Error('localStorage error');
    });

    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

    // Should still work despite localStorage errors
    const { result } = renderHook(
      () => useSpiritualGuidanceTest(),
      { wrapper }
    );

    expect(result.current.interfaceConfig).toBeTruthy();
    expect(result.current.responseConfig).toBeTruthy();
    
    consoleSpy.mockRestore();
  });
});
