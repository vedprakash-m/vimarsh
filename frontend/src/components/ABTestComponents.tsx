/**
 * A/B Testing React Components for Vimarsh
 * 
 * Provides React components that render different variants based on A/B test assignments
 * while maintaining spiritual authenticity and user experience standards.
 */

import React from 'react';
import { useABTest, SpiritualMetrics } from '../utils/abTesting';

// Response Display Variants
interface ResponseDisplayProps {
  response: string;
  citations: Array<{
    text: string;
    source: string;
    reference: string;
  }>;
  onCitationClick: (citation: string) => void;
}

export const ABTestResponseDisplay: React.FC<ResponseDisplayProps> = ({
  response,
  citations,
  onCitationClick
}) => {
  const { variant, config, trackMetric } = useABTest('response-display-format');

  React.useEffect(() => {
    // Track response display
    trackMetric(SpiritualMetrics.RESPONSE_ENGAGEMENT, 1);
  }, [trackMetric]);

  const handleCitationClick = (citation: string) => {
    trackMetric(SpiritualMetrics.CITATION_CLICKS, 1);
    onCitationClick(citation);
  };

  if (!variant) {
    // Fallback to default format
    return <DefaultResponseDisplay {...{ response, citations, onCitationClick }} />;
  }

  switch (variant.id) {
    case 'classic-format':
      return (
        <div className="response-container classic-format">
          <div className="krishna-response">
            <div className={`krishna-icon ${config.krishnaIconPosition}`}>
              🎭
            </div>
            <div className="response-text">
              <p className="divine-response">{response}</p>
            </div>
          </div>
          
          <div className={`citations-section ${config.citationStyle}`}>
            <h4 className="citations-header">📖 Sacred Sources:</h4>
            <div className="citations-list">
              {citations.map((citation, index) => (
                <button
                  key={index}
                  className="citation-link classic"
                  onClick={() => handleCitationClick(citation.reference)}
                >
                  {citation.source} {citation.reference}
                </button>
              ))}
            </div>
          </div>
        </div>
      );

    case 'integrated-format':
      return (
        <div className="response-container integrated-format">
          <div className="krishna-response">
            <div className={`krishna-icon ${config.krishnaIconPosition}`}>
              🎭
            </div>
            <div className="response-text">
              <p className="divine-response">
                {response}
                <span className="inline-citations">
                  {citations.map((citation, index) => (
                    <button
                      key={index}
                      className="citation-link inline"
                      onClick={() => handleCitationClick(citation.reference)}
                      title={citation.text}
                    >
                      [{citation.source}]
                    </button>
                  ))}
                </span>
              </p>
            </div>
          </div>
        </div>
      );

    default:
      return <DefaultResponseDisplay {...{ response, citations, onCitationClick }} />;
  }
};

// Voice Interface Variants
interface VoiceInterfaceProps {
  onVoiceStart: () => void;
  onVoiceStop: () => void;
  isListening: boolean;
  isSupported: boolean;
}

