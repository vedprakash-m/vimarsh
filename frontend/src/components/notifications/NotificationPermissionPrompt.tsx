/**
 * NotificationPermissionPrompt Component
 * UI for requesting notification permission during onboarding or in settings
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  useTheme,
  alpha
} from '@mui/material';
import { Bell, BellOff, CheckCircle, AlertTriangle, X } from 'lucide-react';
import { useNotifications } from './useNotifications';

interface NotificationPermissionPromptProps {
  // Inline mode for settings, dialog mode for onboarding
  variant?: 'inline' | 'dialog';
  open?: boolean;
  onClose?: () => void;
  onComplete?: (subscribed: boolean) => void;
  title?: string;
  description?: string;
}

const NotificationPermissionPrompt: React.FC<NotificationPermissionPromptProps> = ({
  variant = 'inline',
  open = true,
  onClose,
  onComplete,
  title = 'Enable Daily Wisdom Reminders',
  description = 'Get personalized wisdom notifications at your preferred time. Never miss your daily dose of inspiration.'
}) => {
  const theme = useTheme();
  const {
    isSupported,
    permission,
    isSubscribed,
    isLoading,
    error,
    subscribe,
    unsubscribe
  } = useNotifications();

  const [step, setStep] = useState<'prompt' | 'success' | 'denied'>('prompt');

  const handleEnable = async () => {
    const success = await subscribe();
    if (success) {
      setStep('success');
      onComplete?.(true);
    } else if (permission === 'denied') {
      setStep('denied');
    }
  };

  const handleDisable = async () => {
    await unsubscribe();
    onComplete?.(false);
  };

  const handleSkip = () => {
    onComplete?.(false);
    onClose?.();
  };

  // Not supported
  if (!isSupported) {
    return variant === 'dialog' ? null : (
      <Alert severity="info" sx={{ mb: 2 }}>
        Push notifications are not supported in this browser.
      </Alert>
    );
  }

  // Already subscribed state
  if (isSubscribed && step === 'prompt') {
    const content = (
      <Box sx={{ textAlign: 'center', py: 2 }}>
        <CheckCircle 
          size={48} 
          color={theme.palette.success.main} 
          style={{ marginBottom: 16 }}
        />
        <Typography variant="h6" gutterBottom>
          Notifications Enabled
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          You're all set to receive daily wisdom reminders.
        </Typography>
        <Button
          variant="outlined"
          color="error"
          startIcon={<BellOff size={18} />}
          onClick={handleDisable}
          disabled={isLoading}
        >
          Disable Notifications
        </Button>
      </Box>
    );

    if (variant === 'dialog') {
      return (
        <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
          <DialogTitle>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              Notification Settings
              <Button size="small" onClick={onClose} sx={{ minWidth: 'auto' }}>
                <X size={20} />
              </Button>
            </Box>
          </DialogTitle>
          <DialogContent>{content}</DialogContent>
        </Dialog>
      );
    }

    return <Paper sx={{ p: 3 }}>{content}</Paper>;
  }

  // Success state
  if (step === 'success') {
    const content = (
      <Box sx={{ textAlign: 'center', py: 3 }}>
        <Box
          sx={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            bgcolor: alpha(theme.palette.success.main, 0.1),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mx: 'auto',
            mb: 2
          }}
        >
          <CheckCircle size={40} color={theme.palette.success.main} />
        </Box>
        <Typography variant="h6" gutterBottom>
          🔔 Notifications Enabled!
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          You'll receive daily wisdom at your preferred time.
          Customize your preferences in Settings.
        </Typography>
        {variant === 'dialog' && (
          <Button variant="contained" onClick={onClose}>
            Got It
          </Button>
        )}
      </Box>
    );

    if (variant === 'dialog') {
      return (
        <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
          <DialogContent>{content}</DialogContent>
        </Dialog>
      );
    }

    return <Paper sx={{ p: 3 }}>{content}</Paper>;
  }

  // Denied state
  if (step === 'denied' || permission === 'denied') {
    const content = (
      <Box sx={{ textAlign: 'center', py: 3 }}>
        <Box
          sx={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            bgcolor: alpha(theme.palette.warning.main, 0.1),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mx: 'auto',
            mb: 2
          }}
        >
          <AlertTriangle size={40} color={theme.palette.warning.main} />
        </Box>
        <Typography variant="h6" gutterBottom>
          Permission Blocked
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Notifications are blocked. To enable them, click the lock icon in your browser's address bar and allow notifications.
        </Typography>
        <Button variant="outlined" onClick={onClose || handleSkip}>
          Continue Without Notifications
        </Button>
      </Box>
    );

    if (variant === 'dialog') {
      return (
        <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
          <DialogContent>{content}</DialogContent>
        </Dialog>
      );
    }

    return <Paper sx={{ p: 3 }}>{content}</Paper>;
  }

  // Prompt state
  const promptContent = (
    <Box sx={{ textAlign: 'center', py: variant === 'dialog' ? 2 : 3 }}>
      <Box
        sx={{
          width: 80,
          height: 80,
          borderRadius: '50%',
          bgcolor: alpha(theme.palette.primary.main, 0.1),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mx: 'auto',
          mb: 2
        }}
      >
        <Bell size={40} color={theme.palette.primary.main} />
      </Box>
      
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        {description}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2, textAlign: 'left' }}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={isLoading ? <CircularProgress size={18} color="inherit" /> : <Bell size={18} />}
          onClick={handleEnable}
          disabled={isLoading}
        >
          Enable Notifications
        </Button>
        
        {variant === 'dialog' && (
          <Button
            variant="outlined"
            onClick={handleSkip}
            disabled={isLoading}
          >
            Skip for Now
          </Button>
        )}
      </Box>

      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
        You can change this anytime in Settings
      </Typography>
    </Box>
  );

  if (variant === 'dialog') {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
        <DialogContent>{promptContent}</DialogContent>
      </Dialog>
    );
  }

  return <Paper sx={{ p: 3 }}>{promptContent}</Paper>;
};

export default NotificationPermissionPrompt;
