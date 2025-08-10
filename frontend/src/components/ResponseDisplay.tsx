import React, { useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { useSpiritualGuidanceTest } from '../hooks/useABTest';
import '../styles/gap-remediation.css';

interface Citation {
  source: string;
  reference: string;
  verse?: string;
  chapter?: string;
  book?: string;
  sloka?: string;
  adhyaya?: string;
  url?: string;
  verseText?: string;
  translation?: string;
}

interface SpiritualResponse {
  id: string;
  text: string;
  sanskritText?: string;
  transliteration?: string;
  citations: Citation[];
  timestamp: Date;
  confidence?: number;
  audioUrl?: string;
  relatedVerses?: Citation[];
  tags?: string[];
  persona?: 'krishna' | 'arjuna' | 'narrator';
  metadata?: {
    response_source?: 'gemini_ai' | 'template_fallback' | 'hardcoded_fallback' | 'hybrid_rag' | 'simple_rag';
    ai_generated?: boolean;
    service_mode?: 'enhanced' | 'standard' | 'fallback';
    fallback_reason?: string;
    circuit_breaker_status?: {
      state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
      failure_count: number;
      last_failure_time?: string;
    };
    reliability_stats?: {
      success_rate: number;
      total_attempts: number;
      template_fallback_count: number;
    };
    generation_time_ms?: number;
    memory_enhanced?: boolean;
  };
}

interface ResponseDisplayProps {
  response: SpiritualResponse;
  language?: 'en' | 'hi';
  onCitationClick?: (citation: Citation) => void;
  onSpeakResponse?: (text: string) => void;
  onShareResponse?: (response: SpiritualResponse) => void;
  onFeedback?: (responseId: string, feedback: 'helpful' | 'not-helpful') => void;
  showAudioControls?: boolean;
  showRelatedVerses?: boolean;
}

// Gap Remediation: Response Source Transparency Component
interface ResponseSourceBadgeProps {
  metadata: NonNullable<SpiritualResponse['metadata']>;
  language: 'Hindi' | 'English';
}

const ResponseSourceBadge: React.FC<ResponseSourceBadgeProps> = ({ metadata, language }) => {
  const [showDetails, setShowDetails] = useState(false);
  
  const getSourceInfo = () => {
    const isAI = metadata.ai_generated === true;
    const source = metadata.response_source;
    const mode = metadata.service_mode;
    
    if (isAI && source === 'gemini_ai') {
      return {
        type: 'ai',
        icon: '✨',
        label: language === 'Hindi' ? 'व्यक्तिगत' : 'Personalized',
        description: language === 'Hindi' 
          ? 'यह उत्तर आपके विशिष्ट प्रश्न के लिए AI द्वारा तैयार किया गया है'
          : 'This response was crafted specifically for your question using AI wisdom',
        color: 'from-blue-500 to-blue-600',
        bgColor: 'bg-white/10 border-white/20'
      };
    }
    
    if (source === 'template_fallback' || source === 'hardcoded_fallback') {
      return {
        type: 'template',
        icon: '�',
        label: language === 'Hindi' ? 'पारंपरिक' : 'Traditional',
        description: language === 'Hindi'
          ? 'यह शास्त्रों से लिया गया पारंपरिक ज्ञान है'
          : 'This is timeless wisdom from sacred texts and teachings',
        color: 'from-amber-500 to-amber-600',
        bgColor: 'bg-white/10 border-white/20'
      };
    }
    
    if (source === 'hybrid_rag' || source === 'simple_rag') {
      return {
        type: 'enhanced',
        icon: '�',
        label: language === 'Hindi' ? 'संवर्धित' : 'Enhanced',
        description: language === 'Hindi'
          ? 'यह उत्तर गहन खोज और AI के संयोजन से बनाया गया है'
          : 'This combines deep search through wisdom texts with AI insights',
        color: 'from-purple-500 to-purple-600',
        bgColor: 'bg-white/10 border-white/20'
      };
    }
    
    // Fallback
    return {
      type: 'unknown',
      icon: '🎭',
      label: language === 'Hindi' ? 'ज्ञान' : 'Wisdom',
      description: language === 'Hindi'
        ? 'आध्यात्मिक मार्गदर्शन प्रणाली से उत्तर'
        : 'Response from spiritual guidance system',
      color: 'from-gray-500 to-gray-600',
      bgColor: 'bg-gray-50 border-gray-200'
    };
  };
  
  const sourceInfo = getSourceInfo();
  
  return (
    <div className={`response-source-badge rounded-lg border ${sourceInfo.bgColor} p-3 transition-all duration-200`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{sourceInfo.icon}</span>
          <div>
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${sourceInfo.color} text-white`}>
              {sourceInfo.label}
            </span>
            {metadata.generation_time_ms && (
              <span className="ml-2 text-xs text-gray-500">
                {metadata.generation_time_ms}ms
              </span>
            )}
          </div>
        </div>
        
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
          title={showDetails ? 'Hide details' : 'Show details'}
        >
          {showDetails ? '▼' : 'ℹ️'}
        </button>
      </div>
      
      <p className="text-sm text-gray-600 mt-2">
        {sourceInfo.description}
      </p>
      
      {showDetails && (
        <div className="mt-3 pt-3 border-t border-gray-200 text-xs space-y-2">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="font-medium text-gray-700">Service Mode:</span>
              <span className="ml-1 text-gray-600">{metadata.service_mode || 'unknown'}</span>
            </div>
            {metadata.circuit_breaker_status && (
              <div>
                <span className="font-medium text-gray-700">Circuit Breaker:</span>
                <span className={`ml-1 ${
                  metadata.circuit_breaker_status.state === 'CLOSED' ? 'text-green-600' :
                  metadata.circuit_breaker_status.state === 'OPEN' ? 'text-red-600' :
                  'text-yellow-600'
                }`}>
                  {metadata.circuit_breaker_status.state}
                </span>
              </div>
            )}
          </div>
          
          {metadata.fallback_reason && (
            <div>
              <span className="font-medium text-gray-700">Fallback Reason:</span>
              <span className="ml-1 text-gray-600 italic">{metadata.fallback_reason}</span>
            </div>
          )}
          
          {metadata.reliability_stats && (
            <div>
              <span className="font-medium text-gray-700">Success Rate:</span>
              <span className="ml-1 text-gray-600">
                {Math.round(metadata.reliability_stats.success_rate * 100)}%
                {' '}({metadata.reliability_stats.total_attempts} attempts)
              </span>
            </div>
          )}
          
          {metadata.memory_enhanced && (
            <div className="text-green-600">
              <span className="font-medium">✓ Memory Enhanced:</span>
              <span className="ml-1">Personalized based on conversation history</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const ResponseDisplay: React.FC<ResponseDisplayProps> = ({
  response,
  language = 'en',
  onCitationClick,
  onSpeakResponse,
  onShareResponse,
  onFeedback,
  showAudioControls = true,
  showRelatedVerses = true
}) => {
  const { t, currentLanguage } = useLanguage();
  const [expandedCitation, setExpandedCitation] = useState<number | null>(null);
  const [userFeedback, setUserFeedback] = useState<'helpful' | 'not-helpful' | null>(null);
  const [showFullResponse, setShowFullResponse] = useState(false);
  
  // A/B Testing configuration
  const { responseConfig, trackGuidanceInteraction } = useSpiritualGuidanceTest();

  // Enhanced citation formatting with spiritual context
  const formatCitation = (citation: Citation): string => {
    const parts = [];
    
    // Handle different spiritual text formats
    if (citation.source === 'Bhagavad Gita' || citation.source === 'भगवद्गीता') {
      if (citation.chapter && citation.verse) {
        parts.push(`${citation.source} ${citation.chapter}.${citation.verse}`);
      } else if (citation.adhyaya && citation.sloka) {
        parts.push(`${citation.source} ${citation.adhyaya}.${citation.sloka}`);
      }
    } else if (citation.source === 'Mahabharata' || citation.source === 'महाभारत') {
      if (citation.book && citation.chapter) {
        const bookText = currentLanguage === 'Hindi' ? 'पुस्तक' : 'Book';
        const chapterText = currentLanguage === 'Hindi' ? 'अध्याय' : 'Chapter';
        parts.push(`${citation.source}, ${bookText} ${citation.book}, ${chapterText} ${citation.chapter}`);
      }
    } else if (citation.source === 'Srimad Bhagavatam' || citation.source === 'श्रीमद्भागवतम्') {
      if (citation.chapter && citation.verse) {
        parts.push(`${citation.source} ${citation.chapter}.${citation.verse}`);
      }
    } else {
      // Generic format
      if (citation.source) parts.push(citation.source);
      if (citation.reference) parts.push(citation.reference);
    }
    
    return parts.join(', ') || citation.reference || 'Unknown Source';
  };

  const getPersonaInfo = (persona?: string) => {
    switch (persona) {
      case 'krishna':
        return {
          name: currentLanguage === 'Hindi' ? 'श्री कृष्ण' : 'Krishna',
          avatar: 'कृ',
          color: 'from-saffron-primary to-sunset-orange'
        };
      case 'arjuna':
        return {
          name: currentLanguage === 'Hindi' ? 'अर्जुन' : 'Arjuna',
          avatar: 'अ',
          color: 'from-peacock-blue to-forest-green'
        };
      default:
        return {
          name: currentLanguage === 'Hindi' ? 'श्री कृष्ण' : 'Krishna',
          avatar: 'कृ',
          color: 'from-saffron-primary to-sunset-orange'
        };
    }
  };

  const formatTimestamp = (timestamp: Date): string => {
    const locale = currentLanguage === 'Hindi' ? 'hi-IN' : 'en-US';
    return timestamp.toLocaleTimeString(locale, { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const handleCopyToClipboard = async () => {
    const citationsText = response.citations.map(c => formatCitation(c)).join('\n');
    const textToCopy = [
      response.text,
      response.sanskritText ? `\nSanskrit: ${response.sanskritText}` : '',
      response.transliteration ? `Transliteration: ${response.transliteration}` : '',
      citationsText ? `\nSources:\n${citationsText}` : ''
    ].filter(Boolean).join('\n');
    
    try {
      await navigator.clipboard.writeText(textToCopy);
      // TODO: Show success notification
      console.log('✅ Response copied to clipboard');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = textToCopy;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
  };

  const handleFeedback = (feedback: 'helpful' | 'not-helpful') => {
    setUserFeedback(feedback);
    onFeedback?.(response.id, feedback);
    console.log(`📊 User feedback: ${feedback} for response ${response.id}`);
  };

  const toggleCitationDetails = (index: number) => {
    setExpandedCitation(expandedCitation === index ? null : index);
  };

  const persona = getPersonaInfo(response.persona);
  const isLongResponse = response.text.length > 300;

  return (
    <div className="response-display bg-white/95 backdrop-blur-sm rounded-xl shadow-lg border border-neutral-200/50 p-6 mb-6 transition-all hover:shadow-xl">
      {/* Response Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 bg-gradient-to-br ${persona.color} rounded-full flex items-center justify-center shadow-md`}>
            <span className="text-white text-lg font-bold">{persona.avatar}</span>
          </div>
          <div>
            <h3 className="heading-4 text-earth-brown mb-0">{persona.name}</h3>
            <div className="flex items-center gap-2">
              <p className="caption-text text-neutral-500">{formatTimestamp(response.timestamp)}</p>
              {response.tags && response.tags.length > 0 && (
                <div className="flex gap-1">
                  {response.tags.slice(0, 2).map((tag, index) => (
                    <span 
                      key={index} 
                      className="px-2 py-0.5 bg-lotus-pink-light text-earth-brown text-xs rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Confidence & Quality Indicators */}
        <div className="flex flex-col items-end gap-2">
          {response.confidence && response.confidence > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-neutral-500">
                {currentLanguage === 'Hindi' ? 'विश्वसनीयता' : 'Confidence'}:
              </span>
              <div className="w-16 h-2 bg-neutral-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-forest-green to-sacred-gold transition-all duration-500"
                  style={{ width: `${response.confidence * 100}%` }}
                />
              </div>
              <span className="text-xs font-medium text-neutral-600">
                {Math.round(response.confidence * 100)}%
              </span>
            </div>
          )}
          
          {/* Spiritual Authenticity Badge */}
          <div className="flex items-center gap-1 text-xs text-sacred-gold">
            <span>🪷</span>
            <span>{currentLanguage === 'Hindi' ? 'प्रामाणिक' : 'Authentic'}</span>
          </div>
        </div>
      </div>

      {/* Response Quality Indicator - Subtle and Optional */}
      {response.metadata && (
        <div className="response-source-indicator mb-2">
          <details className="group">
            <summary className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm border border-white/30 transition-all duration-200 text-xs text-white/80 cursor-pointer list-none">
              <span className="text-sm">
                {response.metadata.ai_generated ? '✨' : response.metadata.response_source?.includes('template') ? '📿' : '🎭'}
              </span>
              <span className="font-medium">
                {response.metadata.ai_generated ? 'Personalized' : response.metadata.response_source?.includes('template') ? 'Traditional' : 'Wisdom'}
              </span>
              <span className="text-xs opacity-60 group-open:rotate-180 transition-transform">ⓘ</span>
            </summary>
            <div className="mt-2 p-3 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20">
              <ResponseSourceBadge 
                metadata={response.metadata}
                language={currentLanguage}
              />
            </div>
          </details>
        </div>
      )}

      {/* Main Response Text */}
      <div className="response-content mb-6">
        {/* Divine Icon based on A/B test */}
        {responseConfig.showDivineIcon && (
          <div className="divine-icon-container mb-3">
            <span className="text-2xl">🎭</span>
            <span className="text-sm font-medium text-krishna-blue ml-2">
              {currentLanguage === 'Hindi' ? 'श्री कृष्ण' : 'Krishna'}
            </span>
          </div>
        )}
        
        <div className={`body-text text-neutral-800 leading-relaxed mb-4 ${
          responseConfig.quoteStyle === 'highlighted' ? 'response-highlighted' : 'response-italic'
        } ${isLongResponse && !showFullResponse ? 'line-clamp-4' : ''}`}>
          {response.text}
        </div>
        
        {/* Show More/Less for long responses */}
        {isLongResponse && (
          <button
            onClick={() => setShowFullResponse(!showFullResponse)}
            className="text-sm text-peacock-blue hover:text-peacock-dark transition-colors mb-4"
          >
            {showFullResponse 
              ? (currentLanguage === 'Hindi' ? 'कम दिखाएं' : 'Show Less')
              : (currentLanguage === 'Hindi' ? 'और दिखाएं' : 'Show More')
            }
          </button>
        )}

        {/* Sanskrit Text with Enhanced Display */}
        {response.sanskritText && (
          <div className="sanskrit-display bg-gradient-to-r from-sacred-gold/10 via-saffron-primary/10 to-lotus-pink-light/20 rounded-lg p-5 mb-4 border border-sacred-gold/20">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-lg">🕉️</span>
              <span className="text-sm font-medium text-earth-brown">
                {currentLanguage === 'Hindi' ? 'मूल संस्कृत श्लोक' : 'Original Sanskrit Verse'}
              </span>
            </div>
            <div className="sanskrit-text text-lg leading-relaxed text-earth-brown font-devanagari mb-3 text-center">
              {response.sanskritText}
            </div>
            {response.transliteration && (
              <div className="transliteration-text text-sm text-neutral-600 italic text-center border-t border-sacred-gold/20 pt-3">
                <span className="text-xs font-medium text-neutral-500 block mb-1">
                  {currentLanguage === 'Hindi' ? 'रोमन लिपि' : 'Transliteration'}:
                </span>
                {response.transliteration}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Enhanced Citations Section - Positioned based on A/B test */}
      {response.citations.length > 0 && responseConfig.citationPosition === 'inline' && (
        <div className="citations-section mb-4 citations-inline">
          <h4 className="text-sm font-medium text-neutral-700 mb-2 flex items-center gap-2">
            <span>📖</span>
            <span>{t('citations')}</span>
          </h4>
          <div className="flex flex-wrap gap-2">
            {response.citations.map((citation, index) => (
              <button
                key={index}
                onClick={() => {
                  onCitationClick?.(citation);
                  trackGuidanceInteraction('citation_clicked', { 
                    citationIndex: index, 
                    source: citation.source 
                  });
                }}
                className="citation-tag inline-flex items-center gap-1 px-2 py-1 bg-peacock-blue/10 text-peacock-dark text-xs rounded-md hover:bg-peacock-blue/20 transition-colors"
              >
                <span>📖</span>
                <span>{formatCitation(citation)}</span>
              </button>
            ))}
          </div>
        </div>
      )}
      
      {response.citations.length > 0 && responseConfig.citationPosition === 'bottom' && (
        <div className="citations-section mb-6 citations-bottom">
          <h4 className="text-sm font-medium text-neutral-700 mb-3 flex items-center gap-2">
            <span>📖</span>
            <span>{t('citations')}</span>
            <span className="text-xs text-neutral-500">({response.citations.length})</span>
          </h4>
          <div className="space-y-3">
            {response.citations.map((citation, index) => (
              <div key={index} className="citation-card">
                <div className="flex items-center justify-between p-3 bg-peacock-blue/5 border border-peacock-blue/20 rounded-lg hover:bg-peacock-blue/10 transition-colors">
                  <button
                    onClick={() => onCitationClick?.(citation)}
                    className="flex-1 text-left"
                  >
                    <div className="citation-title text-sm font-medium text-peacock-dark mb-1">
                      {formatCitation(citation)}
                    </div>
                    {citation.verseText && expandedCitation === index && (
                      <div className="citation-preview text-xs text-neutral-600 italic mt-2 p-2 bg-white/50 rounded border-l-2 border-peacock-blue">
                        "{citation.verseText}"
                        {citation.translation && (
                          <div className="mt-1 text-neutral-500">
                            — {citation.translation}
                          </div>
                        )}
                      </div>
                    )}
                  </button>
                  
                  <div className="flex items-center gap-2 ml-3">
                    {citation.url && (
                      <button
                        onClick={() => window.open(citation.url, '_blank')}
                        className="text-xs text-peacock-blue hover:text-peacock-dark"
                        title="View source online"
                      >
                        🔗
                      </button>
                    )}
                    <button
                      onClick={() => toggleCitationDetails(index)}
                      className="text-xs text-neutral-500 hover:text-neutral-700"
                      title={expandedCitation === index ? "Hide details" : "Show details"}
                    >
                      {expandedCitation === index ? '▼' : '▶'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Related Verses Section */}
      {showRelatedVerses && response.relatedVerses && response.relatedVerses.length > 0 && (
        <div className="related-verses-section mb-6">
          <h4 className="text-sm font-medium text-neutral-700 mb-3 flex items-center gap-2">
            <span>🔗</span>
            <span>{currentLanguage === 'Hindi' ? 'संबंधित श्लोक' : 'Related Verses'}</span>
          </h4>
          <div className="flex flex-wrap gap-2">
            {response.relatedVerses.slice(0, 3).map((verse, index) => (
              <button
                key={index}
                onClick={() => onCitationClick?.(verse)}
                className="related-verse-tag bg-lotus-pink-light/30 text-earth-brown text-xs px-3 py-2 rounded-lg hover:bg-lotus-pink-light/50 transition-colors border border-lotus-pink-light"
                title={`Explore ${verse.source}`}
              >
                {formatCitation(verse)}
              </button>
            ))}
            {response.relatedVerses.length > 3 && (
              <span className="text-xs text-neutral-500 px-2 py-2">
                +{response.relatedVerses.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Enhanced Action Controls */}
      <div className="response-actions flex items-center justify-between pt-4 border-t border-neutral-100">
        <div className="flex items-center gap-3">
          {/* Audio Controls */}
          {showAudioControls && (
            <button
              onClick={() => onSpeakResponse?.(response.text)}
              className="btn-icon hover:bg-peacock-blue/10 group"
              aria-label={currentLanguage === 'Hindi' ? 'उत्तर सुनें' : 'Listen to response'}
              title={currentLanguage === 'Hindi' ? 'इस ज्ञान को सुनें' : 'Hear this wisdom spoken'}
            >
              <span className="text-lg group-hover:scale-110 transition-transform">🔊</span>
            </button>
          )}

          {/* Copy to Clipboard */}
          <button
            onClick={handleCopyToClipboard}
            className="btn-icon hover:bg-neutral-100 group"
            aria-label={currentLanguage === 'Hindi' ? 'उत्तर कॉपी करें' : 'Copy response'}
            title={currentLanguage === 'Hindi' ? 'ज्ञान को क्लिपबोर्ड में कॉपी करें' : 'Copy wisdom to clipboard'}
          >
            <span className="text-lg group-hover:scale-110 transition-transform">📋</span>
          </button>

          {/* Share Response */}
          <button
            onClick={() => onShareResponse?.(response)}
            className="btn-icon hover:bg-saffron-primary/10 group"
            aria-label={currentLanguage === 'Hindi' ? 'उत्तर साझा करें' : 'Share response'}
            title={currentLanguage === 'Hindi' ? 'इस ज्ञान को साझा करें' : 'Share this wisdom'}
          >
            <span className="text-lg group-hover:scale-110 transition-transform">🔗</span>
          </button>

          {/* Sanskrit Study Mode */}
          {response.sanskritText && (
            <button
              className="btn-icon hover:bg-sacred-gold/10 group"
              aria-label="Study Sanskrit"
              title="Study this verse in Sanskrit"
            >
              <span className="text-lg group-hover:scale-110 transition-transform">📿</span>
            </button>
          )}
        </div>

        {/* Enhanced Feedback Section */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-neutral-500">
            {currentLanguage === 'Hindi' ? 'सहायक?' : 'Helpful?'}
          </span>
          <div className="flex items-center gap-1">
            <button
              onClick={() => handleFeedback('helpful')}
              className={`btn-icon text-sm transition-all ${
                userFeedback === 'helpful' 
                  ? 'bg-forest-green/20 text-forest-green' 
                  : 'hover:bg-forest-green/10 text-neutral-500 hover:text-forest-green'
              }`}
              aria-label={currentLanguage === 'Hindi' ? 'सहायक के रूप में चिह्नित करें' : 'Mark as helpful'}
              title={currentLanguage === 'Hindi' ? 'यह मार्गदर्शन सहायक था' : 'This guidance was helpful'}
            >
              <span className={userFeedback === 'helpful' ? 'text-lg' : ''}>👍</span>
            </button>
            <button
              onClick={() => handleFeedback('not-helpful')}
              className={`btn-icon text-sm transition-all ${
                userFeedback === 'not-helpful' 
                  ? 'bg-red-100 text-red-600' 
                  : 'hover:bg-red-50 text-neutral-500 hover:text-red-500'
              }`}
              aria-label={currentLanguage === 'Hindi' ? 'सुधार की आवश्यकता' : 'Mark as not helpful'}
              title={currentLanguage === 'Hindi' ? 'यह मार्गदर्शन में सुधार की आवश्यकता है' : 'This guidance needs improvement'}
            >
              <span className={userFeedback === 'not-helpful' ? 'text-lg' : ''}>👎</span>
            </button>
          </div>
          
          {/* Feedback confirmation */}
          {userFeedback && (
            <span className="text-xs text-neutral-500 italic">
              {currentLanguage === 'Hindi' ? 'धन्यवाद!' : 'Thank you!'}
            </span>
          )}
        </div>
      </div>

      {/* Reverent Footer with Spiritual Blessing */}
      <div className="mt-6 pt-4 border-t border-neutral-50 text-center">
        <p className="caption-text text-neutral-400 italic flex items-center justify-center gap-2">
          <span className="text-sacred-gold">🕉️</span>
          {currentLanguage === 'Hindi' ? (
            "सत्यं शिवं सुन्दरम्"
          ) : (
            "May this wisdom guide your path"
          )}
          <span className="text-sacred-gold">🕉️</span>
        </p>
        {response.persona === 'krishna' && (
          <p className="text-xs text-neutral-300 mt-1">
            {currentLanguage === 'Hindi' 
              ? "भगवान श्रीकृष्ण की कृपा से"
              : "By the grace of Krishna"
            }
          </p>
        )}
      </div>
    </div>
  );
};

export default ResponseDisplay;
