import { useEffect } from 'react';
import { useABTesting } from '../contexts/ABTestingContext';

/**
 * Hook for easily using A/B tests in components
 * Provides simplified interface for variant resolution and event tracking
 */

export interface UseABTestResult {
  variant: string | null;
  config: Record<string, any> | null;
  isInTest: boolean;
  trackInteraction: (eventData?: Record<string, any>) => void;
  trackConversion: (eventData?: Record<string, any>) => void;
  trackCompletion: (eventData?: Record<string, any>) => void;
}

export const useABTest = (testId: string): UseABTestResult => {
  const { 
    getVariant, 
    getVariantConfig, 
    isInTest: contextIsInTest, 
    trackEvent 
  } = useABTesting();

  const variant = getVariant(testId);
  const config = getVariantConfig(testId);
  const isInTest = contextIsInTest(testId);

  // Track impression when component mounts and user is in test
  useEffect(() => {
    if (isInTest) {
      trackEvent(testId, 'impression');
    }
  }, [testId, isInTest, trackEvent]);

  const trackInteraction = (eventData?: Record<string, any>) => {
    if (isInTest) {
      trackEvent(testId, 'interaction', eventData);
    }
  };

  const trackConversion = (eventData?: Record<string, any>) => {
    if (isInTest) {
      trackEvent(testId, 'conversion', eventData);
    }
  };

  const trackCompletion = (eventData?: Record<string, any>) => {
    if (isInTest) {
      trackEvent(testId, 'completion', eventData);
    }
  };

  return {
    variant,
    config,
    isInTest,
    trackInteraction,
    trackConversion,
    trackCompletion
  };
};

/**
 * Hook for testing specific interface variations
 * Provides type-safe configuration access for spiritual guidance interface
 */
export interface SpiritualGuidanceTestConfig {
  layout: 'standard' | 'enhanced';
  citationPosition: 'bottom' | 'inline';
  voiceButtonSize: 'small' | 'medium' | 'large';
  responseStyle?: 'traditional' | 'modern';
  showDivineIcon?: boolean;
  quoteStyle?: 'italic' | 'highlighted';
}

export const useSpiritualGuidanceTest = (): {
  interfaceConfig: SpiritualGuidanceTestConfig;
  responseConfig: SpiritualGuidanceTestConfig;
  trackGuidanceInteraction: (action: string, data?: Record<string, any>) => void;
  trackGuidanceConversion: (conversionType: string, data?: Record<string, any>) => void;
} => {
  const interfaceTest = useABTest('guidance-interface-layout');
  const responseTest = useABTest('response-formatting');

  // Default configurations
  const defaultInterfaceConfig: SpiritualGuidanceTestConfig = {
    layout: 'standard',
    citationPosition: 'bottom',
    voiceButtonSize: 'medium'
  };

  const defaultResponseConfig: SpiritualGuidanceTestConfig = {
    layout: 'standard',
    citationPosition: 'bottom',
    voiceButtonSize: 'medium',
    responseStyle: 'traditional',
    showDivineIcon: true,
    quoteStyle: 'italic'
  };

  // Merge test configurations with defaults
  const interfaceConfig: SpiritualGuidanceTestConfig = {
    ...defaultInterfaceConfig,
    ...(interfaceTest.config || {})
  };

  const responseConfig: SpiritualGuidanceTestConfig = {
    ...defaultResponseConfig,
    ...(responseTest.config || {})
  };

  const trackGuidanceInteraction = (action: string, data?: Record<string, any>) => {
    const eventData = { action, ...data };
    interfaceTest.trackInteraction(eventData);
    responseTest.trackInteraction(eventData);
  };

  const trackGuidanceConversion = (conversionType: string, data?: Record<string, any>) => {
    const eventData = { conversionType, ...data };
    interfaceTest.trackConversion(eventData);
    responseTest.trackConversion(eventData);
  };

  return {
    interfaceConfig,
    responseConfig,
    trackGuidanceInteraction,
    trackGuidanceConversion
  };
};

/**
 * Hook for testing voice interface variations
 */
export const useVoiceInterfaceTest = () => {
  const test = useABTest('voice-interface-optimization');
  
  const defaultConfig = {
    buttonStyle: 'circular',
    feedbackType: 'visual',
    autoStart: false,
    sensitivityLevel: 'medium'
  };

  const config = {
    ...defaultConfig,
    ...(test.config || {})
  };

  return {
    ...test,
    config,
    trackVoiceStart: () => test.trackInteraction({ action: 'voice_start' }),
    trackVoiceComplete: (duration: number) => test.trackCompletion({ duration }),
    trackVoiceError: (error: string) => test.trackInteraction({ action: 'voice_error', error })
  };
};

export default useABTest;
