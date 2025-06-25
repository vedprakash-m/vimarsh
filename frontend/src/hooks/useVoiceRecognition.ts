import { useState, useEffect, useRef, useCallback } from 'react';

interface VoiceRecognitionConfig {
  language?: 'en' | 'hi';
  continuous?: boolean;
  interimResults?: boolean;
  maxAlternatives?: number;
}

interface VoiceRecognitionState {
  isListening: boolean;
  isSupported: boolean;
  transcript: string;
  finalTranscript: string;
  interimTranscript: string;
  confidence: number;
  error: string | null;
}

interface VoiceRecognitionResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
  alternatives?: string[];
}

const DEFAULT_CONFIG: VoiceRecognitionConfig = {
  language: 'en',
  continuous: false,
  interimResults: true,
  maxAlternatives: 3
};

export const useVoiceRecognition = (
  config: VoiceRecognitionConfig = {},
  onResult?: (result: VoiceRecognitionResult) => void,
  onError?: (error: string) => void
) => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  
  const [state, setState] = useState<VoiceRecognitionState>({
    isListening: false,
    isSupported: false,
    transcript: '',
    finalTranscript: '',
    interimTranscript: '',
    confidence: 0,
    error: null
  });

  const recognitionRef = useRef<any>(null);

  const getLanguageCode = (lang: string): string => {
    switch (lang) {
      case 'hi':
        return 'hi-IN';
      case 'en':
        return 'en-US';
      default:
        return 'en-US';
    }
  };

  const initializeRecognition = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    
    recognition.continuous = finalConfig.continuous || false;
    recognition.interimResults = finalConfig.interimResults !== false;
    recognition.maxAlternatives = finalConfig.maxAlternatives || 3;
    recognition.lang = getLanguageCode(finalConfig.language || 'en');

    recognition.addEventListener('start', () => {
      setState(prev => ({
        ...prev,
        isListening: true,
        error: null,
        transcript: '',
        finalTranscript: '',
        interimTranscript: ''
      }));
    });

    recognition.addEventListener('result', (event: any) => {
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
          
          onResult?.({
            transcript: transcript.trim(),
            confidence,
            isFinal: true
          });
        } else {
          interimTranscript += transcript;
          
          onResult?.({
            transcript: transcript.trim(),
            confidence: confidence || 0,
            isFinal: false
          });
        }
      }

      setState(prev => ({
        ...prev,
        finalTranscript: prev.finalTranscript + finalTranscript,
        interimTranscript,
        transcript: prev.finalTranscript + finalTranscript + interimTranscript,
        confidence: maxConfidence
      }));
    });

    recognition.addEventListener('error', (event: any) => {
      const errorMessage = `Speech recognition error: ${event.error}`;
      
      setState(prev => ({
        ...prev,
        error: errorMessage,
        isListening: false
      }));

      onError?.(errorMessage);
    });

    recognition.addEventListener('end', () => {
      setState(prev => ({
        ...prev,
        isListening: false
      }));
    });

    recognitionRef.current = recognition;
  }, [finalConfig, onResult, onError]);

  const startListening = useCallback(() => {
    if (!state.isSupported || !recognitionRef.current || state.isListening) {
      return false;
    }

    try {
      recognitionRef.current.start();
      return true;
    } catch (error) {
      const errorMessage = 'Failed to start speech recognition';
      setState(prev => ({ ...prev, error: errorMessage }));
      onError?.(errorMessage);
      return false;
    }
  }, [state.isSupported, state.isListening, onError]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current && state.isListening) {
      recognitionRef.current.stop();
    }
  }, [state.isListening]);

  const toggleListening = useCallback(() => {
    if (state.isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [state.isListening, startListening, stopListening]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Initialize on mount
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      setState(prev => ({ ...prev, isSupported: true }));
      initializeRecognition();
    } else {
      setState(prev => ({ 
        ...prev, 
        isSupported: false,
        error: 'Speech recognition not supported in this browser'
      }));
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [initializeRecognition]);

  return {
    isListening: state.isListening,
    isSupported: state.isSupported,
    transcript: state.transcript,
    finalTranscript: state.finalTranscript,
    interimTranscript: state.interimTranscript,
    confidence: state.confidence,
    error: state.error,
    startListening,
    stopListening,
    toggleListening,
    clearError,
    hasTranscript: state.transcript.length > 0,
    currentLanguage: finalConfig.language
  };
};