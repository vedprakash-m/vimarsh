import React, { createContext, useContext, ReactNode } from 'react';
import { usePrivacyAnalytics } from '../hooks/usePrivacyAnalytics';

interface AnalyticsContextType {
  trackEvent: (event: string, category: any, properties?: Record<string, any>) => void;
  trackSpiritualInteraction: (question: string, inputMethod: 'voice' | 'text', language: 'en' | 'hi') => void;
  trackVoiceInteraction: (event: 'voice_start' | 'voice_end' | 'voice_error', properties?: Record<string, any>) => void;
  trackErrorEvent: (error: Error, context: string, properties?: Record<string, any>) => void;
  trackPerformanceMetric: (metric: string, value: number, unit?: string) => void;
  trackAccessibilityUsage: (feature: string, properties?: Record<string, any>) => void;
  trackUserFeedback: (score: number, comment?: string, category?: string) => void;
  resetSession: () => void;
  sessionId: string;
  getAnalyticsSummary: () => any;
  clearAnalyticsData: () => void;
  exportUserData: () => void;
  userBehavior: any;
  isEnabled: boolean;
  setEnabled: (enabled: boolean) => void;
}

const AnalyticsContext = createContext<AnalyticsContextType | null>(null);

interface AnalyticsProviderProps {
  children: ReactNode;
  enableAnalytics?: boolean;
  enableBehaviorTracking?: boolean;
  anonymizeData?: boolean;
  sessionTimeout?: number;
  batchSize?: number;
  onBehaviorInsight?: (insight: any) => void;
  onError?: (error: Error) => void;
}

export const AnalyticsProvider: React.FC<AnalyticsProviderProps> = ({
  children,
  enableAnalytics = true,
  enableBehaviorTracking = true,
  anonymizeData = true,
  sessionTimeout = 30,
  batchSize = 10,
  onBehaviorInsight,
  onError
}) => {
  const analytics = usePrivacyAnalytics({
    enableAnalytics,
    enableBehaviorTracking,
    anonymizeData,
    sessionTimeout,
    batchSize,
    onBehaviorInsight,
    onError
  });

  return (
    <AnalyticsContext.Provider value={analytics}>
      {children}
    </AnalyticsContext.Provider>
  );
};

export const useAnalytics = (): AnalyticsContextType => {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};

// HOC for adding analytics to components
export const withAnalytics = <P extends object>(
  WrappedComponent: React.ComponentType<P>
) => {
  return (props: P) => {
    const analytics = useAnalytics();
    return <WrappedComponent {...props} analytics={analytics} />;
  };
};
