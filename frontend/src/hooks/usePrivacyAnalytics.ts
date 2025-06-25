import { useEffect, useCallback, useRef } from 'react';

interface AnalyticsEvent {
  event: string;
  timestamp: number;
  sessionId: string;
  category: 'spiritual' | 'interaction' | 'error' | 'performance' | 'voice' | 'accessibility';
  properties?: Record<string, any>;
  userId?: string;
  anonymous: boolean;
}

interface UserBehavior {
  sessionDuration: number;
  questionsAsked: number;
  languagePreference: 'en' | 'hi';
  voiceUsage: number;
  textUsage: number;
  featuresUsed: string[];
  spiritualTopics: string[];
  satisfactionScores: number[];
}

interface UsePrivacyAnalyticsOptions {
  enableAnalytics?: boolean;
  enableBehaviorTracking?: boolean;
  anonymizeData?: boolean;
  sessionTimeout?: number; // in minutes
  batchSize?: number;
  onBehaviorInsight?: (insight: UserBehavior) => void;
  onError?: (error: Error) => void;
}

interface AnalyticsState {
  isEnabled: boolean;
  sessionId: string;
  sessionStartTime: number;
  eventQueue: AnalyticsEvent[];
  userBehavior: UserBehavior;
  lastActivity: number;
}

const SPIRITUAL_KEYWORDS = [
  'dharma', 'karma', 'meditation', 'wisdom', 'peace', 'enlightenment',
  'devotion', 'bhakti', 'yoga', 'consciousness', 'atman', 'moksha',
  'samsara', 'ahimsa', 'righteousness', 'duty', 'truth', 'compassion'
];