export const ABTestVoiceInterface: React.FC<VoiceInterfaceProps> = ({
  onVoiceStart,
  onVoiceStop,
  isListening,
  isSupported
}) => {
  const { variant, config, trackMetric } = useABTest('voice-interface-onboarding');
  const [showTutorial, setShowTutorial] = React.useState(false);

  React.useEffect(() => {
    if (variant?.id === 'prominent-voice' && config.showVoiceTutorial) {
      const hasSeenTutorial = localStorage.getItem('vimarsh_voice_tutorial_seen');
      if (!hasSeenTutorial) {
        setShowTutorial(true);
      }
    }
  }, [variant, config]);

  const handleVoiceClick = () => {
    trackMetric(SpiritualMetrics.VOICE_USAGE_RATE, 1);
    
    if (isListening) {
      onVoiceStop();
    } else {
      onVoiceStart();
    }
  };

  const closeTutorial = () => {
    setShowTutorial(false);
    localStorage.setItem('vimarsh_voice_tutorial_seen', 'true');
    trackMetric(SpiritualMetrics.FEATURE_DISCOVERY, 'tutorial_completed');
  };

  if (!variant || !isSupported) {
    return (
      <button
        onClick={handleVoiceClick}
        className="voice-button default"
        disabled={!isSupported}
      >
        🎤
      </button>
    );
  }

  const buttonClass = `voice-button ${variant.id} ${config.voiceButtonSize} ${
    config.microphoneIconStyle === 'animated' ? 'animated' : ''
  } ${isListening ? 'listening' : ''}`;

  return (
    <div className="voice-interface-container">
      <button
        onClick={handleVoiceClick}
        className={buttonClass}
        disabled={!isSupported}
        title={isListening ? 'Stop speaking' : 'Speak your question'}
      >
        {config.microphoneIconStyle === 'animated' ? (
          <span className="animated-mic">🎤</span>
        ) : (
          '🎤'
        )}
        {config.voiceButtonSize === 'large' && (
          <span className="voice-label">
            {isListening ? 'Listening...' : 'Speak'}
          </span>
        )}
      </button>

      {showTutorial && variant.id === 'prominent-voice' && (
        <div className="voice-tutorial-overlay">
          <div className="tutorial-content">
            <h3>🎙️ Voice Feature</h3>
            <p>Speak naturally to receive divine wisdom from Lord Krishna</p>
            <div className="tutorial-steps">
              <div className="step">
                <span className="step-number">1</span>
                <span>Click the microphone button</span>
              </div>
              <div className="step">
                <span className="step-number">2</span>
                <span>Ask your spiritual question clearly</span>
              </div>
              <div className="step">
                <span className="step-number">3</span>
                <span>Receive wisdom in text and audio</span>
              </div>
            </div>
            <button onClick={closeTutorial} className="tutorial-close">
              Begin Journey
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Question Suggestion Variants
interface QuestionSuggestionsProps {
  onQuestionSelect: (question: string) => void;
  conversationHistory: Array<{ question: string; category: string }>;
}

export const ABTestQuestionSuggestions: React.FC<QuestionSuggestionsProps> = ({
  onQuestionSelect,
  conversationHistory
}) => {
  const { variant, config, trackMetric } = useABTest('question-suggestion-style');

  const handleQuestionClick = (question: string, category?: string) => {
    trackMetric(SpiritualMetrics.SUGGESTION_CLICKS, 1, {
      questionType: category as any,
      responseQuality: 0,
      userSatisfaction: 0
    });
    onQuestionSelect(question);
  };

  // Predefined spiritual questions by category
  const spiritualQuestions = {
    dharma: [
      "What is my duty in this situation?",
      "How do I know if my actions are righteous?",
      "What is the nature of dharma in modern times?"
    ],
    karma: [
      "How does karma work in daily life?",
      "Can I change my destiny through actions?",
      "What is the relationship between action and result?"
    ],
    moksha: [
      "What is the path to liberation?",
      "How can I find inner peace?",
      "What is the nature of the soul?"
    ],
    bhakti: [
      "How can I develop devotion?",
      "What is true surrender?",
      "How do I connect with the divine?"
    ]
  };

  if (!variant) {
    // Fallback to simple list
    return (
      <div className="question-suggestions default">
        <h4>💭 Ask Lord Krishna:</h4>
        <div className="suggestion-list">
          {spiritualQuestions.dharma.slice(0, 3).map((question, index) => (
            <button
              key={index}
              onClick={() => handleQuestionClick(question)}
              className="suggestion-button"
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    );
  }

  switch (variant.id) {
    case 'category-based':
      return (
        <div className="question-suggestions category-based">
          <h4>💭 Seek Divine Wisdom:</h4>
          <div className="categories-container">
            {config.categories.map((category: string) => (
              <div key={category} className="category-section">
                <h5 className="category-title">
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </h5>
                <div className={`suggestions-${config.displayFormat}`}>
                  {spiritualQuestions[category as keyof typeof spiritualQuestions]
                    .slice(0, config.questionCount)
                    .map((question, index) => (
                      <button
                        key={index}
                        onClick={() => handleQuestionClick(question, category)}
                        className="suggestion-button category-style"
                      >
                        {question}
                      </button>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      );

    case 'contextual-flow':
      // Generate contextual suggestions based on conversation history
      const contextualQuestions = generateContextualQuestions(conversationHistory);
      
      return (
        <div className="question-suggestions contextual-flow">
          <h4>💭 Continue Your Journey:</h4>
          <div className={`suggestions-${config.displayFormat}`}>
            {contextualQuestions.slice(0, config.questionCount).map((question, index) => (
              <button
                key={index}
                onClick={() => handleQuestionClick(question.text as string, question.category)}
                className="suggestion-button contextual-style"
              >
                {question.text as string}
              </button>
            ))}
          </div>
        </div>
      );

    default:
      return null;
  }
};

// Helper function to generate contextual questions
function generateContextualQuestions(history: Array<{ question: string; category: string }>) {
  // Predefined spiritual questions for contextual suggestions
  const spiritualQuestions = {
    dharma: [
      "What is my duty in this situation?",
      "How do I know if my actions are righteous?",
      "What is the nature of dharma in modern times?"
    ],
    karma: [
      "How does karma work in daily life?",
      "Can I change my destiny through actions?",
      "What is the relationship between action and result?"
    ],
    moksha: [
      "What is the path to liberation?",
      "How can I find inner peace?",
      "What is the nature of the soul?"
    ],
    bhakti: [
      "How can I develop devotion?",
      "What is true surrender?",
      "How do I connect with the divine?"
    ]
  };

  const recentCategories = history.slice(-3).map(h => h.category);
  const allQuestions = Object.values(spiritualQuestions).flat();
  
  // Filter questions that relate to recent conversation themes
  const contextual = allQuestions.map(question => ({
    text: question,
    category: 'general' as const
  }));

  return contextual;
}

// Default components for fallback
const DefaultResponseDisplay: React.FC<ResponseDisplayProps> = ({
  response,
  citations,
  onCitationClick
}) => (
  <div className="response-container default">
    <div className="krishna-response">
      <div className="krishna-icon">🎭</div>
      <p className="divine-response">{response}</p>
    </div>
    <div className="citations-section">
      <h4>📖 Sources:</h4>
      {citations.map((citation, index) => (
        <button
          key={index}
          onClick={() => onCitationClick(citation.reference)}
          className="citation-link"
        >
          {citation.source} {citation.reference}
        </button>
      ))}
    </div>
  </div>
);

// A/B Testing Debug Panel (development only)
export const ABTestDebugPanel: React.FC = () => {
  const [isVisible, setIsVisible] = React.useState(false);

  // Only show in development
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <>
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="ab-debug-toggle"
        style={{
          position: 'fixed',
          bottom: '10px',
          right: '10px',
          zIndex: 9999,
          background: '#007bff',
          color: 'white',
          border: 'none',
          padding: '8px',
          borderRadius: '4px',
          fontSize: '12px'
        }}
      >
        A/B Debug
      </button>

      {isVisible && (
        <div
          className="ab-debug-panel"
          style={{
            position: 'fixed',
            bottom: '50px',
            right: '10px',
            width: '300px',
            background: 'white',
            border: '1px solid #ccc',
            borderRadius: '8px',
            padding: '16px',
            zIndex: 9999,
            fontSize: '12px',
            maxHeight: '400px',
            overflow: 'auto'
          }}
        >
          <h4>A/B Test Status</h4>
          <ABTestStatus />
        </div>
      )}
    </>
  );
};

const ABTestStatus: React.FC = () => {
  const responseTest = useABTest('response-display-format');
  const voiceTest = useABTest('voice-interface-onboarding');
  const questionTest = useABTest('question-suggestion-style');

  return (
    <div>
      <div style={{ marginBottom: '12px' }}>
        <strong>Response Display:</strong>
        <div>Variant: {responseTest.variant?.name || 'Default'}</div>
        <div>Participating: {responseTest.isParticipating ? 'Yes' : 'No'}</div>
      </div>
      
      <div style={{ marginBottom: '12px' }}>
        <strong>Voice Interface:</strong>
        <div>Variant: {voiceTest.variant?.name || 'Default'}</div>
        <div>Participating: {voiceTest.isParticipating ? 'Yes' : 'No'}</div>
      </div>
      
      <div style={{ marginBottom: '12px' }}>
        <strong>Question Suggestions:</strong>
        <div>Variant: {questionTest.variant?.name || 'Default'}</div>
        <div>Participating: {questionTest.isParticipating ? 'Yes' : 'No'}</div>
      </div>
    </div>
  );
};
