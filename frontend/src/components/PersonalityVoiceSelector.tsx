/**
 * Personality Voice Selector Component
 * 
 * Allows users to select and switch between different personality voices
 * with preview functionality and voice characteristics display.
 */

import React, { useState } from 'react';

interface Personality {
  id: string;
  name: string;
  domain: 'spiritual' | 'historical' | 'scientific' | 'philosophical' | 'literary' | 'leadership' | 'psychology';
  voice_settings: {
    language: string;
    voice_name?: string;
    speaking_rate: number;
    pitch: number;
    volume: number;
    voice_characteristics: {
      gender: 'male' | 'female';
      age: 'young' | 'middle' | 'elderly';
      accent?: string;
      tone: 'reverent' | 'authoritative' | 'contemplative' | 'scholarly';
    };
  };
  pronunciation_guide: {
    [term: string]: {
      phonetic: string;
      audio_url?: string;
      language: string;
    };
  };
}

interface PersonalityVoiceSelectorProps {
  personalities: Personality[];
  selectedPersonality?: Personality;
  onPersonalitySelect: (personality: Personality) => void;
  onVoicePreview?: (personality: Personality) => void;
  disabled?: boolean;
}

const PersonalityVoiceSelector: React.FC<PersonalityVoiceSelectorProps> = ({
  personalities,
  selectedPersonality,
  onPersonalitySelect,
  onVoicePreview,
  disabled = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getPersonalityIcon = (domain: string) => {
    switch (domain) {
      case 'spiritual': return '🕉️';
      case 'scientific': return '🔬';
      case 'historical': return '🏛️';
      case 'philosophical': return '🤔';
      case 'literary': return '📚';
      case 'leadership': return '👑';
      case 'psychology': return '🧠';
      default: return '🎭';
    }
  };

  const getDomainColor = (domain: string) => {
    switch (domain) {
      case 'spiritual': return { bg: 'rgba(255, 107, 53, 0.1)', text: '#ea580c', border: 'rgba(255, 107, 53, 0.3)' };
      case 'scientific': return { bg: 'rgba(59, 130, 246, 0.1)', text: '#2563eb', border: 'rgba(59, 130, 246, 0.3)' };
      case 'historical': return { bg: 'rgba(34, 197, 94, 0.1)', text: '#16a34a', border: 'rgba(34, 197, 94, 0.3)' };
      case 'philosophical': return { bg: 'rgba(147, 51, 234, 0.1)', text: '#9333ea', border: 'rgba(147, 51, 234, 0.3)' };
      case 'literary': return { bg: 'rgba(16, 185, 129, 0.1)', text: '#059669', border: 'rgba(16, 185, 129, 0.3)' };
      case 'leadership': return { bg: 'rgba(239, 68, 68, 0.1)', text: '#dc2626', border: 'rgba(239, 68, 68, 0.3)' };
      case 'psychology': return { bg: 'rgba(139, 92, 246, 0.1)', text: '#8b5cf6', border: 'rgba(139, 92, 246, 0.3)' };
      default: return { bg: 'rgba(107, 114, 128, 0.1)', text: '#374151', border: 'rgba(107, 114, 128, 0.3)' };
    }
  };

  const getVoiceCharacteristics = (personality: Personality) => {
    const chars = personality.voice_settings.voice_characteristics;
    return `${chars.gender} • ${chars.age} • ${chars.tone}`;
  };

  const handlePersonalitySelect = (personality: Personality) => {
    onPersonalitySelect(personality);
    setIsExpanded(false);
  };

  const handleVoicePreview = (personality: Personality, event: React.MouseEvent) => {
    event.stopPropagation();
    if (onVoicePreview) {
      onVoicePreview(personality);
    }
  };

  const getPreviewText = (personality: Personality) => {
    const sampleTexts = {
      krishna: "Namaste, dear child. I am here to guide you on the path of dharma and self-realization.",
      albert_einstein: "Hello, my friend. Let us explore the mysteries of the universe together through the lens of science.",
      abraham_lincoln: "Greetings, fellow citizen. I am here to discuss the principles of democracy and freedom.",
      marcus_aurelius: "Welcome, seeker of wisdom. Let us contemplate the virtues of stoic philosophy together."
    };
    return sampleTexts[personality.id as keyof typeof sampleTexts] || 
           `Hello, I am ${personality.name}. How may I assist you today?`;
  };

  return (
    <div>
      {/* Current Selection Display */}
      <div 
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1rem',
          border: '2px solid #e2e8f0',
          borderRadius: '0.75rem',
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s ease',
          background: disabled ? '#f8fafc' : '#ffffff'
        }}
        onMouseEnter={(e) => {
          if (!disabled) {
            e.currentTarget.style.background = '#f8fafc';
            e.currentTarget.style.borderColor = '#FF6B35';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(255, 107, 53, 0.15)';
          }
        }}
        onMouseLeave={(e) => {
          if (!disabled) {
            e.currentTarget.style.background = '#ffffff';
            e.currentTarget.style.borderColor = '#e2e8f0';
            e.currentTarget.style.boxShadow = 'none';
          }
        }}
        onClick={() => !disabled && setIsExpanded(!isExpanded)}
      >
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          {selectedPersonality ? (
            <>
              <span style={{ fontSize: '1.25rem' }}>{getPersonalityIcon(selectedPersonality.domain)}</span>
              <div>
                <div style={{
                  fontWeight: '500',
                  color: '#1e293b'
                }}>
                  {selectedPersonality.name}
                </div>
                <div style={{
                  fontSize: '0.875rem',
                  color: '#64748b'
                }}>
                  {getVoiceCharacteristics(selectedPersonality)}
                </div>
              </div>
              <span style={{
                padding: '0.25rem 0.5rem',
                fontSize: '0.75rem',
                borderRadius: '9999px',
                border: `1px solid ${getDomainColor(selectedPersonality.domain).border}`,
                background: getDomainColor(selectedPersonality.domain).bg,
                color: getDomainColor(selectedPersonality.domain).text
              }}>
                {selectedPersonality.domain}
              </span>
            </>
          ) : (
            <div style={{ color: '#64748b' }}>Select a personality voice...</div>
          )}
        </div>
        <div style={{
          transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: 'transform 0.2s ease'
        }}>
          <span style={{ color: '#FF6B35' }}>▼</span>
        </div>
      </div>

      {/* Expanded Options */}
      {isExpanded && !disabled && (
        <div style={{
          marginTop: '0.5rem',
          border: '1px solid #e2e8f0',
          borderRadius: '0.75rem',
          background: '#ffffff',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.15)',
          maxHeight: '384px',
          overflowY: 'auto'
        }}>
          {personalities.map((personality) => (
            <div
              key={personality.id}
              style={{
                padding: '0.75rem',
                borderBottom: '1px solid #f1f5f9',
                cursor: 'pointer',
                transition: 'background-color 0.2s ease',
                background: selectedPersonality?.id === personality.id ? 'rgba(255, 107, 53, 0.05)' : 'transparent'
              }}
              onMouseEnter={(e) => {
                if (selectedPersonality?.id !== personality.id) {
                  e.currentTarget.style.backgroundColor = '#f8fafc';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedPersonality?.id !== personality.id) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
              onClick={() => handlePersonalitySelect(personality)}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  flex: 1
                }}>
                  <span style={{ fontSize: '1.25rem' }}>{getPersonalityIcon(personality.domain)}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <div style={{
                        fontWeight: '500',
                        color: '#1e293b'
                      }}>
                        {personality.name}
                      </div>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        fontSize: '0.75rem',
                        borderRadius: '9999px',
                        border: `1px solid ${getDomainColor(personality.domain).border}`,
                        background: getDomainColor(personality.domain).bg,
                        color: getDomainColor(personality.domain).text
                      }}>
                        {personality.domain}
                      </span>
                    </div>
                    <div style={{
                      fontSize: '0.875rem',
                      color: '#64748b',
                      marginTop: '0.25rem'
                    }}>
                      {getVoiceCharacteristics(personality)}
                    </div>
                    <div style={{
                      fontSize: '0.75rem',
                      color: '#64748b',
                      marginTop: '0.25rem'
                    }}>
                      Rate: {personality.voice_settings.speaking_rate}x • 
                      Pitch: {personality.voice_settings.pitch > 0 ? '+' : ''}{personality.voice_settings.pitch}
                    </div>
                  </div>
                </div>
                
                {/* Preview Button */}
                {onVoicePreview && (
                  <button
                    onClick={(e) => handleVoicePreview(personality, e)}
                    style={{
                      marginLeft: '0.5rem',
                      padding: '0.25rem 0.75rem',
                      fontSize: '0.75rem',
                      background: 'rgba(59, 130, 246, 0.1)',
                      color: '#2563eb',
                      border: 'none',
                      borderRadius: '0.25rem',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.2)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                    }}
                    title="Preview voice"
                  >
                    🔊 Preview
                  </button>
                )}
              </div>

              {/* Pronunciation Guide Preview */}
              {Object.keys(personality.pronunciation_guide).length > 0 && (
                <div style={{
                  marginTop: '0.5rem',
                  paddingTop: '0.5rem',
                  borderTop: '1px solid #f1f5f9'
                }}>
                  <div style={{
                    fontSize: '0.75rem',
                    color: '#64748b',
                    marginBottom: '0.25rem'
                  }}>Specialized pronunciation:</div>
                  <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '0.25rem'
                  }}>
                    {Object.entries(personality.pronunciation_guide).slice(0, 3).map(([term, guide]) => (
                      <span key={term} style={{
                        background: '#f1f5f9',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.25rem',
                        fontSize: '0.75rem',
                        color: '#64748b'
                      }}>
                        {term}
                      </span>
                    ))}
                    {Object.keys(personality.pronunciation_guide).length > 3 && (
                      <span style={{
                        fontSize: '0.75rem',
                        color: '#64748b'
                      }}>
                        +{Object.keys(personality.pronunciation_guide).length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Voice Settings Display */}
      {selectedPersonality && (
        <div style={{
          marginTop: '0.75rem',
          padding: '0.75rem',
          background: '#f8fafc',
          borderRadius: '0.5rem',
          fontSize: '0.75rem',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{
            fontWeight: '500',
            color: '#334155',
            marginBottom: '0.5rem'
          }}>Current Voice Settings:</div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '0.5rem',
            color: '#64748b'
          }}>
            <div>Speaking Rate: {selectedPersonality.voice_settings.speaking_rate}x</div>
            <div>Pitch: {selectedPersonality.voice_settings.pitch > 0 ? '+' : ''}{selectedPersonality.voice_settings.pitch}</div>
            <div>Volume: {Math.round(selectedPersonality.voice_settings.volume * 100)}%</div>
            <div>Language: {selectedPersonality.voice_settings.language}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PersonalityVoiceSelector;