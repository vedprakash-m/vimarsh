/**
 * WelcomeStep Component
 * First step of onboarding - animated welcome with value proposition
 */

import React from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Fade,
  Grow,
  useTheme
} from '@mui/material';
import {
  Sparkles,
  MessageCircle,
  Users,
  ArrowRight,
  SkipForward
} from 'lucide-react';

interface WelcomeStepProps {
  onStart: () => void;
  onSkip: () => void;
  userName?: string;
}

const WelcomeStep: React.FC<WelcomeStepProps> = ({ onStart, onSkip, userName }) => {
  const theme = useTheme();

  const features = [
    {
      icon: <MessageCircle size={24} />,
      title: 'Personalized Wisdom',
      description: 'Have meaningful conversations with 25 historical luminaries'
    },
    {
      icon: <Users size={24} />,
      title: 'Find Your Guide',
      description: 'Discover which great minds resonate most with you'
    },
    {
      icon: <Sparkles size={24} />,
      title: 'Daily Insights',
      description: 'Build a streak of wisdom-seeking habits'
    }
  ];

  return (
    <Box
      sx={{
        minHeight: '80vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        px: 3,
        py: 4
      }}
    >
      <Grow in timeout={800}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          {/* Animated logo/icon */}
          <Box
            sx={{
              width: 80,
              height: 80,
              mx: 'auto',
              mb: 3,
              borderRadius: '50%',
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: `0 8px 32px ${theme.palette.primary.main}40`,
              animation: 'pulse 2s ease-in-out infinite'
            }}
          >
            <Typography variant="h3" sx={{ color: 'white' }}>
              🕉️
            </Typography>
          </Box>

          <Typography 
            variant="h3" 
            sx={{ 
              fontWeight: 700, 
              mb: 2,
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              color: 'transparent'
            }}
          >
            Welcome{userName ? `, ${userName}` : ''}!
          </Typography>

          <Typography 
            variant="h6" 
            color="text.secondary" 
            sx={{ maxWidth: 500, mx: 'auto' }}
          >
            Vimarsh connects you with timeless wisdom from history's greatest minds.
            Let's personalize your journey in 60 seconds.
          </Typography>
        </Box>
      </Grow>

      {/* Feature cards */}
      <Box 
        sx={{ 
          display: 'flex', 
          gap: 2, 
          flexWrap: 'wrap', 
          justifyContent: 'center',
          mb: 5,
          maxWidth: 800
        }}
      >
        {features.map((feature, index) => (
          <Fade in timeout={800 + index * 200} key={feature.title}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                width: { xs: '100%', sm: 220 },
                textAlign: 'center',
                borderRadius: 3,
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6
                }
              }}
            >
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  mx: 'auto',
                  mb: 2,
                  borderRadius: 2,
                  bgcolor: `${theme.palette.primary.main}15`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme.palette.primary.main
                }}
              >
                {feature.icon}
              </Box>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                {feature.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {feature.description}
              </Typography>
            </Paper>
          </Fade>
        ))}
      </Box>

      {/* Action buttons */}
      <Fade in timeout={1400}>
        <Box sx={{ display: 'flex', gap: 2, flexDirection: 'column', alignItems: 'center' }}>
          <Button
            variant="contained"
            size="large"
            onClick={onStart}
            endIcon={<ArrowRight size={20} />}
            sx={{
              px: 5,
              py: 1.5,
              borderRadius: 3,
              fontSize: '1.1rem',
              fontWeight: 600,
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              '&:hover': {
                background: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.secondary.dark})`,
              }
            }}
          >
            Find My Guide
          </Button>

          <Button
            variant="text"
            color="inherit"
            size="small"
            onClick={onSkip}
            startIcon={<SkipForward size={16} />}
            sx={{ 
              color: 'text.secondary',
              '&:hover': {
                color: 'text.primary'
              }
            }}
          >
            Skip for now
          </Button>
        </Box>
      </Fade>

      {/* CSS Animation */}
      <style>
        {`
          @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
          }
        `}
      </style>
    </Box>
  );
};

export default WelcomeStep;
