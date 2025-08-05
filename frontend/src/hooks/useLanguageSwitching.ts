// Language switching hook with integration support
// Provides easy language switching with voice interface integration

import { usePersonality } from '../contexts/PersonalityContext';

import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../auth/AuthProvider';

export interface LanguageSwitchingOptions {
  persistToUser?: boolean;
  notifyUser?: boolean;
  updateVoiceSettings?: boolean;
}

export const useLanguageSwitching = () => {
  const { 
    currentLanguage, 
    currentLanguageConfig,
    setLanguage, 
    toggleLanguage, 
    t 
  } = useLanguage();
  
  const { account } = useAuth();

  // Switch to specific language with options
  const switchToLanguage = async (
    language: 'English' | 'Hindi', 
    options: LanguageSwitchingOptions = {}
  ) => {
    const {
      persistToUser = true,
      notifyUser = true,
      updateVoiceSettings = true
    } = options;

    try {
      // Update language context
      setLanguage(language);

      // Persist to user profile if authenticated
      if (persistToUser && account) {
        // TODO: Update user preference via API
        console.log(`🌍 Saving language preference: ${language} for user ${account.name}`);
      }

      // Show notification to user
      if (notifyUser) {
        showLanguageChangeNotification(language);
      }

      // Update voice settings for speech synthesis
      if (updateVoiceSettings && 'speechSynthesis' in window) {
        updateVoiceLanguage(language);
      }

      console.log(`🔄 Language switched to ${language}`);
      
    } catch (error) {
      console.error('Failed to switch language:', error);
      // TODO: Show error notification
    }
  };

  // Toggle between English and Hindi
  const toggleLanguageWithOptions = (options?: LanguageSwitchingOptions) => {
    const newLanguage = currentLanguage === 'English' ? 'Hindi' : 'English';
    return switchToLanguage(newLanguage, options);
  };

  // Show language change notification
  const showLanguageChangeNotification = (language: 'English' | 'Hindi') => {
    const message = language === 'English' 
      ? 'Language changed to English'
      : 'भाषा हिन्दी में बदल गई';

    // Create temporary notification element
    const notification = document.createElement('div');
    notification.className = 'language-notification';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
      if (document.body.contains(notification)) {
        notification.style.animation = 'slideOutDown 0.3s ease';
        setTimeout(() => {
          document.body.removeChild(notification);
        }, 300);
      }
    }, 3000);
  };

  // Update voice synthesis language
  const updateVoiceLanguage = (language: 'English' | 'Hindi') => {
    try {
      const voices = speechSynthesis.getVoices();
      const langCode = language === 'Hindi' ? 'hi' : 'en';
      
      const preferredVoice = voices.find(voice => 
        voice.lang.startsWith(langCode)
      );
      
      if (preferredVoice) {
        console.log(`🎤 Voice updated for ${language}: ${preferredVoice.name}`);
      }
    } catch (error) {
      console.warn('Failed to update voice language:', error);
    }
  };

  // Get language-specific greeting based on time of day
  const getContextualGreeting = (): string => {
    const hour = new Date().getHours();
    
    if (currentLanguage === 'Hindi') {
      if (hour < 12) return 'सुप्रभात'; // Good morning
      if (hour < 17) return 'नमस्कार'; // Good afternoon
      return 'सुसंध्या'; // Good evening
    } else {
      if (hour < 12) return 'Good morning';
      if (hour < 17) return 'Good afternoon';
      return 'Good evening';
    }
  };

  // Get language-specific formatting preferences
  const getFormattingPreferences = () => {
    return {
      dateFormat: currentLanguage === 'Hindi' ? 'dd/mm/yyyy' : 'mm/dd/yyyy',
      numberFormat: currentLanguage === 'Hindi' ? 'hi-IN' : 'en-US',
      currencyFormat: 'INR',
      textDirection: currentLanguageConfig.direction,
      fontFamily: currentLanguage === 'Hindi' 
        ? 'Noto Sans Devanagari, Mangal, sans-serif'
        : 'Inter, Segoe UI, sans-serif'
    };
  };

  // Check if browser supports the current language
  const isLanguageSupported = (): boolean => {
    const langCode = currentLanguageConfig.code;
    return navigator.languages.some(lang => lang.startsWith(langCode));
  };

  // Get language-specific voice configuration
  const getVoiceConfiguration = () => {
    return {
      lang: currentLanguageConfig.voiceCode,
      rate: currentLanguage === 'Hindi' ? 0.85 : 0.9, // Slower for Hindi
      pitch: currentLanguage === 'Hindi' ? 1.1 : 1.0,
      volume: 0.9
    };
  };

  return {
    // Current state
    currentLanguage,
    currentLanguageConfig,
    
    // Language switching
    switchToLanguage,
    toggleLanguage: toggleLanguageWithOptions,
    
    // Utilities
    t,
    getContextualGreeting,
    getFormattingPreferences,
    getVoiceConfiguration,
    isLanguageSupported,
    
    // Status
    isHindi: currentLanguage === 'Hindi',
    isEnglish: currentLanguage === 'English',
    languageCode: currentLanguageConfig.code,
    nativeName: currentLanguageConfig.nativeName,
    flag: currentLanguageConfig.flag
  };
};

export default useLanguageSwitching;
