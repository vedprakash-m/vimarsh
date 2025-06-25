import React, { useState } from 'react';
import VoiceInterface from './VoiceInterface';
import ResponseDisplay from './ResponseDisplay';
import ConversationHistory from './ConversationHistory';
import ConversationArchive from './ConversationArchive';
import SessionManager from './SessionManager';
import PWAManager from './PWAManager';
import PrivacySettings from './PrivacySettings';
import { useSpiritualChat } from '../hooks/useSpiritualChat';
import { useAuth } from './AuthenticationWrapper';
import { useLanguage, getLanguageCode } from '../contexts/LanguageContext';
import { usePWA } from '../utils/pwa';
import { useSpiritualGuidanceTest } from '../hooks/useABTest';

interface Citation {
  source: string;
  reference: string;
  verse?: string;
  chapter?: string;
  book?: string;
}

const SpiritualGuidanceInterface: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const { currentLanguage, t } = useLanguage();
  const [inputMessage, setInputMessage] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [showArchive, setShowArchive] = useState(false);
  const [showPrivacySettings, setShowPrivacySettings] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  
  // A/B Testing integration
  const { interfaceConfig, responseConfig, trackGuidanceInteraction, trackGuidanceConversion } = useSpiritualGuidanceTest();
  
  const {
    messages,
    isLoading,
    sendMessage,
    sessionId,
    newConversation,
    loadSession
  } = useSpiritualChat();

  const languageCode = getLanguageCode(currentLanguage);

  // Update current session ID when hook session changes
  React.useEffect(() => {
    setCurrentSessionId(sessionId);
  }, [sessionId]);

  const handleNewConversation = () => {
    const newSessionId = newConversation();
    setCurrentSessionId(newSessionId);
    setInputMessage('');
    setShowHistory(false);
  };

  const handleSessionSelect = (selectedSessionId: string) => {
    const success = loadSession(selectedSessionId);
    if (success) {
      setCurrentSessionId(selectedSessionId);
      setShowHistory(false);
    }
  };

  const handleToggleHistory = () => {
    setShowHistory(!showHistory);
    setShowArchive(false); // Close archive when opening history
  };

  const handleToggleArchive = () => {
    setShowArchive(!showArchive);
    setShowHistory(false); // Close history when opening archive
  };

  const handleTogglePrivacySettings = () => {
    setShowPrivacySettings(!showPrivacySettings);
  };

  if (!isAuthenticated) {
    return (
      <div className="spiritual-guidance-interface flex items-center justify-center min-h-screen bg-gradient-to-br from-saffron-light to-lotus-white">
        <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-md">
          <div className="text-6xl mb-4">🕉️</div>
          <h2 className="heading-3 mb-4 text-neutral-800">
            {t('welcomeToVimarsh')}
          </h2>
          <p className="body-text text-neutral-600 mb-6">
            {t('pleaseSignIn')}
          </p>
          <div className="space-y-3">
            <div className="flex items-center text-sm text-neutral-500">
              <span className="mr-2">🙏</span>
              <span>Authentic spiritual guidance</span>
            </div>
            <div className="flex items-center text-sm text-neutral-500">
              <span className="mr-2">📚</span>
              <span>Based on sacred texts</span>
            </div>
            <div className="flex items-center text-sm text-neutral-500">
              <span className="mr-2">💫</span>
              <span>Personalized spiritual counseling</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    // Track A/B test interaction
    trackGuidanceInteraction('message_sent', { 
      messageLength: inputMessage.length,
      language: currentLanguage,
      sessionId: sessionId 
    });

    try {
      await sendMessage(inputMessage);
      setInputMessage('');
      
      // Track successful message conversion
      trackGuidanceConversion('message_completed', {
        language: currentLanguage,
        sessionId: sessionId
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      // Track error for A/B testing
      trackGuidanceInteraction('message_error', { 
        error: error instanceof Error ? error.message : 'Unknown error' 
      });
    }
  };

  const handleVoiceInput = (text: string) => {
    setInputMessage(text);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleCitationClick = (citation: Citation) => {
    // TODO: Implement citation detail view
    console.log('Citation clicked:', citation);
  };

  const handleSpeakResponse = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = languageCode === 'hi' ? 'hi-IN' : 'en-US';
      utterance.rate = 0.8;
      utterance.pitch = 1.0;
      utterance.volume = 0.9;
      
      // Find appropriate voice
      const voices = speechSynthesis.getVoices();
      const preferredVoice = voices.find(voice => 
        voice.lang.startsWith(languageCode)
      );
      
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      
      speechSynthesis.speak(utterance);
    }
  };

  // Calculate layout classes based on A/B test configuration
  const getLayoutClasses = () => {
    const baseClasses = "spiritual-guidance-interface flex h-full";
    return interfaceConfig.layout === 'enhanced' 
      ? `${baseClasses} enhanced-layout` 
      : baseClasses;
  };

  const getVoiceButtonSize = () => {
    switch (interfaceConfig.voiceButtonSize) {
      case 'large': return 'voice-button-large';
      case 'small': return 'voice-button-small';
      default: return 'voice-button-medium';
    }
  };

  return (
    <>
      <PWAManager />
      <a href="#main-content" className="skip-link">
        {t('skipToMainContent')}
      </a>
      
      <div className={getLayoutClasses()} role="application" aria-label={t('spiritualGuidanceApp')}>
        {/* Main Chat Interface */}
        <main className="flex-1 flex flex-col" id="main-content" tabIndex={-1}>
          <div className="container-narrow flex-1 flex flex-col">
            {/* Header with Session Management */}
            <header className="header flex items-center justify-between mb-6 bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-4">
                <span className="text-2xl sacred-icon" aria-hidden="true">🕉️</span>
                <h1 className="heading-3 mb-0">
                  {t('spiritualGuidance')}
                </h1>
              </div>
              
              <div className="flex items-center gap-3" role="toolbar" aria-label={t('conversationControls')}>
                <SessionManager
                  currentSessionId={currentSessionId}
                  onSessionChange={handleSessionSelect}
                  onNewSession={handleNewConversation}
                />
                
                <button
                  onClick={handleToggleHistory}
                  className={`btn btn-secondary btn-icon ${showHistory ? 'bg-saffron-light' : ''}`}
                  title={t('conversationHistory')}
                  aria-label={showHistory ? t('hideHistory') : t('showHistory')}
                  aria-pressed={showHistory}
                  type="button"
                >
                  <span aria-hidden="true">📚</span>
                  <span className="sr-only">{t('conversationHistory')}</span>
                </button>

                <button
                  onClick={handleToggleArchive}
                  className={`btn btn-secondary btn-icon ${showArchive ? 'bg-saffron-light' : ''}`}
                  title={t('conversationArchive')}
                  aria-label={showArchive ? t('hideArchive') : t('showArchive')}
                  aria-pressed={showArchive}
                  type="button"
                >
                  <span aria-hidden="true">🗂️</span>
                  <span className="sr-only">{t('conversationArchive')}</span>
                </button>

                <button
                  onClick={handleTogglePrivacySettings}
                  className={`btn btn-secondary btn-icon ${showPrivacySettings ? 'bg-saffron-light' : ''}`}
                  title="Privacy Settings"
                  aria-label={showPrivacySettings ? "Hide Privacy Settings" : "Show Privacy Settings"}
                  aria-pressed={showPrivacySettings}
                  type="button"
                >
                  <span aria-hidden="true">🔒</span>
                  <span className="sr-only">Privacy Settings</span>
                </button>
              </div>
            </header>

            {/* Welcome Section */}
            <section className="welcome-section card card-sacred text-center mb-6" aria-labelledby="welcome-heading">
              <h2 id="welcome-heading" className="sr-only">{t('welcomeHeading')}</h2>
              <p className="body-text text-neutral-600">
                {currentLanguage === 'Hindi' 
                  ? 'धर्म के बारे में प्रश्न पूछें, पवित्र ग्रंथों से ज्ञान प्राप्त करें, या अपनी आध्यात्मिक साधना के लिए मार्गदर्शन पाएं।'
                  : 'Ask questions about dharma, seek wisdom from sacred texts, or find guidance for your spiritual practice.'
                }
              </p>
            </section>            {/* Chat Messages Area */}
            <section 
              className="chat-area flex-1 overflow-y-auto space-y-4 px-4 py-2" 
              aria-live="polite"
              aria-label={t('conversationMessages')}
              role="log"
            >
              {messages.length === 0 ? (
                <div className="text-center py-8" role="status">
                  <div className="text-4xl mb-4" aria-hidden="true">🙏</div>
                  <p className="text-neutral-500">
                    {t('startConversation')}
                  </p>
                </div>
              ) : (
                messages.map((message, index) => (
                  <div
                    key={message.id || index}
                    className={`message flex ${
                      message.sender === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                    data-sender={message.sender}
                    role="article"
                    aria-label={`${message.sender === 'user' ? t('yourMessage') : t('lordKrishnaMessage')} ${index + 1}`}
                  >
                    {message.sender === 'user' ? (
                      <div className="bg-saffron-primary text-white rounded-lg p-4 max-w-3xl">
                        <div className="sr-only">{t('yourMessage')}:</div>
                        <p className="body-text">{message.text}</p>
                        <div className="message-timestamp sr-only">
                          {new Date(message.timestamp).toLocaleString()}
                        </div>
                      </div>
                    ) : (
                      <div role="article" aria-label={t('lordKrishnaResponse')}>
                        <div className="sr-only">{t('lordKrishnaMessage')}:</div>
                        <ResponseDisplay
                          response={{
                            ...message,
                            citations: message.citations || []
                          }}
                          onCitationClick={handleCitationClick}
                          onSpeakResponse={handleSpeakResponse}
                        />
                      </div>
                    )}
                  </div>
                ))
              )}
              
              {isLoading && (
                <div className="flex justify-start" role="status" aria-live="polite">
                  <div className="bg-white rounded-lg p-4 shadow-sm border border-neutral-200">
                    <div className="flex items-center space-x-2">
                      <div 
                        className="loading-spinner animate-spin rounded-full h-4 w-4 border-b-2 border-saffron-primary"
                        aria-hidden="true"
                      ></div>
                      <span>{t('lordKrishnaIsTyping')}</span>
                    </div>
                  </div>
                </div>
              )}
            </section>

          {/* Input Area */}
          <div className="input-area bg-white p-4 rounded-lg shadow-sm border border-neutral-200 mt-4">
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={
                    currentLanguage === 'Hindi'
                      ? 'अपना प्रश्न यहाँ लिखें... (Enter दबाएं)'
                      : 'Ask your question here... (Press Enter to send)'
                  }
                  className="w-full p-3 border border-neutral-300 rounded-lg resize-none focus:ring-2 focus:ring-saffron-primary focus:border-transparent"
                  rows={3}
                  disabled={isLoading}
                />
              </div>
              
              <div className="input-actions flex flex-col gap-2">
                <div className={getVoiceButtonSize()}>
                  <VoiceInterface
                    onVoiceInput={handleVoiceInput}
                    language={languageCode}
                    disabled={isLoading}
                  />
                </div>
                
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  className="btn btn-primary px-6"
                >
                  {isLoading ? (
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>{t('sending')}</span>
                    </div>
                  ) : (
                    <span>{t('send')}</span>
                  )}
                </button>
              </div>
            </div>
            </div>
          </div>
        </main>
        
        {/* Conversation History Sidebar */}
        {showHistory && (
          <aside 
            className="region" 
            aria-label={t('conversationHistory')}
            role="region"
          >
            <ConversationHistory
              onSessionSelect={handleSessionSelect}
              currentSessionId={currentSessionId}
              onNewConversation={handleNewConversation}
            />
          </aside>
        )}

        {/* Conversation Archive Sidebar */}
        {showArchive && (
          <aside 
            className="region" 
            aria-label={t('conversationArchive')}
            role="region"
          >
            <ConversationArchive
              onSessionSelect={handleSessionSelect}
              currentSessionId={currentSessionId}
            />
          </aside>
        )}
      </div>

      {/* Privacy Settings Modal */}
      <PrivacySettings
        isOpen={showPrivacySettings}
        onClose={handleTogglePrivacySettings}
      />
    </>
  );
};

export default SpiritualGuidanceInterface;
