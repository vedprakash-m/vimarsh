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

  const quickPrompts = [
    "How can I find my dharma and live according to my true purpose?",
    "How can I maintain equanimity during life's ups and downs?",
    "What are the different paths of yoga and which one suits me?",
    "How do I overcome anger and jealousy through spiritual practice?"
  ];

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="logo">
          <div className="logo-icon">🕉</div>
          <div className="logo-text">
            <h1>Vimarsh</h1>
            <p>Spiritual Guidance</p>
          </div>
        </div>
        
        {/* Personality Selector Toggle */}
        <div className="personality-header">
          <div className="current-personality">
            <span className="personality-name">
              {selectedPersonality?.display_name || 'Loading...'}
            </span>
            <span className="personality-domain">
              {selectedPersonality?.domain || 'spiritual'}
            </span>
          </div>
          <button 
            className="personality-toggle-btn"
            onClick={() => setShowPersonalitySelector(!showPersonalitySelector)}
            title="Change Personality"
            disabled={!selectedPersonality}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"/>
            </svg>
          </button>
        </div>
        
        <button
          className={`voice-btn ${isListening ? 'active' : ''}`}
          onClick={() => setIsListening(!isListening)}
        >
          {isListening ? <MicOff size={18} /> : <Mic size={18} />}
        </button>
      </header>

      {/* Personality Selector Modal */}
      {showPersonalitySelector && (
        <div className="personality-selector-overlay">
          <div className="personality-selector-modal">
            {/* Temporarily simplified selector */}
            <div style={{ padding: '20px', background: 'white', borderRadius: '8px' }}>
              <h3>Select Personality</h3>
              <div style={{ display: 'grid', gap: '10px', marginTop: '15px' }}>
                {availablePersonalities.map((personality) => (
                  <button
                    key={personality.id}
                    onClick={() => handlePersonalitySelect(personality)}
                    style={{
                      padding: '10px',
                      border: selectedPersonality?.id === personality.id ? '2px solid #007bff' : '1px solid #ccc',
                      background: selectedPersonality?.id === personality.id ? '#f0f8ff' : 'white',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      textAlign: 'left'
                    }}
                  >
                    <div style={{ fontWeight: 'bold' }}>{personality.display_name}</div>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>{personality.description}</div>
                    <div style={{ fontSize: '0.8em', color: '#888' }}>{personality.domain}</div>
                  </button>
                ))}
              </div>
            </div>
            <button 
              className="close-personality-selector"
              onClick={() => setShowPersonalitySelector(false)}
              style={{
                position: 'absolute',
                top: '10px',
                right: '10px',
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer'
              }}
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <>
        {/* Welcome Section */}
        {messages.length === 0 && (
            <div className="welcome">
              <div className="welcome-icon">🏵️</div>
              <h2>Welcome to Your Spiritual Journey</h2>
              <p>Ask questions about spirituality, philosophy, and find wisdom from ancient teachings.</p>
              
              <div className="quick-prompts">
                {quickPrompts.map((prompt, index) => (
                  <button
                key={index}
                className="prompt-btn"
                onClick={() => setInputText(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.isUser ? 'user' : 'assistant'}`}>
              <div className="message-content">
                {!message.isUser && (
                  <div className="persona">
                    <span>🎭</span> Lord Krishna
                  </div>
                )}
                <div className="message-text">
                  {message.isUser ? (
                    <div>{message.text}</div>
                  ) : (
                    <ReactMarkdown>{message.text}</ReactMarkdown>
                  )}
                </div>
                <div className="timestamp">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
          </div>
        ))}
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="loading">
          <div className="loading-content">
            <div className="loading-dots">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
            <span>Krishna is reflecting...</span>
          </div>
        </div>
      )}

      {/* Input Form */}
      <form className="input-form" onSubmit={handleSubmit}>
        <input
          className="input-field"
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask your spiritual question..."
        />
        <button
          className="send-btn"
          type="submit"
          disabled={!inputText.trim() || isLoading}
        >
          <Send size={16} />
        </button>
      </form>
      </>
    </div>
  );
}
