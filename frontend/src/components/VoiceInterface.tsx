import React, { useState, useEffect, useRef } from 'react';

interface Personality {
  id: string;
  name: string;
  domain: 'spiritual' | 'historical' | 'scientific' | 'philosophical';
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

interface VoiceInterfaceProps {
  onVoiceInput: (text: string) => void;
  onSpeechStart?: () => void;
  onSpeechEnd?: () => void;
  language?: 'en' | 'hi';
  disabled?: boolean;
  personality?: Personality;
  onPersonalityChange?: (personalityId: string) => void;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface ISpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  maxAlternatives: number;
  serviceURI: string;
  grammars: any;
  start(): void;
  stop(): void;
  abort(): void;
  addEventListener(type: 'result', listener: (ev: SpeechRecognitionEvent) => void): void;
  addEventListener(type: 'error', listener: (ev: SpeechRecognitionErrorEvent) => void): void;
  addEventListener(type: 'start', listener: (ev: Event) => void): void;
  addEventListener(type: 'end', listener: (ev: Event) => void): void;
  addEventListener(type: 'speechstart', listener: (ev: Event) => void): void;
  addEventListener(type: 'speechend', listener: (ev: Event) => void): void;
  addEventListener(type: 'nomatch', listener: (ev: Event) => void): void;
}

declare global {
  interface Window {
    SpeechRecognition: new () => ISpeechRecognition;
    webkitSpeechRecognition: new () => ISpeechRecognition;
  }
}

// Personality-specific voice configurations
const PERSONALITY_VOICES: Record<string, Personality> = {
  krishna: {
    id: 'krishna',
    name: 'Lord Krishna',
    domain: 'spiritual',
    voice_settings: {
      language: 'en-US',
      voice_name: 'Google US English Male',
      speaking_rate: 0.75, // Slower, contemplative pace
      pitch: -1.5, // Lower, more reverent tone
      volume: 0.9,
      voice_characteristics: {
        gender: 'male',
        age: 'middle',
        tone: 'reverent'
      }
    },
    pronunciation_guide: {
      'dharma': { phonetic: 'DHAR-ma', language: 'sanskrit' },
      'karma': { phonetic: 'KAR-ma', language: 'sanskrit' },
      'yoga': { phonetic: 'YO-ga', language: 'sanskrit' },
      'moksha': { phonetic: 'MOHK-sha', language: 'sanskrit' },
      'samsara': { phonetic: 'sam-SAH-ra', language: 'sanskrit' },
      'bhakti': { phonetic: 'BHAK-ti', language: 'sanskrit' },
      'Arjuna': { phonetic: 'ar-JU-na', language: 'sanskrit' },
      'Kurukshetra': { phonetic: 'ku-ruk-SHET-ra', language: 'sanskrit' }
    }
  },
  einstein: {
    id: 'einstein',
    name: 'Albert Einstein',
    domain: 'scientific',
    voice_settings: {
      language: 'en-US',
      voice_name: 'Google US English Male',
      speaking_rate: 0.85, // Thoughtful pace
      pitch: 0.0, // Natural pitch
      volume: 0.9,
      voice_characteristics: {
        gender: 'male',
        age: 'elderly',
        accent: 'slight_german',
        tone: 'scholarly'
      }
    },
    pronunciation_guide: {
      'relativity': { phonetic: 'rel-uh-TIV-i-tee', language: 'english' },
      'spacetime': { phonetic: 'SPACE-time', language: 'english' },
      'quantum': { phonetic: 'KWAN-tum', language: 'english' },
      'photon': { phonetic: 'FOH-ton', language: 'english' },
      'Lorentz': { phonetic: 'LOR-ents', language: 'german' },
      'Minkowski': { phonetic: 'min-KOV-skee', language: 'german' }
    }
  },
  lincoln: {
    id: 'lincoln',
    name: 'Abraham Lincoln',
    domain: 'historical',
    voice_settings: {
      language: 'en-US',
      voice_name: 'Google US English Male',
      speaking_rate: 0.8, // Deliberate, presidential pace
      pitch: -0.5, // Slightly lower, authoritative
      volume: 0.95,
      voice_characteristics: {
        gender: 'male',
        age: 'middle',
        accent: 'midwest_american',
        tone: 'authoritative'
      }
    },
    pronunciation_guide: {
      'Gettysburg': { phonetic: 'GET-eez-burg', language: 'english' },
      'emancipation': { phonetic: 'ih-man-si-PAY-shun', language: 'english' },
      'proclamation': { phonetic: 'prok-luh-MAY-shun', language: 'english' },
      'secession': { phonetic: 'si-SESH-un', language: 'english' }
    }
  },
  marcus_aurelius: {
    id: 'marcus_aurelius',
    name: 'Marcus Aurelius',
    domain: 'philosophical',
    voice_settings: {
      language: 'en-US',
      voice_name: 'Google US English Male',
      speaking_rate: 0.7, // Very contemplative
      pitch: -1.0, // Lower, philosophical tone
      volume: 0.85,
      voice_characteristics: {
        gender: 'male',
        age: 'middle',
        tone: 'contemplative'
      }
    },
    pronunciation_guide: {
      'stoicism': { phonetic: 'STOH-i-sizm', language: 'english' },
      'virtue': { phonetic: 'VUR-choo', language: 'english' },
      'logos': { phonetic: 'LOH-gos', language: 'greek' },
      'ataraxia': { phonetic: 'at-uh-RAK-see-uh', language: 'greek' },
      'Meditations': { phonetic: 'med-i-TAY-shuns', language: 'english' }
    }
  }
};

const VoiceInterface: React.FC<VoiceInterfaceProps> = ({
  onVoiceInput,
  onSpeechStart,
  onSpeechEnd,
  language = 'en',
  disabled = false,
  personality,
  onPersonalityChange
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const recognitionRef = useRef<ISpeechRecognition | null>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Check browser support on mount
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const speechSynthesis = window.speechSynthesis;
    
    if (SpeechRecognition && speechSynthesis) {
      setIsSupported(true);
      initializeSpeechRecognition();
    } else {
      setIsSupported(false);
      setError('Speech recognition not supported in this browser');
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      stopSpeaking();
    };
  }, []);

