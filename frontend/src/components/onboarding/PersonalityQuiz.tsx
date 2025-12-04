/**
 * PersonalityQuiz Component
 * Multi-question quiz flow with navigation
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  IconButton,
  Fade,
  useTheme
} from '@mui/material';
import { ArrowLeft, ArrowRight, Check } from 'lucide-react';
import QuizQuestion from './QuizQuestion';
import { QuizQuestion as QuestionType, QuizResponse } from './types';

interface PersonalityQuizProps {
  questions: QuestionType[];
  responses: QuizResponse[];
  onRecordResponse: (questionId: string, optionId: string) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
}

const PersonalityQuiz: React.FC<PersonalityQuizProps> = ({
  questions,
  responses,
  onRecordResponse,
  onSubmit,
  isSubmitting = false
}) => {
  const theme = useTheme();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showNavigation, setShowNavigation] = useState(true);

  const currentQuestion = questions[currentIndex];
  const currentResponse = responses.find(r => r.question_id === currentQuestion?.id);
  const isLastQuestion = currentIndex === questions.length - 1;
  const allAnswered = questions.every(q => 
    responses.some(r => r.question_id === q.id)
  );

  // Auto-advance to next question after selection
  useEffect(() => {
    if (currentResponse && !isLastQuestion) {
      const timer = setTimeout(() => {
        setCurrentIndex(prev => prev + 1);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [currentResponse, isLastQuestion]);

  const handleSelectOption = (optionId: string) => {
    onRecordResponse(currentQuestion.id, optionId);
  };

  const goToPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const goToNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  if (!currentQuestion) {
    return null;
  }

  return (
    <Box
      sx={{
        minHeight: '70vh',
        display: 'flex',
        flexDirection: 'column',
        py: 4
      }}
    >
      {/* Question content */}
      <Box sx={{ flex: 1, display: 'flex', alignItems: 'center' }}>
        <Fade in key={currentQuestion.id} timeout={300}>
          <Box sx={{ width: '100%' }}>
            <QuizQuestion
              question={currentQuestion}
              questionNumber={currentIndex + 1}
              totalQuestions={questions.length}
              selectedOptionId={currentResponse?.selected_option_id}
              onSelectOption={handleSelectOption}
            />
          </Box>
        </Fade>
      </Box>

      {/* Navigation */}
      {showNavigation && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            maxWidth: 600,
            mx: 'auto',
            px: 2,
            mt: 4,
            width: '100%'
          }}
        >
          <IconButton
            onClick={goToPrevious}
            disabled={currentIndex === 0}
            sx={{
              bgcolor: 'background.paper',
              boxShadow: 1,
              '&:hover': { bgcolor: 'background.paper' },
              '&:disabled': { opacity: 0.3 }
            }}
          >
            <ArrowLeft size={20} />
          </IconButton>

          {/* Question dots */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            {questions.map((q, index) => {
              const isAnswered = responses.some(r => r.question_id === q.id);
              const isCurrent = index === currentIndex;
              
              return (
                <Box
                  key={q.id}
                  onClick={() => setCurrentIndex(index)}
                  sx={{
                    width: isCurrent ? 24 : 8,
                    height: 8,
                    borderRadius: 4,
                    bgcolor: isCurrent 
                      ? theme.palette.primary.main 
                      : isAnswered 
                        ? `${theme.palette.primary.main}60`
                        : theme.palette.grey[300],
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                />
              );
            })}
          </Box>

          {isLastQuestion && currentResponse ? (
            <Button
              variant="contained"
              onClick={onSubmit}
              disabled={!allAnswered || isSubmitting}
              endIcon={<Check size={18} />}
              sx={{
                borderRadius: 3,
                px: 3,
                background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`
              }}
            >
              {isSubmitting ? 'Finding match...' : 'See Results'}
            </Button>
          ) : (
            <IconButton
              onClick={goToNext}
              disabled={!currentResponse || isLastQuestion}
              sx={{
                bgcolor: 'background.paper',
                boxShadow: 1,
                '&:hover': { bgcolor: 'background.paper' },
                '&:disabled': { opacity: 0.3 }
              }}
            >
              <ArrowRight size={20} />
            </IconButton>
          )}
        </Box>
      )}
    </Box>
  );
};

export default PersonalityQuiz;
