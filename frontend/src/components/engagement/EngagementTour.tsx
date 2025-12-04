/**
 * EngagementTour Component
 * 
 * An interactive onboarding tour to introduce users to the engagement system:
 * - Streak tracking and its benefits
 * - Achievement badges and how to earn them
 * - Progress dashboard features
 * - Notification preferences
 * 
 * Uses a step-by-step guided approach with tooltips highlighting key features.
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Paper,
  Fade,
  Backdrop,
  useTheme,
  LinearProgress
} from '@mui/material';
import { X, ChevronLeft, ChevronRight, Flame, Trophy, Target, Bell, Sparkles } from 'lucide-react';

interface TourStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  highlight?: string; // CSS selector to highlight
  position: 'center' | 'top' | 'bottom' | 'left' | 'right';
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface EngagementTourProps {
  open: boolean;
  onClose: () => void;
  onComplete?: () => void;
}

const tourSteps: TourStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to Your Journey! 🎉',
    description: 'We\'ve added new features to help you build a consistent wisdom practice. Let\'s take a quick tour to see what\'s new.',
    icon: <Sparkles size={32} />,
    position: 'center'
  },
  {
    id: 'streaks',
    title: 'Daily Streaks 🔥',
    description: 'Stay consistent with daily streaks! Each day you have a conversation, your streak grows. Miss a day? Don\'t worry - you get a grace period and streak freezes to protect your progress.',
    icon: <Flame size={32} />,
    position: 'center'
  },
  {
    id: 'achievements',
    title: 'Earn Achievements 🏆',
    description: 'Unlock achievements as you explore! From your first conversation to discovering all domains, there are over 50 badges to collect. Each achievement earns you points toward leveling up.',
    icon: <Trophy size={32} />,
    position: 'center'
  },
  {
    id: 'progress',
    title: 'Track Your Progress 📊',
    description: 'Visit your Progress Dashboard to see your complete journey - weekly activity, achievements, level progression, and personalized insights about your wisdom exploration.',
    icon: <Target size={32} />,
    position: 'center'
  },
  {
    id: 'notifications',
    title: 'Stay Connected 🔔',
    description: 'Enable notifications to receive daily wisdom, streak reminders, and achievement celebrations. You\'re in control - customize when and what notifications you receive.',
    icon: <Bell size={32} />,
    position: 'center'
  },
  {
    id: 'complete',
    title: 'You\'re All Set! ✨',
    description: 'Start a conversation now to begin your streak. Remember, consistency is key to building wisdom. Your journey of a thousand insights begins with a single question.',
    icon: <Sparkles size={32} />,
    position: 'center'
  }
];

const EngagementTour: React.FC<EngagementTourProps> = ({
  open,
  onClose,
  onComplete
}) => {
  const theme = useTheme();
  const [currentStep, setCurrentStep] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  const step = tourSteps[currentStep];
  const progress = ((currentStep + 1) / tourSteps.length) * 100;
  const isLastStep = currentStep === tourSteps.length - 1;
  const isFirstStep = currentStep === 0;

  // Reset to first step when tour opens
  useEffect(() => {
    if (open) {
      setCurrentStep(0);
    }
  }, [open]);

  const handleNext = useCallback(() => {
    if (isLastStep) {
      onComplete?.();
      onClose();
      // Save completion to localStorage
      localStorage.setItem('vimarsh_engagement_tour_completed', 'true');
    } else {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentStep(prev => prev + 1);
        setIsAnimating(false);
      }, 150);
    }
  }, [isLastStep, onClose, onComplete]);

  const handlePrev = useCallback(() => {
    if (!isFirstStep) {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentStep(prev => prev - 1);
        setIsAnimating(false);
      }, 150);
    }
  }, [isFirstStep]);

  const handleSkip = useCallback(() => {
    localStorage.setItem('vimarsh_engagement_tour_skipped', 'true');
    onClose();
  }, [onClose]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!open) return;
      
      if (e.key === 'ArrowRight' || e.key === 'Enter') {
        handleNext();
      } else if (e.key === 'ArrowLeft') {
        handlePrev();
      } else if (e.key === 'Escape') {
        handleSkip();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open, handleNext, handlePrev, handleSkip]);

  if (!open) return null;

  return (
    <Backdrop
      open={open}
      sx={{
        zIndex: theme.zIndex.modal + 1,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(4px)'
      }}
    >
      <Fade in={open && !isAnimating}>
        <Paper
          elevation={24}
          sx={{
            position: 'relative',
            maxWidth: 480,
            width: '90%',
            mx: 2,
            borderRadius: 4,
            overflow: 'hidden',
            bgcolor: 'background.paper'
          }}
          role="dialog"
          aria-labelledby="tour-title"
          aria-describedby="tour-description"
        >
          {/* Progress bar */}
          <LinearProgress 
            variant="determinate" 
            value={progress}
            sx={{
              height: 4,
              bgcolor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`
              }
            }}
          />

          {/* Close button */}
          <IconButton
            onClick={handleSkip}
            aria-label="Close tour"
            sx={{
              position: 'absolute',
              right: 8,
              top: 12,
              color: 'grey.500',
              '&:hover': {
                color: 'grey.700'
              }
            }}
          >
            <X size={20} />
          </IconButton>

          {/* Content */}
          <Box sx={{ p: 4, textAlign: 'center' }}>
            {/* Step indicator */}
            <Typography 
              variant="caption" 
              color="text.secondary"
              sx={{ mb: 2, display: 'block' }}
            >
              Step {currentStep + 1} of {tourSteps.length}
            </Typography>

            {/* Icon */}
            <Box
              sx={{
                width: 80,
                height: 80,
                mx: 'auto',
                mb: 3,
                borderRadius: '50%',
                bgcolor: `${theme.palette.primary.main}15`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: theme.palette.primary.main
              }}
            >
              {step.icon}
            </Box>

            {/* Title */}
            <Typography 
              id="tour-title"
              variant="h5" 
              fontWeight={700}
              sx={{ mb: 2 }}
            >
              {step.title}
            </Typography>

            {/* Description */}
            <Typography 
              id="tour-description"
              variant="body1" 
              color="text.secondary"
              sx={{ mb: 4, lineHeight: 1.7 }}
            >
              {step.description}
            </Typography>

            {/* Step dots */}
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 3 }}>
              {tourSteps.map((_, index) => (
                <Box
                  key={index}
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    bgcolor: index === currentStep ? 'primary.main' : 'grey.300',
                    transition: 'all 0.2s'
                  }}
                />
              ))}
            </Box>

            {/* Navigation buttons */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2 }}>
              <Button
                variant="text"
                color="inherit"
                onClick={handlePrev}
                disabled={isFirstStep}
                startIcon={<ChevronLeft size={18} />}
                sx={{ 
                  visibility: isFirstStep ? 'hidden' : 'visible',
                  color: 'text.secondary'
                }}
              >
                Back
              </Button>

              <Button
                variant="contained"
                onClick={handleNext}
                endIcon={!isLastStep && <ChevronRight size={18} />}
                sx={{
                  px: 4,
                  borderRadius: 2,
                  background: isLastStep 
                    ? `linear-gradient(135deg, ${theme.palette.success.main}, ${theme.palette.success.dark})`
                    : `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                  '&:hover': {
                    background: isLastStep
                      ? `linear-gradient(135deg, ${theme.palette.success.dark}, ${theme.palette.success.main})`
                      : `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`
                  }
                }}
              >
                {isLastStep ? 'Get Started' : 'Next'}
              </Button>
            </Box>

            {/* Skip link */}
            {!isLastStep && (
              <Button
                variant="text"
                size="small"
                onClick={handleSkip}
                sx={{ 
                  mt: 2, 
                  color: 'text.secondary',
                  fontSize: '0.75rem'
                }}
              >
                Skip tour
              </Button>
            )}
          </Box>
        </Paper>
      </Fade>
    </Backdrop>
  );
};

