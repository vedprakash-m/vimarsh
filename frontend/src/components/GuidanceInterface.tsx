import React, { useState, useEffect, useRef, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Hash, CornerDownLeft, Settings, User, LogOut, ChevronRight, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import PersonalitySelector from './PersonalitySelector';
import { usePersonality, Personality } from '../contexts/PersonalityContext';
import { useAuth } from '../auth/AuthProvider';
import { useAppLoading } from '../contexts/AppLoadingContext';
import spiritualGuidanceAPI from '../utils/api';
import { engagementApi } from './engagement/engagementApi';
import { Message } from './chat';

import '../styles/wisdom-typography.css';
import '../styles/vimarsh-design-system.css';

// Sample questions mapped to domains/personalities for "Wisdom Starters"
const WISDOM_STARTERS: Record<string, string[]> = {
  'krishna': [
    "How can I find peace in times of great uncertainty?",
    "What is the true meaning of performing one's duty?",
    "How do I overcome attachment to results?"
  ],
  'buddha': [
    "How do I practice mindfulness in a busy world?",
    "What is the path to overcoming suffering?",
    "How can I cultivate more compassion for myself and others?"
  ],
  'marcus_aurelius': [
    "How do I stay resilient when things go wrong?",
    "What should I focus on when I feel overwhelmed?",
    "How can I stop worrying about what others think of me?"
  ],
  'albert_einstein': [
    "What is the importance of curiosity in our lives?",
    "How can we solve problems that seem impossible?",
    "What is the relationship between imagination and knowledge?"
  ],
  'socrates': [
    "How do I know if I am truly living a good life?",
    "What is the value of questioning my own beliefs?",
    "How can I become more wise through self-reflection?"
  ],
  'default': [
    "How can I find more meaning in my daily life?",
    "What is the best way to handle difficult emotions?",
    "How do I align my actions with my values?"
  ]
};

const getDomainThemeConfig = (domain?: string) => {
  switch (domain?.toLowerCase()) {
    case 'spiritual': return { primary: '#007aff', accent: '#5856d6', bgLight: '#f0f9ff' };
    case 'philosophical': return { primary: '#5856d6', accent: '#af52de', bgLight: '#f5f3ff' };
    case 'scientific': return { primary: '#34c759', accent: '#007aff', bgLight: '#f0fdf4' };
    case 'leadership': return { primary: '#ff3b30', accent: '#ff9500', bgLight: '#fff1f2' };
    case 'literary': return { primary: '#af52de', accent: '#ff2d55', bgLight: '#fdf2f8' };
    case 'psychology': return { primary: '#8b5cf6', accent: '#ec4899', bgLight: '#faf5ff' };
    default: return { primary: '#6b7280', accent: '#9ca3af', bgLight: '#f8f9fa' };
  }
};

export default function GuidanceInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPersonalitySelector, setShowPersonalitySelector] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  
  const { logout, account, isAuthenticated } = useAuth();
  const { isInitializing } = useAppLoading();
  const { 
    selectedPersonality, 
    setSelectedPersonality, 
    availablePersonalities, 
    personalityLoading 
  } = usePersonality();

  // Get current effective user ID for API calls
  const effectiveUserId = useMemo(() => {
    return account?.homeAccountId || account?.localAccountId || sessionId;
  }, [account, sessionId]);

  // Redirect if no personality and none available (safety)
  useEffect(() => {
    if (!personalityLoading && availablePersonalities.length > 0 && !selectedPersonality) {
      setShowPersonalitySelector(true);
    }
  }, [personalityLoading, availablePersonalities, selectedPersonality]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handlePersonalitySelect = (personality: Personality) => {
    setSelectedPersonality(personality);
    setShowPersonalitySelector(false);
    setMessages([]); // Clear canvas for new personality
  };

  const starters = useMemo(() => {
    if (!selectedPersonality) return WISDOM_STARTERS.default;
    return WISDOM_STARTERS[selectedPersonality.id] || WISDOM_STARTERS.default;
  }, [selectedPersonality]);

  const handleSubmit = async (e?: React.FormEvent, overrideText?: string) => {
    if (e) e.preventDefault();
    const textToSubmit = overrideText || inputText;
    if (!textToSubmit.trim() || isLoading || !selectedPersonality) return;

    const question = textToSubmit;
    const userMessage: Message = {
      id: Date.now().toString(),
      text: question,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    const aiMessageId = (Date.now() + 1).toString();
    const initialAiMessage: Message = {
      id: aiMessageId,
      text: '',
      isUser: false,
      timestamp: new Date(),
      personality: selectedPersonality.id
    };

    setMessages(prev => [...prev, initialAiMessage]);

    try {
      const recentMessages = messages.slice(-4).map(msg => ({
        role: msg.isUser ? 'user' as const : 'assistant' as const,
        content: msg.text
      }));

      await spiritualGuidanceAPI.getSpiritualGuidanceStream(
        {
          query: question,
          language: 'English',
          include_citations: true,
          voice_enabled: false,
          conversation_context: recentMessages,
          personality_id: selectedPersonality.id,
          user_id: effectiveUserId,
          session_id: sessionId
        },
        (chunk) => {
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessageId ? { ...msg, text: msg.text + chunk } : msg
          ));
        },
        (fullData) => {
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessageId ? { 
              ...msg, 
              text: fullData.response, 
              metadata: fullData.metadata 
            } : msg
          ));
          setIsLoading(false);
          
          // Headless engagement tracking
          engagementApi.recordActivityHeadless(
            effectiveUserId,
            'conversation',
            selectedPersonality.id,
            selectedPersonality.domain,
            { session_id: sessionId, message_count: messages.length + 2 }
          );
        },
        (error) => {
          console.error('Streaming Error:', error);
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessageId ? { 
              ...msg, 
              text: "The silence of the universe remains. Please try again.",
            } : msg
          ));
          setIsLoading(false);
        }
      );
    } catch (error) {
      console.error('Guidance API Error:', error);
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  if (isInitializing || personalityLoading) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fff' }}>
        <div className="apple-spinner"></div>
      </div>
    );
  }
  const themeConfig = getDomainThemeConfig(selectedPersonality?.domain);

  return (
    <div className="wisdom-canvas-container" style={{ 
      minHeight: '100vh', 
      background: '#ffffff',
      display: 'flex', 
      flexDirection: 'column',
      position: 'relative',
      overflowX: 'hidden'
    }}>
      {/* Dynamic Background Mesh Animations */}
      <div style={{
        position: 'fixed',
        top: 0, left: 0, right: 0, bottom: 0,
        zIndex: 0,
        pointerEvents: 'none',
        overflow: 'hidden',
        background: themeConfig.bgLight,
        transition: 'background 1.5s ease-in-out'
      }}>
        {/* Animated Orbs */}
        <div style={{
          position: 'absolute',
          top: '-10%', left: '-10%',
          width: '50vw', height: '50vw',
          background: `radial-gradient(circle, ${themeConfig.primary} 0%, transparent 60%)`,
          opacity: 0.12,
          filter: 'blur(60px)',
          animation: 'blob-bounce 15s infinite ease-in-out alternate',
          transition: 'background 1.5s ease-in-out'
        }} />
        <div style={{
          position: 'absolute',
          bottom: '-20%', right: '-10%',
          width: '60vw', height: '60vw',
          background: `radial-gradient(circle, ${themeConfig.accent} 0%, transparent 60%)`,
          opacity: 0.12,
          filter: 'blur(80px)',
          animation: 'blob-bounce 20s infinite ease-in-out alternate-reverse',
          transition: 'background 1.5s ease-in-out'
        }} />
      </div>

      <style>{`
        .apple-spinner {
          width: 24px;
          height: 24px;
          border: 2px solid rgba(0,0,0,0.1);
          border-top: 2px solid ${themeConfig.primary};
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes blob-bounce {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        @keyframes shimmer-bg {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes slideUpFade {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .glass-pill {
          background: rgba(255,255,255,0.8);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          border: 1px solid rgba(255,255,255,0.9);
          box-shadow: 0 4px 24px rgba(0,0,0,0.04);
        }

        .user-menu-dropdown {
          position: absolute; top: 100%; right: 0; margin-top: 0.5rem;
          background: rgba(255,255,255,0.95);
          backdrop-filter: blur(30px);
          border: 1px solid rgba(255,255,255,0.9);
          border-radius: 16px;
          box-shadow: 0 10px 40px rgba(0,0,0,0.1);
          width: 220px; z-index: 100;
          animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .user-menu-item {
          display: flex; align-items: center; gap: 0.75rem;
          padding: 0.75rem 1.25rem; color: #1d1d1f; cursor: pointer;
          transition: background 0.2s; font-size: 0.9rem; font-weight: 500;
        }
        .user-menu-item:hover { background: rgba(0,0,0,0.04); }

        .wisdom-starter-card {
          background: rgba(255, 255, 255, 0.6);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          border: 1px solid rgba(255,255,255,0.9);
          border-radius: 18px;
          padding: 1.25rem 1.5rem;
          cursor: pointer;
          text-align: left;
          font-size: 1.05rem;
          color: #1d1d1f;
          display: flex;
          align-items: center;
          gap: 1.25rem;
          box-shadow: 0 4px 12px rgba(0,0,0,0.02);
          transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
          animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
        }
        .wisdom-starter-card:hover {
          background: rgba(255, 255, 255, 0.95);
          transform: translateY(-4px) scale(1.02);
          box-shadow: 0 12px 30px rgba(themeConfig.primary, 0.1), 0 0 0 1px rgba(255,255,255,1);
        }

        .cinematic-title {
          background: linear-gradient(135deg, #0f0f11 30%, ${themeConfig.primary} 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-size: 200% 200%;
          animation: shimmer-bg 6s ease infinite;
        }

        .user-message-blob {
          background: #1d1d1f;
          color: #ffffff;
          border-radius: 24px 24px 4px 24px;
          padding: 1.2rem 1.5rem;
          box-shadow: 0 8px 24px rgba(0,0,0,0.1);
          font-family: var(--font-primary);
          font-size: 1.15rem;
          line-height: 1.5;
          display: inline-block;
        }

        .ai-message-blob {
          font-family: var(--font-primary);
          font-size: 1.15rem;
          color: #2c2c2e;
          line-height: 1.8;
          background: transparent;
          padding-left: 0.5rem;
        }
        
        .ai-message-blob p { margin-bottom: 1.25rem; }
        .ai-message-blob p:last-child { margin-bottom: 0; }
        .ai-message-blob strong { color: #000; font-weight: 600; }
        .ai-message-blob em { font-family: var(--font-display); font-size: 1.25em; color: ${themeConfig.primary}; }

        .wisdom-canvas-input-wrapper {
          background: rgba(255, 255, 255, 0.85);
          backdrop-filter: blur(32px);
          -webkit-backdrop-filter: blur(32px);
          border: 1px solid rgba(255,255,255,0.8);
          border-top: 1px solid rgba(255,255,255,1);
          border-radius: 32px;
          padding: 0.75rem 0.75rem 0.75rem 1.5rem;
          box-shadow: 0 12px 40px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.02);
          display: flex;
          align-items: flex-end;
          transition: all 0.3s ease;
        }
        .wisdom-canvas-input-wrapper:focus-within {
          box-shadow: 0 20px 40px rgba(0,0,0,0.12), 0 0 0 2px rgba(0,0,0,0.05);
          background: rgba(255, 255, 255, 0.98);
        }
      `}</style>

      {showPersonalitySelector ? (
        <div style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'rgba(255,255,255,0.7)', backdropFilter: 'blur(40px)', overflowY: 'auto' }}>
          <div style={{ padding: '4rem 2rem', maxWidth: '1200px', margin: '0 auto', animation: 'slideUpFade 0.5s ease-out' }}>
            <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '3.5rem', textAlign: 'center', marginBottom: '3rem', color: '#1d1d1f' }}>
              Whose wisdom do you seek?
            </h1>
            <PersonalitySelector 
              availablePersonalities={availablePersonalities}
              selectedPersonalityId={selectedPersonality?.id} 
              onPersonalitySelect={handlePersonalitySelect} 
              onClose={() => setShowPersonalitySelector(false)}
            />
          </div>
        </div>
      ) : (
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '1.5rem', maxWidth: '1000px', margin: '0 auto', width: '100%', zIndex: 10 }}>
          
          {/* Navigation Bar */}
          <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4rem' }}>
            <div 
              onClick={() => setShowPersonalitySelector(true)}
              className="glass-pill"
              style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.6rem 1rem', borderRadius: '30px', transition: 'all 0.2s', color: '#1d1d1f' }}
            >
              <div style={{ width: 28, height: 28, borderRadius: '50%', background: themeConfig.primary, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '0.8rem', fontWeight: 700 }}>
                {selectedPersonality?.display_name?.charAt(0) || 'W'}
              </div>
              <span style={{ fontSize: '0.95rem', fontWeight: 600 }}>{selectedPersonality?.display_name || 'Select Guide'}</span>
              <ChevronRight size={14} color="#999" />
            </div>

            <div style={{ position: 'relative' }}>
              <div 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="glass-pill"
                style={{ cursor: 'pointer', width: '46px', height: '46px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'transform 0.2s' }}
                onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.05)'}
                onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
              >
                <User size={18} color="#1d1d1f" />
              </div>
              
              {showUserMenu && (
                <div className="user-menu-dropdown">
                  <div className="user-menu-item" style={{ borderBottom: '1px solid #f0f0f0', padding: '1rem', cursor: 'default' }}>
                    <div style={{ fontSize: '0.8rem', color: '#999', marginBottom: '0.25rem' }}>Signed in as</div>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem', overflow: 'hidden', textOverflow: 'ellipsis' }}>{account?.username || 'Guest Seeker'}</div>
                  </div>
                  <div className="user-menu-item" onClick={() => { setShowUserMenu(false); navigate('/settings'); }}>
                    <Settings size={16} />
                    <span>Settings</span>
                  </div>
                  <div className="user-menu-item" onClick={() => { logout(); navigate('/'); }}>
                    <LogOut size={16} />
                    <span>Sign Out</span>
                  </div>
                </div>
              )}
            </div>
          </header>

          {/* Conversation Canvas */}
          <div className="wisdom-canvas-messages" style={{ flex: 1, paddingBottom: '2rem' }}>
            {messages.length === 0 ? (
              <div style={{ marginTop: '5vh', animation: 'fadeIn 1s ease-out' }}>
                <h2 className="cinematic-title" style={{ 
                  textAlign: 'center',
                  fontFamily: 'var(--font-display)',
                  fontSize: '4.5rem',
                  fontWeight: 600,
                  letterSpacing: '-0.04em',
                  marginBottom: '4rem',
                  lineHeight: '1.1'
                }}>
                  What burdens your mind today?
                </h2>
                
                <div style={{ 
                  display: 'flex', 
                  flexDirection: 'column',
                  gap: '1.25rem', 
                  maxWidth: '600px', 
                  margin: '0 auto' 
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', justifyContent: 'center', marginBottom: '0.5rem' }}>
                    <Sparkles size={14} style={{ color: themeConfig.primary }} />
                    <span style={{ fontSize: '0.8rem', color: '#666', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                      Wisdom Starters
                    </span>
                  </div>
                  {starters.map((starter, idx) => (
                    <button 
                      key={idx} 
                      className="wisdom-starter-card"
                      style={{ animationDelay: `${idx * 0.15}s` }}
                      onClick={() => handleSubmit(undefined, starter)}
                    >
                      <div style={{ flex: 1 }}>{starter}</div>
                      <ChevronRight size={18} style={{ color: '#ccc' }} />
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
                {messages.map((msg, index) => (
                  <div key={msg.id} style={{ 
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: msg.isUser ? 'flex-end' : 'flex-start',
                    width: '100%',
                    animation: 'slideUpFade 0.4s ease-out'
                  }}>
                    {msg.isUser ? (
                      <div className="user-message-blob">
                        {msg.text}
                      </div>
                    ) : (
                      <div style={{ display: 'flex', gap: '1.25rem', maxWidth: '95%' }}>
                        <div style={{ 
                          width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
                          background: themeConfig.primary, color: '#fff', 
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: '0.9rem', fontWeight: 600, marginTop: '0.25rem',
                          boxShadow: `0 4px 16px ${themeConfig.primary}50`
                        }}>
                          {selectedPersonality?.display_name?.charAt(0) || 'W'}
                        </div>
                        <div className="ai-message-blob">
                          <ReactMarkdown>{msg.text}</ReactMarkdown>
                          {msg.metadata?.citations && msg.metadata.citations.length > 0 && (
                            <div style={{ marginTop: '1.5rem', fontSize: '0.85rem', color: '#888', fontStyle: 'italic', borderLeft: `2px solid ${themeConfig.primary}40`, paddingLeft: '1rem' }}>
                              — Based on material from {msg.metadata.citations[0].source}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
            
            {isLoading && (
              <div style={{ padding: '2rem 1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                 <div style={{ width: 36, height: 36, borderRadius: '50%', background: themeConfig.primary, opacity: 0.2 }} />
                 <div className="apple-spinner" style={{ borderColor: `transparent ${themeConfig.primary} ${themeConfig.primary} ${themeConfig.primary}` }}></div>
              </div>
            )}
            <div ref={messagesEndRef} style={{ height: '40px' }} />
          </div>

          {/* Input Area */}
          <div style={{ position: 'sticky', bottom: '2rem', width: '100%', paddingTop: '1rem' }}>
            <form onSubmit={handleSubmit} style={{ position: 'relative' }}>
              <div className="wisdom-canvas-input-wrapper">
                <textarea
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={`Seek ${selectedPersonality?.display_name || 'wisdom'}'s perspective...`}
                  rows={1}
                  style={{ 
                    fontFamily: 'var(--font-primary)', 
                    fontSize: '1.15rem',
                    lineHeight: '1.5',
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    width: '100%',
                    resize: 'none',
                    padding: '0.5rem 0',
                    color: '#1d1d1f'
                  }}
                  onInput={(e) => {
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = 'auto';
                    target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
                  }}
                />
                <button 
                  type="submit" 
                  disabled={!inputText.trim() || isLoading}
                  style={{ 
                    background: inputText.trim() ? themeConfig.primary : '#e5e5ea',
                    border: 'none',
                    width: '42px',
                    height: '42px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    cursor: inputText.trim() ? 'pointer' : 'default',
                    transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
                    marginLeft: '1rem',
                    flexShrink: 0,
                    boxShadow: inputText.trim() ? `0 4px 16px ${themeConfig.primary}60` : 'none',
                    transform: inputText.trim() ? 'scale(1)' : 'scale(0.95)'
                  }}
                  onMouseEnter={e => { if (inputText.trim()) e.currentTarget.style.transform = 'scale(1.05)'; }}
                  onMouseLeave={e => { if (inputText.trim()) e.currentTarget.style.transform = 'scale(1)'; }}
                >
                  <CornerDownLeft size={20} />
                </button>
              </div>
            </form>
            
            <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.75rem', color: '#999', fontWeight: 500 }}>
               Powered by ancient texts and advanced LLM fusion
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
