import React, { useEffect } from 'react';
import { usePersonality } from '../contexts/PersonalityContext';
import { useSettings } from '../contexts/SettingsContext';

/**
 * Theme Manager Component
 * Dynamically applies domain-specific and dark mode themes based on selected personality and settings.
 */
export const DomainThemeManager: React.FC = () => {
  const { selectedPersonality } = usePersonality();
  const { settings } = useSettings();

  // Handle Domain Theme
  useEffect(() => {
    let domain = 'spiritual';
    if (selectedPersonality) {
      domain = selectedPersonality.domain.toLowerCase();
      // Special handling for Rumi who is mystical/philosophical
      if (domain === 'spiritual' && selectedPersonality.name.toLowerCase().includes('rumi')) {
        domain = 'philosophical';
      }
    }
    document.documentElement.setAttribute('data-domain', domain);
  }, [selectedPersonality]);

  // Handle Light/Dark Mode Theme
  useEffect(() => {
    const themePref = settings?.experience_preferences?.theme || 'auto';
    
    const applyTheme = (theme: 'light' | 'dark') => {
      document.documentElement.setAttribute('data-theme', theme);
    };

    if (themePref === 'auto') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      applyTheme(isDark ? 'dark' : 'light');
      
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e: MediaQueryListEvent) => {
        applyTheme(e.matches ? 'dark' : 'light');
      };
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      applyTheme(themePref);
    }
  }, [settings?.experience_preferences?.theme]);

  // Handle Text Size and Reduced Animations
  useEffect(() => {
    const textSize = settings?.experience_preferences?.text_size || 'medium';
    document.documentElement.setAttribute('data-text-size', textSize);
    
    const reduceAnimations = settings?.experience_preferences?.reduce_animations || false;
    document.documentElement.setAttribute('data-reduce-animations', reduceAnimations.toString());
  }, [settings?.experience_preferences?.text_size, settings?.experience_preferences?.reduce_animations]);

  return null; // This component only manages themes, no UI
};

/**
 * Domain Theme Configuration (Legacy export for remaining dependencies)
 */
export const DOMAIN_THEMES = {
  spiritual: {
    name: 'Sacred Harmony',
    description: 'Reverent design inspired by ancient spiritual traditions',
    primaryColor: '#f59e0b',
    personalities: ['Krishna', 'Buddha', 'Jesus']
  },
  scientific: {
    name: 'Rational Clarity', 
    description: 'Clean, precise design reflecting scientific methodology',
    primaryColor: '#3b82f6',
    personalities: ['Einstein']
  },
  historical: {
    name: 'Timeless Authority',
    description: 'Classical design honoring historical gravitas',
    primaryColor: '#6b7280', 
    personalities: ['Lincoln']
  },
  philosophical: {
    name: 'Contemplative Wisdom',
    description: 'Thoughtful design for deep philosophical inquiry',
    primaryColor: '#6366f1',
    personalities: ['Marcus Aurelius', 'Lao Tzu', 'Rumi']
  },
  leadership: {
    name: 'Strategic Vision',
    description: 'Commanding and strategic design',
    primaryColor: '#10b981',
    personalities: []
  },
  literary: {
    name: 'Poetic Flow',
    description: 'Elegant and flowing design',
    primaryColor: '#f43f5e',
    personalities: []
  },
  psychology: {
    name: 'Inner Insight',
    description: 'Deep and introspective design',
    primaryColor: '#14b8a6',
    personalities: []
  }
};

export function getPersonalityTheme(personalityName: string, domain: string) {
  const themeKey = domain.toLowerCase() === 'spiritual' && personalityName.toLowerCase().includes('rumi') 
    ? 'philosophical' 
    : domain.toLowerCase();
    
  return DOMAIN_THEMES[themeKey as keyof typeof DOMAIN_THEMES] || DOMAIN_THEMES.spiritual;
}
