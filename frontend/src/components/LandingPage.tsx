import React, { useState, useEffect } from 'react';
import { ArrowRight, Brain, Heart, Star, Zap, Users, Shield, Sparkles, MessageCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';

// CSS Variables for Apple Design System
const cssVariables = `
  :root {
    --background-primary: #ffffff;
    --background-secondary: #f5f5f7;
    --text-primary: #1d1d1f;
    --text-secondary: #6e6e73;
    --accent-brand: #f97316;
    --accent-interactive: #007aff;
    --border-color: #d2d2d7;
  }

  @keyframes pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
  }

  @keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(5deg); }
  }
`;

interface Personality {
  id: string;
  name: string;
  domain: string;
  description: string;
  expertise: string;
  color: string;
  darkColor: string;
}

// Apple Design System Colors
const domainColors = {
  'Spiritual': '#007aff',
  'Scientific': '#34c759', 
  'Philosophical': '#5856d6',
  'Historical': '#ff9500',
  'Literary': '#af52de',
  'Leadership': '#ff3b30'
};

// Live Conversation Preview Component
const ConversationPreview: React.FC = () => {
  const [currentPersonality, setCurrentPersonality] = useState(0);
  const [messageIndex, setMessageIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(false);

  const conversations = [
    {
      personality: { name: 'Einstein', avatar: '🧠', color: '#34c759' },
      messages: [
        { type: 'user', text: 'How do you approach complex problems?' },
        { type: 'ai', text: 'Imagination is more important than knowledge. I like to think in pictures, not words. When facing the impossible, I ask: what if we\'re looking at this backwards?' }
      ]
    },
    {
      personality: { name: 'Marcus Aurelius', avatar: '🏛️', color: '#5856d6' },
      messages: [
        { type: 'user', text: 'How do I handle difficult people?' },
        { type: 'ai', text: 'Remember that the best revenge is not to be like your enemy. Focus on what you can control - your own actions and responses. Their behavior is their responsibility.' }
      ]
    },
    {
      personality: { name: 'Krishna', avatar: '🕉️', color: '#007aff' },
      messages: [
        { type: 'user', text: 'I\'m struggling with a difficult decision...' },
        { type: 'ai', text: 'Do your duty without attachment to results. When the path is unclear, ask yourself: what action aligns with dharma? What serves the greater good beyond yourself?' }
      ]
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setIsTyping(true);
      setTimeout(() => {
        setIsTyping(false);
        setMessageIndex((prev) => {
          if (prev >= conversations[currentPersonality].messages.length - 1) {
            setCurrentPersonality((p) => (p + 1) % conversations.length);
            return 0;
          }
          return prev + 1;
        });
      }, 1000);
    }, 4000);

    return () => clearInterval(interval);
  }, [currentPersonality]);

  const currentConvo = conversations[currentPersonality];
  const displayedMessages = currentConvo.messages.slice(0, messageIndex + 1);

  return (
    <div style={{
      background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
      borderRadius: '20px',
      padding: '24px',
      height: '480px',
      border: '1px solid #e2e8f0',
      boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '20px',
        padding: '12px 16px',
        background: 'rgba(255,255,255,0.8)',
        borderRadius: '12px',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{
          fontSize: '24px',
          marginRight: '12px'
        }}>
          {currentConvo.personality.avatar}
        </div>
        <div>
          <div style={{
            fontWeight: '600',
            color: '#1e293b',
            fontSize: '16px'
          }}>
            {currentConvo.personality.name}
          </div>
          <div style={{
            fontSize: '12px',
            color: '#64748b'
          }}>
            ✨ Live conversation
          </div>
        </div>
      </div>

      {/* Messages */}
      <div style={{
        height: '320px',
        overflowY: 'auto',
        marginBottom: '16px',
        paddingRight: '8px'
      }}>
        {displayedMessages.map((message, idx) => (
          <div key={idx} style={{
            display: 'flex',
            justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: '12px'
          }}>
            <div style={{
              maxWidth: '80%',
              padding: '12px 16px',
              borderRadius: '18px',
              background: message.type === 'user' 
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : 'rgba(255,255,255,0.9)',
              color: message.type === 'user' ? 'white' : '#1e293b',
              fontSize: '14px',
              lineHeight: '1.4',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              border: message.type === 'ai' ? '1px solid #e2e8f0' : 'none'
            }}>
              {message.text}
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start',
            marginBottom: '12px'
          }}>
            <div style={{
              padding: '12px 16px',
              borderRadius: '18px',
              background: 'rgba(255,255,255,0.9)',
              border: '1px solid #e2e8f0',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <div style={{
                display: 'flex',
                gap: '4px',
                alignItems: 'center'
              }}>
                <div style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: currentConvo.personality.color,
                  animation: 'pulse 1.5s ease-in-out infinite'
                }}></div>
                <div style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: currentConvo.personality.color,
                  animation: 'pulse 1.5s ease-in-out infinite 0.2s'
                }}></div>
                <div style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: currentConvo.personality.color,
                  animation: 'pulse 1.5s ease-in-out infinite 0.4s'
                }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Preview */}
      <div style={{
        position: 'absolute',
        bottom: '16px',
        left: '24px',
        right: '24px',
        background: 'rgba(255,255,255,0.9)',
        borderRadius: '24px',
        padding: '12px 20px',
        border: '1px solid #e2e8f0',
        backdropFilter: 'blur(10px)',
        fontSize: '14px',
        color: '#64748b',
        fontStyle: 'italic'
      }}>
        Ask anything... {currentConvo.personality.name} is listening
      </div>

      {/* Animated Background */}
      <div style={{
        position: 'absolute',
        top: '-50%',
        right: '-20%',
        width: '200px',
        height: '200px',
        background: `linear-gradient(45deg, ${currentConvo.personality.color}20, ${currentConvo.personality.color}10)`,
        borderRadius: '50%',
        filter: 'blur(60px)',
        animation: 'float 6s ease-in-out infinite'
      }}></div>
    </div>
  );
};

