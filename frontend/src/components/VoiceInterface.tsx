import React, { useState, useEffect, useRef } from 'react';

interface VoiceInterfaceProps {
  onVoiceInput: (text: string) => void;
  onSpeechStart?: () => void;
  onSpeechEnd?: () => void;
  language?: 'en' | 'hi';
  disabled?: boolean;
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

const VoiceInterface: React.FC<VoiceInterfaceProps> = ({
  onVoiceInput,
  onSpeechStart,
  onSpeechEnd,
  language = 'en',
  disabled = false
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

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Configure voice parameters for spiritual content
    utterance.rate = 0.8; // Slower, more contemplative pace
    utterance.pitch = 1.0; // Natural pitch
    utterance.volume = 0.9; // Clear but not overwhelming
    
    // Set language and voice
    utterance.lang = language === 'hi' ? 'hi-IN' : 'en-US';
    
    // Find appropriate voice
    const voices = window.speechSynthesis.getVoices();
    const targetLang = language === 'hi' ? 'hi' : 'en';
    const preferredVoice = voices.find(voice => 
      voice.lang.startsWith(targetLang) && 
      (voice.name.includes('Female') || voice.name.includes('Google'))
    ) || voices.find(voice => voice.lang.startsWith(targetLang));
    
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

  return (
    <div className="voice-interface">
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
              <span className="text-sm text-neutral-600">Speaking...</span>
            </div>
          )}
        </div>
      </div>

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
          "🎙️ Speak your question • 🔊 Listen to wisdom"
        )}
      </div>
    </div>
  );
};

// Hook for easier voice integration
export const useVoiceInterface = () => {
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const voiceRef = useRef<{ speak: (text: string) => void } | null>(null);

  const speakText = (text: string) => {
    if (isVoiceEnabled && voiceRef.current) {
      voiceRef.current.speak(text);
    }
  };

  const toggleVoice = () => {
    setIsVoiceEnabled(!isVoiceEnabled);
  };

  return {
    isVoiceEnabled,
    toggleVoice,
    speakText,
    voiceRef
  };
};

export default VoiceInterface;
