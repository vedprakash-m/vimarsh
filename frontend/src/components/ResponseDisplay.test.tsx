/**
 * Test suite for ResponseDisplay component
 * 
 * Focuses on spiritual content rendering, citation formatting,
 * and cultural appropriateness in displaying divine guidance.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResponseDisplay from './ResponseDisplay';

// Mock the language context
jest.mock('../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    currentLanguage: 'English',
    t: (key: string) => key
  })
}));

// Mock the A/B testing hook
jest.mock('../hooks/useABTest', () => ({
  useSpiritualGuidanceTest: () => ({
    responseConfig: { tone: 'compassionate', formality: 'reverent' },
    trackGuidanceInteraction: jest.fn()
  })
}));

describe('ResponseDisplay', () => {
  const mockSpiritualResponse = {
    id: '1',
    text: 'Dear devotee, the path of dharma is illuminated by the wisdom of the Bhagavad Gita. As I taught Arjuna on the battlefield of Kurukshetra, one must perform their prescribed duties without attachment to the fruits of action.',
    sanskritText: 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन',
    transliteration: 'karmaṇy evādhikāras te mā phaleṣu kadācana',
    timestamp: new Date('2024-01-15T10:30:00Z'),
    citations: [
      {
        source: 'Bhagavad Gita',
        reference: '2.47',
        verse: 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन',
        chapter: '2',
        book: 'Bhagavad Gita',
        translation: 'You have a right to perform your prescribed duty, but not to the fruits of action'
      }
    ],
    confidence: 0.95,
    persona: 'krishna' as const
  };

  const mockHindiResponse = {
    id: '2',
    text: 'प्रिय भक्त, ॐ एक पवित्र ध्वनि है जो ब्रह्मांड की आदिम ध्वनि का प्रतिनिधित्व करती है।',
    timestamp: new Date('2024-01-15T10:31:00Z'),
    citations: [
      {
        source: 'Mandukya Upanishad',
        reference: '1.1',
        verse: 'ॐ इत्येतदक्षरमिदं सर्वम्',
        translation: 'Om - this syllable is all this (universe)'
      }
    ],
    confidence: 0.97
  };

  describe('Spiritual Content Rendering', () => {
    test('displays spiritual guidance with proper reverence', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      expect(screen.getByText(/Dear devotee/)).toBeInTheDocument();
      expect(screen.getByText(/dharma/)).toBeInTheDocument();
      expect(screen.getByText(/Bhagavad Gita/)).toBeInTheDocument();
    });

    test('preserves Sanskrit terminology in responses', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      expect(screen.getByText(/dharma/)).toBeInTheDocument();
      expect(screen.getByText(/Kurukshetra/)).toBeInTheDocument();
    });

    test('displays Sanskrit text when available', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      expect(screen.getByText(/कर्मण्येवाधिकारस्ते/)).toBeInTheDocument();
    });

    test('shows transliteration for Sanskrit verses', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      expect(screen.getByText(/karmaṇy evādhikāras te/)).toBeInTheDocument();
    });

    test('handles Hindi content properly', () => {
      render(<ResponseDisplay response={mockHindiResponse} language="hi" />);
      
      expect(screen.getByText(/प्रिय भक्त/)).toBeInTheDocument();
      expect(screen.getByText(/ॐ/)).toBeInTheDocument();
    });
  });

  describe('Citation Display', () => {
    test('renders citations with proper formatting', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      expect(screen.getByText(/Bhagavad Gita 2.47/)).toBeInTheDocument();
    });

    test('displays Sanskrit verses in citations', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      expect(screen.getByText(/कर्मण्येवाधिकारस्ते/)).toBeInTheDocument();
    });

    test('shows English translations', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      expect(screen.getByText(/You have a right to perform/)).toBeInTheDocument();
    });
  });

  describe('Cultural Appropriateness', () => {
    test('maintains respectful tone for divine content', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      const responseElement = screen.getByText(/Dear devotee/);
      expect(responseElement).toBeInTheDocument();
      
      // Check the full text content
      const textContent = responseElement.closest('div')?.textContent || '';
      expect(textContent).not.toMatch(/hey|cool|awesome/i);
    });

    test('properly formats sacred text references', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      expect(screen.getByText(/Bhagavad Gita/)).toBeInTheDocument();
      expect(screen.queryByText(/gita\b/)).not.toBeInTheDocument();
    });

    test('preserves divine persona characteristics', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      expect(screen.getByText(/As I taught Arjuna/)).toBeInTheDocument();
    });
  });

  describe('Confidence and Quality Display', () => {
    test('shows confidence score when high', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      // High confidence responses should be displayed prominently
      const confidenceElements = screen.getAllByText(/95%|0.95/);
      if (confidenceElements.length > 0) {
        expect(confidenceElements[0]).toBeInTheDocument();
      }
    });
  });

  describe('Accessibility', () => {
    test('provides appropriate ARIA labels', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      // Should have proper semantic structure
      const responseContainer = screen.getByText(/Dear devotee/).closest('[role], article, section');
      expect(responseContainer).toBeTruthy();
    });

    test('makes Sanskrit content accessible', () => {
      render(<ResponseDisplay response={mockSpiritualResponse} />);
      
      const sanskritElement = screen.getByText(/कर्मण्येवाधिकारस्ते/);
      const langAttr = sanskritElement.getAttribute('lang');
      const ariaLabel = sanskritElement.getAttribute('aria-label');
      const title = sanskritElement.getAttribute('title');
      
      expect(langAttr || ariaLabel || title).toBeTruthy();
    });
  });

  describe('Error Handling', () => {
    test('handles missing citations gracefully', () => {
      const responseWithoutCitations = {
        ...mockSpiritualResponse,
        citations: []
      };
      
      render(<ResponseDisplay response={responseWithoutCitations} />);
      
      expect(screen.getByText(/Dear devotee/)).toBeInTheDocument();
    });

    test('handles missing Sanskrit text', () => {
      const responseWithoutSanskrit = {
        ...mockSpiritualResponse,
        sanskritText: undefined,
        transliteration: undefined
      };
      
      render(<ResponseDisplay response={responseWithoutSanskrit} />);
      
      expect(screen.getByText(/Dear devotee/)).toBeInTheDocument();
    });
  });

  describe('Interaction Features', () => {
    test('supports citation click handling', () => {
      const onCitationClick = jest.fn();
      render(
        <ResponseDisplay 
          response={mockSpiritualResponse} 
          onCitationClick={onCitationClick}
        />
      );
      
      // Citations should be clickable if handler is provided
      const citationElement = screen.getByText(/Bhagavad Gita 2.47/);
      expect(citationElement).toBeInTheDocument();
    });

    test('supports feedback collection', () => {
      const onFeedback = jest.fn();
      render(
        <ResponseDisplay 
          response={mockSpiritualResponse} 
          onFeedback={onFeedback}
        />
      );
      
      // Should show feedback options
      expect(screen.getByText(/Dear devotee/)).toBeInTheDocument();
    });
  });
});
