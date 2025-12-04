/**
 * useOnboarding Hook
 * Manages onboarding state and flow
 */

import { useState, useEffect, useCallback } from 'react';
import { OnboardingState, QuizQuestion, QuizResponse, QuizResult, OnboardingStep } from './types';
import { onboardingApi } from './onboardingApi';

interface UseOnboardingResult {
  // State
  state: OnboardingState | null;
  questions: QuizQuestion[];
  quizResult: QuizResult | null;
  currentStep: OnboardingStep;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  loadOnboardingState: () => Promise<void>;
  advanceStep: () => Promise<void>;
  recordResponse: (questionId: string, optionId: string) => void;
  submitQuiz: () => Promise<void>;
  completeOnboarding: () => Promise<void>;
  skipOnboarding: () => Promise<void>;
  
  // Quiz state
  responses: QuizResponse[];
  currentQuestionIndex: number;
  goToNextQuestion: () => void;
  goToPreviousQuestion: () => void;
  isQuizComplete: boolean;
}

export function useOnboarding(userId: string): UseOnboardingResult {
  const [state, setState] = useState<OnboardingState | null>(null);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);
  const [responses, setResponses] = useState<QuizResponse[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Calculate current step
  const currentStep: OnboardingStep = state?.current_step || 'welcome';

  // Check if quiz is complete
  const isQuizComplete = questions.length > 0 && responses.length >= questions.length;

  // Load initial state and questions
  useEffect(() => {
    const initialize = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Load questions and state in parallel
        const [questionsData, stateData] = await Promise.all([
          onboardingApi.getQuizQuestions(),
          onboardingApi.getOnboardingState(userId)
        ]);
        
        setQuestions(questionsData);
        setState(stateData);
        
        // Restore any existing responses
        if (stateData.quiz_responses) {
          setResponses(stateData.quiz_responses);
        }
      } catch (err) {
        console.error('Failed to initialize onboarding:', err);
        setError('Failed to load onboarding. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    if (userId) {
      initialize();
    }
  }, [userId]);

  // Load onboarding state
  const loadOnboardingState = useCallback(async () => {
    try {
      const stateData = await onboardingApi.getOnboardingState(userId);
      setState(stateData);
    } catch (err) {
      console.error('Failed to load onboarding state:', err);
      setError('Failed to load progress.');
    }
  }, [userId]);

  // Advance to next step
  const advanceStep = useCallback(async () => {
    try {
      const newState = await onboardingApi.advanceStep(userId);
      setState(newState);
    } catch (err) {
      console.error('Failed to advance step:', err);
      setError('Failed to proceed. Please try again.');
    }
  }, [userId]);

  // Record a quiz response
  const recordResponse = useCallback((questionId: string, optionId: string) => {
    setResponses(prev => {
      // Remove any existing response for this question
      const filtered = prev.filter(r => r.question_id !== questionId);
      return [...filtered, { question_id: questionId, selected_option_id: optionId }];
    });
  }, []);

  // Submit quiz responses
  const submitQuiz = useCallback(async () => {
    if (!isQuizComplete) {
      setError('Please answer all questions before submitting.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const result = await onboardingApi.processQuizResponses(responses);
      setQuizResult(result);
      
      // Advance to next step after quiz submission
      await advanceStep();
    } catch (err) {
      console.error('Failed to submit quiz:', err);
      setError('Failed to process quiz. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [isQuizComplete, responses, advanceStep]);

  // Complete onboarding
  const completeOnboarding = useCallback(async () => {
    setIsLoading(true);
    try {
      const newState = await onboardingApi.completeOnboarding(userId);
      setState(newState);
    } catch (err) {
      console.error('Failed to complete onboarding:', err);
      setError('Failed to complete. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Skip onboarding
  const skipOnboarding = useCallback(async () => {
    setIsLoading(true);
    try {
      const newState = await onboardingApi.skipOnboarding(userId);
      setState(newState);
    } catch (err) {
      console.error('Failed to skip onboarding:', err);
      setError('Failed to skip. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Navigate quiz questions
  const goToNextQuestion = useCallback(() => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  }, [currentQuestionIndex, questions.length]);

  const goToPreviousQuestion = useCallback(() => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  }, [currentQuestionIndex]);

  return {
    // State
    state,
    questions,
    quizResult,
    currentStep,
    isLoading,
    error,
    
    // Actions
    loadOnboardingState,
    advanceStep,
    recordResponse,
    submitQuiz,
    completeOnboarding,
    skipOnboarding,
    
    // Quiz state
    responses,
    currentQuestionIndex,
    goToNextQuestion,
    goToPreviousQuestion,
    isQuizComplete
  };
}

export default useOnboarding;
