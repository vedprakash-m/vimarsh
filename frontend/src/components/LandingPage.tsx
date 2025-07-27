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
    name: 'Lord Krishna',
    domain: 'Spiritual',
    description: 'Divine wisdom from the Bhagavad Gita',
    expertise: 'Dharma, duty, and spiritual enlightenment',
    color: '#4F46E5',
    darkColor: '#3730A3'
  },
  {
    id: 'buddha',
    name: 'Buddha',
    domain: 'Spiritual',
    description: 'Path to liberation from suffering',
    expertise: 'Mindfulness, compassion, and enlightenment',
    color: '#F59E0B',
    darkColor: '#D97706'
  },
  {
    id: 'einstein',
    name: 'Albert Einstein',
    domain: 'Scientific',
    description: 'Revolutionary insights into the universe',
    expertise: 'Physics, mathematics, and scientific thinking',
    color: '#10B981',
    darkColor: '#059669'
  },
  {
    id: 'lincoln',
    name: 'Abraham Lincoln',
    domain: 'Historical',
    description: 'Leadership through moral conviction',
    expertise: 'Governance, unity, and moral leadership',
    color: '#EF4444',
    darkColor: '#DC2626'
  },
  {
    id: 'aurelius',
    name: 'Marcus Aurelius',
    domain: 'Philosophical',
    description: 'Stoic wisdom for life\'s challenges',
    expertise: 'Philosophy, resilience, and inner strength',
    color: '#8B5CF6',
    darkColor: '#7C3AED'
  },
  {
    id: 'jesus',
    name: 'Jesus Christ',
    domain: 'Spiritual',
    description: 'Love, compassion, and spiritual guidance',
    expertise: 'Faith, love, and spiritual transformation',
    color: '#06B6D4',
    darkColor: '#0891B2'
  },
  {
    id: 'rumi',
    name: 'Rumi',
    domain: 'Philosophical',
    description: 'Mystical poetry and divine love',
    expertise: 'Sufism, poetry, and spiritual love',
    color: '#EC4899',
    darkColor: '#DB2777'
  },
  {
    id: 'laotzu',
    name: 'Lao Tzu',
    domain: 'Philosophical',
    description: 'The way of natural harmony',
    expertise: 'Taoism, balance, and natural wisdom',
    color: '#14B8A6',
    darkColor: '#0D9488'
  }
];

const LandingPage: React.FC = () => {
  const { isAuthenticated, account, login } = useAuth();
  const navigate = useNavigate();
  const [selectedPersonality, setSelectedPersonality] = useState(personalities[0]);

  // Redirect authenticated users
  useEffect(() => {
    if (isAuthenticated && account) {
      navigate('/guidance');
    }
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
          Experience authentic conversations with Einstein about scientific discovery, seek spiritual wisdom from Lord Krishna, learn leadership from Lincoln, or explore philosophy with Marcus Aurelius. Each personality grounded in their actual works and teachings.
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
          Secure sign-in with Microsoft to unlock conversations
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
            <div style={{ fontSize: '2.5rem', fontWeight: '700', marginBottom: '0.5rem', textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)' }}>12</div>
            <div style={{ opacity: 0.9, fontSize: '0.95rem', textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)' }}>Great Minds</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: '700', marginBottom: '0.5rem', textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)' }}>4</div>
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
                  {selectedPersonality.id === 'einstein' && 
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
                  {selectedPersonality.id === 'lincoln' && 
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
          marginBottom: '3rem',
          textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
        }}>
          Meet the Great Minds
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.5rem'
        }}>
          {personalities.map((personality) => (
            <div
              key={personality.id}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '1rem',
                padding: '1.5rem',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                transition: 'all 0.3s ease',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-5px)';
                e.currentTarget.style.boxShadow = `0 20px 40px ${personality.color}30`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                marginBottom: '1rem'
              }}>
                <div style={{
                  width: '3.5rem',
                  height: '3.5rem',
                  borderRadius: '50%',
                  background: `linear-gradient(135deg, ${personality.color}, ${personality.darkColor})`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: '600',
                  fontSize: '1.5rem'
                }}>
                  {personality.name.charAt(0)}
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: '600' }}>{personality.name}</h3>
                  <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.7 }}>{personality.domain}</p>
                </div>
              </div>
              <p style={{ 
                margin: '0 0 1rem 0', 
                fontSize: '0.95rem', 
                lineHeight: '1.5',
                opacity: 0.9 
              }}>
                {personality.description}
              </p>
              <div style={{
                fontSize: '0.8rem',
                opacity: 0.7,
                fontStyle: 'italic'
              }}>
                Expertise: {personality.expertise}
              </div>
            </div>
          ))}
        </div>
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
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Authentic Personalities</h3>
              <p style={{ opacity: 0.8, lineHeight: '1.5' }}>
                Each AI personality is trained on authentic texts, speeches, and writings to provide genuine insights and perspectives.
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
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Secure & Private</h3>
              <p style={{ opacity: 0.8, lineHeight: '1.5' }}>
                Enterprise-grade security with Microsoft authentication ensures your conversations remain private and secure.
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
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Continuous Learning</h3>
              <p style={{ opacity: 0.8, lineHeight: '1.5' }}>
                Our AI continuously improves, providing more nuanced and contextual responses with each interaction.
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
