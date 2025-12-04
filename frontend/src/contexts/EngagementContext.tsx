/**
 * Engagement Context Provider for Vimarsh
 * 
 * Manages engagement state (streaks, achievements) across the application.
 * Integrates with the engagement API and provides hooks for components.
 */

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { engagementApi } from '../components/engagement/engagementApi';
import { 
  trackStreakEvent, 
  trackAchievementEvent, 
  trackCheckInEvent, 
  trackLevelEvent 
} from '../utils/analytics';
import type { 
  StreakData, 
  AchievementsData, 
  Achievement, 
  EngagementDashboard,
  WeeklySummary 
} from '../components/engagement/types';

// Engagement context state
interface EngagementContextState {
  // Streak data
  streakData: StreakData | null;
  
  // Achievements data
  achievementsData: AchievementsData | null;
  
  // Dashboard summary
  dashboard: EngagementDashboard | null;
  
  // Weekly summary
  weeklySummary: WeeklySummary | null;
  
  // Loading states
  isLoading: boolean;
  isRecordingActivity: boolean;
  
  // Error state
  error: string | null;
  
  // Recently unlocked achievements (for showing notifications)
  recentUnlocks: Achievement[];
  
  // Flag to show achievement modal
  showAchievementModal: boolean;
  pendingAchievement: Achievement | null;
}

// Context type with actions
interface EngagementContextType extends EngagementContextState {
  // Load engagement data
  loadEngagementData: (userId: string) => Promise<void>;
  refreshStreakData: () => Promise<void>;
  refreshAchievements: () => Promise<void>;
  
  // Record activity (called after conversations)
  recordActivity: (
    activityType?: string,
    personalityId?: string,
    domain?: string,
    metadata?: Record<string, unknown>
  ) => Promise<{
    newlyUnlocked: Achievement[];
    milestoneReached: boolean;
    milestoneMessage?: string;
  }>;
  
  // Use streak freeze
  useStreakFreeze: () => Promise<boolean>;
  
  // Achievement modal management
  dismissAchievementModal: () => void;
  
  // Helper functions
  getStreakStatus: () => 'safe' | 'at-risk' | 'broken' | 'none';
  getAchievementProgress: (achievementId: string) => number;
}

const EngagementContext = createContext<EngagementContextType | undefined>(undefined);

interface EngagementProviderProps {
  children: ReactNode;
  userId?: string;
}

