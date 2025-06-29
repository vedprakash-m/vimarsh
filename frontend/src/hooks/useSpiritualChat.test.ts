/**
 * Test suite for useSpiritualChat hook
 * 
 * Tests the main chat functionality for spiritual guidance,
 * including message handling, spiritual content validation,
 * and conversation management.
 */

import { renderHook, waitFor } from '@testing-library/react';
import { act } from 'react';
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

// Mock fetch with improved error handling
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
      expect(result.current.messages[0].sender).toBe('user');
      expect(result.current.messages[1].sender).toBe('ai');
      expect(result.current.sessionId).toBe('test-session');
    });

    test('creates new session with Hindi language', () => {
      const { result } = renderHook(() => 
        useSpiritualChat({ language: 'hi' })
      );

      expect(result.current.messages).toHaveLength(1);
      expect(result.current.messages[0].text).toMatch(/नमस्ते/);
    });

    test('initializes with custom API base URL', () => {
      const customUrl = 'https://custom-api.example.com';
      const { result } = renderHook(() => 
        useSpiritualChat({ apiBaseUrl: customUrl })
      );

      expect(result.current.isConnected).toBe(true);
    });
  });

  describe('Message Sending', () => {
    test('sends message successfully', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          id: '3',
          response: 'The purpose of life is to realize your true nature and achieve union with the Divine.',
          citations: [
            {
              source: 'Upanishads',
              reference: 'Isa Upanishad 1',
              verse: 'ईशावास्यमिदं सर्वं यत्किञ्च जगत्यां जगत्'
            }
          ],
          sanskritText: 'आत्मानं विद्धि',
          transliteration: 'ātmānaṃ viddhi',
          confidence: 0.95
        })
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('What is the purpose of life?');
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(3); // Welcome + User + AI
        expect(result.current.messages[1].sender).toBe('user');
        expect(result.current.messages[1].text).toBe('What is the purpose of life?');
        expect(result.current.messages[2].sender).toBe('ai');
        expect(result.current.messages[2].text).toMatch(/purpose of life/);
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    test('handles loading state during message sending', async () => {
      let resolvePromise: ((value: any) => void) | undefined;
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
            response: 'The purpose of life is to realize your true nature and achieve union with the Divine.',
            citations: [],
            confidence: 0.95
          })
        });
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
        expect(result.current.messages[2].isLoading).toBe(false);
      });
    });

    test('ignores empty messages', async () => {
      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('');
      });

      await act(async () => {
        await result.current.sendMessage('   ');
      });

      expect(result.current.messages).toHaveLength(1); // Only welcome message
      expect(global.fetch).not.toHaveBeenCalled();
    });

    test('sends context with message', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          id: '2',
          response: 'Test response',
          citations: []
        })
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('Test message');
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/spiritual_guidance'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: expect.stringContaining('Test message')
        })
      );
    });
  });

  describe('Error Handling', () => {
    test('handles API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Bad request' })
      });

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('What is the meaning of life?');
      });

      await waitFor(() => {
        expect(result.current.error).toBeTruthy();
        expect(result.current.isLoading).toBe(false);
      });
    });

    test('handles network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('Test message');
      });

      await waitFor(() => {
        expect(result.current.error).toBeTruthy();
        expect(result.current.isLoading).toBe(false);
      });
    });

    test('retries failed requests', async () => {
      // First call fails
      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: '2',
            response: 'Success after retry',
            citations: []
          })
        });

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('Test message');
      });

      // Wait for retry to complete
      await waitFor(() => {
        expect(result.current.messages[2].text).toBe('Success after retry');
      }, { timeout: 5000 });

      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    test('handles request cancellation', async () => {
      let rejectPromise: ((reason: any) => void) | undefined;
      const promise = new Promise((_, reject) => {
        rejectPromise = reject;
      });

      (global.fetch as jest.Mock).mockReturnValueOnce(promise);

      const { result } = renderHook(() => useSpiritualChat());

      act(() => {
        result.current.sendMessage('Test message');
      });

      expect(result.current.isLoading).toBe(true);

      // Cancel the request
      act(() => {
        result.current.cancelCurrentRequest();
      });

      await act(async () => {
        const abortError = new Error('Request cancelled');
        abortError.name = 'AbortError';
        rejectPromise!(abortError);
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
        expect(result.current.messages).toHaveLength(2); // Welcome + User (AI message removed)
      });
    });

    test('clears error after timeout', async () => {
      jest.useFakeTimers();

      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Test error'));

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('Test message');
      });

      expect(result.current.error).toBeTruthy();

      act(() => {
        jest.advanceTimersByTime(5000);
      });

      await waitFor(() => {
        expect(result.current.error).toBeNull();
      });

      jest.useRealTimers();
    });
  });

  describe('Chat Management', () => {
    test('clears chat messages', () => {
      const { result } = renderHook(() => useSpiritualChat());

      act(() => {
        result.current.clearChat();
      });

      expect(result.current.messages).toHaveLength(1); // Only welcome message
      expect(result.current.error).toBeNull();
    });

    test('starts new session', () => {
      const { result } = renderHook(() => useSpiritualChat());
      const originalSessionId = result.current.sessionId;

      act(() => {
        result.current.startNewSession();
      });

      expect(result.current.sessionId).not.toBe(originalSessionId);
      expect(result.current.messages).toHaveLength(1); // Only welcome message
      expect(result.current.error).toBeNull();
    });

    test('exports conversation', () => {
      const { result } = renderHook(() => useSpiritualChat());

      const exportData = result.current.exportConversation();

      expect(exportData).toBeDefined();
      expect(exportData.sessionId).toBe(result.current.sessionId);
      expect(exportData.messages).toEqual(result.current.messages);
      expect(exportData.timestamp).toBeInstanceOf(Date);
    });
  });

  describe('Spiritual Content Validation', () => {
    test('validates spiritual content in responses', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          id: '2',
          response: 'According to the Bhagavad Gita, one should perform their duty without attachment to results.',
          citations: [
            {
              source: 'Bhagavad Gita',
              reference: '2.47',
              verse: 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन'
            }
          ],
          sanskritText: 'कर्मण्येवाधिकारस्ते',
          confidence: 0.92
        })
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('What does the Gita say about duty?');
      });

      await waitFor(() => {
        const aiMessage = result.current.messages[2];
        expect(aiMessage.citations).toHaveLength(1);
        expect(aiMessage.citations![0].source).toBe('Bhagavad Gita');
        expect(aiMessage.sanskritText).toBeTruthy();
        expect(aiMessage.confidence).toBeGreaterThan(0.8);
      });
    });

    test('handles responses without Sanskrit text', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          id: '2',
          response: 'Meditation is a practice of focusing the mind.',
          citations: [],
          confidence: 0.85
        })
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useSpiritualChat());

      await act(async () => {
        await result.current.sendMessage('What is meditation?');
      });

      await waitFor(() => {
        const aiMessage = result.current.messages[2];
        expect(aiMessage.text).toMatch(/meditation/i);
        expect(aiMessage.sanskritText).toBeUndefined();
        expect(aiMessage.citations).toEqual([]);
      });
    });
  });

  describe('Language Support', () => {
    test('sends messages in Hindi', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          id: '2',
          response: 'धर्म का अर्थ है सही रास्ते पर चलना।',
          citations: [],
          confidence: 0.88
        })
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useSpiritualChat({ language: 'hi' }));

      await act(async () => {
        await result.current.sendMessage('धर्म क्या है?');
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: expect.stringContaining('"language":"hi"')
        })
      );
    });

    test('shows error messages in Hindi', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useSpiritualChat({ language: 'hi' }));

      await act(async () => {
        await result.current.sendMessage('Test message');
      });

      await waitFor(() => {
        expect(result.current.error?.message).toMatch(/व्यवधान/);
      });
    });
  });

  describe('Configuration', () => {
    test('uses custom API base URL', async () => {
      const customUrl = 'https://custom-api.example.com';
      const mockResponse = {
        ok: true,
        json: async () => ({ id: '2', response: 'Test response', citations: [] })
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => 
        useSpiritualChat({ apiBaseUrl: customUrl })
      );

      await act(async () => {
        await result.current.sendMessage('Test message');
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining(customUrl),
        expect.any(Object)
      );
    });

    test('respects custom retry configuration', async () => {
      const maxRetries = 2;
      
      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Error 1'))
        .mockRejectedValueOnce(new Error('Error 2'))
        .mockRejectedValueOnce(new Error('Error 3'));

      const { result } = renderHook(() => 
        useSpiritualChat({ maxRetries })
      );

      await act(async () => {
        await result.current.sendMessage('Test message');
      });

      // Should try initial + 2 retries = 3 total calls
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(3);
      }, { timeout: 5000 });
    });

    test('disables auto-save when configured', () => {
      const { result } = renderHook(() => 
        useSpiritualChat({ autoSave: false })
      );

      expect(result.current.sessionId).toBeTruthy();
      // Auto-save disabled, so session shouldn't be created in history
    });
  });

  describe('Performance', () => {
    test('handles rapid message sending', async () => {
      const responses = Array.from({ length: 5 }, (_, i) => ({
        ok: true,
        json: async () => ({
          id: `${i + 2}`,
          response: `Response ${i + 1}`,
          citations: []
        })
      }));

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce(responses[0])
        .mockResolvedValueOnce(responses[1])
        .mockResolvedValueOnce(responses[2])
        .mockResolvedValueOnce(responses[3])
        .mockResolvedValueOnce(responses[4]);

      const { result } = renderHook(() => useSpiritualChat());

      // Send multiple messages rapidly
      await act(async () => {
        await Promise.all([
          result.current.sendMessage('Message 1'),
          result.current.sendMessage('Message 2'),
          result.current.sendMessage('Message 3'),
          result.current.sendMessage('Message 4'),
          result.current.sendMessage('Message 5')
        ]);
      });

      await waitFor(() => {
        expect(result.current.messages.length).toBeGreaterThan(5);
      });
    });
  });
});
