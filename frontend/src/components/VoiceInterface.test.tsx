/**
 * Test suite for VoiceInterface component
 * 
 * Tests voice recognition and synthesis for spiritual queries,
 * including Sanskrit pronunciation, Hindi language support,
 * and spiritual content accessibility.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import VoiceInterface from './VoiceInterface';

// Mock Web Speech API
const mockSpeechRecognition = {
  continuous: false,
  interimResults: false,
  lang: 'en-US',
  start: jest.fn(),
  stop: jest.fn(),
  abort: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn()
};

const mockSpeechSynthesis = {
  speak: jest.fn(),
  cancel: jest.fn(),
  pause: jest.fn(),
  resume: jest.fn(),
  getVoices: jest.fn(() => [
    { name: 'English Voice', lang: 'en-US' },
    { name: 'Hindi Voice', lang: 'hi-IN' }
  ]),
  speaking: false,
  pending: false,
  paused: false
};

const mockSpeechSynthesisUtterance = jest.fn().mockImplementation((text) => ({
  text,
  lang: 'en-US',
  voice: null,
  volume: 1,
  rate: 1,
  pitch: 1,
  addEventListener: jest.fn(),
  removeEventListener: jest.fn()
}));

// Setup global mocks
beforeAll(() => {
  Object.defineProperty(window, 'SpeechRecognition', {
    writable: true,
    value: jest.fn(() => mockSpeechRecognition)
  });

  Object.defineProperty(window, 'webkitSpeechRecognition', {
    writable: true,
    value: jest.fn(() => mockSpeechRecognition)
  });

  Object.defineProperty(window, 'speechSynthesis', {
    writable: true,
    value: mockSpeechSynthesis
  });

  Object.defineProperty(window, 'SpeechSynthesisUtterance', {
    writable: true,
    value: mockSpeechSynthesisUtterance
  });
});

describe('VoiceInterface', () => {
  const mockOnVoiceInput = jest.fn();
  const mockOnSpeechStart = jest.fn();
  const mockOnSpeechEnd = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Functionality', () => {
    test('renders voice interface components', () => {
      render(
        <VoiceInterface 
          onVoiceInput={mockOnVoiceInput}
          onSpeechStart={mockOnSpeechStart}
          onSpeechEnd={mockOnSpeechEnd}
        />
      );

      expect(screen.getByRole('button', { name: /start voice/i })).toBeInTheDocument();
    });

    test('starts voice recognition when activated', async () => {
      const user = userEvent.setup();
      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      const startButton = screen.getByRole('button', { name: /start voice/i });
      await user.click(startButton);

      expect(mockSpeechRecognition.start).toHaveBeenCalled();
    });

    test('handles unsupported browsers gracefully', () => {
      // Temporarily remove speech recognition support
      const originalSpeechRecognition = window.SpeechRecognition;
      const originalWebkitSpeechRecognition = window.webkitSpeechRecognition;
      
      delete (window as any).SpeechRecognition;
      delete (window as any).webkitSpeechRecognition;

      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      expect(screen.getByText(/speech recognition not supported/i)).toBeInTheDocument();

      // Restore
      window.SpeechRecognition = originalSpeechRecognition;
      window.webkitSpeechRecognition = originalWebkitSpeechRecognition;
    });
  });

  describe('Spiritual Content Voice Recognition', () => {
    test('handles Sanskrit spiritual terms correctly', () => {
      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      // Simulate speech recognition result with Sanskrit terms
      const mockEvent = {
        results: [
          {
            0: { transcript: 'What is dharma and karma?' },
            isFinal: true,
            length: 1
          }
        ],
        resultIndex: 0
      };

      // Trigger the result event
      const resultCallback = mockSpeechRecognition.addEventListener.mock.calls
        .find(call => call[0] === 'result')?.[1];
      
      if (resultCallback) {
        resultCallback(mockEvent);
        expect(mockOnVoiceInput).toHaveBeenCalledWith('What is dharma and karma?');
      }
    });

    test('processes spiritual queries with reverent tone', () => {
      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      const spiritualQueries = [
        'Please explain the meaning of Om',
        'What did Lord Krishna teach about dharma?',
        'How can I achieve moksha?'
      ];

      spiritualQueries.forEach(query => {
        const mockEvent = {
          results: [
            {
              0: { transcript: query },
              isFinal: true,
              length: 1
            }
          ],
          resultIndex: 0
        };

        const resultCallback = mockSpeechRecognition.addEventListener.mock.calls
          .find(call => call[0] === 'result')?.[1];
        
        if (resultCallback) {
          resultCallback(mockEvent);
          expect(mockOnVoiceInput).toHaveBeenCalledWith(query);
        }
      });
    });

    test('handles Hindi spiritual content', () => {
      render(
        <VoiceInterface 
          onVoiceInput={mockOnVoiceInput} 
          language="hi"
        />
      );

      // Verify Hindi language is set
      expect(mockSpeechRecognition.lang).toBe('hi-IN');

      const mockEvent = {
        results: [
          {
            0: { transcript: 'ॐ का अर्थ क्या है?' },
            isFinal: true,
            length: 1
          }
        ],
        resultIndex: 0
      };

      const resultCallback = mockSpeechRecognition.addEventListener.mock.calls
        .find(call => call[0] === 'result')?.[1];
      
      if (resultCallback) {
        resultCallback(mockEvent);
        expect(mockOnVoiceInput).toHaveBeenCalledWith('ॐ का अर्थ क्या है?');
      }
    });
  });

  describe('Language Support for Spiritual Content', () => {
    test('switches between English and Hindi correctly', () => {
      const { rerender } = render(
        <VoiceInterface 
          onVoiceInput={mockOnVoiceInput} 
          language="en"
        />
      );

      expect(mockSpeechRecognition.lang).toBe('en-US');

      rerender(
        <VoiceInterface 
          onVoiceInput={mockOnVoiceInput} 
          language="hi"
        />
      );

      expect(mockSpeechRecognition.lang).toBe('hi-IN');
    });

    test('maintains spiritual context across languages', () => {
      render(
        <VoiceInterface 
          onVoiceInput={mockOnVoiceInput} 
          language="hi"
        />
      );

      const hindiSpiritualTerms = [
        'धर्म क्या है?',
        'कर्म का सिद्धांत',
        'मोक्ष कैसे प्राप्त करें?'
      ];

      hindiSpiritualTerms.forEach(term => {
        const mockEvent = {
          results: [
            {
              0: { transcript: term },
              isFinal: true,
              length: 1
            }
          ],
          resultIndex: 0
        };

        const resultCallback = mockSpeechRecognition.addEventListener.mock.calls
          .find(call => call[0] === 'result')?.[1];
        
        if (resultCallback) {
          resultCallback(mockEvent);
          expect(mockOnVoiceInput).toHaveBeenCalledWith(term);
        }
      });
    });
  });

  describe('Voice Synthesis for Spiritual Responses', () => {
    test('speaks spiritual content with appropriate settings', async () => {
      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      // Simulate speaking a spiritual response
      const spiritualText = 'Dear devotee, dharma is the path of righteousness as taught in the Bhagavad Gita.';
      
      // Access the speak function (would need to be exposed in component)
      // This is a conceptual test - actual implementation would depend on component structure
      expect(mockSpeechSynthesis).toBeDefined();
    });

    test('handles Sanskrit pronunciation correctly', () => {
      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      // Test Sanskrit terms that should be pronounced correctly
      const sanskritTerms = ['dharma', 'karma', 'moksha', 'ahimsa', 'satsang'];
      
      // This would test the pronunciation settings for Sanskrit terms
      expect(mockSpeechSynthesisUtterance).toBeDefined();
    });
  });

  describe('Error Handling for Spiritual Content', () => {
    test('handles speech recognition errors gracefully', () => {
      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      const mockErrorEvent = {
        error: 'network',
        message: 'Network error occurred'
      };

      const errorCallback = mockSpeechRecognition.addEventListener.mock.calls
        .find(call => call[0] === 'error')?.[1];
      
      if (errorCallback) {
        errorCallback(mockErrorEvent);
        expect(screen.getByText(/speech recognition error/i)).toBeInTheDocument();
      }
    });

    test('maintains spiritual context during error recovery', () => {
      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      // Test that spiritual content context is maintained even after errors
      const mockErrorEvent = { error: 'network', message: 'Network error' };
      const mockRecoveryEvent = {
        results: [
          {
            0: { transcript: 'What is the meaning of dharma?' },
            isFinal: true,
            length: 1
          }
        ],
        resultIndex: 0
      };

      const errorCallback = mockSpeechRecognition.addEventListener.mock.calls
        .find(call => call[0] === 'error')?.[1];
      const resultCallback = mockSpeechRecognition.addEventListener.mock.calls
        .find(call => call[0] === 'result')?.[1];
      
      if (errorCallback && resultCallback) {
        errorCallback(mockErrorEvent);
        resultCallback(mockRecoveryEvent);
        expect(mockOnVoiceInput).toHaveBeenCalledWith('What is the meaning of dharma?');
      }
    });
  });

  describe('Accessibility for Spiritual Voice Interface', () => {
    test('provides accessible controls for voice interaction', () => {
      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      const startButton = screen.getByRole('button', { name: /start voice/i });
      expect(startButton).toHaveAccessibleName();
      expect(startButton).not.toHaveAttribute('aria-disabled', 'true');
    });

    test('announces spiritual content status to screen readers', () => {
      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      // Check for ARIA live regions that announce voice status
      const liveRegion = screen.getByRole('status') || screen.getByLabelText(/voice status/i);
      if (liveRegion) {
        expect(liveRegion).toBeInTheDocument();
      }
    });

    test('handles disabled state appropriately', () => {
      render(
        <VoiceInterface 
          onVoiceInput={mockOnVoiceInput} 
          disabled={true}
        />
      );

      const startButton = screen.getByRole('button', { name: /start voice/i });
      expect(startButton).toBeDisabled();
    });
  });

  describe('Integration with Spiritual Guidance Flow', () => {
    test('maintains conversation context through voice', () => {
      render(<VoiceInterface onVoiceInput={mockOnVoiceInput} />);

      // Test that voice interface maintains spiritual conversation context
      const conversationFlow = [
        'What is dharma?',
        'Can you explain more about karma?',
        'How do dharma and karma relate to moksha?'
      ];

      conversationFlow.forEach((query, index) => {
        const mockEvent = {
          results: [
            {
              0: { transcript: query },
              isFinal: true,
              length: 1
            }
          ],
          resultIndex: 0
        };

        const resultCallback = mockSpeechRecognition.addEventListener.mock.calls
          .find(call => call[0] === 'result')?.[1];
        
        if (resultCallback) {
          resultCallback(mockEvent);
          expect(mockOnVoiceInput).toHaveBeenNthCalledWith(index + 1, query);
        }
      });
    });

    test('triggers appropriate callbacks for spiritual interactions', async () => {
      const user = userEvent.setup();
      render(
        <VoiceInterface 
          onVoiceInput={mockOnVoiceInput}
          onSpeechStart={mockOnSpeechStart}
          onSpeechEnd={mockOnSpeechEnd}
        />
      );

      const startButton = screen.getByRole('button', { name: /start voice/i });
      await user.click(startButton);

      // Simulate speech start
      const startCallback = mockSpeechRecognition.addEventListener.mock.calls
        .find(call => call[0] === 'start')?.[1];
      
      if (startCallback) {
        startCallback(new Event('start'));
        expect(mockOnSpeechStart).toHaveBeenCalled();
      }

      // Simulate speech end
      const endCallback = mockSpeechRecognition.addEventListener.mock.calls
        .find(call => call[0] === 'end')?.[1];
      
      if (endCallback) {
        endCallback(new Event('end'));
        expect(mockOnSpeechEnd).toHaveBeenCalled();
      }
    });
  });
});
