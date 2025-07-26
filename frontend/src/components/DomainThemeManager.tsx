import React, { useEffect } from 'react';
import { usePersonality } from '../contexts/PersonalityContext';

/**
 * Domain Theme Manager Component
 * Dynamically applies domain-specific themes based on selected personality
 */
export const DomainThemeManager: React.FC = () => {
  const { selectedPersonality } = usePersonality();

  useEffect(() => {
    // Remove all existing theme classes
    document.body.classList.remove(
      'spiritual-theme',
      'scientific-theme', 
      'historical-theme',
      'philosophical-theme'
    );

    // Apply theme based on personality domain
    if (selectedPersonality) {
      const themeClass = getThemeClass(selectedPersonality.domain, selectedPersonality.name);
      document.body.classList.add(themeClass);
    } else {
      // Default to spiritual theme
      document.body.classList.add('spiritual-theme');
    }
  }, [selectedPersonality]);

  return null; // This component only manages themes, no UI
};

/**
 * Get appropriate theme class based on personality domain and name
 */
function getThemeClass(domain: string, personalityName: string): string {
  switch (domain.toLowerCase()) {
    case 'scientific':
      return 'scientific-theme';
    
    case 'historical':
      return 'historical-theme';
    
    case 'philosophical':
      return 'philosophical-theme';
    
    case 'spiritual':
    default:
      // Special handling for Rumi who is mystical/philosophical
      if (personalityName.toLowerCase().includes('rumi')) {
        return 'philosophical-theme';
      }
      return 'spiritual-theme';
  }
}

/**
 * Domain Theme Configuration
 */
export const DOMAIN_THEMES = {
  spiritual: {
    name: 'Sacred Harmony',
    description: 'Reverent design inspired by ancient spiritual traditions',
    primaryColor: '#FF9933',
    personalities: ['Krishna', 'Buddha', 'Jesus']
  },
  scientific: {
    name: 'Rational Clarity', 
    description: 'Clean, precise design reflecting scientific methodology',
    primaryColor: '#0066CC',
    personalities: ['Einstein']
  },
  historical: {
    name: 'Timeless Authority',
    description: 'Classical design honoring historical gravitas',
    primaryColor: '#1E3A5F', 
    personalities: ['Lincoln']
  },
  philosophical: {
    name: 'Contemplative Wisdom',
    description: 'Thoughtful design for deep philosophical inquiry',
    primaryColor: '#7C3AED',
    personalities: ['Marcus Aurelius', 'Lao Tzu', 'Rumi']
  }
};

/**
 * Get theme information for a personality
 */
export function getPersonalityTheme(personalityName: string, domain: string) {
  const themeKey = domain.toLowerCase() === 'spiritual' && personalityName.toLowerCase().includes('rumi') 
    ? 'philosophical' 
    : domain.toLowerCase();
    
  return DOMAIN_THEMES[themeKey as keyof typeof DOMAIN_THEMES] || DOMAIN_THEMES.spiritual;
}
