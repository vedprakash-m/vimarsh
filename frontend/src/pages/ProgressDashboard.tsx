/**
 * Progress Dashboard Page
 * 
 * Full-page view of user's engagement progress including:
 * - Streak tracking with weekly view
 * - Achievement badges and unlocks
 * - Level progression
 * - Activity statistics
 * 
 * Part of Priority 2: Build Habit Loops engagement system
 */

import React, { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Flame, Trophy, Target, TrendingUp, Calendar, Award, RefreshCw } from 'lucide-react';
import {
  StreakDisplay,
  StreakWeekView,
  AchievementsPanel,
  AchievementUnlockModal
} from '../components/engagement';
import { useEngagement } from '../contexts/EngagementContext';
import type { 
  Achievement
} from '../components/engagement/types';
import { useAuth } from '../auth/AuthProvider';

const ProgressDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { account } = useAuth();
  const userId = account?.username || account?.localAccountId || 'anonymous';

  // Use engagement context
  const {
    streakData,
    achievementsData,
    dashboard: dashboardData,
    isLoading: loading,
    error,
    loadEngagementData,
    showAchievementModal,
    pendingAchievement,
    dismissAchievementModal
  } = useEngagement();

  // Load data on mount if not already loaded
  useEffect(() => {
    if (userId && !streakData) {
      loadEngagementData(userId);
    }
  }, [userId, streakData, loadEngagementData]);

  // Handler for refresh button
  const handleRefresh = useCallback(() => {
    if (userId) {
      loadEngagementData(userId);
    }
  }, [userId, loadEngagementData]);

  // Calculate stats from correct type structure
  const totalConversations = dashboardData?.weekly_activity?.total_conversations || 0;
  const totalPoints = achievementsData?.summary?.total_points || 0;
  const currentLevel = achievementsData?.summary?.level || 1;
  const unlockedCount = achievementsData?.summary?.unlocked || 0;
  const totalAchievements = achievementsData?.summary?.total || 0;

  // Build activity history for weekly view from streak data
  const activityHistory = streakData?.activity_history || [];

  // Build achievements summary for panel
  const achievementsSummary = achievementsData?.summary || {
    total: 0,
    unlocked: 0,
    total_points: 0,
    level: 1,
    level_progress: 0
  };

  // Get all achievements for panel
  const allAchievements = achievementsData?.achievements || [];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #fafafa 0%, #f5f5f7 100%)',
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    }}>
      {/* Mobile responsive styles */}
      <style>{`
        @media (max-width: 640px) {
          .dashboard-header {
            padding: 0.75rem 1rem !important;
          }
          .dashboard-header h1 {
            font-size: 1.25rem !important;
          }
          .dashboard-content {
            padding: 1rem !important;
          }
          .stats-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 0.75rem !important;
          }
          .stat-card {
            padding: 1rem !important;
          }
          .stat-value {
            font-size: 1.5rem !important;
          }
        }
        @media (max-width: 480px) {
          .stats-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
      
      {/* Header */}
      <header className="dashboard-header" style={{
        background: '#ffffff',
        borderBottom: '1px solid #e5e7eb',
        padding: '1rem 2rem',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button
              onClick={() => navigate(-1)}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '0.5rem',
                borderRadius: '0.5rem',
                display: 'flex',
                alignItems: 'center',
                color: '#6b7280',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#f3f4f6';
                e.currentTarget.style.color = '#1f2937';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'none';
                e.currentTarget.style.color = '#6b7280';
              }}
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 style={{ 
                margin: 0, 
                fontSize: '1.5rem', 
                fontWeight: 600,
                color: '#1d1d1f'
              }}>
                Your Progress
              </h1>
              <p style={{
                margin: 0,
                fontSize: '0.875rem',
                color: '#6b7280'
              }}>
                Track your wisdom journey
              </p>
            </div>
          </div>
          
          {/* Current Streak in Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button
              onClick={handleRefresh}
              disabled={loading}
              style={{
                background: 'none',
                border: '1px solid #e5e7eb',
                cursor: loading ? 'not-allowed' : 'pointer',
                padding: '0.5rem',
                borderRadius: '0.5rem',
                display: 'flex',
                alignItems: 'center',
                color: '#6b7280',
                transition: 'all 0.2s ease',
                opacity: loading ? 0.5 : 1
              }}
              title="Refresh data"
            >
              <RefreshCw size={18} style={{ 
                animation: loading ? 'spin 1s linear infinite' : 'none' 
              }} />
            </button>
            <StreakDisplay
              currentStreak={streakData?.current_streak || 0}
              longestStreak={streakData?.longest_streak}
              streakAtRisk={streakData?.streak_at_risk}
              freezesAvailable={streakData?.streak_freezes_available}
              compact={false}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-content" style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '2rem'
      }}>
        {loading && !streakData ? (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '400px'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '3px solid #f3f4f6',
              borderTop: '3px solid #f97316',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
            <style>{`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        ) : error ? (
          <div style={{
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '0.75rem',
            padding: '2rem',
            textAlign: 'center'
          }}>
            <p style={{ color: '#dc2626', margin: 0 }}>
              {error}
            </p>
            <button
              onClick={() => loadEngagementData(userId)}
              style={{
                marginTop: '1rem',
                background: '#f97316',
                color: 'white',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontWeight: 500
              }}
            >
              Retry
            </button>
          </div>
        ) : (
          <>
            {/* Stats Overview */}
            <div className="stats-grid" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
              marginBottom: '2rem'
            }}>
              {/* Current Streak */}
              <div className="stat-card" style={{
                background: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)',
                borderRadius: '1rem',
                padding: '1.5rem',
                border: '1px solid #fed7aa'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <Flame size={20} style={{ color: '#f97316' }} />
                  <span style={{ fontSize: '0.875rem', color: '#9a3412', fontWeight: 500 }}>
                    Current Streak
                  </span>
                </div>
                <div className="stat-value" style={{ fontSize: '2rem', fontWeight: 700, color: '#ea580c' }}>
                  {streakData?.current_streak || 0}
                  <span style={{ fontSize: '1rem', fontWeight: 400, marginLeft: '0.25rem' }}>days</span>
                </div>
                {streakData?.longest_streak && streakData.longest_streak > 0 && (
                  <div style={{ fontSize: '0.75rem', color: '#c2410c', marginTop: '0.25rem' }}>
                    Best: {streakData.longest_streak} days
                  </div>
                )}
              </div>

              {/* Total Points */}
              <div className="stat-card" style={{
                background: 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)',
                borderRadius: '1rem',
                padding: '1.5rem',
                border: '1px solid #e9d5ff'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <Trophy size={20} style={{ color: '#9333ea' }} />
                  <span style={{ fontSize: '0.875rem', color: '#6b21a8', fontWeight: 500 }}>
                    Total Points
                  </span>
                </div>
                <div className="stat-value" style={{ fontSize: '2rem', fontWeight: 700, color: '#7c3aed' }}>
                  {totalPoints.toLocaleString()}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#7e22ce', marginTop: '0.25rem' }}>
                  Level {currentLevel}
                </div>
              </div>

              {/* Achievements */}
              <div className="stat-card" style={{
                background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                borderRadius: '1rem',
                padding: '1.5rem',
                border: '1px solid #bbf7d0'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <Award size={20} style={{ color: '#16a34a' }} />
                  <span style={{ fontSize: '0.875rem', color: '#166534', fontWeight: 500 }}>
                    Achievements
                  </span>
                </div>
                <div className="stat-value" style={{ fontSize: '2rem', fontWeight: 700, color: '#15803d' }}>
                  {unlockedCount}
                  <span style={{ fontSize: '1rem', fontWeight: 400, color: '#22c55e' }}>
                    /{totalAchievements}
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#15803d', marginTop: '0.25rem' }}>
                  {Math.round((unlockedCount / Math.max(totalAchievements, 1)) * 100)}% complete
                </div>
              </div>

              {/* Conversations */}
              <div className="stat-card" style={{
                background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
                borderRadius: '1rem',
                padding: '1.5rem',
                border: '1px solid #bfdbfe'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <TrendingUp size={20} style={{ color: '#2563eb' }} />
                  <span style={{ fontSize: '0.875rem', color: '#1e40af', fontWeight: 500 }}>
                    Conversations
                  </span>
                </div>
                <div className="stat-value" style={{ fontSize: '2rem', fontWeight: 700, color: '#1d4ed8' }}>
                  {totalConversations}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#1e40af', marginTop: '0.25rem' }}>
                  Total wisdom exchanges
                </div>
              </div>
            </div>

            {/* Weekly Activity */}
            <div style={{
              background: '#ffffff',
              borderRadius: '1rem',
              padding: '1.5rem',
              marginBottom: '2rem',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{
                margin: '0 0 1rem 0',
                fontSize: '1.125rem',
                fontWeight: 600,
                color: '#1d1d1f',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <Calendar size={20} style={{ color: '#6b7280' }} />
                This Week's Activity
              </h2>
              <StreakWeekView
                activityHistory={activityHistory}
                currentStreak={streakData?.current_streak || 0}
              />
            </div>

            {/* Achievements Panel */}
            <AchievementsPanel
              achievements={allAchievements}
              summary={achievementsSummary}
            />
          </>
        )}
      </main>

      {/* Achievement Unlock Modal */}
      {showAchievementModal && pendingAchievement && (
        <AchievementUnlockModal
          open={showAchievementModal}
          achievement={pendingAchievement}
          onClose={dismissAchievementModal}
        />
      )}
    </div>
  );
};

export default ProgressDashboard;
