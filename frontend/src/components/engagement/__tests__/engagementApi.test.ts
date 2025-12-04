/**
 * Engagement API Tests
 */

// Mock axios before importing
jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn()
}));

import axios from 'axios';
import { engagementApi } from '../engagementApi';

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('engagementApi', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getStreakData', () => {
    it('should fetch streak data successfully', async () => {
      const mockStreakData = {
        current_streak: 7,
        longest_streak: 14,
        streak_freezes_available: 3,
        streak_freezes_used_this_week: 0,
        last_active_date: '2024-01-15',
        streak_at_risk: false,
        activity_history: []
      };

      mockedAxios.get.mockResolvedValueOnce({
        data: { data: mockStreakData }
      });

      const result = await engagementApi.getStreakData('user123');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/engagement/streaks'),
        { params: { user_id: 'user123' } }
      );
      expect(result).toEqual(mockStreakData);
    });

    it('should throw error on failure', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

      await expect(engagementApi.getStreakData('user123')).rejects.toThrow('Network error');
    });
  });

  describe('recordActivity', () => {
    it('should record activity successfully', async () => {
      const mockResponse = {
        streak_data: {
          current_streak: 8,
          longest_streak: 14,
          streak_freezes_available: 3,
          streak_freezes_used_this_week: 0,
          last_active_date: '2024-01-16',
          streak_at_risk: false,
          activity_history: []
        },
        newly_unlocked_achievements: [],
        milestone_reached: false
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: { result: mockResponse }
      });

      const result = await engagementApi.recordActivity(
        'user123',
        'conversation',
        'krishna',
        'spiritual'
      );

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/engagement/activity'),
        {
          user_id: 'user123',
          activity_type: 'conversation',
          personality_id: 'krishna',
          domain: 'spiritual',
          metadata: undefined
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should record activity with metadata', async () => {
      const mockResponse = {
        streak_data: {
          current_streak: 5,
          longest_streak: 10,
          streak_freezes_available: 2,
          streak_freezes_used_this_week: 1,
          last_active_date: '2024-01-16',
          streak_at_risk: false,
          activity_history: []
        },
        newly_unlocked_achievements: [],
        milestone_reached: false
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: { result: mockResponse }
      });

      const metadata = { conversation_id: 'conv123', duration: 300 };
      await engagementApi.recordActivity('user123', 'conversation', 'buddha', 'spiritual', metadata);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/engagement/activity'),
        expect.objectContaining({ metadata })
      );
    });

    it('should throw error on failure', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Server error'));

      await expect(
        engagementApi.recordActivity('user123', 'conversation')
      ).rejects.toThrow('Server error');
    });
  });

  describe('useStreakFreeze', () => {
    it('should use streak freeze successfully', async () => {
      const mockResponse = {
        success: true,
        message: 'Streak freeze applied',
        freezes_remaining: 2
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: { result: mockResponse }
      });

      const result = await engagementApi.useStreakFreeze('user123');

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/engagement/streaks/freeze'),
        { user_id: 'user123' }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw error when no freezes available', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('No freezes available'));

      await expect(engagementApi.useStreakFreeze('user123')).rejects.toThrow('No freezes available');
    });
  });

  describe('getWeeklySummary', () => {
    it('should fetch weekly summary successfully', async () => {
      const mockSummary = {
        active_days: 5,
        total_conversations: 12,
        unique_personalities: 4,
        domains_covered: 3,
        top_personality: 'krishna',
        top_domain: 'spiritual',
        streak_milestone_reached: false
      };

      mockedAxios.get.mockResolvedValueOnce({
        data: { summary: mockSummary }
      });

      const result = await engagementApi.getWeeklySummary('user123');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/engagement/summary'),
        { params: { user_id: 'user123' } }
      );
      expect(result).toEqual(mockSummary);
    });

    it('should throw error on failure', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Fetch failed'));

      await expect(engagementApi.getWeeklySummary('user123')).rejects.toThrow('Fetch failed');
    });
  });

  describe('getAchievements', () => {
    it('should fetch achievements successfully', async () => {
      const mockAchievements = {
        achievements: [
          {
            id: 'first_steps',
            name: 'First Steps',
            description: 'Start your journey',
            icon: '👣',
            points: 10,
            category: 'onboarding',
            tier: 'bronze',
            unlocked: true,
            unlocked_at: '2024-01-15',
            progress: { current: 1, target: 1, percentage: 100 }
          }
        ],
        summary: {
          total: 50,
          unlocked: 5,
          total_points: 100,
          level: 2,
          level_progress: 40
        },
        recent_unlocks: []
      };

      mockedAxios.get.mockResolvedValueOnce({
        data: { data: mockAchievements }
      });

      const result = await engagementApi.getAchievements('user123');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/engagement/achievements'),
        { params: { user_id: 'user123' } }
      );
      expect(result).toEqual(mockAchievements);
    });

    it('should throw error on failure', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('API error'));

      await expect(engagementApi.getAchievements('user123')).rejects.toThrow('API error');
    });
  });

  describe('checkAchievements', () => {
    it('should check and return newly unlocked achievements', async () => {
      const mockNewAchievements = [
        {
          id: 'streak_week',
          name: 'Week Warrior',
          description: '7 day streak',
          icon: '🔥',
          points: 50,
          category: 'streak',
          tier: 'silver',
          unlocked: true,
          unlocked_at: '2024-01-22',
          progress: { current: 7, target: 7, percentage: 100 }
        }
      ];

      mockedAxios.post.mockResolvedValueOnce({
        data: { newly_unlocked: mockNewAchievements }
      });

      const metrics = { current_streak: 7, conversations: 20 };
      const result = await engagementApi.checkAchievements('user123', metrics);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/engagement/achievements/check'),
        expect.objectContaining({
          user_id: 'user123',
          metrics
        })
      );
      expect(result).toEqual(mockNewAchievements);
    });
  });

  describe('getDashboard', () => {
    it('should fetch full engagement dashboard', async () => {
      const mockDashboard = {
        streaks: {
          current_streak: 7,
          longest_streak: 14,
          streak_freezes_available: 3
        },
        achievements: {
          unlocked_count: 10,
          total_points: 250,
          level: 3
        },
        score: {
          score: 500,
          tier: 'dedicated',
          tier_label: 'Dedicated Seeker'
        }
      };

      mockedAxios.get.mockResolvedValueOnce({
        data: { dashboard: mockDashboard }
      });

      const result = await engagementApi.getDashboard('user123');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/engagement/dashboard'),
        { params: { user_id: 'user123' } }
      );
      expect(result).toEqual(mockDashboard);
    });
  });
});
