/**
 * StreakWeekView Component
 * 7-day activity visualization
 */

import React from 'react';
import {
  Box,
  Typography,
  Tooltip,
  useTheme
} from '@mui/material';
import { Check, X, Snowflake } from 'lucide-react';
import { DailyActivity } from './types';

interface StreakWeekViewProps {
  activityHistory: DailyActivity[];
  currentStreak: number;
}

const StreakWeekView: React.FC<StreakWeekViewProps> = ({
  activityHistory,
  currentStreak
}) => {
  const theme = useTheme();

  // Get last 7 days
  const last7Days = activityHistory.slice(0, 7).reverse();

  // Day labels
  const getDayLabel = (index: number): string => {
    const days = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    const today = new Date();
    const dayIndex = new Date(today.setDate(today.getDate() - (6 - index))).getDay();
    return days[dayIndex];
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  return (
    <Box>
      <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1.5 }}>
        This Week
      </Typography>
      
      <Box sx={{ display: 'flex', gap: 1, justifyContent: 'space-between' }}>
        {[...Array(7)].map((_, index) => {
          const activity = last7Days[index];
          const hasActivity = activity?.has_activity || false;
          const wasFrozen = activity?.was_frozen || false;
          const isToday = index === 6;

          return (
            <Tooltip
              key={index}
              title={
                activity ? (
                  <Box sx={{ p: 0.5 }}>
                    <Typography variant="body2" fontWeight={600}>
                      {formatDate(activity.date)}
                    </Typography>
                    {hasActivity ? (
                      <>
                        <Typography variant="caption" display="block">
                          ✅ {activity.conversations} conversation{activity.conversations !== 1 ? 's' : ''}
                        </Typography>
                        {activity.personalities_interacted?.length > 0 && (
                          <Typography variant="caption" display="block" color="text.secondary">
                            👤 {activity.personalities_interacted.join(', ')}
                          </Typography>
                        )}
                      </>
                    ) : wasFrozen ? (
                      <Typography variant="caption" display="block">
                        ❄️ Streak frozen
                      </Typography>
                    ) : (
                      <Typography variant="caption" display="block">
                        ❌ No activity
                      </Typography>
                    )}
                  </Box>
                ) : (
                  isToday ? 'Today - Complete activity to extend your streak!' : 'No data'
                )
              }
              arrow
              placement="top"
            >
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 0.5
                }}
              >
                {/* Day label */}
                <Typography 
                  variant="caption" 
                  color={isToday ? 'primary.main' : 'text.secondary'}
                  fontWeight={isToday ? 600 : 400}
                >
                  {getDayLabel(index)}
                </Typography>

                {/* Activity indicator */}
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: hasActivity 
                      ? 'success.main'
                      : wasFrozen 
                        ? 'info.main'
                        : isToday 
                          ? `${theme.palette.primary.main}15`
                          : 'grey.100',
                    border: isToday && !hasActivity 
                      ? `2px dashed ${theme.palette.primary.main}` 
                      : 'none',
                    transition: 'all 0.2s',
                    '&:hover': {
                      transform: 'scale(1.1)'
                    }
                  }}
                >
                  {hasActivity ? (
                    <Check size={18} color="white" />
                  ) : wasFrozen ? (
                    <Snowflake size={18} color="white" />
                  ) : isToday ? (
                    <Typography variant="caption" color="primary.main">
                      ?
                    </Typography>
                  ) : (
                    <X size={16} color={theme.palette.grey[400]} />
                  )}
                </Box>
              </Box>
            </Tooltip>
          );
        })}
      </Box>

      {/* Streak progress bar */}
      <Box sx={{ mt: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="caption" color="text.secondary">
            Streak Progress
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Next milestone: {getNextMilestone(currentStreak)} days
          </Typography>
        </Box>
        <Box
          sx={{
            height: 4,
            bgcolor: 'grey.200',
            borderRadius: 2,
            overflow: 'hidden'
          }}
        >
          <Box
            sx={{
              height: '100%',
              width: `${getMilestoneProgress(currentStreak)}%`,
              bgcolor: 'success.main',
              borderRadius: 2,
              transition: 'width 0.5s ease-out'
            }}
          />
        </Box>
      </Box>
    </Box>
  );
};

// Helper functions
function getNextMilestone(current: number): number {
  const milestones = [7, 14, 30, 50, 100, 365];
  return milestones.find(m => m > current) || 365;
}

function getMilestoneProgress(current: number): number {
  const milestones = [0, 7, 14, 30, 50, 100, 365];
  
  for (let i = 0; i < milestones.length - 1; i++) {
    const prev = milestones[i];
    const next = milestones[i + 1];
    
    if (current >= prev && current < next) {
      return ((current - prev) / (next - prev)) * 100;
    }
  }
  
  return 100;
}

export default StreakWeekView;
