import { useState, useEffect, useRef, useCallback } from 'react';

export interface VoiceConfig {
  language?: 'en' | 'hi';
  continuous?: boolean;
  interimResults?: boolean;
  personality?: string;
  autoSpeak?: boolean;
}

export interface VoiceState {
  isListening: boolean;
  isSpeaking: boolean;
  isSupported: boolean;
  isSpeechSupported: boolean;
  transcript: string;
  interimTranscript: string;
  error: string | null;
  audioLevel: number;
}

export interface VoiceResult {
  text: string;
  confidence: number;
  isFinal: boolean;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

const DEFAULT_CONFIG: VoiceConfig = {
  language: 'en',
  continuous: false,
  interimResults: true,
  autoSpeak: false
};

// Personality-specific voice settings
const VOICE_SETTINGS: Record<string, { rate: number; pitch: number }> = {
  // Spiritual - calm, measured
  krishna: { rate: 0.85, pitch: 0.9 },
  buddha: { rate: 0.8, pitch: 0.85 },
  jesus_christ: { rate: 0.85, pitch: 1.0 },
  rumi: { rate: 0.9, pitch: 1.0 },
  swami_vivekananda: { rate: 0.95, pitch: 1.1 },
  
  // Scientific - clear, articulate
  albert_einstein: { rate: 0.9, pitch: 1.0 },
  isaac_newton: { rate: 0.85, pitch: 0.95 },
  nikola_tesla: { rate: 0.9, pitch: 1.05 },
  archimedes: { rate: 0.88, pitch: 0.95 },
  leonardo_da_vinci: { rate: 0.9, pitch: 1.0 },
  
  // Leadership - authoritative
  abraham_lincoln: { rate: 0.85, pitch: 0.9 },
  mahatma_gandhi: { rate: 0.8, pitch: 0.95 },
  chanakya: { rate: 0.88, pitch: 0.9 },
  benjamin_franklin: { rate: 0.9, pitch: 0.95 },
  george_washington: { rate: 0.85, pitch: 0.9 },
  martin_luther_king_jr: { rate: 0.9, pitch: 1.1 },
  
  // Philosophical - thoughtful
  marcus_aurelius: { rate: 0.85, pitch: 0.9 },
  socrates: { rate: 0.88, pitch: 1.0 },
  plato: { rate: 0.85, pitch: 0.95 },
  aristotle: { rate: 0.88, pitch: 0.95 },
  confucius: { rate: 0.82, pitch: 0.9 },
  lao_tzu: { rate: 0.78, pitch: 0.85 },
  
  // Literary - expressive
  william_shakespeare: { rate: 0.88, pitch: 1.05 },
  rabindranath_tagore: { rate: 0.85, pitch: 1.0 },
  
  // Psychology
  sigmund_freud: { rate: 0.88, pitch: 0.95 },
  
  // Default
  default: { rate: 0.9, pitch: 1.0 }
};

export const useVoiceConversation = (
  config: VoiceConfig = {},
  onResult?: (result: VoiceResult) => void,
  onError?: (error: string) => void
) => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  
  const [state, setState] = useState<VoiceState>({
    isListening: false,
    isSpeaking: false,
    isSupported: false,
    isSpeechSupported: false,
    transcript: '',
    interimTranscript: '',
    error: null,
    audioLevel: 0
  });

  const recognitionRef = useRef<any>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Get language code
  const getLanguageCode = useCallback((lang: string): string => {
    const langMap: Record<string, string> = {
      'hi': 'hi-IN',
      'en': 'en-US'
    };
    return langMap[lang] || 'en-US';
  }, []);

  // Get voice settings for personality
  const getVoiceSettings = useCallback((personality?: string) => {
    if (!personality) return VOICE_SETTINGS.default;
    const normalizedPersonality = personality.toLowerCase().replace(/\s+/g, '_');
    return VOICE_SETTINGS[normalizedPersonality] || VOICE_SETTINGS.default;
  }, []);

  // Check browser support on mount
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const isSpeechSupported = 'speechSynthesis' in window;
    
