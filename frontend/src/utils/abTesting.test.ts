/**
 * Unit Tests for A/B Testing Framework
 * 
 * Tests the core A/B testing functionality, variant assignment,
 * metric tracking, and spiritual content compliance.
 */

import { abTesting, SPIRITUAL_AB_TESTS, SpiritualMetrics } from '../utils/abTesting';

// Mock localStorage and sessionStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();

const sessionStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();

// Mock window.localStorage and sessionStorage
Object.defineProperty(window, 'localStorage', { value: localStorageMock });
Object.defineProperty(window, 'sessionStorage', { value: sessionStorageMock });

describe('A/B Testing Framework', () => {
  beforeEach(() => {
    // Clear storage before each test
    localStorageMock.clear();
    sessionStorageMock.clear();
    
    // Reset the framework instance
    jest.clearAllMocks();
  });

  describe('User Assignment', () => {
    test('should assign user to variant consistently', () => {
      const testId = 'response-display-format';
      
      // Get variant multiple times
      const variant1 = abTesting.getVariant(testId);
      const variant2 = abTesting.getVariant(testId);
      const variant3 = abTesting.getVariant(testId);
      
      // Should return the same variant consistently
      expect(variant1).toBeTruthy();
      expect(variant2).toEqual(variant1);
      expect(variant3).toEqual(variant1);
      
      // Should be participating in the test
      expect(abTesting.isParticipating(testId)).toBe(true);
    });

    test('should assign users to variants based on weights', () => {
      const testId = 'response-display-format';
      const assignments: string[] = [];
      
      // Simulate multiple users (by clearing assignments)
      for (let i = 0; i < 100; i++) {
        localStorageMock.clear();
        sessionStorageMock.clear();
        
        // Create new instance for each "user"
        const variant = abTesting.getVariant(testId);
        if (variant) {
          assignments.push(variant.id);
        }
      }
      
      // Should have assignments to both variants
      const classicCount = assignments.filter(id => id === 'classic-format').length;
      const integratedCount = assignments.filter(id => id === 'integrated-format').length;
      
      expect(classicCount).toBeGreaterThan(20); // Roughly 50% (allowing variance)
      expect(integratedCount).toBeGreaterThan(20);
      expect(classicCount + integratedCount).toBe(100);
    });

    test('should return null for inactive tests', () => {
      const inactiveTestId = 'non-existent-test';
      const variant = abTesting.getVariant(inactiveTestId);
      
      expect(variant).toBeNull();
      expect(abTesting.isParticipating(inactiveTestId)).toBe(false);
    });

    test('should persist assignments across page loads', () => {
      const testId = 'voice-interface-onboarding';
      
      // Get initial variant
      const variant1 = abTesting.getVariant(testId);
      
      // Simulate page reload by checking localStorage
      const storedAssignments = localStorageMock.getItem('vimarsh_ab_assignments');
      expect(storedAssignments).toBeTruthy();
      
      const assignments = JSON.parse(storedAssignments!);
      const testAssignment = assignments.find((a: any) => a.testId === testId);
      
      expect(testAssignment).toBeTruthy();
      expect(testAssignment.variantId).toBe(variant1?.id);
    });
  });

  describe('Metric Tracking', () => {
    test('should track metrics with spiritual context', () => {
      const testId = 'response-display-format';
      
      // Assign to variant first
      const variant = abTesting.getVariant(testId);
      expect(variant).toBeTruthy();
      
      // Track a spiritual metric
      abTesting.trackMetric(
        testId,
        SpiritualMetrics.RESPONSE_ENGAGEMENT,
        1,
        {
          questionType: 'dharma',
          responseQuality: 5,
          userSatisfaction: 4
        }
      );
      
      // Check if metric was stored
      const storedMetrics = localStorageMock.getItem('vimarsh_ab_metrics');
      expect(storedMetrics).toBeTruthy();
      
      const metrics = JSON.parse(storedMetrics!);
      expect(metrics).toHaveLength(1);
      
      const metric = metrics[0];
      expect(metric.testId).toBe(testId);
      expect(metric.variantId).toBe(variant!.id);
      expect(metric.metricName).toBe(SpiritualMetrics.RESPONSE_ENGAGEMENT);
      expect(metric.value).toBe(1);
      expect(metric.spiritualContext).toEqual({
        questionType: 'dharma',
        responseQuality: 5,
        userSatisfaction: 4
      });
    });

    test('should not track metrics for non-participating users', () => {
      const testId = 'non-existent-test';
      
      // Try to track metric without variant assignment
      abTesting.trackMetric(testId, SpiritualMetrics.CITATION_CLICKS, 1);
      
      // Should not store any metrics
      const storedMetrics = localStorageMock.getItem('vimarsh_ab_metrics');
      expect(storedMetrics).toBeFalsy();
    });

    test('should limit stored metrics to prevent memory issues', () => {
      const testId = 'response-display-format';
      
      // Assign to variant
      abTesting.getVariant(testId);
      
      // Track many metrics
      for (let i = 0; i < 1100; i++) {
        abTesting.trackMetric(testId, SpiritualMetrics.SESSION_DURATION, i);
      }
      
      // Should keep only last 1000 metrics
      const storedMetrics = localStorageMock.getItem('vimarsh_ab_metrics');
      const metrics = JSON.parse(storedMetrics!);
      
      expect(metrics).toHaveLength(1000);
      expect(metrics[0].value).toBe(100); // First 100 should be removed
      expect(metrics[999].value).toBe(1099); // Last one should be preserved
    });
  });

  describe('Test Configuration', () => {
    test('should return correct test configuration', () => {
      const testId = 'response-display-format';
      const variant = abTesting.getVariant(testId);
      const config = abTesting.getTestConfig(testId);
      
      expect(variant).toBeTruthy();
      expect(config).toEqual(variant!.config);
      
      // Should have expected configuration properties
      expect(config).toHaveProperty('citationPosition');
      expect(config).toHaveProperty('responseStyle');
      expect(config).toHaveProperty('krishnaIconPosition');
      expect(config).toHaveProperty('citationStyle');
    });

    test('should return empty config for invalid tests', () => {
      const config = abTesting.getTestConfig('invalid-test');
      expect(config).toEqual({});
    });
  });

  describe('Force Variant Assignment', () => {
    test('should allow forced variant assignment for testing', () => {
      const testId = 'voice-interface-onboarding';
      const variantId = 'prominent-voice';
      
      const success = abTesting.forceVariant(testId, variantId);
      expect(success).toBe(true);
      
      const variant = abTesting.getVariant(testId);
      expect(variant?.id).toBe(variantId);
      expect(abTesting.isParticipating(testId)).toBe(true);
    });

    test('should reject invalid forced assignments', () => {
      const success1 = abTesting.forceVariant('invalid-test', 'invalid-variant');
      const success2 = abTesting.forceVariant('response-display-format', 'invalid-variant');
      
      expect(success1).toBe(false);
      expect(success2).toBe(false);
    });
  });

  describe('Privacy and Data Management', () => {
    test('should clear all test data on request', () => {
      const testId = 'response-display-format';
      
      // Generate some test data
      abTesting.getVariant(testId);
      abTesting.trackMetric(testId, SpiritualMetrics.RESPONSE_ENGAGEMENT, 1);
      
      // Verify data exists
      expect(localStorageMock.getItem('vimarsh_ab_assignments')).toBeTruthy();
      expect(localStorageMock.getItem('vimarsh_ab_metrics')).toBeTruthy();
      
      // Clear data
      abTesting.clearTestData();
      
      // Verify data is cleared
      expect(localStorageMock.getItem('vimarsh_ab_assignments')).toBeFalsy();
      expect(localStorageMock.getItem('vimarsh_ab_metrics')).toBeFalsy();
    });

    test('should export metrics for analysis', () => {
      const testId = 'question-suggestion-style';
      
      abTesting.getVariant(testId);
      abTesting.trackMetric(testId, SpiritualMetrics.SUGGESTION_CLICKS, 3);
      abTesting.trackMetric(testId, SpiritualMetrics.CONVERSATION_DEPTH, 5);
      
      const exportedMetrics = abTesting.exportMetrics();
      
      expect(exportedMetrics).toHaveLength(2);
      expect(exportedMetrics[0].metricName).toBe(SpiritualMetrics.SUGGESTION_CLICKS);
      expect(exportedMetrics[1].metricName).toBe(SpiritualMetrics.CONVERSATION_DEPTH);
    });
  });

  describe('Spiritual Content Validation', () => {
    test('should ensure all test variants are spiritually validated', () => {
      SPIRITUAL_AB_TESTS.forEach(test => {
        test.variants.forEach(variant => {
          expect(variant.spirituallyValidated).toBe(true);
        });
      });
    });

    test('should mark tests requiring spiritual review', () => {
      const responseTest = SPIRITUAL_AB_TESTS.find(t => t.id === 'response-display-format');
      const questionTest = SPIRITUAL_AB_TESTS.find(t => t.id === 'question-suggestion-style');
      const voiceTest = SPIRITUAL_AB_TESTS.find(t => t.id === 'voice-interface-onboarding');
      
      expect(responseTest?.spiritualReviewRequired).toBe(true);
      expect(questionTest?.spiritualReviewRequired).toBe(true);
      expect(voiceTest?.spiritualReviewRequired).toBe(false);
    });

    test('should track spiritual content exposure', () => {
      const testId = 'response-display-format';
      
      // Assign variant
      abTesting.getVariant(testId);
      
      // Track metric with spiritual context
      abTesting.trackMetric(
        testId,
        SpiritualMetrics.SPIRITUAL_ENGAGEMENT,
        1,
        {
          questionType: 'moksha',
          responseQuality: 4,
          userSatisfaction: 5
        }
      );
      
      // Should mark spiritual content exposure
      const assignments = abTesting.getActiveAssignments();
      const testAssignment = assignments.find(a => a.testId === testId);
      
      expect(testAssignment?.spiritualContentExposure).toBe(true);
    });
  });

  describe('Test Definitions', () => {
    test('should have valid test definitions', () => {
      expect(SPIRITUAL_AB_TESTS).toHaveLength(3);
      
      SPIRITUAL_AB_TESTS.forEach(test => {
        // Basic test structure
        expect(test.id).toBeTruthy();
        expect(test.name).toBeTruthy();
        expect(test.description).toBeTruthy();
        expect(test.active).toBe(true);
        expect(Array.isArray(test.variants)).toBe(true);
        expect(Array.isArray(test.targetMetrics)).toBe(true);
        
        // Variant structure
        expect(test.variants.length).toBeGreaterThan(0);
        test.variants.forEach(variant => {
          expect(variant.id).toBeTruthy();
          expect(variant.name).toBeTruthy();
          expect(variant.weight).toBeGreaterThan(0);
          expect(variant.weight).toBeLessThanOrEqual(100);
          expect(typeof variant.config).toBe('object');
          expect(variant.spirituallyValidated).toBe(true);
        });
        
        // Weight distribution should total 100%
        const totalWeight = test.variants.reduce((sum, v) => sum + v.weight, 0);
        expect(totalWeight).toBe(100);
      });
    });

    test('should use defined spiritual metrics', () => {
      const validMetrics = Object.values(SpiritualMetrics);
      
      SPIRITUAL_AB_TESTS.forEach(test => {
        test.targetMetrics.forEach(metric => {
          expect(validMetrics.includes(metric as any)).toBe(true);
        });
      });
    });
  });
});
