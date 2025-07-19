import React, { useState } from 'react';
import { Send, Mic, MicOff, Shield, MessageSquare } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useAdmin } from '../contexts/AdminContext';
import AdminDashboard from './admin/AdminDashboard';
import { getApiBaseUrl } from '../config/environment';
import '../styles/spiritual-theme.css';
import '../styles/admin.css';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

type AppTab = 'guidance' | 'admin';

export default function CleanSpiritualInterface() {
  const { user } = useAdmin();
  const [activeTab, setActiveTab] = useState<AppTab>('guidance');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);

  // Debug logging for admin user
  React.useEffect(() => {
    console.log('🎨 CleanSpiritualInterface - user state:', user);
    if (user) {
      console.log('🔍 Admin check details:', {
        isAdmin: user.isAdmin,
        role: user.role,
        email: user.email
      });
    }
  }, [user]);

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
          conversation_context: recentMessages
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
        
        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button
            className={`tab-btn ${activeTab === 'guidance' ? 'active' : ''}`}
            onClick={() => setActiveTab('guidance')}
          >
            <MessageSquare size={18} />
            <span>Guidance</span>
          </button>
          
          {user?.isAdmin && (
            <button
              className={`tab-btn ${activeTab === 'admin' ? 'active' : ''}`}
              onClick={() => setActiveTab('admin')}
            >
              <Shield size={18} />
              <span>Admin</span>
            </button>
          )}
        </div>
        
        <button
          className={`voice-btn ${isListening ? 'active' : ''}`}
          onClick={() => setIsListening(!isListening)}
        >
          {isListening ? <MicOff size={18} /> : <Mic size={18} />}
        </button>
      </header>

      {/* Content based on active tab */}
      {activeTab === 'admin' && user?.isAdmin ? (
        <AdminDashboard />
      ) : (
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
      )}
    </div>
  );
}
