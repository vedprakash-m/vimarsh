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
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0.75rem 1rem',
        background: '#ffffff',
        border: '2px solid #e2e8f0',
        borderRadius: '0.75rem',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        fontSize: '0.875rem',
        fontWeight: '500',
        color: '#1e293b',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = '#FF6B35';
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(255, 107, 53, 0.15)';
        e.currentTarget.style.transform = 'translateY(-1px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = '#e2e8f0';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.06)';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
      aria-label={currentLanguage === 'English' ? t('switchToHindi') : t('switchToEnglish')}
      title={`${t('switchToHindi')} / ${t('switchToEnglish')}`}
    >
      {/* Current language display */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.25rem'
      }}>
        <span style={{ fontSize: '0.875rem' }}>{currentLanguageConfig.flag}</span>
        <span style={{
          fontWeight: '600',
          fontSize: '0.75rem',
          color: '#1e293b'
        }}>
          {currentLanguageConfig.nativeName}
        </span>
      </div>
      
      {/* Switch indicator */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        color: '#FF6B35'
      }}>
        <span style={{ fontSize: '0.875rem' }}>⇄</span>
      </div>
      
      {/* Target language preview */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.25rem',
        opacity: 0.6
      }}>
        <span style={{ fontSize: '0.875rem' }}>{otherLanguageConfig.flag}</span>
        <span style={{
          fontWeight: '600',
          fontSize: '0.75rem',
          color: '#64748b'
        }}>
          {otherLanguageConfig.nativeName}
        </span>
      </div>
    </button>
  );
};

export default LanguageSelector;
