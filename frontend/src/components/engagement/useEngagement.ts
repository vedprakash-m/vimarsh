/**
 * useEngagement Hook
 * Manages engagement state including streaks and achievements
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  StreakData, 
  AchievementsData, 
  EngagementDashboard,
  Achievement,
  WeeklySummary
} from './types';
import { engagementApi } from './engagementApi';

interface UseEngagementResult {
  // State
  streakData: StreakData | null;
  achievements: AchievementsData | null;
  dashboard: EngagementDashboard | null;
  weeklySummary: WeeklySummary | null;
  recentlyUnlocked: Achievement[];
  isLoading: boolean;
  error: string | null;

  // Actions
  loadStreakData: () => Promise<void>;
  loadAchievements: () => Promise<void>;
  loadDashboard: () => Promise<void>;
  recordActivity: (
    activityType?: string,
    personalityId?: string,
    domain?: string,
    metadata?: Record<string, unknown>
  ) => Promise<Achievement[]>;
  useStreakFreeze: () => Promise<boolean>;
  clearRecentlyUnlocked: () => void;
}

export function useEngagement(userId: string): UseEngagementResult {
  const [streakData, setStreakData] = useState<StreakData | null>(null);
  const [achievements, setAchievements] = useState<AchievementsData | null>(null);
  const [dashboard, setDashboard] = useState<EngagementDashboard | null>(null);
  const [weeklySummary, setWeeklySummary] = useState<WeeklySummary | null>(null);
  const [recentlyUnlocked, setRecentlyUnlocked] = useState<Achievement[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load streak data
  const loadStreakData = useCallback(async () => {
    if (!userId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const data = await engagementApi.getStreakData(userId);
      setStreakData(data);
    } catch (err) {
      console.error('Failed to load streak data:', err);
      setError('Failed to load streak information.');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Load achievements
  const loadAchievements = useCallback(async () => {
    if (!userId) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await engagementApi.getAchievements(userId);
      setAchievements(data);
    } catch (err) {
      console.error('Failed to load achievements:', err);
      setError('Failed to load achievements.');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Load full dashboard
  const loadDashboard = useCallback(async () => {
    if (!userId) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await engagementApi.getDashboard(userId);
      setDashboard(data);
      // Also update individual states from dashboard
      setWeeklySummary(data.weekly_activity);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
      setError('Failed to load engagement dashboard.');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Record activity and get newly unlocked achievements
  const recordActivity = useCallback(async (
    activityType: string = 'conversation',
    personalityId?: string,
    domain?: string,
    metadata?: Record<string, unknown>
  ): Promise<Achievement[]> => {
    if (!userId) return [];

    try {
      const result = await engagementApi.recordActivity(
        userId,
        activityType,
        personalityId,
        domain,
        metadata
      );

      // Update streak data
      setStreakData(result.streak_data);

      // Handle newly unlocked achievements
      if (result.newly_unlocked_achievements?.length > 0) {
        setRecentlyUnlocked(prev => [...result.newly_unlocked_achievements, ...prev]);
        // Refresh achievements to get updated state
        await loadAchievements();
      }

      return result.newly_unlocked_achievements || [];
    } catch (err) {
      console.error('Failed to record activity:', err);
      return [];
    }
  }, [userId, loadAchievements]);

  // Use streak freeze
  const useStreakFreeze = useCallback(async (): Promise<boolean> => {
    if (!userId) return false;

    try {
      const result = await engagementApi.useStreakFreeze(userId);
      if (result.success) {
        // Refresh streak data
        await loadStreakData();
      }
      return result.success;
    } catch (err) {
      console.error('Failed to use streak freeze:', err);
      return false;
    }
  }, [userId, loadStreakData]);

  // Clear recently unlocked achievements (after showing celebration)
  const clearRecentlyUnlocked = useCallback(() => {
    setRecentlyUnlocked([]);
  }, []);

  // Initial load
  useEffect(() => {
    if (userId) {
      loadDashboard();
    }
  }, [userId, loadDashboard]);

  return {
    streakData,
    achievements,
    dashboard,
    weeklySummary,
    recentlyUnlocked,
    isLoading,
    error,
    loadStreakData,
    loadAchievements,
    loadDashboard,
    recordActivity,
    useStreakFreeze,
    clearRecentlyUnlocked
  };
}

export default useEngagement;
