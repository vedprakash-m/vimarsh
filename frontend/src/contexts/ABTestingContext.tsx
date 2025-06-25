import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';

/**
 * A/B Testing Framework for Vimarsh
 * Provides privacy-respecting interface optimization experiments
 * Aligns with spiritual guidance principles and user consent
 */

export interface ABTest {
  id: string;
  name: string;
  description: string;
  variants: ABVariant[];
  startDate: Date;
  endDate?: Date;
  isActive: boolean;
  targetPercentage: number; // Percentage of users to include in test
  metadata?: Record<string, any>;
}

export interface ABVariant {
  id: string;
  name: string;
  description: string;
  weight: number; // Distribution weight (sum should equal 1.0 across variants)
  config: Record<string, any>; // Configuration options for this variant
}

export interface ABTestAssignment {
  testId: string;
  variantId: string;
  assignedAt: Date;
  isControl: boolean;
}

export interface ABTestEvent {
  testId: string;
  variantId: string;
  eventType: 'impression' | 'interaction' | 'conversion' | 'completion';
  eventData?: Record<string, any>;
  timestamp: Date;
}

interface ABTestingContextType {
  // Test management
  activeTests: ABTest[];
  userAssignments: Record<string, ABTestAssignment>;
  
  // Variant resolution
  getVariant: (testId: string) => string | null;
  getVariantConfig: (testId: string) => Record<string, any> | null;
  isInTest: (testId: string) => boolean;
  
  // Event tracking
  trackEvent: (testId: string, eventType: ABTestEvent['eventType'], eventData?: Record<string, any>) => void;
  
  // Opt-out functionality
  isOptedOut: boolean;
  setOptOut: (optOut: boolean) => void;
  
  // Test results
  getTestResults: (testId: string) => ABTestResults | null;
}

export interface ABTestResults {
  testId: string;
  variants: Array<{
    variantId: string;
    participants: number;
    conversions: number;
    conversionRate: number;
    significance: number;
  }>;
  isSignificant: boolean;
  recommendedVariant?: string;
}

const ABTestingContext = createContext<ABTestingContextType | undefined>(undefined);

// Sample test configurations aligned with spiritual guidance interface
const DEFAULT_TESTS: ABTest[] = [
  {
    id: 'guidance-interface-layout',
    name: 'Spiritual Guidance Interface Layout',
    description: 'Test different layouts for the main guidance interface',
    variants: [
      {
        id: 'control',
        name: 'Current Layout',
        description: 'Standard interface layout',
        weight: 0.5,
        config: {
          layout: 'standard',
          citationPosition: 'bottom',
          voiceButtonSize: 'medium'
        }
      },
      {
        id: 'enhanced',
        name: 'Enhanced Layout',
        description: 'Enhanced interface with better visual hierarchy',
        weight: 0.5,
        config: {
          layout: 'enhanced',
          citationPosition: 'inline',
          voiceButtonSize: 'large'
        }
      }
    ],
    startDate: new Date(),
    isActive: true,
    targetPercentage: 50, // Only test with 50% of users
    metadata: {
      category: 'interface',
      priority: 'high'
    }
  },
  {
    id: 'response-formatting',
    name: 'Divine Response Formatting',
    description: 'Test different ways to format Lord Krishna\'s responses',
    variants: [
      {
        id: 'traditional',
        name: 'Traditional Format',
        description: 'Classic response format with clear attribution',
        weight: 0.5,
        config: {
          responseStyle: 'traditional',
          showDivineIcon: true,
          quoteStyle: 'italic'
        }
      },
      {
        id: 'modern',
        name: 'Modern Format',
        description: 'Modern response format with enhanced readability',
        weight: 0.5,
        config: {
          responseStyle: 'modern',
          showDivineIcon: true,
          quoteStyle: 'highlighted'
        }
      }
    ],
    startDate: new Date(),
    isActive: true,
    targetPercentage: 30,
    metadata: {
      category: 'content',
      priority: 'medium'
    }
  }
];

