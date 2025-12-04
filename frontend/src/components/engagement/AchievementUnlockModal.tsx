/**
 * AchievementUnlockModal Component
 * Celebration modal shown when an achievement is unlocked
 */

import React from 'react';
import {
  Dialog,
  DialogContent,
  Box,
  Typography,
  Button,
  IconButton,
  useTheme,
  Fade,
  Grow,
  keyframes
} from '@mui/material';
import { X, Share2 } from 'lucide-react';
import { Achievement, AchievementTier } from './types';

interface AchievementUnlockModalProps {
  open: boolean;
  achievement: Achievement | null;
  onClose: () => void;
  onShare?: () => void;
}

// Tier colors
const tierColors: Record<AchievementTier, string> = {
  bronze: '#CD7F32',
  silver: '#C0C0C0',
  gold: '#FFD700',
  platinum: '#E5E4E2'
};

// Confetti animation
const confettiFall = keyframes`
  0% { transform: translateY(-100vh) rotate(0deg); opacity: 1; }
  100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
`;

const bounce = keyframes`
  0%, 100% { transform: scale(1); }
  25% { transform: scale(1.1); }
  50% { transform: scale(0.95); }
  75% { transform: scale(1.05); }
`;

const glow = keyframes`
  0%, 100% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
  50% { box-shadow: 0 0 40px rgba(255, 215, 0, 0.8), 0 0 60px rgba(255, 152, 0, 0.6); }
`;

const AchievementUnlockModal: React.FC<AchievementUnlockModalProps> = ({
  open,
  achievement,
  onClose,
  onShare
}) => {
  const theme = useTheme();

  if (!achievement) return null;

  const tierColor = tierColors[achievement.tier];

  // Generate confetti pieces
  const confettiPieces = Array.from({ length: 30 }, (_, i) => ({
    id: i,
    left: `${Math.random() * 100}%`,
    delay: `${Math.random() * 2}s`,
    duration: `${2 + Math.random() * 2}s`,
    color: ['#FFD700', '#FF6B6B', '#4ECDC4', '#95E1D3', '#F7DC6F', '#BB8FCE'][Math.floor(Math.random() * 6)]
  }));

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      aria-labelledby="achievement-unlock-title"
      aria-describedby="achievement-unlock-description"
      PaperProps={{
        sx: {
          borderRadius: 4,
          overflow: 'hidden',
          bgcolor: 'background.paper'
        }
      }}
    >
      {/* Confetti overlay */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          overflow: 'hidden',
          pointerEvents: 'none'
        }}
      >
        {confettiPieces.map(piece => (
          <Box
            key={piece.id}
            sx={{
              position: 'absolute',
              left: piece.left,
              top: 0,
              width: 10,
              height: 10,
              bgcolor: piece.color,
              borderRadius: '50%',
              animation: `${confettiFall} ${piece.duration} ease-out ${piece.delay} forwards`
            }}
          />
        ))}
      </Box>

      {/* Close button */}
      <IconButton
        onClick={onClose}
        aria-label="Close achievement notification"
        sx={{
          position: 'absolute',
          right: 8,
          top: 8,
          zIndex: 10
        }}
      >
        <X size={20} />
      </IconButton>

      <DialogContent sx={{ textAlign: 'center', py: 5, px: 4 }}>
        {/* Achievement unlocked text */}
        <Fade in timeout={300}>
          <Typography
            variant="overline"
            id="achievement-unlock-title"
            sx={{
              display: 'block',
              mb: 2,
              color: tierColor,
              fontWeight: 600,
              letterSpacing: 2
            }}
          >
            🎉 ACHIEVEMENT UNLOCKED!
          </Typography>
        </Fade>

        {/* Achievement icon */}
        <Grow in timeout={500}>
          <Box
            sx={{
              width: 120,
              height: 120,
              mx: 'auto',
              mb: 3,
              borderRadius: '50%',
              bgcolor: `${tierColor}15`,
              border: `4px solid ${tierColor}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: `${bounce} 0.6s ease-out, ${glow} 2s ease-in-out infinite`
            }}
            role="img"
            aria-label={`${achievement.name} achievement icon`}
          >
            <Typography sx={{ fontSize: 60 }} aria-hidden="true">
              {achievement.icon}
            </Typography>
          </Box>
        </Grow>

        {/* Achievement name */}
        <Fade in timeout={700}>
          <Typography
            variant="h4"
            fontWeight={700}
            sx={{ mb: 1 }}
          >
            {achievement.name}
          </Typography>
        </Fade>

        {/* Achievement description */}
        <Fade in timeout={900}>
          <Typography
            variant="body1"
            color="text.secondary"
            id="achievement-unlock-description"
            sx={{ mb: 2 }}
          >
            {achievement.description}
          </Typography>
        </Fade>

        {/* Points earned */}
        <Fade in timeout={1100}>
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 1,
              px: 3,
              py: 1,
              borderRadius: 3,
              bgcolor: `${tierColor}15`,
              mb: 3
            }}
          >
            <Typography variant="h5" fontWeight={700} sx={{ color: tierColor }}>
              +{achievement.points}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              points earned
            </Typography>
          </Box>
        </Fade>

        {/* Tier badge */}
        <Fade in timeout={1300}>
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              mb: 3,
              color: tierColor,
              fontWeight: 600
            }}
          >
            {achievement.tier.toUpperCase()} TIER
          </Typography>
        </Fade>

        {/* Action buttons */}
        <Fade in timeout={1500}>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            {onShare && (
              <Button
                variant="outlined"
                startIcon={<Share2 size={18} />}
                onClick={onShare}
                sx={{ borderRadius: 3 }}
              >
                Share
              </Button>
            )}
            <Button
              variant="contained"
              onClick={onClose}
              sx={{
                borderRadius: 3,
                bgcolor: tierColor,
                '&:hover': {
                  bgcolor: tierColor,
                  filter: 'brightness(0.9)'
                }
              }}
            >
              Awesome!
            </Button>
          </Box>
        </Fade>
      </DialogContent>
    </Dialog>
  );
};

export default AchievementUnlockModal;
