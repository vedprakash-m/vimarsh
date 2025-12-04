/**
 * StreakDisplay Component
 * Compact streak counter with fire animation for header display
 */

import React from 'react';
import {
  Box,
  Typography,
  Tooltip,
  Badge,
  Skeleton,
  useTheme,
  keyframes
} from '@mui/material';
import { Flame, Snowflake, AlertTriangle } from 'lucide-react';

interface StreakDisplayProps {
  currentStreak: number;
  longestStreak?: number;
  streakAtRisk?: boolean;
  freezesAvailable?: number;
  onClick?: () => void;
  compact?: boolean;
  loading?: boolean;
}

// Fire animation keyframes
const flicker = keyframes`
  0%, 100% { transform: scale(1) rotate(0deg); opacity: 1; }
  25% { transform: scale(1.1) rotate(-2deg); opacity: 0.9; }
  50% { transform: scale(1.05) rotate(1deg); opacity: 1; }
  75% { transform: scale(1.15) rotate(-1deg); opacity: 0.95; }
`;

const pulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
`;

const glow = keyframes`
  0%, 100% { box-shadow: 0 0 5px rgba(255, 87, 34, 0.5); }
  50% { box-shadow: 0 0 20px rgba(255, 87, 34, 0.8), 0 0 30px rgba(255, 152, 0, 0.6); }
