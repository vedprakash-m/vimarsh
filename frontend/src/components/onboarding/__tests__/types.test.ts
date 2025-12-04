/**
 * Onboarding Types Tests
 */

import {
  OnboardingStep,
  QuizQuestion,
  QuizOption,
  QuizResponse,
  DomainScore,
  PersonalityMatch,
  OnboardingState,
  QuizResult
} from '../types';

describe('Onboarding Types', () => {
  describe('OnboardingStep', () => {
    it('should accept all valid steps', () => {
      const steps: OnboardingStep[] = [
        'welcome',
        'quiz',
        'first_chat',
        'discovery',
        'complete'
      ];

      expect(steps).toHaveLength(5);
      steps.forEach(step => {
        expect(typeof step).toBe('string');
      });
    });
  });

  describe('QuizQuestion', () => {
    it('should create valid quiz question', () => {
      const question: QuizQuestion = {
        id: 'q1',
        question: 'What type of wisdom interests you most?',
        options: [
          {
            id: 'opt1',
            text: 'Spiritual teachings',
            domain_weights: { spiritual: 1.0, philosophical: 0.3 }
          },
          {
            id: 'opt2',
            text: 'Leadership principles',
            domain_weights: { leadership: 1.0, historical: 0.5 }
          }
        ]
      };

      expect(question.id).toBe('q1');
      expect(question.options).toHaveLength(2);
    });
  });

  describe('QuizOption', () => {
    it('should create valid option with weights', () => {
      const option: QuizOption = {
        id: 'opt1',
        text: 'Inner peace and mindfulness',
        domain_weights: {
          spiritual: 1.0,
          philosophical: 0.5,
          psychology: 0.3
        }
      };

      expect(option.domain_weights.spiritual).toBe(1.0);
      expect(Object.keys(option.domain_weights)).toHaveLength(3);
    });
  });

  describe('QuizResponse', () => {
    it('should create valid response', () => {
      const response: QuizResponse = {
        question_id: 'q1',
        selected_option_id: 'opt2'
      };

      expect(response.question_id).toBe('q1');
      expect(response.selected_option_id).toBe('opt2');
    });
  });

  describe('DomainScore', () => {
    it('should create valid domain score', () => {
      const score: DomainScore = {
        domain: 'spiritual',
        score: 0.85,
        label: 'Spiritual Wisdom'
      };

      expect(score.domain).toBe('spiritual');
      expect(score.score).toBe(0.85);
    });

    it('should handle multiple domain scores', () => {
      const scores: DomainScore[] = [
        { domain: 'spiritual', score: 0.9, label: 'Spiritual' },
        { domain: 'philosophical', score: 0.7, label: 'Philosophical' },
        { domain: 'leadership', score: 0.5, label: 'Leadership' }
      ];

      const sorted = scores.sort((a, b) => b.score - a.score);
      expect(sorted[0].domain).toBe('spiritual');
    });
  });

  describe('PersonalityMatch', () => {
    it('should create valid personality match', () => {
      const match: PersonalityMatch = {
        personality_id: 'krishna',
        name: 'Krishna',
        domain: 'spiritual',
        description: 'Divine teacher from Bhagavad Gita',
        match_score: 0.92,
        match_reason: 'Your interest in spiritual wisdom aligns with Krishna\'s teachings'
      };

      expect(match.personality_id).toBe('krishna');
      expect(match.match_score).toBe(0.92);
    });
  });

  describe('OnboardingState', () => {
    it('should create initial state', () => {
      const state: OnboardingState = {
        current_step: 'welcome',
        completed_steps: [],
        quiz_responses: [],
        recommended_personalities: [],
        started_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T10:00:00Z',
        is_complete: false,
        was_skipped: false
      };

      expect(state.current_step).toBe('welcome');
      expect(state.is_complete).toBe(false);
    });

    it('should create completed state', () => {
      const state: OnboardingState = {
        current_step: 'complete',
        completed_steps: ['welcome', 'quiz', 'first_chat', 'discovery', 'complete'],
        quiz_responses: [
          { question_id: 'q1', selected_option_id: 'opt1' },
          { question_id: 'q2', selected_option_id: 'opt3' }
        ],
        recommended_personalities: [
          {
            personality_id: 'buddha',
            name: 'Buddha',
            domain: 'spiritual',
            description: 'Enlightened teacher',
            match_score: 0.88,
            match_reason: 'Based on your quiz responses'
          }
        ],
        selected_personality: 'buddha',
        started_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T10:15:00Z',
        is_complete: true,
        was_skipped: false
      };

      expect(state.is_complete).toBe(true);
      expect(state.selected_personality).toBe('buddha');
    });

    it('should create skipped state', () => {
      const state: OnboardingState = {
        current_step: 'complete',
        completed_steps: ['welcome'],
        quiz_responses: [],
        recommended_personalities: [],
        started_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T10:01:00Z',
        is_complete: true,
        was_skipped: true
      };

      expect(state.was_skipped).toBe(true);
    });
  });

  describe('QuizResult', () => {
    it('should create valid quiz result', () => {
      const result: QuizResult = {
        domain_scores: [
          { domain: 'spiritual', score: 0.9, label: 'Spiritual' },
          { domain: 'philosophical', score: 0.6, label: 'Philosophical' }
        ],
        recommended_personality: {
          personality_id: 'krishna',
          name: 'Krishna',
          domain: 'spiritual',
          description: 'Divine teacher',
          match_score: 0.9,
          match_reason: 'Best match based on quiz'
        },
        alternative_matches: [
          {
            personality_id: 'buddha',
            name: 'Buddha',
            domain: 'spiritual',
            description: 'Enlightened one',
            match_score: 0.85,
            match_reason: 'Similar spiritual focus'
          }
        ],
        personality_reasoning: 'Your responses show a strong affinity for spiritual wisdom.'
      };

      expect(result.domain_scores).toHaveLength(2);
      expect(result.recommended_personality.personality_id).toBe('krishna');
      expect(result.alternative_matches).toHaveLength(1);
    });
  });
});