export default EngagementTour;

/**
 * Hook to manage engagement tour state
 */
export const useEngagementTour = () => {
  const [showTour, setShowTour] = useState(false);

  // Check if user has seen the tour
  const hasCompletedTour = useCallback(() => {
    return localStorage.getItem('vimarsh_engagement_tour_completed') === 'true';
  }, []);

  const hasSkippedTour = useCallback(() => {
    return localStorage.getItem('vimarsh_engagement_tour_skipped') === 'true';
  }, []);

  const shouldShowTour = useCallback(() => {
    return !hasCompletedTour() && !hasSkippedTour();
  }, [hasCompletedTour, hasSkippedTour]);

  const startTour = useCallback(() => {
    setShowTour(true);
  }, []);

  const closeTour = useCallback(() => {
    setShowTour(false);
  }, []);

  const resetTour = useCallback(() => {
    localStorage.removeItem('vimarsh_engagement_tour_completed');
    localStorage.removeItem('vimarsh_engagement_tour_skipped');
  }, []);

  // Auto-show tour for new users
  useEffect(() => {
    if (shouldShowTour()) {
      // Delay to let the page load
      const timer = setTimeout(() => {
        setShowTour(true);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [shouldShowTour]);

  return {
    showTour,
    startTour,
    closeTour,
    resetTour,
    hasCompletedTour,
    hasSkippedTour,
    shouldShowTour
  };
};