export const EngagementProvider: React.FC<EngagementProviderProps> = ({ 
  children,
  userId: propUserId 
}) => {
  // State
  const [userId, setUserId] = useState<string | null>(propUserId || null);
  const [streakData, setStreakData] = useState<StreakData | null>(null);
  const [achievementsData, setAchievementsData] = useState<AchievementsData | null>(null);
  const [dashboard, setDashboard] = useState<EngagementDashboard | null>(null);
  const [weeklySummary, setWeeklySummary] = useState<WeeklySummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecordingActivity, setIsRecordingActivity] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recentUnlocks, setRecentUnlocks] = useState<Achievement[]>([]);
  const [showAchievementModal, setShowAchievementModal] = useState(false);
  const [pendingAchievement, setPendingAchievement] = useState<Achievement | null>(null);

  // Update userId if prop changes
  useEffect(() => {
    if (propUserId && propUserId !== userId) {
      setUserId(propUserId);
    }
  }, [propUserId, userId]);

  // Load engagement data
  const loadEngagementData = useCallback(async (uid: string) => {
    if (!uid) return;
    
    setUserId(uid);
    setIsLoading(true);
    setError(null);
    
    try {
      // Load dashboard data (includes streaks, achievements summary, weekly activity)
      const dashboardData = await engagementApi.getDashboard(uid);
      setDashboard(dashboardData);
      
      // Extract streak data from dashboard
      if (dashboardData.streaks) {
        setStreakData({
          current_streak: dashboardData.streaks.current_streak,
          longest_streak: dashboardData.streaks.longest_streak,
          streak_freezes_available: dashboardData.streaks.streak_freezes_available,
          streak_freezes_used_this_week: 0, // Not in dashboard response
          last_active_date: dashboardData.streaks.last_active_date,
          streak_at_risk: dashboardData.streaks.streak_at_risk,
          activity_history: [] // Load separately if needed
        });
      }
      
      // Load full achievements data
      const achievements = await engagementApi.getAchievements(uid);
      setAchievementsData(achievements);
      
      // Set weekly summary
      if (dashboardData.weekly_activity) {
        setWeeklySummary(dashboardData.weekly_activity);
      }
      
    } catch (err) {
      console.error('Failed to load engagement data:', err);
      setError('Failed to load engagement data');
      
      // Try loading individual endpoints as fallback
      try {
        const [streaks, achievements] = await Promise.allSettled([
          engagementApi.getStreakData(uid),
          engagementApi.getAchievements(uid)
        ]);
        
        if (streaks.status === 'fulfilled') {
          setStreakData(streaks.value);
        }
        if (achievements.status === 'fulfilled') {
          setAchievementsData(achievements.value);
        }
      } catch (fallbackErr) {
        console.error('Fallback loading also failed:', fallbackErr);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Refresh streak data only
  const refreshStreakData = useCallback(async () => {
    if (!userId) return;
    
    try {
      const data = await engagementApi.getStreakData(userId);
      setStreakData(data);
    } catch (err) {
      console.error('Failed to refresh streak data:', err);
    }
  }, [userId]);

  // Refresh achievements only
  const refreshAchievements = useCallback(async () => {
    if (!userId) return;
    
    try {
      const data = await engagementApi.getAchievements(userId);
      setAchievementsData(data);
    } catch (err) {
      console.error('Failed to refresh achievements:', err);
    }
  }, [userId]);

  // Record activity
  const recordActivity = useCallback(async (
    activityType: string = 'conversation',
    personalityId?: string,
    domain?: string,
    metadata?: Record<string, unknown>
  ): Promise<{
    newlyUnlocked: Achievement[];
    milestoneReached: boolean;
    milestoneMessage?: string;
  }> => {
    if (!userId) {
      return { newlyUnlocked: [], milestoneReached: false };
    }
    
    setIsRecordingActivity(true);
    
    try {
      // Check if backend already provided achievements (from guidance endpoint)
      const backendAchievements = metadata?.backend_achievements as Achievement[] | undefined;
      
      // If backend provided achievements, use those directly (no duplicate API call needed)
      if (backendAchievements && backendAchievements.length > 0) {
        setRecentUnlocks(prev => [...prev, ...backendAchievements]);
        
        // Track achievement unlocks
        backendAchievements.forEach(achievement => {
          trackAchievementEvent('unlocked', {
            achievementId: achievement.id,
            achievementName: achievement.name,
            category: achievement.category,
            rarity: achievement.rarity,
            totalUnlocked: achievementsData?.total_unlocked
          });
        });
        
        // Show modal for first unlocked achievement
        const firstUnlock = backendAchievements[0];
        setPendingAchievement(firstUnlock);
        setShowAchievementModal(true);
        
        // Refresh full achievements data
        await refreshAchievements();
        
        // Also refresh streak data since backend updated it
        await refreshStreakData();
        
        return {
          newlyUnlocked: backendAchievements,
          milestoneReached: false,
          milestoneMessage: undefined
        };
      }
      
      // Otherwise, call the engagement API to record activity
      const result = await engagementApi.recordActivity(
        userId,
        activityType,
        personalityId,
        domain,
        metadata
      );
      
      // Update streak data
      if (result.streak_data) {
        setStreakData(result.streak_data);
      }
      
      // Handle newly unlocked achievements
      if (result.newly_unlocked_achievements?.length > 0) {
        setRecentUnlocks(prev => [...prev, ...result.newly_unlocked_achievements]);
        
        // Track achievement unlocks
        result.newly_unlocked_achievements.forEach((achievement: Achievement) => {
          trackAchievementEvent('unlocked', {
            achievementId: achievement.id,
            achievementName: achievement.name,
            category: achievement.category,
            rarity: achievement.rarity
          });
        });
        
        // Show modal for first unlocked achievement
        const firstUnlock = result.newly_unlocked_achievements[0];
        setPendingAchievement(firstUnlock);
        setShowAchievementModal(true);
        
        // Refresh full achievements data
        await refreshAchievements();
      }
      
      // Track streak milestone if reached
      if (result.milestone_reached && result.streak_data) {
        trackStreakEvent('milestone', {
          currentStreak: result.streak_data.current_streak,
          longestStreak: result.streak_data.longest_streak,
          milestone: result.streak_data.current_streak
        });
      }
      
      // Track check-in completion
      trackCheckInEvent('completed', {
        dayOfWeek: new Date().getDay(),
        consecutiveDays: result.streak_data?.current_streak,
        pointsEarned: 10 // Base points for activity
      });
      
      return {
        newlyUnlocked: result.newly_unlocked_achievements || [],
        milestoneReached: result.milestone_reached || false,
        milestoneMessage: result.milestone_message
      };
      
    } catch (err) {
      console.error('Failed to record activity:', err);
      return { newlyUnlocked: [], milestoneReached: false };
    } finally {
      setIsRecordingActivity(false);
    }
  }, [userId, refreshAchievements, refreshStreakData]);

  // Use streak freeze
  const useStreakFreeze = useCallback(async (): Promise<boolean> => {
    if (!userId) return false;
    
    try {
      const result = await engagementApi.useStreakFreeze(userId);
      
      if (result.success) {
        // Track streak restored via freeze
        trackStreakEvent('restored', {
          currentStreak: streakData?.current_streak,
          longestStreak: streakData?.longest_streak
        });
        
        // Refresh streak data to get updated freeze count
        await refreshStreakData();
        return true;
      }
      
      return false;
    } catch (err) {
      console.error('Failed to use streak freeze:', err);
      return false;
    }
  }, [userId, refreshStreakData, streakData]);

  // Dismiss achievement modal
  const dismissAchievementModal = useCallback(() => {
    setShowAchievementModal(false);
    
    // Check if there are more achievements to show
    const remaining = recentUnlocks.filter(a => a.id !== pendingAchievement?.id);
    setRecentUnlocks(remaining);
    
    if (remaining.length > 0) {
      // Show next achievement after a short delay
      setTimeout(() => {
        setPendingAchievement(remaining[0]);
        setShowAchievementModal(true);
      }, 300);
    } else {
      setPendingAchievement(null);
    }
  }, [recentUnlocks, pendingAchievement]);

  // Get streak status helper
  const getStreakStatus = useCallback((): 'safe' | 'at-risk' | 'broken' | 'none' => {
    if (!streakData) return 'none';
    
    if (streakData.current_streak === 0) {
      return streakData.longest_streak > 0 ? 'broken' : 'none';
    }
    
    return streakData.streak_at_risk ? 'at-risk' : 'safe';
  }, [streakData]);

  // Get achievement progress helper
  const getAchievementProgress = useCallback((achievementId: string): number => {
    if (!achievementsData) return 0;
    
    const achievement = achievementsData.achievements.find(a => a.id === achievementId);
    return achievement?.progress.percentage || 0;
  }, [achievementsData]);

  // Auto-load data when userId changes
  useEffect(() => {
    if (userId) {
      loadEngagementData(userId);
    }
  }, [userId, loadEngagementData]);

  const contextValue: EngagementContextType = {
    // State
    streakData,
    achievementsData,
    dashboard,
    weeklySummary,
    isLoading,
    isRecordingActivity,
    error,
    recentUnlocks,
    showAchievementModal,
    pendingAchievement,
    
    // Actions
    loadEngagementData,
    refreshStreakData,
    refreshAchievements,
    recordActivity,
    useStreakFreeze,
    dismissAchievementModal,
    getStreakStatus,
    getAchievementProgress
  };

  return (
    <EngagementContext.Provider value={contextValue}>
      {children}
    </EngagementContext.Provider>
  );
};

// Custom hook for using engagement context
export const useEngagement = (): EngagementContextType => {
  const context = useContext(EngagementContext);
  if (!context) {
    throw new Error('useEngagement must be used within an EngagementProvider');
  }
  return context;
};

// Export context for testing
export { EngagementContext };
