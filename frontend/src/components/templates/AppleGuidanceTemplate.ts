/**
 * Apple-inspired GuidanceInterface Template
 * This is a template showing the key design patterns to apply to the existing GuidanceInterface
 */

// Key styles to apply to GuidanceInterface.tsx:

const appleGuidanceStyles = {
  // Main container
  guidanceInterface: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: '#ffffff',
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
  },

  // Header redesign
  header: {
    background: '#ffffff',
    borderBottom: '1px solid #e5e7eb',
    padding: '1rem 2rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
  },

  // Back button
  backButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    background: 'none',
    border: 'none',
    color: '#007aff',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: 500,
    padding: '0.5rem 1rem',
    borderRadius: '0.5rem',
    transition: 'all 0.2s ease'
  },

  // Messages container
  messagesContainer: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    maxWidth: '800px',
    margin: '0 auto',
    width: '100%',
    padding: '2rem',
    gap: '1.5rem'
  },

  // User message bubble
  userMessage: {
    alignSelf: 'flex-end',
    maxWidth: '70%',
    background: '#007aff',
    color: 'white',
    padding: '0.75rem 1rem',
    borderRadius: '1.125rem',
    fontSize: '1rem',
    lineHeight: 1.4,
    wordWrap: 'break-word'
  },

  // Assistant message bubble
  assistantMessage: {
    alignSelf: 'flex-start',
    maxWidth: '85%',
    background: '#f1f5f9',
    color: '#1e293b',
    padding: '1rem 1.25rem',
    borderRadius: '1.125rem',
    fontSize: '1rem',
    lineHeight: 1.5,
    border: '1px solid #e2e8f0'
  },

  // Input area
  inputArea: {
    background: '#ffffff',
    borderTop: '1px solid #e5e7eb',
    padding: '1.5rem 2rem',
    position: 'sticky',
    bottom: 0
  },

  // Input container
  inputContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    background: '#f8fafc',
    border: '1px solid #e2e8f0',
    borderRadius: '1.25rem',
    padding: '0.5rem',
    maxWidth: '800px',
    margin: '0 auto',
    transition: 'border-color 0.2s ease'
  },

  // Message input
  messageInput: {
    flex: 1,
    border: 'none',
    background: 'none',
    padding: '0.75rem 1rem',
    fontSize: '1rem',
    outline: 'none',
    resize: 'none',
    fontFamily: 'inherit',
    color: '#1e293b'
  },

  // Send button
  sendButton: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    border: 'none',
    background: '#007aff',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  },

  // Welcome state
  welcomeState: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
    textAlign: 'center',
    padding: '3rem 2rem'
  },

  welcomeContent: {
    maxWidth: '500px'
  },

  welcomeTitle: {
    fontSize: '2rem',
    fontWeight: 600,
    color: '#1d1d1f',
    marginBottom: '0.75rem'
  },

  welcomeSubtitle: {
    fontSize: '1.125rem',
    color: '#6e6e73',
    lineHeight: 1.5,
    marginBottom: '2rem'
  },

  // Personality indicator
  personalityIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.75rem 1rem',
    background: '#f8fafc',
    borderRadius: '0.75rem',
    border: '1px solid #e2e8f0'
  },

  personalityAvatar: {
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontSize: '0.875rem',
    fontWeight: 600
  },

  // Loading state
  loadingDots: {
    display: 'flex',
    gap: '0.25rem',
    alignItems: 'center',
    padding: '0.5rem'
  },

  loadingDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: '#9ca3af',
    animation: 'pulse 1.5s ease-in-out infinite'
  }
};

// CSS to inject into the component
const appleGuidanceCSS = `
  @keyframes pulse {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
  }

  .loading-dot:nth-child(1) { animation-delay: 0s; }
  .loading-dot:nth-child(2) { animation-delay: 0.15s; }
  .loading-dot:nth-child(3) { animation-delay: 0.3s; }

  .input-container:focus-within {
    border-color: #007aff;
    box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
  }

  .send-button:hover {
    background: #0056d3;
    transform: scale(1.05);
  }

  .send-button:disabled {
    background: #e5e7eb;
    cursor: not-allowed;
    transform: none;
  }

  .back-button:hover {
    background: #f0f9ff;
  }

  .user-message {
    box-shadow: 0 1px 2px rgba(0, 122, 255, 0.2);
  }

  .assistant-message {
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .messages-container {
      padding: 1rem;
    }
    
    .input-area {
      padding: 1rem;
    }
    
    .user-message,
    .assistant-message {
      max-width: 90%;
    }
    
    .welcome-title {
      font-size: 1.5rem;
    }
    
    .welcome-subtitle {
      font-size: 1rem;
    }
  }
`;

export { appleGuidanceStyles, appleGuidanceCSS };
