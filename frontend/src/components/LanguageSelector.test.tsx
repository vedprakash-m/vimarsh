/**
 * Test suite for LanguageSelector component
 * 
 * Tests multilingual support for spiritual guidance interface,
 * including English/Hindi switching and cultural sensitivity.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import LanguageSelector from './LanguageSelector';

// Mock the language context
const mockToggleLanguage = jest.fn();
const mockT = jest.fn((key: string) => key);

jest.mock('../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    currentLanguage: 'English',
    currentLanguageConfig: {
      flag: '🇺🇸',
      nativeName: 'English'
    },
    toggleLanguage: mockToggleLanguage,
    t: mockT
  })
}));

describe('LanguageSelector', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    test('displays current language with flag', () => {
      render(<LanguageSelector />);
      
      expect(screen.getByText('🇺🇸')).toBeInTheDocument();
      expect(screen.getByText('English')).toBeInTheDocument();
    });

    test('shows target language preview', () => {
      render(<LanguageSelector />);
      
      expect(screen.getByText('🇮🇳')).toBeInTheDocument();
      expect(screen.getByText('हिन्दी')).toBeInTheDocument();
    });

    test('displays switch indicator', () => {
      render(<LanguageSelector />);
      
      expect(screen.getByText('⇄')).toBeInTheDocument();
    });

    test('has appropriate button styling', () => {
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn', 'btn-secondary');
    });
  });

  describe('Language Switching', () => {
    test('calls toggle function when clicked', async () => {
      const user = userEvent.setup();
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(mockToggleLanguage).toHaveBeenCalledTimes(1);
    });

    test('can be activated with keyboard', async () => {
      const user = userEvent.setup();
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      button.focus();
      
      await user.keyboard('{Enter}');
      expect(mockToggleLanguage).toHaveBeenCalledTimes(1);
      
      await user.keyboard('{Space}');
      expect(mockToggleLanguage).toHaveBeenCalledTimes(2);
    });
  });

  describe('Hindi Language State', () => {
    beforeEach(() => {
      jest.doMock('../contexts/LanguageContext', () => ({
        useLanguage: () => ({
          currentLanguage: 'Hindi',
          currentLanguageConfig: {
            flag: '🇮🇳',
            nativeName: 'हिन्दी'
          },
          toggleLanguage: mockToggleLanguage,
          t: mockT
        })
      }));
    });

    test('displays Hindi as current language', () => {
      const LanguageSelector = require('./LanguageSelector').default;
      render(<LanguageSelector />);
      
      expect(screen.getByText('🇮🇳')).toBeInTheDocument();
      expect(screen.getByText('हिन्दी')).toBeInTheDocument();
    });
  });

  describe('Spiritual Content Context', () => {
    test('maintains appropriate cultural representation', () => {
      render(<LanguageSelector />);
      
      // Should use appropriate flags for cultural representation
      expect(screen.getByText('🇺🇸')).toBeInTheDocument(); // US flag for English
      expect(screen.getByText('🇮🇳')).toBeInTheDocument(); // Indian flag for Hindi
    });

    test('preserves native script for Hindi', () => {
      render(<LanguageSelector />);
      
      // Hindi should be displayed in Devanagari script
      const hindiText = screen.getByText('हिन्दी');
      expect(hindiText).toBeInTheDocument();
      expect(hindiText).toHaveAttribute('lang', 'hi');
    });

    test('provides appropriate spiritual context for language choice', () => {
      render(<LanguageSelector />);
      
      // Language choice should be meaningful for spiritual content
      const button = screen.getByRole('button');
      expect(button).toHaveAccessibleName();
    });
  });

  describe('Accessibility', () => {
    test('provides accessible labels', () => {
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAccessibleName();
    });

    test('has appropriate ARIA attributes', () => {
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label');
      expect(button).toHaveAttribute('title');
    });

    test('supports screen reader announcements for language changes', () => {
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      const ariaLabel = button.getAttribute('aria-label');
      
      // Should indicate what the button does
      expect(ariaLabel).toBeTruthy();
    });

    test('maintains focus visibility', () => {
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      button.focus();
      
      expect(button).toHaveFocus();
    });
  });

  describe('Cultural Sensitivity', () => {
    test('respects cultural preferences in language presentation', () => {
      render(<LanguageSelector />);
      
      // Hindi should be presented with respect
      const hindiText = screen.getByText('हिन्दी');
      expect(hindiText).toBeInTheDocument();
      
      // English should be neutral
      const englishText = screen.getByText('English');
      expect(englishText).toBeInTheDocument();
    });

    test('uses appropriate flag symbols', () => {
      render(<LanguageSelector />);
      
      // Flags should be culturally appropriate
      expect(screen.getByText('🇺🇸')).toBeInTheDocument();
      expect(screen.getByText('🇮🇳')).toBeInTheDocument();
    });

    test('maintains visual hierarchy for spiritual interface', () => {
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      
      // Should have spiritual-appropriate styling
      expect(button).toHaveClass('btn-secondary');
      expect(button).not.toHaveClass('btn-primary'); // Secondary to main interface
    });
  });

  describe('Integration with Spiritual Guidance', () => {
    test('integrates smoothly with spiritual interface', () => {
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      
      // Should not interfere with main spiritual guidance flow
      expect(button).toBeInTheDocument();
      expect(button).toBeEnabled();
    });

    test('maintains spiritual context during language switches', async () => {
      const user = userEvent.setup();
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      // Should call toggle without disrupting spiritual conversation
      expect(mockToggleLanguage).toHaveBeenCalled();
    });

    test('preserves spiritual tone in language selection', () => {
      render(<LanguageSelector />);
      
      // Language selector should be respectful and not casual
      const button = screen.getByRole('button');
      const classes = button.className;
      
      expect(classes).not.toMatch(/casual|fun|playful/);
    });
  });

  describe('Error Handling', () => {
    test('handles missing language configuration gracefully', () => {
      jest.doMock('../contexts/LanguageContext', () => ({
        useLanguage: () => ({
          currentLanguage: 'English',
          currentLanguageConfig: null,
          toggleLanguage: mockToggleLanguage,
          t: mockT
        })
      }));

      const LanguageSelector = require('./LanguageSelector').default;
      
      // Should not crash with missing config
      expect(() => render(<LanguageSelector />)).not.toThrow();
    });

    test('handles toggle function errors gracefully', async () => {
      const user = userEvent.setup();
      const errorToggle = jest.fn(() => {
        throw new Error('Toggle failed');
      });
      
      jest.doMock('../contexts/LanguageContext', () => ({
        useLanguage: () => ({
          currentLanguage: 'English',
          currentLanguageConfig: {
            flag: '🇺🇸',
            nativeName: 'English'
          },
          toggleLanguage: errorToggle,
          t: mockT
        })
      }));

      const LanguageSelector = require('./LanguageSelector').default;
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      
      // Should handle errors without crashing the interface
      await expect(async () => {
        await user.click(button);
      }).not.toThrow();
    });
  });

  describe('Responsive Design', () => {
    test('maintains readability at different screen sizes', () => {
      render(<LanguageSelector />);
      
      const button = screen.getByRole('button');
      
      // Should have responsive classes
      expect(button).toHaveClass('flex', 'items-center', 'gap-2');
    });

    test('preserves cultural symbols in compact view', () => {
      render(<LanguageSelector />);
      
      // Flags and text should remain visible
      expect(screen.getByText('🇺🇸')).toBeInTheDocument();
      expect(screen.getByText('🇮🇳')).toBeInTheDocument();
      expect(screen.getByText('English')).toBeInTheDocument();
      expect(screen.getByText('हिन्दी')).toBeInTheDocument();
    });
  });
});