    setState(prev => ({
      ...prev,
      isSupported: !!SpeechRecognition,
      isSpeechSupported
    }));
  }, []);

  // Initialize speech recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = finalConfig.continuous ?? false;
    recognition.interimResults = finalConfig.interimResults ?? true;
    recognition.lang = getLanguageCode(finalConfig.language || 'en');
    recognition.maxAlternatives = 3;

    recognition.addEventListener('start', () => {
      setState(prev => ({
        ...prev,
        isListening: true,
        transcript: '',
        interimTranscript: '',
        error: null
      }));
    });

    recognition.addEventListener('result', (event: SpeechRecognitionEvent) => {
      let finalTranscript = '';
      let interimTranscript = '';
      let maxConfidence = 0;

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;
        const confidence = result[0].confidence || 0;

        if (result.isFinal) {
          finalTranscript += transcript;
          maxConfidence = Math.max(maxConfidence, confidence);
        } else {
          interimTranscript += transcript;
        }
      }

      setState(prev => ({
        ...prev,
        transcript: finalTranscript || prev.transcript,
        interimTranscript
      }));

      if (finalTranscript) {
        onResult?.({
          text: finalTranscript,
          confidence: maxConfidence,
          isFinal: true
        });
      }
    });

    recognition.addEventListener('error', (event: SpeechRecognitionErrorEvent) => {
      let errorMessage = 'Voice recognition error';
      
      switch (event.error) {
        case 'not-allowed':
          errorMessage = 'Microphone permission denied. Please allow microphone access.';
          break;
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.';
          break;
        case 'network':
          errorMessage = 'Network error. Please check your connection.';
          break;
        case 'aborted':
          errorMessage = 'Recognition aborted';
          break;
        case 'audio-capture':
          errorMessage = 'No microphone found. Please connect a microphone.';
          break;
      }

      setState(prev => ({
        ...prev,
        isListening: false,
        error: errorMessage
      }));
      
      onError?.(errorMessage);
    });

    recognition.addEventListener('end', () => {
      setState(prev => ({
        ...prev,
        isListening: false,
        audioLevel: 0
      }));
    });

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {
          // Ignore cleanup errors
        }
      }
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [finalConfig.continuous, finalConfig.interimResults, finalConfig.language, getLanguageCode, onResult, onError]);

  // Start listening
  const startListening = useCallback(async () => {
    if (!recognitionRef.current || state.isListening) return;

    try {
      // Request microphone permission first
      await navigator.mediaDevices.getUserMedia({ audio: true });
      
      setState(prev => ({ ...prev, error: null }));
      recognitionRef.current.start();
    } catch (error: any) {
      const errorMessage = error.name === 'NotAllowedError' 
        ? 'Microphone permission denied' 
        : 'Failed to start voice recognition';
      
      setState(prev => ({ ...prev, error: errorMessage }));
      onError?.(errorMessage);
    }
  }, [state.isListening, onError]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !state.isListening) return;

    try {
      recognitionRef.current.stop();
    } catch (error) {
      console.error('Failed to stop voice recognition:', error);
    }
  }, [state.isListening]);

  // Toggle listening
  const toggleListening = useCallback(() => {
    if (state.isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [state.isListening, startListening, stopListening]);

  // Speak text (Text-to-Speech)
  const speak = useCallback((text: string, personality?: string) => {
    if (!state.isSpeechSupported || !text) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    const settings = getVoiceSettings(personality || finalConfig.personality);

    // Find a suitable voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(
      v => v.lang.startsWith('en') && v.name.toLowerCase().includes('male')
    ) || voices.find(v => v.lang.startsWith('en')) || voices[0];

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.rate = settings.rate;
    utterance.pitch = settings.pitch;
    utterance.volume = 1.0;

    utterance.onstart = () => {
      setState(prev => ({ ...prev, isSpeaking: true }));
    };

    utterance.onend = () => {
      setState(prev => ({ ...prev, isSpeaking: false }));
    };

    utterance.onerror = (event) => {
      setState(prev => ({
        ...prev,
        isSpeaking: false,
        error: 'Speech synthesis failed'
      }));
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [state.isSpeechSupported, getVoiceSettings, finalConfig.personality]);

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    if (!state.isSpeechSupported) return;
    
    window.speechSynthesis.cancel();
    setState(prev => ({ ...prev, isSpeaking: false }));
  }, [state.isSpeechSupported]);

  // Toggle speaking
  const toggleSpeaking = useCallback((text: string, personality?: string) => {
    if (state.isSpeaking) {
      stopSpeaking();
    } else {
      speak(text, personality);
    }
  }, [state.isSpeaking, speak, stopSpeaking]);

  // Clear error
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Clear transcript
  const clearTranscript = useCallback(() => {
    setState(prev => ({ 
      ...prev, 
      transcript: '', 
      interimTranscript: '' 
    }));
  }, []);

  return {
    // State
    isListening: state.isListening,
    isSpeaking: state.isSpeaking,
    isSupported: state.isSupported,
    isSpeechSupported: state.isSpeechSupported,
    transcript: state.transcript,
    interimTranscript: state.interimTranscript,
    error: state.error,
    audioLevel: state.audioLevel,

    // Actions
    startListening,
    stopListening,
    toggleListening,
    speak,
    stopSpeaking,
    toggleSpeaking,
    clearError,
    clearTranscript
  };
};

export default useVoiceConversation;