export const ABTestingProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [activeTests] = useState<ABTest[]>(DEFAULT_TESTS);
  const [userAssignments, setUserAssignments] = useState<Record<string, ABTestAssignment>>({});
  const [isOptedOut, setIsOptedOut] = useState<boolean>(false);
  const [testEvents, setTestEvents] = useState<ABTestEvent[]>([]);

  // Load user preferences and assignments on mount
  useEffect(() => {
    try {
      const storedOptOut = localStorage.getItem('vimarsh_ab_optout');
      const storedAssignments = localStorage.getItem('vimarsh_ab_assignments');
      
      if (storedOptOut) {
        setIsOptedOut(JSON.parse(storedOptOut));
      }
      
      if (storedAssignments && !isOptedOut) {
        setUserAssignments(JSON.parse(storedAssignments));
      }
    } catch (error) {
      console.warn('Failed to load A/B testing preferences:', error);
    }
  }, [isOptedOut]);

  // Assign user to tests based on consistent hashing
  const assignUserToTest = (test: ABTest): ABTestAssignment | null => {
    if (isOptedOut || !test.isActive) {
      return null;
    }

    // Check if user should be included in this test
    const userId = getUserId();
    const hash = hashString(`${userId}-${test.id}`);
    const shouldInclude = (hash % 100) < test.targetPercentage;
    
    if (!shouldInclude) {
      return null;
    }

    // Assign to variant based on weight distribution
    const random = (hash % 1000) / 1000; // Convert to 0-1 range
    let cumulativeWeight = 0;
    
    for (const variant of test.variants) {
      cumulativeWeight += variant.weight;
      if (random <= cumulativeWeight) {
        const assignment: ABTestAssignment = {
          testId: test.id,
          variantId: variant.id,
          assignedAt: new Date(),
          isControl: variant.id === 'control'
        };
        
        return assignment;
      }
    }
    
    // Fallback to control
    return {
      testId: test.id,
      variantId: test.variants[0].id,
      assignedAt: new Date(),
      isControl: true
    };
  };

  // Get or create assignment for a test
  const getAssignment = useCallback((testId: string): ABTestAssignment | null => {
    if (isOptedOut) {
      return null;
    }

    // Return existing assignment
    if (userAssignments[testId]) {
      return userAssignments[testId];
    }

    // Create new assignment
    const test = activeTests.find(t => t.id === testId);
    if (!test) {
      return null;
    }

    const assignment = assignUserToTest(test);
    if (assignment) {
      // Defer state update to avoid render-time updates
      setTimeout(() => {
        const newAssignments = { ...userAssignments, [testId]: assignment };
        setUserAssignments(newAssignments);
        
        try {
          localStorage.setItem('vimarsh_ab_assignments', JSON.stringify(newAssignments));
        } catch (error) {
          console.warn('Failed to save A/B test assignment:', error);
        }
      }, 0);
    }

    return assignment;
  }, [isOptedOut, userAssignments, activeTests]);

  const getVariant = (testId: string): string | null => {
    const assignment = getAssignment(testId);
    return assignment?.variantId || null;
  };

  const getVariantConfig = (testId: string): Record<string, any> | null => {
    const variantId = getVariant(testId);
    if (!variantId) {
      return null;
    }

    const test = activeTests.find(t => t.id === testId);
    const variant = test?.variants.find(v => v.id === variantId);
    return variant?.config || null;
  };

  const isInTest = (testId: string): boolean => {
    return getVariant(testId) !== null;
  };

  const trackEvent = (
    testId: string, 
    eventType: ABTestEvent['eventType'], 
    eventData?: Record<string, any>
  ): void => {
    if (isOptedOut) {
      return;
    }

    const assignment = getAssignment(testId);
    if (!assignment) {
      return;
    }

    const event: ABTestEvent = {
      testId,
      variantId: assignment.variantId,
      eventType,
      eventData,
      timestamp: new Date()
    };

    setTestEvents(prev => [...prev, event]);

    // In a production environment, you would send this to your analytics service
    console.log('A/B Test Event:', event);
  };

  const setOptOut = (optOut: boolean): void => {
    setIsOptedOut(optOut);
    
    try {
      localStorage.setItem('vimarsh_ab_optout', JSON.stringify(optOut));
      
      if (optOut) {
        // Clear assignments when opting out
        setUserAssignments({});
        localStorage.removeItem('vimarsh_ab_assignments');
      }
    } catch (error) {
      console.warn('Failed to save A/B testing opt-out preference:', error);
    }
  };

  const getTestResults = (testId: string): ABTestResults | null => {
    // This would typically fetch from your analytics backend
    // For now, return null as this is a framework implementation
    return null;
  };

  const contextValue: ABTestingContextType = {
    activeTests,
    userAssignments,
    getVariant,
    getVariantConfig,
    isInTest,
    trackEvent,
    isOptedOut,
    setOptOut,
    getTestResults
  };

  return (
    <ABTestingContext.Provider value={contextValue}>
      {children}
    </ABTestingContext.Provider>
  );
};

export const useABTesting = (): ABTestingContextType => {
  const context = useContext(ABTestingContext);
  if (!context) {
    throw new Error('useABTesting must be used within an ABTestingProvider');
  }
  return context;
};

// Utility functions
function getUserId(): string {
  // Generate or retrieve a consistent user ID for assignment
  try {
    let userId = localStorage.getItem('vimarsh_user_id');
    if (!userId) {
      userId = Math.random().toString(36).substring(2, 15);
      try {
        localStorage.setItem('vimarsh_user_id', userId);
      } catch (error) {
        // Fallback to session-based ID if localStorage fails
        userId = sessionStorage.getItem('vimarsh_session_id') || Math.random().toString(36).substring(2, 15);
        try {
          sessionStorage.setItem('vimarsh_session_id', userId);
        } catch (sessionError) {
          // Final fallback to temporary ID
          return Math.random().toString(36).substring(2, 15);
        }
      }
    }
    return userId;
  } catch (error) {
    // Fallback to temporary ID if all storage fails
    return Math.random().toString(36).substring(2, 15);
  }
}

function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash);
}

export default ABTestingContext;
