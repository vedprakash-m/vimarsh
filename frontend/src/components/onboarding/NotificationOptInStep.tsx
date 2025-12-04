/**
 * NotificationOptInStep Component
 * Onboarding step for notification opt-in after personality match
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  useTheme,
  alpha
} from '@mui/material';
import { Bell, BellOff, Zap, Shield, Clock, ArrowRight } from 'lucide-react';
import { useNotifications } from '../notifications';

interface NotificationOptInStepProps {
  onContinue: () => void;
  personalityName?: string;
}

const NotificationOptInStep: React.FC<NotificationOptInStepProps> = ({
  onContinue,
  personalityName = 'your guide'
}) => {
  const theme = useTheme();
  const { isSupported, subscribe, isLoading } = useNotifications();
  const [isEnabling, setIsEnabling] = useState(false);
  const [hasChosen, setHasChosen] = useState(false);

  const handleEnable = async () => {
    setIsEnabling(true);
    try {
      await subscribe();
      setHasChosen(true);
      // Auto-continue after enabling
      setTimeout(() => onContinue(), 1500);
    } catch (err) {
      console.error('Failed to enable notifications:', err);
      setHasChosen(true);
      // Continue anyway even if notification setup fails
      setTimeout(() => onContinue(), 1500);
    } finally {
      setIsEnabling(false);
    }
  };

  const handleSkip = () => {
    setHasChosen(true);
    onContinue();
  };

  // If notifications not supported, skip this step
  if (!isSupported) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          p: 4,
          textAlign: 'center'
        }}
      >
        <Box
          sx={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            bgcolor: alpha(theme.palette.grey[500], 0.1),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 3
          }}
        >
          <BellOff size={40} color={theme.palette.grey[500]} />
        </Box>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Notifications Not Available
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
          Your browser doesn't support push notifications.
          You can still enjoy all features of Vimarsh!
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={onContinue}
          endIcon={<ArrowRight size={20} />}
        >
          Continue
        </Button>
      </Box>
    );
  }

  // Success state after enabling
  if (hasChosen && !isEnabling) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          p: 4,
          textAlign: 'center'
        }}
      >
        <Box
          sx={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            bgcolor: alpha(theme.palette.success.main, 0.1),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 3,
            animation: 'pulse 1s ease-in-out'
          }}
        >
          <Bell size={40} color={theme.palette.success.main} />
        </Box>
        <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
          You're All Set! ✨
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Starting your journey...
        </Typography>
        <CircularProgress sx={{ mt: 3 }} size={24} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        minHeight: '70vh',
        p: { xs: 3, md: 4 },
        textAlign: 'center'
      }}
    >
      {/* Bell Icon */}
      <Box
        sx={{
          width: 100,
          height: 100,
          borderRadius: '50%',
          background: `linear-gradient(135deg, ${theme.palette.primary.light}, ${theme.palette.primary.main})`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 4,
          boxShadow: `0 8px 32px ${alpha(theme.palette.primary.main, 0.3)}`
        }}
      >
        <Bell size={48} color="white" />
      </Box>

      {/* Title */}
      <Typography 
        variant="h4" 
        sx={{ 
          mb: 2, 
          fontWeight: 700,
          background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}
      >
        Stay Connected
      </Typography>

      {/* Subtitle */}
      <Typography 
        variant="h6" 
        color="text.secondary" 
        sx={{ mb: 4, maxWidth: 400 }}
      >
        Get daily wisdom from {personalityName} and never miss a moment of guidance
      </Typography>

      {/* Benefits */}
      <Box sx={{ maxWidth: 350, mb: 4 }}>
        {[
          {
            icon: <Zap size={24} />,
            title: 'Daily Wisdom',
            description: 'Start each day with inspiring insights'
          },
          {
            icon: <Clock size={24} />,
            title: 'Streak Reminders',
            description: 'Keep your learning momentum going'
          },
          {
            icon: <Shield size={24} />,
            title: 'Your Control',
            description: 'Customize or disable anytime in settings'
          }
        ].map((benefit, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 2,
              p: 2,
              borderRadius: 2,
              bgcolor: alpha(theme.palette.primary.main, 0.05),
              mb: 2,
              textAlign: 'left'
            }}
          >
            <Box
              sx={{
                p: 1,
                borderRadius: 1.5,
                bgcolor: alpha(theme.palette.primary.main, 0.1),
                color: theme.palette.primary.main
              }}
            >
              {benefit.icon}
            </Box>
            <Box>
              <Typography variant="subtitle2" fontWeight={600}>
                {benefit.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {benefit.description}
              </Typography>
            </Box>
          </Box>
        ))}
      </Box>

      {/* Actions */}
      <Box sx={{ width: '100%', maxWidth: 320 }}>
        <Button
          variant="contained"
          size="large"
          fullWidth
          onClick={handleEnable}
          disabled={isEnabling || isLoading}
          startIcon={isEnabling ? <CircularProgress size={20} color="inherit" /> : <Bell size={20} />}
          sx={{
            py: 1.5,
            mb: 2,
            borderRadius: 3,
            fontWeight: 600
          }}
        >
          {isEnabling ? 'Enabling...' : 'Enable Notifications'}
        </Button>

        <Button
          variant="text"
          size="large"
          fullWidth
          onClick={handleSkip}
          disabled={isEnabling}
          sx={{
            color: 'text.secondary',
            '&:hover': {
              bgcolor: 'transparent',
              color: 'text.primary'
            }
          }}
        >
          Maybe Later
        </Button>
      </Box>

      {/* Privacy note */}
      <Typography 
        variant="caption" 
        color="text.secondary"
        sx={{ mt: 4, maxWidth: 300 }}
      >
        We respect your privacy. You can change notification 
        settings anytime from your profile.
      </Typography>
    </Box>
  );
};

export default NotificationOptInStep;
