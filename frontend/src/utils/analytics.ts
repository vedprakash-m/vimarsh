// Analytics utilities for Vimarsh application

export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
}

export const trackEvent = (event: AnalyticsEvent): void => {
  // In development mode, just log to console
  if (process.env.NODE_ENV === 'development') {
    console.log('📊 Analytics:', event);
    return;
  }
  
  // TODO: Implement Application Insights tracking for production
  // Example: appInsights.trackEvent(event.name, event.properties);
};

export const trackPageView = (pageName: string): void => {
  if (process.env.NODE_ENV === 'development') {
    console.log('📄 Page View:', pageName);
    return;
  }
  
  // TODO: Implement Application Insights page tracking for production
  // Example: appInsights.trackPageView({ name: pageName });
};

export const trackUserAction = (action: string, context?: Record<string, any>): void => {
  trackEvent({
    name: 'user_action',
    properties: {
      action,
      ...context,
      timestamp: new Date().toISOString()
    }
  });
};

// ============================================
// Engagement Analytics
// ============================================

export const trackStreakEvent = (
  action: 'view' | 'milestone' | 'broken' | 'restored',
  streakData: {
    currentStreak?: number;
    longestStreak?: number;
    milestone?: number;
  }
): void => {
  trackEvent({
    name: 'engagement_streak',
    properties: {
      action,
      ...streakData,
      timestamp: new Date().toISOString()
    }
  });
};

export const trackAchievementEvent = (
  action: 'unlocked' | 'viewed' | 'shared' | 'progress',
  achievementData: {
    achievementId?: string;
    achievementName?: string;
    category?: string;
    rarity?: string;
    progress?: number;
    totalUnlocked?: number;
  }
): void => {
  trackEvent({
    name: 'engagement_achievement',
    properties: {
      action,
      ...achievementData,
      timestamp: new Date().toISOString()
    }
  });
};

export const trackCheckInEvent = (
  action: 'completed' | 'skipped' | 'reminder_shown',
  checkInData: {
    dayOfWeek?: number;
    consecutiveDays?: number;
    pointsEarned?: number;
  }
): void => {
  trackEvent({
    name: 'engagement_checkin',
    properties: {
      action,
      ...checkInData,
      timestamp: new Date().toISOString()
    }
  });
};

export const trackGoalEvent = (
  action: 'set' | 'updated' | 'achieved' | 'progress',
  goalData: {
    goalType?: string;
    targetValue?: number;
    currentValue?: number;
    percentComplete?: number;
  }
): void => {
  trackEvent({
    name: 'engagement_goal',
    properties: {
      action,
      ...goalData,
      timestamp: new Date().toISOString()
    }
  });
};

export const trackLevelEvent = (
  action: 'level_up' | 'points_earned',
  levelData: {
    newLevel?: number;
    previousLevel?: number;
    totalPoints?: number;
    pointsEarned?: number;
    source?: string;
  }
): void => {
  trackEvent({
    name: 'engagement_level',
    properties: {
      action,
      ...levelData,
      timestamp: new Date().toISOString()
    }
  });
};

export const trackDashboardEvent = (
  action: 'viewed' | 'tab_changed' | 'time_filter_changed',
  dashboardData?: {
    activeTab?: string;
    timeFilter?: string;
    sessionDuration?: number;
  }
): void => {
  trackEvent({
    name: 'engagement_dashboard',
    properties: {
      action,
      ...dashboardData,
      timestamp: new Date().toISOString()
    }
  });
};

// Export empty object to make this a module
export {};