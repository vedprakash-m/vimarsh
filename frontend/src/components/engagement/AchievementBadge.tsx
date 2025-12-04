/**
 * AchievementBadge Component
 * Single achievement display with progress ring
 */

import React from 'react';
import {
  Box,
  Typography,
  Tooltip,
  Skeleton,
  useTheme,
  keyframes
} from '@mui/material';
import { Lock } from 'lucide-react';
import { Achievement, AchievementTier } from './types';

interface AchievementBadgeProps {
  achievement?: Achievement;
  size?: 'small' | 'medium' | 'large';
  showProgress?: boolean;
  onClick?: () => void;
  loading?: boolean;
}

// Tier colors
const tierColors: Record<AchievementTier, string> = {
  bronze: '#CD7F32',
  silver: '#C0C0C0',
  gold: '#FFD700',
  platinum: '#E5E4E2'
};

// Glow animation for recently unlocked
const unlockGlow = keyframes`
  0%, 100% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }
  50% { box-shadow: 0 0 25px rgba(255, 215, 0, 0.8); }
`;

const AchievementBadge: React.FC<AchievementBadgeProps> = ({
  achievement,
  size = 'medium',
  showProgress = true,
  onClick,
  loading = false
}) => {
  const theme = useTheme();

  const sizes = {
    small: { badge: 48, icon: 24, ring: 56 },
    medium: { badge: 64, icon: 32, ring: 72 },
    large: { badge: 80, icon: 40, ring: 88 }
  };

  const dimensions = sizes[size];

  // Loading state
  if (loading || !achievement) {
    return (
      <Box
        sx={{
          position: 'relative',
          width: dimensions.ring,
          height: dimensions.ring,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Skeleton 
          variant="circular" 
          width={dimensions.badge} 
          height={dimensions.badge}
          animation="wave"
        />
      </Box>
    );
  }

  const { unlocked, progress, tier } = achievement;
  const tierColor = tierColors[tier];
  const progressPercent = progress?.percentage || 0;

  // Calculate SVG circle values
  const strokeWidth = size === 'small' ? 3 : 4;
  const radius = (dimensions.ring - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progressPercent / 100) * circumference;

  const tooltipContent = (
    <Box sx={{ p: 1, maxWidth: 200 }}>
      <Typography variant="subtitle2" fontWeight={600}>
        {achievement.name}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        {achievement.description}
      </Typography>
      {!unlocked && progress.target && (
        <Typography variant="caption" color="primary.main">
          Progress: {progress.current} / {progress.target}
        </Typography>
      )}
      {unlocked && achievement.unlocked_at && (
        <Typography variant="caption" color="success.main">
          ✅ Unlocked {new Date(achievement.unlocked_at).toLocaleDateString()}
        </Typography>
      )}
      <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
        {achievement.points} points • {tier.charAt(0).toUpperCase() + tier.slice(1)}
      </Typography>
    </Box>
  );

  return (
    <Tooltip title={tooltipContent} arrow placement="top">
      <Box
        onClick={onClick}
        role={onClick ? "button" : undefined}
        tabIndex={onClick ? 0 : undefined}
        aria-label={`${achievement.name}${unlocked ? ', unlocked' : `, ${Math.round(progressPercent)}% progress`}, ${achievement.points} points, ${tier} tier`}
        onKeyDown={(e) => {
          if (onClick && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            onClick();
          }
        }}
        sx={{
          position: 'relative',
          width: dimensions.ring,
          height: dimensions.ring,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: onClick ? 'pointer' : 'default',
          transition: 'transform 0.2s',
          '&:hover': onClick ? {
            transform: 'scale(1.1)'
          } : {},
          '&:focus-visible': {
            outline: '2px solid',
            outlineColor: 'primary.main',
            outlineOffset: 2,
            borderRadius: '50%'
          }
        }}
      >
        {/* Progress ring */}
        {showProgress && !unlocked && (
          <svg
            width={dimensions.ring}
            height={dimensions.ring}
            style={{ position: 'absolute', transform: 'rotate(-90deg)' }}
          >
            {/* Background ring */}
            <circle
              cx={dimensions.ring / 2}
              cy={dimensions.ring / 2}
              r={radius}
              fill="none"
              stroke={theme.palette.grey[200]}
              strokeWidth={strokeWidth}
            />
            {/* Progress ring */}
            <circle
              cx={dimensions.ring / 2}
              cy={dimensions.ring / 2}
              r={radius}
              fill="none"
              stroke={tierColor}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              style={{ transition: 'stroke-dashoffset 0.5s ease-out' }}
            />
          </svg>
        )}

        {/* Unlocked ring */}
        {unlocked && (
          <Box
            sx={{
              position: 'absolute',
              width: dimensions.ring,
              height: dimensions.ring,
              borderRadius: '50%',
              border: `${strokeWidth}px solid ${tierColor}`,
              boxShadow: `0 0 10px ${tierColor}40`
            }}
          />
        )}

        {/* Badge container */}
        <Box
          sx={{
            width: dimensions.badge,
            height: dimensions.badge,
            borderRadius: '50%',
            bgcolor: unlocked ? `${tierColor}15` : 'grey.100',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            filter: unlocked ? 'none' : 'grayscale(50%)',
            opacity: unlocked ? 1 : 0.7,
            animation: unlocked ? `${unlockGlow} 2s ease-in-out infinite` : 'none'
          }}
        >
          {/* Achievement icon */}
          <Typography
            sx={{
              fontSize: dimensions.icon,
              lineHeight: 1,
              filter: unlocked ? 'none' : 'grayscale(100%)'
            }}
          >
            {achievement.icon}
          </Typography>

          {/* Lock overlay for locked achievements */}
          {!unlocked && (
            <Box
              sx={{
                position: 'absolute',
                bottom: 0,
                right: 0,
                width: 20,
                height: 20,
                borderRadius: '50%',
                bgcolor: 'grey.400',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <Lock size={12} color="white" />
            </Box>
          )}
        </Box>
      </Box>
    </Tooltip>
  );
};

export default AchievementBadge;
