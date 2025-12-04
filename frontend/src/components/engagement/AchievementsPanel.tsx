/**
 * AchievementsPanel Component
 * Achievement collection view with filtering
 */

import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Chip,
  LinearProgress,
  useTheme
} from '@mui/material';
import { Trophy, Star, Target } from 'lucide-react';
import AchievementBadge from './AchievementBadge';
import { Achievement, AchievementCategory, AchievementSummary } from './types';

interface AchievementsPanelProps {
  achievements: Achievement[];
  summary: AchievementSummary;
  onAchievementClick?: (achievement: Achievement) => void;
}

// Category configuration
const categoryConfig: Record<AchievementCategory, { label: string; icon: string }> = {
  onboarding: { label: 'Getting Started', icon: '🎯' },
  conversation: { label: 'Conversations', icon: '💬' },
  exploration: { label: 'Exploration', icon: '🔍' },
  streak: { label: 'Streaks', icon: '🔥' },
  mastery: { label: 'Mastery', icon: '🏆' },
  special: { label: 'Special', icon: '✨' }
};

const AchievementsPanel: React.FC<AchievementsPanelProps> = ({
  achievements,
  summary,
  onAchievementClick
}) => {
  const theme = useTheme();
  const [selectedCategory, setSelectedCategory] = useState<AchievementCategory | 'all'>('all');

  // Filter achievements by category
  const filteredAchievements = useMemo(() => {
    if (selectedCategory === 'all') return achievements;
    return achievements.filter(a => a.category === selectedCategory);
  }, [achievements, selectedCategory]);

  // Group achievements by unlocked status
  const unlockedAchievements = filteredAchievements.filter(a => a.unlocked);
  const lockedAchievements = filteredAchievements.filter(a => !a.unlocked);

  // Calculate level progress
  const levelProgress = summary.level_progress * 100;
  const pointsToNextLevel = Math.ceil((1 - summary.level_progress) * 100 * summary.level);

  return (
    <Box>
      {/* Summary header */}
      <Paper
        elevation={2}
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 3,
          background: `linear-gradient(135deg, ${theme.palette.primary.main}10, ${theme.palette.secondary.main}10)`
        }}
      >
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, alignItems: 'center' }}>
          {/* Level badge */}
          <Box sx={{ flex: { xs: '1 1 100%', sm: '0 0 auto' } }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box
                sx={{
                  width: 64,
                  height: 64,
                  borderRadius: 2,
                  bgcolor: theme.palette.primary.main,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: `0 4px 20px ${theme.palette.primary.main}40`
                }}
              >
                <Typography variant="h4" fontWeight={700} color="white">
                  {summary.level}
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  Level {summary.level}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {pointsToNextLevel} pts to next level
                </Typography>
              </Box>
            </Box>
          </Box>

          {/* Level progress */}
          <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 0' }, minWidth: 200 }}>
            <Box sx={{ mb: 1, display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Level Progress
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {Math.round(levelProgress)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={levelProgress}
              sx={{
                height: 10,
                borderRadius: 5,
                bgcolor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 5,
                  background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`
                }
              }}
            />
          </Box>
        </Box>

        {/* Stats */}
        <Box 
          sx={{ 
            display: 'flex', 
            gap: 3, 
            mt: 3,
            flexWrap: 'wrap'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Trophy size={18} color={theme.palette.warning.main} />
            <Typography variant="body2">
              <strong>{summary.unlocked}</strong> / {summary.total} unlocked
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Star size={18} color={theme.palette.info.main} />
            <Typography variant="body2">
              <strong>{summary.total_points}</strong> total points
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Target size={18} color={theme.palette.success.main} />
            <Typography variant="body2">
              <strong>{Math.round((summary.unlocked / summary.total) * 100)}%</strong> complete
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Category tabs */}
      <Tabs
        value={selectedCategory}
        onChange={(_, value) => setSelectedCategory(value)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{
          mb: 3,
          '& .MuiTab-root': {
            minWidth: 'auto',
            px: 2
          }
        }}
      >
        <Tab label="All" value="all" />
        {Object.entries(categoryConfig).map(([key, config]) => (
          <Tab
            key={key}
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <span>{config.icon}</span>
                <span>{config.label}</span>
              </Box>
            }
            value={key}
          />
        ))}
      </Tabs>

      {/* Unlocked achievements */}
      {unlockedAchievements.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
            🏆 Unlocked ({unlockedAchievements.length})
          </Typography>
          <Box 
            sx={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              gap: 2,
              '& > *': {
                flex: '0 0 auto'
              }
            }}
          >
            {unlockedAchievements.map(achievement => (
              <AchievementBadge
                key={achievement.id}
                achievement={achievement}
                size="medium"
                onClick={() => onAchievementClick?.(achievement)}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Locked achievements */}
      {lockedAchievements.length > 0 && (
        <Box>
          <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
            🔒 In Progress ({lockedAchievements.length})
          </Typography>
          <Box 
            sx={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              gap: 2,
              '& > *': {
                flex: '0 0 auto'
              }
            }}
          >
            {lockedAchievements.map(achievement => (
              <AchievementBadge
                key={achievement.id}
                achievement={achievement}
                size="medium"
                showProgress
                onClick={() => onAchievementClick?.(achievement)}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Empty state */}
      {filteredAchievements.length === 0 && (
        <Box
          sx={{
            textAlign: 'center',
            py: 6,
            color: 'text.secondary'
          }}
        >
          <Typography variant="h6">No achievements in this category</Typography>
          <Typography variant="body2">
            Keep exploring to unlock more achievements!
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default AchievementsPanel;
