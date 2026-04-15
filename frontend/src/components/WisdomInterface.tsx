import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Hash, CornerDownLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import PersonalitySelector from './PersonalitySelector';
import { usePersonality, Personality } from '../contexts/PersonalityContext';
import { Message } from './chat';
import spiritualGuidanceAPI from '../utils/api';
// Headless engagement tracking
import { engagementApi } from './engagement/engagementApi';
import { useAppLoading } from '../contexts/AppLoadingContext';

import '../styles/wisdom-typography.css';
import '../styles/vimarsh-design-system.css';

export default function WisdomInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPersonalitySelector, setShowPersonalitySelector] = useState(false);
  
  // Use constant session for component lifecycle
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { 
    selectedPersonality, 
    setSelectedPersonality, 
    availablePersonalities, 
    personalityLoading 
  } = usePersonality();

  const { isInitializing } = useAppLoading();

  // Show personality selector if none selected (fulfilling the spec to keep manual selection)
  useEffect(() => {
    if (availablePersonalities.length > 0 && !selectedPersonality && !personalityLoading) {
      setShowPersonalitySelector(true);
    }
  }, [availablePersonalities.length, selectedPersonality, personalityLoading]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handlePersonalitySelect = (personality: Personality) => {
    setSelectedPersonality(personality);
    setShowPersonalitySelector(false);
    setMessages([]);
  };

  const trackEngagementHeadless = (messageCount: number, domain?: string, pId?: string) => {
    // We send activity silently in the background
    const userIdDesktopFallback = sessionId; // Need to grab actual user ID from Auth context in a full impl
    // As per Tier 1 spec, we use the headless tracker to guarantee background execution
    engagementApi.recordActivityHeadless(
      userIdDesktopFallback, 
      'conversation',
      pId,
      domain,
      { session_id: sessionId, message_count: messageCount }
    );
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
          user_id: sessionId,
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
          trackEngagementHeadless(messages.length + 2, selectedPersonality.domain, selectedPersonality.id);
        },
        (error) => {
          console.error('Streaming Error:', error);
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessageId ? { 
              ...msg, 
              text: "The stream of thought has been interrupted. Please re-engage.",
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
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  if (isInitializing || personalityLoading) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fff' }}>
        <p style={{ fontFamily: 'var(--font-wisdom-ui)', color: '#666' }}>Loading wisdom...</p>
      </div>
    );
  }

  return (
    <div className="wisdom-canvas-container" style={{ minHeight: '100vh', background: '#fff', display: 'flex', flexDirection: 'column' }}>
      
      {showPersonalitySelector ? (
        <div style={{ position: 'fixed', inset: 0, zIndex: 50, background: '#fff', overflowY: 'auto' }}>
          <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
            <h1 style={{ fontFamily: 'var(--font-wisdom-body)', fontSize: '2.5rem', textAlign: 'center', marginBottom: '2rem', fontWeight: 300 }}>
              Choose your guide.
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
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '2rem 1rem', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
          
          {/* Header minimal */}
          <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <div 
              onClick={() => setShowPersonalitySelector(true)}
              style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', opacity: 0.6, transition: 'opacity 0.2s' }}
            >
              <Hash size={16} />
              <span style={{ fontSize: '0.9rem' }}>{selectedPersonality?.display_name}</span>
            </div>
          </header>

          <div className="wisdom-canvas-messages" style={{ flex: 1, overflowY: 'auto', paddingBottom: '3rem' }}>
            {messages.length === 0 ? (
              <div className="wisdom-greeting-prompt" style={{ marginTop: '20vh' }}>
                What burdens your mind today?
              </div>
            ) : (
              messages.map(msg => (
                <div key={msg.id} style={{ marginBottom: '2rem' }}>
                  {msg.isUser ? (
                    <div style={{ 
                      fontFamily: 'var(--font-wisdom-ui)', 
                      fontSize: '1.25rem', 
                      color: '#000', 
                      fontWeight: 500,
                      maxWidth: '85%',
                      marginLeft: 'auto',
                      textAlign: 'right'
                    }}>
                      {msg.text}
                    </div>
                  ) : (
                    <div className="wisdom-ai-response">
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>
                  )}
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="wisdom-ai-response" style={{ opacity: 0.5 }}>
                 <p>...</p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} style={{ position: 'relative', marginTop: 'auto' }}>
            <div className="wisdom-canvas-input">
              <textarea
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Seek understanding..."
                rows={1}
                style={{ 
                  fontFamily: 'var(--font-wisdom-body)', 
                  fontSize: '1.25rem',
                  lineHeight: '1.6',
                  paddingRight: '3rem',
                  color: '#111'
                }}
              />
              <button 
                type="submit" 
                disabled={!inputText.trim() || isLoading}
                style={{ 
                  position: 'absolute', 
                  right: '0', 
                  bottom: '12px', 
                  background: 'transparent',
                  border: 'none',
                  color: inputText.trim() ? '#000' : '#ccc',
                  cursor: inputText.trim() ? 'pointer' : 'default',
                  transition: 'color 0.2s'
                }}
              >
                <CornerDownLeft size={20} />
              </button>
            </div>
          </form>
        </main>
      )}
    </div>
  );
}
