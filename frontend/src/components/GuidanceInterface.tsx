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

const InkGathering = () => (
  <div className="flex items-center gap-2 px-4 py-3 opacity-80 transition-all duration-500 ease-in-out">
    <div className="flex gap-1.5 drop-shadow-[0_0_8px_var(--domain-glow)]">
      <div className="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
    <span className="text-sm italic font-serif text-accent ml-2">Gathering thoughts...</span>
  </div>
);

export default function GuidanceInterface() {
  const { logout, account } = useAuth();
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  
  // Non-Destructive Switching: Dictionary mapping personality_id -> messages
  const [messageThreads, setMessageThreads] = useState<Record<string, Message[]>>(() => {
    const saved = localStorage.getItem('vimarsh_threads_' + (account?.localAccountId || 'guest'));
    return saved ? JSON.parse(saved) : {};
  });

  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPersonalitySelector, setShowPersonalitySelector] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  
  const { isInitializing } = useAppLoading();
  const { 
    selectedPersonality, 
    setSelectedPersonality, 
    availablePersonalities, 
    personalityLoading 
  } = usePersonality();

  // Current active messages
  const messages = selectedPersonality ? (messageThreads[selectedPersonality.id] || []) : [];

  // Update messages wrapper
  const setMessages = (updater: React.SetStateAction<Message[]>) => {
    if (!selectedPersonality) return;
    setMessageThreads(prev => {
      const current = prev[selectedPersonality.id] || [];
      const next = typeof updater === 'function' ? updater(current) : updater;
      return { ...prev, [selectedPersonality.id]: next };
    });
  };

  // Sync to local storage
  useEffect(() => {
    const key = 'vimarsh_threads_' + (account?.localAccountId || 'guest');
    localStorage.setItem(key, JSON.stringify(messageThreads));
  }, [messageThreads, account]);

  const effectiveUserId = useMemo(() => {
    return account?.localAccountId || account?.homeAccountId || sessionId;
  }, [account, sessionId]);

  useEffect(() => {
    if (!personalityLoading && availablePersonalities.length > 0 && !selectedPersonality) {
      setShowPersonalitySelector(true);
    }
  }, [personalityLoading, availablePersonalities, selectedPersonality]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Swipe events for personality switching
  useEffect(() => {
    const handleSwipeLeft = () => {
      if (!selectedPersonality || availablePersonalities.length <= 1) return;
      const currentIndex = availablePersonalities.findIndex(p => p.id === selectedPersonality.id);
      const nextIndex = (currentIndex + 1) % availablePersonalities.length;
      setSelectedPersonality(availablePersonalities[nextIndex]);
    };

    const handleSwipeRight = () => {
      if (!selectedPersonality || availablePersonalities.length <= 1) return;
      const currentIndex = availablePersonalities.findIndex(p => p.id === selectedPersonality.id);
      const prevIndex = (currentIndex - 1 + availablePersonalities.length) % availablePersonalities.length;
      setSelectedPersonality(availablePersonalities[prevIndex]);
    };

    window.addEventListener('device-swipe-left', handleSwipeLeft);
    window.addEventListener('device-swipe-right', handleSwipeRight);
    
    return () => {
      window.removeEventListener('device-swipe-left', handleSwipeLeft);
      window.removeEventListener('device-swipe-right', handleSwipeRight);
    };
  }, [selectedPersonality, availablePersonalities, setSelectedPersonality]);

  const handlePersonalitySelect = (personality: Personality) => {
    setSelectedPersonality(personality);
    setShowPersonalitySelector(false);
    // Non-destructive: We no longer clear messages here!
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
          voice_enabled: true,
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
      <div className="h-screen w-full flex items-center justify-center bg-canvas">
        <div className="w-6 h-6 border-2 border-elevated border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-canvas transition-colors duration-1000 ease-in-out relative">
      {showPersonalitySelector ? (
        <div className="fixed inset-0 z-50 bg-canvas overflow-y-auto">
          <div className="max-w-6xl mx-auto py-16 px-8">
            <h1 className="font-serif text-4xl text-center mb-12 font-medium tracking-tight text-primary">
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
        <main className="flex-1 flex flex-col w-full max-w-3xl mx-auto p-4 md:p-6 lg:p-8">
          
          {/* Navigation Bar */}
          <header className="flex justify-between items-center mb-10 mt-2">
            <button 
              onClick={() => setShowPersonalitySelector(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-surface/50 backdrop-blur-md border border-border-subtle hover:bg-surface/80 transition-all group"
            >
              <Hash size={16} className="text-tertiary group-hover:text-accent transition-colors" />
              <span className="text-sm font-medium text-primary">{selectedPersonality?.display_name || 'Select Guide'}</span>
              <ChevronRight size={16} className="text-tertiary" />
            </button>

            <div className="relative">
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="w-10 h-10 rounded-full bg-surface/50 backdrop-blur-md border border-border-subtle flex items-center justify-center hover:bg-surface/80 transition-all"
              >
                <User size={18} className="text-primary" />
              </button>
              
              {showUserMenu && (
                <div className="absolute top-full right-0 mt-2 w-56 bg-surface border border-border-subtle rounded-xl shadow-lg z-40 overflow-hidden animate-in fade-in slide-in-from-top-2">
                  <div className="p-4 border-b border-border-subtle cursor-default">
                    <div className="text-xs text-tertiary mb-1">Signed in as</div>
                    <div className="font-medium text-sm text-primary truncate">{account?.username || 'Guest Seeker'}</div>
                  </div>
                  <button onClick={() => navigate('/settings')} className="w-full flex items-center gap-3 px-4 py-3 text-sm text-primary hover:bg-elevated transition-colors text-left">
                    <Settings size={16} />
                    Settings
                  </button>
                  <button onClick={() => { logout(); navigate('/'); }} className="w-full flex items-center gap-3 px-4 py-3 text-sm text-primary hover:bg-elevated transition-colors text-left">
                    <LogOut size={16} />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          </header>

          {/* Conversation Canvas - Document Style */}
          <div className="flex-1 overflow-y-auto pb-24 space-y-8">
            {messages.length === 0 ? (
              <div className="mt-16 md:mt-24 animate-in fade-in slide-in-from-bottom-4 duration-700">
                <h2 className="font-serif text-3xl md:text-4xl text-center font-medium text-primary tracking-tight mb-12">
                  What burdens your mind today?
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                  <div className="col-span-1 md:col-span-2 text-xs font-medium text-tertiary uppercase tracking-widest text-center mb-2">
                    Wisdom Starters for {selectedPersonality?.display_name}
                  </div>
                  {starters.map((starter, idx) => (
                    <button 
                      key={idx} 
                      className="text-left p-4 rounded-2xl bg-surface border border-border-subtle hover:border-accent/30 hover:shadow-[0_4px_20px_var(--domain-glow)] transition-all flex items-start gap-3 group"
                      onClick={() => handleSubmit(undefined, starter)}
                    >
                      <Sparkles size={18} className="text-accent shrink-0 mt-0.5 opacity-70 group-hover:opacity-100 transition-opacity" />
                      <span className="text-sm md:text-base text-secondary group-hover:text-primary transition-colors">{starter}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-8 md:gap-10">
                {messages.map((msg, idx) => (
                  <div key={msg.id} className={`w-full max-w-2xl ${msg.isUser ? 'self-end' : 'self-start'}`}>
                    {msg.isUser ? (
                      <div className="text-lg md:text-xl font-sans text-primary text-right leading-relaxed pl-12 opacity-90">
                        {msg.text}
                      </div>
                    ) : (
                      <div className="relative pl-6 md:pl-8 border-l-2 border-accent/20 bg-gradient-to-r from-[var(--domain-glow)] to-transparent rounded-r-xl py-2 animate-in fade-in duration-500">
                        <div className="absolute -left-3.5 top-0 w-7 h-7 rounded-full bg-surface border-2 border-accent/30 flex items-center justify-center font-serif text-xs font-bold text-accent shadow-sm">
                          {selectedPersonality?.display_name.charAt(0)}
                        </div>
                        <div className="font-serif text-[1.1rem] md:text-[1.2rem] leading-[1.8] text-primary prose prose-p:my-3 prose-strong:font-semibold prose-a:text-accent max-w-none">
                          <ReactMarkdown>{msg.text}</ReactMarkdown>
                        </div>
                        {msg.metadata?.citations && msg.metadata.citations.length > 0 && (
                          <div className="mt-4 text-xs text-tertiary italic">
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
              <div className="self-start relative pl-6 md:pl-8 border-l-2 border-accent/20">
                 <InkGathering />
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Sticky Composer */}
          <div className="sticky bottom-4 md:bottom-8 w-full">
            <form onSubmit={handleSubmit} className="relative group">
              <div className="bg-surface/80 backdrop-blur-xl rounded-3xl border border-border-subtle shadow-lg focus-within:border-accent/50 focus-within:shadow-[0_8px_30px_var(--domain-glow)] transition-all duration-300 flex items-end p-2 md:p-3">
                <textarea
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={`Seek ${selectedPersonality?.display_name || 'wisdom'}'s perspective...`}
                  rows={1}
                  className="w-full bg-transparent border-none outline-none resize-none font-sans text-base md:text-lg text-primary placeholder:text-tertiary py-2 px-4 max-h-[200px]"
                  onInput={(e) => {
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = 'auto';
                    target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
                  }}
                />
                <button 
                  type="submit" 
                  disabled={!inputText.trim() || isLoading}
                  className={`shrink-0 w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center transition-all duration-300 ml-2 ${
                    inputText.trim() && !isLoading
                      ? 'bg-primary text-canvas shadow-md hover:scale-105 active:scale-95' 
                      : 'bg-elevated text-tertiary cursor-not-allowed'
                  }`}
                >
                  <CornerDownLeft size={20} className={inputText.trim() ? "opacity-100" : "opacity-50"} />
                </button>
              </div>
            </form>
          </div>
        </main>
      )}
    </div>
  );
}
