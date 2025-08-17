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
      background: 'linear-gradient(to bottom, #fafafa 0%, #ffffff 50%)',
      color: '#1d1d1f',
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    }}>
      {/* Header */}
      <header style={{
        padding: '0.75rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: '#fafafa',
        borderBottom: '1px solid #f0f0f0'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '3.5rem',
            height: '3.5rem',
            background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '2rem',
            fontWeight: 'bold',
            color: 'white',
            border: '2px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)'
          }}>
            V
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '600', color: '#1d1d1f' }}>Vimarsh</h1>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#8b8b8b' }}>Wisdom Without Boundaries</p>
          </div>
        </div>
        <nav style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <a href="#personalities" style={{ color: '#6b7280', textDecoration: 'none', fontSize: '0.9rem', fontWeight: '500' }}>Personalities</a>
          <a href="#features" style={{ color: '#6b7280', textDecoration: 'none', fontSize: '0.9rem', fontWeight: '500' }}>Features</a>
          <button
            onClick={handleBeginJourney}
            style={{
              background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
              border: 'none',
              color: 'white',
              padding: '0.6rem 1.25rem',
              borderRadius: '0.75rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontSize: '0.85rem',
              fontWeight: '500',
              transition: 'all 0.3s ease',
              boxShadow: '0 2px 8px rgba(99, 102, 241, 0.25)'
            }}
          >
            Begin Journey <ArrowRight size={14} />
          </button>
        </nav>
      </header>

      {/* Hero Section */}
      <section style={{
        padding: '4rem 2rem',
        textAlign: 'center',
        maxWidth: '1000px',
        margin: '2rem auto 4rem'
      }}>
        <h1 style={{
          fontSize: '2.75rem',
          fontWeight: '600',
          marginBottom: '1.25rem',
          color: '#1d1d1f',
          lineHeight: '1.2'
        }}>
          Converse with<br />
          History's{' '}
          <span style={{
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: '700'
          }}>
            Greatest Minds
          </span>
        </h1>

        <p style={{
          fontSize: '1.125rem',
          color: '#6b7280',
          maxWidth: '700px',
          margin: '0 auto 2.5rem',
          lineHeight: '1.6'
        }}>
          Experience authentic conversations with 25 distinct personalities across 6 domains - from Einstein about scientific discovery to Krishna for spiritual wisdom, Lincoln for leadership, or Marcus Aurelius for philosophy.
        </p>

        <button
          onClick={handleBeginJourney}
          style={{
            background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
            color: 'white',
            border: 'none',
            padding: '0.875rem 2rem',
            fontSize: '1rem',
            borderRadius: '0.75rem',
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontWeight: '500',
            boxShadow: '0 8px 20px rgba(99, 102, 241, 0.3)',
            transition: 'all 0.3s ease',
            marginBottom: '0.75rem'
          }}
        >
          Start Your Journey
        </button>

        <p style={{ fontSize: '0.85rem', color: '#9ca3af', margin: 0 }}>
          Secure sign-in with Microsoft to unlock persistent conversations
        </p>

        {/* Stats */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: '1.5rem',
          marginTop: '4rem',
          padding: '0'
        }}>
          <div style={{ textAlign: 'center', background: 'rgba(255, 255, 255, 0.8)', padding: '1.5rem 1rem', borderRadius: '1rem', boxShadow: '0 2px 8px rgba(0,0,0,0.06)', border: '1px solid rgba(255, 255, 255, 0.2)' }}>
            <div style={{ fontSize: '2rem', fontWeight: '600', marginBottom: '0.25rem', color: '#1d1d1f' }}>25</div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Great Minds</div>
          </div>
          <div style={{ textAlign: 'center', background: 'rgba(255, 255, 255, 0.8)', padding: '1.5rem 1rem', borderRadius: '1rem', boxShadow: '0 2px 8px rgba(0,0,0,0.06)', border: '1px solid rgba(255, 255, 255, 0.2)' }}>
            <div style={{ fontSize: '2rem', fontWeight: '600', marginBottom: '0.25rem', color: '#1d1d1f' }}>6</div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Domains</div>
          </div>
          <div style={{ textAlign: 'center', background: 'rgba(255, 255, 255, 0.8)', padding: '1.5rem 1rem', borderRadius: '1rem', boxShadow: '0 2px 8px rgba(0,0,0,0.06)', border: '1px solid rgba(255, 255, 255, 0.2)' }}>
            <div style={{ fontSize: '2rem', fontWeight: '600', marginBottom: '0.25rem', color: '#1d1d1f' }}>1000+</div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Authentic Texts</div>
          </div>
          <div style={{ textAlign: 'center', background: 'rgba(255, 255, 255, 0.8)', padding: '1.5rem 1rem', borderRadius: '1rem', boxShadow: '0 2px 8px rgba(0,0,0,0.06)', border: '1px solid rgba(255, 255, 255, 0.2)' }}>
            <div style={{ fontSize: '2rem', fontWeight: '600', marginBottom: '0.25rem', color: '#1d1d1f' }}>Deep</div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Insights</div>
          </div>
        </div>
      </section>

      {/* Interactive Demo */}
      <section style={{
        padding: '4rem 2rem',
        maxWidth: '1000px',
        margin: '4rem auto'
      }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <h2 style={{
            fontSize: '2.25rem',
            fontWeight: '600',
            textAlign: 'center',
            marginBottom: '3rem',
            color: '#1d1d1f'
          }}>
            Start Your Journey
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '2.5rem',
            alignItems: 'center'
          }}>
            {/* Personality Selector Grid */}
            <div>
              <h3 style={{ fontSize: '1.125rem', marginBottom: '1.5rem', fontWeight: '600', color: '#374151' }}>Choose a Great Mind</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                {personalities.slice(0, 4).map((personality) => (
                  <button
                    key={personality.id}
                    onClick={() => setSelectedPersonality(personality)}
                    style={{
                      background: selectedPersonality.id === personality.id 
                        ? '#6366f1'
                        : '#ffffff',
                      border: selectedPersonality.id === personality.id 
                        ? 'none'
                        : '1px solid #e5e7eb',
                      color: selectedPersonality.id === personality.id ? '#ffffff' : '#1f2937',
                      padding: '1.25rem',
                      borderRadius: '0.75rem',
                      cursor: 'pointer',
                      textAlign: 'center',
                      transition: 'all 0.3s ease',
                      boxShadow: selectedPersonality.id === personality.id 
                        ? '0 4px 12px rgba(99, 102, 241, 0.25)'
                        : '0 1px 3px rgba(0, 0, 0, 0.1)',
                      transform: selectedPersonality.id === personality.id ? 'translateY(-1px)' : 'none'
                    }}>
                    <div style={{ 
                      fontWeight: '600', 
                      fontSize: '0.9rem',
                      marginBottom: '0.25rem' 
                    }}>
                      {personality.name}
                    </div>
                    <div style={{ 
                      fontSize: '0.75rem', 
                      opacity: selectedPersonality.id === personality.id ? 0.9 : 0.7 
                    }}>
                      {personality.domain}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Demo Conversation */}
            <div style={{
              background: 'white',
              borderRadius: '1rem',
              padding: '1.5rem',
              boxShadow: '0 2px 10px rgba(0,0,0,0.08)',
              border: '1px solid #f0f0f0'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '1.25rem',
                paddingBottom: '0.75rem',
                borderBottom: '1px solid #f3f4f6'
              }}>
                <div style={{
                  width: '2.5rem',
                  height: '2.5rem',
                  borderRadius: '50%',
                  background: '#f8fafc',
                  border: `2px solid ${domainColors[selectedPersonality.domain as keyof typeof domainColors] || '#6b7280'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: domainColors[selectedPersonality.domain as keyof typeof domainColors] || '#6b7280',
                  fontWeight: '600',
                  fontSize: '1rem'
                }}>
                  {selectedPersonality.name.charAt(0)}
                </div>
                <div>
                  <div style={{ fontWeight: '600', fontSize: '1rem', color: '#1f2937' }}>{selectedPersonality.name}</div>
                  <div style={{ color: '#6b7280', fontSize: '0.8rem' }}>{selectedPersonality.domain} Wisdom</div>
                </div>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <div style={{
                  background: '#f3f4f6',
                  padding: '0.75rem 1rem',
                  borderRadius: '1rem 1rem 1rem 0.25rem',
                  marginBottom: '0.75rem',
                  fontSize: '0.9rem',
                  color: '#1f2937'
                }}>
                  How can I find peace in difficult times?
                </div>

                <div style={{
                  background: '#ffffff',
                  border: '1px solid #e5e7eb',
                  padding: '1rem',
                  borderRadius: '1rem 1rem 0.25rem 1rem',
                  fontSize: '0.9rem',
                  lineHeight: '1.5',
                  color: '#1f2937',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
                }}>
                  {(() => {
                    const responses = {
                      krishna: "True peace comes from understanding your dharma - your righteous duty. When you act without attachment to results, performing your duty with devotion, the mind finds its natural state of tranquility.",
                      buddha: "Suffering arises from attachment and desire. Practice mindfulness, observe your thoughts without judgment, and remember that all difficult times are impermanent - this too shall pass.",
                      jesus_christ: "Come unto me, all ye that labor and are heavy laden, and I will give you rest. Find peace through faith, love for others, and trust in divine providence.",
                      albert_einstein: "In the midst of difficulty lies opportunity. Peace comes from understanding that we are part of something greater than ourselves - the magnificent cosmos that operates by natural laws."
                    };
                    return responses[selectedPersonality.id as keyof typeof responses] || responses.krishna;
                  })()}
                </div>
              </div>

              <div style={{
                fontSize: '0.75rem',
                color: '#9ca3af',
                fontStyle: 'italic',
                textAlign: 'center'
              }}>
                Response based on authentic {selectedPersonality.expertise}
              </div>
            </div>
          </div>
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
                  ? '#6366f1'
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
                boxShadow: selectedDomain === domain ? '0 2px 8px rgba(99, 102, 241, 0.25)' : '0 1px 3px rgba(0, 0, 0, 0.05)'
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
              background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
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
