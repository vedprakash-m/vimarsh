import { useState, useCallback, useRef, useEffect } from 'react';
import { conversationHistory, ConversationSession } from '../utils/conversationHistory';
import { API_BASE_URL } from '../config/environment';
import { getAuthHeaders } from '../auth/authService';

// Debug log
console.log('useSpiritualChat - API_BASE_URL:', API_BASE_URL);

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  citations?: Citation[];
  sanskritText?: string;
  transliteration?: string;
  confidence?: number;
  isLoading?: boolean;
}

export interface Citation {
  source: string;
  reference: string;
  verse?: string;
  chapter?: string;
  book?: string;
}

export interface ChatError {
  message: string;
  code: string;
  timestamp: Date;
}

export interface SpiritualChatState {
  messages: Message[];
  isLoading: boolean;
  error: ChatError | null;
  currentSessionId: string;
  isConnected: boolean;
}

interface SpiritualChatConfig {
  apiBaseUrl?: string;
  language?: 'en' | 'hi';
  autoSave?: boolean;
  maxRetries?: number;
  timeout?: number;
  sessionId?: string; // Allow loading a specific session
  personalityId?: string; // Personality to use for responses
}

const DEFAULT_CONFIG: SpiritualChatConfig = {
  apiBaseUrl: API_BASE_URL,
  language: 'en',
  autoSave: true,
  maxRetries: 3,
  timeout: 30000
};

