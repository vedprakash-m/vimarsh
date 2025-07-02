import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, ArrowLeft, ThumbsUp, ThumbsDown, Copy, Share2, Book } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  citations?: string[];
}

interface ConversationInterfaceProps {
  onBack: () => void;
}

const ConversationInterface: React.FC<ConversationInterfaceProps> = ({ onBack }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

    // Simulate API response with Krishna's wisdom
    setTimeout(() => {
      const responses = [
        {
          text: `🙏 Dear seeker, your question about life's purpose touches the very essence of dharma. In the Bhagavad Gita, I teach Arjuna that true purpose is found not in the fruits of action, but in righteous action itself.\n\n"You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty."\n\nYour dharma is unique to you - it is the path of righteousness that aligns with your nature and serves the greater good. When you act without attachment to results, performing your duty with devotion, you discover your true purpose.`,
          citations: ['Bhagavad Gita 2.47', 'Bhagavad Gita 3.8']
        },
        {
          text: `🌸 Beloved child, inner peace is your birthright, not something to be achieved but something to be remembered. The mind, like wind, is restless by nature, but through practice and detachment, it can be stilled.\n\n"For one who has conquered the mind, the mind is the best of friends; but for one who has failed to do so, his very mind will be the greatest enemy."\n\nPractice yoga - not merely physical postures, but the union of your individual consciousness with the divine. Through meditation, selfless service, and surrender to the divine will, you will find the peace that surpasses understanding.`,
          citations: ['Bhagavad Gita 6.6', 'Bhagavad Gita 6.19']
        }
      ];
      
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      
      const response: Message = {
        id: (Date.now() + 1).toString(),
        text: randomResponse.text,
        isUser: false,
        timestamp: new Date(),
        citations: randomResponse.citations
      };
      setMessages(prev => [...prev, response]);
      setIsLoading(false);
    }, 2000);
  };

  const handleVoiceToggle = () => {
    setIsListening(!isListening);
    // Voice implementation would go here
  };

  const suggestedQuestions = [
    "How do I practice detachment?",
    "What is the nature of the soul?",
    "How can I serve others selflessly?",
    "What is true knowledge?"
  ];

  return (
    <div className="conversation-interface">
      {/* Header */}
      <header className="conversation-header">
        <button className="back-button" onClick={onBack}>
          <ArrowLeft />
        </button>
        <div className="header-info">
          <div className="krishna-indicator">
            <div className="avatar-small">🎭</div>
            <div>
              <h3>Lord Krishna</h3>
              <p>Divine Guide</p>
            </div>
          </div>
        </div>
        <button 
          className={`voice-toggle ${isListening ? 'listening' : ''}`}
          onClick={handleVoiceToggle}
        >
          {isListening ? <MicOff /> : <Mic />}
        </button>
      </header>

      {/* Messages Container */}
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <div className="welcome-avatar">
              <div className="avatar-large">🎭</div>
              <div className="divine-aura"></div>
            </div>
            <h2>Namaste, Spiritual Seeker</h2>
            <p>I am here to guide you with timeless wisdom from the sacred texts. What weighs on your heart today?</p>
            
            <div className="suggested-questions">
              <p>You might ask:</p>
              <div className="suggestions-grid">
                {suggestedQuestions.map((question, index) => (
                  <button 
                    key={index}
                    className="suggestion-chip"
                    onClick={() => setInputText(question)}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message ${message.isUser ? 'user' : 'assistant'}`}>
            {!message.isUser && (
              <div className="message-avatar">
                <div className="avatar-small">🎭</div>
              </div>
            )}
            <div className="message-content">
              <div className="message-text">
                {message.text}
              </div>
              {message.citations && (
                <div className="citations">
                  <div className="citations-header">
                    <Book className="citation-icon" />
                    <span>Sacred Sources:</span>
                  </div>
                  <div className="citation-list">
                    {message.citations.map((citation, index) => (
                      <span key={index} className="citation">{citation}</span>
                    ))}
                  </div>
                </div>
              )}
              {!message.isUser && (
                <div className="message-actions">
                  <button className="action-btn" title="Helpful">
                    <ThumbsUp />
                  </button>
                  <button className="action-btn" title="Not helpful">
                    <ThumbsDown />
                  </button>
                  <button className="action-btn" title="Copy">
                    <Copy />
                  </button>
                  <button className="action-btn" title="Share">
                    <Share2 />
                  </button>
                </div>
              )}
            </div>
            {message.isUser && (
              <div className="message-avatar user-avatar">
                <div className="avatar-small user">👤</div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">
              <div className="avatar-small">🎭</div>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <div className="divine-thinking">
                  <div className="lotus-bloom">
                    <div className="petal"></div>
                    <div className="petal"></div>
                    <div className="petal"></div>
                    <div className="petal"></div>
                  </div>
                  <span>Seeking wisdom from sacred texts...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-area">
        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-container">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={isListening ? "Listening..." : "Ask your spiritual question..."}
              className={`message-input ${isListening ? 'listening' : ''}`}
              disabled={isLoading || isListening}
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={!inputText.trim() || isLoading}
            >
              <Send />
            </button>
          </div>
        </form>
        <p className="input-hint">
          🙏 Ask with respect and receive wisdom with reverence
        </p>
      </div>
    </div>
  );
};

export default ConversationInterface;
