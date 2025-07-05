import React, { useState, useEffect, useRef } from 'react';
import { Send, Copy, Heart } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import '../styles/spiritual-theme.css';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  isTyping?: boolean;
  isFavorite?: boolean;
}

export default function CleanSpiritualInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + Enter to send message
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (inputText.trim() && !isLoading) {
          handleSubmit(e as any);
        }
      }
      // Escape to clear input
      if (e.key === 'Escape') {
        setInputText('');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [inputText, isLoading]);

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // Could add a toast notification here
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const toggleFavorite = (messageId: string) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, isFavorite: !msg.isFavorite } : msg
    ));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

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
    setIsTyping(true);

    // Add typing indicator
    const typingMessage: Message = {
      id: `typing-${Date.now()}`,
      text: '',
      isUser: false,
      timestamp: new Date(),
      isTyping: true
    };
    setMessages(prev => [...prev, typingMessage]);

    try {
      // Get conversation context (last 4 messages for context)
      const recentMessages = messages.slice(-4).map(msg => ({
        role: msg.isUser ? 'user' : 'assistant',
        content: msg.text
      }));

      // Call real spiritual guidance API with conversation context
      const response = await fetch('https://vimarsh-backend-app.azurewebsites.net/api/spiritual_guidance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: question,
          language: 'English',
          include_citations: true,
          voice_enabled: false,
          conversation_context: recentMessages
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      const apiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isUser: false,
        timestamp: new Date()
      };
      
      // Remove typing indicator and add real response
      setMessages(prev => prev.filter(msg => !msg.isTyping).concat(apiResponse));
      
    } catch (error) {
      console.error('Error calling spiritual guidance API:', error);
      
      // Fallback response for errors
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: "🙏 I'm having trouble connecting to the spiritual guidance service. Please check your connection and try again, dear soul. (Frontend Error)",
        isUser: false,
        timestamp: new Date()
      };
      
      // Remove typing indicator and add error response
      setMessages(prev => prev.filter(msg => !msg.isTyping).concat(errorResponse));
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const quickPrompts = [
    {
      category: "dharma",
      icon: "🎯",
      question: "How can I find my dharma and live according to my true purpose?",
      description: "Discover your life's sacred mission"
    },
    {
      category: "equanimity",
      icon: "⚖️",
      question: "How can I maintain equanimity during life's ups and downs?",
      description: "Find balance through life's challenges"
    },
    {
      category: "yoga",
      icon: "🧘",
      question: "What are the different paths of yoga and which one suits me?",
      description: "Explore the sacred paths of union"
    },
    {
      category: "emotions",
      icon: "💫",
      question: "How do I overcome anger and jealousy through spiritual practice?",
      description: "Transform negative emotions into wisdom"
    },
    {
      category: "meditation",
      icon: "🪷",
      question: "What is the best way to start a meditation practice?",
      description: "Begin your journey into inner peace"
    },
    {
      category: "karma",
      icon: "🔄",
      question: "How does karma work and how can I create positive karma?",
      description: "Understand the law of cause and effect"
    }
  ];

  return (
    <div className="container">
      {/* Header */}
      <header className="header enhanced">
        <div className="logo enhanced">
          <div className="logo-icon enhanced">
            <span className="om-symbol">🕉</span>
          </div>
          <div className="logo-text enhanced">
            <h1>Vimarsh</h1>
            <p>Spiritual Guidance</p>
          </div>
        </div>
      </header>

      {/* Compact Welcome Section */}
      {messages.length === 0 && (
        <div className="welcome compact">
          <div className="welcome-hero">
            <div className="welcome-icon">
              <span className="lotus-symbol">🪷</span>
            </div>
            <h2>Seek Wisdom from Lord Krishna</h2>
            <p className="welcome-subtitle">
              Ask questions about dharma, karma, meditation, and the path to inner peace.
            </p>
          </div>
          
          <div className="quick-prompts-section">
            <div className="quick-prompts compact">
              {quickPrompts.slice(0, 3).map((prompt, index) => (
                <button
                  key={index}
                  className="prompt-btn compact"
                  onClick={() => setInputText(prompt.question)}
                >
                  <span className="prompt-icon">{prompt.icon}</span>
                  <span className="prompt-text">{prompt.question}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.isUser ? 'user' : 'assistant'} ${message.isTyping ? 'typing' : ''}`}>
              <div className="message-content">
                {!message.isUser && (
                  <div className="persona">
                    <span className="persona-icon">🎭</span> 
                    <span className="persona-name">Lord Krishna</span>
                  </div>
                )}
                <div className="message-text">
                  {message.isTyping ? (
                    <div className="typing-indicator">
                      <span className="dot"></span>
                      <span className="dot"></span>
                      <span className="dot"></span>
                    </div>
                  ) : message.isUser ? (
                    <div>{message.text}</div>
                  ) : (
                    <ReactMarkdown>{message.text}</ReactMarkdown>
                  )}
                </div>
                {!message.isTyping && (
                  <div className="message-actions">
                    <div className="timestamp">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                    {!message.isUser && (
                      <div className="action-buttons">
                        <button 
                          className="action-btn"
                          onClick={() => copyToClipboard(message.text)}
                          title="Copy message"
                        >
                          <Copy size={14} />
                        </button>
                        <button 
                          className={`action-btn ${message.isFavorite ? 'active' : ''}`}
                          onClick={() => toggleFavorite(message.id)}
                          title="Add to favorites"
                        >
                          <Heart size={14} />
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
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
      <form className="input-form enhanced" onSubmit={handleSubmit}>
        <div className="input-container">
          <input
            className="input-field enhanced"
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask your spiritual question..."
            disabled={isLoading}
          />
          <div className="input-actions">
            <button
              className="send-btn enhanced"
              type="submit"
              disabled={!inputText.trim() || isLoading}
              title="Send message (Ctrl+Enter)"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
        <div className="input-hint">
          <span>Press Enter to send • Ctrl+Enter for quick send • Esc to clear</span>
        </div>
      </form>
    </div>
  );
}