export const useSpiritualChat = (config: SpiritualChatConfig = {}) => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  
  const [state, setState] = useState<SpiritualChatState>({
    messages: [],
    isLoading: false,
    error: null,
    currentSessionId: config.sessionId || generateSessionId(),
    isConnected: true
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const retryCountRef = useRef<number>(0);

  // Load session on mount or when sessionId changes
  useEffect(() => {
    if (config.sessionId) {
      // Load existing session
      const session = conversationHistory.getSession(config.sessionId);
      if (session) {
        setState(prev => ({
          ...prev,
          messages: session.messages,
          currentSessionId: session.id
        }));
        conversationHistory.setCurrentSession(session.id);
        return;
      }
    }

    // Create new session or initialize with welcome message
    initializeNewSession();
  }, [config.sessionId, finalConfig.language]);

  // Auto-save messages when they change
  useEffect(() => {
    if (finalConfig.autoSave && state.messages.length > 0 && state.currentSessionId) {
      // Skip auto-save if this is just the welcome message
      const hasUserMessages = state.messages.some(m => m.sender === 'user');
      if (hasUserMessages) {
        conversationHistory.updateSessionMessages(state.currentSessionId, state.messages);
      }
    }
  }, [state.messages, state.currentSessionId, finalConfig.autoSave]);

  // Initialize new session
  const initializeNewSession = useCallback(() => {
    const welcomeMessage: Message = {
      id: 'welcome-' + Date.now(),
      text: finalConfig.language === 'hi' 
        ? 'नमस्ते! मैं आपकी आध्यात्मिक यात्रा में मार्गदर्शन करने के लिए यहाँ हूँ। आप मुझसे कोई भी प्रश्न पूछ सकते हैं।'
        : 'Namaste! I am here to guide you on your spiritual journey. Ask me any question about dharma, life, or spiritual practice.',
      sender: 'ai',
      timestamp: new Date(),
      sanskritText: 'नमस्ते! धर्मे अर्थे काम मोक्षे च सर्वत्र अहं सह आपकी।',
      citations: []
    };

    const sessionId = config.sessionId || generateSessionId();
    
    setState(prev => ({
      ...prev,
      messages: [welcomeMessage],
      currentSessionId: sessionId
    }));

    // Create session in history if auto-save enabled
    if (finalConfig.autoSave) {
      const session = conversationHistory.createSession(finalConfig.language);
      if (session && session.id) {
        setState(prev => ({
          ...prev,
          currentSessionId: session.id
        }));
      }
    }
  }, [finalConfig.language, finalConfig.autoSave, config.sessionId]);

  // Generate unique session ID
  function generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Clear error after some time
  useEffect(() => {
    if (state.error) {
      const timer = setTimeout(() => {
        setState(prev => ({ ...prev, error: null }));
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [state.error]);

  const setError = useCallback((error: string, code: string = 'UNKNOWN_ERROR') => {
    setState(prev => ({
      ...prev,
      error: {
        message: error,
        code,
        timestamp: new Date()
      },
      isLoading: false
    }));
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, newMessage]
    }));

    return newMessage.id;
  }, []);

  const updateMessage = useCallback((messageId: string, updates: Partial<Message>) => {
    setState(prev => ({
      ...prev,
      messages: prev.messages.map(msg => 
        msg.id === messageId ? { ...msg, ...updates } : msg
      )
    }));
  }, []);

  const sendMessage = useCallback(async (text: string): Promise<void> => {
    if (!text.trim()) return;

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Add user message
    const userMessageId = addMessage({
      text: text.trim(),
      sender: 'user'
    });

    // Add loading AI message
    const aiMessageId = addMessage({
      text: '',
      sender: 'ai',
      isLoading: true
    });

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // Create new abort controller for this request
      abortControllerRef.current = new AbortController();
      
      const apiUrl = `${finalConfig.apiBaseUrl}/spiritual_guidance`;
      
      // Get authentication headers
      const authHeaders = await getAuthHeaders();
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders
        },
        body: JSON.stringify({
          query: text.trim(),
          language: finalConfig.language === 'hi' ? 'Hindi' : 'English',
          user_id: `user-${Date.now()}`,
          include_citations: true,
          voice_enabled: false,
          personality_id: finalConfig.personalityId || 'krishna'
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Update AI message with actual response
      updateMessage(aiMessageId, {
        text: data.response || 'I apologize, but I could not provide a proper response at this time.',
        citations: data.citations || [],
        sanskritText: data.sanskritText,
        transliteration: data.transliteration,
        confidence: data.confidence,
        isLoading: false
      });

      retryCountRef.current = 0; // Reset retry count on success

    } catch (error: any) {
      console.error('Error sending message:', error);

      // Handle different types of errors
      if (error.name === 'AbortError') {
        // Request was cancelled, remove loading message
        setState(prev => ({
          ...prev,
          messages: prev.messages.filter(msg => msg.id !== aiMessageId),
          isLoading: false
        }));
        return;
      }

      // Implement retry logic
      if (retryCountRef.current < (finalConfig.maxRetries || 3)) {
        retryCountRef.current++;
        updateMessage(aiMessageId, {
          text: `Seeking wisdom... (attempt ${retryCountRef.current}/${finalConfig.maxRetries})`,
          isLoading: true
        });
        
        // Retry after delay
        setTimeout(() => {
          sendMessage(text);
        }, 1000 * retryCountRef.current);
        return;
      }

      // Final failure - show fallback response
      updateMessage(aiMessageId, {
        text: finalConfig.language === 'hi' 
          ? 'क्षमा करें, इस समय मैं आपका उत्तर नहीं दे सकता। कृपया बाद में पुनः प्रयास करें।'
          : 'I apologize, but I am unable to provide guidance at this moment. Please try again later.',
        isLoading: false,
        citations: []
      });

      setError(
        finalConfig.language === 'hi'
          ? 'सेवा में अस्थायी व्यवधान है। कृपया पुनः प्रयास करें।'
          : 'There was an issue connecting to the wisdom guidance service. Please try again.',
        'NETWORK_ERROR'
      );
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
      abortControllerRef.current = null;
    }
  }, [finalConfig, state.currentSessionId, state.messages, addMessage, updateMessage, setError]);

  const clearChat = useCallback(() => {
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    initializeNewSession();
  }, [initializeNewSession]);

  const newConversation = useCallback(() => {
    const session = conversationHistory.createSession(finalConfig.language);
    setState(prev => ({
      ...prev,
      messages: [createWelcomeMessage()],
      currentSessionId: session.id,
      error: null,
      isLoading: false
    }));
    return session.id;
  }, [finalConfig.language]);

  const loadSession = useCallback((sessionId: string) => {
    const session = conversationHistory.getSession(sessionId);
    if (session) {
      setState(prev => ({
        ...prev,
        messages: session.messages,
        currentSessionId: session.id,
        error: null,
        isLoading: false
      }));
      conversationHistory.setCurrentSession(session.id);
      return true;
    }
    return false;
  }, []);

  const createWelcomeMessage = (): Message => ({
    id: 'welcome-' + Date.now(),
    text: finalConfig.language === 'hi' 
      ? 'नमस्ते! मैं आपकी आध्यात्मिक यात्रा में मार्गदर्शन करने के लिए यहाँ हूँ। आप मुझसे कोई भी प्रश्न पूछ सकते हैं।'
      : 'Namaste! I am here to guide you on your spiritual journey. Ask me any question about dharma, life, or spiritual practice.',
    sender: 'ai',
    timestamp: new Date(),
    sanskritText: 'नमस्ते! धर्मे अर्थे काम मोक्षे च सर्वत्र अहं सह आपकी।',
    citations: []
  });

  const exportChat = useCallback((): string => {
    const chatExport = {
      sessionId: state.currentSessionId,
      timestamp: new Date().toISOString(),
      language: finalConfig.language,
      messages: state.messages.map(msg => ({
        text: msg.text,
        sender: msg.sender,
        timestamp: msg.timestamp.toISOString(),
        citations: msg.citations,
        sanskritText: msg.sanskritText
      }))
    };

    return JSON.stringify(chatExport, null, 2);
  }, [state, finalConfig.language]);

  const exportConversation = useCallback(() => {
    return {
      sessionId: state.currentSessionId,
      timestamp: new Date().toISOString(),
      language: finalConfig.language,
      messages: state.messages.map(msg => ({
        text: msg.text,
        sender: msg.sender,
        timestamp: msg.timestamp.toISOString(),
        citations: msg.citations,
        sanskritText: msg.sanskritText
      }))
    };
  }, [state, finalConfig.language]);

  const startNewSession = useCallback(() => {
    const newSessionId = `session-${Date.now()}`;
    setState(prev => ({
      ...prev,
      currentSessionId: newSessionId,
      messages: [createWelcomeMessage()]
    }));
  }, []);

  const cancelCurrentRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setState(prev => ({
      ...prev,
      isLoading: false
    }));
  }, []);

  const getLastAIMessage = useCallback((): Message | null => {
    const aiMessages = state.messages.filter(msg => msg.sender === 'ai' && !msg.isLoading);
    return aiMessages.length > 0 ? aiMessages[aiMessages.length - 1] : null;
  }, [state.messages]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    // State
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    isConnected: state.isConnected,
    sessionId: state.currentSessionId,

    // Actions
    sendMessage,
    clearChat,
    clearError,
    addMessage,
    updateMessage,
    newConversation,
    loadSession,
    startNewSession,
    cancelCurrentRequest,

    // Utilities
    exportChat,
    exportConversation,
    getLastAIMessage,

    // Stats
    messageCount: state.messages.length,
    conversationStarted: state.messages.length > 1
  };
};
