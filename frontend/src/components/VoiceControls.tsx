import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Loader2 } from 'lucide-react';

interface VoiceState {
  isListening: boolean;
  isSpeaking: boolean;
  isProcessing: boolean;
  transcript: string;
  error: string | null;
}

interface VoiceControlsProps {
  onTranscript: (text: string) => void;
  onSpeakText?: (text: string) => void;
  textToSpeak?: string;
  personality?: string;
  domain?: string;
  disabled?: boolean;
  className?: string;
}

// Personality-specific voice settings for text-to-speech
const getPersonalityVoiceSettings = (personality: string): { rate: number; pitch: number; voiceType: string } => {
  const settings: Record<string, { rate: number; pitch: number; voiceType: string }> = {
    // Spiritual domain - calm, measured delivery
    krishna: { rate: 0.85, pitch: 0.9, voiceType: 'male' },
    buddha: { rate: 0.8, pitch: 0.85, voiceType: 'male' },
    jesus: { rate: 0.85, pitch: 1.0, voiceType: 'male' },
    jesus_christ: { rate: 0.85, pitch: 1.0, voiceType: 'male' },
    rumi: { rate: 0.9, pitch: 1.0, voiceType: 'male' },
    swami_vivekananda: { rate: 0.95, pitch: 1.1, voiceType: 'male' },
    vivekananda: { rate: 0.95, pitch: 1.1, voiceType: 'male' },

    // Scientific domain - clear, articulate
    einstein: { rate: 0.9, pitch: 1.0, voiceType: 'male' },
    albert_einstein: { rate: 0.9, pitch: 1.0, voiceType: 'male' },
    newton: { rate: 0.85, pitch: 0.95, voiceType: 'male' },
    isaac_newton: { rate: 0.85, pitch: 0.95, voiceType: 'male' },
    tesla: { rate: 0.9, pitch: 1.05, voiceType: 'male' },
    nikola_tesla: { rate: 0.9, pitch: 1.05, voiceType: 'male' },
    archimedes: { rate: 0.88, pitch: 0.95, voiceType: 'male' },
    leonardo_da_vinci: { rate: 0.9, pitch: 1.0, voiceType: 'male' },

    // Leadership domain - authoritative, inspiring
    lincoln: { rate: 0.85, pitch: 0.9, voiceType: 'male' },
    abraham_lincoln: { rate: 0.85, pitch: 0.9, voiceType: 'male' },
    gandhi: { rate: 0.8, pitch: 0.95, voiceType: 'male' },
    mahatma_gandhi: { rate: 0.8, pitch: 0.95, voiceType: 'male' },
    chanakya: { rate: 0.88, pitch: 0.9, voiceType: 'male' },
    benjamin_franklin: { rate: 0.9, pitch: 0.95, voiceType: 'male' },
    george_washington: { rate: 0.85, pitch: 0.9, voiceType: 'male' },
    martin_luther_king_jr: { rate: 0.9, pitch: 1.1, voiceType: 'male' },

    // Philosophical domain - thoughtful, measured
    marcus_aurelius: { rate: 0.85, pitch: 0.9, voiceType: 'male' },
    aurelius: { rate: 0.85, pitch: 0.9, voiceType: 'male' },
    socrates: { rate: 0.88, pitch: 1.0, voiceType: 'male' },
    plato: { rate: 0.85, pitch: 0.95, voiceType: 'male' },
    aristotle: { rate: 0.88, pitch: 0.95, voiceType: 'male' },
    confucius: { rate: 0.82, pitch: 0.9, voiceType: 'male' },
    lao_tzu: { rate: 0.78, pitch: 0.85, voiceType: 'male' },
    laotzu: { rate: 0.78, pitch: 0.85, voiceType: 'male' },

    // Literary domain - expressive
    shakespeare: { rate: 0.88, pitch: 1.05, voiceType: 'male' },
    william_shakespeare: { rate: 0.88, pitch: 1.05, voiceType: 'male' },
    tagore: { rate: 0.85, pitch: 1.0, voiceType: 'male' },
    rabindranath_tagore: { rate: 0.85, pitch: 1.0, voiceType: 'male' },

    // Psychology domain
    freud: { rate: 0.88, pitch: 0.95, voiceType: 'male' },
    sigmund_freud: { rate: 0.88, pitch: 0.95, voiceType: 'male' },

    // Default settings
    default: { rate: 0.9, pitch: 1.0, voiceType: 'male' }
  };

  const normalizedPersonality = personality?.toLowerCase().replace(/\s+/g, '_') || 'default';
  return settings[normalizedPersonality] || settings.default;
};

