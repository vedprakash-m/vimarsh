/**
 * Onboarding API Service for Vimarsh
 * Handles all API calls related to onboarding flow
 */

import axios from 'axios';
import { QuizQuestion, QuizResponse, OnboardingState, QuizResult } from './types';

const API_BASE = process.env.REACT_APP_API_URL || 'https://vimarsh-backend.azurewebsites.net/api';

export const onboardingApi = {
  /**
   * Get all quiz questions
   */
  async getQuizQuestions(): Promise<QuizQuestion[]> {
    try {
      const response = await axios.get(`${API_BASE}/onboarding/quiz/questions`);
      return response.data.questions;
    } catch (error) {
      console.error('Failed to fetch quiz questions:', error);
      throw error;
    }
  },

  /**
   * Process quiz responses and get personality recommendations
   */
  async processQuizResponses(responses: QuizResponse[]): Promise<QuizResult> {
    try {
      const response = await axios.post(`${API_BASE}/onboarding/quiz/process`, {
        responses
      });
      return response.data.result;
    } catch (error) {
      console.error('Failed to process quiz responses:', error);
      throw error;
    }
  },

  /**
   * Get current onboarding state for a user
   */
  async getOnboardingState(userId: string): Promise<OnboardingState> {
    try {
      const response = await axios.get(`${API_BASE}/onboarding/state`, {
        params: { user_id: userId }
      });
      return response.data.state;
    } catch (error) {
      console.error('Failed to get onboarding state:', error);
      throw error;
    }
  },

  /**
   * Advance to the next onboarding step
   */
  async advanceStep(userId: string): Promise<OnboardingState> {
    try {
      const response = await axios.post(`${API_BASE}/onboarding/state/advance`, {
        user_id: userId
      });
      return response.data.state;
    } catch (error) {
      console.error('Failed to advance onboarding step:', error);
      throw error;
    }
  },

  /**
   * Record a single quiz response
   */
  async recordQuizResponse(
    userId: string, 
    questionId: string, 
    selectedOptionId: string
  ): Promise<OnboardingState> {
    try {
      const response = await axios.post(`${API_BASE}/onboarding/quiz/response`, {
        user_id: userId,
        question_id: questionId,
        selected_option_id: selectedOptionId
      });
      return response.data.state;
    } catch (error) {
      console.error('Failed to record quiz response:', error);
      throw error;
    }
  },

  /**
   * Complete the onboarding flow
   */
  async completeOnboarding(userId: string): Promise<OnboardingState> {
    try {
      const response = await axios.post(`${API_BASE}/onboarding/complete`, {
        user_id: userId
      });
      return response.data.state;
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
      throw error;
    }
  },

  /**
   * Skip the onboarding flow
   */
  async skipOnboarding(userId: string): Promise<OnboardingState> {
    try {
      const response = await axios.post(`${API_BASE}/onboarding/skip`, {
        user_id: userId
      });
      return response.data.state;
    } catch (error) {
      console.error('Failed to skip onboarding:', error);
      throw error;
    }
  }
};

export default onboardingApi;
