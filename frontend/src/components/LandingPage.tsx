import React, { useState, useEffect } from 'react';
import { ArrowRight, Brain, Shield, Sparkles, Play, Mic, Share2, Bell, Volume2, Heart, Trophy, Zap } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import { WisdomOfDay } from './WisdomOfDay';
import { OnboardingWizard } from './onboarding';
import { onboardingApi } from './onboarding/onboardingApi';

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

  /* Responsive hero layout to ensure the Einstein card is visible on smaller screens */
  .hero-layout {
    display: flex;
    gap: 4rem;
    align-items: flex-start;
    min-height: 500px;
    width: 100%;
  }
  .hero-left {
    width: 50%;
    padding-right: 2rem;
  }
  .hero-right {
    width: 50%;
    padding-left: 2rem;
    position: relative;
    min-height: 420px;
  }
  .hero-right .card-wrapper { position: relative; z-index: 1; }

  @media (max-width: 1024px) {
    .hero-layout { flex-direction: column; gap: 2rem; min-height: unset; }
    .hero-left, .hero-right { width: 100%; padding: 0; }
    .hero-right { min-height: auto; }
    .hero-right .card-wrapper { max-width: 420px; margin: 0 auto; }
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

// Static Einstein Conversation Card (hero preview)
const EinsteinConversationCard: React.FC = () => {
  return (
    <div style={{
      background: '#fff',
      borderRadius: 16,
      padding: 16,
      width: '100%',
      maxWidth: 420,
      border: '1px solid #e5e7eb',
      boxShadow: '0 10px 30px rgba(0,0,0,0.08)'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            border: '2px solid #34c759',
            color: '#34c759',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700
          }}>E</div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 13, color: '#111827' }}>Albert Einstein</div>
            <div style={{ fontSize: 11, color: '#6b7280' }}>Theoretical Physicist • Nobel Laureate</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#64748b' }}>
          <span style={{ background: '#e5e7eb', borderRadius: 9999, padding: '2px 8px' }}>Live</span>
        </div>
      </div>

      {/* User prompt */}
      <div style={{
        background: '#f9fafb',
        border: '1px solid #e5e7eb',
        borderRadius: 10,
        padding: '10px 12px',
        fontSize: 13,
        color: '#111827',
        marginBottom: 10
      }}>
        Problem: what was your biggest mistake while developing relativity?
      </div>

      {/* AI response */}
      <div style={{
        background: '#ffffff',
        border: '1px solid #e5e7eb',
        borderRadius: 10,
        padding: '12px 12px',
        fontSize: 13,
        color: '#334155',
        lineHeight: 1.5,
        boxShadow: '0 1px 2px rgba(0,0,0,0.03)'
      }}>
        I tried to force a static universe by adding the cosmological constant. Later observations showed the universe is expanding, and I called that addition my “biggest blunder.” The lesson: let evidence guide the equations, not preference.
      </div>

      {/* Memory indicator */}
      <div style={{
        marginTop: 12,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 6,
        padding: '6px 10px',
        background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
        borderRadius: 8,
        border: '1px solid #bae6fd'
      }}>
        <Heart size={12} style={{ color: '#0ea5e9', fill: '#0ea5e9' }} />
        <span style={{ fontSize: 11, color: '#0369a1', fontWeight: 500 }}>Remembers your journey across sessions</span>
      </div>
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
  const location = useLocation();
  const [selectedDomain, setSelectedDomain] = useState('All');
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [onboardingChecked, setOnboardingChecked] = useState(false);

  // Helper function to filter personalities by domain
  const getFilteredPersonalities = () => {
    if (selectedDomain === 'All') {
      return personalities;
    }
    return personalities.filter(p => p.domain === selectedDomain);
  };

  // Check onboarding status for authenticated users
  useEffect(() => {
    const checkOnboardingStatus = async () => {
      if (isAuthenticated && account && !onboardingChecked) {
        try {
          const state = await onboardingApi.getOnboardingState(account.homeAccountId);
          // Show onboarding wizard if not completed
          if (state && !state.is_complete) {
            setShowOnboarding(true);
          }
          setOnboardingChecked(true);
        } catch (error) {
          console.log('📋 Onboarding check skipped (new user or service unavailable)');
          // For new users, show onboarding wizard
          setShowOnboarding(true);
          setOnboardingChecked(true);
        }
      }
    };
    
    checkOnboardingStatus();
  }, [isAuthenticated, account, onboardingChecked]);

  // Handle onboarding completion
  const handleOnboardingComplete = (personalityId?: string) => {
    setShowOnboarding(false);
    if (personalityId) {
      // Navigate to guidance with the matched personality
      navigate(`/guidance?personality=${personalityId}`);
    } else {
      navigate('/guidance');
    }
  };

  // Redirect authenticated users - with protection against circular redirects
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    // Allow preview of landing page even when authenticated
    const params = new URLSearchParams(location.search);
    const isPreview = params.get('preview') === '1' || params.get('preview') === 'true';

    if (isAuthenticated && account && !isPreview) {
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
  }, [isAuthenticated, account, navigate, location.search]);

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
      {/* Root CSS variables */}
      <style>{cssVariables}</style>
      {/* Header */}
      <header style={{ background: '#ffffff', borderBottom: '1px solid #f3f4f6' }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '1rem 2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '1.5rem',
              height: '1.5rem',
              background: '#f97316',
              borderRadius: '50%'
            }} />
            <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600, color: '#1d1d1f' }}>Vimarsh</h1>
          </div>
          <nav style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <a href="#personalities" style={{ color: '#1d1d1f', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500 }}>Personalities</a>
            <a href="#features" style={{ color: '#1d1d1f', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500 }}>Features</a>
            <button
              onClick={handleBeginJourney}
              style={{
                background: 'linear-gradient(135deg, #f97316, #f59e0b)',
                border: 'none',
                color: 'white',
                padding: '0.6rem 1.25rem',
                borderRadius: '1.5rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.85rem',
                fontWeight: 600,
                transition: 'all 0.3s ease',
                boxShadow: '0 6px 18px rgba(249, 115, 22, 0.35)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 10px 24px rgba(249, 115, 22, 0.45)';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = '0 6px 18px rgba(249, 115, 22, 0.35)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              Sign In / Sign Up
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section style={{
        padding: '4rem 2rem',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div className="hero-layout">
          {/* Left side - Text content */}
          <div className="hero-left">
            {/* Badge */}
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: 'linear-gradient(135deg, #fff7ed 0%, #fef3c7 100%)',
              color: '#9a3412',
              border: '1px solid #fed7aa',
              padding: '0.35rem 0.75rem',
              borderRadius: '9999px',
              fontSize: '0.8rem',
              fontWeight: 500,
              marginBottom: '0.75rem'
            }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#f97316', display: 'inline-block', animation: 'pulse 2s infinite' }} />
              NEW: World-Class Memory • Voice • Social Sharing • Daily Wisdom
            </div>
            <h1 style={{
              fontSize: '3rem',
              fontWeight: '600',
              marginBottom: '1.25rem',
              color: '#1d1d1f',
              lineHeight: '1.2'
            }}>
              Converse with History's <br />
              <span style={{
                background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                WebkitBackgroundClip: 'text',
                backgroundClip: 'text',
                color: 'transparent',
                fontWeight: 700
              }}>Greatest Minds</span>
            </h1>

            <p style={{
              fontSize: '1.125rem',
              color: '#6b7280',
              marginBottom: '2rem',
              lineHeight: '1.6'
            }}>
              Ask Einstein about his failures. Challenge Gandhi’s philosophy. Learn creativity from Shakespeare. Experience authentic, evolving conversations that span domains and deepen over time.
            </p>

            <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
              <button
                onClick={handleBeginJourney}
                style={{
                  background: 'linear-gradient(135deg, #f97316, #f59e0b)',
                  color: '#ffffff',
                  border: 'none',
                  padding: '0.875rem 1.25rem',
                  fontSize: '1rem',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  fontWeight: 600,
                  boxShadow: '0 6px 18px rgba(249, 115, 22, 0.35)',
                  transition: 'all 0.2s ease',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = '0 10px 24px rgba(249, 115, 22, 0.45)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 6px 18px rgba(249, 115, 22, 0.35)';
                }}
                aria-label="Begin your journey"
              >
                Begin Your Journey
                <ArrowRight size={18} />
              </button>
              <button
                onClick={handleBeginJourney}
                style={{
                  background: 'white',
                  border: '1px solid #e5e7eb',
                  color: '#1f2937',
                  padding: '0.875rem 1.25rem',
                  fontSize: '1rem',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  fontWeight: 500,
                  transition: 'all 0.2s ease',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = '#f9fafb';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.06)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'white';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <Play size={18} />
                Watch the Magic
              </button>
            </div>

      {/* Stats with memory highlight */}
            <div style={{
              display: 'flex',
              gap: '2.5rem',
              alignItems: 'center',
              flexWrap: 'wrap'
            }}>
              <div>
        <div style={{ fontSize: '2rem', fontWeight: 600, color: '#1d1d1f' }}>25</div>
        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Great minds</div>
              </div>
              <div>
        <div style={{ fontSize: '2rem', fontWeight: 600, color: '#1d1d1f' }}>6</div>
        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Domains</div>
              </div>
              <div>
        <div style={{ fontSize: '2rem', fontWeight: 600, color: '#1d1d1f' }}>1000+</div>
        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Ancient texts</div>
              </div>
              <div>
        <div style={{ fontSize: '2rem', fontWeight: 600, color: '#1d1d1f', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          <Heart size={20} style={{ color: '#ec4899', fill: '#ec4899' }} /> ∞
        </div>
        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Memory</div>
              </div>
            </div>
          </div>

          {/* Right side - Conversation Card with colorful halo */}
          <div className="hero-right">
            {/* Ambient gradient blobs */}
            <div style={{
              position: 'absolute',
              top: 0,
              right: 0,
              width: '80%',
              height: '80%',
              background: 'radial-gradient(600px circle at 75% 25%, rgba(249,115,22,0.22), rgba(124,58,237,0.16), transparent 60%)',
              filter: 'blur(10px)',
              zIndex: 0
            }} />
            <div style={{
              position: 'absolute',
              bottom: 0,
              left: '10%',
              width: 260,
              height: 160,
              background: 'radial-gradient(closest-side, rgba(37,99,235,0.14), transparent)',
              filter: 'blur(25px)',
              zIndex: 0
            }} />
            <div className="card-wrapper">
              <EinsteinConversationCard />
            </div>
          </div>
        </div>
      </section>

      {/* Wisdom of the Day Section */}
      <section style={{
        padding: '2rem 2rem 3rem',
        maxWidth: '800px',
        margin: '0 auto',
        textAlign: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <h2 style={{ 
            fontSize: '1.5rem', 
            fontWeight: 600, 
            color: '#1d1d1f',
            margin: 0
          }}>
            Today's Wisdom
          </h2>
          <span style={{
            background: '#fef3c7',
            color: '#92400e',
            fontSize: '0.65rem',
            fontWeight: 600,
            padding: '2px 6px',
            borderRadius: 4,
            textTransform: 'uppercase'
          }}>New</span>
        </div>
        <p style={{ 
          color: '#6b7280', 
          marginBottom: '0.75rem', 
          fontSize: '0.9rem' 
        }}>
          A daily dose of timeless insight from history's greatest minds
        </p>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          gap: '0.5rem',
          marginBottom: '1.5rem',
          fontSize: '0.8rem',
          color: '#6b7280'
        }}>
          <Bell size={14} style={{ color: '#f97316' }} />
          <span>Get daily wisdom notifications</span>
        </div>
        <WisdomOfDay />
      </section>

      {/* Start Your Journey */}
      <section style={{
        padding: '2rem 2rem 0',
        maxWidth: '1200px',
        margin: '0 auto',
        textAlign: 'center'
      }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: 6, color: '#1d1d1f' }}>Start Your Journey</h2>
        <p style={{ color: '#6b7280', marginBottom: '1.25rem', fontSize: 13 }}>
          Begin with these intro cards, each offering unique wisdom from their life’s work.
        </p>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1rem'
        }}>
          {[
            { name: 'Albert Einstein', domain: 'Scientific', color: '#34c759', cta: 'Discuss curiosity' },
            { name: 'Mahatma Gandhi', domain: 'Leadership', color: '#ff3b30', cta: 'Discuss leadership' },
            { name: 'Socrates', domain: 'Philosophical', color: '#5856d6', cta: 'Explore dialogue' },
            { name: 'William Shakespeare', domain: 'Literary', color: '#af52de', cta: 'Discuss creativity' }
          ].map((p) => (
            <div key={p.name} style={{
              background: '#ffffff',
              borderRadius: 12,
              padding: 16,
              border: '1px solid #e5e7eb',
              boxShadow: '0 2px 10px rgba(0,0,0,0.04)',
              transition: 'all .2s ease',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 8px 20px rgba(0,0,0,0.08)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 2px 10px rgba(0,0,0,0.04)';
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: 8 }}>
                <div style={{
                  width: 36,
                  height: 36,
                  borderRadius: '50%',
                  border: `2px solid ${p.color}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: p.color,
                  fontWeight: 700
                }}>{p.name.charAt(0)}</div>
                <div>
                  <div style={{ fontWeight: 600, color: '#111827' }}>{p.name}</div>
                  <div style={{ fontSize: 12, color: '#6b7280' }}>{p.domain}</div>
                </div>
              </div>
              <button style={{
                border: '1px solid #e5e7eb',
                background: '#fff',
                color: '#1f2937',
                padding: '6px 10px',
                borderRadius: 20,
                fontSize: 12,
                fontWeight: 500
              }}
              onClick={handleBeginJourney}
              >{p.cta} →</button>
            </div>
          ))}
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

        {/* View all link to match screenshot */}
        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <a
            href="#personalities"
            onClick={(e) => { e.preventDefault(); /* no-op for now */ }}
            style={{ color: '#2563eb', fontSize: 14, textDecoration: 'none' }}
            onMouseEnter={(e) => { e.currentTarget.style.textDecoration = 'underline'; }}
            onMouseLeave={(e) => { e.currentTarget.style.textDecoration = 'none'; }}
          >
            View all Great Minds →
          </a>
        </div>
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
            {/* Voice Conversations - NEW */}
            <div style={{
              background: 'linear-gradient(135deg, #fef3c7 0%, #fff 100%)',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              textAlign: 'center',
              border: '1px solid #fcd34d',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
              position: 'relative'
            }}>
              <span style={{
                position: 'absolute',
                top: 12,
                right: 12,
                background: '#f97316',
                color: 'white',
                fontSize: '0.6rem',
                fontWeight: 700,
                padding: '2px 6px',
                borderRadius: 4,
                textTransform: 'uppercase'
              }}>New</span>
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
                <Mic size={24} style={{ color: 'white' }} />
              </div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.75rem', color: '#1f2937' }}>Speak, Don't Type</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.5', fontSize: '0.9rem' }}>
                Have natural voice conversations with Einstein, Gandhi, or any of our 25 minds. Ask questions by speaking and hear their wisdom read aloud in their unique voice.
              </p>
            </div>

            {/* Share Wisdom - NEW */}
            <div style={{
              background: 'linear-gradient(135deg, #dbeafe 0%, #fff 100%)',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              textAlign: 'center',
              border: '1px solid #93c5fd',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
              position: 'relative'
            }}>
              <span style={{
                position: 'absolute',
                top: 12,
                right: 12,
                background: '#3b82f6',
                color: 'white',
                fontSize: '0.6rem',
                fontWeight: 700,
                padding: '2px 6px',
                borderRadius: 4,
                textTransform: 'uppercase'
              }}>New</span>
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
                <Share2 size={24} style={{ color: 'white' }} />
              </div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.75rem', color: '#1f2937' }}>Share the Wisdom</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.5', fontSize: '0.9rem' }}>
                Found a profound insight? Share it instantly on Twitter, LinkedIn, WhatsApp, or any platform. Spread timeless wisdom with beautiful, auto-generated social cards.
              </p>
            </div>

            {/* Daily Wisdom - NEW */}
            <div style={{
              background: 'linear-gradient(135deg, #dcfce7 0%, #fff 100%)',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              textAlign: 'center',
              border: '1px solid #86efac',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
              position: 'relative'
            }}>
              <span style={{
                position: 'absolute',
                top: 12,
                right: 12,
                background: '#10b981',
                color: 'white',
                fontSize: '0.6rem',
                fontWeight: 700,
                padding: '2px 6px',
                borderRadius: 4,
                textTransform: 'uppercase'
              }}>New</span>
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
                <Bell size={24} style={{ color: 'white' }} />
              </div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.75rem', color: '#1f2937' }}>Daily Wisdom Delivered</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.5', fontSize: '0.9rem' }}>
                Start each day inspired. Get a curated insight from a different great mind every morning, with push notifications at your preferred time.
              </p>
            </div>
          </div>

          {/* Original features in second row */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '1.25rem',
            marginTop: '1.25rem'
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
                background: '#8b5cf6',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
              }}>
                <Brain size={24} style={{ color: 'white' }} />
              </div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.75rem', color: '#1f2937' }}>Authentic Thinking</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.5', fontSize: '0.9rem' }}>
                Each personality draws from their authentic writings and works. They engage with your questions using their actual thought patterns.
              </p>
            </div>

            <div style={{
              background: 'linear-gradient(135deg, #fdf2f8 0%, #fce7f3 50%, #fff 100%)',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              textAlign: 'center',
              border: '1px solid #f9a8d4',
              boxShadow: '0 4px 12px rgba(236, 72, 153, 0.12)',
              position: 'relative'
            }}>
              <span style={{
                position: 'absolute',
                top: 12,
                right: 12,
                background: 'linear-gradient(135deg, #ec4899, #be185d)',
                color: 'white',
                fontSize: '0.6rem',
                fontWeight: 700,
                padding: '2px 6px',
                borderRadius: 4,
                textTransform: 'uppercase'
              }}>Enhanced</span>
              <div style={{
                width: '3rem',
                height: '3rem',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #ec4899, #be185d)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
                boxShadow: '0 4px 12px rgba(236, 72, 153, 0.3)'
              }}>
                <Heart size={24} style={{ color: 'white', fill: 'white' }} />
              </div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem', color: '#1f2937' }}>World-Class Memory</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.5', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                4-layer hierarchical memory inspired by Stanford & Berkeley research. They remember your journey, celebrate milestones, and proactively recall past wisdom.
              </p>
              <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.7rem', background: '#fce7f3', color: '#be185d', padding: '2px 8px', borderRadius: 12 }}>🏆 Milestones</span>
                <span style={{ fontSize: '0.7rem', background: '#fce7f3', color: '#be185d', padding: '2px 8px', borderRadius: 12 }}>🔮 Proactive Recall</span>
                <span style={{ fontSize: '0.7rem', background: '#fce7f3', color: '#be185d', padding: '2px 8px', borderRadius: 12 }}>📊 Analytics</span>
              </div>
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
                background: '#06b6d4',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
              }}>
                <Sparkles size={24} style={{ color: 'white' }} />
              </div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.75rem', color: '#1f2937' }}>1000+ Ancient Texts</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.5', fontSize: '0.9rem' }}>
                Access thousands of years of human wisdom. Strategic advice from Chanakya, spiritual guidance from Buddha, or scientific insights from Newton.
              </p>
            </div>
          </div>

          <div style={{ marginTop: '2rem' }}>
            <button
              onClick={handleBeginJourney}
              style={{
                background: 'linear-gradient(135deg, #f97316, #f59e0b)',
                color: 'white',
                border: 'none',
                padding: '12px 20px',
                fontSize: 16,
                borderRadius: 9999,
                cursor: 'pointer',
                fontWeight: 600,
                boxShadow: '0 8px 24px rgba(249, 115, 22, 0.35)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 12px 28px rgba(249, 115, 22, 0.45)';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(249, 115, 22, 0.35)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              Experience This for Yourself
            </button>
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

      {/* Onboarding Wizard for New Users */}
      {showOnboarding && account && (
        <OnboardingWizard
          open={showOnboarding}
          onClose={() => setShowOnboarding(false)}
          userId={account.homeAccountId}
          userName={account.name}
          onSelectPersonality={handleOnboardingComplete}
        />
      )}
    </div>
  );
};

export default LandingPage;
 