  const initializeSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    
    // Set language based on props
    recognition.lang = language === 'hi' ? 'hi-IN' : 'en-US';

    recognition.addEventListener('start', () => {
      setIsListening(true);
      setError(null);
      onSpeechStart?.();
    });

    recognition.addEventListener('result', (event: SpeechRecognitionEvent) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      setTranscript(interimTranscript || finalTranscript);

      if (finalTranscript) {
        onVoiceInput(finalTranscript.trim());
        setTranscript('');
      }
    });

    recognition.addEventListener('error', (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error);
      setError(`Speech recognition error: ${event.error}`);
      setIsListening(false);
    });

    recognition.addEventListener('end', () => {
      setIsListening(false);
      setTranscript('');
      onSpeechEnd?.();
    });

    recognitionRef.current = recognition;
  };

  const startListening = () => {
    if (!isSupported || !recognitionRef.current || disabled) return;

    try {
      // Update language if changed
      recognitionRef.current.lang = language === 'hi' ? 'hi-IN' : 'en-US';
      recognitionRef.current.start();
    } catch (error) {
      console.error('Failed to start speech recognition:', error);
      setError('Failed to start voice recognition');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const speak = (text: string) => {
    if (!window.speechSynthesis || !text.trim()) return;

    // Stop any ongoing speech
    stopSpeaking();

    // Apply pronunciation corrections for specialized terms
    const processedText = applyPronunciationGuide(text);

    const utterance = new SpeechSynthesisUtterance(processedText);
    
    // Get personality-specific voice settings
    const currentPersonality = personality || PERSONALITY_VOICES.krishna; // Default to Krishna
    const voiceSettings = currentPersonality.voice_settings;
    
    // Configure voice parameters based on personality
    utterance.rate = voiceSettings.speaking_rate;
    utterance.pitch = 1.0 + (voiceSettings.pitch / 10); // Convert to 0-2 range
    utterance.volume = voiceSettings.volume;
    
    // Set language based on personality and user preference
    const personalityLang = voiceSettings.language;
    utterance.lang = language === 'hi' ? 'hi-IN' : personalityLang;
    
    // Find appropriate voice based on personality characteristics
    const voices = window.speechSynthesis.getVoices();
    const targetLang = language === 'hi' ? 'hi' : personalityLang.split('-')[0];
    
    // Voice selection based on personality characteristics
    let preferredVoice = null;
    
    if (voiceSettings.voice_name) {
      // Try to find the specific voice name
      preferredVoice = voices.find(voice => voice.name.includes(voiceSettings.voice_name!));
    }
    
    if (!preferredVoice) {
      // Fallback to gender and characteristics-based selection
      const genderPreference = voiceSettings.voice_characteristics.gender;
      const agePreference = voiceSettings.voice_characteristics.age;
      
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

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      setIsSpeaking(false);
      setError(`Speech synthesis error: ${event.error}`);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const applyPronunciationGuide = (text: string): string => {
    if (!personality) return text;
    
    let processedText = text;
    const pronunciationGuide = personality.pronunciation_guide;
    
    // Apply pronunciation corrections for specialized terms
    Object.entries(pronunciationGuide).forEach(([term, guide]) => {
      const regex = new RegExp(`\\b${term}\\b`, 'gi');
      // For TTS, we can use SSML-like phonetic representations
      // Most browsers support basic phonetic hints through creative spelling
      processedText = processedText.replace(regex, guide.phonetic);
    });
    
    return processedText;
  };

  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  if (!isSupported) {
    return (
      <div className="text-center p-4 bg-neutral-100 rounded-lg">
        <span className="text-neutral-600 text-sm">
          Voice features not available in this browser
        </span>
      </div>
    );
  }

  const getPersonalityIcon = (domain: string) => {
    switch (domain) {
      case 'spiritual': return '🕉️';
      case 'scientific': return '🔬';
      case 'historical': return '🏛️';
      case 'philosophical': return '🤔';
      default: return '🎭';
    }
  };

  const getVoiceCharacteristics = () => {
    if (!personality) return null;
    const chars = personality.voice_settings.voice_characteristics;
    return `${chars.gender} • ${chars.age} • ${chars.tone}`;
  };

  return (
    <div className="voice-interface">
      {/* Personality Voice Info */}
      {personality && (
        <div className="mb-3 p-2 bg-neutral-50 rounded-lg border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-lg">{getPersonalityIcon(personality.domain)}</span>
              <div>
                <div className="text-sm font-medium text-neutral-800">
                  {personality.name} Voice
                </div>
                <div className="text-xs text-neutral-600">
                  {getVoiceCharacteristics()}
                </div>
              </div>
            </div>
            <div className="text-xs text-neutral-500">
              Rate: {personality.voice_settings.speaking_rate}x
            </div>
          </div>
        </div>
      )}

      {/* Voice Input Controls */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggleListening}
          disabled={disabled || isSpeaking}
          className={`voice-button btn-icon ${isListening ? 'listening' : ''}`}
          aria-label={isListening ? "Stop listening" : "Start voice input"}
          title={isListening ? "Stop listening" : "Speak your question"}
        >
          {isListening ? (
            <span className="text-xl animate-pulse">🎙️</span>
          ) : (
            <span className="text-xl">🎤</span>
          )}
        </button>

        {isSpeaking && (
          <button
            onClick={stopSpeaking}
            className="voice-button btn-icon"
            aria-label="Stop speaking"
            title="Stop audio playback"
          >
            <span className="text-xl">🔇</span>
          </button>
        )}

        {/* Voice Status Indicator */}
        <div className="flex-1 min-w-0">
          {isListening && (
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-saffron-primary rounded-full animate-pulse"></div>
              <span className="text-sm text-neutral-600">
                {transcript || "Listening..."}
              </span>
            </div>
          )}
          
          {isSpeaking && (
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-peacock-blue rounded-full animate-pulse"></div>
              <span className="text-sm text-neutral-600">
                Speaking as {personality?.name || 'Default'}...
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Pronunciation Guide */}
      {personality && Object.keys(personality.pronunciation_guide).length > 0 && (
        <div className="mt-2 p-2 bg-blue-50 rounded text-xs">
          <div className="font-medium text-blue-800 mb-1">Pronunciation Guide:</div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(personality.pronunciation_guide).slice(0, 4).map(([term, guide]) => (
              <span key={term} className="bg-blue-100 px-2 py-1 rounded text-blue-700">
                {term} → {guide.phonetic}
              </span>
            ))}
            {Object.keys(personality.pronunciation_guide).length > 4 && (
              <span className="text-blue-600">
                +{Object.keys(personality.pronunciation_guide).length - 4} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
          <button 
            onClick={() => setError(null)}
            className="ml-2 text-red-500 hover:text-red-700"
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      {/* Voice Instructions */}
      <div className="mt-2 text-xs text-neutral-500 text-center">
        {language === 'hi' ? (
          "🎙️ अपना प्रश्न बोलें • 🔊 उत्तर सुनें"
        ) : (
          `🎙️ Speak your question • 🔊 Listen to ${personality?.name || 'wisdom'}`
        )}
      </div>
    </div>
  );
};

// Hook for easier voice integration with personality support
export const useVoiceInterface = () => {
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [currentPersonality, setCurrentPersonality] = useState<Personality | null>(null);
  const voiceRef = useRef<{ speak: (text: string) => void } | null>(null);

  const speakText = (text: string, personalityId?: string) => {
    if (isVoiceEnabled && voiceRef.current) {
      // Switch personality if specified
      if (personalityId && personalityId !== currentPersonality?.id) {
        const personality = PERSONALITY_VOICES[personalityId];
        if (personality) {
          setCurrentPersonality(personality);
        }
      }
      voiceRef.current.speak(text);
    }
  };

  const switchPersonality = (personalityId: string) => {
    const personality = PERSONALITY_VOICES[personalityId];
    if (personality) {
      setCurrentPersonality(personality);
    }
  };

  const toggleVoice = () => {
    setIsVoiceEnabled(!isVoiceEnabled);
  };

  const getAvailablePersonalities = () => {
    return Object.values(PERSONALITY_VOICES);
  };

  return {
    isVoiceEnabled,
    toggleVoice,
    speakText,
    voiceRef,
    currentPersonality,
    switchPersonality,
    getAvailablePersonalities
  };
};

export default VoiceInterface;
