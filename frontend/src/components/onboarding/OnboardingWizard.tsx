/**
 * OnboardingWizard Component
 * Flattened domain selector for immediate Time-To-Wisdom
 */

import React from 'react';
import {
  Box,
  Dialog,
  DialogContent,
  IconButton,
  useTheme,
  useMediaQuery,
  Typography,
  Grid,
  Card,
  CardActionArea,
  CircularProgress
} from '@mui/material';
import { X, Flame, BookOpen, Crown, Microscope, Feather, Brain } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { usePersonality } from '../../contexts/PersonalityContext';

interface OnboardingWizardProps {
  open: boolean;
  onClose: () => void;
  userId?: string;
  userName?: string;
  onSelectPersonality: (personalityId: string) => void;
}

const DOMAIN_CONFIG = [
  { id: 'spiritual', label: 'Spiritual', icon: <Flame size={24} /> },
  { id: 'philosophical', label: 'Philosophical', icon: <BookOpen size={24} /> },
  { id: 'leadership', label: 'Leadership', icon: <Crown size={24} /> },
  { id: 'scientific', label: 'Scientific', icon: <Microscope size={24} /> },
  { id: 'literary', label: 'Literary', icon: <Feather size={24} /> },
  { id: 'psychology', label: 'Psychology', icon: <Brain size={24} /> }
];

const OnboardingWizard: React.FC<OnboardingWizardProps> = ({
  open,
  onClose,
  onSelectPersonality
}) => {
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { availablePersonalities, personalityLoading, setSelectedPersonality } = usePersonality();

  const handleDomainSelect = (domainId: string) => {
    // Find the first available personality for this domain or fallback to first
    const personality = availablePersonalities.find(p => p.domain === domainId) || availablePersonalities[0];
    
    if (personality) {
      setSelectedPersonality(personality);
      onSelectPersonality(personality.id);
      onClose();
      navigate('/guidance');
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullScreen={fullScreen}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: fullScreen ? 0 : 4,
          minHeight: fullScreen ? '100vh' : 'auto',
          overflow: 'hidden'
        }
      }}
    >
      <IconButton
        onClick={onClose}
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

      <DialogContent sx={{ p: { xs: 3, md: 6 }, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontFamily: 'var(--font-wisdom-body, serif)', fontWeight: 300, color: '#111', mb: 2 }}>
          Choose your path.
        </Typography>
        <Typography variant="subtitle1" sx={{ color: '#666', mb: 6, maxWidth: '600px', mx: 'auto' }}>
          Select a domain of wisdom to begin your journey immediately.
        </Typography>

        {personalityLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {DOMAIN_CONFIG.map((domain) => {
              const count = availablePersonalities.filter(p => p.domain === domain.id).length;
              return (
                <Grid size={{ xs: 12, sm: 6, md: 4 }} key={domain.id}>
                  <Card 
                    elevation={0}
                    sx={{ 
                      border: '1px solid #eaeaea',
                      borderRadius: 3,
                      transition: 'all 0.2s',
                      '&:hover': {
                        borderColor: '#222',
                        transform: 'translateY(-2px)'
                      }
                    }}
                  >
                    <CardActionArea 
                      onClick={() => handleDomainSelect(domain.id)}
                      sx={{ p: 4, height: '100%' }}
                    >
                      <Box sx={{ color: '#222', mb: 2, display: 'flex', justifyContent: 'center' }}>
                        {domain.icon}
                      </Box>
                      <Typography variant="h6" sx={{ fontFamily: 'var(--font-wisdom-ui, sans-serif)', fontWeight: 500, color: '#111' }}>
                        {domain.label}
                      </Typography>
                      {count > 0 && (
                        <Typography variant="caption" sx={{ color: '#888', display: 'block', mt: 1 }}>
                          {count} guide{count !== 1 ? 's' : ''} available
                        </Typography>
                      )}
                    </CardActionArea>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default OnboardingWizard;
