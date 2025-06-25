/**
 * Integration Tests for A/B Testing Components
 * 
 * Tests the React components that use A/B testing variants,
 * ensuring proper rendering and user interaction tracking.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import {
  ABTestResponseDisplay,
  ABTestVoiceInterface,
  ABTestQuestionSuggestions,
  ABTestDebugPanel
} from '../components/ABTestComponents';
import { abTesting } from '../utils/abTesting';

// Mock the A/B testing framework
jest.mock('../utils/abTesting', () => {
  const originalModule = jest.requireActual('../utils/abTesting');
  
  return {
    ...originalModule,
    abTesting: {
      getVariant: jest.fn(),
      getTestConfig: jest.fn(),
      trackMetric: jest.fn(),
      isParticipating: jest.fn(),
      forceVariant: jest.fn(),
      getActiveAssignments: jest.fn()
    }
  };
});

// Mock CSS imports
jest.mock('../styles/ab-testing.css', () => ({}));

const mockAbTesting = abTesting as jest.Mocked<typeof abTesting>;

describe('A/B Testing Components', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default mock implementations
    mockAbTesting.isParticipating.mockReturnValue(true);
    mockAbTesting.trackMetric.mockImplementation(() => {});
  });

  describe('ABTestResponseDisplay', () => {
    const mockCitations = [
      {
        text: "As stated in the Gita",
        source: "Bhagavad Gita",
        reference: "2.47"
      },
      {
        text: "Krishna explains",
        source: "Mahabharata",
        reference: "6.23"
      }
    ];

    const mockProps = {
      response: "Your duty is to act without attachment to results, dear Arjuna.",
      citations: mockCitations,
      onCitationClick: jest.fn()
    };

    test('should render classic format variant', () => {
      mockAbTesting.getVariant.mockReturnValue({
        id: 'classic-format',
        name: 'Classic Citation Format',
        description: 'Traditional format',
        weight: 50,
        config: {
          citationPosition: 'bottom',
          responseStyle: 'classic',
          krishnaIconPosition: 'left',
          citationStyle: 'compact'
        },
        spirituallyValidated: true
      });

      mockAbTesting.getTestConfig.mockReturnValue({
        citationPosition: 'bottom',
        responseStyle: 'classic',
        krishnaIconPosition: 'left',
        citationStyle: 'compact'
      });

      render(<ABTestResponseDisplay {...mockProps} />);

      // Should show Krishna icon
      expect(screen.getByText('🎭')).toBeInTheDocument();

      // Should show response text
      expect(screen.getByText(/Your duty is to act without attachment/)).toBeInTheDocument();

      // Should show citations section
      expect(screen.getByText('📖 Sacred Sources:')).toBeInTheDocument();

      // Should show citation buttons
      expect(screen.getByText(/Bhagavad Gita 2\.47/)).toBeInTheDocument();
      expect(screen.getByText(/Mahabharata 6\.23/)).toBeInTheDocument();

      // Should have classic format styling
      expect(screen.getByText(/Your duty is to act without attachment/).closest('.response-container'))
        .toHaveClass('classic-format');
    });

    test('should render integrated format variant', () => {
      mockAbTesting.getVariant.mockReturnValue({
        id: 'integrated-format',
        name: 'Integrated Citation Format',
        description: 'Integrated format',
        weight: 50,
        config: {
          citationPosition: 'inline',
          responseStyle: 'modern',
          krishnaIconPosition: 'center',
          citationStyle: 'expanded'
        },
        spirituallyValidated: true
      });

      mockAbTesting.getTestConfig.mockReturnValue({
        citationPosition: 'inline',
        responseStyle: 'modern',
        krishnaIconPosition: 'center',
        citationStyle: 'expanded'
      });

      render(<ABTestResponseDisplay {...mockProps} />);

      // Should show inline citations
      expect(screen.getByText('[Bhagavad Gita]')).toBeInTheDocument();
      expect(screen.getByText('[Mahabharata]')).toBeInTheDocument();

      // Should have integrated format styling
      expect(screen.getByText(/Your duty is to act without attachment/).closest('.response-container'))
        .toHaveClass('integrated-format');
    });

    test('should track citation clicks', async () => {
      const user = userEvent.setup();
      mockAbTesting.getVariant.mockReturnValue({
        id: 'classic-format',
        name: 'Classic Citation Format',
        description: 'Traditional format',
        weight: 50,
        config: {},
        spirituallyValidated: true
      });

      render(<ABTestResponseDisplay {...mockProps} />);

      const citationButton = screen.getByText(/Bhagavad Gita 2\.47/);
      await user.click(citationButton);

      // Should track citation click
      expect(mockAbTesting.trackMetric).toHaveBeenCalledWith('citation_clicks', 1);

      // Should call onCitationClick prop
      expect(mockProps.onCitationClick).toHaveBeenCalledWith('2.47');
    });

    test('should fallback to default when no variant', () => {
      mockAbTesting.getVariant.mockReturnValue(null);

      render(<ABTestResponseDisplay {...mockProps} />);

      // Should still render response and citations
      expect(screen.getByText(/Your duty is to act without attachment/)).toBeInTheDocument();
      expect(screen.getByText('📖 Sources:')).toBeInTheDocument();
    });
  });

  describe('ABTestVoiceInterface', () => {
    const mockProps = {
      onVoiceStart: jest.fn(),
      onVoiceStop: jest.fn(),
      isListening: false,
      isSupported: true
    };

    test('should render prominent voice variant with tutorial', async () => {
      const user = userEvent.setup();
      
      mockAbTesting.getVariant.mockReturnValue({
        id: 'prominent-voice',
        name: 'Prominent Voice CTA',
        description: 'Prominent voice',
        weight: 50,
        config: {
          voiceButtonSize: 'large',
          showVoiceTutorial: true,
          microphoneIconStyle: 'animated'
        },
        spirituallyValidated: true
      });

      mockAbTesting.getTestConfig.mockReturnValue({
        voiceButtonSize: 'large',
        showVoiceTutorial: true,
        microphoneIconStyle: 'animated'
      });

      // Clear tutorial seen flag
      localStorage.removeItem('vimarsh_voice_tutorial_seen');

      render(<ABTestVoiceInterface {...mockProps} />);

      // Should show tutorial overlay
      expect(screen.getByText('🎙️ Voice Feature')).toBeInTheDocument();
      expect(screen.getByText('Speak naturally to receive divine wisdom')).toBeInTheDocument();

      // Should show tutorial steps
      expect(screen.getByText('Click the microphone button')).toBeInTheDocument();
      expect(screen.getByText('Ask your spiritual question clearly')).toBeInTheDocument();

      // Close tutorial
      const closeButton = screen.getByText('Begin Journey');
      await user.click(closeButton);

      // Tutorial should be hidden
      expect(screen.queryByText('🎙️ Voice Feature')).not.toBeInTheDocument();

      // Should mark tutorial as seen
      expect(localStorage.getItem('vimarsh_voice_tutorial_seen')).toBe('true');
    });

    test('should render subtle voice variant', () => {
      mockAbTesting.getVariant.mockReturnValue({
        id: 'subtle-voice',
        name: 'Subtle Voice Integration',
        description: 'Subtle voice',
        weight: 50,
        config: {
          voiceButtonSize: 'medium',
          showVoiceTutorial: false,
          microphoneIconStyle: 'static'
        },
        spirituallyValidated: true
      });

      mockAbTesting.getTestConfig.mockReturnValue({
        voiceButtonSize: 'medium',
        showVoiceTutorial: false,
        microphoneIconStyle: 'static'
      });

      render(<ABTestVoiceInterface {...mockProps} />);

      // Should not show tutorial
      expect(screen.queryByText('🎙️ Voice Feature')).not.toBeInTheDocument();

      // Should have medium size button
      const voiceButton = screen.getByRole('button');
      expect(voiceButton).toHaveClass('medium');
    });

    test('should track voice usage', async () => {
      const user = userEvent.setup();
      
      mockAbTesting.getVariant.mockReturnValue({
        id: 'prominent-voice',
        name: 'Prominent Voice CTA',
        description: 'Prominent voice',
        weight: 50,
        config: { voiceButtonSize: 'large' },
        spirituallyValidated: true
      });

      render(<ABTestVoiceInterface {...mockProps} />);

      const voiceButton = screen.getByRole('button');
      await user.click(voiceButton);

      // Should track voice usage
      expect(mockAbTesting.trackMetric).toHaveBeenCalledWith('voice_usage_rate', 1);

      // Should call onVoiceStart
      expect(mockProps.onVoiceStart).toHaveBeenCalled();
    });

    test('should handle unsupported voice', () => {
      const unsupportedProps = { ...mockProps, isSupported: false };
      
      mockAbTesting.getVariant.mockReturnValue({
        id: 'prominent-voice',
        name: 'Prominent Voice CTA',
        description: 'Prominent voice',
        weight: 50,
        config: {},
        spirituallyValidated: true
      });

      render(<ABTestVoiceInterface {...unsupportedProps} />);

      const voiceButton = screen.getByRole('button');
      expect(voiceButton).toBeDisabled();
    });
  });

  describe('ABTestQuestionSuggestions', () => {
    const mockProps = {
      onQuestionSelect: jest.fn(),
      conversationHistory: [
        { question: "What is dharma?", category: "dharma" },
        { question: "How does karma work?", category: "karma" }
      ]
    };

    test('should render category-based suggestions', () => {
      mockAbTesting.getVariant.mockReturnValue({
        id: 'category-based',
        name: 'Category-Based Suggestions',
        description: 'Category-based',
        weight: 50,
        config: {
          suggestionStyle: 'categorized',
          categories: ['dharma', 'karma'],
          displayFormat: 'cards',
          questionCount: 2
        },
        spirituallyValidated: true
      });

      mockAbTesting.getTestConfig.mockReturnValue({
        suggestionStyle: 'categorized',
        categories: ['dharma', 'karma'],
        displayFormat: 'cards',
        questionCount: 2
      });

      render(<ABTestQuestionSuggestions {...mockProps} />);

      // Should show category sections
      expect(screen.getByText('Dharma')).toBeInTheDocument();
      expect(screen.getByText('Karma')).toBeInTheDocument();

      // Should show dharma questions
      expect(screen.getByText(/What is my duty in this situation/)).toBeInTheDocument();
      expect(screen.getByText(/How do I know if my actions are righteous/)).toBeInTheDocument();

      // Should show karma questions
      expect(screen.getByText(/How does karma work in daily life/)).toBeInTheDocument();
      expect(screen.getByText(/Can I change my destiny/)).toBeInTheDocument();
    });

    test('should render contextual flow suggestions', () => {
      mockAbTesting.getVariant.mockReturnValue({
        id: 'contextual-flow',
        name: 'Contextual Flow Suggestions',
        description: 'Contextual flow',
        weight: 50,
        config: {
          suggestionStyle: 'contextual',
          displayFormat: 'list',
          questionCount: 3
        },
        spirituallyValidated: true
      });

      mockAbTesting.getTestConfig.mockReturnValue({
        suggestionStyle: 'contextual',
        displayFormat: 'list',
        questionCount: 3
      });

      render(<ABTestQuestionSuggestions {...mockProps} />);

      // Should show contextual header
      expect(screen.getByText('💭 Continue Your Journey:')).toBeInTheDocument();

      // Should have contextual styling
      expect(screen.getByText(/Continue Your Journey/).closest('.question-suggestions'))
        .toHaveClass('contextual-flow');
    });

    test('should track suggestion clicks', async () => {
      const user = userEvent.setup();
      
      mockAbTesting.getVariant.mockReturnValue({
        id: 'category-based',
        name: 'Category-Based Suggestions',
        description: 'Category-based',
        weight: 50,
        config: {
          categories: ['dharma'],
          questionCount: 1
        },
        spirituallyValidated: true
      });

      render(<ABTestQuestionSuggestions {...mockProps} />);

      const suggestionButton = screen.getByText(/What is my duty in this situation/);
      await user.click(suggestionButton);

      // Should track suggestion click
      expect(mockAbTesting.trackMetric).toHaveBeenCalledWith(
        'suggestion_clicks',
        1,
        expect.objectContaining({
          questionType: 'dharma'
        })
      );

      // Should call onQuestionSelect
      expect(mockProps.onQuestionSelect).toHaveBeenCalledWith(
        "What is my duty in this situation?"
      );
    });
  });

  describe('ABTestDebugPanel', () => {
    const originalEnv = process.env.NODE_ENV;

    beforeEach(() => {
      // Mock active assignments
      mockAbTesting.getActiveAssignments.mockReturnValue([]);
    });

    afterEach(() => {
      process.env.NODE_ENV = originalEnv;
    });

    test('should not render in production', () => {
      process.env.NODE_ENV = 'production';

      render(<ABTestDebugPanel />);

      expect(screen.queryByText('A/B Debug')).not.toBeInTheDocument();
    });

    test('should render in development', async () => {
      const user = userEvent.setup();
      process.env.NODE_ENV = 'development';

      render(<ABTestDebugPanel />);

      // Should show debug toggle
      const debugToggle = screen.getByText('A/B Debug');
      expect(debugToggle).toBeInTheDocument();

      // Click to open panel
      await user.click(debugToggle);

      // Should show debug panel
      expect(screen.getByText('A/B Test Status')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    test('should handle missing variants gracefully', () => {
      mockAbTesting.getVariant.mockReturnValue(null);
      mockAbTesting.getTestConfig.mockReturnValue({});

      const mockProps = {
        response: "Test response",
        citations: [],
        onCitationClick: jest.fn()
      };

      // Should not throw error
      expect(() => {
        render(<ABTestResponseDisplay {...mockProps} />);
      }).not.toThrow();

      // Should render fallback
      expect(screen.getByText("Test response")).toBeInTheDocument();
    });

    test('should handle tracking errors gracefully', async () => {
      const user = userEvent.setup();
      
      // Mock tracking to throw error
      mockAbTesting.trackMetric.mockImplementation(() => {
        throw new Error('Tracking failed');
      });

      mockAbTesting.getVariant.mockReturnValue({
        id: 'classic-format',
        name: 'Classic Citation Format',
        description: 'Traditional format',
        weight: 50,
        config: {},
        spirituallyValidated: true
      });

      const mockProps = {
        response: "Test response",
        citations: [{
          text: "Citation",
          source: "Source",
          reference: "1.1"
        }],
        onCitationClick: jest.fn()
      };

      render(<ABTestResponseDisplay {...mockProps} />);

      const citationButton = screen.getByText(/Source 1\.1/);
      
      // Should not crash when tracking fails
      expect(async () => {
        await user.click(citationButton);
      }).not.toThrow();

      // Should still call the click handler
      expect(mockProps.onCitationClick).toHaveBeenCalled();
    });
  });
});
