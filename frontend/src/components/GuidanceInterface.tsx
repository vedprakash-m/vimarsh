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

const getDomainGradient = (domain?: string) => {
  switch (domain) {
    case 'spiritual': return 'linear-gradient(180deg, #fffcf0 0%, #ffffff 100%)';
    case 'philosophical': return 'linear-gradient(180deg, #f5f3ff 0%, #ffffff 100%)';
    case 'scientific': return 'linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%)';
    case 'leadership': return 'linear-gradient(180deg, #fef2f2 0%, #ffffff 100%)';
    case 'literary': return 'linear-gradient(180deg, #fdf2f8 0%, #ffffff 100%)';
    case 'psychology': return 'linear-gradient(180deg, #faf5ff 0%, #ffffff 100%)';
    default: return 'linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%)';
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
  
  const { logout, account } = useAuth();
  const { isInitializing } = useAppLoading();
  const { 
    selectedPersonality, 
    setSelectedPersonality, 
    availablePersonalities, 
    personalityLoading 
  } = usePersonality();

  // Get current effective user ID for API calls — Ensuring this matches MSAL and Backend format
  const effectiveUserId = useMemo(() => {
    // Priority 1: localAccountId (stable ID used by back-end for Cosmos partition)
    // Priority 2: homeAccountId (fallback)
    // Priority 3: sessionId (for guests)
    return account?.localAccountId || account?.homeAccountId || sessionId;
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
              text: "The connection to the source of wisdom has been interrupted. Please ensure you are logged in and try again.",
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

  return (
    <div className="wisdom-canvas-container" style={{ 
      minHeight: '100vh', 
      background: getDomainGradient(selectedPersonality?.domain), 
      display: 'flex', 
      flexDirection: 'column',
      transition: 'background 1s ease'
    }}>
      <style>{`
        .apple-spinner {
          width: 24px;
          height: 24px;
          border: 2px solid #f3f4f6;
          border-top: 2px solid #000;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .user-menu-dropdown {
          position: absolute;
          top: 100%;
          right: 0;
          margin-top: 0.5rem;
          background: #fff;
          border: 1px solid #eee;
          border-radius: 12px;
          box-shadow: 0 10px 25px rgba(0,0,0,0.1);
          width: 200px;
          z-index: 100;
          overflow: hidden;
          animation: fadeIn 0.2s ease-out;
        }
        .user-menu-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          color: #333;
          text-decoration: none;
          cursor: pointer;
          transition: background 0.2s;
          font-size: 0.9rem;
        }
        .user-menu-item:hover {
          background: #f5f5f7;
        }
        .wisdom-starter-card {
          background: rgba(255, 255, 255, 0.7);
          border: 1px solid rgba(0, 0, 0, 0.05);
          border-radius: 16px;
          padding: 1rem 1.25rem;
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: left;
          font-size: 0.95rem;
          color: #444;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }
        .wisdom-starter-card:hover {
          background: #fff;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.05);
          border-color: rgba(0, 0, 0, 0.1);
        }
        
        /* Mobile Optimizations */
        @media (max-width: 768px) {
          .wisdom-canvas-messages {
            padding: 0 0.5rem 6rem 0.5rem !important;
          }
          .greeting-text {
            font-size: 1.8rem !important;
            margin-top: 4vh !important;
            margin-bottom: 2rem !important;
            padding: 0 1rem;
          }
          .wisdom-starter-grid {
            grid-template-columns: 1fr !important;
            gap: 0.75rem !important;
            padding: 0 1rem;
          }
          .wisdom-starter-card {
            padding: 0.85rem 1rem !important;
            font-size: 0.85rem !important;
          }
          .nav-header {
            margin-bottom: 2rem !important;
            padding: 1rem 1rem 0 1rem !important;
          }
          .input-container {
            bottom: 1rem !important;
            padding: 0 1rem !important;
          }
          .message-user {
            font-size: 1.1rem !important;
            max-width: 90% !important;
          }
          .wisdom-ai-response {
            padding: 0 0.5rem !important;
            font-size: 1rem !important;
          }
        }
      `}</style>

      {showPersonalitySelector ? (
        <div style={{ position: 'fixed', inset: 0, zIndex: 200, background: '#fff', overflowY: 'auto' }}>
          <div style={{ padding: '4rem 2rem', maxWidth: '1200px', margin: '0 auto' }}>
            <h1 style={{ fontFamily: 'var(--font-wisdom-ui)', fontSize: '2rem', textAlign: 'center', marginBottom: '3rem', fontWeight: 400, letterSpacing: '-0.02em' }}>
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
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '1.5rem', maxWidth: '900px', margin: '0 auto', width: '100%' }}>
          
          {/* Navigation Bar */}
          <header className="nav-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4rem' }}>
            <div 
              onClick={() => setShowPersonalitySelector(true)}
              style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.5rem 0.75rem', borderRadius: '20px', background: 'rgba(255,255,255,0.8)', backdropFilter: 'blur(10px)', border: '1px solid rgba(0,0,0,0.05)', transition: 'all 0.2s' }}
            >
              <Hash size={14} color="#666" />
              <span style={{ fontSize: '0.85rem', fontWeight: 500, color: '#333' }}>{selectedPersonality?.display_name || 'Select Guide'}</span>
              <ChevronRight size={14} color="#999" />
            </div>

            <div style={{ position: 'relative' }}>
              <div 
                onClick={() => setShowUserMenu(!showUserMenu)}
                style={{ cursor: 'pointer', width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(255,255,255,0.8)', backdropFilter: 'blur(10px)', border: '1px solid rgba(0,0,0,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'opacity 0.2s' }}
              >
                <User size={18} color="#333" />
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
          <div className="wisdom-canvas-messages" style={{ flex: 1, overflowY: 'auto', paddingBottom: '4rem' }}>
            {messages.length === 0 ? (
              <div style={{ marginTop: '8vh', animation: 'fadeIn 1s ease-out' }}>
                <h2 className="greeting-text" style={{ 
                  textAlign: 'center',
                  fontFamily: 'var(--font-wisdom-ui)',
                  fontSize: '2.5rem',
                  fontWeight: 500,
                  color: '#1d1d1f',
                  letterSpacing: '-0.03em',
                  marginBottom: '3rem',
                  opacity: 0.9
                }}>
                  What burdens your mind today?
                </h2>
                
                <div className="wisdom-starter-grid" style={{ 
                  display: 'grid', 
                  gridTemplateColumns: '1fr', 
                  gap: '1rem', 
                  maxWidth: '500px', 
                  margin: '0 auto' 
                }}>
                  <div style={{ fontSize: '0.8rem', color: '#999', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem', textAlign: 'center' }}>
                    Wisdom Starters for {selectedPersonality?.display_name}
                  </div>
                  {starters.map((starter, idx) => (
                    <button 
                      key={idx} 
                      className="wisdom-starter-card"
                      onClick={() => handleSubmit(undefined, starter)}
                    >
                      <Sparkles size={16} style={{ color: '#f97316', flexShrink: 0 }} />
                      <span>{starter}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
                {messages.map(msg => (
                  <div key={msg.id} style={{ 
                    maxWidth: msg.isUser ? '85%' : '100%',
                    alignSelf: msg.isUser ? 'flex-end' : 'flex-start',
                    width: '100%'
                  }}>
                    {msg.isUser ? (
                      <div className="message-user" style={{ 
                        fontFamily: 'var(--font-wisdom-ui)', 
                        fontSize: '1.25rem', 
                        color: '#1d1d1f', 
                        fontWeight: 500,
                        textAlign: 'right',
                        lineHeight: 1.4
                      }}>
                        {msg.text}
                      </div>
                    ) : (
                      <div className="wisdom-ai-response" style={{ 
                        animation: 'fadeIn 0.5s ease-out',
                        padding: '0 1rem'
                      }}>
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                        {msg.metadata?.citations && msg.metadata.citations.length > 0 && (
                          <div style={{ marginTop: '1.5rem', fontSize: '0.75rem', color: '#999', fontStyle: 'italic' }}>
                            — Grounded in {msg.metadata.citations[0].source}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
            
            {isLoading && (
              <div className="wisdom-ai-response" style={{ opacity: 0.4, padding: '2rem 1rem' }}>
                 <div className="apple-spinner"></div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="input-container" style={{ position: 'sticky', bottom: '2rem', width: '100%', padding: '1rem 0' }}>
            <form onSubmit={handleSubmit} style={{ position: 'relative' }}>
              <div className="wisdom-canvas-input" style={{ 
                background: 'rgba(245, 245, 247, 0.8)', 
                backdropFilter: 'blur(20px)',
                borderRadius: '24px', 
                padding: '0.75rem 1.25rem',
                border: '1px solid rgba(0,0,0,0.05)',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'flex-end',
                boxShadow: '0 4px 20px rgba(0,0,0,0.03)'
              }}>
                <textarea
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={`Seek ${selectedPersonality?.display_name || 'wisdom'}'s perspective...`}
                  rows={1}
                  style={{ 
                    fontFamily: 'var(--font-wisdom-body)', 
                    fontSize: '1.1rem',
                    lineHeight: '1.5',
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    width: '100%',
                    resize: 'none',
                    padding: '0.25rem 0',
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
                    background: inputText.trim() ? '#000' : 'transparent',
                    border: 'none',
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: inputText.trim() ? '#fff' : '#ccc',
                    cursor: inputText.trim() ? 'pointer' : 'default',
                    transition: 'all 0.2s',
                    marginLeft: '0.5rem',
                    flexShrink: 0
                  }}
                >
                  <CornerDownLeft size={18} />
                </button>
              </div>
            </form>
          </div>
        </main>
      )}
    </div>
  );
}
