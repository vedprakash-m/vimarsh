/**
 * StreakDisplayContainer
 * Self-contained streak display that fetches its own data
 * Used in headers where we need autonomous streak display
 */

import React, { useState, useEffect } from 'react';
import { Box, Skeleton } from '@mui/material';
import StreakDisplay from './StreakDisplay';
import { engagementApi } from './engagementApi';
import type { StreakData } from './types';
import { useAuth } from '../../auth/AuthProvider';

interface StreakDisplayContainerProps {
  compact?: boolean;
  onClick?: () => void;
}

const StreakDisplayContainer: React.FC<StreakDisplayContainerProps> = ({
  compact = true,
  onClick
}) => {
  const { account, isAuthenticated } = useAuth();
  const [streakData, setStreakData] = useState<StreakData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStreakData = async () => {
      if (!isAuthenticated || !account) {
        setLoading(false);
        return;
      }

      const userId = account.username || account.localAccountId || '';
      if (!userId) {
        setLoading(false);
        return;
      }

      try {
        const data = await engagementApi.getStreakData(userId);
        setStreakData(data);
      } catch (error) {
        console.log('🔥 Streak data unavailable:', error);
        // Silently fail - streak display will show 0
      } finally {
        setLoading(false);
      }
    };

    fetchStreakData();
  }, [isAuthenticated, account]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, px: 1.5, py: 0.5 }}>
        <Skeleton variant="circular" width={18} height={18} />
        <Skeleton variant="text" width={20} />
      </Box>
    );
  }

  if (!isAuthenticated || !streakData) {
    // Show a zero streak as placeholder
    return (
      <StreakDisplay
        currentStreak={0}
        compact={compact}
        onClick={onClick}
      />
    );
  }

  return (
    <StreakDisplay
      currentStreak={streakData.current_streak}
      longestStreak={streakData.longest_streak}
      streakAtRisk={streakData.streak_at_risk}
      freezesAvailable={streakData.streak_freezes_available}
      compact={compact}
      onClick={onClick}
    />
  );
};

export default StreakDisplayContainer;
