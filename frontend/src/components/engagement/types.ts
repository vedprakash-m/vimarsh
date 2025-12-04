/**
 * Engagement Types for Vimarsh
 * Type definitions for streaks, achievements, and gamification
 */

export interface StreakData {
  current_streak: number;
  longest_streak: number;
  streak_freezes_available: number;
  streak_freezes_used_this_week: number;
  last_active_date: string | null;
  streak_at_risk: boolean;
  activity_history: DailyActivity[];
}

export interface DailyActivity {
  date: string;
  has_activity: boolean;
  conversations: number;
  personalities_interacted: string[];
  domains_explored: string[];
  was_frozen: boolean;
}

export interface WeeklySummary {
  active_days: number;
  total_conversations: number;
  unique_personalities: number;
  domains_covered: number;
  top_personality: string | null;
  top_domain: string | null;
  streak_milestone_reached: boolean;
  milestone_value?: number;
}

export type AchievementCategory = 
  | 'onboarding'
  | 'conversation'
  | 'exploration'
  | 'streak'
  | 'mastery'
  | 'special';

export type AchievementTier = 
  | 'bronze'
  | 'silver'
  | 'gold'
  | 'platinum';

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  points: number;
  category: AchievementCategory;
  tier: AchievementTier;
  unlocked: boolean;
  unlocked_at: string | null;
  progress: {
    current: number;
    target: number | null;
    percentage: number;
  };
}

export interface AchievementSummary {
  total: number;
  unlocked: number;
  total_points: number;
  level: number;
  level_progress: number;
}

export interface RecentUnlock {
  id: string;
  name: string;
  icon: string;
  unlocked_at: string;
}

export interface AchievementsData {
  achievements: Achievement[];
  summary: AchievementSummary;
  recent_unlocks: RecentUnlock[];
}

export interface EngagementScore {
  score: number;
  tier: 'beginner' | 'active' | 'dedicated' | 'master' | 'legendary';
  tier_label: string;
  streak_contribution: number;
  achievement_contribution: number;
}

export interface EngagementDashboard {
  streaks: {
    current_streak: number;
    longest_streak: number;
    streak_freezes_available: number;
    last_active_date: string | null;
    streak_at_risk: boolean;
  };
  achievements: {
    total: number;
    unlocked: number;
    total_points: number;
    level: number;
    level_progress: number;
    recent_unlocks: RecentUnlock[];
  };
  weekly_activity: WeeklySummary;
  engagement_score: EngagementScore;
}
