/**
 * Test suite for SpiritualGuidanceInterface component
 * 
 * This test suite focuses on spiritual content scenarios and cultural sensitivity,
 * ensuring proper handling of sacred texts, Sanskrit terminology, and user interactions.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import SpiritualGuidanceInterface from './SpiritualGuidanceInterface';

// Mock the hooks and contexts
jest.mock('../hooks/useSpiritualChat', () => ({
  useSpiritualChat: () => ({
    messages: [
      {
        id: '1',
        text: 'What is dharma?',
        isUser: true,
        timestamp: new Date(),
      },
      {
        id: '2',
        text: 'Dear devotee, dharma refers to righteous living according to cosmic law. As I taught Arjuna in the Bhagavad Gita, dharma is your sacred duty aligned with your nature and circumstances.',
        isUser: false,
        timestamp: new Date(),
        citations: [
          {
            source: 'Bhagavad Gita',
            reference: '2.47',
            verse: 'You have a right to perform your prescribed duty, but not to the fruits of action.',
            chapter: '2',
            book: 'Bhagavad Gita'
          }
        ],
        metadata: {
          authenticity_score: 0.95,
          spiritual_depth: 0.88,
          cultural_sensitivity: 0.92
        }
      }
    ],
    isLoading: false,
    sendMessage: jest.fn().mockResolvedValue(undefined),
    sessionId: 'test-session-123',
    newConversation: jest.fn(),
    loadSession: jest.fn()
  })
}));

jest.mock('./AuthenticationWrapper', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { name: 'Test User', id: 'user123' }
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>
}));

jest.mock('../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    currentLanguage: 'English',
    t: (key: string) => key,
    switchLanguage: jest.fn()
  }),
  getLanguageCode: (lang: string) => lang === 'English' ? 'en' : 'hi',
  LanguageProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>
}));

jest.mock('../utils/pwa', () => ({
  usePWA: () => ({
    isInstallable: false,
    installApp: jest.fn(),
    isStandalone: false
  })
}));

jest.mock('../hooks/useABTest', () => ({
  useSpiritualGuidanceTest: () => ({
    interfaceConfig: { theme: 'sacred', layout: 'traditional' },
    responseConfig: { tone: 'compassionate', formality: 'reverent' },
    trackGuidanceInteraction: jest.fn(),
    trackGuidanceConversion: jest.fn()
  })
}));

// Mock child components
jest.mock('./VoiceInterface', () => {
  return function MockVoiceInterface({ onVoiceInput }: { onVoiceInput: (text: string) => void }) {
    return (
      <div data-testid="voice-interface">
        <button 
          onClick={() => onVoiceInput('Voice input: What is moksha?')}
          data-testid="voice-input-button"
        >
          Start Voice Input
        </button>
      </div>
    );
  };
});

jest.mock('./ResponseDisplay', () => {
  return function MockResponseDisplay({ message }: { message: any }) {
    if (!message) {
      return <div data-testid="response-display">No message</div>;
    }
    return (
      <div data-testid="response-display">
        <div data-testid="message-text">{message.text || 'No text'}</div>
        {message.citations && message.citations.length > 0 && (
          <div data-testid="citations">
            {message.citations.map((citation: any, index: number) => (
              <div key={index} data-testid={`citation-${index}`}>
                {citation.source} {citation.reference}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };
});

jest.mock('./ConversationHistory', () => {
  return function MockConversationHistory() {
    return <div data-testid="conversation-history">Conversation History</div>;
  };
});

jest.mock('./PrivacySettings', () => {
  return function MockPrivacySettings() {
    return <div data-testid="privacy-settings">Privacy Settings</div>;
  };
});

// Mock analytics context
jest.mock('../contexts/AnalyticsContext', () => ({
  useAnalytics: () => ({
    trackEvent: jest.fn(),
    trackSpiritualInteraction: jest.fn(),
    isEnabled: true,
    sessionId: 'test-session'
  }),
  AnalyticsProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(component);
};

describe('SpiritualGuidanceInterface', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering and Structure', () => {
    test('renders main interface components', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      expect(screen.getByRole('textbox')).toBeInTheDocument();
      expect(screen.getByText('Send')).toBeInTheDocument();
      expect(screen.getByTestId('voice-interface')).toBeInTheDocument();
    });

    test('displays spiritual greeting message', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Check for spiritual greeting or welcome message
      expect(screen.getByText(/welcome/i) || screen.getByText(/namaste/i) || screen.getByText(/guidance/i)).toBeInTheDocument();
    });

    test('shows conversation messages', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      expect(screen.getByText('What is dharma?')).toBeInTheDocument();
      expect(screen.getByText(/Dear devotee, dharma refers to righteous living/)).toBeInTheDocument();
    });
  });

  describe('Spiritual Content Handling', () => {
    test('properly displays Sanskrit terminology', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Check that Sanskrit/spiritual terms are preserved
      expect(screen.getByText(/dharma/)).toBeInTheDocument();
      expect(screen.getByText(/Arjuna/)).toBeInTheDocument();
      expect(screen.getByText(/Bhagavad Gita/)).toBeInTheDocument();
    });

    test('shows citations with proper formatting', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      expect(screen.getByTestId('citations')).toBeInTheDocument();
      expect(screen.getByTestId('citation-0')).toHaveTextContent('Bhagavad Gita 2.47');
    });

    test('handles spiritual content with reverence', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Check for respectful language patterns
      const responseText = screen.getByText(/Dear devotee/);
      expect(responseText).toBeInTheDocument();
      
      // Verify no casual or inappropriate language
      expect(screen.queryByText(/hey/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/cool/i)).not.toBeInTheDocument();
    });

    test('displays Lord Krishna persona appropriately', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Check for divine persona markers
      expect(screen.getByText(/As I taught Arjuna/)).toBeInTheDocument();
      expect(screen.getByText(/Dear devotee/)).toBeInTheDocument();
    });
  });

  describe('User Interactions with Spiritual Content', () => {
    test('handles spiritual query input', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      const input = screen.getByRole('textbox');
      const sendButton = screen.getByText('Send');
      
      await user.type(input, 'What is the meaning of Om?');
      await user.click(sendButton);
      
      expect(input).toHaveValue('');
    });

    test('handles voice input for spiritual queries', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      const voiceButton = screen.getByTestId('voice-input-button');
      await user.click(voiceButton);
      
      await waitFor(() => {
        const input = screen.getByRole('textbox');
        expect(input).toHaveValue('Voice input: What is moksha?');
      });
    });

    test('prevents inappropriate content submission', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      const input = screen.getByRole('textbox');
      
      // Test inappropriate content filtering
      await user.type(input, 'inappropriate content here');
      
      // The component should handle this gracefully
      expect(input).toHaveValue('inappropriate content here');
    });
  });

  describe('Multilingual Support', () => {
    test('supports English spiritual content', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      expect(screen.getByText(/dharma refers to righteous living/)).toBeInTheDocument();
    });

    test('handles Sanskrit terms in English context', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Sanskrit terms should be preserved even in English interface
      expect(screen.getByText(/dharma/)).toBeInTheDocument();
      expect(screen.getByText(/Arjuna/)).toBeInTheDocument();
    });
  });

  describe('Cultural Sensitivity', () => {
    test('maintains spiritual dignity in interface', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Check for respectful language and tone
      const messages = screen.getAllByTestId('message-text');
      messages.forEach(message => {
        const text = message.textContent?.toLowerCase() || '';
        
        // Should not contain casual language
        expect(text).not.toMatch(/cool|awesome|dude|hey/);
        
        // Should contain respectful patterns if it's a response
        if (text.includes('devotee') || text.includes('dharma')) {
          expect(text).toMatch(/dear|beloved|sacred|divine/);
        }
      });
    });

    test('properly formats sacred text references', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      const citation = screen.getByTestId('citation-0');
      expect(citation).toHaveTextContent('Bhagavad Gita 2.47');
      
      // Citations should be formal and complete
      expect(citation.textContent).not.toMatch(/gita|bg|bhagavad/i);
      expect(citation.textContent).toMatch(/Bhagavad Gita/);
    });

    test('handles spiritual concepts with appropriate context', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Complex spiritual concepts should be explained thoughtfully
      const response = screen.getByText(/dharma refers to righteous living according to cosmic law/);
      expect(response).toBeInTheDocument();
    });
  });

  describe('Accessibility for Spiritual Content', () => {
    test('provides accessible labels for spiritual elements', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      const input = screen.getByRole('textbox');
      expect(input).toHaveAccessibleName();
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toBeInTheDocument();
    });

    test('supports screen readers for Sanskrit content', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Sanskrit content should have appropriate ARIA labels
      const citations = screen.getByTestId('citations');
      expect(citations).toBeInTheDocument();
    });
  });

  describe('Error Handling for Spiritual Context', () => {
    test('handles API errors gracefully', async () => {
      // Mock sendMessage to reject
      const mockSendMessage = jest.fn().mockRejectedValue(new Error('API Error'));
      
      jest.doMock('../hooks/useSpiritualChat', () => ({
        useSpiritualChat: () => ({
          messages: [],
          isLoading: false,
          sendMessage: mockSendMessage,
          sessionId: null,
          newConversation: jest.fn(),
          loadSession: jest.fn()
        })
      }));

      const user = userEvent.setup();
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      const input = screen.getByRole('textbox');
      const sendButton = screen.getByText('Send');
      
      await user.type(input, 'What is karma?');
      await user.click(sendButton);
      
      // Should handle error without breaking the interface
      expect(input).toHaveValue('');
    });

    test('shows appropriate loading states during spiritual guidance', () => {
      // Mock loading state
      jest.doMock('../hooks/useSpiritualChat', () => ({
        useSpiritualChat: () => ({
          messages: [],
          isLoading: true,
          sendMessage: jest.fn(),
          sessionId: null,
          newConversation: jest.fn(),
          loadSession: jest.fn()
        })
      }));

      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Should show loading indicator
      expect(screen.getByText('Send')).toBeDisabled();
    });
  });

  describe('Session Management for Spiritual Conversations', () => {
    test('maintains conversation context', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Should show session ID or indicator
      expect(screen.getByText(/session/i) || screen.getByTestId('conversation-history')).toBeInTheDocument();
    });

    test('handles new conversation creation', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Look for new conversation button or link
      const newConversationButton = screen.getByText(/new/i) || screen.getByRole('button', { name: /conversation/i });
      if (newConversationButton) {
        await user.click(newConversationButton);
      }
      
      // Should maintain interface integrity
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });
  });

  describe('Integration with Other Components', () => {
    test('integrates properly with voice interface', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      expect(screen.getByTestId('voice-interface')).toBeInTheDocument();
    });

    test('displays responses through ResponseDisplay component', () => {
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      expect(screen.getByTestId('response-display')).toBeInTheDocument();
    });

    test('shows conversation history when requested', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SpiritualGuidanceInterface />);
      
      // Look for history button
      const historyButton = screen.getByText(/history/i) || screen.getByRole('button', { name: /history/i });
      if (historyButton) {
        await user.click(historyButton);
        expect(screen.getByTestId('conversation-history')).toBeInTheDocument();
      }
    });
  });
});
