/**
 * Memory Context Provider for Vimarsh
 * 
 * Manages the hierarchical memory state across the application,
 * providing memory-aware conversation capabilities.
 * 
 * Features:
 * - 4-layer memory state (Working, Core, Episodic, Semantic)
 * - Relationship tracking with personalities
 * - Memory-enhanced guidance requests
 * - Session management
 */

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

// Memory layer types
export type RelationshipDepth = 'stranger' | 'acquaintance' | 'familiar' | 'trusted' | 'kindred';
export type EmotionalTone = 'curious' | 'seeking' | 'troubled' | 'hopeful' | 'grateful' | 'peaceful' | 'inspired' | 'reflective' | 'uncertain' | 'determined' | 'frustrated' | 'joyful' | 'sad' | 'anxious' | 'calm' | 'neutral';

// Core memory profile interface
export interface MemoryProfile {
  userId: string;
  displayName?: string;
  lifeConcerns: string[];
  spiritualJourney: string;
  philosophicalInterests: string[];
  primaryDomain: string;
  createdAt: string;
  lastActiveAt: string;
  totalSessions: number;
  totalMessages: number;
}

// Relationship with a personality
export interface RelationshipState {
  personalityId: string;
  userId: string;
  depth: RelationshipDepth;
  interactionCount: number;
  lastInteraction: string;
  topicsExplored: string[];
  emotionalHistory: EmotionalTone[];
  insightsMilestones: string[];
  trustIndicators: number;
}

// Session summary from episodic memory
export interface SessionSummary {
  id: string;
  personalityId: string;
  sessionStart: string;
  sessionEnd: string;
  messageCount: number;
  summary: string;
  keyInsights: string[];
  emotionalArc: {
    start: EmotionalTone;
    end: EmotionalTone;
    journey: string;
  };
  topicsDiscussed: string[];
  userReflection?: string;
}

// Working memory context for current session
export interface WorkingMemoryContext {
  sessionId: string;
  personalityId: string;
  currentTopics: string[];
  emotionalState: EmotionalTone;
  recentMessages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    importance?: number;
  }>;
  activeMemories: string[];
  tokenCount: number;
}

// Memory-aware request to backend
export interface MemoryGuidanceRequest {
  query: string;
  personalityId: string;
  sessionId: string;
  userId: string;
  includeMemoryContext: boolean;
  emotionalState?: EmotionalTone;
  currentTopics?: string[];
}

// Memory context state
interface MemoryContextState {
  // Profile & relationships
  memoryProfile: MemoryProfile | null;
  relationships: Map<string, RelationshipState>;
  
  // Session state
  currentSession: WorkingMemoryContext | null;
  recentSessions: SessionSummary[];
  
  // Loading states
  isLoading: boolean;
  isMemoryEnabled: boolean;
  memoryError: string | null;
  
  // Memory stats for dashboard
  memoryStats: {
    totalConversations: number;
    totalPersonalities: number;
    averageSessionLength: number;
    primaryEmotions: string[];
    topTopics: string[];
  };
}

// Context type with actions
interface MemoryContextType extends MemoryContextState {
  // Core actions
  loadMemoryProfile: (userId: string) => Promise<void>;
  startSession: (personalityId: string, sessionId: string) => Promise<void>;
  endSession: () => Promise<void>;
  
  // Memory updates
  updateWorkingMemory: (message: { role: 'user' | 'assistant'; content: string }) => void;
  updateEmotionalState: (emotion: EmotionalTone) => void;
  addTopic: (topic: string) => void;
  
  // Relationship tracking
  getRelationship: (personalityId: string) => RelationshipState | null;
  updateRelationship: (personalityId: string, updates: Partial<RelationshipState>) => void;
  
  // Memory search
  searchMemories: (query: string, personalityId?: string) => Promise<string[]>;
  
  // Session management
  getRecentSessions: (personalityId: string, limit?: number) => SessionSummary[];
  
  // Memory context for requests
  getMemoryContext: () => WorkingMemoryContext | null;
  
  // Dashboard helpers
  getRelationshipDepthLabel: (depth: RelationshipDepth) => string;
  getRelationshipProgress: (personalityId: string) => number;
}

const MemoryContext = createContext<MemoryContextType | undefined>(undefined);

interface MemoryProviderProps {
  children: ReactNode;
}

// Helper to get API base URL
const getApiBaseUrl = (): string => {
  return process.env.REACT_APP_API_BASE_URL || 'http://localhost:7071/api';
};

// Relationship depth labels
const DEPTH_LABELS: Record<RelationshipDepth, string> = {
  stranger: 'New Seeker',
  acquaintance: 'Beginning Journey',
  familiar: 'Growing Understanding',
  trusted: 'Deep Connection',
  kindred: 'Spiritual Kinship'
};

// Relationship depth thresholds
const DEPTH_THRESHOLDS: Record<RelationshipDepth, number> = {
  stranger: 0,
  acquaintance: 3,
  familiar: 10,
  trusted: 25,
  kindred: 50
};