`;

const StreakDisplay: React.FC<StreakDisplayProps> = ({
  currentStreak,
  longestStreak,
  streakAtRisk = false,
  freezesAvailable = 0,
  onClick,
  compact = false,
  loading = false
}) => {
  const theme = useTheme();

  // Loading state - compact
  if (loading && compact) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 0.5,
          px: 1.5,
          py: 0.5,
        }}
      >
        <Skeleton variant="circular" width={18} height={18} />
        <Skeleton variant="text" width={20} height={20} />
      </Box>
    );
  }

  // Loading state - full
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 1.5,
          borderRadius: 3,
          bgcolor: 'background.paper',
          boxShadow: 1,
        }}
      >
        <Skeleton variant="rounded" width={44} height={44} sx={{ borderRadius: 2 }} />
        <Box>
          <Skeleton variant="text" width={60} height={32} />
          <Skeleton variant="text" width={50} height={16} />
        </Box>
      </Box>
    );
  }

  // Determine streak tier for styling
  const getStreakTier = () => {
    if (currentStreak >= 100) return { color: '#FFD700', label: 'Legendary' };
    if (currentStreak >= 30) return { color: '#FF9800', label: 'On Fire' };
    if (currentStreak >= 7) return { color: '#FF5722', label: 'Hot' };
    if (currentStreak >= 3) return { color: '#F44336', label: 'Warming Up' };
    return { color: '#9E9E9E', label: 'Starting' };
  };

  const tier = getStreakTier();

  // Milestone check
  const isMilestone = [7, 14, 30, 50, 100, 365].includes(currentStreak);

  const tooltipContent = (
    <Box sx={{ p: 1 }}>
      <Typography variant="subtitle2" fontWeight={600}>
        🔥 {currentStreak} Day Streak
      </Typography>
      {longestStreak && longestStreak > currentStreak && (
        <Typography variant="body2" color="text.secondary">
          Best: {longestStreak} days
        </Typography>
      )}
      {streakAtRisk && (
        <Typography variant="body2" color="warning.main">
          ⚠️ Complete activity today to keep your streak!
        </Typography>
      )}
      {freezesAvailable > 0 && (
        <Typography variant="body2" color="info.main">
          ❄️ {freezesAvailable} streak freeze{freezesAvailable > 1 ? 's' : ''} available
        </Typography>
      )}
    </Box>
  );

  if (compact) {
    return (
      <Tooltip title={tooltipContent} arrow placement="bottom">
        <Box
          onClick={onClick}
          role={onClick ? "button" : undefined}
          tabIndex={onClick ? 0 : undefined}
          aria-label={`${currentStreak} day streak${streakAtRisk ? ', at risk' : ''}${freezesAvailable > 0 ? `, ${freezesAvailable} freezes available` : ''}`}
          onKeyDown={(e) => {
            if (onClick && (e.key === 'Enter' || e.key === ' ')) {
              e.preventDefault();
              onClick();
            }
          }}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            cursor: onClick ? 'pointer' : 'default',
            px: 1.5,
            py: 0.5,
            borderRadius: 2,
            bgcolor: streakAtRisk ? 'warning.50' : 'transparent',
            transition: 'all 0.2s',
            '&:hover': onClick ? {
              bgcolor: 'action.hover'
            } : {},
            '&:focus-visible': {
              outline: '2px solid',
              outlineColor: 'primary.main',
              outlineOffset: 2
            }
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              animation: currentStreak > 0 ? `${flicker} 1.5s ease-in-out infinite` : 'none',
              color: tier.color
            }}
          >
            <Flame size={18} fill={currentStreak > 0 ? tier.color : 'none'} />
          </Box>
          <Typography
            variant="body2"
            fontWeight={600}
            sx={{ color: tier.color }}
          >
            {currentStreak}
          </Typography>
          {streakAtRisk && (
            <AlertTriangle size={14} color={theme.palette.warning.main} />
          )}
        </Box>
      </Tooltip>
    );
  }

  return (
    <Tooltip title={tooltipContent} arrow placement="bottom">
      <Box
        onClick={onClick}
        role={onClick ? "button" : undefined}
        tabIndex={onClick ? 0 : undefined}
        aria-label={`${currentStreak} day streak, ${tier.label}${streakAtRisk ? ', at risk' : ''}${freezesAvailable > 0 ? `, ${freezesAvailable} streak freezes available` : ''}`}
        onKeyDown={(e) => {
          if (onClick && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            onClick();
          }
        }}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          cursor: onClick ? 'pointer' : 'default',
          p: 1.5,
          borderRadius: 3,
          bgcolor: 'background.paper',
          boxShadow: 1,
          border: streakAtRisk ? `2px solid ${theme.palette.warning.main}` : 'none',
          animation: isMilestone ? `${glow} 2s ease-in-out infinite` : 'none',
          transition: 'all 0.2s',
          '&:hover': onClick ? {
            transform: 'translateY(-2px)',
            boxShadow: 3
          } : {},
          '&:focus-visible': {
            outline: '2px solid',
            outlineColor: 'primary.main',
            outlineOffset: 2
          }
        }}
      >
        {/* Fire icon */}
        <Badge
          badgeContent={freezesAvailable}
          color="info"
          invisible={freezesAvailable === 0}
          anchorOrigin={{ vertical: 'top', horizontal: 'left' }}
        >
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: 2,
              bgcolor: `${tier.color}15`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: currentStreak > 0 
                ? `${flicker} 1.5s ease-in-out infinite`
                : 'none'
            }}
          >
            <Flame 
              size={24} 
              color={tier.color} 
              fill={currentStreak > 0 ? tier.color : 'none'}
            />
          </Box>
        </Badge>

        {/* Streak count */}
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5 }}>
            <Typography 
              variant="h5" 
              fontWeight={700}
              sx={{ 
                color: tier.color,
                animation: isMilestone ? `${pulse} 1s ease-in-out infinite` : 'none'
              }}
            >
              {currentStreak}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              day{currentStreak !== 1 ? 's' : ''}
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            {tier.label}
          </Typography>
        </Box>

        {/* Risk indicator */}
        {streakAtRisk && (
          <Box
            sx={{
              ml: 1,
              p: 0.5,
              borderRadius: 1,
              bgcolor: 'warning.50',
              display: 'flex',
              alignItems: 'center',
              gap: 0.5
            }}
          >
            <AlertTriangle size={14} color={theme.palette.warning.main} />
            <Typography variant="caption" color="warning.main" fontWeight={600}>
              At Risk
            </Typography>
          </Box>
        )}
      </Box>
    </Tooltip>
  );
};

export default StreakDisplay;
