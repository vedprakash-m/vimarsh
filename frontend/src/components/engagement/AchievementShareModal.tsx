/**
 * AchievementShareModal Component
 * 
 * Modal for sharing unlocked achievements on social media
 */

import React, { useState, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  IconButton,
  Stack,
  Snackbar,
  Alert,
  useTheme
} from '@mui/material';
import {
  X,
  Share2,
  Copy,
  Check,
  Trophy,
  Flame,
  Star,
  Zap
} from 'lucide-react';
import { trackAchievementEvent } from '../../utils/analytics';
import type { Achievement, AchievementTier } from './types';

// Platform icons
const TwitterIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

const FacebookIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
  </svg>
);

const LinkedInIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
  </svg>
);

const WhatsAppIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
  </svg>
);

interface AchievementShareModalProps {
  open: boolean;
  achievement: Achievement | null;
  onClose: () => void;
}

// Get icon for achievement category
const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'streak':
      return <Flame size={24} />;
    case 'exploration':
      return <Star size={24} />;
    case 'mastery':
      return <Zap size={24} />;
    default:
      return <Trophy size={24} />;
  }
};

// Get color for tier
const getTierColor = (tier: AchievementTier) => {
  switch (tier) {
    case 'platinum':
      return '#E5E4E2';
    case 'gold':
      return '#FFD700';
    case 'silver':
      return '#C0C0C0';
    case 'bronze':
      return '#CD7F32';
    default:
      return '#9E9E9E';
  }
};

// Get tier label
const getTierLabel = (tier: AchievementTier) => {
  switch (tier) {
    case 'platinum':
      return '💎 Platinum';
    case 'gold':
      return '🏆 Gold';
    case 'silver':
      return '🥈 Silver';
    case 'bronze':
      return '🥉 Bronze';
    default:
      return '📜 Common';
  }
};

