/**
 * ShareView - Public Share Landing Page
 * 
 * Displays shared wisdom with personality attribution.
 * Provides CTA for users to start their own conversation.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowRight, MessageCircle, Sparkles, Share2, Copy, Check } from 'lucide-react';
import { getApiBaseUrl } from '../config/environment';

interface SharedWisdom {
  id: string;
  text: string;
  personality_id: string;
  personality_name: string;
  domain: string;
  citation?: string;
  shared_at: string;
  share_count: number;
}

// Domain-specific colors
const getDomainColors = (domain: string) => {
  const colorMap: Record<string, { bg: string; border: string; text: string; gradient: string; accent: string }> = {
    spiritual: {
      bg: 'rgba(255, 107, 53, 0.08)',
      border: 'rgba(255, 107, 53, 0.3)',
      text: '#ea580c',
      gradient: 'linear-gradient(135deg, #FF6B35, #F7931E)',
      accent: '#FF6B35'
    },
    scientific: {
      bg: 'rgba(59, 130, 246, 0.08)',
      border: 'rgba(59, 130, 246, 0.3)',
      text: '#2563eb',
      gradient: 'linear-gradient(135deg, #3B82F6, #1D4ED8)',
      accent: '#3B82F6'
    },
    philosophical: {
      bg: 'rgba(147, 51, 234, 0.08)',
      border: 'rgba(147, 51, 234, 0.3)',
      text: '#9333ea',
      gradient: 'linear-gradient(135deg, #9333EA, #7C3AED)',
      accent: '#9333EA'
    },
    historical: {
      bg: 'rgba(34, 197, 94, 0.08)',
      border: 'rgba(34, 197, 94, 0.3)',
      text: '#16a34a',
      gradient: 'linear-gradient(135deg, #22C55E, #16A34A)',
      accent: '#22C55E'
    },
    leadership: {
      bg: 'rgba(239, 68, 68, 0.08)',
      border: 'rgba(239, 68, 68, 0.3)',
      text: '#dc2626',
      gradient: 'linear-gradient(135deg, #EF4444, #DC2626)',
      accent: '#EF4444'
    },
    literary: {
      bg: 'rgba(16, 185, 129, 0.08)',
      border: 'rgba(16, 185, 129, 0.3)',
      text: '#059669',
      gradient: 'linear-gradient(135deg, #10B981, #059669)',
      accent: '#10B981'
    },
    psychology: {
      bg: 'rgba(139, 92, 246, 0.08)',
      border: 'rgba(139, 92, 246, 0.3)',
      text: '#8b5cf6',
      gradient: 'linear-gradient(135deg, #8B5CF6, #7C3AED)',
      accent: '#8B5CF6'
    }
  };
  
  return colorMap[domain] || colorMap.spiritual;
};

// Domain icons
const getDomainIcon = (domain: string): string => {
  const icons: Record<string, string> = {
    spiritual: '🙏',
    scientific: '🔬',
    philosophical: '🤔',
    historical: '📜',
    leadership: '👑',
    literary: '📚',
    psychology: '🧠'
  };
  return icons[domain] || '✨';
};

// Static fallback wisdom for demo/testing
const FALLBACK_WISDOM: SharedWisdom = {
  id: 'demo',
  text: 'The unexamined life is not worth living. To find yourself, think for yourself.',
  personality_id: 'socrates',
  personality_name: 'Socrates',
  domain: 'philosophical',
  citation: 'Apology of Socrates',
  shared_at: new Date().toISOString(),
  share_count: 42
};

const ShareView: React.FC = () => {
  const { shareId } = useParams<{ shareId: string }>();
  const navigate = useNavigate();
  
  const [wisdom, setWisdom] = useState<SharedWisdom | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSharedWisdom = async () => {
      if (!shareId) {
        setWisdom(FALLBACK_WISDOM);
        setLoading(false);
        return;
      }

      try {
        const apiUrl = getApiBaseUrl();
        const response = await fetch(`${apiUrl}/share/${shareId}`);
        
        if (response.ok) {
          const data = await response.json();
          setWisdom(data);
        } else {
          // Use fallback for demo purposes
          setWisdom(FALLBACK_WISDOM);
        }
      } catch (err) {
        console.error('Error fetching shared wisdom:', err);
        setWisdom(FALLBACK_WISDOM);
      } finally {
        setLoading(false);
      }
    };

    fetchSharedWisdom();
  }, [shareId]);

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Copy failed:', err);
    }
  };

  const handleStartConversation = () => {
    if (wisdom) {
      // Navigate to guidance with personality pre-selected
      navigate(`/guidance?personality=${wisdom.personality_id}`);
    } else {
      navigate('/guidance');
    }
  };

  const handleExploreMore = () => {
    navigate('/');
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #FFF8E1 0%, #FFE0B2 100%)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            display: 'flex',
            gap: '0.5rem',
            justifyContent: 'center',
            marginBottom: '1rem'
          }}>
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                style={{
                  width: '12px',
                  height: '12px',
                  background: '#FF6B35',
                  borderRadius: '50%',
                  animation: `pulse 1.5s ease-in-out ${i * 0.2}s infinite`
                }}
              />
            ))}
          </div>
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>Loading wisdom...</p>
        </div>
        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 0.4; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
          }
        `}</style>
      </div>
    );
  }

  if (!wisdom) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #FFF8E1 0%, #FFE0B2 100%)',
        padding: '2rem'
      }}>
        <div style={{
          textAlign: 'center',
          maxWidth: '400px'
        }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🔍</div>
          <h1 style={{ fontSize: '1.5rem', color: '#1e293b', marginBottom: '0.5rem' }}>
            Wisdom Not Found
          </h1>
          <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>
            This shared wisdom may have expired or doesn't exist.
          </p>
          <button
            onClick={handleExploreMore}
            style={{
              background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
              color: 'white',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.75rem',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: '600',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            Explore Vimarsh
            <ArrowRight size={18} />
          </button>
        </div>
      </div>
    );
  }

  const colors = getDomainColors(wisdom.domain);
  const domainIcon = getDomainIcon(wisdom.domain);

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #FFF8E1 0%, #FFE0B2 100%)',
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    }}>
      {/* Header */}
      <header style={{
        background: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(0, 0, 0, 0.05)',
        padding: '1rem 2rem',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{
          maxWidth: '800px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.75rem',
              cursor: 'pointer'
            }}
            onClick={handleExploreMore}
          >
            <div style={{
              width: '32px',
              height: '32px',
              background: colors.gradient,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Sparkles size={16} color="white" />
            </div>
            <span style={{ 
              fontSize: '1.25rem', 
              fontWeight: '600',
              color: '#1e293b'
            }}>
              Vimarsh
            </span>
          </div>
          
          <button
            onClick={handleCopyLink}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: copied ? '#22c55e' : 'transparent',
              border: `1px solid ${copied ? '#22c55e' : '#e2e8f0'}`,
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              color: copied ? 'white' : '#64748b',
              fontSize: '0.875rem',
              transition: 'all 0.2s ease'
            }}
          >
            {copied ? <Check size={16} /> : <Copy size={16} />}
            {copied ? 'Copied!' : 'Copy Link'}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '800px',
        margin: '0 auto',
        padding: '3rem 1.5rem'
      }}>
        {/* Wisdom Card */}
        <div style={{
          background: 'white',
          borderRadius: '1.5rem',
          padding: '2.5rem',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.08)',
          border: `2px solid ${colors.border}`,
          marginBottom: '2rem'
        }}>
          {/* Domain Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: colors.bg,
            padding: '0.5rem 1rem',
            borderRadius: '2rem',
            marginBottom: '1.5rem'
          }}>
            <span>{domainIcon}</span>
            <span style={{
              fontSize: '0.875rem',
              fontWeight: '500',
              color: colors.text,
              textTransform: 'capitalize'
            }}>
              {wisdom.domain} Wisdom
            </span>
          </div>

          {/* Quote */}
          <blockquote style={{
            fontSize: '1.5rem',
            lineHeight: '1.6',
            color: '#1e293b',
            margin: '0 0 1.5rem 0',
            fontStyle: 'italic',
            position: 'relative',
            paddingLeft: '1.5rem',
            borderLeft: `4px solid ${colors.accent}`
          }}>
            "{wisdom.text}"
          </blockquote>

          {/* Attribution */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem'
          }}>
            <div>
              <p style={{
                fontSize: '1.125rem',
                fontWeight: '600',
                color: colors.text,
                margin: '0 0 0.25rem 0'
              }}>
                — {wisdom.personality_name}
              </p>
              {wisdom.citation && (
                <p style={{
                  fontSize: '0.875rem',
                  color: '#64748b',
                  margin: 0
                }}>
                  {wisdom.citation}
                </p>
              )}
            </div>
            
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: '#94a3b8',
              fontSize: '0.875rem'
            }}>
              <Share2 size={14} />
              <span>{wisdom.share_count || 0} shares</span>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div style={{
          background: 'white',
          borderRadius: '1.5rem',
          padding: '2rem',
          textAlign: 'center',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: '600',
            color: '#1e293b',
            marginBottom: '0.75rem'
          }}>
            Want more wisdom from {wisdom.personality_name}?
          </h2>
          <p style={{
            color: '#64748b',
            marginBottom: '1.5rem',
            fontSize: '1rem'
          }}>
            Start your own conversation and explore insights from 25 legendary minds.
          </p>
          
          <div style={{
            display: 'flex',
            gap: '1rem',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={handleStartConversation}
              style={{
                background: colors.gradient,
                color: 'white',
                border: 'none',
                padding: '1rem 2rem',
                borderRadius: '0.75rem',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '600',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                boxShadow: `0 4px 15px ${colors.accent}40`,
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = `0 8px 25px ${colors.accent}50`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = `0 4px 15px ${colors.accent}40`;
              }}
            >
              <MessageCircle size={18} />
              Chat with {wisdom.personality_name}
            </button>
            
            <button
              onClick={handleExploreMore}
              style={{
                background: 'transparent',
                color: '#64748b',
                border: '1px solid #e2e8f0',
                padding: '1rem 2rem',
                borderRadius: '0.75rem',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '500',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#f8fafc';
                e.currentTarget.style.borderColor = colors.accent;
                e.currentTarget.style.color = colors.text;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.borderColor = '#e2e8f0';
                e.currentTarget.style.color = '#64748b';
              }}
            >
              Explore All Minds
              <ArrowRight size={18} />
            </button>
          </div>
        </div>

        {/* Featured Personalities */}
        <div style={{
          marginTop: '3rem',
          textAlign: 'center'
        }}>
          <p style={{
            color: '#94a3b8',
            fontSize: '0.875rem',
            marginBottom: '1rem'
          }}>
            Also converse with
          </p>
          <div style={{
            display: 'flex',
            gap: '0.75rem',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            {[
              { name: 'Krishna', domain: 'spiritual' },
              { name: 'Einstein', domain: 'scientific' },
              { name: 'Buddha', domain: 'spiritual' },
              { name: 'Lincoln', domain: 'leadership' },
              { name: 'Shakespeare', domain: 'literary' }
            ].map((p) => {
              const pColors = getDomainColors(p.domain);
              return (
                <span
                  key={p.name}
                  style={{
                    background: pColors.bg,
                    color: pColors.text,
                    padding: '0.5rem 1rem',
                    borderRadius: '2rem',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    border: `1px solid ${pColors.border}`
                  }}
                >
                  {p.name}
                </span>
              );
            })}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer style={{
        textAlign: 'center',
        padding: '2rem',
        color: '#94a3b8',
        fontSize: '0.875rem'
      }}>
        <p>
          © 2025 Vimarsh - Wisdom Without Boundaries
        </p>
      </footer>
    </div>
  );
};

export default ShareView;
