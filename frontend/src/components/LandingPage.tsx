import React, { useState, useEffect } from 'react';
import { ArrowRight, Brain, Heart, Star, Zap, Users, Shield, Sparkles, MessageCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';

interface Personality {
  id: string;
  name: string;
  domain: string;
  description: string;
  expertise: string;
  color: string;
  darkColor: string;
}

const personalities: Personality[] = [
  {
    id: 'krishna',
    name: 'Krishna',
    domain: 'Spiritual',
    description: 'Divine wisdom from the Bhagavad Gita with cross-session memory',
    expertise: 'Dharma, duty, and spiritual enlightenment',
    color: '#4F46E5',
    darkColor: '#3730A3'
  },
  {
    id: 'buddha',
    name: 'Buddha',
    domain: 'Spiritual',
    description: 'Path to liberation from suffering with persistent insights',
    expertise: 'Mindfulness, compassion, and enlightenment',
    color: '#F59E0B',
    darkColor: '#D97706'
  },
  {
    id: 'jesus_christ',
    name: 'Jesus Christ',
    domain: 'Spiritual',
    description: 'Love, compassion, and spiritual guidance with memory',
    expertise: 'Faith, love, and spiritual transformation',
    color: '#06B6D4',
    darkColor: '#0891B2'
  },
  {
    id: 'rumi',
    name: 'Rumi',
    domain: 'Spiritual',
    description: 'Mystical poetry and divine love with enhanced citations',
    expertise: 'Sufism, poetry, and spiritual love',
    color: '#EC4899',
    darkColor: '#DB2777'
  },
  {
    id: 'swami_vivekananda',
    name: 'Swami Vivekananda',
    domain: 'Spiritual',
    description: 'Vedantic wisdom and spiritual strength with cross-session guidance',
    expertise: 'Vedanta, spirituality, and human potential',
    color: '#F97316',
    darkColor: '#EA580C'
  },
  {
    id: 'albert_einstein',
    name: 'Albert Einstein',
    domain: 'Scientific',
    description: 'Revolutionary insights into the universe with enhanced RAG',
    expertise: 'Physics, mathematics, and scientific thinking',
    color: '#10B981',
    darkColor: '#059669'
  },
  {
    id: 'isaac_newton',
    name: 'Isaac Newton',
    domain: 'Scientific',
    description: 'Mathematical genius with persistent scientific insights',
    expertise: 'Mathematics, physics, and natural laws',
    color: '#8B5CF6',
    darkColor: '#7C3AED'
  },
  {
    id: 'nikola_tesla',
    name: 'Nikola Tesla',
    domain: 'Scientific',
    description: 'Visionary inventor with enhanced technical guidance',
    expertise: 'Electrical engineering, innovation, and invention',
    color: '#0EA5E9',
    darkColor: '#0284C7'
  },
  {
    id: 'leonardo_da_vinci',
    name: 'Leonardo da Vinci',
    domain: 'Scientific',
    description: 'Renaissance genius with persistent creative insights',
    expertise: 'Art, science, and innovation',
    color: '#059669',
    darkColor: '#047857'
  },
  {
    id: 'archimedes',
    name: 'Archimedes',
    domain: 'Scientific',
    description: 'Ancient mathematical genius with enhanced problem-solving',
    expertise: 'Mathematics, physics, and engineering',
    color: '#7C3AED',
    darkColor: '#5B21B6'
  },
  {
    id: 'abraham_lincoln',
    name: 'Abraham Lincoln',
    domain: 'Leadership',
    description: 'Leadership through moral conviction with conversation memory',
    expertise: 'Governance, unity, and moral leadership',
    color: '#EF4444',
    darkColor: '#DC2626'
  },
  {
    id: 'chanakya',
    name: 'Chanakya',
    domain: 'Leadership',
    description: 'Ancient strategist with cross-session strategic insights',
    expertise: 'Strategy, economics, and political wisdom',
    color: '#F97316',
    darkColor: '#EA580C'
  },
  {
    id: 'mahatma_gandhi',
    name: 'Mahatma Gandhi',
    domain: 'Leadership',
    description: 'Non-violent resistance with persistent moral guidance',
    expertise: 'Non-violence, civil rights, and moral leadership',
    color: '#059669',
    darkColor: '#047857'
  },
  {
    id: 'george_washington',
    name: 'George Washington',
    domain: 'Leadership',
    description: 'Founding leadership with enhanced historical perspective',
    expertise: 'Leadership, governance, and nation-building',
    color: '#DC2626',
    darkColor: '#991B1B'
  },
  {
    id: 'benjamin_franklin',
    name: 'Benjamin Franklin',
    domain: 'Leadership',
    description: 'Practical wisdom and diplomacy with cross-session insights',
    expertise: 'Diplomacy, innovation, and practical wisdom',
    color: '#0891B2',
    darkColor: '#0E7490'
  },
  {
    id: 'martin_luther_king_jr',
    name: 'Martin Luther King Jr.',
    domain: 'Leadership',
    description: 'Civil rights leadership with cross-session inspiration',
    expertise: 'Civil rights, equality, and social justice',
    color: '#7C3AED',
    darkColor: '#5B21B6'
  },
  {
    id: 'marcus_aurelius',
    name: 'Marcus Aurelius',
    domain: 'Philosophical',
    description: 'Stoic wisdom for life\'s challenges with persistent guidance',
    expertise: 'Philosophy, resilience, and inner strength',
    color: '#8B5CF6',
    darkColor: '#7C3AED'
  },
  {
    id: 'lao_tzu',
    name: 'Lao Tzu',
    domain: 'Philosophical',
    description: 'The way of natural harmony with persistent wisdom',
    expertise: 'Taoism, balance, and natural wisdom',
    color: '#14B8A6',
    darkColor: '#0D9488'
  },
  {
    id: 'confucius',
    name: 'Confucius',
    domain: 'Philosophical',
    description: 'Ethics and social harmony with enhanced authenticity',
    expertise: 'Ethics, social harmony, and education',
    color: '#6366F1',
    darkColor: '#4F46E5'
  },
  {
    id: 'plato',
    name: 'Plato',
    domain: 'Philosophical',
    description: 'Foundational philosophical wisdom with enhanced reasoning',
    expertise: 'Philosophy, politics, and metaphysics',
    color: '#DC2626',
    darkColor: '#B91C1C'
  },
  {
    id: 'aristotle',
    name: 'Aristotle',
    domain: 'Philosophical',
    description: 'Systematic knowledge with enhanced logical reasoning',
    expertise: 'Logic, ethics, and natural philosophy',
    color: '#991B1B',
    darkColor: '#7F1D1D'
  },
  {
    id: 'socrates',
    name: 'Socrates',
    domain: 'Philosophical',
    description: 'Questioning wisdom with persistent dialectical memory',
    expertise: 'Philosophy, ethics, and critical thinking',
    color: '#7C2D12',
    darkColor: '#451A03'
  },
  {
    id: 'william_shakespeare',
    name: 'William Shakespeare',
    domain: 'Literary',
    description: 'Timeless literary wisdom with cross-session creativity',
    expertise: 'Poetry, drama, and human nature',
    color: '#7C3AED',
    darkColor: '#5B21B6'
  },
  {
    id: 'rabindranath_tagore',
    name: 'Rabindranath Tagore',
    domain: 'Literary',
    description: 'Bengali literary genius with enhanced poetic insights',
    expertise: 'Poetry, literature, and cultural renaissance',
    color: '#059669',
    darkColor: '#047857'
  },
  {
    id: 'sigmund_freud',
    name: 'Sigmund Freud',
    domain: 'Psychology',
    description: 'Psychological insights with enhanced understanding of the mind',
    expertise: 'Psychology, psychoanalysis, and human behavior',
    color: '#DC2626',
    darkColor: '#991B1B'
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
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    }}>
      {/* Header */}
      <header style={{
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '4.5rem',
            height: '4.5rem',
            background: 'linear-gradient(135deg, #fbbf24, #f59e0b)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '2.5rem',
            fontWeight: 'bold',
            color: 'white',
            border: '3px solid rgba(255, 255, 255, 0.3)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
          }}>
            V
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: '700' }}>Vimarsh</h1>
            <p style={{ margin: 0, fontSize: '0.875rem', opacity: 0.8 }}>Wisdom Without Boundaries</p>
          </div>
        </div>
        <nav style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <a href="#personalities" style={{ color: 'white', textDecoration: 'none', opacity: 0.9, fontSize: '0.95rem' }}>Personalities</a>
          <a href="#features" style={{ color: 'white', textDecoration: 'none', opacity: 0.9, fontSize: '0.95rem' }}>Features</a>
          <button
            onClick={handleBeginJourney}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontSize: '0.875rem',
              transition: 'all 0.3s ease'
            }}
          >
            Begin Journey <ArrowRight size={16} />
          </button>
        </nav>
      </header>

      {/* Hero Section */}
      <section style={{
        padding: '4rem 2rem',
        textAlign: 'center',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <h1 style={{
          fontSize: '3.5rem',
          fontWeight: '700',
          marginBottom: '1rem',
          color: 'white',
          lineHeight: '1.1',
          textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
        }}>
          Converse with History's<br />
          <span style={{
            background: 'linear-gradient(135deg, #fef3c7, #fbbf24, #34d399, #60a5fa)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            textShadow: 'none',
            filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3))'
          }}>
            Greatest Minds
          </span>
        </h1>

        <p style={{
          fontSize: '1.25rem',
          opacity: 1,
          maxWidth: '800px',
          margin: '0 auto 2rem',
          lineHeight: '1.6',
          color: 'rgba(255, 255, 255, 0.95)',
          textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)'
        }}>
          Experience authentic conversations with 25 distinct personalities across 6 domains - from Einstein about scientific discovery to Krishna for spiritual wisdom, Lincoln for leadership, or Marcus Aurelius for philosophy. Enhanced with cross-session memory, each personality is grounded in their actual works with persistent conversation history that continues across your sessions.
        </p>

        <button
          onClick={handleBeginJourney}
          style={{
            background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
            color: 'white',
            border: 'none',
            padding: '1rem 2rem',
            fontSize: '1.1rem',
            borderRadius: '0.75rem',
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontWeight: '600',
            boxShadow: '0 10px 25px rgba(59, 130, 246, 0.3)',
            transition: 'all 0.3s ease',
            marginBottom: '1rem'
          }}
        >
          Begin Your Journey
        </button>

        <p style={{ fontSize: '0.9rem', opacity: 0.9, margin: 0, textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)' }}>
          Secure sign-in with Microsoft to unlock conversations with persistent memory across sessions
        </p>

        {/* Stats */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '1.5rem',
          marginTop: '4rem',
          padding: '2rem',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '1rem',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: '700', marginBottom: '0.5rem', textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)' }}>25</div>
            <div style={{ opacity: 0.9, fontSize: '0.95rem', textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)' }}>Great Minds</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: '700', marginBottom: '0.5rem', textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)' }}>6</div>
            <div style={{ opacity: 0.9, fontSize: '0.95rem', textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)' }}>Domains</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: '700', marginBottom: '0.5rem', textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)' }}>1000+</div>
            <div style={{ opacity: 0.9, fontSize: '0.95rem', textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)' }}>Authentic Texts</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: '700', marginBottom: '0.5rem', textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)' }}>Deep</div>
            <div style={{ opacity: 0.9, fontSize: '0.95rem', textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)' }}>Insights</div>
          </div>
        </div>
      </section>

      {/* Interactive Demo */}
      <section style={{
        padding: '4rem 2rem',
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{
            fontSize: '2.5rem',
            fontWeight: '700',
            textAlign: 'center',
            marginBottom: '3rem',
            textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
          }}>
            Experience the Conversation
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 2fr',
            gap: '2rem',
            alignItems: 'start'
          }}>
            {/* Personality Selector */}
            <div>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem', fontWeight: '600', textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)' }}>Choose a Personality</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {personalities.slice(0, 4).map((personality) => (
                  <button
                    key={personality.id}
                    onClick={() => setSelectedPersonality(personality)}
                    style={{
                      background: selectedPersonality.id === personality.id 
                        ? `linear-gradient(135deg, ${personality.color}, ${personality.darkColor})`
                        : 'rgba(255, 255, 255, 0.1)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      color: 'white',
                      padding: '1rem',
                      borderRadius: '0.75rem',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.3s ease',
                      backdropFilter: 'blur(10px)'
                    }}
                  >
                    <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{personality.name}</div>
                    <div style={{ fontSize: '0.85rem', opacity: 0.8 }}>{personality.domain}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Demo Conversation */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '1rem',
              padding: '1.5rem',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '1.5rem',
                paddingBottom: '1rem',
                borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
              }}>
                <div style={{
                  width: '3rem',
                  height: '3rem',
                  borderRadius: '50%',
                  background: `linear-gradient(135deg, ${selectedPersonality.color}, ${selectedPersonality.darkColor})`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: '600',
                  fontSize: '1.25rem'
                }}>
                  {selectedPersonality.name.charAt(0)}
                </div>
                <div>
                  <div style={{ fontWeight: '600', fontSize: '1.1rem' }}>{selectedPersonality.name}</div>
                  <div style={{ opacity: 0.7, fontSize: '0.85rem' }}>{selectedPersonality.domain} Wisdom</div>
                </div>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <div style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  padding: '0.75rem 1rem',
                  borderRadius: '1rem 1rem 1rem 0.25rem',
                  marginBottom: '0.75rem',
                  fontSize: '0.95rem'
                }}>
                  How can I find peace in difficult times?
                </div>

                <div style={{
                  background: `linear-gradient(135deg, ${selectedPersonality.color}20, ${selectedPersonality.darkColor}20)`,
                  padding: '1rem',
                  borderRadius: '1rem 1rem 0.25rem 1rem',
                  fontSize: '0.95rem',
                  lineHeight: '1.5',
                  border: `1px solid ${selectedPersonality.color}40`
                }}>
                  {selectedPersonality.id === 'krishna' && 
                    <>
                      <div style={{ marginBottom: '0.75rem' }}>
                        "In the midst of chaos, remember that you are not the body, nor the mind, but the eternal soul. As I taught Arjuna, perform your duty without attachment to results, and you shall find the peace that surpasses all understanding."
                      </div>
                      <div style={{
                        fontSize: '0.8rem',
                        opacity: 0.7,
                        fontStyle: 'italic',
                        borderTop: `1px solid ${selectedPersonality.color}30`,
                        paddingTop: '0.5rem'
                      }}>
                        Source: Bhagavad Gita 2.47, 6.29 - "You have a right to perform your prescribed duty, but not to the fruits of action"
                      </div>
                    </>
                  }
                  {selectedPersonality.id === 'buddha' && 
                    <>
                      <div style={{ marginBottom: '0.75rem' }}>
                        "Peace comes from within. Do not seek it without. The root of suffering is attachment - to outcomes, to desires, to the illusion of permanence. When you accept that all things are impermanent and release your grip on expectations, you will find the peace that surpasses understanding."
                      </div>
                      <div style={{
                        fontSize: '0.8rem',
                        opacity: 0.7,
                        fontStyle: 'italic',
                        borderTop: `1px solid ${selectedPersonality.color}30`,
                        paddingTop: '0.5rem'
                      }}>
                        Source: Dhammapada 1.1, Four Noble Truths - "All that we are is the result of what we have thought"
                      </div>
                    </>
                  }
                  {selectedPersonality.id === 'albert_einstein' && 
                    <>
                      <div style={{ marginBottom: '0.75rem' }}>
                        "In times of difficulty, I find solace in the eternal laws of nature. The universe operates on principles of harmony and order. When we align our understanding with these cosmic truths, we find a peace that transcends temporary troubles."
                      </div>
                      <div style={{
                        fontSize: '0.8rem',
                        opacity: 0.7,
                        fontStyle: 'italic',
                        borderTop: `1px solid ${selectedPersonality.color}30`,
                        paddingTop: '0.5rem'
                      }}>
                        Source: "The World As I See It" (1930) - "A human being is part of the whole called by us universe"
                      </div>
                    </>
                  }
                  {selectedPersonality.id === 'abraham_lincoln' && 
                    <>
                      <div style={{ marginBottom: '0.75rem' }}>
                        "I have learned that in our darkest hours, we must hold fast to the better angels of our nature. A house divided cannot stand, and neither can the human spirit when it wars against itself. Seek unity within, and peace will follow."
                      </div>
                      <div style={{
                        fontSize: '0.8rem',
                        opacity: 0.7,
                        fontStyle: 'italic',
                        borderTop: `1px solid ${selectedPersonality.color}30`,
                        paddingTop: '0.5rem'
                      }}>
                        Source: First Inaugural Address (1861), House Divided Speech (1858) - "The better angels of our nature"
                      </div>
                    </>
                  }
                  {selectedPersonality.id === 'aurelius' && 
                    <>
                      <div style={{ marginBottom: '0.75rem' }}>
                        "Remember, you have power over your mind - not outside events. Realize this, and you will find strength. What disturbs people's minds is not events but their judgments about events. Change your perspective, and find your peace."
                      </div>
                      <div style={{
                        fontSize: '0.8rem',
                        opacity: 0.7,
                        fontStyle: 'italic',
                        borderTop: `1px solid ${selectedPersonality.color}30`,
                        paddingTop: '0.5rem'
                      }}>
                        Source: Meditations Book 2.11, 11.18 - "You have power over your mind - not outside events"
                      </div>
                    </>
                  }
                </div>
              </div>

              <div style={{
                fontSize: '0.8rem',
                opacity: 0.6,
                fontStyle: 'italic',
                textAlign: 'center'
              }}>
                Authentic responses based on {selectedPersonality.expertise}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Personalities Showcase */}
      <section id="personalities" style={{
        padding: '4rem 2rem',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <h2 style={{
          fontSize: '2.5rem',
          fontWeight: '700',
          textAlign: 'center',
          marginBottom: '1rem',
          textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
        }}>
          Meet the Great Minds
        </h2>
        
        <p style={{
          textAlign: 'center',
          fontSize: '1.1rem',
          opacity: 0.8,
          marginBottom: '3rem',
          maxWidth: '600px',
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
                  ? 'linear-gradient(135deg, #fbbf24, #f59e0b)'
                  : 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: 'white',
                padding: '0.75rem 1.5rem',
                borderRadius: '2rem',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: '500',
                transition: 'all 0.3s ease',
                backdropFilter: 'blur(10px)'
              }}
              onMouseEnter={(e) => {
                if (selectedDomain !== domain) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedDomain !== domain) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
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
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1rem',
          maxHeight: selectedDomain === 'All' ? 'none' : '800px',
          overflow: selectedDomain === 'All' ? 'visible' : 'hidden'
        }}>
          {getFilteredPersonalities().map((personality) => (
            <div
              key={personality.id}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '0.75rem',
                padding: '1.25rem',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                transition: 'all 0.3s ease',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-3px)';
                e.currentTarget.style.boxShadow = `0 15px 30px ${personality.color}25`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '0.75rem'
              }}>
                <div style={{
                  width: '2.5rem',
                  height: '2.5rem',
                  borderRadius: '50%',
                  background: `linear-gradient(135deg, ${personality.color}, ${personality.darkColor})`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: '600',
                  fontSize: '1rem'
                }}>
                  {personality.name.charAt(0)}
                </div>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '600' }}>{personality.name}</h3>
                  <p style={{ margin: 0, fontSize: '0.8rem', opacity: 0.7 }}>{personality.domain}</p>
                </div>
              </div>
              <p style={{ 
                margin: '0 0 0.75rem 0', 
                fontSize: '0.9rem', 
                lineHeight: '1.4',
                opacity: 0.9,
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}>
                {personality.description}
              </p>
              <div style={{
                fontSize: '0.75rem',
                opacity: 0.6,
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
        padding: '4rem 2rem',
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{
            fontSize: '2.5rem',
            fontWeight: '700',
            textAlign: 'center',
            marginBottom: '3rem',
            textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
          }}>
            Powered by Advanced AI
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1.5rem'
          }}>
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '1rem',
              padding: '2rem',
              textAlign: 'center',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <Brain size={48} style={{ color: '#3b82f6', marginBottom: '1rem' }} />
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Enhanced RAG Service</h3>
              <p style={{ opacity: 0.8, lineHeight: '1.5' }}>
                Advanced Retrieval-Augmented Generation with 25 authentic personalities trained on curated historical texts, providing cited responses grounded in primary sources.
              </p>
            </div>

            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '1rem',
              padding: '2rem',
              textAlign: 'center',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <Shield size={48} style={{ color: '#10b981', marginBottom: '1rem' }} />
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Cross-Session Memory</h3>
              <p style={{ opacity: 0.8, lineHeight: '1.5' }}>
                Enhanced authentication with user persistence ensures your conversations continue seamlessly across sessions with progressive personalization and contextual awareness.
              </p>
            </div>

            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '1rem',
              padding: '2rem',
              textAlign: 'center',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <Sparkles size={48} style={{ color: '#f59e0b', marginBottom: '1rem' }} />
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Database Integration</h3>
              <p style={{ opacity: 0.8, lineHeight: '1.5' }}>
                Azure Cosmos DB integration with user deduplication, conversation persistence, and enhanced citation grounding for transparent source tracking and authentic responses.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: '3rem 2rem 2rem',
        textAlign: 'center',
        borderTop: '1px solid rgba(255, 255, 255, 0.2)',
        background: 'rgba(0, 0, 0, 0.2)',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <div style={{
              width: '2.5rem',
              height: '2.5rem',
              background: 'linear-gradient(135deg, #fbbf24, #f59e0b)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
              fontWeight: 'bold',
              color: 'white',
              border: '2px solid rgba(255, 255, 255, 0.3)'
            }}>
              V
            </div>
            <span style={{ fontSize: '1.5rem', fontWeight: '700' }}>Vimarsh</span>
          </div>
          <p style={{ opacity: 0.7, marginBottom: '1.5rem', maxWidth: '600px', margin: '0 auto 1.5rem' }}>
            Bridging ancient wisdom with modern technology to bring you meaningful conversations with history's greatest minds.
          </p>
          <div style={{ opacity: 0.5, fontSize: '0.875rem' }}>
            © 2025 Vimarsh. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
