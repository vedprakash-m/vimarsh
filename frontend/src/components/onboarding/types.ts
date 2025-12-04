/**
 * Onboarding Types for Vimarsh
 * Type definitions for the onboarding wizard flow
 */

export type OnboardingStep = 
  | 'welcome'
  | 'quiz'
  | 'first_chat'
  | 'discovery'
  | 'complete';

export interface QuizQuestion {
  id: string;
  question: string;
  options: QuizOption[];
}

export interface QuizOption {
  id: string;
  text: string;
  domain_weights: Record<string, number>;
}

export interface QuizResponse {
  question_id: string;
  selected_option_id: string;
}

export interface DomainScore {
  domain: string;
  score: number;
  label: string;
}

export interface PersonalityMatch {
  personality_id: string;
  name: string;
  domain: string;
  description: string;
  match_score: number;
  match_reason: string;
}

export interface OnboardingState {
  current_step: OnboardingStep;
  completed_steps: OnboardingStep[];
  quiz_responses: QuizResponse[];
  recommended_personalities: PersonalityMatch[];
  selected_personality?: string;
  started_at: string;
  updated_at: string;
  is_complete: boolean;
  was_skipped: boolean;
}

export interface QuizResult {
  domain_scores: DomainScore[];
  recommended_personality: PersonalityMatch;
  alternative_matches: PersonalityMatch[];
  personality_reasoning: string;
}