const personalities: Personality[] = [
  {
    id: 'krishna',
    name: 'Krishna',
    domain: 'Spiritual',
    description: 'Divine wisdom from the Bhagavad Gita with cross-session memory',
    expertise: 'Dharma, duty, and spiritual enlightenment',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'buddha',
    name: 'Buddha',
    domain: 'Spiritual',
    description: 'Path to liberation from suffering with persistent insights',
    expertise: 'Mindfulness, compassion, and enlightenment',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'jesus_christ',
    name: 'Jesus Christ',
    domain: 'Spiritual',
    description: 'Love, compassion, and spiritual guidance with memory',
    expertise: 'Faith, love, and spiritual transformation',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'rumi',
    name: 'Rumi',
    domain: 'Spiritual',
    description: 'Mystical poetry and divine love with enhanced citations',
    expertise: 'Sufism, poetry, and spiritual love',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'swami_vivekananda',
    name: 'Swami Vivekananda',
    domain: 'Spiritual',
    description: 'Vedantic wisdom and spiritual strength with cross-session guidance',
    expertise: 'Vedanta, spirituality, and human potential',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'albert_einstein',
    name: 'Albert Einstein',
    domain: 'Scientific',
    description: 'Revolutionary insights into the universe with enhanced RAG',
    expertise: 'Physics, mathematics, and scientific thinking',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'isaac_newton',
    name: 'Isaac Newton',
    domain: 'Scientific',
    description: 'Mathematical genius with persistent scientific insights',
    expertise: 'Mathematics, physics, and natural laws',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'nikola_tesla',
    name: 'Nikola Tesla',
    domain: 'Scientific',
    description: 'Visionary inventor with enhanced technical guidance',
    expertise: 'Electrical engineering, innovation, and invention',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'leonardo_da_vinci',
    name: 'Leonardo da Vinci',
    domain: 'Scientific',
    description: 'Renaissance genius with persistent creative insights',
    expertise: 'Art, science, and innovation',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'archimedes',
    name: 'Archimedes',
    domain: 'Scientific',
    description: 'Ancient mathematical genius with enhanced problem-solving',
    expertise: 'Mathematics, physics, and engineering',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'abraham_lincoln',
    name: 'Abraham Lincoln',
    domain: 'Leadership',
    description: 'Leadership through moral conviction with conversation memory',
    expertise: 'Governance, unity, and moral leadership',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'chanakya',
    name: 'Chanakya',
    domain: 'Leadership',
    description: 'Ancient strategist with cross-session strategic insights',
    expertise: 'Strategy, economics, and political wisdom',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'mahatma_gandhi',
    name: 'Mahatma Gandhi',
    domain: 'Leadership',
    description: 'Non-violent resistance with persistent moral guidance',
    expertise: 'Non-violence, civil rights, and moral leadership',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'george_washington',
    name: 'George Washington',
    domain: 'Leadership',
    description: 'Founding leadership with enhanced historical perspective',
    expertise: 'Leadership, governance, and nation-building',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'benjamin_franklin',
    name: 'Benjamin Franklin',
    domain: 'Leadership',
    description: 'Practical wisdom and diplomacy with cross-session insights',
    expertise: 'Diplomacy, innovation, and practical wisdom',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'martin_luther_king_jr',
    name: 'Martin Luther King Jr.',
    domain: 'Leadership',
    description: 'Civil rights leadership with cross-session inspiration',
    expertise: 'Civil rights, equality, and social justice',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'marcus_aurelius',
    name: 'Marcus Aurelius',
    domain: 'Philosophical',
    description: 'Stoic wisdom for life\'s challenges with persistent guidance',
    expertise: 'Philosophy, resilience, and inner strength',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'lao_tzu',
    name: 'Lao Tzu',
    domain: 'Philosophical',
    description: 'The way of natural harmony with persistent wisdom',
    expertise: 'Taoism, balance, and natural wisdom',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'confucius',
    name: 'Confucius',
    domain: 'Philosophical',
    description: 'Ethics and social harmony with enhanced authenticity',
    expertise: 'Ethics, social harmony, and education',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'plato',
    name: 'Plato',
    domain: 'Philosophical',
    description: 'Foundational philosophical wisdom with enhanced reasoning',
    expertise: 'Philosophy, politics, and metaphysics',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'aristotle',
    name: 'Aristotle',
    domain: 'Philosophical',
    description: 'Systematic knowledge with enhanced logical reasoning',
    expertise: 'Logic, ethics, and natural philosophy',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'socrates',
    name: 'Socrates',
    domain: 'Philosophical',
    description: 'Questioning wisdom with persistent dialectical memory',
    expertise: 'Philosophy, ethics, and critical thinking',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'william_shakespeare',
    name: 'William Shakespeare',
    domain: 'Literary',
    description: 'Timeless literary wisdom with cross-session creativity',
    expertise: 'Poetry, drama, and human nature',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'rabindranath_tagore',
    name: 'Rabindranath Tagore',
    domain: 'Literary',
    description: 'Bengali literary genius with enhanced poetic insights',
    expertise: 'Poetry, literature, and cultural renaissance',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  },
  {
    id: 'sigmund_freud',
    name: 'Sigmund Freud',
    domain: 'Psychology',
    description: 'Psychological insights with enhanced understanding of the mind',
    expertise: 'Psychology, psychoanalysis, and human behavior',
    color: '#ffffff',
    darkColor: '#f5f5f7'
  }
];

