/**
 * Memory API Client
 * 
 * Client-side API functions for interacting with the memory backend.
 * Provides typed interfaces for all memory operations.
 */

import {
  MemoryProfile,
  RelationshipState,
  SessionSummary,
  WorkingMemoryContext,
  EmotionalTone
} from '../contexts/MemoryContext';

// API configuration
const getApiBaseUrl = (): string => {
  return process.env.REACT_APP_API_BASE_URL || 'http://localhost:7071/api';
};

// Error handling
export class MemoryApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'MemoryApiError';
  }
}

// Helper for API requests
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${getApiBaseUrl()}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
  
  if (!response.ok) {
    const errorBody = await response.text();
    throw new MemoryApiError(
      `API request failed: ${response.statusText}`,
      response.status,
      errorBody
    );
  }
  
  return response.json();
}

// ============================================================================
// Memory Profile API
// ============================================================================

export interface GetProfileResponse {
  profile: MemoryProfile;
  relationships: RelationshipState[];
  stats: {
    totalConversations: number;
    totalPersonalities: number;
    averageSessionLength: number;
    primaryEmotions: string[];
    topTopics: string[];
  };
}

export interface UpdateProfileRequest {
  user_id: string;
  display_name?: string;
  life_concerns?: string[];
  spiritual_journey?: string;
  philosophical_interests?: string[];
  primary_domain?: string;
}

/**
 * Get user's memory profile with relationships and stats
 */
export async function getMemoryProfile(userId: string): Promise<GetProfileResponse> {
  return apiRequest<GetProfileResponse>(`/memory/profile?user_id=${encodeURIComponent(userId)}`);
}

/**
 * Update user's memory profile
 */
export async function updateMemoryProfile(data: UpdateProfileRequest): Promise<{ success: boolean }> {
  return apiRequest<{ success: boolean }>('/memory/update', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

// ============================================================================
// Memory Context API
// ============================================================================

export interface GetContextRequest {
  user_id: string;
  personality_id: string;
  session_id: string;
  include_history?: boolean;
}

export interface GetContextResponse {
  working_memory: WorkingMemoryContext;
  active_memories: string[];
  relationship: RelationshipState | null;
  recent_sessions: SessionSummary[];
  suggested_topics: string[];
}

/**
 * Get memory context for starting/continuing a conversation
 */
export async function getMemoryContext(request: GetContextRequest): Promise<GetContextResponse> {
  return apiRequest<GetContextResponse>('/memory/context', {
    method: 'POST',
    body: JSON.stringify(request)
  });
}

// ============================================================================
// Session Management API
// ============================================================================

export interface EndSessionRequest {
  user_id: string;
  personality_id: string;
  session_id: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
  topics: string[];
  emotional_arc: {
    start?: EmotionalTone;
    end?: EmotionalTone;
  };
}

export interface EndSessionResponse {
  success: boolean;
  summary: SessionSummary;
  relationship_update: RelationshipState;
}

/**
 * End a session and trigger summarization
 */
export async function endSession(request: EndSessionRequest): Promise<EndSessionResponse> {
  return apiRequest<EndSessionResponse>('/memory/session/end', {
    method: 'POST',
    body: JSON.stringify(request)
  });
}

// ============================================================================
// Memory Search API
// ============================================================================

export interface SearchMemoriesRequest {
  user_id: string;
  query: string;
  personality_id?: string;
  limit?: number;
  min_relevance?: number;
}

export interface SearchMemoriesResponse {
  results: Array<{
    content: string;
    relevance: number;
    source: 'conversation' | 'session_summary' | 'insight';
    timestamp: string;
    personality_id?: string;
  }>;
  total_count: number;
}

/**
 * Search user's memories semantically
 */
export async function searchMemories(request: SearchMemoriesRequest): Promise<SearchMemoriesResponse> {
  return apiRequest<SearchMemoriesResponse>('/memory/search', {
    method: 'POST',
    body: JSON.stringify(request)
  });
}

// ============================================================================
// Relationship API
// ============================================================================

export interface UpdateRelationshipRequest {
  user_id: string;
  personality_id: string;
  interaction_count?: number;
  topics_explored?: string[];
  emotional_history?: EmotionalTone[];
  insights_milestones?: string[];
}

export interface GetRelationshipResponse {
  relationship: RelationshipState;
  recent_sessions: SessionSummary[];
  shared_topics: string[];
}

/**
 * Get relationship details with a specific personality
 */
export async function getRelationship(
  userId: string,
  personalityId: string
): Promise<GetRelationshipResponse> {
  return apiRequest<GetRelationshipResponse>(
    `/memory/relationship?user_id=${encodeURIComponent(userId)}&personality_id=${encodeURIComponent(personalityId)}`
  );
}

/**
 * Update relationship with a personality
 */
export async function updateRelationship(
  request: UpdateRelationshipRequest
): Promise<{ success: boolean; relationship: RelationshipState }> {
  return apiRequest<{ success: boolean; relationship: RelationshipState }>('/memory/relationship', {
    method: 'POST',
    body: JSON.stringify(request)
  });
}

// ============================================================================
// Memory Feedback API
// ============================================================================

export interface MemoryFeedbackRequest {
  user_id: string;
  session_id: string;
  personality_id: string;
  feedback_type: 'helpful' | 'not_helpful' | 'incorrect' | 'missing_context';
  message_id?: string;
  details?: string;
}

/**
 * Submit feedback about memory quality
 */
export async function submitMemoryFeedback(
  request: MemoryFeedbackRequest
): Promise<{ success: boolean }> {
  return apiRequest<{ success: boolean }>('/memory/feedback', {
    method: 'POST',
    body: JSON.stringify(request)
  });
}

// ============================================================================
// Session History API
// ============================================================================

export interface GetSessionsRequest {
  user_id: string;
  personality_id?: string;
  limit?: number;
  offset?: number;
}

export interface GetSessionsResponse {
  sessions: SessionSummary[];
  total_count: number;
  has_more: boolean;
}

/**
 * Get session history for a user
 */
export async function getSessionHistory(request: GetSessionsRequest): Promise<GetSessionsResponse> {
  const params = new URLSearchParams({
    user_id: request.user_id,
    ...(request.personality_id && { personality_id: request.personality_id }),
    ...(request.limit && { limit: request.limit.toString() }),
    ...(request.offset && { offset: request.offset.toString() })
  });
  
  return apiRequest<GetSessionsResponse>(`/memory/sessions?${params}`);
}

// ============================================================================
// Memory Health API
// ============================================================================

export interface MemoryHealthResponse {
  status: 'healthy' | 'degraded' | 'unavailable';
  latency_ms: number;
  features: {
    semantic_search: boolean;
    session_summarization: boolean;
    relationship_tracking: boolean;
  };
}

/**
 * Check memory service health
 */
export async function checkMemoryHealth(): Promise<MemoryHealthResponse> {
  try {
    return await apiRequest<MemoryHealthResponse>('/memory/health');
  } catch {
    return {
      status: 'unavailable',
      latency_ms: 0,
      features: {
        semantic_search: false,
        session_summarization: false,
        relationship_tracking: false
      }
    };
  }
}

// Export all functions
export const memoryApi = {
  getMemoryProfile,
  updateMemoryProfile,
  getMemoryContext,
  endSession,
  searchMemories,
  getRelationship,
  updateRelationship,
  submitMemoryFeedback,
  getSessionHistory,
  checkMemoryHealth
};

export default memoryApi;
