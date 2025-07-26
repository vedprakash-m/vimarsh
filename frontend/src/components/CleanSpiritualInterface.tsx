import React, { useState, useEffect } from 'react';
import { Send, Mic, MicOff, MessageSquare, Users } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import PersonalitySelector from './PersonalitySelector';
import { usePersonality, Personality } from '../contexts/PersonalityContext';
import { getApiBaseUrl } from '../config/environment';
import '../styles/spiritual-theme.css';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  personality?: string;
}

export default function CleanSpiritualInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Add animation styles
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

  const handlePersonalitySelect = (personality: Personality) => {
    setSelectedPersonality(personality);
    setShowPersonalitySelector(false);
    // Clear messages when switching personality to provide fresh context
    setMessages([]);
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

      // Call real spiritual guidance API with conversation context
      const apiUrl = getApiBaseUrl();
      const response = await fetch(`${apiUrl}/spiritual_guidance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: question,
          language: 'English',
          include_citations: true,
          voice_enabled: false,
          conversation_context: recentMessages,
          personality_id: selectedPersonality.id
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Use the response as-is from the backend
      // The backend should handle inline citations if needed
      const apiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isUser: false,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, apiResponse]);
      
    } catch (error) {
      console.error('Error calling spiritual guidance API:', error);
      
      // Fallback response for errors
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: "🙏 I'm having trouble connecting to the spiritual guidance service. Please check your connection and try again, dear soul. (Frontend Error)",
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

  // Dynamic quick prompts based on selected personality domain
  const getQuickPrompts = () => {
    if (!selectedPersonality) {
      return [
        "How can I find my dharma and live according to my true purpose?",
        "How can I maintain equanimity during life's ups and downs?",
        "What are the different paths of yoga and which one suits me?",
        "How do I overcome anger and jealousy through spiritual practice?"
      ];
    }

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
  };

  const quickPrompts = getQuickPrompts();

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    }}>
      {/* Header */}
      <header style={{
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '3rem',
            height: '3rem',
            background: 'linear-gradient(135deg, #fbbf24, #f59e0b)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.5rem',
            fontWeight: 'bold',
            color: 'white',
            border: '2px solid rgba(255, 255, 255, 0.3)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)'
          }}>
            V
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '700' }}>Vimarsh</h1>
            <p style={{ 
              margin: 0, 
              fontSize: '0.85rem', 
              opacity: 0.9,
              fontWeight: '500',
              color: '#fbbf24'
            }}>
              Wisdom Without Boundaries
            </p>
          </div>
        </div>
        
        {/* Personality Selector Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '0.75rem',
            padding: '0.5rem 1rem',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            backdropFilter: 'blur(10px)'
          }}>
            <span style={{ fontSize: '0.9rem', fontWeight: '600' }}>
              {selectedPersonality?.name || 'Loading...'}
            </span>
            <span style={{ 
              fontSize: '0.75rem', 
              opacity: 0.7, 
              marginLeft: '0.5rem',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              {selectedPersonality?.domain === 'spiritual' ? 'SPIRITUAL' :
               selectedPersonality?.domain === 'scientific' ? 'SCIENTIFIC' :
               selectedPersonality?.domain === 'historical' ? 'HISTORICAL' :
               selectedPersonality?.domain === 'philosophical' ? 'PHILOSOPHICAL' :
               selectedPersonality?.domain === 'literary' ? 'LITERARY' :
               'SPIRITUAL'}
            </span>
          </div>
          <button 
            onClick={() => setShowPersonalitySelector(!showPersonalitySelector)}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              color: 'white',
              padding: '0.5rem',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              transition: 'all 0.3s ease'
            }}
            title="Change Personality"
            disabled={!selectedPersonality}
          >
            <Users size={18} />
          </button>
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
        </div>
      </header>

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

      {/* Main Content */}
      <div style={{
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '1rem 2rem',
        minHeight: 'calc(100vh - 140px)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Welcome Section */}
        {messages.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '2rem 1rem',
            marginBottom: '1rem'
          }}>
            <div style={{
              fontSize: '4rem',
              marginBottom: '1rem',
              filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3))'
            }}>🏵️</div>
            
            {!selectedPersonality ? (
              <>
                <h2 style={{
                  fontSize: '2.5rem',
                  fontWeight: '700',
                  marginBottom: '1rem',
                  textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
                }}>Welcome to Vimarsh</h2>
                <p style={{
                  fontSize: '1.25rem',
                  opacity: 0.9,
                  maxWidth: '600px',
                  margin: '0 auto 2rem',
                  lineHeight: '1.6',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)'
                }}>
                  <strong>Wisdom Without Boundaries</strong><br/>
                  Choose your spiritual guide to begin your journey of divine wisdom and enlightenment.
                </p>
                <button
                  onClick={() => setShowPersonalitySelector(true)}
                  style={{
                    background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                    border: 'none',
                    color: 'white',
                    padding: '1rem 2rem',
                    borderRadius: '1rem',
                    fontSize: '1.1rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 8px 20px rgba(59, 130, 246, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.3)';
                  }}
                >
                  Choose Your Spiritual Guide
                </button>
              </>
            ) : (
              <>
                <h2 style={{
                  fontSize: '2.5rem',
                  fontWeight: '700',
                  marginBottom: '1rem',
                  textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
                }}>Welcome to Your {selectedPersonality.domain === 'spiritual' ? 'Spiritual' :
                  selectedPersonality.domain === 'scientific' ? 'Scientific' :
                  selectedPersonality.domain === 'historical' ? 'Historical' :
                  selectedPersonality.domain === 'philosophical' ? 'Philosophical' :
                  selectedPersonality.domain === 'literary' ? 'Literary' :
                  'Spiritual'} Journey</h2>
                <p style={{
                  fontSize: '1.25rem',
                  opacity: 0.9,
                  maxWidth: '600px',
                  margin: '0 auto 1rem',
                  lineHeight: '1.6',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)'
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
                    : 'Ask questions about spirituality, philosophy, and find wisdom from ancient teachings with'}{' '}
                  <strong>{selectedPersonality.name}</strong>.
                </p>
                <p style={{
                  fontSize: '1rem',
                  opacity: 0.8,
                  marginBottom: '2rem',
                  fontStyle: 'italic'
                }}>
                  {selectedPersonality.description}
                </p>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: '1rem',
                  maxWidth: '800px',
                  margin: '0 auto'
                }}>
                  {quickPrompts.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => setInputText(prompt)}
                      style={{
                        background: 'rgba(255, 255, 255, 0.1)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        color: 'white',
                        padding: '1rem',
                        borderRadius: '0.75rem',
                        cursor: 'pointer',
                        textAlign: 'left',
                        fontSize: '0.9rem',
                        lineHeight: '1.4',
                        transition: 'all 0.3s ease',
                        backdropFilter: 'blur(10px)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = 'none';
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

        {/* Messages */}
        <div style={{
          flex: '1',
          marginBottom: '2rem',
          overflowY: 'auto'
        }}>
          {messages.map((message) => (
            <div key={message.id} style={{
              display: 'flex',
              justifyContent: message.isUser ? 'flex-end' : 'flex-start',
              marginBottom: '1rem'
            }}>
              <div style={{
                maxWidth: '70%',
                background: message.isUser 
                  ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)' 
                  : 'rgba(255, 255, 255, 0.1)',
                borderRadius: '1rem',
                padding: '1rem',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}>
                {!message.isUser && (
                  <div style={{
                    fontSize: '0.8rem',
                    opacity: 0.8,
                    marginBottom: '0.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span>🎭</span> {selectedPersonality?.display_name || 'Spiritual Guide'}
                  </div>
                )}
                <div style={{
                  fontSize: '0.95rem',
                  lineHeight: '1.5'
                }}>
                  {message.isUser ? (
                    <div>{message.text}</div>
                  ) : (
                    <ReactMarkdown>{message.text}</ReactMarkdown>
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
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '1rem',
              padding: '1.5rem 2rem',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem'
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
                      background: 'white',
                      borderRadius: '50%',
                      animation: `pulse 1.5s ease-in-out ${i * 0.2}s infinite`
                    }}
                  />
                ))}
              </div>
              <span style={{ fontSize: '0.9rem' }}>
                {selectedPersonality?.display_name || 'Your guide'} is reflecting...
              </span>
            </div>
          </div>
        )}

        {/* Enhanced Input Form */}
        <form 
          onSubmit={handleSubmit}
          style={{
            position: 'sticky',
            bottom: '1rem',
            background: selectedPersonality ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
            borderRadius: '1.5rem',
            padding: '1rem',
            backdropFilter: 'blur(10px)',
            border: `1px solid ${selectedPersonality ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)'}`,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            display: 'flex',
            gap: '1rem',
            alignItems: 'center',
            opacity: selectedPersonality ? 1 : 0.6,
            pointerEvents: selectedPersonality ? 'auto' : 'none'
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
              background: selectedPersonality ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${selectedPersonality ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)'}`,
              borderRadius: '1rem',
              padding: '1rem 1.5rem',
              color: 'white',
              fontSize: '1rem',
              outline: 'none',
              backdropFilter: 'blur(10px)',
              cursor: selectedPersonality ? 'text' : 'not-allowed'
            }}
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading || !selectedPersonality}
            style={{
              background: inputText.trim() && !isLoading && selectedPersonality
                ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)' 
                : 'rgba(255, 255, 255, 0.1)',
              border: 'none',
              borderRadius: '1rem',
              padding: '1rem',
              color: 'white',
              cursor: inputText.trim() && !isLoading && selectedPersonality ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minWidth: '3rem',
              transition: 'all 0.3s ease',
              boxShadow: inputText.trim() && !isLoading && selectedPersonality ? '0 4px 12px rgba(59, 130, 246, 0.3)' : 'none'
            }}
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
