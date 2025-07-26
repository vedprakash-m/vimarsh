import React, { useState } from 'react';
import VoiceInterface from './VoiceInterface';
import ResponseDisplay from './ResponseDisplay';
import ConversationHistory from './ConversationHistory';
import ConversationArchive from './ConversationArchive';
import SessionManager from './SessionManager';
import PWAManager from './PWAManager';
import PrivacySettings from './PrivacySettings';
import PersonalitySelector from './PersonalitySelector';
import { useSpiritualChat } from '../hooks/useSpiritualChat';

// Personality type definition
interface Personality {
  id: string;
  name: string;
  display_name: string;
  domain: 'spiritual' | 'scientific' | 'historical' | 'philosophical' | 'literary' | 'political';
  time_period: string;
  description: string;
  expertise_areas: string[];
  cultural_context: string;
  quality_score: number;
  usage_count: number;
  is_active: boolean;
  tags: string[];
}
import { useIsAuthenticated, useMsal } from '@azure/msal-react';
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
  const isAuthenticated = useIsAuthenticated();
  const { accounts } = useMsal();
  const user = accounts[0] || null;
  const { currentLanguage, t } = useLanguage();
  const [inputMessage, setInputMessage] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [showArchive, setShowArchive] = useState(false);
  const [showPrivacySettings, setShowPrivacySettings] = useState(false);
  const [showPersonalitySelector, setShowPersonalitySelector] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [selectedPersonality, setSelectedPersonality] = useState<any>(null);
  const [personalityLoading, setPersonalityLoading] = useState(false);
  const [personalitySwitchNotification, setPersonalitySwitchNotification] = useState<string | null>(null);
  
  // A/B Testing integration
  const { interfaceConfig, responseConfig, trackGuidanceInteraction, trackGuidanceConversion } = useSpiritualGuidanceTest();
  
  const {
    messages,
    isLoading,
    sendMessage,
    sessionId,
    newConversation,
    loadSession
  } = useSpiritualChat({
    personalityId: selectedPersonality?.id || 'krishna'
  });

  const languageCode = getLanguageCode(currentLanguage);

  // Update current session ID when hook session changes
  React.useEffect(() => {
    setCurrentSessionId(sessionId);
  }, [sessionId]);

  // Load saved personality on mount
  React.useEffect(() => {
    try {
      const savedPersonality = localStorage.getItem('vimarsh_selected_personality');
      if (savedPersonality) {
        const personality = JSON.parse(savedPersonality);
        setSelectedPersonality(personality);
      } else {
        // Set default Krishna personality
        setSelectedPersonality({
          id: 'krishna',
          name: 'Krishna',
          display_name: 'Lord Krishna',
          domain: 'spiritual',
          description: 'Divine teacher and guide from the Bhagavad Gita'
        });
      }
    } catch (error) {
      console.error('Failed to load saved personality:', error);
      // Set default Krishna personality on error
      setSelectedPersonality({
        id: 'krishna',
        name: 'Krishna',
        display_name: 'Lord Krishna',
        domain: 'spiritual',
        description: 'Divine teacher and guide from the Bhagavad Gita'
      });
    }
  }, []);

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
      // Apply personality-specific pronunciation corrections
      const processedText = applyPersonalityPronunciation(text);
      
      const utterance = new SpeechSynthesisUtterance(processedText);
      
      // Get personality-specific voice settings
      const voiceSettings = selectedPersonality?.voice_settings || {
        language: 'en-US',
        speaking_rate: 0.8,
        pitch: -1.0,
        volume: 0.9,
        voice_characteristics: {
          gender: 'male',
          age: 'middle',
          tone: 'reverent'
        }
      };
      
      // Configure voice parameters based on personality
      utterance.lang = languageCode === 'hi' ? 'hi-IN' : voiceSettings.language;
      utterance.rate = voiceSettings.speaking_rate;
      utterance.pitch = 1.0 + (voiceSettings.pitch / 10); // Convert to 0-2 range
      utterance.volume = voiceSettings.volume;
      
      // Find appropriate voice based on personality characteristics
      const voices = speechSynthesis.getVoices();
      const targetLang = languageCode === 'hi' ? 'hi' : voiceSettings.language.split('-')[0];
      
      let preferredVoice = null;
      
      if (voiceSettings.voice_name) {
        // Try to find the specific voice name
        preferredVoice = voices.find(voice => voice.name.includes(voiceSettings.voice_name!));
      }
      
      if (!preferredVoice && voiceSettings.voice_characteristics) {
        // Fallback to gender and characteristics-based selection
        const genderPreference = voiceSettings.voice_characteristics.gender;
        
        preferredVoice = voices.find(voice => {
          const voiceName = voice.name.toLowerCase();
          const langMatch = voice.lang.startsWith(targetLang);
          const genderMatch = genderPreference === 'female' ? 
            voiceName.includes('female') || voiceName.includes('woman') :
            voiceName.includes('male') || voiceName.includes('man') || !voiceName.includes('female');
          
          return langMatch && genderMatch;
        });
      }
      
      // Final fallback to any voice in the target language
      if (!preferredVoice) {
        preferredVoice = voices.find(voice => voice.lang.startsWith(targetLang));
      }
      
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      
      speechSynthesis.speak(utterance);
    }
  };

  const applyPersonalityPronunciation = (text: string): string => {
    if (!selectedPersonality?.pronunciation_guide) return text;
    
    let processedText = text;
    const pronunciationGuide = selectedPersonality.pronunciation_guide;
    
    // Apply pronunciation corrections for specialized terms
    Object.entries(pronunciationGuide).forEach(([term, guide]) => {
      const regex = new RegExp(`\\b${term}\\b`, 'gi');
      // For TTS, we can use phonetic representations
      const guideObj = guide as { phonetic: string };
      processedText = processedText.replace(regex, guideObj.phonetic);
    });
    
    return processedText;
  };

  const handlePersonalitySelect = async (personality: any) => {
    setPersonalityLoading(true);
    
    try {
      // Update selected personality
      setSelectedPersonality(personality);
      setShowPersonalitySelector(false);
      
      // Start a new conversation when switching personalities
      handleNewConversation();
      
      // Store selected personality in localStorage for persistence
      localStorage.setItem('vimarsh_selected_personality', JSON.stringify(personality));
      
      // Show switch notification
      setPersonalitySwitchNotification(`Now conversing with ${personality.display_name}`);
      setTimeout(() => setPersonalitySwitchNotification(null), 3000);
      
    } catch (error) {
      console.error('Failed to select personality:', error);
    } finally {
      setPersonalityLoading(false);
    }
  };

  const handleTogglePersonalitySelector = () => {
    setShowPersonalitySelector(!showPersonalitySelector);
  };

  // Get personality-specific placeholder text
  const getPersonalityPlaceholder = () => {
    if (!selectedPersonality) {
      return currentLanguage === 'Hindi'
        ? 'अपना प्रश्न यहाँ लिखें... (Enter दबाएं)'
        : 'Ask your spiritual question here... (Press Enter to send)';
    }

    switch (selectedPersonality.domain) {
      case 'spiritual':
        return currentLanguage === 'Hindi'
          ? `${selectedPersonality.display_name} से आध्यात्मिक प्रश्न पूछें...`
          : `Ask ${selectedPersonality.display_name} about spiritual matters...`;
      case 'scientific':
        return `Ask ${selectedPersonality.display_name} about science and the universe...`;
      case 'historical':
        return `Ask ${selectedPersonality.display_name} about leadership and history...`;
      case 'philosophical':
        return `Ask ${selectedPersonality.display_name} about philosophy and wisdom...`;
      default:
        return `Ask ${selectedPersonality.display_name} a question...`;
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
                <div>
                  <h1 className="heading-3 mb-0">
                    {selectedPersonality ? `${selectedPersonality.display_name}` : t('spiritualGuidance')}
                  </h1>
                  {selectedPersonality && (
                    <p className="text-sm text-neutral-600 mt-1">
                      {selectedPersonality.domain} • {selectedPersonality.description.substring(0, 50)}...
                    </p>
                  )}
                </div>
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

                <button
                  onClick={() => setShowPersonalitySelector(true)}
                  className={`btn btn-secondary btn-icon ${selectedPersonality ? 'bg-saffron-light' : ''}`}
                  title={selectedPersonality ? `Current: ${selectedPersonality.display_name}` : "Choose Personality"}
                  aria-label={selectedPersonality ? `Current personality: ${selectedPersonality.display_name}. Click to change.` : "Choose conversation personality"}
                  type="button"
                  disabled={personalityLoading}
                >
                  {personalityLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-saffron-primary"></div>
                  ) : (
                    <span aria-hidden="true">🧠</span>
                  )}
                  <span className="sr-only">
                    {personalityLoading ? 'Loading personality...' : 'Choose Personality'}
                  </span>
                </button>
              </div>
            </header>

            {/* Welcome Section */}
            <section className="welcome-section card card-sacred text-center mb-6" aria-labelledby="welcome-heading">
              <h2 id="welcome-heading" className="sr-only">{t('welcomeHeading')}</h2>
              <p className="body-text text-neutral-600">
                {selectedPersonality ? (
                  currentLanguage === 'Hindi' 
                    ? `${selectedPersonality.display_name} से बात करें और उनके ज्ञान से सीखें।`
                    : `Converse with ${selectedPersonality.display_name} and learn from their wisdom.`
                ) : (
                  currentLanguage === 'Hindi' 
                    ? 'धर्म के बारे में प्रश्न पूछें, पवित्र ग्रंथों से ज्ञान प्राप्त करें, या अपनी आध्यात्मिक साधना के लिए मार्गदर्शन पाएं।'
                    : 'Ask questions about dharma, seek wisdom from sacred texts, or find guidance for your spiritual practice.'
                )}
              </p>
            </section>

            {/* Personality Switch Notification */}
            {personalitySwitchNotification && (
              <div className="personality-switch-notification bg-saffron-light border border-saffron-primary rounded-lg p-3 mb-4 text-center">
                <p className="text-sm text-saffron-dark font-medium">
                  {personalitySwitchNotification}
                </p>
              </div>
            )}

            {/* Chat Messages Area */}
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
                    aria-label={`${message.sender === 'user' ? t('yourMessage') : (selectedPersonality?.display_name || 'AI')} message ${index + 1}`}
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
                      <div role="article" aria-label={`${selectedPersonality?.display_name || 'AI'} response`}>
                        <div className="sr-only">{selectedPersonality?.display_name || 'AI'} message:</div>
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
                      <span>{selectedPersonality?.display_name || 'AI'} is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </section>

          {/* Input Area */}
          </div>
          <div className="w-full px-4">
            <div className="input-area bg-white p-4 rounded-lg shadow-sm border border-neutral-200 mt-4 w-full">
              <div className="flex gap-4 items-end w-full max-w-none">
                <div className="flex-1 w-full min-w-0">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={getPersonalityPlaceholder()}
                    className="w-full p-3 border border-neutral-300 rounded-lg resize-none focus:ring-2 focus:ring-saffron-primary focus:border-transparent min-w-0"
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
                      personality={selectedPersonality ? {
                        id: selectedPersonality.id,
                        name: selectedPersonality.display_name || selectedPersonality.name,
                        domain: selectedPersonality.domain || 'spiritual',
                        voice_settings: selectedPersonality.voice_settings || {
                          language: 'en-US',
                          speaking_rate: 0.8,
                          pitch: -1.0,
                          volume: 0.9,
                          voice_characteristics: {
                            gender: 'male',
                            age: 'middle',
                            tone: 'reverent'
                          }
                        },
                        pronunciation_guide: selectedPersonality.pronunciation_guide || {}
                      } : undefined}
                      onPersonalityChange={handlePersonalitySelect}
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

      {/* Personality Selector Modal */}
      {showPersonalitySelector && (
        <PersonalitySelector
          selectedPersonalityId={selectedPersonality?.id}
          onPersonalitySelect={handlePersonalitySelect}
          onClose={() => setShowPersonalitySelector(false)}
          showAsDialog={true}
        />
      )}
    </>
  );
};

export default SpiritualGuidanceInterface;
