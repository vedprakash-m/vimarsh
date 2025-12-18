/**
 * Personality Context Provider for Vimarsh
 * 
 * Manages the currently selected personality across the application
 * and provides personality-related functionality.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Personality interface matching the application structure
export interface Personality {
  id: string;
  name: string;
  display_name: string;
  domain: 'spiritual' | 'scientific' | 'historical' | 'philosophical' | 'literary' | 'leadership' | 'psychology';
  time_period: string;
  description: string;
  expertise_areas: string[];
  cultural_context: string;
  quality_score: number;
  usage_count: number;
  is_active: boolean;
  tags: string[];
  // UI-specific properties for backward compatibility
  color?: string;
  darkColor?: string;
  expertise?: string;
  voice_settings?: {
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
  pronunciation_guide?: {
    [term: string]: {
      phonetic: string;
      audio_url?: string;
      language: string;
    };
  };
}

interface PersonalityContextType {
  selectedPersonality: Personality | null;
  setSelectedPersonality: (personality: Personality | null) => void;
  personalitySwitchNotification: string | null;
  setPersonalitySwitchNotification: (message: string | null) => void;
  personalityLoading: boolean;
  setPersonalityLoading: (loading: boolean) => void;
  availablePersonalities: Personality[];
  setAvailablePersonalities: (personalities: Personality[]) => void;
  loadPersonalities: () => Promise<void>;
}

const PersonalityContext = createContext<PersonalityContextType | undefined>(undefined);

interface PersonalityProviderProps {
  children: ReactNode;
}

// Default Krishna personality for fallback
const DEFAULT_KRISHNA_PERSONALITY: Personality = {
  id: 'krishna',
  name: 'Krishna',
  display_name: 'Krishna',
  domain: 'spiritual',
  time_period: 'Ancient India (3000+ BCE)',
  description: 'Divine teacher and guide from the Bhagavad Gita, offering spiritual wisdom and life guidance',
  expertise_areas: ['dharma', 'karma', 'devotion', 'self-realization', 'divine wisdom'],
  cultural_context: 'Ancient Indian spiritual tradition',
  quality_score: 95.0,
  usage_count: 1000,
  is_active: true,
  tags: ['spiritual', 'divine', 'bhagavad-gita', 'dharma']
};

// Request deduplication: track in-flight personality load requests
let personalitiesLoadPromise: Promise<void> | null = null;

export const PersonalityProvider: React.FC<PersonalityProviderProps> = ({ children }) => {
  // State management
  const [selectedPersonality, setSelectedPersonalityState] = useState<Personality | null>(null);
  const [personalitySwitchNotification, setPersonalitySwitchNotification] = useState<string | null>(null);
  const [personalityLoading, setPersonalityLoading] = useState<boolean>(false);
  const [availablePersonalities, setAvailablePersonalities] = useState<Personality[]>([]);

  // Enhanced personality setter with persistence
  const setSelectedPersonality = (personality: Personality | null) => {
    setSelectedPersonalityState(personality);
    
    // Persist to localStorage
    if (personality) {
      try {
        localStorage.setItem('vimarsh_selected_personality', JSON.stringify(personality));
      } catch (error) {
        console.error('Failed to save personality to localStorage:', error);
      }
    } else {
      try {
        localStorage.removeItem('vimarsh_selected_personality');
      } catch (error) {
        console.error('Failed to remove personality from localStorage:', error);
      }
    }
  };

  // Load personalities from API with request deduplication
  const loadPersonalities = async () => {
    // If already loading, return existing promise to prevent duplicate calls
    if (personalitiesLoadPromise) {
      if (process.env.NODE_ENV === 'development') {
        console.log('⏭️ PersonalityContext: Load already in progress, reusing promise');
      }
      return personalitiesLoadPromise;
    }
    
    // If already loaded, skip
    if (availablePersonalities.length > 0) {
      if (process.env.NODE_ENV === 'development') {
        console.log('✅ PersonalityContext: Personalities already loaded, skipping');
      }
      return;
    }
    
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log('🔄 PersonalityContext: Starting personality load...');
      }
      
      // Create and store the load promise
      personalitiesLoadPromise = (async () => {
        setPersonalityLoading(true);
      
      // Check if we're in test environment
      if (process.env.NODE_ENV === 'test') {
        console.log('🧪 PersonalityContext: Test environment detected, using mock data');
        const mockPersonalities: Personality[] = [
          {
            id: 'krishna',
            name: 'krishna',
            display_name: 'Krishna',
            domain: 'spiritual' as const,
            time_period: 'Ancient India (3102 BCE)',
            description: 'Divine incarnation and spiritual guide',
            expertise_areas: ['dharma', 'devotion'],
            cultural_context: 'Hindu tradition',
            quality_score: 95.0,
            usage_count: 1000,
            is_active: true,
            tags: ['spiritual', 'divine']
          }
        ];
        setAvailablePersonalities(mockPersonalities);
        if (!selectedPersonality) {
          setSelectedPersonality(mockPersonalities[0]);
        }
        setPersonalityLoading(false);
        console.log('🏁 PersonalityContext: Personality loading complete (test mode)');
        return;
      }
      
      // Import API configuration
      const { getApiBaseUrl } = await import('../config/environment');
      const apiBaseUrl = getApiBaseUrl();
      
      const params = new URLSearchParams();
      params.append('active_only', 'true');
      
      const url = `${apiBaseUrl}/personalities/active?${params.toString()}`;
      
      if (process.env.NODE_ENV === 'development') {
        console.log('📤 PersonalityContext: Calling API:', url);
      }
      
      const response = await fetch(url);
      
      if (process.env.NODE_ENV === 'development') {
        console.log('📥 PersonalityContext: API response status:', response.status, response.statusText);
      }
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.personalities && Array.isArray(data.personalities)) {
        if (process.env.NODE_ENV === 'development') {
          console.log('✅ PersonalityContext: Successfully loaded', data.personalities.length, 'personalities');
        }
        
        // Map API response to frontend interface
        const mappedPersonalities: Personality[] = data.personalities.map((p: any) => ({
          id: p.id,
          name: p.name,
          display_name: p.name, // Use name as display_name since API doesn't have display_name
          domain: p.domain as 'spiritual' | 'scientific' | 'historical' | 'philosophical' | 'literary' | 'leadership' | 'psychology',
          time_period: 'Ancient/Historical', // Default since API doesn't provide this
          description: p.description,
          expertise_areas: [], // Default since API doesn't provide this
          cultural_context: 'Historical', // Default since API doesn't provide this
          quality_score: 95.0, // Default since API doesn't provide this
          usage_count: 0, // Default since API doesn't provide this
          is_active: true, // Default since API doesn't provide this
          tags: [p.domain] // Use domain as default tag
        }));
        
        setAvailablePersonalities(mappedPersonalities);
      } else {
        console.warn('⚠️ PersonalityContext: Failed to load personalities from API - unexpected response format:', data);
        // Set default personalities if API fails
        setAvailablePersonalities([DEFAULT_KRISHNA_PERSONALITY]);
      }
    } catch (error) {
      console.error('❌ PersonalityContext: Failed to load personalities:', error);
        // Set default personalities on error
        setAvailablePersonalities([DEFAULT_KRISHNA_PERSONALITY]);
      } finally {
        setPersonalityLoading(false);
        if (process.env.NODE_ENV === 'development') {
          console.log('🏁 PersonalityContext: Personality loading complete');
        }
      }
      })();
      
      await personalitiesLoadPromise;
    } finally {
      // Clear the promise after completion (success or failure)
      personalitiesLoadPromise = null;
    }
  };

  // Load saved personality and available personalities on mount
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🚀 PersonalityContext: useEffect triggered - loading personalities and saved state');
    }
    
    // Load saved personality from localStorage (synchronous, fast)
    try {
      const savedPersonality = localStorage.getItem('vimarsh_selected_personality');
      if (savedPersonality) {
        const personality = JSON.parse(savedPersonality);
        if (process.env.NODE_ENV === 'development') {
          console.log('📦 PersonalityContext: Loaded saved personality from localStorage:', personality.name);
        }
        setSelectedPersonalityState(personality);
      } else {
        if (process.env.NODE_ENV === 'development') {
          console.log('🔷 PersonalityContext: No saved personality found, leaving null for user selection');
        }
        setSelectedPersonalityState(null);
      }
    } catch (error) {
      console.error('❌ PersonalityContext: Failed to load saved personality:', error);
      setSelectedPersonalityState(null);
    }

    // Load available personalities (non-blocking)
    if (process.env.NODE_ENV === 'development') {
      console.log('🔄 PersonalityContext: Calling loadPersonalities()');
    }
    loadPersonalities();
  }, []);

  // Context value
  const contextValue: PersonalityContextType = {
    selectedPersonality,
    setSelectedPersonality,
    personalitySwitchNotification,
    setPersonalitySwitchNotification,
    personalityLoading,
    setPersonalityLoading,
    availablePersonalities,
    setAvailablePersonalities,
    loadPersonalities
  };

  return (
    <PersonalityContext.Provider value={contextValue}>
      {children}
    </PersonalityContext.Provider>
  );
};

// Custom hook for using personality context
export const usePersonality = (): PersonalityContextType => {
  const context = useContext(PersonalityContext);
  if (context === undefined) {
    throw new Error('usePersonality must be used within a PersonalityProvider');
  }
  return context;
};

export { PersonalityContext, DEFAULT_KRISHNA_PERSONALITY };
export type { PersonalityContextType };
