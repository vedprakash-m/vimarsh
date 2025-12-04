/**
 * Engagement Types Tests
 */

import {
  StreakData,
  DailyActivity,
  Achievement,
  AchievementCategory,
  AchievementTier,
  AchievementSummary,
  EngagementScore
} from '../types';

describe('Engagement Types', () => {
  describe('StreakData', () => {
    it('should create valid streak data', () => {
      const streakData: StreakData = {
        current_streak: 7,
        longest_streak: 14,
        streak_freezes_available: 3,
        streak_freezes_used_this_week: 1,
        last_active_date: '2024-01-15',
        streak_at_risk: false,
        activity_history: []
      };

      expect(streakData.current_streak).toBe(7);
      expect(streakData.longest_streak).toBe(14);
      expect(streakData.streak_freezes_available).toBe(3);
      expect(streakData.streak_at_risk).toBe(false);
    });

    it('should handle null last_active_date', () => {
      const streakData: StreakData = {
        current_streak: 0,
        longest_streak: 0,
        streak_freezes_available: 3,
        streak_freezes_used_this_week: 0,
        last_active_date: null,
        streak_at_risk: false,
        activity_history: []
      };

      expect(streakData.last_active_date).toBeNull();
    });
  });

  describe('DailyActivity', () => {
    it('should create valid daily activity', () => {
      const activity: DailyActivity = {
        date: '2024-01-15',
        has_activity: true,
        conversations: 5,
        personalities_interacted: ['krishna', 'buddha'],
        domains_explored: ['spiritual', 'philosophical'],
        was_frozen: false
      };

      expect(activity.date).toBe('2024-01-15');
      expect(activity.has_activity).toBe(true);
      expect(activity.conversations).toBe(5);
      expect(activity.personalities_interacted).toHaveLength(2);
    });

    it('should handle inactive day', () => {
      const activity: DailyActivity = {
        date: '2024-01-16',
        has_activity: false,
        conversations: 0,
        personalities_interacted: [],
        domains_explored: [],
        was_frozen: true
      };

      expect(activity.has_activity).toBe(false);
      expect(activity.was_frozen).toBe(true);
    });
  });

  describe('Achievement', () => {
    it('should create valid unlocked achievement', () => {
      const achievement: Achievement = {
        id: 'first_steps',
        name: 'First Steps',
        description: 'Complete your first conversation',
        icon: '💬',
        points: 10,
        category: 'onboarding',
        tier: 'bronze',
        unlocked: true,
        unlocked_at: '2024-01-15T10:00:00Z',
        progress: {
          current: 1,
          target: 1,
          percentage: 100
        }
      };

      expect(achievement.unlocked).toBe(true);
      expect(achievement.progress.percentage).toBe(100);
    });

    it('should create valid locked achievement with progress', () => {
      const achievement: Achievement = {
        id: 'streak_master',
        name: 'Streak Master',
        description: 'Maintain a 30-day streak',
        icon: '🔥',
        points: 100,
        category: 'streak',
        tier: 'gold',
        unlocked: false,
        unlocked_at: null,
        progress: {
          current: 15,
          target: 30,
          percentage: 50
        }
      };

      expect(achievement.unlocked).toBe(false);
      expect(achievement.unlocked_at).toBeNull();
      expect(achievement.progress.current).toBe(15);
    });
  });

  describe('AchievementCategory', () => {
    it('should accept all valid categories', () => {
      const categories: AchievementCategory[] = [
        'onboarding',
        'conversation',
        'exploration',
        'streak',
        'mastery',
        'special'
      ];

      expect(categories).toHaveLength(6);
      categories.forEach(cat => {
        expect(typeof cat).toBe('string');
      });
    });
  });

  describe('AchievementTier', () => {
    it('should accept all valid tiers', () => {
      const tiers: AchievementTier[] = [
        'bronze',
        'silver',
        'gold',
        'platinum'
      ];

      expect(tiers).toHaveLength(4);
    });
  });

  describe('AchievementSummary', () => {
    it('should create valid summary', () => {
      const summary: AchievementSummary = {
        total: 50,
        unlocked: 15,
        total_points: 350,
        level: 5,
        level_progress: 75
      };

      expect(summary.total).toBe(50);
      expect(summary.unlocked).toBe(15);
      expect(summary.level).toBe(5);
    });
  });

  describe('EngagementScore', () => {
    it('should create beginner tier score', () => {
      const score: EngagementScore = {
        score: 50,
        tier: 'beginner',
        tier_label: 'Beginner',
        streak_contribution: 20,
        achievement_contribution: 30
      };

      expect(score.tier).toBe('beginner');
    });

    it('should create master tier score', () => {
      const score: EngagementScore = {
        score: 850,
        tier: 'master',
        tier_label: 'Master',
        streak_contribution: 400,
        achievement_contribution: 450
      };

      expect(score.tier).toBe('master');
    });

    it('should create legendary tier score', () => {
      const score: EngagementScore = {
        score: 1200,
        tier: 'legendary',
        tier_label: 'Legendary',
        streak_contribution: 600,
        achievement_contribution: 600
      };

      expect(score.tier).toBe('legendary');
    });
  });
});
