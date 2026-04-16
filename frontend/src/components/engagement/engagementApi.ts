/**
 * Engagement API Service for Vimarsh
 * Handles all API calls related to streaks and achievements.
 * Uses the authenticated SpiritualGuidanceAPI singleton for consistent
 * auth token injection, retry logic, and error handling.
 */

import spiritualGuidanceAPI from '../../utils/api';
import { 
  StreakData, 
  AchievementsData, 
  EngagementDashboard, 
  WeeklySummary,
  Achievement
} from './types';

// Access the authenticated axios client from the API singleton.
// This ensures all engagement calls include the Bearer token via interceptor.
const getClient = () => (spiritualGuidanceAPI as any).client;

export const engagementApi = {
  /**
   * Get streak data for a user
   */
  async getStreakData(userId: string): Promise<StreakData> {
    try {
      const response = await getClient().get('/engagement/streaks', {
        params: { user_id: userId }
      });
      return response.data.data;
    } catch (error) {
      console.error('Failed to fetch streak data:', error);
      throw error;
    }
  },

  /**
   * Record user activity for streak tracking
   */
  async recordActivity(
    userId: string,
    activityType: string = 'conversation',
    personalityId?: string,
    domain?: string,
    metadata?: Record<string, unknown>
  ): Promise<{
    streak_data: StreakData;
    newly_unlocked_achievements: Achievement[];
    milestone_reached: boolean;
    milestone_message?: string;
  }> {
    try {
      const response = await getClient().post('/engagement/activity', {
        user_id: userId,
        activity_type: activityType,
        personality_id: personalityId,
        domain,
        metadata
      });
      return response.data.result;
    } catch (error) {
      console.error('Failed to record activity:', error);
      throw error;
    }
  },

  /**
   * Headless tracking that acts silently as an un-awaited background process.
   * Guarantees zero UI modaling or error boundary breaks if it fails.
   */
  async recordActivityHeadless(
    userId: string,
    activityType: string = 'conversation',
    personalityId?: string,
    domain?: string,
    metadata?: Record<string, unknown>
  ): Promise<void> {
    try {
      await getClient().post('/engagement/activity', {
        user_id: userId,
        activity_type: activityType,
        personality_id: personalityId,
        domain,
        metadata
      });
    } catch (error) {
      // Intentionally swallowed for UI continuity
      console.warn('Headless analytics tracking dynamically failed. Ignoring error.');
    }
  },

  /**
   * Use a streak freeze
   */
  async useStreakFreeze(userId: string): Promise<{
    success: boolean;
    message: string;
    freezes_remaining: number;
  }> {
    try {
      const response = await getClient().post('/engagement/streaks/freeze', {
        user_id: userId
      });
      return response.data.result;
    } catch (error) {
      console.error('Failed to use streak freeze:', error);
      throw error;
    }
  },

  /**
   * Get weekly engagement summary
   */
  async getWeeklySummary(userId: string): Promise<WeeklySummary> {
    try {
      const response = await getClient().get('/engagement/summary', {
        params: { user_id: userId }
      });
      return response.data.summary;
    } catch (error) {
      console.error('Failed to fetch weekly summary:', error);
      throw error;
    }
  },

  /**
   * Get all achievements with user progress
   */
  async getAchievements(userId: string): Promise<AchievementsData> {
    try {
      const response = await getClient().get('/engagement/achievements', {
        params: { user_id: userId }
      });
      return response.data.data;
    } catch (error) {
      console.error('Failed to fetch achievements:', error);
      throw error;
    }
  },

  /**
   * Check for new achievements based on metrics
   */
  async checkAchievements(
    userId: string,
    metrics: Record<string, unknown>
  ): Promise<Achievement[]> {
    try {
      const response = await getClient().post('/engagement/achievements/check', {
        user_id: userId,
        metrics
      });
      return response.data.newly_unlocked;
    } catch (error) {
      console.error('Failed to check achievements:', error);
      throw error;
    }
  },

  /**
   * Get combined engagement dashboard data
   */
  async getDashboard(userId: string): Promise<EngagementDashboard> {
    try {
      const response = await getClient().get('/engagement/dashboard', {
        params: { user_id: userId }
      });
      return response.data.dashboard;
    } catch (error) {
      console.error('Failed to fetch engagement dashboard:', error);
      throw error;
    }
  }
};

export default engagementApi;
