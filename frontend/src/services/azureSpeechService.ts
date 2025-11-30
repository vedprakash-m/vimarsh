/**
 * Azure Speech Service Client
 * 
 * Provides personality-specific text-to-speech using Azure Neural Voices.
 * Each personality has a unique voice with appropriate gender, locale, and style.
 */

import { API_BASE_URL } from '../config/environment';

// Audio format options
export type AudioFormat = 'mp3' | 'mp3-hd' | 'wav' | 'ogg';

// Voice configuration for a personality
export interface VoiceConfig {
  voice_name: string;
  gender: 'male' | 'female';
  locale: string;
  style: string;
  description: string;
}

// Voice info response from API
export interface VoiceInfoResponse {
  service_available: boolean;
  total_personalities: number;
  personalities: Record<string, VoiceConfig>;
  supported_formats: AudioFormat[];
  timestamp: string;
}

// Synthesis request
export interface SynthesisRequest {
  text: string;
  personality?: string;
  format?: AudioFormat;
}

// Cache for audio blobs to avoid re-synthesis
const audioCache = new Map<string, string>();
const MAX_CACHE_SIZE = 50;

// Cache key generator
function getCacheKey(text: string, personality: string, format: AudioFormat): string {
  return `${personality}:${format}:${text.slice(0, 100)}`;
}

/**
 * Azure Speech Service client for personality TTS
 */
class AzureSpeechService {
  private voiceInfo: VoiceInfoResponse | null = null;
  private currentAudio: HTMLAudioElement | null = null;

  /**
   * Get voice service information and available personalities
   */
  async getVoiceInfo(): Promise<VoiceInfoResponse> {
    if (this.voiceInfo) {
      return this.voiceInfo;
    }

    const response = await fetch(`${API_BASE_URL}/api/voice/info`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get voice info: ${response.statusText}`);
    }

    this.voiceInfo = await response.json();
    return this.voiceInfo!;
  }

  /**
   * Check if the voice service is available
   */
  async isAvailable(): Promise<boolean> {
    try {
      const info = await this.getVoiceInfo();
      return info.service_available;
    } catch {
      return false;
    }
  }

  /**
   * Synthesize speech for the given text and personality
   * 
   * @param text - Text to convert to speech
   * @param personality - Personality ID (e.g., "krishna", "buddha")
   * @param format - Audio format (default: "mp3")
   * @returns Blob URL for the audio
   */
  async synthesize(
    text: string,
    personality: string = 'krishna',
    format: AudioFormat = 'mp3'
  ): Promise<string> {
    // Check cache first
    const cacheKey = getCacheKey(text, personality, format);
    if (audioCache.has(cacheKey)) {
      return audioCache.get(cacheKey)!;
    }

    const response = await fetch(`${API_BASE_URL}/api/voice/synthesize`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        personality,
        format,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Speech synthesis failed: ${response.statusText}`);
    }

    // Get audio blob and create URL
    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);

    // Cache the result (with size limit)
    if (audioCache.size >= MAX_CACHE_SIZE) {
      // Remove oldest entry
      const firstKey = audioCache.keys().next().value;
      if (firstKey) {
        URL.revokeObjectURL(audioCache.get(firstKey)!);
        audioCache.delete(firstKey);
      }
    }
    audioCache.set(cacheKey, audioUrl);

    return audioUrl;
  }

  /**
   * Play synthesized speech for the given text
   * 
   * @param text - Text to speak
   * @param personality - Personality ID
   * @param options - Playback options
   * @returns Promise that resolves when playback completes
   */
  async speak(
    text: string,
    personality: string = 'krishna',
    options: {
      format?: AudioFormat;
      onStart?: () => void;
      onEnd?: () => void;
      onError?: (error: Error) => void;
    } = {}
  ): Promise<void> {
    const { format = 'mp3', onStart, onEnd, onError } = options;

    try {
      // Stop any currently playing audio
      this.stop();

      // Get audio URL (may be cached)
      const audioUrl = await this.synthesize(text, personality, format);

      // Create and play audio element
      this.currentAudio = new Audio(audioUrl);
      
      return new Promise((resolve, reject) => {
        if (!this.currentAudio) {
          reject(new Error('Audio element not created'));
          return;
        }

        this.currentAudio.onplay = () => {
          onStart?.();
        };

        this.currentAudio.onended = () => {
          onEnd?.();
          this.currentAudio = null;
          resolve();
        };

        this.currentAudio.onerror = () => {
          const error = new Error('Audio playback failed');
          onError?.(error);
          this.currentAudio = null;
          reject(error);
        };

        this.currentAudio.play().catch((err) => {
          onError?.(err);
          reject(err);
        });
      });
    } catch (error) {
      onError?.(error as Error);
      throw error;
    }
  }

  /**
   * Stop currently playing audio
   */
  stop(): void {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
  }

  /**
   * Pause currently playing audio
   */
  pause(): void {
    if (this.currentAudio) {
      this.currentAudio.pause();
    }
  }

  /**
   * Resume paused audio
   */
  resume(): void {
    if (this.currentAudio) {
      this.currentAudio.play();
    }
  }

  /**
   * Check if audio is currently playing
   */
  isPlaying(): boolean {
    return this.currentAudio !== null && !this.currentAudio.paused;
  }

  /**
   * Get the current audio element for advanced control
   */
  getCurrentAudio(): HTMLAudioElement | null {
    return this.currentAudio;
  }

  /**
   * Clear the audio cache
   */
  clearCache(): void {
    audioCache.forEach((url) => URL.revokeObjectURL(url));
    audioCache.clear();
  }

  /**
   * Get voice configuration for a specific personality
   */
  async getVoiceConfig(personality: string): Promise<VoiceConfig | undefined> {
    const info = await this.getVoiceInfo();
    return info.personalities[personality];
  }
}

// Singleton instance
const azureSpeechService = new AzureSpeechService();

export default azureSpeechService;

// Named exports for convenience
export { azureSpeechService };
