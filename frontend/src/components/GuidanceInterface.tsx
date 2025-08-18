import React, { useState, useEffect } from 'react';
import { Send, MessageSquare, Users, Settings, LogOut, Download, X } from 'lucide-react';
// Voice functionality temporarily disabled - imports kept for future implementation
// import { Mic, MicOff } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import PersonalitySelector from './PersonalitySelector';
import ServiceStatusIndicator from './ServiceStatusIndicator';
import { usePersonality, Personality } from '../contexts/PersonalityContext';
import { useAdmin } from '../contexts/AdminProviderContext';
import { useAppLoading } from '../contexts/AppLoadingContext';
import { useNavigate } from 'react-router-dom';
import { getApiBaseUrl } from '../config/environment';
import { getAuthHeaders, authService } from '../auth/authService';
import DebugAuth from './DebugAuth';
import { pwaManager } from '../utils/pwa';
import '../styles/vimarsh-design-system.css';
import '../styles/spiritual-theme.css';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  personality?: string;
  metadata?: {
    response_source?: 'gemini_ai' | 'template_fallback' | 'hardcoded_fallback' | 'hybrid_rag' | 'simple_rag';
    ai_generated?: boolean;
    service_mode?: 'enhanced' | 'standard' | 'fallback';
    fallback_reason?: string;
    circuit_breaker_status?: {
      state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
      failure_count: number;
      last_failure_time?: string;
    };
    reliability_stats?: {
      success_rate: number;
      total_attempts: number;
      template_fallback_count: number;
    };
    generation_time_ms?: number;
    memory_enhanced?: boolean;
  };
}

// Compact Message Source Badge for chat interface
interface MessageSourceBadgeProps {
  metadata: NonNullable<Message['metadata']>;
  compact?: boolean;
}

