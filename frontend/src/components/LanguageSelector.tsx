import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';

const LanguageSelector: React.FC = () => {
  const { currentLanguage, currentLanguageConfig, toggleLanguage, t } = useLanguage();

  const otherLanguage = currentLanguage === 'English' ? 'Hindi' : 'English';
  const otherLanguageConfig = currentLanguage === 'English' 
    ? { flag: '🇮🇳', nativeName: 'हिन्दी' }
    : { flag: '🇺🇸', nativeName: 'English' };

  return (
    <button
      onClick={toggleLanguage}
      className="btn btn-secondary flex items-center gap-2 transition-all hover:shadow-md"
      aria-label={currentLanguage === 'English' ? t('switchToHindi') : t('switchToEnglish')}
      title={`${t('switchToHindi')} / ${t('switchToEnglish')}`}
    >
      {/* Current language display */}
      <div className="flex items-center gap-1">
        <span className="text-sm">{currentLanguageConfig.flag}</span>
        <span className="font-medium text-xs">
          {currentLanguageConfig.nativeName}
        </span>
      </div>
      
      {/* Switch indicator */}
      <div className="flex items-center text-neutral-400">
        <span className="text-xs">⇄</span>
      </div>
      
      {/* Target language preview */}
      <div className="flex items-center gap-1 opacity-60">
        <span className="text-sm">{otherLanguageConfig.flag}</span>
        <span className="font-medium text-xs">
          {otherLanguageConfig.nativeName}
        </span>
      </div>
    </button>
  );
};

export default LanguageSelector;
