/**
 * OnboardingWizard Component
 * Main onboarding container that manages the multi-step flow
 */

import React, { useMemo, useState } from 'react';
import {
  Box,
  Dialog,
  DialogContent,
  IconButton,
  useTheme,
  useMediaQuery,
  Slide,
  CircularProgress
} from '@mui/material';
import { TransitionProps } from '@mui/material/transitions';
import { X } from 'lucide-react';
import WelcomeStep from './WelcomeStep';
import PersonalityQuiz from './PersonalityQuiz';
import MatchResult from './MatchResult';
import NotificationOptInStep from './NotificationOptInStep';
import { useOnboarding } from './useOnboarding';

interface OnboardingWizardProps {
  open: boolean;
  onClose: () => void;
  userId: string;
  userName?: string;
  onSelectPersonality: (personalityId: string) => void;
}

// Slide transition for mobile
const Transition = React.forwardRef(function Transition(
  props: TransitionProps & { children: React.ReactElement },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const OnboardingWizard: React.FC<OnboardingWizardProps> = ({
  open,
  onClose,
  userId,
  userName,
  onSelectPersonality
}) => {
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('md'));

  // Track if user has seen notification opt-in
  const [showNotificationOptIn, setShowNotificationOptIn] = useState(false);
  const [selectedPersonalityForNotif, setSelectedPersonalityForNotif] = useState<string | null>(null);

  const {
    state,
    questions,
    quizResult,
    currentStep,
    isLoading,
    error,
    advanceStep,
    recordResponse,
    submitQuiz,
    completeOnboarding,
    skipOnboarding,
    responses
  } = useOnboarding(userId);

  // Handle starting the quiz
  const handleStartQuiz = async () => {
    await advanceStep();
  };

  // Handle skipping onboarding
  const handleSkip = async () => {
    await skipOnboarding();
    onClose();
  };

  // Handle starting conversation with selected personality - show notification opt-in first
  const handleStartConversation = async (personalityId: string) => {
    // Store selected personality and show notification opt-in
    setSelectedPersonalityForNotif(personalityId);
    setShowNotificationOptIn(true);
  };

  // Handle continuing after notification opt-in
  const handleNotificationComplete = async () => {
    await completeOnboarding();
    if (selectedPersonalityForNotif) {
      onSelectPersonality(selectedPersonalityForNotif);
    }
    onClose();
  };

  // Handle exploring all personalities - show notification opt-in first
  const handleExploreMore = async () => {
    // Show notification opt-in before exploring
    setSelectedPersonalityForNotif(null);
    setShowNotificationOptIn(true);
  };

  // Handle continuing to explore after notification opt-in
  const handleExploreAfterNotification = async () => {
    await completeOnboarding();
    onClose();
  };

  // Render current step content
  const renderStepContent = () => {
    if (isLoading && !questions.length) {
      return (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '50vh'
          }}
        >
          <CircularProgress />
        </Box>
      );
    }

    // Check if already completed
    if (state?.is_complete || state?.was_skipped) {
      onClose();
      return null;
    }

    // Show notification opt-in if triggered
    if (showNotificationOptIn) {
      const personalityName = quizResult?.recommended_personality?.name || 'your guide';
      return (
        <NotificationOptInStep
          onContinue={selectedPersonalityForNotif ? handleNotificationComplete : handleExploreAfterNotification}
          personalityName={personalityName}
        />
      );
    }

    switch (currentStep) {
      case 'welcome':
        return (
          <WelcomeStep
            onStart={handleStartQuiz}
            onSkip={handleSkip}
            userName={userName}
          />
        );

      case 'quiz':
        return (
          <PersonalityQuiz
            questions={questions}
            responses={responses}
            onRecordResponse={recordResponse}
            onSubmit={submitQuiz}
            isSubmitting={isLoading}
          />
        );

      case 'first_chat':
      case 'discovery':
        // Show match results if we have quiz results
        if (quizResult) {
          return (
            <MatchResult
              result={quizResult}
              onStartConversation={handleStartConversation}
              onExploreMore={handleExploreMore}
            />
          );
        }
        // Fallback - shouldn't happen normally
        return (
          <WelcomeStep
            onStart={handleStartQuiz}
            onSkip={handleSkip}
            userName={userName}
          />
        );

      case 'complete':
        onClose();
        return null;

      default:
        return (
          <WelcomeStep
            onStart={handleStartQuiz}
            onSkip={handleSkip}
            userName={userName}
          />
        );
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleSkip}
      fullScreen={fullScreen}
      maxWidth="md"
      fullWidth
      TransitionComponent={fullScreen ? Transition : undefined}
      PaperProps={{
        sx: {
          borderRadius: fullScreen ? 0 : 4,
          minHeight: fullScreen ? '100vh' : '70vh',
          maxHeight: fullScreen ? '100vh' : '90vh',
          overflow: 'hidden'
        }
      }}
    >
      {/* Close button */}
      <IconButton
        onClick={handleSkip}
        sx={{
          position: 'absolute',
          right: 16,
          top: 16,
          zIndex: 10,
          bgcolor: 'background.paper',
          boxShadow: 1,
          '&:hover': {
            bgcolor: 'grey.100'
          }
        }}
      >
        <X size={20} />
      </IconButton>

      <DialogContent
        sx={{
          p: 0,
          overflow: 'auto',
          '&::-webkit-scrollbar': {
            width: 6
          },
          '&::-webkit-scrollbar-thumb': {
            bgcolor: 'grey.300',
            borderRadius: 3
          }
        }}
      >
        {renderStepContent()}
      </DialogContent>
    </Dialog>
  );
};

export default OnboardingWizard;