// Get domain color for visual feedback
const getDomainColor = (domain: string): string => {
  const colors: Record<string, string> = {
    spiritual: '#ea580c',
    scientific: '#2563eb',
    historical: '#16a34a',
    philosophical: '#9333ea',
    literary: '#059669',
    leadership: '#dc2626',
    psychology: '#8b5cf6'
  };
  return colors[domain] || '#6b7280';
};

export const VoiceControls: React.FC<VoiceControlsProps> = ({
  onTranscript,
  textToSpeak,
  personality = 'default',
  domain = 'spiritual',
  disabled = false,
  className
}) => {
  const [voiceState, setVoiceState] = useState<VoiceState>({
    isListening: false,
    isSpeaking: false,
    isProcessing: false,
    transcript: '',
    error: null
  });
  
  const [isVoiceSupported, setIsVoiceSupported] = useState(false);
  const [isSpeechSupported, setIsSpeechSupported] = useState(false);
  
  const recognitionRef = useRef<any>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Check for browser support
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    setIsVoiceSupported(!!SpeechRecognition);
    setIsSpeechSupported('speechSynthesis' in window);
  }, []);

  // Initialize speech recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 3;

    recognition.onstart = () => {
      setVoiceState(prev => ({ 
        ...prev, 
        isListening: true, 
        transcript: '', 
        error: null 
      }));
    };

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      setVoiceState(prev => ({ 
        ...prev, 
        transcript: finalTranscript || interimTranscript 
      }));

      if (finalTranscript) {
        onTranscript(finalTranscript);
      }
    };

    recognition.onerror = (event: any) => {
      let errorMessage = 'Voice recognition error';
      
      switch (event.error) {
        case 'not-allowed':
          errorMessage = 'Microphone permission denied';
          break;
        case 'no-speech':
          errorMessage = 'No speech detected';
          break;
        case 'network':
          errorMessage = 'Network error';
          break;
        case 'aborted':
          errorMessage = 'Recognition aborted';
          break;
      }

      setVoiceState(prev => ({ 
        ...prev, 
        isListening: false, 
        error: errorMessage 
      }));
    };

    recognition.onend = () => {
      setVoiceState(prev => ({ ...prev, isListening: false }));
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {
          // Ignore cleanup errors
        }
      }
    };
  }, [onTranscript]);

  // Start listening
  const startListening = useCallback(() => {
    if (recognitionRef.current && !voiceState.isListening) {
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Failed to start voice recognition:', error);
        setVoiceState(prev => ({ 
          ...prev, 
          error: 'Failed to start voice recognition' 
        }));
      }
    }
  }, [voiceState.isListening]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current && voiceState.isListening) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Failed to stop voice recognition:', error);
      }
    }
  }, [voiceState.isListening]);

  // Speak text (Text-to-Speech)
  const speakText = useCallback((text: string) => {
    if (!isSpeechSupported || !text) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    const voiceSettings = getPersonalityVoiceSettings(personality);

    // Try to find a suitable voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(
      v => v.lang.startsWith('en') && 
           v.name.toLowerCase().includes(voiceSettings.voiceType)
    ) || voices.find(v => v.lang.startsWith('en')) || voices[0];

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.rate = voiceSettings.rate;
    utterance.pitch = voiceSettings.pitch;
    utterance.volume = 1.0;

    utterance.onstart = () => {
      setVoiceState(prev => ({ ...prev, isSpeaking: true }));
    };

    utterance.onend = () => {
      setVoiceState(prev => ({ ...prev, isSpeaking: false }));
    };

    utterance.onerror = () => {
      setVoiceState(prev => ({ 
        ...prev, 
        isSpeaking: false,
        error: 'Speech synthesis failed'
      }));
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [personality, isSpeechSupported]);

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    if (isSpeechSupported) {
      window.speechSynthesis.cancel();
      setVoiceState(prev => ({ ...prev, isSpeaking: false }));
    }
  }, [isSpeechSupported]);

  // Speak the provided text when it changes
  useEffect(() => {
    if (textToSpeak && !voiceState.isSpeaking) {
      // Don't auto-speak - let user trigger it
    }
  }, [textToSpeak]);

  // If neither voice nor speech is supported, don't render
  if (!isVoiceSupported && !isSpeechSupported) {
    return null;
  }

  const domainColor = getDomainColor(domain);
  const { isListening, isSpeaking, isProcessing, error } = voiceState;

  return (
    <div 
      className={className}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}
    >
      {/* Microphone Button - Voice Input */}
      {isVoiceSupported && (
        <button
          onClick={isListening ? stopListening : startListening}
          disabled={disabled || isProcessing}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '2.5rem',
            height: '2.5rem',
            borderRadius: '50%',
            border: isListening 
              ? `2px solid ${domainColor}` 
              : '1px solid #e2e8f0',
            background: isListening 
              ? `${domainColor}20` 
              : 'white',
            color: isListening ? domainColor : '#64748b',
            cursor: disabled || isProcessing ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease',
            position: 'relative',
            opacity: disabled ? 0.5 : 1
          }}
          onMouseEnter={(e) => {
            if (!isListening && !disabled) {
              e.currentTarget.style.borderColor = domainColor;
              e.currentTarget.style.color = domainColor;
              e.currentTarget.style.background = `${domainColor}10`;
            }
          }}
          onMouseLeave={(e) => {
            if (!isListening && !disabled) {
              e.currentTarget.style.borderColor = '#e2e8f0';
              e.currentTarget.style.color = '#64748b';
              e.currentTarget.style.background = 'white';
            }
          }}
          title={isListening ? 'Stop listening' : 'Start voice input'}
          aria-label={isListening ? 'Stop listening' : 'Start voice input'}
        >
          {isProcessing ? (
            <Loader2 size={18} className="animate-spin" />
          ) : isListening ? (
            <MicOff size={18} />
          ) : (
            <Mic size={18} />
          )}
          
          {/* Listening pulse animation */}
          {isListening && (
            <span
              style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                borderRadius: '50%',
                border: `2px solid ${domainColor}`,
                animation: 'voicePulse 1.5s ease-out infinite',
                pointerEvents: 'none'
              }}
            />
          )}
        </button>
      )}

      {/* Speaker Button - Read Response */}
      {isSpeechSupported && textToSpeak && (
        <button
          onClick={isSpeaking ? stopSpeaking : () => speakText(textToSpeak)}
          disabled={disabled}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '2.5rem',
            height: '2.5rem',
            borderRadius: '50%',
            border: isSpeaking 
              ? `2px solid ${domainColor}` 
              : '1px solid #e2e8f0',
            background: isSpeaking 
              ? `${domainColor}20` 
              : 'white',
            color: isSpeaking ? domainColor : '#64748b',
            cursor: disabled ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease',
            opacity: disabled ? 0.5 : 1
          }}
          onMouseEnter={(e) => {
            if (!isSpeaking && !disabled) {
              e.currentTarget.style.borderColor = domainColor;
              e.currentTarget.style.color = domainColor;
              e.currentTarget.style.background = `${domainColor}10`;
            }
          }}
          onMouseLeave={(e) => {
            if (!isSpeaking && !disabled) {
              e.currentTarget.style.borderColor = '#e2e8f0';
              e.currentTarget.style.color = '#64748b';
              e.currentTarget.style.background = 'white';
            }
          }}
          title={isSpeaking ? 'Stop speaking' : 'Read aloud'}
          aria-label={isSpeaking ? 'Stop speaking' : 'Read aloud'}
        >
          {isSpeaking ? <VolumeX size={18} /> : <Volume2 size={18} />}
        </button>
      )}

      {/* Listening indicator */}
      {isListening && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.35rem 0.75rem',
            background: `${domainColor}15`,
            borderRadius: '1rem',
            fontSize: '0.75rem',
            color: domainColor,
            fontWeight: '500'
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: domainColor,
              animation: 'blink 1s ease-in-out infinite'
            }}
          />
          Listening...
        </div>
      )}

      {/* Error message */}
      {error && (
        <div
          style={{
            fontSize: '0.75rem',
            color: '#ef4444',
            padding: '0.25rem 0.5rem',
            background: '#fef2f2',
            borderRadius: '0.25rem'
          }}
        >
          {error}
        </div>
      )}

      {/* Animation styles */}
      <style>{`
        @keyframes voicePulse {
          0% {
            transform: scale(1);
            opacity: 0.8;
          }
          100% {
            transform: scale(1.8);
            opacity: 0;
          }
        }
        
        @keyframes blink {
          0%, 50%, 100% {
            opacity: 1;
          }
          25%, 75% {
            opacity: 0.3;
          }
        }
        
        .animate-spin {
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
};

export default VoiceControls;