const AchievementShareModal: React.FC<AchievementShareModalProps> = ({
  open,
  achievement,
  onClose
}) => {
  const theme = useTheme();
  const [copied, setCopied] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'info' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  // Generate share text
  const generateShareText = useCallback((platform?: string) => {
    if (!achievement) return '';

    const tierEmoji = achievement.tier === 'platinum' ? '💎' :
                      achievement.tier === 'gold' ? '🏆' :
                      achievement.tier === 'silver' ? '🥈' : '🥉';

    const maxLength = platform === 'twitter' ? 240 : 400;
    const achievementText = `${tierEmoji} I just unlocked "${achievement.name}" on Vimarsh!`;
    const description = achievement.description.length > maxLength 
      ? achievement.description.substring(0, maxLength - 3) + '...'
      : achievement.description;

    return `${achievementText}\n\n${description}\n\n#Vimarsh #WisdomJourney #Achievement`;
  }, [achievement]);

  // Get share URL
  const getShareUrl = () => 'https://vimarsh.vedmishra.com';

  // Track share
  const trackShare = useCallback((platform: string) => {
    if (achievement) {
      trackAchievementEvent('shared', {
        achievementId: achievement.id,
        achievementName: achievement.name,
        category: achievement.category,
        tier: achievement.tier
      });
    }
  }, [achievement]);

  // Share handlers
  const shareToTwitter = () => {
    const text = generateShareText('twitter');
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(getShareUrl())}`;
    window.open(url, '_blank', 'width=550,height=420,noopener,noreferrer');
    trackShare('twitter');
    setSnackbar({ open: true, message: 'Opening Twitter...', severity: 'info' });
  };

  const shareToFacebook = () => {
    const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(getShareUrl())}&quote=${encodeURIComponent(generateShareText('facebook'))}`;
    window.open(url, '_blank', 'width=550,height=420,noopener,noreferrer');
    trackShare('facebook');
    setSnackbar({ open: true, message: 'Opening Facebook...', severity: 'info' });
  };

  const shareToLinkedIn = () => {
    const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(getShareUrl())}`;
    window.open(url, '_blank', 'width=550,height=500,noopener,noreferrer');
    trackShare('linkedin');
    setSnackbar({ open: true, message: 'Opening LinkedIn...', severity: 'info' });
  };

  const shareToWhatsApp = () => {
    const text = generateShareText('whatsapp');
    const url = `https://wa.me/?text=${encodeURIComponent(text + '\n\n' + getShareUrl())}`;
    window.open(url, '_blank', 'noopener,noreferrer');
    trackShare('whatsapp');
    setSnackbar({ open: true, message: 'Opening WhatsApp...', severity: 'info' });
  };

  const copyToClipboard = async () => {
    try {
      const text = generateShareText() + '\n\n' + getShareUrl();
      await navigator.clipboard.writeText(text);
      setCopied(true);
      trackShare('copy');
      setSnackbar({ open: true, message: 'Copied to clipboard!', severity: 'success' });
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Copy failed:', error);
      setSnackbar({ open: true, message: 'Failed to copy', severity: 'info' });
    }
  };

  const shareNative = async () => {
    if (navigator.share && achievement) {
      try {
        await navigator.share({
          title: `Vimarsh Achievement: ${achievement.name}`,
          text: generateShareText(),
          url: getShareUrl()
        });
        trackShare('native');
      } catch (error) {
        if ((error as Error).name !== 'AbortError') {
          console.error('Share failed:', error);
        }
      }
    }
  };

  if (!achievement) return null;

  const tierColor = getTierColor(achievement.tier);

  return (
    <>
      <Dialog 
        open={open} 
        onClose={onClose}
        maxWidth="sm"
        fullWidth
        aria-labelledby="share-achievement-title"
        PaperProps={{
          sx: {
            borderRadius: 3,
            overflow: 'hidden'
          }
        }}
      >
        {/* Header with achievement preview */}
        <Box
          sx={{
            background: `linear-gradient(135deg, ${tierColor}20 0%, ${tierColor}40 100%)`,
            p: 3,
            textAlign: 'center',
            position: 'relative'
          }}
        >
          <IconButton
            onClick={onClose}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8
            }}
            aria-label="Close share dialog"
          >
            <X size={20} />
          </IconButton>

          {/* Achievement Icon */}
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              backgroundColor: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px',
              boxShadow: `0 4px 20px ${tierColor}60`,
              border: `3px solid ${tierColor}`,
              color: tierColor
            }}
          >
            {achievement.icon ? (
              <span style={{ fontSize: '2.5rem' }}>{achievement.icon}</span>
            ) : (
              getCategoryIcon(achievement.category)
            )}
          </Box>

          <Typography variant="h6" fontWeight={700} gutterBottom>
            {achievement.name}
          </Typography>

          <Typography 
            variant="body2" 
            sx={{ 
              color: tierColor,
              fontWeight: 600,
              mb: 1
            }}
          >
            {getTierLabel(achievement.tier)}
          </Typography>

          <Typography variant="body2" color="text.secondary">
            {achievement.description}
          </Typography>
        </Box>

        <DialogTitle id="share-achievement-title" sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Share2 size={20} />
            <Typography variant="h6">Share Your Achievement</Typography>
          </Box>
        </DialogTitle>

        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Celebrate your wisdom journey! Share this achievement with your friends.
          </Typography>

          {/* Share buttons */}
          <Stack direction="row" spacing={2} justifyContent="center" flexWrap="wrap" useFlexGap>
            {/* Twitter */}
            <IconButton
              onClick={shareToTwitter}
              sx={{
                backgroundColor: '#1DA1F2',
                color: 'white',
                '&:hover': { backgroundColor: '#1a91da' },
                width: 48,
                height: 48
              }}
              aria-label="Share on Twitter"
            >
              <TwitterIcon />
            </IconButton>

            {/* Facebook */}
            <IconButton
              onClick={shareToFacebook}
              sx={{
                backgroundColor: '#4267B2',
                color: 'white',
                '&:hover': { backgroundColor: '#3b5998' },
                width: 48,
                height: 48
              }}
              aria-label="Share on Facebook"
            >
              <FacebookIcon />
            </IconButton>

            {/* LinkedIn */}
            <IconButton
              onClick={shareToLinkedIn}
              sx={{
                backgroundColor: '#0A66C2',
                color: 'white',
                '&:hover': { backgroundColor: '#004182' },
                width: 48,
                height: 48
              }}
              aria-label="Share on LinkedIn"
            >
              <LinkedInIcon />
            </IconButton>

            {/* WhatsApp */}
            <IconButton
              onClick={shareToWhatsApp}
              sx={{
                backgroundColor: '#25D366',
                color: 'white',
                '&:hover': { backgroundColor: '#128C7E' },
                width: 48,
                height: 48
              }}
              aria-label="Share on WhatsApp"
            >
              <WhatsAppIcon />
            </IconButton>

            {/* Copy */}
            <IconButton
              onClick={copyToClipboard}
              sx={{
                backgroundColor: theme.palette.grey[200],
                color: theme.palette.text.primary,
                '&:hover': { backgroundColor: theme.palette.grey[300] },
                width: 48,
                height: 48
              }}
              aria-label="Copy to clipboard"
            >
              {copied ? <Check size={18} /> : <Copy size={18} />}
            </IconButton>
          </Stack>

          {/* Native share button for mobile */}
          {'share' in navigator && (
            <Box sx={{ mt: 3 }}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Share2 size={18} />}
                onClick={shareNative}
                sx={{ borderRadius: 2 }}
              >
                More sharing options...
              </Button>
            </Box>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={onClose} sx={{ borderRadius: 2 }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for feedback */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          severity={snackbar.severity}
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default AchievementShareModal;
