/**
 * A/B Testing Framework for Vimarsh Frontend
 * 
 * Provides interface optimization testing while maintaining spiritual authenticity
 * and user privacy. Focused on UX improvements that enhance spiritual experience.
 */

// Simple UUID v4 implementation to avoid external dependency
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Test variant definitions
export interface TestVariant {
  id: string;
  name: string;
  description: string;
  weight: number; // Percentage allocation (0-100)
  config: Record<string, any>;
  spirituallyValidated: boolean; // Ensures spiritual appropriateness
}

export interface ABTest {
  id: string;
  name: string;
  description: string;
  startDate: Date;
  endDate?: Date;
  active: boolean;
  variants: TestVariant[];
  targetMetrics: string[];
  spiritualReviewRequired: boolean;
}

export interface UserTestAssignment {
  userId: string;
  sessionId: string;
  testId: string;
  variantId: string;
  assignedAt: Date;
  spiritualContentExposure: boolean;
}

export interface TestMetric {
  testId: string;
  variantId: string;
  userId: string;
  sessionId: string;
  metricName: string;
  value: number | string | boolean;
  timestamp: Date;
  spiritualContext?: {
    questionType: 'dharma' | 'karma' | 'moksha' | 'bhakti' | 'general';
    responseQuality: number; // 1-5 scale
    userSatisfaction: number; // 1-5 scale
  };
}

// Predefined test configurations for spiritual interface optimization
export const SPIRITUAL_AB_TESTS: ABTest[] = [
  {
    id: 'response-display-format',
    name: 'Response Display Format Optimization',
    description: 'Test different ways of displaying Lord Krishna\'s wisdom and citations',
    startDate: new Date(),
    active: true,
    variants: [
      {
        id: 'classic-format',
        name: 'Classic Citation Format',
        description: 'Traditional format with citations at the bottom',
        weight: 50,
        config: {
          citationPosition: 'bottom',
          responseStyle: 'classic',
          krishnaIconPosition: 'left',
          citationStyle: 'compact'
        },
        spirituallyValidated: true
      },
      {
        id: 'integrated-format',
        name: 'Integrated Citation Format',
        description: 'Citations integrated within the response flow',
        weight: 50,
        config: {
          citationPosition: 'inline',
          responseStyle: 'modern',
          krishnaIconPosition: 'center',
          citationStyle: 'expanded'
        },
        spirituallyValidated: true
      }
    ],
    targetMetrics: ['response_engagement', 'citation_clicks', 'session_duration'],
    spiritualReviewRequired: true
  },
  {
    id: 'voice-interface-onboarding',
    name: 'Voice Interface Introduction',
    description: 'Test different approaches to introducing voice features',
    startDate: new Date(),
    active: true,
    variants: [
      {
        id: 'prominent-voice',
        name: 'Prominent Voice CTA',
        description: 'Voice button prominently displayed with tutorial',
        weight: 50,
        config: {
          voiceButtonSize: 'large',
          showVoiceTutorial: true,
          voicePromptFrequency: 'high',
          microphoneIconStyle: 'animated'
        },
        spirituallyValidated: true
      },
      {
        id: 'subtle-voice',
        name: 'Subtle Voice Integration',
        description: 'Voice available but not prominently featured',
        weight: 50,
        config: {
          voiceButtonSize: 'medium',
          showVoiceTutorial: false,
          voicePromptFrequency: 'low',
          microphoneIconStyle: 'static'
        },
        spirituallyValidated: true
      }
    ],
    targetMetrics: ['voice_usage_rate', 'feature_discovery', 'user_satisfaction'],
    spiritualReviewRequired: false
  },
  {
    id: 'question-suggestion-style',
    name: 'Spiritual Question Suggestions',
    description: 'Test different formats for suggesting spiritual questions',
    startDate: new Date(),
    active: true,
    variants: [
      {
        id: 'category-based',
        name: 'Category-Based Suggestions',
        description: 'Questions organized by spiritual categories (Dharma, Karma, etc.)',
        weight: 50,
        config: {
          suggestionStyle: 'categorized',
          categories: ['dharma', 'karma', 'moksha', 'bhakti'],
          displayFormat: 'cards',
          questionCount: 3
        },
        spirituallyValidated: true
      },
      {
        id: 'contextual-flow',
        name: 'Contextual Flow Suggestions',
        description: 'Questions that flow naturally from previous conversations',
        weight: 50,
        config: {
          suggestionStyle: 'contextual',
          categories: [],
          displayFormat: 'list',
          questionCount: 5
        },
        spirituallyValidated: true
      }
    ],
    targetMetrics: ['suggestion_clicks', 'conversation_depth', 'spiritual_engagement'],
    spiritualReviewRequired: true
  }
];

