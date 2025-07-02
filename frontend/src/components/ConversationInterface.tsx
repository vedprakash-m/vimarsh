import React, { useState } from 'react';
import { ArrowLeft, Send, Mic } from 'lucide-react';

interface ConversationInterfaceProps {
  onBack: () => void;
}

const ConversationInterface: React.FC<ConversationInterfaceProps> = ({ onBack }) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Array<{id: string, text: string, isUser: boolean, citations?: any[]}>>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    const userQuery = message.trim(); // Save the message before clearing
    
    // Add user message
    const userMessage = { id: Date.now().toString(), text: userQuery, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setMessage(''); // Clear input immediately
    
    // Add loading message
    const loadingId = (Date.now() + 1).toString();
    const loadingMessage = { id: loadingId, text: "🙏 Seeking divine wisdom...", isUser: false };
    setMessages(prev => [...prev, loadingMessage]);
    
    try {
      // Call the real spiritual guidance API
      const response = await fetch('/api/spiritual_guidance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userQuery, // Use saved message
          language: 'English',
          include_citations: true,
          voice_enabled: false
        })
      });
      
      if (!response.ok) {
        throw new Error(`API call failed: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Remove loading message and add real response
      setMessages(prev => prev.filter(msg => msg.id !== loadingId));
      
      const krishnaResponse = {
        id: (Date.now() + 2).toString(),
        text: data.response,
        isUser: false,
        citations: data.citations
      };
      setMessages(prev => [...prev, krishnaResponse]);
      
    } catch (error) {
      console.error('Failed to get spiritual guidance:', error);
      
      // Remove loading message and show error
      setMessages(prev => prev.filter(msg => msg.id !== loadingId));
      
      const errorResponse = {
        id: (Date.now() + 2).toString(),
        text: "I apologize, dear devotee, but I am experiencing some difficulty in providing guidance at this moment. Please try again shortly, and I shall guide you with wisdom from the eternal teachings.",
        isUser: false
      };
      setMessages(prev => [...prev, errorResponse]);
    }
  };

  return (
    <div className="conversation-interface">
      {/* Clean Header */}
      <header className="conversation-header">
        <button className="back-button" onClick={onBack}>
          <ArrowLeft size={20} />
          <span>Back to Home</span>
        </button>
        <div className="conversation-title">
          <div className="title-content">
            <span className="krishna-symbol">🕉</span>
            <div>
              <h1>Lord Krishna</h1>
              <p>Divine Guide</p>
            </div>
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <main className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-state">
            <div className="welcome-content">
              <span className="welcome-symbol">🌸</span>
              <h2>Welcome, beloved seeker</h2>
              <p>Ask me about dharma, life's purpose, or any spiritual guidance you seek. I am here to share the eternal wisdom of the sacred texts.</p>
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map(msg => (
              <div key={msg.id} className={`message ${msg.isUser ? 'user-message' : 'krishna-message'}`}>
                <div className="message-content">
                  {!msg.isUser && <span className="avatar">🕉</span>}
                  <div className="message-text">
                    {msg.text}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="citations">
                        <p className="citations-title">📚 Sacred Sources:</p>
                        {msg.citations.map((citation, index) => (
                          <div key={index} className="citation">
                            <strong>{citation.source}</strong> {citation.chapter}:{citation.verse}
                            {citation.sanskrit && (
                              <div className="sanskrit-citation">{citation.sanskrit}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Input Area */}
      <footer className="input-area">
        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-container">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask your spiritual question..."
              className="message-input"
            />
            <button type="button" className="voice-button">
              <Mic size={20} />
            </button>
            <button type="submit" className="send-button" disabled={!message.trim()}>
              <Send size={20} />
            </button>
          </div>
        </form>
        <p className="guidance-text">🙏 Ask with respect and receive wisdom with reverence</p>
      </footer>
    </div>
  );
};

export default ConversationInterface;