const LandingPage: React.FC = () => {
  const { isAuthenticated, account, login } = useAuth();
  const navigate = useNavigate();
  const [selectedPersonality, setSelectedPersonality] = useState(personalities[0]);
  const [selectedDomain, setSelectedDomain] = useState('All');

  // Helper function to filter personalities by domain
  const getFilteredPersonalities = () => {
    if (selectedDomain === 'All') {
      return personalities;
    }
    return personalities.filter(p => p.domain === selectedDomain);
  };

  // Redirect authenticated users - with protection against circular redirects
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    if (isAuthenticated && account) {
      console.log('🔄 LandingPage: Authenticated user detected, scheduling redirect to guidance');
      console.log('👤 User account:', account.username || account.name);
      
      // Add a small delay to prevent immediate redirects that might cause loops
      timeoutId = setTimeout(() => {
        console.log('🚀 LandingPage: Executing redirect to /guidance');
        navigate('/guidance', { replace: true });
      }, 200);
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [isAuthenticated, account, navigate]);

  const handleSignIn = async () => {
    try {
      await login();
    } catch (error) {
      console.error('Sign-in error:', error);
    }
  };

  const handleBeginJourney = () => {
    if (isAuthenticated) {
      navigate('/guidance');
    } else {
      handleSignIn();
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#ffffff',
      color: '#1d1d1f',
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    }}>
      {/* Header */}
      <header style={{
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: '#ffffff'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '1.5rem',
            height: '1.5rem',
            background: '#f97316',
            borderRadius: '50%'
          }}>
          </div>
          <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600', color: '#1d1d1f' }}>Vimarsh</h1>
        </div>
        <nav style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <a href="#personalities" style={{ color: '#1d1d1f', textDecoration: 'none', fontSize: '0.9rem', fontWeight: '500' }}>Personalities</a>
          <a href="#features" style={{ color: '#1d1d1f', textDecoration: 'none', fontSize: '0.9rem', fontWeight: '500' }}>Features</a>
          <button
            onClick={handleBeginJourney}
            style={{
              background: '#007aff',
              border: 'none',
              color: 'white',
              padding: '0.6rem 1.25rem',
              borderRadius: '1.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontSize: '0.85rem',
              fontWeight: '500',
              transition: 'all 0.3s ease',
              boxShadow: '0 2px 8px rgba(0, 122, 255, 0.25)'
            }}
          >
            Get Started
          </button>
        </nav>
      </header>

      {/* Hero Section */}
      <section style={{
        padding: '4rem 2rem',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div style={{
          display: 'flex',
          gap: '4rem',
          alignItems: 'flex-start',
          minHeight: '500px',
          width: '100%'
        }}>
          {/* Left side - Text content */}
          <div style={{ 
            width: '50%',
            paddingRight: '2rem'
          }}>
            <h1 style={{
              fontSize: '3rem',
              fontWeight: '600',
              marginBottom: '1.25rem',
              color: '#1d1d1f',
              lineHeight: '1.2'
            }}>
              Step into History.<br />
              <span style={{
                color: '#8b5cf6',
                fontWeight: '700'
              }}>
                Wisdom Awaits.
              </span>
            </h1>

            <p style={{
              fontSize: '1.125rem',
              color: '#6b7280',
              marginBottom: '2rem',
              lineHeight: '1.6'
            }}>
              What would you ask Einstein about the universe? How would Marcus Aurelius guide you through adversity? Experience real conversations with history's greatest minds — each personality remembers your journey and offers wisdom tailored to your life.
            </p>

            <button
              onClick={handleBeginJourney}
              style={{
                background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                color: 'white',
                border: 'none',
                padding: '0.875rem 2rem',
                fontSize: '1rem',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontWeight: '500',
                marginBottom: '2rem',
                boxShadow: '0 4px 14px rgba(139, 92, 246, 0.3)',
                transition: 'all 0.2s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(139, 92, 246, 0.4)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 14px rgba(139, 92, 246, 0.3)';
              }}
            >
              Begin Your Journey ✨
            </button>

            {/* Stats */}
            <div style={{
              display: 'flex',
              gap: '3rem',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontSize: '2rem', fontWeight: '600', color: '#1d1d1f' }}>25</div>
                <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Legendary Minds</div>
              </div>
              <div>
                <div style={{ fontSize: '2rem', fontWeight: '600', color: '#1d1d1f' }}>∞</div>
                <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Conversations</div>
              </div>
              <div>
                <div style={{ fontSize: '2rem', fontWeight: '600', color: '#1d1d1f' }}>2500+</div>
                <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Years of Wisdom</div>
              </div>
            </div>
          </div>

          {/* Right side - Live Conversation Preview */}
          <div style={{ 
            width: '50%',
            paddingLeft: '2rem'
          }}>
            <ConversationPreview />
          </div>
        </div>
      </section>

      {/* Wisdom in Action */}
      <section style={{
        padding: '4rem 2rem',
        maxWidth: '1200px',
        margin: '0 auto',
        textAlign: 'center'
      }}>
        <h2 style={{
          fontSize: '2.25rem',
          fontWeight: '600',
          marginBottom: '1rem',
          color: '#1d1d1f'
        }}>
          Wisdom in Action
        </h2>
        
        <p style={{
          fontSize: '1.125rem',
          color: '#6b7280',
          marginBottom: '3rem',
          maxWidth: '600px',
          margin: '0 auto 3rem auto'
        }}>
          See how history's greatest minds would respond to today's challenges
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '2rem',
          maxWidth: '1000px',
          margin: '0 auto'
        }}>
          {/* Einstein Card */}
          <div style={{
            background: 'linear-gradient(135deg, #f8fafc 0%, #e1f5fe 100%)',
            border: '1px solid #e2e8f0',
            borderRadius: '20px',
            padding: '24px',
            textAlign: 'left',
            transition: 'all 0.3s ease',
            cursor: 'pointer',
            position: 'relative',
            overflow: 'hidden'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '16px'
            }}>
              <div style={{
                fontSize: '32px',
                marginRight: '12px'
              }}>🧠</div>
              <div>
                <div style={{ fontWeight: '600', color: '#1e293b' }}>Einstein</div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>On Innovation</div>
              </div>
            </div>
            <div style={{
              background: 'rgba(255,255,255,0.8)',
              padding: '16px',
              borderRadius: '12px',
              fontSize: '14px',
              color: '#334155',
              fontStyle: 'italic',
              lineHeight: '1.5'
            }}>
              "Innovation is not about having all the answers — it's about asking better questions. What if we approached this problem from the impossible angle?"
            </div>
            <div style={{
              position: 'absolute',
              top: '-20px',
              right: '-20px',
              width: '80px',
              height: '80px',
              background: 'linear-gradient(45deg, #34c75920, #34c75910)',
              borderRadius: '50%',
              filter: 'blur(20px)'
            }}></div>
          </div>

          {/* Marcus Aurelius Card */}
          <div style={{
            background: 'linear-gradient(135deg, #f8fafc 0%, #f3e8ff 100%)',
            border: '1px solid #e2e8f0',
            borderRadius: '20px',
            padding: '24px',
            textAlign: 'left',
            transition: 'all 0.3s ease',
            cursor: 'pointer',
            position: 'relative',
            overflow: 'hidden'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '16px'
            }}>
              <div style={{
                fontSize: '32px',
                marginRight: '12px'
              }}>🏛️</div>
              <div>
                <div style={{ fontWeight: '600', color: '#1e293b' }}>Marcus Aurelius</div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>On Resilience</div>
              </div>
            </div>
            <div style={{
              background: 'rgba(255,255,255,0.8)',
              padding: '16px',
              borderRadius: '12px',
              fontSize: '14px',
              color: '#334155',
              fontStyle: 'italic',
              lineHeight: '1.5'
            }}>
              "You cannot control what happens to you, but you can master how you respond. In every setback lies the seed of equal or greater benefit."
            </div>
            <div style={{
              position: 'absolute',
              top: '-20px',
              right: '-20px',
              width: '80px',
              height: '80px',
              background: 'linear-gradient(45deg, #5856d620, #5856d610)',
              borderRadius: '50%',
              filter: 'blur(20px)'
            }}></div>
          </div>

          {/* Krishna Card */}
          <div style={{
            background: 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)',
            border: '1px solid #e2e8f0',
            borderRadius: '20px',
            padding: '24px',
            textAlign: 'left',
            transition: 'all 0.3s ease',
            cursor: 'pointer',
            position: 'relative',
            overflow: 'hidden'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '16px'
            }}>
              <div style={{
                fontSize: '32px',
                marginRight: '12px'
              }}>🕉️</div>
              <div>
                <div style={{ fontWeight: '600', color: '#1e293b' }}>Krishna</div>
                <div style={{ fontSize: '12px', color: '#64748b' }}>On Purpose</div>
              </div>
            </div>
            <div style={{
              background: 'rgba(255,255,255,0.8)',
              padding: '16px',
              borderRadius: '12px',
              fontSize: '14px',
              color: '#334155',
              fontStyle: 'italic',
              lineHeight: '1.5'
            }}>
              "When you act with dharma as your guide, the outcome becomes secondary. Focus on righteous action, and let the universe handle the results."
            </div>
            <div style={{
              position: 'absolute',
              top: '-20px',
              right: '-20px',
              width: '80px',
              height: '80px',
              background: 'linear-gradient(45deg, #007aff20, #007aff10)',
              borderRadius: '50%',
              filter: 'blur(20px)'
            }}></div>
          </div>
        </div>

        <div style={{
          marginTop: '3rem'
        }}>
          <button
            onClick={handleBeginJourney}
            style={{
              background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              fontSize: '16px',
              borderRadius: '12px',
              cursor: 'pointer',
              fontWeight: '500',
              boxShadow: '0 4px 14px rgba(30, 41, 59, 0.3)',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 8px 25px rgba(30, 41, 59, 0.4)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 14px rgba(30, 41, 59, 0.3)';
            }}
          >
            Explore All 25 Minds →
          </button>
        </div>
      </section>

      {/* Personalities Showcase */}
      <section id="personalities" style={{
        padding: '4rem 2rem',
        maxWidth: '1000px',
        margin: '4rem auto'
      }}>
        <h2 style={{
          fontSize: '2.25rem',
          fontWeight: '600',
          textAlign: 'center',
          marginBottom: '0.75rem',
          color: '#1d1d1f'
        }}>
          Meet the Great Minds
        </h2>
        
        <p style={{
          textAlign: 'center',
          fontSize: '1rem',
          color: '#6b7280',
          marginBottom: '3rem',
          maxWidth: '550px',
          margin: '0 auto 3rem'
        }}>
          Explore 25 distinct personalities across 6 domains of human knowledge and wisdom
        </p>

        {/* Domain Tabs */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          flexWrap: 'wrap',
          gap: '0.5rem',
          marginBottom: '2rem'
        }}>
          {['All', 'Spiritual', 'Philosophical', 'Scientific', 'Leadership', 'Literary', 'Psychology'].map((domain) => (
            <button
              key={domain}
              onClick={() => setSelectedDomain(domain)}
              style={{
                background: selectedDomain === domain 
                  ? '#007aff'
                  : 'white',
                border: selectedDomain === domain 
                  ? 'none'
                  : '1px solid #e5e7eb',
                color: selectedDomain === domain ? 'white' : '#374151',
                padding: '0.6rem 1.25rem',
                borderRadius: '1.5rem',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: '500',
                transition: 'all 0.3s ease',
                boxShadow: selectedDomain === domain ? '0 2px 8px rgba(0, 122, 255, 0.25)' : '0 1px 3px rgba(0, 0, 0, 0.05)'
              }}
              onMouseEnter={(e) => {
                if (selectedDomain !== domain) {
                  e.currentTarget.style.background = '#f9fafb';
                  e.currentTarget.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.1)';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedDomain !== domain) {
                  e.currentTarget.style.background = 'white';
                  e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
                }
              }}
            >
              {domain}
            </button>
          ))}
        </div>

        {/* Personalities Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.5rem',
          maxHeight: selectedDomain === 'All' ? 'none' : '800px',
          overflow: selectedDomain === 'All' ? 'visible' : 'hidden'
        }}>
          {getFilteredPersonalities().map((personality) => (
            <div
              key={personality.id}
              style={{
                background: 'white',
                borderRadius: '0.75rem',
                padding: '1.75rem',
                boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                transition: 'all 0.3s ease',
                cursor: 'pointer',
                border: '1px solid #f3f4f6'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)';
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '1rem'
              }}>
                <div style={{
                  width: '2.25rem',
                  height: '2.25rem',
                  borderRadius: '50%',
                  background: '#f8fafc',
                  border: `2px solid ${domainColors[personality.domain as keyof typeof domainColors] || '#6b7280'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: domainColors[personality.domain as keyof typeof domainColors] || '#6b7280',
                  fontWeight: '600',
                  fontSize: '0.9rem'
                }}>
                  {personality.name.charAt(0)}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.5rem',
                    marginBottom: '0.25rem'
                  }}>
                    <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: '600', color: '#1f2937' }}>{personality.name}</h3>
                    <div style={{
                      width: '0.375rem',
                      height: '0.375rem',
                      borderRadius: '50%',
                      backgroundColor: domainColors[personality.domain as keyof typeof domainColors] || '#6b7280'
                    }} />
                  </div>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: '#6b7280' }}>{personality.domain}</p>
                </div>
              </div>
              <p style={{ 
                margin: '0 0 0.75rem 0', 
                fontSize: '0.85rem', 
                lineHeight: '1.4',
                color: '#6b7280',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}>
                {personality.description}
              </p>
              <div style={{
                fontSize: '0.75rem',
                color: '#9ca3af',
                fontStyle: 'italic'
              }}>
                {personality.expertise}
              </div>
            </div>
          ))}
        </div>

        {selectedDomain === 'All' && getFilteredPersonalities().length > 12 && (
          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <p style={{ fontSize: '0.9rem', opacity: 0.7 }}>
              Showing all {getFilteredPersonalities().length} personalities
            </p>
          </div>
        )}
      </section>

      {/* Features */}
      <section id="features" style={{
        padding: '3rem 2rem',
        background: 'rgba(255, 255, 255, 0.8)',
        borderRadius: '1.25rem',
        margin: '2rem auto',
        maxWidth: '1000px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.2)'
      }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <h2 style={{
            fontSize: '2rem',
            fontWeight: '600',
            textAlign: 'center',
            marginBottom: '2.5rem',
            color: '#1f2937'
          }}>
            How It Feels to Talk with Genius
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '1.25rem'
          }}>
            <div style={{
              background: 'white',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              textAlign: 'center',
              border: '1px solid #f0f0f0',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
            }}>
              <div style={{
                width: '3rem',
                height: '3rem',
                borderRadius: '50%',
                background: '#f97316',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
              }}>
                <Brain size={24} style={{ color: 'white' }} />
              </div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.75rem', color: '#1f2937' }}>They Actually Think with You</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.5', fontSize: '0.9rem' }}>
                Each personality draws from their authentic writings, speeches, and works. They don't just recite facts - they engage with your questions using their actual thought patterns and wisdom.
              </p>
            </div>

            <div style={{
              background: 'white',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              textAlign: 'center',
              border: '1px solid #f0f0f0',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
            }}>
              <div style={{
                width: '3rem',
                height: '3rem',
                borderRadius: '50%',
                background: '#3b82f6',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
              }}>
                <Shield size={24} style={{ color: 'white' }} />
              </div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.75rem', color: '#1f2937' }}>They Remember You</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.5', fontSize: '0.9rem' }}>
                Every conversation builds on the last. Ask Einstein about quantum mechanics today, then return tomorrow and he'll remember your previous discussion and build upon it.
              </p>
            </div>

            <div style={{
              background: 'white',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              textAlign: 'center',
              border: '1px solid #f0f0f0',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
            }}>
              <div style={{
                width: '3rem',
                height: '3rem',
                borderRadius: '50%',
                background: '#10b981',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
              }}>
                <Sparkles size={24} style={{ color: 'white' }} />
              </div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.75rem', color: '#1f2937' }}>Their Life's Work at Your Fingertips</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.5', fontSize: '0.9rem' }}>
                Access thousands of years of human wisdom. Whether you need strategic advice from Chanakya, spiritual guidance from Buddha, or scientific insights from Newton.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: '3rem 2rem 2rem',
        textAlign: 'center',
        background: '#fafafa',
        color: '#6b7280',
        marginTop: '4rem'
      }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
            <div style={{
              width: '2.25rem',
              height: '2.25rem',
              background: 'linear-gradient(135deg, #f97316, #ea580c)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.25rem',
              fontWeight: 'bold',
              color: 'white',
              border: '2px solid rgba(255, 255, 255, 0.2)'
            }}>
              V
            </div>
            <span style={{ fontSize: '1.375rem', fontWeight: '600', color: '#6b7280' }}>Vimarsh</span>
          </div>
          <p style={{ color: '#6b7280', marginBottom: '1.25rem', maxWidth: '550px', margin: '0 auto 1.25rem', fontSize: '0.9rem' }}>
            Bridging ancient wisdom with modern technology to bring you meaningful conversations with history's greatest minds.
          </p>
          <div style={{ color: '#9ca3af', fontSize: '0.8rem' }}>
            © 2025 Vimarsh. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
