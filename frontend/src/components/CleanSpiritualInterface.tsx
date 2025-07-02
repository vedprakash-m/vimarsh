import React, { useState } from 'react';
import { Send, Mic, MicOff } from 'lucide-react';
import '../styles/spiritual-theme.css';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export default function CleanSpiritualInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);

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

    // Simulate API response
    setTimeout(() => {
      const response: Message = {
        id: (Date.now() + 1).toString(),
        text: `🙏 Thank you for asking: "${question}"\n\nThis is a spiritual guidance response. In the Bhagavad Gita, Krishna teaches us about finding peace through self-realization and dharma. Your question touches upon the eternal wisdom that guides us toward inner harmony.`,
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, response]);
      setIsLoading(false);
    }, 1500);
  };

  const quickPrompts = [
    "What is the meaning of life according to the Bhagavad Gita?",
    "How can I find inner peace?",
    "What does Krishna teach about duty?",
    "How to practice mindfulness?"
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
        <button
          className={`voice-btn ${isListening ? 'active' : ''}`}
          onClick={() => setIsListening(!isListening)}
        >
          {isListening ? <MicOff size={18} /> : <Mic size={18} />}
        </button>
      </header>

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
              <div>{message.text}</div>
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
    </div>
  );
}
