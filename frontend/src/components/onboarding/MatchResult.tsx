/**
 * MatchResult Component
 * Displays personality match result with animations
 */

import React from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Chip,
  Fade,
  Grow,
  useTheme,
  Avatar
} from '@mui/material';
import { Sparkles, MessageCircle, ChevronRight } from 'lucide-react';
import { QuizResult, DomainScore } from './types';

interface MatchResultProps {
  result: QuizResult;
  onStartConversation: (personalityId: string) => void;
  onExploreMore: () => void;
}

// Domain icons mapping
const domainIcons: Record<string, string> = {
  spiritual: '🕉️',
  scientific: '🔬',
  philosophical: '💭',
  leadership: '🏛️',
  literary: '📚',
  psychology: '🧠'
};

// Domain colors mapping
const domainColors: Record<string, string> = {
  spiritual: '#FF9800',
  scientific: '#2196F3',
  philosophical: '#9C27B0',
  leadership: '#4CAF50',
  literary: '#E91E63',
  psychology: '#00BCD4'
};

const MatchResult: React.FC<MatchResultProps> = ({
  result,
  onStartConversation,
  onExploreMore
}) => {
  const theme = useTheme();
  const { recommended_personality, domain_scores, alternative_matches, personality_reasoning } = result;

  // Sort domain scores by value
  const sortedScores = [...domain_scores].sort((a, b) => b.score - a.score);
  const topDomain = sortedScores[0];

  return (
    <Box
      sx={{
        maxWidth: 700,
        mx: 'auto',
        px: 3,
        py: 4
      }}
    >
      {/* Celebration header */}
      <Grow in timeout={500}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Box
            sx={{
              width: 64,
              height: 64,
              mx: 'auto',
              mb: 2,
              borderRadius: '50%',
              bgcolor: `${domainColors[recommended_personality.domain]}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'celebrate 0.6s ease-out'
            }}
          >
            <Sparkles size={32} color={domainColors[recommended_personality.domain]} />
          </Box>
          <Typography variant="h5" fontWeight={600} gutterBottom>
            Your Perfect Guide Found!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Based on your answers, we've found your ideal wisdom companion
          </Typography>
        </Box>
      </Grow>

      {/* Main match card */}
      <Fade in timeout={800}>
        <Paper
          elevation={4}
          sx={{
            p: 4,
            borderRadius: 4,
            mb: 4,
            background: `linear-gradient(135deg, ${domainColors[recommended_personality.domain]}10, ${domainColors[recommended_personality.domain]}05)`,
            border: `2px solid ${domainColors[recommended_personality.domain]}40`
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 3 }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                bgcolor: domainColors[recommended_personality.domain],
                fontSize: '2.5rem'
              }}
            >
              {domainIcons[recommended_personality.domain]}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" fontWeight={700} gutterBottom>
                {recommended_personality.name}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Chip
                  label={recommended_personality.domain.charAt(0).toUpperCase() + recommended_personality.domain.slice(1)}
                  size="small"
                  sx={{
                    bgcolor: `${domainColors[recommended_personality.domain]}20`,
                    color: domainColors[recommended_personality.domain],
                    fontWeight: 600
                  }}
                />
                <Chip
                  label={`${Math.round(recommended_personality.match_score * 100)}% Match`}
                  size="small"
                  color="success"
                  sx={{ fontWeight: 600 }}
                />
              </Box>
            </Box>
          </Box>

          <Typography variant="body1" sx={{ mb: 3 }}>
            {recommended_personality.description}
          </Typography>

          <Paper
            sx={{
              p: 2,
              bgcolor: 'background.paper',
              borderRadius: 2,
              mb: 3
            }}
          >
            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
              "{personality_reasoning}"
            </Typography>
          </Paper>

          <Button
            variant="contained"
            fullWidth
            size="large"
            onClick={() => onStartConversation(recommended_personality.personality_id)}
            startIcon={<MessageCircle size={20} />}
            sx={{
              py: 1.5,
              borderRadius: 3,
              fontSize: '1.1rem',
              fontWeight: 600,
              bgcolor: domainColors[recommended_personality.domain],
              '&:hover': {
                bgcolor: domainColors[recommended_personality.domain],
                filter: 'brightness(0.9)'
              }
            }}
          >
            Start Conversation with {recommended_personality.name}
          </Button>
        </Paper>
      </Fade>

      {/* Domain scores */}
      <Fade in timeout={1000}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Your Wisdom Profile
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            {sortedScores.slice(0, 4).map((score, index) => (
              <Box key={score.domain} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography sx={{ fontSize: '1.2rem', width: 30 }}>
                  {domainIcons[score.domain]}
                </Typography>
                <Typography variant="body2" sx={{ width: 100, fontWeight: index === 0 ? 600 : 400 }}>
                  {score.label}
                </Typography>
                <Box
                  sx={{
                    flex: 1,
                    height: 8,
                    bgcolor: 'grey.200',
                    borderRadius: 4,
                    overflow: 'hidden'
                  }}
                >
                  <Box
                    sx={{
                      width: `${score.score * 100}%`,
                      height: '100%',
                      bgcolor: domainColors[score.domain],
                      borderRadius: 4,
                      transition: 'width 0.5s ease-out'
                    }}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ width: 40 }}>
                  {Math.round(score.score * 100)}%
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>
      </Fade>

      {/* Alternative matches */}
      {alternative_matches && alternative_matches.length > 0 && (
        <Fade in timeout={1200}>
          <Box sx={{ mb: 4 }}>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>
              Also Great For You
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {alternative_matches.slice(0, 3).map((match) => (
                <Paper
                  key={match.personality_id}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    flex: '1 1 150px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: 3
                    }
                  }}
                  onClick={() => onStartConversation(match.personality_id)}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                    <Typography fontSize="1.4rem">
                      {domainIcons[match.domain]}
                    </Typography>
                    <Typography variant="subtitle2" fontWeight={600}>
                      {match.name}
                    </Typography>
                  </Box>
                  <Chip
                    label={`${Math.round(match.match_score * 100)}% Match`}
                    size="small"
                    variant="outlined"
                  />
                </Paper>
              ))}
            </Box>
          </Box>
        </Fade>
      )}

      {/* Explore more button */}
      <Fade in timeout={1400}>
        <Button
          variant="text"
          fullWidth
          onClick={onExploreMore}
          endIcon={<ChevronRight size={18} />}
          sx={{ color: 'text.secondary' }}
        >
          Explore all 25 personalities
        </Button>
      </Fade>

      {/* Animation styles */}
      <style>
        {`
          @keyframes celebrate {
            0% { transform: scale(0); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
          }
        `}
      </style>
    </Box>
  );
};

export default MatchResult;
