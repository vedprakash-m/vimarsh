import { Message, SpiritualChatState, Citation } from '../hooks/useSpiritualChat';

export interface ConversationSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  language: 'en' | 'hi';
  metadata: {
    messageCount: number;
    lastActivity: Date;
    topics?: string[];
    duration?: number; // in milliseconds
  };
}

export interface ConversationStorage {
  sessions: ConversationSession[];
  currentSessionId: string | null;
  preferences: {
    maxSessions: number;
    autoSaveEnabled: boolean;
    exportFormat: 'json' | 'txt' | 'pdf';
  };
}

class ConversationHistoryManager {
  private readonly STORAGE_KEY = 'vimarsh_conversation_history';
  private readonly MAX_SESSIONS_DEFAULT = 50;

  constructor() {
    this.migrateOldData();
  }

  /**
   * Get all conversation sessions
   */
  getSessions(): ConversationSession[] {
    const data = this.getStorageData();
    return data.sessions.sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
  }

  /**
   * Get a specific session by ID
   */
  getSession(sessionId: string): ConversationSession | null {
    const data = this.getStorageData();
    const session = data.sessions.find(s => s.id === sessionId);
    return session ? this.deserializeSession(session) : null;
  }

  /**
   * Create a new conversation session
   */
  createSession(language: 'en' | 'hi' = 'en'): ConversationSession {
    const newSession: ConversationSession = {
      id: this.generateSessionId(),
      title: this.generateSessionTitle(language),
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      language,
      metadata: {
        messageCount: 0,
        lastActivity: new Date(),
        topics: [],
        duration: 0
      }
    };

    this.saveSession(newSession);
    this.setCurrentSession(newSession.id);
    return newSession;
  }

  /**
   * Save or update a session
   */
  saveSession(session: ConversationSession): void {
    const data = this.getStorageData();
    const existingIndex = data.sessions.findIndex(s => s.id === session.id);
    
    const updatedSession = {
      ...session,
      updatedAt: new Date(),
      metadata: {
        ...session.metadata,
        messageCount: session.messages.length,
        lastActivity: new Date()
      }
    };

    if (existingIndex >= 0) {
      data.sessions[existingIndex] = updatedSession;
    } else {
      data.sessions.push(updatedSession);
    }

    // Limit the number of sessions
    if (data.sessions.length > data.preferences.maxSessions) {
      data.sessions = data.sessions
        .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
        .slice(0, data.preferences.maxSessions);
    }

    this.setStorageData(data);
  }

  /**
   * Update session with new messages
   */
  updateSessionMessages(sessionId: string, messages: Message[]): void {
    const session = this.getSession(sessionId);
    if (session) {
      session.messages = messages;
      session.title = this.generateSessionTitle(session.language, messages);
      this.saveSession(session);
    }
  }

  /**
   * Delete a session
   */
  deleteSession(sessionId: string): void {
    const data = this.getStorageData();
    data.sessions = data.sessions.filter(s => s.id !== sessionId);
    
    if (data.currentSessionId === sessionId) {
      data.currentSessionId = null;
    }
    
    this.setStorageData(data);
  }

  /**
   * Get current session ID
   */
  getCurrentSessionId(): string | null {
    const data = this.getStorageData();
    return data.currentSessionId;
  }

  /**
   * Set current session
   */
  setCurrentSession(sessionId: string): void {
    const data = this.getStorageData();
    data.currentSessionId = sessionId;
    this.setStorageData(data);
  }

  /**
   * Search sessions by query
   */
  searchSessions(query: string): ConversationSession[] {
    const sessions = this.getSessions();
    const lowerQuery = query.toLowerCase();
    
    return sessions.filter(session => 
      session.title.toLowerCase().includes(lowerQuery) ||
      session.messages.some(msg => 
        msg.text.toLowerCase().includes(lowerQuery)
      ) ||
      session.metadata.topics?.some(topic => 
        topic.toLowerCase().includes(lowerQuery)
      )
    );
  }

  /**
   * Export session to different formats
   */
  exportSession(sessionId: string, format: 'json' | 'txt' = 'txt'): string {
    const session = this.getSession(sessionId);
    if (!session) return '';

    if (format === 'json') {
      return JSON.stringify(session, null, 2);
    }

    // Text format
    let output = `Vimarsh Conversation - ${session.title}\n`;
    output += `Created: ${session.createdAt.toLocaleString()}\n`;
    output += `Language: ${session.language === 'hi' ? 'Hindi' : 'English'}\n`;
    output += `Messages: ${session.metadata.messageCount}\n\n`;
    output += '='.repeat(50) + '\n\n';

    session.messages.forEach((message, index) => {
      const timestamp = message.timestamp.toLocaleString();
      const sender = message.sender === 'user' ? 'You' : 'Lord Krishna';
      
      output += `[${timestamp}] ${sender}:\n`;
      output += `${message.text}\n`;
      
      if (message.citations && message.citations.length > 0) {
        output += '\nCitations:\n';
        message.citations.forEach((citation: Citation) => {
          output += `- ${citation.source} ${citation.reference}\n`;
        });
      }
      
      if (message.sanskritText) {
        output += `Sanskrit: ${message.sanskritText}\n`;
      }
      
      output += '\n' + '-'.repeat(30) + '\n\n';
    });

    return output;
  }

