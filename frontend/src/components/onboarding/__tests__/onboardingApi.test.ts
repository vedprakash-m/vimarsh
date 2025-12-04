/**
 * Onboarding API Tests
 */

// Mock axios before importing
jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn()
}));

import axios from 'axios';
import { onboardingApi } from '../onboardingApi';

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('onboardingApi', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getQuizQuestions', () => {
    it('should fetch quiz questions successfully', async () => {
      const mockQuestions = [
        {
          id: 'q1',
          question: 'What draws you to seek wisdom?',
          options: [
            { id: 'q1_a', text: 'Inner peace', domain_weights: { spiritual: 1.0 } },
            { id: 'q1_b', text: 'Leadership skills', domain_weights: { leadership: 1.0 } }
          ]
        },
        {
          id: 'q2',
          question: 'How do you prefer to learn?',
          options: [
            { id: 'q2_a', text: 'Stories and parables', domain_weights: { spiritual: 0.8 } },
            { id: 'q2_b', text: 'Logical reasoning', domain_weights: { philosophical: 1.0 } }
          ]
        }
      ];

      mockedAxios.get.mockResolvedValueOnce({
        data: { questions: mockQuestions }
      });

      const result = await onboardingApi.getQuizQuestions();

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/quiz/questions')
      );
      expect(result).toHaveLength(2);
      expect(result[0].id).toBe('q1');
    });

    it('should throw error on failure', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

      await expect(onboardingApi.getQuizQuestions()).rejects.toThrow('Network error');
    });
  });

  describe('processQuizResponses', () => {
    it('should process responses and return quiz result', async () => {
      const mockResponses = [
        { question_id: 'q1', selected_option_id: 'q1_a' },
        { question_id: 'q2', selected_option_id: 'q2_a' }
      ];

      const mockResult = {
        domain_scores: [
          { domain: 'spiritual', score: 0.9, label: 'Spiritual' }
        ],
        recommended_personality: {
          personality_id: 'krishna',
          name: 'Krishna',
          domain: 'spiritual',
          description: 'Divine teacher',
          match_score: 0.92,
          match_reason: 'Best match'
        },
        alternative_matches: [],
        personality_reasoning: 'Your responses indicate spiritual interest'
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: { result: mockResult }
      });

      const result = await onboardingApi.processQuizResponses(mockResponses);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/quiz/process'),
        { responses: mockResponses }
      );
      expect(result.recommended_personality.personality_id).toBe('krishna');
    });

    it('should throw error on failure', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Processing failed'));

      await expect(onboardingApi.processQuizResponses([])).rejects.toThrow('Processing failed');
    });
  });

  describe('getOnboardingState', () => {
    it('should fetch onboarding state successfully', async () => {
      const mockState = {
        current_step: 'quiz',
        completed_steps: ['welcome'],
        quiz_responses: [],
        recommended_personalities: [],
        started_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T10:05:00Z',
        is_complete: false,
        was_skipped: false
      };

      mockedAxios.get.mockResolvedValueOnce({
        data: { state: mockState }
      });

      const result = await onboardingApi.getOnboardingState('user123');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/state'),
        { params: { user_id: 'user123' } }
      );
      expect(result.current_step).toBe('quiz');
    });

    it('should throw error on failure', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('User not found'));

      await expect(onboardingApi.getOnboardingState('unknown')).rejects.toThrow('User not found');
    });
  });

  describe('advanceStep', () => {
    it('should advance to next step successfully', async () => {
      const mockState = {
        current_step: 'first_chat',
        completed_steps: ['welcome', 'quiz'],
        quiz_responses: [{ question_id: 'q1', selected_option_id: 'q1_a' }],
        recommended_personalities: [],
        started_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T10:10:00Z',
        is_complete: false,
        was_skipped: false
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: { state: mockState }
      });

      const result = await onboardingApi.advanceStep('user123');

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/state/advance'),
        { user_id: 'user123' }
      );
      expect(result.current_step).toBe('first_chat');
    });

    it('should throw error on failure', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Cannot advance'));

      await expect(onboardingApi.advanceStep('user123')).rejects.toThrow('Cannot advance');
    });
  });

  describe('recordQuizResponse', () => {
    it('should record quiz response successfully', async () => {
      const mockState = {
        current_step: 'quiz',
        completed_steps: ['welcome'],
        quiz_responses: [{ question_id: 'q1', selected_option_id: 'q1_a' }],
        recommended_personalities: [],
        started_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T10:06:00Z',
        is_complete: false,
        was_skipped: false
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: { state: mockState }
      });

      const result = await onboardingApi.recordQuizResponse('user123', 'q1', 'q1_a');

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/quiz/response'),
        {
          user_id: 'user123',
          question_id: 'q1',
          selected_option_id: 'q1_a'
        }
      );
      expect(result.quiz_responses).toHaveLength(1);
    });

    it('should throw error on failure', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Invalid question'));

      await expect(
        onboardingApi.recordQuizResponse('user123', 'invalid', 'opt')
      ).rejects.toThrow('Invalid question');
    });
  });

  describe('completeOnboarding', () => {
    it('should complete onboarding successfully', async () => {
      const mockState = {
        current_step: 'complete',
        completed_steps: ['welcome', 'quiz', 'first_chat', 'discovery', 'complete'],
        quiz_responses: [
          { question_id: 'q1', selected_option_id: 'q1_a' },
          { question_id: 'q2', selected_option_id: 'q2_b' }
        ],
        recommended_personalities: [],
        selected_personality: 'krishna',
        started_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T10:20:00Z',
        is_complete: true,
        was_skipped: false
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: { state: mockState }
      });

      const result = await onboardingApi.completeOnboarding('user123');

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/complete'),
        { user_id: 'user123' }
      );
      expect(result.is_complete).toBe(true);
    });

    it('should throw error on failure', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Completion failed'));

      await expect(onboardingApi.completeOnboarding('user123')).rejects.toThrow('Completion failed');
    });
  });

  describe('skipOnboarding', () => {
    it('should skip onboarding successfully', async () => {
      const mockState = {
        current_step: 'complete',
        completed_steps: ['welcome'],
        quiz_responses: [],
        recommended_personalities: [],
        started_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T10:01:00Z',
        is_complete: true,
        was_skipped: true
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: { state: mockState }
      });

      const result = await onboardingApi.skipOnboarding('user123');

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/skip'),
        { user_id: 'user123' }
      );
      expect(result.was_skipped).toBe(true);
      expect(result.is_complete).toBe(true);
    });

    it('should throw error on failure', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Skip failed'));

      await expect(onboardingApi.skipOnboarding('user123')).rejects.toThrow('Skip failed');
    });
  });
});