class ABTestingFramework {
  private storage: Storage;
  private userId: string;
  private sessionId: string;
  private assignments: Map<string, UserTestAssignment> = new Map();

  constructor() {
    this.storage = window.localStorage;
    this.userId = this.getUserId();
    this.sessionId = this.generateSessionId();
    this.loadAssignments();
  }

  private getUserId(): string {
    let userId = this.storage.getItem('vimarsh_user_id');
    if (!userId) {
      userId = generateUUID();
      this.storage.setItem('vimarsh_user_id', userId);
    }
    return userId;
  }

  private generateSessionId(): string {
    let sessionId = sessionStorage.getItem('vimarsh_session_id');
    if (!sessionId) {
      sessionId = generateUUID();
      sessionStorage.setItem('vimarsh_session_id', sessionId);
    }
    return sessionId;
  }

  private loadAssignments(): void {
    const stored = this.storage.getItem('vimarsh_ab_assignments');
    if (stored) {
      try {
        const assignments = JSON.parse(stored);
        for (const assignment of assignments) {
          this.assignments.set(assignment.testId, {
            ...assignment,
            assignedAt: new Date(assignment.assignedAt)
          });
        }
      } catch (error) {
        console.warn('Failed to load A/B test assignments:', error);
      }
    }
  }

  private saveAssignments(): void {
    const assignments = Array.from(this.assignments.values());
    this.storage.setItem('vimarsh_ab_assignments', JSON.stringify(assignments));
  }

  /**
   * Get variant for a specific test, assigning user if not already assigned
   */
  public getVariant(testId: string): TestVariant | null {
    const test = SPIRITUAL_AB_TESTS.find(t => t.id === testId && t.active);
    if (!test) {
      return null;
    }

    // Check if user is already assigned
    const existing = this.assignments.get(testId);
    if (existing) {
      const variant = test.variants.find(v => v.id === existing.variantId);
      return variant || null;
    }

    // Assign user to variant based on weights
    const variant = this.assignToVariant(test);
    if (variant) {
      const assignment: UserTestAssignment = {
        userId: this.userId,
        sessionId: this.sessionId,
        testId,
        variantId: variant.id,
        assignedAt: new Date(),
        spiritualContentExposure: false
      };
      
      this.assignments.set(testId, assignment);
      this.saveAssignments();
    }

    return variant;
  }

  private assignToVariant(test: ABTest): TestVariant | null {
    const random = Math.random() * 100;
    let cumulative = 0;

    for (const variant of test.variants) {
      cumulative += variant.weight;
      if (random <= cumulative) {
        return variant;
      }
    }

    // Fallback to first variant
    return test.variants[0] || null;
  }

  /**
   * Track metric for A/B testing with spiritual context
   */
  public trackMetric(
    testId: string,
    metricName: string,
    value: number | string | boolean,
    spiritualContext?: TestMetric['spiritualContext']
  ): void {
    const assignment = this.assignments.get(testId);
    if (!assignment) {
      return;
    }

    const metric: TestMetric = {
      testId,
      variantId: assignment.variantId,
      userId: this.userId,
      sessionId: this.sessionId,
      metricName,
      value,
      timestamp: new Date(),
      spiritualContext
    };

    // Store metric (in production, this would be sent to analytics service)
    this.storeMetric(metric);

    // Mark spiritual content exposure if relevant
    if (spiritualContext) {
      assignment.spiritualContentExposure = true;
      this.saveAssignments();
    }
  }