const MessageSourceBadge: React.FC<MessageSourceBadgeProps> = ({ metadata, compact = true }) => {
  const getSourceInfo = () => {
    const isAI = metadata.ai_generated === true;
    const source = metadata.response_source;
    
    if (isAI && source === 'gemini_ai') {
      return {
        icon: '🤖',
        label: 'AI',
        color: 'rgba(59, 130, 246, 0.7)',
        bgColor: 'rgba(59, 130, 246, 0.1)'
      };
    }
    
    if (source === 'template_fallback' || source === 'hardcoded_fallback') {
      return {
        icon: '📜',
        label: 'Traditional',
        color: 'rgba(245, 158, 11, 0.7)',
        bgColor: 'rgba(245, 158, 11, 0.1)'
      };
    }
    
    if (source === 'hybrid_rag' || source === 'simple_rag') {
      return {
        icon: '📚',
        label: 'Enhanced',
        color: 'rgba(147, 51, 234, 0.7)',
        bgColor: 'rgba(147, 51, 234, 0.1)'
      };
    }
    
    return {
      icon: '🎭',
      label: 'Wisdom',
      color: 'rgba(107, 114, 128, 0.7)',
      bgColor: 'rgba(107, 114, 128, 0.1)'
    };
  };
  
  const sourceInfo = getSourceInfo();
  
  if (compact) {
    return (
      <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.25rem',
        padding: '0.25rem 0.5rem',
        backgroundColor: sourceInfo.bgColor,
        border: `1px solid ${sourceInfo.color}`,
        borderRadius: '0.5rem',
        fontSize: '0.7rem',
        color: sourceInfo.color
      }}>
        <span>{sourceInfo.icon}</span>
        <span>{sourceInfo.label}</span>
        {metadata.generation_time_ms && (
          <span style={{ opacity: 0.7 }}>
            {metadata.generation_time_ms}ms
          </span>
        )}
      </div>
    );
  }
  
  return (
    <div style={{
      padding: '0.5rem',
      backgroundColor: sourceInfo.bgColor,
      border: `1px solid ${sourceInfo.color}`,
      borderRadius: '0.5rem',
      fontSize: '0.8rem',
      color: sourceInfo.color
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span>{sourceInfo.icon}</span>
        <span>{sourceInfo.label} Response</span>
        {metadata.generation_time_ms && (
          <span style={{ opacity: 0.7 }}>
            ({metadata.generation_time_ms}ms)
          </span>
        )}
      </div>
      {metadata.fallback_reason && (
        <div style={{ fontSize: '0.7rem', opacity: 0.8, marginTop: '0.25rem' }}>
          Reason: {metadata.fallback_reason}
        </div>
      )}
    </div>
  );
};

export default function GuidanceInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const navigate = useNavigate();

  // Context hooks
  const { user } = useAdmin();
  const { isInitializing, allReady } = useAppLoading();

  // Don't show admin button until all contexts are ready to prevent layout shift
  const showAdminButton = allReady && user?.isAdmin;

  // Debug toggle for production troubleshooting
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Ctrl/Cmd + Shift + D to toggle debug
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        setShowDebug(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  // Logout functionality
  const handleLogout = async () => {
    try {
      await authService.logout();
      // Navigate to login page or reload to trigger authentication flow
      window.location.href = '/';
    } catch (error) {
      console.error('Logout failed:', error);
      // Still navigate away even if logout fails
      window.location.href = '/';
    }
  };  // Add animation styles
  useEffect(() => {
    const styles = `
      @keyframes pulse {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 1; }
      }
    `;
    
    if (!document.getElementById('pulse-animation')) {
      const styleSheet = document.createElement('style');
      styleSheet.id = 'pulse-animation';
      styleSheet.textContent = styles;
      document.head.appendChild(styleSheet);
    }
  }, []);
  const [isListening, setIsListening] = useState(false);
  const [showPersonalitySelector, setShowPersonalitySelector] = useState(false);
  
  // PWA install prompt state
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [canInstall, setCanInstall] = useState(false);
  
  // Use PersonalityContext instead of local state
  const { 
    selectedPersonality, 
    setSelectedPersonality, 
    availablePersonalities, 
    personalityLoading,
    loadPersonalities 
  } = usePersonality();

  // Load personalities on component mount if not already loaded
  useEffect(() => {
    if (availablePersonalities.length === 0 && !personalityLoading) {
      loadPersonalities();
    }
  }, [availablePersonalities.length, personalityLoading, loadPersonalities]);

  // Auto-show personality selector if no personality is selected and personalities are loaded
  useEffect(() => {
    if (availablePersonalities.length > 0 && !selectedPersonality && !personalityLoading) {
      setShowPersonalitySelector(true);
    }
  }, [availablePersonalities.length, selectedPersonality, personalityLoading]);

  // Check for PWA install prompt availability
  useEffect(() => {
    const checkInstallPrompt = () => {
      const installAvailable = pwaManager.canInstall();
      setCanInstall(installAvailable);
      
      // Show install prompt on mobile after user has been active for 30 seconds
      if (installAvailable && window.innerWidth <= 768) {
        setTimeout(() => {
          setShowInstallPrompt(true);
        }, 30000);
      }
    };
    
    checkInstallPrompt();
  }, []);

  const handlePersonalitySelect = (personality: Personality) => {
    setSelectedPersonality(personality);
    setShowPersonalitySelector(false);
    // Clear messages when switching personality to provide fresh context
    setMessages([]);
  };

  // PWA install prompt handlers
  const handleInstallApp = async () => {
    try {
      await pwaManager.showInstallPrompt();
      setShowInstallPrompt(false);
    } catch (error) {
      console.error('Install prompt failed:', error);
    }
  };

  const dismissInstallPrompt = () => {
    setShowInstallPrompt(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading || !selectedPersonality) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const question = inputText;
    setInputText('');
    setIsLoading(true);

    try {
      // Get conversation context (last 4 messages for context)
      const recentMessages = messages.slice(-4).map(msg => ({
        role: msg.isUser ? 'user' : 'assistant',
        content: msg.text
      }));

      // Call real guidance API with conversation context
      const apiUrl = getApiBaseUrl();
      const authHeaders = await getAuthHeaders();
      const response = await fetch(`${apiUrl}/guidance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders
        },
        body: JSON.stringify({
          query: question,
          language: 'English',
          include_citations: true,
          voice_enabled: false,
          conversation_context: recentMessages,
          personality_id: selectedPersonality.id,
          user_id: sessionId,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Use the response with metadata from backend
      const apiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        personality: selectedPersonality.id,
        metadata: data.metadata // Include the gap remediation metadata
      };
      
      setMessages(prev => [...prev, apiResponse]);
      
    } catch (error) {
      console.error('Error calling guidance API:', error);
      
      // Fallback response for errors
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: "🤔 I'm having trouble connecting to the guidance service. Please check your connection and try again. (Frontend Error)",
        isUser: false,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate domain-appropriate placeholder text
  const getPlaceholderText = () => {
    if (!selectedPersonality) {
      return "Please choose a guide first...";
    }
    
    const domainPlaceholders = {
      spiritual: "Ask your spiritual question...",
      scientific: "Ask your scientific question...",
      historical: "Ask your historical question...", 
      philosophical: "Ask your philosophical question...",
      literary: "Ask your literary question..."
    };
    
    return domainPlaceholders[selectedPersonality.domain as keyof typeof domainPlaceholders] || "Ask your question...";
  };

  // Dynamic quick prompts based on selected personality
  const getQuickPrompts = () => {
    if (!selectedPersonality) {
      return [
        "How can I find my dharma and live according to my true purpose?",
        "How can I maintain equanimity during life's ups and downs?",
        "What are the different paths of yoga and which one suits me?",
        "How do I overcome anger and jealousy through spiritual practice?"
      ];
    }

    // First check for specific personality-based questions
    const personalityId = selectedPersonality.id?.toLowerCase() || selectedPersonality.name?.toLowerCase();
    
    switch (personalityId) {
      case 'jesus':
      case 'jesus christ':
        return [
          "How can I show love and compassion to those who have hurt me?",
          "What does it mean to carry my cross in daily life?",
          "How do I find hope and peace during times of suffering?",
          "How can I serve others and live according to God's will?"
        ];
      
      case 'krishna':
      case 'lord krishna':
        return [
          "How can I find my dharma and live according to my true purpose?",
          "How can I maintain equanimity during life's ups and downs?",
          "What are the different paths of yoga and which one suits me?",
          "How do I overcome anger and jealousy through spiritual practice?"
        ];
      
      case 'buddha':
      case 'gautama buddha':
        return [
          "How can I find freedom from suffering and attachment?",
          "What is the path to mindfulness and inner peace?",
          "How do I cultivate compassion for all living beings?",
          "How can I understand the nature of impermanence?"
        ];
      
      case 'einstein':
      case 'albert einstein':
        return [
          "How does the theory of relativity change our understanding of time and space?",
          "What is the relationship between energy and matter in the universe?",
          "How do we approach scientific discovery and overcome preconceived notions?",
          "What role does imagination play in scientific breakthroughs?"
        ];
      
      case 'lincoln':
      case 'abraham lincoln':
      case 'abraham_lincoln':
        return [
          "What lessons can we learn from leadership during times of crisis?",
          "How do we build unity and preserve democracy in challenging times?",
          "What role does character play in effective governance?",
          "How do we balance justice with compassion in difficult decisions?"
        ];
      
      case 'aurelius':
      case 'marcus aurelius':
        return [
          "How do we cultivate virtue and wisdom in daily life?",
          "What is the relationship between reason and emotion in decision-making?",
          "How do we find meaning and purpose in the face of adversity?",
          "What does it mean to live according to nature and cosmic order?"
        ];
      
      case 'rumi':
        return [
          "How do I open my heart to divine love and connection?",
          "What is the spiritual meaning behind life's joys and sorrows?",
          "How do I find unity with the divine through mystical experience?",
          "How can poetry and beauty lead me to spiritual truth?"
        ];
      
      case 'laotzu':
      case 'lao tzu':
        return [
          "How do I find balance and harmony in the natural flow of life?",
          "What does it mean to act through wu wei (effortless action)?",
          "How do I cultivate simplicity and humility in modern life?",
          "What is the Way and how do I align with it?"
        ];
      
      default:
        // Fall back to domain-based questions if personality not found
        switch (selectedPersonality.domain) {
          case 'scientific':
            return [
              "How does the theory of relativity change our understanding of time and space?",
              "What is the relationship between energy and matter in the universe?",
              "How do we approach scientific discovery and overcome preconceived notions?",
              "What role does imagination play in scientific breakthroughs?"
            ];
          case 'historical':
            return [
              "What lessons can we learn from leadership during times of crisis?",
              "How do we build unity and preserve democracy in challenging times?",
              "What role does character play in effective governance?",
              "How do we balance justice with compassion in difficult decisions?"
            ];
          case 'philosophical':
            return [
              "How do we cultivate virtue and wisdom in daily life?",
              "What is the relationship between reason and emotion in decision-making?",
              "How do we find meaning and purpose in the face of adversity?",
              "What does it mean to live according to nature and cosmic order?"
            ];
          case 'literary':
            return [
              "How does literature help us understand the human condition?",
              "What is the relationship between beauty and truth in art?",
              "How do stories shape our understanding of morality and ethics?",
              "What role does creativity play in personal transformation?"
            ];
          case 'spiritual':
          default:
            return [
              "How can I find my dharma and live according to my true purpose?",
              "How can I maintain equanimity during life's ups and downs?",
              "What are the different paths of yoga and which one suits me?",
              "How do I overcome anger and jealousy through spiritual practice?"
            ];
        }
    }
  };

  const quickPrompts = getQuickPrompts();

  return (
    <div style={{
      minHeight: '100vh',
      background: '#ffffff',
      color: '#1d1d1f',
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Mobile-Optimized Header */}
      <header style={{
        padding: window.innerWidth <= 768 ? '1rem 1.5rem' : '1.5rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: '#ffffff',
        borderBottom: '1px solid #e5e7eb',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: window.innerWidth <= 768 ? '0.5rem' : '0.75rem' 
        }}>
          <div style={{
            width: window.innerWidth <= 768 ? '2.5rem' : '3rem',
            height: window.innerWidth <= 768 ? '2.5rem' : '3rem',
            background: 'linear-gradient(135deg, #f97316, #f59e0b)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: window.innerWidth <= 768 ? '1.25rem' : '1.5rem',
            fontWeight: 'bold',
            color: 'white',
            boxShadow: '0 4px 12px rgba(249, 115, 22, 0.3)'
          }}>
            V
          </div>
          {window.innerWidth > 480 && (
            <div>
              <h1 style={{ 
                margin: 0, 
                fontSize: window.innerWidth <= 768 ? '1.25rem' : '1.5rem', 
                fontWeight: '600',
                color: '#1d1d1f'
              }}>
                Vimarsh
              </h1>
              <p style={{ 
                margin: 0, 
                fontSize: window.innerWidth <= 768 ? '0.75rem' : '0.85rem', 
                fontWeight: '500',
                color: '#6e6e73'
              }}>
                Wisdom Without Boundaries
              </p>
            </div>
          )}
        </div>
        
        {/* Mobile-Responsive Personality Info & Toggle */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: window.innerWidth <= 768 ? '0.5rem' : '1rem' 
        }}>
          {selectedPersonality && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: window.innerWidth <= 768 ? '0.5rem' : '0.75rem',
              padding: window.innerWidth <= 768 ? '0.375rem 0.75rem' : '0.5rem 1rem',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              backdropFilter: 'blur(10px)',
              maxWidth: window.innerWidth <= 768 ? '120px' : 'none',
              overflow: 'hidden'
            }}>
              <div style={{ 
                fontSize: window.innerWidth <= 768 ? '0.8rem' : '0.9rem', 
                fontWeight: '600',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}>
                {selectedPersonality?.name || 'Loading...'}
              </div>
              {window.innerWidth > 480 && (
                <div style={{ 
                  fontSize: window.innerWidth <= 768 ? '0.65rem' : '0.75rem', 
                  opacity: 0.7,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  {selectedPersonality?.domain === 'spiritual' ? 'SPIRITUAL' :
                   selectedPersonality?.domain === 'scientific' ? 'SCIENTIFIC' :
                   selectedPersonality?.domain === 'historical' ? 'HISTORICAL' :
                   selectedPersonality?.domain === 'philosophical' ? 'PHILOSOPHICAL' :
                   selectedPersonality?.domain === 'literary' ? 'LITERARY' :
                   selectedPersonality?.domain === 'leadership' ? 'LEADERSHIP' :
                   selectedPersonality?.domain === 'psychology' ? 'PSYCHOLOGY' :
                   'SPIRITUAL'}
                </div>
              )}
            </div>
          )}
          <button 
            onClick={() => setShowPersonalitySelector(!showPersonalitySelector)}
            style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              color: '#1e293b',
              padding: window.innerWidth <= 768 ? '0.5rem' : '0.5rem',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              transition: 'all 0.2s ease',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
            }}
            title="Change Personality"
            disabled={!selectedPersonality}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#f1f5f9';
              e.currentTarget.style.borderColor = '#cbd5e1';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#f8fafc';
              e.currentTarget.style.borderColor = '#e2e8f0';
            }}
          >
            <Users size={18} />
          </button>
          
          {/* Admin Panel Button - Only visible to admin users after full initialization */}
          {showAdminButton && (
            <button 
              onClick={() => navigate('/admin')}
              style={{
                background: '#f8fafc',
                border: '1px solid #fbbf24',
                color: '#92400e',
                padding: '0.5rem 1rem',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                transition: 'all 0.2s ease',
                fontSize: '0.9rem',
                fontWeight: '600',
                gap: '0.5rem',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
              }}
              title="Admin Panel"
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#fef9c3';
                e.currentTarget.style.borderColor = '#f59e0b';
                e.currentTarget.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#f8fafc';
                e.currentTarget.style.borderColor = '#fbbf24';
                e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
              }}
            >
              ⚙️ Admin
            </button>
          )}
          
          {/* Logout Button */}
          <button 
            onClick={handleLogout}
            style={{
              background: '#f8fafc',
              border: '1px solid #ef4444',
              color: '#991b1b',
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              transition: 'all 0.2s ease',
              fontSize: '0.9rem',
              fontWeight: '600',
              gap: '0.5rem',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
            }}
            title="Logout"
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#fef2f2';
              e.currentTarget.style.borderColor = '#dc2626';
              e.currentTarget.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#f8fafc';
              e.currentTarget.style.borderColor = '#ef4444';
              e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
            }}
          >
            <LogOut size={18} />
            Logout
          </button>
          {/* Voice functionality temporarily hidden until fully implemented */}
          {/* 
          <button
            onClick={() => setIsListening(!isListening)}
            style={{
              background: isListening ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.2)',
              border: `1px solid ${isListening ? 'rgba(239, 68, 68, 0.3)' : 'rgba(255, 255, 255, 0.3)'}`,
              color: 'white',
              padding: '0.5rem',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              transition: 'all 0.3s ease'
            }}
          >
            {isListening ? <MicOff size={18} /> : <Mic size={18} />}
          </button>
          */}
        </div>
      </header>

      {/* PWA Install Prompt */}
      {showInstallPrompt && canInstall && (
        <div style={{
          position: 'fixed',
          top: '80px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: '#ffffff',
          color: '#1e293b',
          padding: window.innerWidth <= 768 ? '1rem' : '1.5rem',
          borderRadius: '12px',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.1)',
          zIndex: 200,
          maxWidth: window.innerWidth <= 768 ? '90vw' : '400px',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <Download size={24} color="#FF6B35" />
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '600' }}>Install Vimarsh</h3>
            <button
              onClick={dismissInstallPrompt}
              style={{
                marginLeft: 'auto',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '4px',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center'
              }}
            >
              <X size={18} color="#666" />
            </button>
          </div>
          <p style={{ 
            margin: '0 0 1rem 0', 
            fontSize: '0.9rem', 
            lineHeight: '1.4',
            color: '#555'
          }}>
            Install Vimarsh as an app for faster access and a better mobile experience. Get spiritual guidance anytime, even offline.
          </p>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={handleInstallApp}
              style={{
                flex: 1,
                background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
                color: 'white',
                border: 'none',
                padding: '0.75rem',
                borderRadius: '8px',
                fontSize: '0.9rem',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'transform 0.2s ease'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              Install Now
            </button>
            <button
              onClick={dismissInstallPrompt}
              style={{
                background: 'transparent',
                color: '#666',
                border: '1px solid #ddd',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                fontSize: '0.9rem',
                cursor: 'pointer'
              }}
            >
              Later
            </button>
          </div>
        </div>
      )}

      {/* Personality Selector Modal */}
      {showPersonalitySelector && (
        <PersonalitySelector
          availablePersonalities={availablePersonalities}
          selectedPersonalityId={selectedPersonality?.id}
          onPersonalitySelect={handlePersonalitySelect}
          onClose={() => setShowPersonalitySelector(false)}
          showAsDialog={true}
        />
      )}

      {/* System Status Indicator - Admin Only */}
      {user?.role === 'admin' && (
        <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '1rem 2rem 0' }}>
          <ServiceStatusIndicator compact={true} className="mb-4" />
        </div>
      )}

      {/* Mobile-Optimized Main Content */}
      <div style={{
        maxWidth: window.innerWidth <= 768 ? '100%' : '1000px',
        margin: '0 auto',
        padding: window.innerWidth <= 768 ? '0.75rem 1rem' : '1rem 2rem',
        minHeight: window.innerWidth <= 768 ? 'calc(100vh - 120px)' : 'calc(100vh - 140px)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Mobile-Optimized Welcome Section */}
        {messages.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: window.innerWidth <= 768 ? '1rem 0.5rem' : '2rem 1rem',
            marginBottom: window.innerWidth <= 768 ? '0.5rem' : '1rem'
          }}>
            <div style={{
              fontSize: window.innerWidth <= 768 ? '2.5rem' : '4rem',
              marginBottom: window.innerWidth <= 768 ? '0.5rem' : '1rem'
            }}>🏵️</div>
            
            {!selectedPersonality ? (
              <>
                <h2 style={{
                  fontSize: window.innerWidth <= 768 ? '1.75rem' : '2.5rem',
                  fontWeight: '700',
                  marginBottom: window.innerWidth <= 768 ? '0.5rem' : '1rem',
                  lineHeight: '1.2',
                  color: '#1e293b'
                }}>Welcome to Vimarsh</h2>
                <p style={{
                  fontSize: window.innerWidth <= 768 ? '1rem' : '1.25rem',
                  maxWidth: window.innerWidth <= 768 ? '100%' : '600px',
                  margin: window.innerWidth <= 768 ? '0 auto 1rem' : '0 auto 2rem',
                  lineHeight: window.innerWidth <= 768 ? '1.4' : '1.6',
                  padding: window.innerWidth <= 768 ? '0 0.5rem' : '0',
                  color: '#475569'
                }}>
                  <strong>Wisdom Without Boundaries</strong><br/>
                  Choose your wisdom guide to begin your journey of knowledge and insight.
                </p>
                <button
                  onClick={() => setShowPersonalitySelector(true)}
                  style={{
                    background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
                    border: 'none',
                    color: 'white',
                    padding: '1rem 2rem',
                    borderRadius: '0.75rem',
                    fontSize: '1.1rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    boxShadow: '0 2px 8px rgba(255, 107, 53, 0.2)',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-1px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(255, 107, 53, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.3)';
                  }}
                >
                  Choose Your Wisdom Guide
                </button>
              </>
            ) : (
              <>
                <h2 style={{
                  fontSize: window.innerWidth <= 768 ? '1.5rem' : '2.5rem',
                  fontWeight: '700',
                  marginBottom: window.innerWidth <= 768 ? '0.5rem' : '1rem',
                  textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
                  lineHeight: '1.2'
                }}>Welcome to Your {selectedPersonality.domain === 'spiritual' ? 'Spiritual' :
                  selectedPersonality.domain === 'scientific' ? 'Scientific' :
                  selectedPersonality.domain === 'historical' ? 'Historical' :
                  selectedPersonality.domain === 'philosophical' ? 'Philosophical' :
                  selectedPersonality.domain === 'literary' ? 'Literary' :
                  selectedPersonality.domain === 'leadership' ? 'Leadership' :
                  selectedPersonality.domain === 'psychology' ? 'Psychology' :
                  'Spiritual'} Journey</h2>
                <p style={{
                  fontSize: window.innerWidth <= 768 ? '0.95rem' : '1.25rem',
                  maxWidth: window.innerWidth <= 768 ? '100%' : '600px',
                  margin: window.innerWidth <= 768 ? '0 auto 0.75rem' : '0 auto 1rem',
                  lineHeight: '1.6',
                  color: '#475569'
                }}>
                  {selectedPersonality.domain === 'spiritual' 
                    ? 'Ask questions about spirituality, philosophy, and find wisdom from ancient teachings with' 
                    : selectedPersonality.domain === 'scientific'
                    ? 'Explore the mysteries of the universe and scientific discoveries with'
                    : selectedPersonality.domain === 'historical'
                    ? 'Learn from history\'s great leaders and their timeless wisdom with'
                    : selectedPersonality.domain === 'philosophical'
                    ? 'Contemplate life\'s deepest questions and philosophical insights with'
                    : selectedPersonality.domain === 'literary'
                    ? 'Discover the beauty and wisdom found in great literature with'
                    : selectedPersonality.domain === 'leadership'
                    ? 'Learn about leadership, governance, and strategic thinking with'
                    : selectedPersonality.domain === 'psychology'
                    ? 'Explore the human mind, behavior, and psychological insights with'
                    : 'Ask questions about spirituality, philosophy, and find wisdom from ancient teachings with'}{' '}
                  <strong>{selectedPersonality.name}</strong>.
                </p>
                <p style={{
                  fontSize: '1rem',
                  marginBottom: '2rem',
                  fontStyle: 'italic',
                  color: '#64748b'
                }}>
                  {selectedPersonality.description}
                </p>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: window.innerWidth <= 768 ? '1fr' : 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: window.innerWidth <= 768 ? '0.75rem' : '1rem',
                  maxWidth: window.innerWidth <= 768 ? '100%' : '800px',
                  margin: '0 auto'
                }}>
                  {quickPrompts.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => setInputText(prompt)}
                      style={{
                        background: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        color: '#334155',
                        padding: '1rem',
                        borderRadius: '0.75rem',
                        cursor: 'pointer',
                        textAlign: 'left',
                        fontSize: '0.9rem',
                        lineHeight: '1.4',
                        transition: 'all 0.2s ease',
                        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#f1f5f9';
                        e.currentTarget.style.borderColor = '#cbd5e1';
                        e.currentTarget.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.1)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#f8fafc';
                        e.currentTarget.style.borderColor = '#e2e8f0';
                        e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
                      }}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

        {/* Mobile-Optimized Messages */}
        <div style={{
          flex: '1',
          marginBottom: window.innerWidth <= 768 ? '1rem' : '2rem',
          overflowY: 'auto'
        }}>
          {messages.map((message) => (
            <div key={message.id} style={{
              display: 'flex',
              justifyContent: message.isUser ? 'flex-end' : 'flex-start',
              marginBottom: window.innerWidth <= 768 ? '0.75rem' : '1rem'
            }}>
              <div style={{
                maxWidth: window.innerWidth <= 768 ? '85%' : '70%',
                background: message.isUser 
                  ? 'linear-gradient(135deg, #FF6B35, #F7931E)' 
                  : '#ffffff',
                borderRadius: '1rem',
                padding: window.innerWidth <= 768 ? '0.75rem' : '1rem',
                border: message.isUser ? 'none' : '1px solid #e2e8f0',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
                color: message.isUser ? 'white' : '#1e293b'
              }}>
                {!message.isUser && (
                  <div style={{
                    fontSize: '0.8rem',
                    marginBottom: '0.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#64748b'
                  }}>
                    <span>🎭</span> {selectedPersonality?.display_name || 'Wisdom Guide'}
                  </div>
                )}
                <div style={{
                  fontSize: '0.95rem',
                  lineHeight: '1.5'
                }}>
                  {message.isUser ? (
                    <div>{message.text}</div>
                  ) : (
                    <div>
                      <ReactMarkdown>{message.text}</ReactMarkdown>
                      {/* Response Source Transparency for Assistant Messages - Admin Only */}
                      {message.metadata && user?.role === 'admin' && (
                        <div style={{ marginTop: '0.75rem' }}>
                          <MessageSourceBadge 
                            metadata={message.metadata}
                            compact={true}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <div style={{
                  fontSize: '0.7rem',
                  opacity: 0.6,
                  marginTop: '0.5rem',
                  textAlign: message.isUser ? 'right' : 'left'
                }}>
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Loading */}
        {isLoading && (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            padding: '2rem',
            marginBottom: '2rem'
          }}>
            <div style={{
              background: '#ffffff',
              borderRadius: '1rem',
              padding: '1.5rem 2rem',
              border: '1px solid #e2e8f0',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)'
            }}>
              <div style={{
                display: 'flex',
                gap: '0.25rem'
              }}>
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    style={{
                      width: '8px',
                      height: '8px',
                      background: '#FF6B35',
                      borderRadius: '50%',
                      animation: `pulse 1.5s ease-in-out ${i * 0.2}s infinite`
                    }}
                  />
                ))}
              </div>
              <span style={{ fontSize: '0.9rem', color: '#64748b' }}>
                {selectedPersonality?.display_name || 'Your guide'} is reflecting...
              </span>
            </div>
          </div>
        )}

        {/* Mobile-Optimized Input Form */}
        <form 
          onSubmit={handleSubmit}
          style={{
            position: 'sticky',
            bottom: window.innerWidth <= 768 ? '0.5rem' : '1rem',
            background: '#ffffff',
            borderRadius: window.innerWidth <= 768 ? '1rem' : '1.5rem',
            padding: window.innerWidth <= 768 ? '0.75rem' : '1rem',
            border: '1px solid #e2e8f0',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
            display: 'flex',
            gap: window.innerWidth <= 768 ? '0.75rem' : '1rem',
            alignItems: 'center',
            opacity: selectedPersonality ? 1 : 0.6,
            pointerEvents: selectedPersonality ? 'auto' : 'none',
            margin: window.innerWidth <= 768 ? '0 -0.5rem' : '0'
          }}
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={getPlaceholderText()}
            disabled={!selectedPersonality}
            style={{
              flex: '1',
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: window.innerWidth <= 768 ? '0.75rem' : '1rem',
              padding: window.innerWidth <= 768 ? '0.875rem 1rem' : '1rem 1.5rem',
              color: '#1e293b',
              fontSize: '1rem',
              outline: 'none',
              cursor: selectedPersonality ? 'text' : 'not-allowed'
            }}
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading || !selectedPersonality}
            style={{
              background: inputText.trim() && !isLoading && selectedPersonality
                ? 'linear-gradient(135deg, #FF6B35, #F7931E)' 
                : '#e2e8f0',
              border: 'none',
              borderRadius: window.innerWidth <= 768 ? '0.75rem' : '1rem',
              padding: window.innerWidth <= 768 ? '0.875rem' : '1rem',
              color: inputText.trim() && !isLoading && selectedPersonality ? 'white' : '#94a3b8',
              cursor: inputText.trim() && !isLoading && selectedPersonality ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minWidth: window.innerWidth <= 768 ? '2.75rem' : '3rem',
              transition: 'all 0.3s ease',
              boxShadow: inputText.trim() && !isLoading && selectedPersonality ? '0 4px 12px rgba(59, 130, 246, 0.3)' : 'none'
            }}
          >
            <Send size={18} />
          </button>
        </form>
      </div>
      
      {/* Debug overlay for troubleshooting auth issues in production */}
      {showDebug && <DebugAuth />}
    </div>
  );
}
