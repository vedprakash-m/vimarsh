/**
 * useMemoryAwareChat Hook
 * 
 * Provides memory-enhanced chat functionality that integrates
 * with the hierarchical memory system for contextual conversations.
 * 
 * Features:
 * - Automatic memory context injection
 * - Session lifecycle management
 * - Relationship tracking updates
 * - Emotional state detection
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useMemory, EmotionalTone, RelationshipDepth } from '../contexts/MemoryContext';

// Simple UUID v4 implementation to avoid external dependency
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Message type for chat
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  citations?: string[];
  emotionalTone?: EmotionalTone;
  memoryRelevance?: number;
}

// Chat options
export interface MemoryAwareChatOptions {
  userId: string;
  personalityId: string;
  onSessionStart?: (sessionId: string) => void;
  onSessionEnd?: (summary: string) => void;
  onRelationshipUpdate?: (depth: RelationshipDepth) => void;
  enableEmotionDetection?: boolean;
}

// Hook return type
export interface MemoryAwareChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  relationshipDepth: RelationshipDepth;
  currentEmotion: EmotionalTone;
  sessionDuration: number;
  messageCount: number;
  
  // Actions
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  startNewSession: () => Promise<void>;
  endCurrentSession: () => Promise<void>;
  setEmotion: (emotion: EmotionalTone) => void;
}

// API base URL
const getApiUrl = () => process.env.REACT_APP_API_BASE_URL || 'http://localhost:7071/api';

/**
 * Memory-aware chat hook that enhances conversations with memory context
 */
export function useMemoryAwareChat(options: MemoryAwareChatOptions): MemoryAwareChatState {
  const {
    userId,
    personalityId,
    onSessionStart,
    onSessionEnd,
    onRelationshipUpdate,
    enableEmotionDetection = true
  } = options;
  
  // Memory context
  const memory = useMemory();
  
  // Local state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentEmotion, setCurrentEmotion] = useState<EmotionalTone>('curious');
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  
  // Refs for cleanup
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // Derived state
  const relationship = memory.getRelationship(personalityId);
  const relationshipDepth: RelationshipDepth = relationship?.depth || 'stranger';
  const sessionDuration = sessionStartTime 
    ? Math.floor((Date.now() - sessionStartTime.getTime()) / 1000 / 60) 
    : 0;
  
  // Start new session
  const startNewSession = useCallback(async () => {
    const newSessionId = generateUUID();
    setSessionId(newSessionId);
    setMessages([]);
    setError(null);
    setSessionStartTime(new Date());
    
    // Initialize memory session
    await memory.startSession(personalityId, newSessionId);
    
    onSessionStart?.(newSessionId);
    
    console.log(`🧠 Started memory-aware session: ${newSessionId}`);
  }, [personalityId, memory, onSessionStart]);
  
  // End current session
  const endCurrentSession = useCallback(async () => {
    if (!sessionId) return;
    
    // Update relationship
    const currentRel = memory.getRelationship(personalityId);
    memory.updateRelationship(personalityId, {
      interactionCount: (currentRel?.interactionCount || 0) + messages.length,
      lastInteraction: new Date().toISOString(),
      topicsExplored: [...(currentRel?.topicsExplored || []), ...(memory.currentSession?.currentTopics || [])],
      emotionalHistory: [...(currentRel?.emotionalHistory || []), currentEmotion]
    });
    
    // End memory session (triggers summarization)
    await memory.endSession();
    
    onSessionEnd?.('Session ended');
    onRelationshipUpdate?.(memory.getRelationship(personalityId)?.depth || 'stranger');
    
    setSessionId(null);
    setSessionStartTime(null);
    
    console.log(`🧠 Ended memory-aware session`);
  }, [sessionId, messages.length, personalityId, memory, currentEmotion, onSessionEnd, onRelationshipUpdate]);
  
  // Send message with memory context
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;
    
    // Ensure session exists
    if (!sessionId) {
      await startNewSession();
    }
    
    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    
    // Create user message
    const userMessage: ChatMessage = {
      id: generateUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
      emotionalTone: currentEmotion
    };
    
    // Create loading placeholder
    const loadingMessage: ChatMessage = {
      id: generateUUID(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true
    };
    
    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);
    setError(null);
    
    // Update working memory
    memory.updateWorkingMemory({ role: 'user', content });
    
    try {
      // Get memory context for enhanced request
      const memoryContext = memory.getMemoryContext();
      
      // Build request with memory context
      const requestBody = {
        query: content,
        personality: personalityId,
        session_id: sessionId,
        user_id: userId,
        // Memory-enhanced fields
        include_memory: true,
        memory_context: memoryContext ? {
          topics: memoryContext.currentTopics,
          emotional_state: memoryContext.emotionalState,
          active_memories: memoryContext.activeMemories,
          relationship_depth: relationshipDepth
        } : undefined
      };
      
      const response = await fetch(`${getApiUrl()}/guidance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody),
        signal: abortControllerRef.current.signal
      });
      
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Extract response and metadata
      const responseContent = data.guidance || data.response || data.message || 'I understand your question. Let me reflect...';
      const citations = data.citations || [];
      const detectedEmotion = data.emotional_tone as EmotionalTone | undefined;
      const topics = data.topics || [];
      
      // Update assistant message
      const assistantMessage: ChatMessage = {
        id: loadingMessage.id,
        role: 'assistant',
        content: responseContent,
        timestamp: new Date(),
        isLoading: false,
        citations,
        emotionalTone: detectedEmotion || 'calm'
      };
      
      setMessages(prev => prev.map(m => 
        m.id === loadingMessage.id ? assistantMessage : m
      ));
      
      // Update memory with response
      memory.updateWorkingMemory({ role: 'assistant', content: responseContent });
      
      // Update topics from response
      topics.forEach((topic: string) => memory.addTopic(topic));
      
      // Update emotional state if detected
      if (enableEmotionDetection && detectedEmotion) {
        setCurrentEmotion(detectedEmotion);
        memory.updateEmotionalState(detectedEmotion);
      }
      
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        console.log('Request aborted');
        return;
      }
      
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorMessage);
      
      // Update loading message with error
      setMessages(prev => prev.map(m => 
        m.id === loadingMessage.id 
          ? { ...m, content: 'I apologize, but I encountered an issue. Please try again.', isLoading: false }
          : m
      ));
      
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [
    sessionId,
    isLoading,
    userId,
    personalityId,
    relationshipDepth,
    currentEmotion,
    memory,
    enableEmotionDetection,
    startNewSession
  ]);
  
  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);
  
  // Set emotion manually
  const setEmotion = useCallback((emotion: EmotionalTone) => {
    setCurrentEmotion(emotion);
    memory.updateEmotionalState(emotion);
  }, [memory]);
  
  // Initialize session on mount if not exists
  useEffect(() => {
    if (userId && personalityId && !sessionId) {
      startNewSession();
    }
    
    // Cleanup on unmount
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [userId, personalityId]); // eslint-disable-line react-hooks/exhaustive-deps
  
  // End session on personality change
  useEffect(() => {
    return () => {
      if (sessionId) {
        endCurrentSession();
      }
    };
  }, [personalityId]); // eslint-disable-line react-hooks/exhaustive-deps
  
  return {
    messages,
    isLoading,
    error,
    sessionId,
    relationshipDepth,
    currentEmotion,
    sessionDuration,
    messageCount: messages.filter(m => m.role === 'user').length,
    
    sendMessage,
    clearMessages,
    startNewSession,
    endCurrentSession,
    setEmotion
  };
}

export default useMemoryAwareChat;