export const MemoryProvider: React.FC<MemoryProviderProps> = ({ children }) => {
  // State
  const [memoryProfile, setMemoryProfile] = useState<MemoryProfile | null>(null);
  const [relationships, setRelationships] = useState<Map<string, RelationshipState>>(new Map());
  const [currentSession, setCurrentSession] = useState<WorkingMemoryContext | null>(null);
  const [recentSessions, setRecentSessions] = useState<SessionSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isMemoryEnabled, setIsMemoryEnabled] = useState(true);
  const [memoryError, setMemoryError] = useState<string | null>(null);
  const [memoryStats, setMemoryStats] = useState({
    totalConversations: 0,
    totalPersonalities: 0,
    averageSessionLength: 0,
    primaryEmotions: [] as string[],
    topTopics: [] as string[]
  });

  // Load memory profile from backend or localStorage
  const loadMemoryProfile = useCallback(async (userId: string) => {
    if (!userId) return;
    
    setIsLoading(true);
    setMemoryError(null);
    
    try {
      const response = await fetch(`${getApiBaseUrl()}/memory/profile?user_id=${userId}`, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMemoryProfile(data.profile);
        
        // Load relationships if included
        if (data.relationships) {
          const relMap = new Map<string, RelationshipState>();
          data.relationships.forEach((rel: RelationshipState) => {
            relMap.set(rel.personalityId, rel);
          });
          setRelationships(relMap);
        }
        
        // Update stats
        if (data.stats) {
          setMemoryStats(data.stats);
        }
        
        setIsMemoryEnabled(true);
      } else if (response.status === 404) {
        // Create new profile
        const newProfile: MemoryProfile = {
          userId,
          lifeConcerns: [],
          spiritualJourney: '',
          philosophicalInterests: [],
          primaryDomain: 'spiritual',
          createdAt: new Date().toISOString(),
          lastActiveAt: new Date().toISOString(),
          totalSessions: 0,
          totalMessages: 0
        };
        setMemoryProfile(newProfile);
      } else {
        console.warn('Memory service unavailable, using local state');
        setIsMemoryEnabled(false);
      }
    } catch (error) {
      console.error('Failed to load memory profile:', error);
      setMemoryError('Memory service unavailable');
      setIsMemoryEnabled(false);
      
      // Try localStorage fallback
      const cached = localStorage.getItem(`vimarsh_memory_${userId}`);
      if (cached) {
        try {
          setMemoryProfile(JSON.parse(cached));
        } catch (e) {
          console.error('Failed to parse cached memory:', e);
        }
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Start a new session
  const startSession = useCallback(async (personalityId: string, sessionId: string) => {
    const newSession: WorkingMemoryContext = {
      sessionId,
      personalityId,
      currentTopics: [],
      emotionalState: 'curious',
      recentMessages: [],
      activeMemories: [],
      tokenCount: 0
    };
    
    setCurrentSession(newSession);
    
    // Try to fetch relevant memories from backend
    if (memoryProfile && isMemoryEnabled) {
      try {
        const response = await fetch(`${getApiBaseUrl()}/memory/context`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            user_id: memoryProfile.userId,
            personality_id: personalityId,
            session_id: sessionId
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.active_memories) {
            setCurrentSession(prev => prev ? {
              ...prev,
              activeMemories: data.active_memories
            } : null);
          }
        }
      } catch (error) {
        console.warn('Failed to load session context:', error);
      }
    }
  }, [memoryProfile, isMemoryEnabled]);

  // End current session
  const endSession = useCallback(async () => {
    if (!currentSession || !memoryProfile) {
      setCurrentSession(null);
      return;
    }
    
    // Send session end to backend for summarization
    if (isMemoryEnabled) {
      try {
        await fetch(`${getApiBaseUrl()}/memory/session/end`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            user_id: memoryProfile.userId,
            personality_id: currentSession.personalityId,
            session_id: currentSession.sessionId,
            messages: currentSession.recentMessages,
            topics: currentSession.currentTopics,
            emotional_arc: {
              end: currentSession.emotionalState
            }
          })
        });
      } catch (error) {
        console.warn('Failed to end session properly:', error);
      }
    }
    
    // Cache to localStorage
    try {
      localStorage.setItem(`vimarsh_memory_${memoryProfile.userId}`, JSON.stringify(memoryProfile));
    } catch (e) {
      console.error('Failed to cache memory:', e);
    }
    
    setCurrentSession(null);
  }, [currentSession, memoryProfile, isMemoryEnabled]);

  // Update working memory with new message
  const updateWorkingMemory = useCallback((message: { role: 'user' | 'assistant'; content: string }) => {
    setCurrentSession(prev => {
      if (!prev) return null;
      
      const newMessage = {
        ...message,
        timestamp: new Date().toISOString()
      };
      
      // Keep last 20 messages in working memory
      const updatedMessages = [...prev.recentMessages, newMessage].slice(-20);
      
      // Estimate token count (rough approximation)
      const tokenCount = updatedMessages.reduce((sum, m) => sum + Math.ceil(m.content.length / 4), 0);
      
      return {
        ...prev,
        recentMessages: updatedMessages,
        tokenCount
      };
    });
  }, []);

  // Update emotional state
  const updateEmotionalState = useCallback((emotion: EmotionalTone) => {
    setCurrentSession(prev => prev ? { ...prev, emotionalState: emotion } : null);
  }, []);

  // Add topic to current session
  const addTopic = useCallback((topic: string) => {
    setCurrentSession(prev => {
      if (!prev) return null;
      const topics = new Set([...prev.currentTopics, topic]);
      return { ...prev, currentTopics: Array.from(topics).slice(-10) };
    });
  }, []);

  // Get relationship with personality
  const getRelationship = useCallback((personalityId: string): RelationshipState | null => {
    return relationships.get(personalityId) || null;
  }, [relationships]);

  // Update relationship
  const updateRelationship = useCallback((personalityId: string, updates: Partial<RelationshipState>) => {
    setRelationships(prev => {
      const newMap = new Map(prev);
      const existing = newMap.get(personalityId) || {
        personalityId,
        userId: memoryProfile?.userId || '',
        depth: 'stranger' as RelationshipDepth,
        interactionCount: 0,
        lastInteraction: new Date().toISOString(),
        topicsExplored: [],
        emotionalHistory: [],
        insightsMilestones: [],
        trustIndicators: 0
      };
      
      const updated = { ...existing, ...updates };
      
      // Auto-update depth based on interaction count
      if (updated.interactionCount >= DEPTH_THRESHOLDS.kindred) {
        updated.depth = 'kindred';
      } else if (updated.interactionCount >= DEPTH_THRESHOLDS.trusted) {
        updated.depth = 'trusted';
      } else if (updated.interactionCount >= DEPTH_THRESHOLDS.familiar) {
        updated.depth = 'familiar';
      } else if (updated.interactionCount >= DEPTH_THRESHOLDS.acquaintance) {
        updated.depth = 'acquaintance';
      }
      
      newMap.set(personalityId, updated);
      return newMap;
    });
    
    // Persist to backend asynchronously
    if (isMemoryEnabled && memoryProfile) {
      fetch(`${getApiBaseUrl()}/memory/relationship`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: memoryProfile.userId,
          personality_id: personalityId,
          ...updates
        })
      }).catch(e => console.warn('Failed to persist relationship:', e));
    }
  }, [memoryProfile, isMemoryEnabled]);

  // Search memories
  const searchMemories = useCallback(async (query: string, personalityId?: string): Promise<string[]> => {
    if (!memoryProfile || !isMemoryEnabled) return [];
    
    try {
      const response = await fetch(`${getApiBaseUrl()}/memory/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: memoryProfile.userId,
          query,
          personality_id: personalityId,
          limit: 5
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.results || [];
      }
    } catch (error) {
      console.warn('Memory search failed:', error);
    }
    
    return [];
  }, [memoryProfile, isMemoryEnabled]);

  // Get recent sessions for a personality
  const getRecentSessions = useCallback((personalityId: string, limit = 5): SessionSummary[] => {
    return recentSessions
      .filter(s => s.personalityId === personalityId)
      .slice(0, limit);
  }, [recentSessions]);

  // Get current memory context
  const getMemoryContext = useCallback((): WorkingMemoryContext | null => {
    return currentSession;
  }, [currentSession]);

  // Get relationship depth label
  const getRelationshipDepthLabel = useCallback((depth: RelationshipDepth): string => {
    return DEPTH_LABELS[depth];
  }, []);

  // Get relationship progress (0-100)
  const getRelationshipProgress = useCallback((personalityId: string): number => {
    const rel = relationships.get(personalityId);
    if (!rel) return 0;
    
    const maxThreshold = DEPTH_THRESHOLDS.kindred;
    return Math.min(100, (rel.interactionCount / maxThreshold) * 100);
  }, [relationships]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (currentSession) {
        // Best effort cleanup
        endSession();
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const contextValue: MemoryContextType = {
    // State
    memoryProfile,
    relationships,
    currentSession,
    recentSessions,
    isLoading,
    isMemoryEnabled,
    memoryError,
    memoryStats,
    
    // Actions
    loadMemoryProfile,
    startSession,
    endSession,
    updateWorkingMemory,
    updateEmotionalState,
    addTopic,
    getRelationship,
    updateRelationship,
    searchMemories,
    getRecentSessions,
    getMemoryContext,
    getRelationshipDepthLabel,
    getRelationshipProgress
  };

  return (
    <MemoryContext.Provider value={contextValue}>
      {children}
    </MemoryContext.Provider>
  );
};

// Custom hook for using memory context
export const useMemory = (): MemoryContextType => {
  const context = useContext(MemoryContext);
  if (!context) {
    throw new Error('useMemory must be used within a MemoryProvider');
  }
  return context;
};

// Export context for testing
export { MemoryContext };