export const usePrivacyAnalytics = (options: UsePrivacyAnalyticsOptions = {}) => {
  const {
    enableAnalytics = true,
    enableBehaviorTracking = true,
    anonymizeData = true,
    sessionTimeout = 30,
    batchSize = 10,
    onBehaviorInsight,
    onError
  } = options;

  const stateRef = useRef<AnalyticsState>({
    isEnabled: enableAnalytics,
    sessionId: generateSessionId(),
    sessionStartTime: Date.now(),
    eventQueue: [],
    userBehavior: {
      sessionDuration: 0,
      questionsAsked: 0,
      languagePreference: 'en',
      voiceUsage: 0,
      textUsage: 0,
      featuresUsed: [],
      spiritualTopics: [],
      satisfactionScores: []
    },
    lastActivity: Date.now()
  });

  const sessionTimeoutRef = useRef<number | null>(null);
  const batchTimeoutRef = useRef<number | null>(null);

  // Generate anonymous session ID
  function generateSessionId(): string {
    const timestamp = Date.now().toString(36);
    const randomStr = Math.random().toString(36).substring(2);
    return `vimarsh_${timestamp}_${randomStr}`;
  }

  // Sanitize data for privacy
  const sanitizeData = useCallback((data: any): any => {
    if (!anonymizeData) return data;

    const sanitized = { ...data };
    
    // Remove any potential PII
    delete sanitized.email;
    delete sanitized.name;
    delete sanitized.ip;
    delete sanitized.location;
    delete sanitized.deviceId;
    
    // Sanitize text content while preserving spiritual analysis
    if (sanitized.question) {
      sanitized.question = extractSpiritualTopics(sanitized.question);
    }
    
    if (sanitized.response) {
      sanitized.responseLength = sanitized.response.length;
      delete sanitized.response; // Don't store full responses
    }

    return sanitized;
  }, [anonymizeData]);

  // Extract spiritual topics from text for behavior analysis
  const extractSpiritualTopics = useCallback((text: string): string[] => {
    const lowerText = text.toLowerCase();
    return SPIRITUAL_KEYWORDS.filter(keyword => 
      lowerText.includes(keyword)
    );
  }, []);

  // Track an analytics event
  const trackEvent = useCallback((
    event: string,
    category: AnalyticsEvent['category'],
    properties: Record<string, any> = {}
  ) => {
    if (!stateRef.current.isEnabled) return;

    try {
      const sanitizedProperties = sanitizeData(properties);
      
      const analyticsEvent: AnalyticsEvent = {
        event,
        timestamp: Date.now(),
        sessionId: stateRef.current.sessionId,
        category,
        properties: sanitizedProperties,
        anonymous: anonymizeData
      };

      stateRef.current.eventQueue.push(analyticsEvent);
      stateRef.current.lastActivity = Date.now();

      // Process event queue if it reaches batch size
      if (stateRef.current.eventQueue.length >= batchSize) {
        processBatch();
      }

      // Update behavior tracking
      if (enableBehaviorTracking) {
        updateUserBehavior(event, category, sanitizedProperties);
      }

    } catch (error) {
      onError?.(error as Error);
    }
  }, [sanitizeData, anonymizeData, batchSize, enableBehaviorTracking, onError]);

  // Update user behavior metrics
  const updateUserBehavior = useCallback((
    event: string,
    category: AnalyticsEvent['category'],
    properties: Record<string, any>
  ) => {
    const behavior = stateRef.current.userBehavior;

    // Update session duration
    behavior.sessionDuration = Date.now() - stateRef.current.sessionStartTime;

    // Track question metrics
    if (event === 'question_asked') {
      behavior.questionsAsked++;
      
      if (properties.inputMethod === 'voice') {
        behavior.voiceUsage++;
      } else {
        behavior.textUsage++;
      }

      // Extract spiritual topics
      if (properties.topics) {
        const uniqueTopics = new Set([...behavior.spiritualTopics, ...properties.topics]);
        behavior.spiritualTopics = Array.from(uniqueTopics);
      }
    }

    // Track language preference
    if (properties.language) {
      behavior.languagePreference = properties.language;
    }

    // Track feature usage
    if (properties.feature && !behavior.featuresUsed.includes(properties.feature)) {
      behavior.featuresUsed.push(properties.feature);
    }

    // Track satisfaction
    if (event === 'feedback_given' && properties.score) {
      behavior.satisfactionScores.push(properties.score);
    }

    // Trigger insight callback
    onBehaviorInsight?.(behavior);
  }, [onBehaviorInsight]);

  // Process batch of events
  const processBatch = useCallback(() => {
    if (stateRef.current.eventQueue.length === 0) return;

    try {
      // In a real implementation, this would send to analytics service
      // For privacy, we're storing locally or sending to privacy-respecting service
      const events = [...stateRef.current.eventQueue];
      
      // Store in localStorage with rotation to prevent storage bloat
      storeEventsLocally(events);
      
      // Clear the queue
      stateRef.current.eventQueue = [];

    } catch (error) {
      onError?.(error as Error);
    }
  }, [onError]);

  // Store events locally with privacy considerations
  const storeEventsLocally = useCallback((events: AnalyticsEvent[]) => {
    try {
      const storageKey = 'vimarsh_analytics';
      const existingData = localStorage.getItem(storageKey);
      const existingEvents = existingData ? JSON.parse(existingData) : [];
      
      const allEvents = [...existingEvents, ...events];
      
      // Keep only last 1000 events to prevent storage bloat
      const limitedEvents = allEvents.slice(-1000);
      
      localStorage.setItem(storageKey, JSON.stringify(limitedEvents));
    } catch (error) {
      // Storage might be full or disabled
      console.warn('Failed to store analytics locally:', error);
    }
  }, []);

  // Get analytics summary for export or review
  const getAnalyticsSummary = useCallback(() => {
    try {
      const storageKey = 'vimarsh_analytics';
      const data = localStorage.getItem(storageKey);
      
      if (!data) return null;
      
      const events: AnalyticsEvent[] = JSON.parse(data);
      
      return {
        totalEvents: events.length,
        categories: events.reduce((acc, event) => {
          acc[event.category] = (acc[event.category] || 0) + 1;
          return acc;
        }, {} as Record<string, number>),
        sessionCount: new Set(events.map(e => e.sessionId)).size,
        timeRange: {
          earliest: Math.min(...events.map(e => e.timestamp)),
          latest: Math.max(...events.map(e => e.timestamp))
        },
        userBehavior: stateRef.current.userBehavior
      };
    } catch (error) {
      onError?.(error as Error);
      return null;
    }
  }, [onError]);

  // Clear all analytics data
  const clearAnalyticsData = useCallback(() => {
    try {
      localStorage.removeItem('vimarsh_analytics');
      stateRef.current.eventQueue = [];
      stateRef.current.userBehavior = {
        sessionDuration: 0,
        questionsAsked: 0,
        languagePreference: 'en',
        voiceUsage: 0,
        textUsage: 0,
        featuresUsed: [],
        spiritualTopics: [],
        satisfactionScores: []
      };
    } catch (error) {
      onError?.(error as Error);
    }
  }, [onError]);

  // Export analytics data (for GDPR compliance)
  const exportUserData = useCallback(() => {
    try {
      const summary = getAnalyticsSummary();
      const exportData = {
        sessionId: stateRef.current.sessionId,
        summary,
        exportTimestamp: Date.now(),
        anonymized: anonymizeData
      };
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `vimarsh-analytics-${stateRef.current.sessionId}.json`;
      link.click();
      
      URL.revokeObjectURL(url);
    } catch (error) {
      onError?.(error as Error);
    }
  }, [getAnalyticsSummary, anonymizeData, onError]);

  // Reset session (for new user or timeout)
  const resetSession = useCallback(() => {
    // Process any remaining events
    processBatch();
    
    // Generate new session
    stateRef.current.sessionId = generateSessionId();
    stateRef.current.sessionStartTime = Date.now();
    stateRef.current.lastActivity = Date.now();
    stateRef.current.userBehavior = {
      sessionDuration: 0,
      questionsAsked: 0,
      languagePreference: 'en',
      voiceUsage: 0,
      textUsage: 0,
      featuresUsed: [],
      spiritualTopics: [],
      satisfactionScores: []
    };
  }, [processBatch]);

  // Check for session timeout
  const checkSessionTimeout = useCallback(() => {
    const now = Date.now();
    const timeoutMs = sessionTimeout * 60 * 1000;
    
    if (now - stateRef.current.lastActivity > timeoutMs) {
      resetSession();
    }
  }, [sessionTimeout, resetSession]);

  // Set up periodic batch processing and session timeout checks
  useEffect(() => {
    if (!stateRef.current.isEnabled) return;

    // Set up batch processing timer
    batchTimeoutRef.current = window.setInterval(() => {
      if (stateRef.current.eventQueue.length > 0) {
        processBatch();
      }
    }, 30000); // Process batch every 30 seconds

    // Set up session timeout check
    sessionTimeoutRef.current = window.setInterval(() => {
      checkSessionTimeout();
    }, 60000); // Check every minute

    return () => {
      if (batchTimeoutRef.current) {
        clearInterval(batchTimeoutRef.current);
      }
      if (sessionTimeoutRef.current) {
        clearInterval(sessionTimeoutRef.current);
      }
    };
  }, [processBatch, checkSessionTimeout]);

  // Process remaining events on unmount
  useEffect(() => {
    return () => {
      processBatch();
    };
  }, [processBatch]);

  // Page visibility change handler
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Process batch when page becomes hidden
        processBatch();
      } else {
        // Update last activity when page becomes visible
        stateRef.current.lastActivity = Date.now();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [processBatch]);

  // Convenience methods for common events
  const trackSpiritualInteraction = useCallback((
    question: string,
    inputMethod: 'voice' | 'text',
    language: 'en' | 'hi'
  ) => {
    const topics = extractSpiritualTopics(question);
    trackEvent('question_asked', 'spiritual', {
      topics,
      inputMethod,
      language,
      questionLength: question.length,
      feature: 'spiritual_guidance'
    });
  }, [trackEvent, extractSpiritualTopics]);

  const trackVoiceInteraction = useCallback((
    event: 'voice_start' | 'voice_end' | 'voice_error',
    properties: Record<string, any> = {}
  ) => {
    trackEvent(event, 'voice', {
      ...properties,
      feature: 'voice_interface'
    });
  }, [trackEvent]);

  const trackErrorEvent = useCallback((
    error: Error,
    context: string,
    properties: Record<string, any> = {}
  ) => {
    trackEvent('error_occurred', 'error', {
      errorType: error.name,
      errorMessage: error.message.substring(0, 100), // Limit message length
      context,
      ...properties
    });
  }, [trackEvent]);

  const trackPerformanceMetric = useCallback((
    metric: string,
    value: number,
    unit: string = 'ms'
  ) => {
    trackEvent('performance_metric', 'performance', {
      metric,
      value,
      unit,
      timestamp: Date.now()
    });
  }, [trackEvent]);

  const trackAccessibilityUsage = useCallback((
    feature: string,
    properties: Record<string, any> = {}
  ) => {
    trackEvent('accessibility_used', 'accessibility', {
      feature,
      ...properties
    });
  }, [trackEvent]);

  const trackUserFeedback = useCallback((
    score: number,
    comment?: string,
    category?: string
  ) => {
    trackEvent('feedback_given', 'interaction', {
      score,
      comment: comment?.substring(0, 200), // Limit comment length
      category,
      feature: 'feedback'
    });
  }, [trackEvent]);

  return {
    // Core analytics methods
    trackEvent,
    trackSpiritualInteraction,
    trackVoiceInteraction,
    trackErrorEvent,
    trackPerformanceMetric,
    trackAccessibilityUsage,
    trackUserFeedback,

    // Session management
    resetSession,
    sessionId: stateRef.current.sessionId,

    // Data management
    getAnalyticsSummary,
    clearAnalyticsData,
    exportUserData,
    
    // Current behavior metrics
    userBehavior: stateRef.current.userBehavior,
    
    // Privacy controls
    isEnabled: stateRef.current.isEnabled,
    setEnabled: (enabled: boolean) => {
      stateRef.current.isEnabled = enabled;
    }
  };
};
