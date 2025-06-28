/**
 * Test suite for useSpiritualChat hook
 * 
 * Tests the main chat     }),
    getSessions: jest.fn(() => []),
    setCurrentSession: jest.fn(),
    updateSessionMessages: jest.fn(),
    saveSession: jest.fn(),ty for spiritual guidance,
 * including message handling, spiritual content validation,
 * and conversation management.
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useSpiritualChat } from './useSpiritualChat';

// Mock the conversation history utility
jest.mock('../utils/conversationHistory', () => ({
  conversationHistory: {
    saveSession: jest.fn(),
    getSession: jest.fn((sessionId) => {
      if (sessionId === 'existing-session') {
        return {
          id: 'test-session',
          messages: [
            {
              id: '1',
              text: 'What is dharma?',
              sender: 'user',
              timestamp: new Date('2024-01-15T10:30:00Z')
            },
            {
              id: '2',
              text: 'Dear devotee, dharma refers to righteous living according to cosmic law.',
              sender: 'ai',
              timestamp: new Date('2024-01-15T10:30:30Z'),
              citations: [
                {
                  source: 'Bhagavad Gita',
                  reference: '2.47',
                  verse: 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन'
                }
              ]
            }
          ],
          title: 'Understanding Dharma',
          timestamp: new Date('2024-01-15T10:30:00Z')
        };
      }
      return null;
    }),
    loadSession: jest.fn(() => ({
      id: 'test-session',
      messages: [
        {
          id: '1',
          text: 'What is dharma?',
          sender: 'user',
          timestamp: new Date('2024-01-15T10:30:00Z')
        },
        {
          id: '2',
          text: 'Dear devotee, dharma refers to righteous living according to cosmic law.',
          sender: 'ai',
          timestamp: new Date('2024-01-15T10:30:30Z'),
          citations: [
            {
              source: 'Bhagavad Gita',
              reference: '2.47',
              verse: 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन'
            }
          ]
        }
      ],
      title: 'Understanding Dharma',
      timestamp: new Date('2024-01-15T10:30:00Z')
    })),
    getSessions: jest.fn(() => []),
    setCurrentSession: jest.fn(),
    updateSessionMessages: jest.fn(),
    createSession: jest.fn(() => ({
      id: 'new-session-id',
      title: 'New Session',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      language: 'en',
      metadata: {
        messageCount: 0,
        lastActivity: new Date(),
        topics: [],
        duration: 0
      }
    }))
  }
}));

// Mock fetch
global.fetch = jest.fn();

describe('useSpiritualChat', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  describe('Initialization', () => {
    test('initializes with welcome message', () => {
      const { result } = renderHook(() => useSpiritualChat());

      expect(result.current.messages).toHaveLength(1);
      expect(result.current.messages[0].sender).toBe('ai');
      expect(result.current.messages[0].text).toMatch(/Namaste/);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.sessionId).toBeTruthy();
      expect(result.current.isConnected).toBe(true);
    });

    test('loads existing session when provided', () => {
      const { result } = renderHook(() => 
        useSpiritualChat({ sessionId: 'existing-session' })
      );

      expect(result.current.messages).toHaveLength(2);
      expect(result.current.messages[0].text).toBe('What is dharma?');
      expect(result.current.messages[1].text).toMatch(/Dear devotee, dharma refers/);
    });

    test('initializes with custom configuration', () => {
      const config = {
        language: 'hi' as const,
        apiBaseUrl: 'https://custom-api.com',
        maxRetries: 5
      };

      const { result } = renderHook(() => useSpiritualChat(config));

      expect(result.current.sessionId).toBeTruthy();
      expect(result.current.isConnected).toBe(true);
    });
  });

  describe('Sending Spiritual Messages', () => {
    test('sends spiritual question and receives response', async () => {
      const mockResponse = {
        id: '3',
        text: 'Dear seeker, karma is the law of cause and effect that governs all actions.',
        sender: 'ai',
        timestamp: new Date(),
        citations: [
          {
            source: 'Bhagavad Gita',
            reference: '4.17',
            verse: 'गहना कर्मणो गतिः'
          }
        ],
        confidence: 0.95
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('What is karma?');
      });

      expect(result.current.messages).toHaveLength(2);
      expect(result.current.messages[0].text).toBe('What is karma?');
      expect(result.current.messages[0].sender).toBe('user');
      expect(result.current.messages[1].text).toMatch(/Dear seeker, karma is the law/);
      expect(result.current.messages[1].sender).toBe('ai');
    });

    test('handles Sanskrit terminology in questions', async () => {
      const mockResponse = {
        id: '3',
        text: 'The concept of moksha represents ultimate liberation from the cycle of samsara.',
        sender: 'ai',
        timestamp: new Date(),
        sanskritText: 'मोक्ष',
        transliteration: 'mokṣa'
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('Please explain moksha');
      });

      expect(result.current.messages[1].sanskritText).toBe('मोक्ष');
      expect(result.current.messages[1].transliteration).toBe('mokṣa');
    });

    test('preserves spiritual citations in responses', async () => {
      const mockResponse = {
        id: '3',
        text: 'As I taught in the Bhagavad Gita, one must perform their duty without attachment.',
        sender: 'ai',
        timestamp: new Date(),
        citations: [
          {
            source: 'Bhagavad Gita',
            reference: '2.47',
            verse: 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन',
            chapter: '2',
            book: 'Bhagavad Gita'
          }
        ]
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('What did Krishna teach about duty?');
      });

      const response = result.current.messages[1];
      expect(response.citations).toHaveLength(1);
      expect(response.citations![0].source).toBe('Bhagavad Gita');
      expect(response.citations![0].verse).toBe('कर्मण्येवाधिकारस्ते मा फलेषु कदाचन');
    });

    test('shows loading state during spiritual guidance generation', async () => {
      let resolvePromise: (value: any) => void;
      const promise = new Promise((resolve) => {
        resolvePromise = resolve;
      });

      (global.fetch as jest.Mock).mockReturnValueOnce(promise);

      const { result } = renderHook(() => useSpiritualChat());

      act(() => {
        result.current.sendMessage('What is the purpose of life?');
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.messages[1].isLoading).toBe(true);

      await act(async () => {
        resolvePromise!({
          ok: true,
          json: async () => ({
            id: '3',
            text: 'The purpose of life is to realize your true nature and achieve union with the Divine.',
            sender: 'ai',
            timestamp: new Date()
          })
        });
        await promise;
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Hindi Language Support', () => {
    test('handles Hindi spiritual questions', async () => {
      const mockResponse = {
        id: '3',
        text: 'प्रिय भक्त, धर्म का अर्थ है धारण करने योग्य गुण और कर्तव्य।',
        sender: 'ai',
        timestamp: new Date(),
        citations: [
          {
            source: 'श्रीमद्भगवद्गीता',
            reference: '२.४७'
          }
        ]
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const { result } = renderHook(() => 
        useSpiritualChat({ language: 'hi' })
      );

      await act(async () => {
        await result.current.sendMessage('धर्म क्या है?');
      });

      expect(result.current.messages[1].text).toMatch(/प्रिय भक्त/);
      expect(result.current.messages[1].citations![0].source).toBe('श्रीमद्भगवद्गीता');
    });

    test('preserves Devanagari script in conversations', async () => {
      const mockResponse = {
        id: '3',
        text: 'ॐ शांति शांति शांतिः',
        sender: 'ai',
        timestamp: new Date(),
        sanskritText: 'ॐ शान्तिः शान्तिः शान्तिः',
        transliteration: 'Oṃ śāntiḥ śāntiḥ śāntiḥ'
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const { result } = renderHook(() => 
        useSpiritualChat({ language: 'hi' })
      );

      await act(async () => {
        await result.current.sendMessage('मंत्र का अर्थ बताइए');
      });

      expect(result.current.messages[1].text).toBe('ॐ शांति शांति शांतिः');
      expect(result.current.messages[1].sanskritText).toBe('ॐ शान्तिः शान्तिः शान्तिः');
    });
  });

  describe('Error Handling', () => {
    test('handles API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Internal server error' })
      });

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('What is the meaning of life?');
      });

      expect(result.current.error).toBeTruthy();
      expect(result.current.error!.message).toMatch(/failed to get spiritual guidance/i);
      expect(result.current.isLoading).toBe(false);
    });

    test('retries failed requests for spiritual guidance', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: false,
          status: 500
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: '3',
            text: 'After contemplation, the divine wisdom emerges.',
            sender: 'ai',
            timestamp: new Date()
          })
        });

      const { result } = renderHook(() => 
        useSpiritualChat({ maxRetries: 2 })
      );

      await act(async () => {
        await result.current.sendMessage('Please guide me');
      });

      expect(global.fetch).toHaveBeenCalledTimes(2);
      expect(result.current.error).toBeNull();
      expect(result.current.messages[1].text).toMatch(/divine wisdom emerges/);
    });

    test('handles network errors with spiritual context', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('Guide me, Krishna');
      });

      expect(result.current.error).toBeTruthy();
      expect(result.current.error!.message).toMatch(/unable to connect/i);
    });
  });

  describe('Session Management', () => {
    test('creates new conversation session', async () => {
      const { conversationHistory } = require('../utils/conversationHistory');
      
      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.newConversation();
      });

      expect(conversationHistory.createSession).toHaveBeenCalled();
      expect(result.current.messages).toEqual([]);
    });

    test('loads existing conversation session', async () => {
      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.loadSession('existing-session');
      });

      expect(result.current.messages).toHaveLength(2);
      expect(result.current.sessionId).toBe('test-session');
    });

    test('auto-saves conversation with spiritual content', async () => {
      const { conversationHistory } = require('../utils/conversationHistory');
      
      const mockResponse = {
        id: '3',
        text: 'Spiritual wisdom flows when the mind is still.',
        sender: 'ai',
        timestamp: new Date()
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const { result } = renderHook(() => 
        useSpiritualChat({ autoSave: true })
      );

      await act(async () => {
        await result.current.sendMessage('How to find peace?');
      });

      expect(conversationHistory.saveSession).toHaveBeenCalled();
    });
  });

  describe('Spiritual Content Validation', () => {
    test('maintains spiritual authenticity in responses', async () => {
      const mockResponse = {
        id: '3',
        text: 'Dear devotee, the path of bhakti leads to divine realization.',
        sender: 'ai',
        timestamp: new Date(),
        confidence: 0.98,
        metadata: {
          spiritualAuthenticity: 0.95,
          culturalSensitivity: 0.92
        }
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('What is bhakti?');
      });

      const response = result.current.messages[1];
      expect(response.text).toMatch(/Dear devotee/);
      expect(response.confidence).toBeGreaterThan(0.9);
    });

    test('preserves Krishna persona in responses', async () => {
      const mockResponse = {
        id: '3',
        text: 'As I taught Arjuna, surrender all actions to Me and I shall liberate you.',
        sender: 'ai',
        timestamp: new Date(),
        persona: 'krishna'
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('How to surrender to you, Krishna?');
      });

      expect(result.current.messages[1].text).toMatch(/As I taught Arjuna/);
    });
  });

  describe('Connection Management', () => {
    test('tracks connection status', async () => {
      const { result } = renderHook(() => useSpiritualChat());

      expect(result.current.isConnected).toBe(true);

      // Simulate connection loss
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      await act(async () => {
        await result.current.sendMessage('Test connection');
      });

      expect(result.current.isConnected).toBe(false);
    });

    test('reconnects automatically for spiritual guidance', async () => {
      const { result } = renderHook(() => useSpiritualChat());

      // Simulate initial failure then success
      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: '3',
            text: 'Connection restored. Divine grace flows again.',
            sender: 'ai',
            timestamp: new Date()
          })
        });

      await act(async () => {
        await result.current.sendMessage('Are you there, Krishna?');
      });

      expect(result.current.isConnected).toBe(true);
      expect(result.current.messages[1].text).toMatch(/Connection restored/);
    });
  });
});
