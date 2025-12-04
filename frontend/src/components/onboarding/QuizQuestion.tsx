/**
 * QuizQuestion Component
 * Individual quiz question with animated option cards
 */

import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardActionArea,
  LinearProgress,
  Fade,
  useTheme
} from '@mui/material';
import { QuizQuestion as QuestionType, QuizOption } from './types';

interface QuizQuestionProps {
  question: QuestionType;
  questionNumber: number;
  totalQuestions: number;
  selectedOptionId?: string;
  onSelectOption: (optionId: string) => void;
}

const QuizQuestionComponent: React.FC<QuizQuestionProps> = ({
  question,
  questionNumber,
  totalQuestions,
  selectedOptionId,
  onSelectOption
}) => {
  const theme = useTheme();
  const progress = ((questionNumber) / totalQuestions) * 100;

  // Map option icons based on common patterns
  const getOptionEmoji = (index: number): string => {
    const emojis = ['🌟', '💫', '✨', '🔮', '🎯'];
    return emojis[index % emojis.length];
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', px: 2 }}>
      {/* Progress indicator */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Question {questionNumber} of {totalQuestions}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {Math.round(progress)}% complete
          </Typography>
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ 
            height: 8, 
            borderRadius: 4,
            backgroundColor: `${theme.palette.primary.main}15`,
            '& .MuiLinearProgress-bar': {
              borderRadius: 4,
              background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`
            }
          }} 
        />
      </Box>

      {/* Question text */}
      <Fade in timeout={400}>
        <Typography 
          variant="h5" 
          sx={{ 
            mb: 4, 
            textAlign: 'center',
            fontWeight: 600,
            color: 'text.primary'
          }}
        >
          {question.question}
        </Typography>
      </Fade>

      {/* Options */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {question.options.map((option, index) => (
          <Fade in timeout={500 + index * 100} key={option.id}>
            <Card
              elevation={selectedOptionId === option.id ? 4 : 1}
              sx={{
                borderRadius: 3,
                border: selectedOptionId === option.id 
                  ? `2px solid ${theme.palette.primary.main}`
                  : '2px solid transparent',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: 3
                }
              }}
            >
              <CardActionArea
                onClick={() => onSelectOption(option.id)}
                sx={{ p: 2.5 }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box
                    sx={{
                      width: 44,
                      height: 44,
                      borderRadius: 2,
                      bgcolor: selectedOptionId === option.id 
                        ? `${theme.palette.primary.main}20`
                        : `${theme.palette.grey[100]}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '1.4rem',
                      transition: 'background-color 0.2s'
                    }}
                  >
                    {getOptionEmoji(index)}
                  </Box>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      flex: 1,
                      fontWeight: selectedOptionId === option.id ? 600 : 400,
                      color: selectedOptionId === option.id 
                        ? theme.palette.primary.main 
                        : 'text.primary'
                    }}
                  >
                    {option.text}
                  </Typography>
                  {selectedOptionId === option.id && (
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        bgcolor: theme.palette.primary.main,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white'
                      }}
                    >
                      ✓
                    </Box>
                  )}
                </Box>
              </CardActionArea>
            </Card>
          </Fade>
        ))}
      </Box>
    </Box>
  );
};

export default QuizQuestionComponent;