  /**
   * Export all sessions
   */
  exportAllSessions(format: 'json' | 'txt' = 'txt'): string {
    const sessions = this.getSessions();
    
    if (format === 'json') {
      return JSON.stringify(sessions, null, 2);
    }

    let output = 'Vimarsh Conversation History Export\n';
    output += `Exported: ${new Date().toLocaleString()}\n`;
    output += `Total Sessions: ${sessions.length}\n\n`;
    output += '='.repeat(80) + '\n\n';

    sessions.forEach((session, index) => {
      output += `Session ${index + 1}: ${session.title}\n`;
      output += this.exportSession(session.id, format);
      output += '\n' + '='.repeat(80) + '\n\n';
    });

    return output;
  }

  /**
   * Clear all conversation history
   */
  clearAllHistory(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }

  /**
   * Get storage statistics
   */
  getStorageStats(): {
    totalSessions: number;
    totalMessages: number;
    oldestSession: Date | null;
    storageSize: number;
  } {
    const sessions = this.getSessions();
    const totalMessages = sessions.reduce((sum, session) => sum + session.metadata.messageCount, 0);
    const oldestSession = sessions.length > 0 
      ? new Date(Math.min(...sessions.map(s => new Date(s.createdAt).getTime())))
      : null;
    
    const storageData = localStorage.getItem(this.STORAGE_KEY) || '';
    const storageSize = new Blob([storageData]).size;

    return {
      totalSessions: sessions.length,
      totalMessages,
      oldestSession,
      storageSize
    };
  }

  private getStorageData(): ConversationStorage {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY);
      if (data) {
        const parsed = JSON.parse(data);
        return {
          sessions: parsed.sessions || [],
          currentSessionId: parsed.currentSessionId || null,
          preferences: {
            maxSessions: parsed.preferences?.maxSessions || this.MAX_SESSIONS_DEFAULT,
            autoSaveEnabled: parsed.preferences?.autoSaveEnabled !== false,
            exportFormat: parsed.preferences?.exportFormat || 'txt'
          }
        };
      }
    } catch (error) {
      console.warn('Failed to parse conversation history from localStorage:', error);
    }

    return {
      sessions: [],
      currentSessionId: null,
      preferences: {
        maxSessions: this.MAX_SESSIONS_DEFAULT,
        autoSaveEnabled: true,
        exportFormat: 'txt'
      }
    };
  }

  private setStorageData(data: ConversationStorage): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save conversation history to localStorage:', error);
      // Could implement fallback strategies here
    }
  }

  private deserializeSession(session: any): ConversationSession {
    return {
      ...session,
      createdAt: new Date(session.createdAt),
      updatedAt: new Date(session.updatedAt),
      messages: session.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      })),
      metadata: {
        ...session.metadata,
        lastActivity: new Date(session.metadata.lastActivity)
      }
    };
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateSessionTitle(language: 'en' | 'hi', messages?: Message[]): string {
    if (messages && messages.length > 1) {
      // Extract title from first user message
      const firstUserMessage = messages.find(m => m.sender === 'user');
      if (firstUserMessage) {
        const text = firstUserMessage.text.trim();
        if (text.length > 40) {
          return text.substring(0, 40) + '...';
        }
        return text;
      }
    }

    const timestamp = new Date().toLocaleDateString();
    return language === 'hi' 
      ? `नया वार्तालाप - ${timestamp}`
      : `New Conversation - ${timestamp}`;
  }

  private migrateOldData(): void {
    // Migration logic for any old data formats
    const data = this.getStorageData();
    
    // Ensure all sessions have required metadata
    let needsUpdate = false;
    data.sessions = data.sessions.map(session => {
      if (!session.metadata) {
        needsUpdate = true;
        return {
          ...session,
          metadata: {
            messageCount: session.messages?.length || 0,
            lastActivity: new Date(session.updatedAt || session.createdAt),
            topics: [],
            duration: 0
          }
        };
      }
      return session;
    });

    if (needsUpdate) {
      this.setStorageData(data);
    }
  }
}

export const conversationHistory = new ConversationHistoryManager();
export default ConversationHistoryManager;