  private storeMetric(metric: TestMetric): void {
    // In development, store in localStorage
    // In production, send to analytics service
    const stored = this.storage.getItem('vimarsh_ab_metrics') || '[]';
    const metrics = JSON.parse(stored);
    metrics.push(metric);
    
    // Keep only last 1000 metrics in localStorage
    if (metrics.length > 1000) {
      metrics.splice(0, metrics.length - 1000);
    }
    
    this.storage.setItem('vimarsh_ab_metrics', JSON.stringify(metrics));
  }

  /**
   * Get test configuration for a specific test
   */
  public getTestConfig(testId: string): Record<string, any> {
    const variant = this.getVariant(testId);
    return variant?.config || {};
  }

  /**
   * Check if user is participating in a test
   */
  public isParticipating(testId: string): boolean {
    return this.assignments.has(testId);
  }

  /**
   * Get all active test assignments for current user
   */
  public getActiveAssignments(): UserTestAssignment[] {
    return Array.from(this.assignments.values());
  }

  /**
   * Force assignment to specific variant (for testing/debugging)
   */
  public forceVariant(testId: string, variantId: string): boolean {
    const test = SPIRITUAL_AB_TESTS.find(t => t.id === testId);
    const variant = test?.variants.find(v => v.id === variantId);
    
    if (!test || !variant) {
      return false;
    }

    const assignment: UserTestAssignment = {
      userId: this.userId,
      sessionId: this.sessionId,
      testId,
      variantId,
      assignedAt: new Date(),
      spiritualContentExposure: false
    };

    this.assignments.set(testId, assignment);
    this.saveAssignments();
    return true;
  }

  /**
   * Export metrics for analysis (respecting privacy)
   */
  public exportMetrics(): TestMetric[] {
    const stored = this.storage.getItem('vimarsh_ab_metrics') || '[]';
    return JSON.parse(stored);
  }

  /**
   * Clear all test data (for privacy compliance)
   */
  public clearTestData(): void {
    this.assignments.clear();
    this.storage.removeItem('vimarsh_ab_assignments');
    this.storage.removeItem('vimarsh_ab_metrics');
  }
}

// Singleton instance
export const abTesting = new ABTestingFramework();

// React hook for using A/B testing in components
export function useABTest(testId: string) {
  const variant = abTesting.getVariant(testId);
  const config = abTesting.getTestConfig(testId);
  
  const trackMetric = (
    metricName: string,
    value: number | string | boolean,
    spiritualContext?: TestMetric['spiritualContext']
  ) => {
    abTesting.trackMetric(testId, metricName, value, spiritualContext);
  };

  return {
    variant,
    config,
    trackMetric,
    isParticipating: abTesting.isParticipating(testId)
  };
}

// Metrics tracking helpers for spiritual context
export const SpiritualMetrics = {
  RESPONSE_ENGAGEMENT: 'response_engagement',
  CITATION_CLICKS: 'citation_clicks',
  SESSION_DURATION: 'session_duration',
  VOICE_USAGE_RATE: 'voice_usage_rate',
  FEATURE_DISCOVERY: 'feature_discovery',
  USER_SATISFACTION: 'user_satisfaction',
  SUGGESTION_CLICKS: 'suggestion_clicks',
  CONVERSATION_DEPTH: 'conversation_depth',
  SPIRITUAL_ENGAGEMENT: 'spiritual_engagement',
  QUESTION_QUALITY: 'question_quality',
  RESPONSE_AUTHENTICITY: 'response_authenticity'
} as const;

export type SpiritualMetricType = typeof SpiritualMetrics[keyof typeof SpiritualMetrics];
