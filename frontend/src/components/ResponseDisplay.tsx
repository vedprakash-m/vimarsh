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
        color: '#3B82F6',
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
        color: '#F59E0B',
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
        color: '#8B5CF6',
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
              color: '#6B7280',
      bgColor: 'bg-gray-50 border-gray-200'
    };
  };
  
  const sourceInfo = getSourceInfo();
  
  return (
    <div style={{
      borderRadius: '0.75rem',
      border: sourceInfo.type === 'unknown' ? '1px solid #E5E7EB' : '1px solid rgba(255, 255, 255, 0.2)',
      backgroundColor: sourceInfo.type === 'unknown' ? '#F9FAFB' : 'rgba(255, 255, 255, 0.1)',
      padding: '0.75rem',
      transition: 'all 0.2s ease'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span style={{ fontSize: '1.125rem' }}>{sourceInfo.icon}</span>
          <div>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              padding: '0.25rem 0.5rem',
              borderRadius: '9999px',
              fontSize: '0.75rem',
              fontWeight: '500',
              background: `linear-gradient(135deg, ${sourceInfo.color}, ${sourceInfo.color}E6)`,
              color: '#ffffff'
            }}>
              {sourceInfo.label}
            </span>
            {metadata.generation_time_ms && (
              <span style={{
                marginLeft: '0.5rem',
                fontSize: '0.75rem',
                color: '#6B7280'
              }}>
                {metadata.generation_time_ms}ms
              </span>
            )}
          </div>
        </div>
        
        <button
          onClick={() => setShowDetails(!showDetails)}
          style={{
            fontSize: '0.75rem',
            color: '#6B7280',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            transition: 'color 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#374151';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = '#6B7280';
          }}
          title={showDetails ? 'Hide details' : 'Show details'}
        >
          {showDetails ? '▼' : 'ℹ️'}
        </button>
      </div>
      
      <p style={{
        fontSize: '0.875rem',
        color: '#4B5563',
        marginTop: '0.5rem'
      }}>
        {sourceInfo.description}
      </p>
      
      {showDetails && (
        <div style={{
          marginTop: '0.75rem',
          paddingTop: '0.75rem',
          borderTop: '1px solid #E5E7EB',
          fontSize: '0.75rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '0.5rem'
          }}>
            <div>
              <span style={{
                fontWeight: '500',
                color: '#374151'
              }}>Service Mode:</span>
              <span style={{
                marginLeft: '0.25rem',
                color: '#4B5563'
              }}>{metadata.service_mode || 'unknown'}</span>
            </div>
            {metadata.circuit_breaker_status && (
              <div>
                <span style={{
                  fontWeight: '500',
                  color: '#374151'
                }}>Circuit Breaker:</span>
                <span style={{
                  marginLeft: '0.25rem',
                  color: metadata.circuit_breaker_status.state === 'CLOSED' ? '#059669' :
                        metadata.circuit_breaker_status.state === 'OPEN' ? '#DC2626' :
                        '#D97706'
                }}>
                  {metadata.circuit_breaker_status.state}
                </span>
              </div>
            )}
          </div>
          
          {metadata.fallback_reason && (
            <div>
              <span style={{
                fontWeight: '500',
                color: '#374151'
              }}>Fallback Reason:</span>
              <span style={{
                marginLeft: '0.25rem',
                color: '#4B5563',
                fontStyle: 'italic'
              }}>{metadata.fallback_reason}</span>
            </div>
          )}
          
          {metadata.reliability_stats && (
            <div>
              <span style={{
                fontWeight: '500',
                color: '#374151'
              }}>Success Rate:</span>
              <span style={{
                marginLeft: '0.25rem',
                color: '#4B5563'
              }}>
                {Math.round(metadata.reliability_stats.success_rate * 100)}%
                {' '}({metadata.reliability_stats.total_attempts} attempts)
              </span>
            </div>
          )}
          
          {metadata.memory_enhanced && (
            <div style={{
              color: '#059669'
            }}>
              <span style={{ fontWeight: '500' }}>✓ Memory Enhanced:</span>
              <span style={{ marginLeft: '0.25rem' }}>Personalized based on conversation history</span>
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
    <div style={{
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(8px)',
      borderRadius: '1.5rem',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
      border: '1px solid rgba(226, 232, 240, 0.5)',
      padding: '1.5rem',
      marginBottom: '1.5rem',
      transition: 'all 0.3s ease',
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.boxShadow = '0 20px 50px rgba(0, 0, 0, 0.15)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.1)';
    }}
    >
      {/* Response Header */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        marginBottom: '1rem'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <div style={{
            width: '2.5rem',
            height: '2.5rem',
            background: `linear-gradient(135deg, ${persona.color.includes('saffron') ? '#FF6B35, #F7931E' : '#1e40af, #059669'})`,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
          }}>
            <span style={{
              color: '#ffffff',
              fontSize: '1.125rem',
              fontWeight: '700'
            }}>{persona.avatar}</span>
          </div>
          <div>
            <h3 style={{
              fontSize: '1.125rem',
              fontWeight: '600',
              color: '#1e293b',
              margin: '0 0 0.25rem 0'
            }}>{persona.name}</h3>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <p style={{
                color: '#64748b',
                fontSize: '0.75rem',
                margin: 0
              }}>{formatTimestamp(response.timestamp)}</p>
              {response.tags && response.tags.length > 0 && (
                <div style={{ display: 'flex', gap: '0.25rem' }}>
                  {response.tags.slice(0, 2).map((tag, index) => (
                    <span 
                      key={index} 
                      style={{
                        padding: '0.125rem 0.5rem',
                        background: '#fef3f2',
                        color: '#1e293b',
                        fontSize: '0.75rem',
                        borderRadius: '9999px',
                        border: '1px solid #fed7d7'
                      }}
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
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          gap: '0.5rem'
        }}>
          {response.confidence && response.confidence > 0 && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <span style={{
                fontSize: '0.75rem',
                color: '#64748b'
              }}>
                {currentLanguage === 'Hindi' ? 'विश्वसनीयता' : 'Confidence'}:
              </span>
              <div style={{
                width: '4rem',
                height: '0.5rem',
                background: '#e2e8f0',
                borderRadius: '9999px',
                overflow: 'hidden'
              }}>
                <div 
                  style={{
                    height: '100%',
                    background: 'linear-gradient(to right, #059669, #F7931E)',
                    transition: 'all 0.5s ease',
                    width: `${response.confidence * 100}%`
                  }}
                />
              </div>
              <span style={{
                fontSize: '0.75rem',
                fontWeight: '500',
                color: '#475569'
              }}>
                {Math.round(response.confidence * 100)}%
              </span>
            </div>
          )}
          
          {/* Spiritual Authenticity Badge */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem',
            fontSize: '0.75rem',
            color: '#F7931E'
          }}>
            <span>🪷</span>
            <span>{currentLanguage === 'Hindi' ? 'प्रामाणिक' : 'Authentic'}</span>
          </div>
        </div>
      </div>

      {/* Response Quality Indicator - Subtle and Optional */}
      {response.metadata && (
        <div style={{ marginBottom: '0.5rem' }}>
          <details style={{ display: 'inline-block' }}>
            <summary style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.25rem',
              padding: '0.25rem 0.5rem',
              borderRadius: '9999px',
              background: 'rgba(255, 255, 255, 0.2)',
              backdropFilter: 'blur(4px)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              transition: 'all 0.2s ease',
              fontSize: '0.75rem',
              color: 'rgba(255, 255, 255, 0.8)',
              cursor: 'pointer',
              listStyle: 'none'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
            }}
            >
              <span style={{ fontSize: '0.875rem' }}>
                {response.metadata.ai_generated ? '✨' : response.metadata.response_source?.includes('template') ? '📿' : '🎭'}
              </span>
              <span style={{ fontWeight: '500' }}>
                {response.metadata.ai_generated ? 'Personalized' : response.metadata.response_source?.includes('template') ? 'Traditional' : 'Wisdom'}
              </span>
              <span style={{
                fontSize: '0.75rem',
                opacity: 0.6,
                transition: 'transform 0.2s ease'
              }}>ⓘ</span>
            </summary>
            <div style={{
              marginTop: '0.5rem',
              padding: '0.75rem',
              borderRadius: '0.5rem',
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(4px)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <ResponseSourceBadge 
                metadata={response.metadata}
                language={currentLanguage}
              />
            </div>
          </details>
        </div>
      )}

      {/* Main Response Text */}
      <div style={{ marginBottom: '1.5rem' }}>
        {/* Divine Icon based on A/B test */}
        {responseConfig.showDivineIcon && (
          <div style={{ marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '1.5rem' }}>🎭</span>
            <span style={{
              fontSize: '0.875rem',
              fontWeight: '500',
              color: '#1e40af',
              marginLeft: '0.5rem'
            }}>
              {currentLanguage === 'Hindi' ? 'श्री कृष्ण' : 'Krishna'}
            </span>
          </div>
        )}
        
        <div style={{
          fontSize: '1rem',
          color: '#1f2937',
          lineHeight: '1.625',
          marginBottom: '1rem',
          fontStyle: responseConfig.quoteStyle === 'highlighted' ? 'normal' : 'italic',
          background: responseConfig.quoteStyle === 'highlighted' ? 'rgba(255, 107, 53, 0.05)' : 'transparent',
          padding: responseConfig.quoteStyle === 'highlighted' ? '1rem' : '0',
          borderRadius: responseConfig.quoteStyle === 'highlighted' ? '0.5rem' : '0',
          borderLeft: responseConfig.quoteStyle === 'highlighted' ? '4px solid #FF6B35' : 'none',
          overflow: isLongResponse && !showFullResponse ? 'hidden' : 'visible',
          display: isLongResponse && !showFullResponse ? '-webkit-box' : 'block',
          WebkitLineClamp: isLongResponse && !showFullResponse ? 4 : 'none',
          WebkitBoxOrient: isLongResponse && !showFullResponse ? 'vertical' : 'initial'
        }}>
          {response.text}
        </div>
        
        {/* Show More/Less for long responses */}
        {isLongResponse && (
          <button
            onClick={() => setShowFullResponse(!showFullResponse)}
            style={{
              fontSize: '0.875rem',
              color: '#1e40af',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              transition: 'color 0.2s ease',
              marginBottom: '1rem',
              padding: 0
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = '#1e3a8a';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = '#1e40af';
            }}
          >
            {showFullResponse 
              ? (currentLanguage === 'Hindi' ? 'कम दिखाएं' : 'Show Less')
              : (currentLanguage === 'Hindi' ? 'और दिखाएं' : 'Show More')
            }
          </button>
        )}

        {/* Sanskrit Text with Enhanced Display */}
        {response.sanskritText && (
          <div style={{
            background: 'linear-gradient(to right, rgba(247, 147, 30, 0.1), rgba(255, 107, 53, 0.1), rgba(254, 243, 242, 0.2))',
            borderRadius: '0.5rem',
            padding: '1.25rem',
            marginBottom: '1rem',
            border: '1px solid rgba(247, 147, 30, 0.2)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              marginBottom: '0.75rem'
            }}>
              <span style={{ fontSize: '1.125rem' }}>🕉️</span>
              <span style={{
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#1e293b'
              }}>
                {currentLanguage === 'Hindi' ? 'मूल संस्कृत श्लोक' : 'Original Sanskrit Verse'}
              </span>
            </div>
            <div style={{
              fontSize: '1.125rem',
              lineHeight: '1.625',
              color: '#1e293b',
              fontFamily: 'serif',
              marginBottom: '0.75rem',
              textAlign: 'center'
            }}>
              {response.sanskritText}
            </div>
            {response.transliteration && (
              <div style={{
                fontSize: '0.875rem',
                color: '#64748b',
                fontStyle: 'italic',
                textAlign: 'center',
                borderTop: '1px solid rgba(247, 147, 30, 0.2)',
                paddingTop: '0.75rem'
              }}>
                <span style={{
                  fontSize: '0.75rem',
                  fontWeight: '500',
                  color: '#64748b',
                  display: 'block',
                  marginBottom: '0.25rem'
                }}>
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
        <div style={{ marginBottom: '1rem' }}>
          <h4 style={{
            fontSize: '0.875rem',
            fontWeight: '500',
            color: '#334155',
            marginBottom: '0.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span>📖</span>
            <span>{t('citations')}</span>
          </h4>
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.5rem'
          }}>
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
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                  padding: '0.25rem 0.5rem',
                  background: 'rgba(30, 64, 175, 0.1)',
                  color: '#1e40af',
                  fontSize: '0.75rem',
                  borderRadius: '0.375rem',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(30, 64, 175, 0.2)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(30, 64, 175, 0.1)';
                }}
              >
                <span>📖</span>
                <span>{formatCitation(citation)}</span>
              </button>
            ))}
          </div>
        </div>
      )}
      
      {response.citations.length > 0 && responseConfig.citationPosition === 'bottom' && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{
            fontSize: '0.875rem',
            fontWeight: '500',
            color: '#334155',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span>📖</span>
            <span>{t('citations')}</span>
            <span style={{
              fontSize: '0.75rem',
              color: '#64748b'
            }}>({response.citations.length})</span>
          </h4>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem'
          }}>
            {response.citations.map((citation, index) => (
              <div key={index}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem',
                  background: 'rgba(30, 64, 175, 0.05)',
                  border: '1px solid rgba(30, 64, 175, 0.2)',
                  borderRadius: '0.75rem',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(30, 64, 175, 0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(30, 64, 175, 0.05)';
                }}
                >
                  <button
                    onClick={() => onCitationClick?.(citation)}
                    style={{
                      flex: 1,
                      textAlign: 'left',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer'
                    }}
                  >
                    <div style={{
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      color: '#1e40af',
                      marginBottom: '0.25rem'
                    }}>
                      {formatCitation(citation)}
                    </div>
                    {citation.verseText && expandedCitation === index && (
                      <div style={{
                        fontSize: '0.75rem',
                        color: '#64748b',
                        fontStyle: 'italic',
                        marginTop: '0.5rem',
                        padding: '0.5rem',
                        background: 'rgba(255, 255, 255, 0.5)',
                        borderRadius: '0.25rem',
                        borderLeft: '2px solid #1e40af'
                      }}>
                        "{citation.verseText}"
                        {citation.translation && (
                          <div style={{
                            marginTop: '0.25rem',
                            color: '#64748b'
                          }}>
                            — {citation.translation}
                          </div>
                        )}
                      </div>
                    )}
                  </button>
                  
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    marginLeft: '0.75rem'
                  }}>
                    {citation.url && (
                      <button
                        onClick={() => window.open(citation.url, '_blank')}
                        style={{
                          fontSize: '0.75rem',
                          color: '#1e40af',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          transition: 'color 0.2s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.color = '#1e3a8a';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.color = '#1e40af';
                        }}
                        title="View source online"
                      >
                        🔗
                      </button>
                    )}
                    <button
                      onClick={() => toggleCitationDetails(index)}
                      style={{
                        fontSize: '0.75rem',
                        color: '#64748b',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        transition: 'color 0.2s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.color = '#334155';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.color = '#64748b';
                      }}
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
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{
            fontSize: '0.875rem',
            fontWeight: '500',
            color: '#334155',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span>🔗</span>
            <span>{currentLanguage === 'Hindi' ? 'संबंधित श्लोक' : 'Related Verses'}</span>
          </h4>
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.5rem'
          }}>
            {response.relatedVerses.slice(0, 3).map((verse, index) => (
              <button
                key={index}
                onClick={() => onCitationClick?.(verse)}
                style={{
                  background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
                  color: '#ffffff',
                  fontSize: '0.75rem',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '0.75rem',
                  border: '1px solid rgba(255, 107, 53, 0.3)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(255, 107, 53, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
                title={`Explore ${verse.source}`}
              >
                {formatCitation(verse)}
              </button>
            ))}
            {response.relatedVerses.length > 3 && (
              <span style={{
                fontSize: '0.75rem',
                color: '#64748b',
                padding: '0.5rem'
              }}>
                +{response.relatedVerses.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Enhanced Action Controls */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: '1rem',
        borderTop: '1px solid #F1F5F9'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          {/* Audio Controls */}
          {showAudioControls && (
            <button
              onClick={() => onSpeakResponse?.(response.text)}
              style={{
                padding: '0.5rem',
                borderRadius: '0.5rem',
                border: 'none',
                background: 'transparent',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(255, 107, 53, 0.1)';
                const span = e.currentTarget.querySelector('span');
                if (span) span.style.transform = 'scale(1.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                const span = e.currentTarget.querySelector('span');
                if (span) span.style.transform = 'scale(1)';
              }}
              aria-label={currentLanguage === 'Hindi' ? 'उत्तर सुनें' : 'Listen to response'}
              title={currentLanguage === 'Hindi' ? 'इस ज्ञान को सुनें' : 'Hear this wisdom spoken'}
            >
              <span style={{
                fontSize: '1.125rem',
                transition: 'transform 0.2s ease'
              }}>🔊</span>
            </button>
          )}

          {/* Copy to Clipboard */}
          <button
            onClick={handleCopyToClipboard}
            style={{
              padding: '0.5rem',
              borderRadius: '0.5rem',
              border: 'none',
              background: 'transparent',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F1F5F9';
              const span = e.currentTarget.querySelector('span');
              if (span) span.style.transform = 'scale(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              const span = e.currentTarget.querySelector('span');
              if (span) span.style.transform = 'scale(1)';
            }}
            aria-label={currentLanguage === 'Hindi' ? 'उत्तर कॉपी करें' : 'Copy response'}
            title={currentLanguage === 'Hindi' ? 'ज्ञान को क्लिपबोर्ड में कॉपी करें' : 'Copy wisdom to clipboard'}
          >
            <span style={{
              fontSize: '1.125rem',
              transition: 'transform 0.2s ease'
            }}>📋</span>
          </button>

          {/* Share Response */}
          <button
            onClick={() => onShareResponse?.(response)}
            style={{
              padding: '0.5rem',
              borderRadius: '0.5rem',
              border: 'none',
              background: 'transparent',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255, 107, 53, 0.1)';
              const span = e.currentTarget.querySelector('span');
              if (span) span.style.transform = 'scale(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              const span = e.currentTarget.querySelector('span');
              if (span) span.style.transform = 'scale(1)';
            }}
            aria-label={currentLanguage === 'Hindi' ? 'उत्तर साझा करें' : 'Share response'}
            title={currentLanguage === 'Hindi' ? 'इस ज्ञान को साझा करें' : 'Share this wisdom'}
          >
            <span style={{
              fontSize: '1.125rem',
              transition: 'transform 0.2s ease'
            }}>🔗</span>
          </button>

          {/* Sanskrit Study Mode */}
          {response.sanskritText && (
            <button
              style={{
                padding: '0.5rem',
                borderRadius: '0.5rem',
                border: 'none',
                background: 'transparent',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(247, 147, 30, 0.1)';
                const span = e.currentTarget.querySelector('span');
                if (span) span.style.transform = 'scale(1.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                const span = e.currentTarget.querySelector('span');
                if (span) span.style.transform = 'scale(1)';
              }}
              aria-label="Study Sanskrit"
              title="Study this verse in Sanskrit"
            >
              <span style={{
                fontSize: '1.125rem',
                transition: 'transform 0.2s ease'
              }}>📿</span>
            </button>
          )}
        </div>

        {/* Enhanced Feedback Section */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <span style={{
            fontSize: '0.75rem',
            color: '#64748b'
          }}>
            {currentLanguage === 'Hindi' ? 'सहायक?' : 'Helpful?'}
          </span>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem'
          }}>
            <button
              onClick={() => handleFeedback('helpful')}
              style={{
                padding: '0.5rem',
                borderRadius: '0.5rem',
                border: 'none',
                background: userFeedback === 'helpful' ? 'rgba(34, 197, 94, 0.2)' : 'transparent',
                color: userFeedback === 'helpful' ? '#059669' : '#64748b',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontSize: '0.875rem'
              }}
              onMouseEnter={(e) => {
                if (userFeedback !== 'helpful') {
                  e.currentTarget.style.backgroundColor = 'rgba(34, 197, 94, 0.1)';
                  e.currentTarget.style.color = '#059669';
                }
              }}
              onMouseLeave={(e) => {
                if (userFeedback !== 'helpful') {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = '#64748b';
                }
              }}
              aria-label={currentLanguage === 'Hindi' ? 'सहायक के रूप में चिह्नित करें' : 'Mark as helpful'}
              title={currentLanguage === 'Hindi' ? 'यह मार्गदर्शन सहायक था' : 'This guidance was helpful'}
            >
              <span style={{
                fontSize: userFeedback === 'helpful' ? '1.125rem' : '1rem'
              }}>👍</span>
            </button>
            <button
              onClick={() => handleFeedback('not-helpful')}
              style={{
                padding: '0.5rem',
                borderRadius: '0.5rem',
                border: 'none',
                background: userFeedback === 'not-helpful' ? '#FEF2F2' : 'transparent',
                color: userFeedback === 'not-helpful' ? '#DC2626' : '#64748b',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontSize: '0.875rem'
              }}
              onMouseEnter={(e) => {
                if (userFeedback !== 'not-helpful') {
                  e.currentTarget.style.backgroundColor = '#FEF2F2';
                  e.currentTarget.style.color = '#EF4444';
                }
              }}
              onMouseLeave={(e) => {
                if (userFeedback !== 'not-helpful') {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = '#64748b';
                }
              }}
              aria-label={currentLanguage === 'Hindi' ? 'सुधार की आवश्यकता' : 'Mark as not helpful'}
              title={currentLanguage === 'Hindi' ? 'यह मार्गदर्शन में सुधार की आवश्यकता है' : 'This guidance needs improvement'}
            >
              <span style={{
                fontSize: userFeedback === 'not-helpful' ? '1.125rem' : '1rem'
              }}>👎</span>
            </button>
          </div>
          
          {/* Feedback confirmation */}
          {userFeedback && (
            <span style={{
              fontSize: '0.75rem',
              color: '#64748b',
              fontStyle: 'italic'
            }}>
              {currentLanguage === 'Hindi' ? 'धन्यवाद!' : 'Thank you!'}
            </span>
          )}
        </div>
      </div>

      {/* Reverent Footer with Spiritual Blessing */}
      <div style={{
        marginTop: '1.5rem',
        paddingTop: '1rem',
        borderTop: '1px solid #F8FAFC',
        textAlign: 'center'
      }}>
        <p style={{
          fontSize: '0.75rem',
          color: '#9CA3AF',
          fontStyle: 'italic',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem'
        }}>
          <span style={{ color: '#F7931E' }}>🕉️</span>
          {currentLanguage === 'Hindi' ? (
            "सत्यं शिवं सुन्दरम्"
          ) : (
            "May this wisdom guide your path"
          )}
          <span style={{ color: '#F7931E' }}>🕉️</span>
        </p>
        {response.persona === 'krishna' && (
          <p style={{
            fontSize: '0.75rem',
            color: '#D1D5DB',
            marginTop: '0.25rem'
          }}>
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
