import React, { useState, useEffect, useCallback } from 'react';
import { Sparkles, Heart, BookOpen, ChevronRight, RefreshCw } from 'lucide-react';
import SharingInterface from './SharingInterface';
import { getApiBaseUrl } from '../config/environment';

interface WisdomData {
  id: string;
  date: string;
  personality: string;
  personality_display_name: string;
  domain: string;
  wisdom_text: string;
  source_citation?: string;
  context?: string;
  reflection_prompt: string;
  hashtags: string[];
}

interface WisdomOfDayProps {
  className?: string;
  onExplore?: (personalityId: string) => void;
  compact?: boolean;
}

// Static wisdom quotes for different personalities - used as fallback
const STATIC_WISDOM: WisdomData[] = [
  {
    id: 'static-krishna-1',
    date: new Date().toISOString().split('T')[0],
    personality: 'krishna',
    personality_display_name: 'Lord Krishna',
    domain: 'spiritual',
    wisdom_text: 'You have the right to work, but never to the fruit of work. You should never engage in action for the sake of reward, nor should you long for inaction.',
    source_citation: 'Bhagavad Gita, Chapter 2, Verse 47',
    context: 'This foundational teaching on Karma Yoga encourages us to focus on our duties without attachment to outcomes, finding peace in right action itself.',
    reflection_prompt: 'What would change if you focused entirely on the quality of your actions rather than their results?',
    hashtags: ['KarmaYoga', 'BhagavadGita', 'Detachment']
  },
  {
    id: 'static-buddha-1',
    date: new Date().toISOString().split('T')[0],
    personality: 'buddha',
    personality_display_name: 'Gautama Buddha',
    domain: 'spiritual',
    wisdom_text: 'Peace comes from within. Do not seek it without. The mind is everything. What you think you become.',
    source_citation: 'Dhammapada',
    context: 'The Buddha teaches that true peace cannot be found in external circumstances but must be cultivated through inner practice and mindfulness.',
    reflection_prompt: 'How might your life change if you spent more time cultivating inner peace rather than seeking external solutions?',
    hashtags: ['InnerPeace', 'Mindfulness', 'Buddhism']
  },
  {
    id: 'static-einstein-1',
    date: new Date().toISOString().split('T')[0],
    personality: 'albert_einstein',
    personality_display_name: 'Albert Einstein',
    domain: 'scientific',
    wisdom_text: 'Imagination is more important than knowledge. Knowledge is limited. Imagination encircles the world.',
    source_citation: 'Interview, 1929',
    context: 'Einstein emphasizes that while knowledge tells us what is, imagination allows us to envision what could be—the foundation of all scientific breakthroughs.',
    reflection_prompt: 'When did you last allow yourself to imagine without the constraints of what you currently know?',
    hashtags: ['Imagination', 'Science', 'Innovation']
  },
  {
    id: 'static-aurelius-1',
    date: new Date().toISOString().split('T')[0],
    personality: 'marcus_aurelius',
    personality_display_name: 'Marcus Aurelius',
    domain: 'philosophical',
    wisdom_text: 'Very little is needed to make a happy life; it is all within yourself, in your way of thinking.',
    source_citation: 'Meditations, Book 7',
    context: 'The Stoic emperor reminds us that external wealth and status matter little compared to the quality of our thoughts and perspective.',
    reflection_prompt: 'What simple changes in your thinking could bring more contentment to your daily life?',
    hashtags: ['Stoicism', 'Wisdom', 'InnerLife']
  },
  {
    id: 'static-lincoln-1',
    date: new Date().toISOString().split('T')[0],
    personality: 'abraham_lincoln',
    personality_display_name: 'Abraham Lincoln',
    domain: 'leadership',
    wisdom_text: 'I am a slow walker, but I never walk back. The best way to predict the future is to create it.',
    source_citation: 'Personal letters',
    context: 'Lincoln\'s persistence through countless failures and setbacks teaches us that steady progress toward our goals matters more than speed.',
    reflection_prompt: 'What goal have you been approaching with impatience that might benefit from steady, unwavering progress?',
    hashtags: ['Persistence', 'Leadership', 'Progress']
  },
  {
    id: 'static-rumi-1',
    date: new Date().toISOString().split('T')[0],
    personality: 'rumi',
    personality_display_name: 'Rumi',
    domain: 'spiritual',
    wisdom_text: 'The wound is the place where the Light enters you. What you seek is seeking you.',
    source_citation: 'Masnavi',
    context: 'Rumi transforms our understanding of suffering, revealing that our deepest wounds can become openings for spiritual growth and divine connection.',
    reflection_prompt: 'What difficult experience in your life has ultimately led to growth or understanding?',
    hashtags: ['Sufi', 'Transformation', 'DivineLove']
  },
  {
    id: 'static-confucius-1',
    date: new Date().toISOString().split('T')[0],
    personality: 'confucius',
    personality_display_name: 'Confucius',
    domain: 'philosophical',
    wisdom_text: 'It does not matter how slowly you go as long as you do not stop. The man who moves a mountain begins by carrying away small stones.',
    source_citation: 'Analects',
    context: 'Confucius teaches the value of persistent effort and the understanding that great achievements come through consistent small actions.',
    reflection_prompt: 'What small step could you take today toward a goal that seems overwhelming?',
    hashtags: ['Persistence', 'Wisdom', 'SelfCultivation']
  }
];

// Get domain-specific colors
const getDomainColors = (domain: string) => {
  const colorMap: Record<string, { bg: string; border: string; text: string; gradient: string }> = {
    spiritual: {
      bg: 'rgba(255, 107, 53, 0.08)',
      border: 'rgba(255, 107, 53, 0.25)',
      text: '#ea580c',
      gradient: 'linear-gradient(135deg, #fff8f0 0%, #fff0e6 100%)'
    },
    scientific: {
      bg: 'rgba(59, 130, 246, 0.08)',
      border: 'rgba(59, 130, 246, 0.25)',
      text: '#2563eb',
      gradient: 'linear-gradient(135deg, #f0f7ff 0%, #e6f0ff 100%)'
    },
    philosophical: {
      bg: 'rgba(147, 51, 234, 0.08)',
      border: 'rgba(147, 51, 234, 0.25)',
      text: '#9333ea',
      gradient: 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)'
    },
    historical: {
      bg: 'rgba(34, 197, 94, 0.08)',
      border: 'rgba(34, 197, 94, 0.25)',
      text: '#16a34a',
      gradient: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)'
    },
    leadership: {
      bg: 'rgba(239, 68, 68, 0.08)',
      border: 'rgba(239, 68, 68, 0.25)',
      text: '#dc2626',
      gradient: 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)'
    },
    literary: {
      bg: 'rgba(16, 185, 129, 0.08)',
      border: 'rgba(16, 185, 129, 0.25)',
      text: '#059669',
      gradient: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)'
    },
    psychology: {
      bg: 'rgba(139, 92, 246, 0.08)',
      border: 'rgba(139, 92, 246, 0.25)',
      text: '#8b5cf6',
      gradient: 'linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%)'
    }
  };
  
  return colorMap[domain] || colorMap.spiritual;
};

// Get a random wisdom for the day based on date
const getWisdomForDate = (dateStr: string): WisdomData => {
  // Use date to deterministically select wisdom
  const dateNum = new Date(dateStr).getTime();
  const index = Math.abs(dateNum) % STATIC_WISDOM.length;
  const wisdom = { ...STATIC_WISDOM[index] };
  wisdom.date = dateStr;
  wisdom.id = `wotd-${dateStr}-${wisdom.personality}`;
  return wisdom;
};

export const WisdomOfDay: React.FC<WisdomOfDayProps> = ({ 
  className, 
  onExplore,
  compact = false 
}) => {
  const [wisdom, setWisdom] = useState<WisdomData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);
  const [showContext, setShowContext] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch wisdom of the day
  const fetchWisdom = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Try to fetch from API first
      const apiUrl = getApiBaseUrl();
      const response = await fetch(`${apiUrl}/wisdom-of-day`);
      
      if (response.ok) {
        const data = await response.json();
        // Map API response to our WisdomData format
        const apiWisdom = data.wisdom;
        setWisdom({
          id: `wotd-${data.date}`,
          date: data.date,
          personality: apiWisdom.personality_id,
          personality_display_name: apiWisdom.personality_name,
          domain: apiWisdom.domain,
          wisdom_text: apiWisdom.quote,
          source_citation: apiWisdom.source,
          context: `This wisdom from ${apiWisdom.personality_name} offers timeless insight for your journey.`,
          reflection_prompt: 'How might this wisdom apply to your life today?',
          hashtags: [apiWisdom.domain, 'Wisdom', 'Vimarsh']
        });
      } else {
        // Fall back to static wisdom
        const today = new Date().toISOString().split('T')[0];
        setWisdom(getWisdomForDate(today));
      }
    } catch (err) {
      // Use static wisdom on error
      const today = new Date().toISOString().split('T')[0];
      setWisdom(getWisdomForDate(today));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWisdom();
  }, [fetchWisdom]);

  // Save wisdom to collection
  const handleSave = async () => {
    if (!wisdom) return;

    try {
      // Try to save to backend
      await fetch('/api/wisdom/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wisdom_id: wisdom.id })
      });
    } catch (err) {
      // Silent fail - just update UI state
    }

    setSaved(true);
  };

  // Handle explore personality
  const handleExplore = () => {
    if (wisdom && onExplore) {
      onExplore(wisdom.personality);
    }
  };

  // Loading skeleton
  if (loading) {
    return (
      <div 
        className={className}
        style={{
          background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
          borderRadius: '1rem',
          padding: compact ? '1rem' : '1.5rem',
          border: '1px solid #e2e8f0'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: '#e2e8f0', animation: 'pulse 1.5s ease-in-out infinite' }} />
          <div style={{ width: '120px', height: '16px', borderRadius: '4px', background: '#e2e8f0', animation: 'pulse 1.5s ease-in-out infinite' }} />
        </div>
        <div style={{ width: '100%', height: '80px', borderRadius: '8px', background: '#e2e8f0', animation: 'pulse 1.5s ease-in-out infinite', marginBottom: '1rem' }} />
        <div style={{ width: '60%', height: '14px', borderRadius: '4px', background: '#e2e8f0', animation: 'pulse 1.5s ease-in-out infinite' }} />
      </div>
    );
  }

  if (!wisdom) {
    return null;
  }

  const colors = getDomainColors(wisdom.domain);
  const formattedDate = new Date(wisdom.date).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric'
  });

  return (
    <div
      className={className}
      style={{
        background: colors.gradient,
        borderRadius: '1rem',
        border: `2px solid ${colors.border}`,
        padding: compact ? '1rem' : '1.5rem',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
        transition: 'all 0.3s ease'
      }}
    >
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: compact ? '0.75rem' : '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={18} color={colors.text} />
          <span style={{
            fontSize: '0.85rem',
            fontWeight: '600',
            color: colors.text,
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Wisdom of the Day
          </span>
        </div>
        <span style={{
          fontSize: '0.75rem',
          color: '#64748b'
        }}>
          {formattedDate}
        </span>
      </div>

      {/* Wisdom Text */}
      <blockquote style={{
        fontSize: compact ? '1rem' : '1.15rem',
        fontFamily: 'Georgia, serif',
        fontStyle: 'italic',
        lineHeight: '1.6',
        color: '#1e293b',
        margin: `0 0 ${compact ? '0.75rem' : '1rem'} 0`,
        padding: '0',
        borderLeft: `3px solid ${colors.text}`,
        paddingLeft: '1rem'
      }}>
        "{wisdom.wisdom_text}"
      </blockquote>

      {/* Attribution */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        marginBottom: compact ? '0.75rem' : '1rem',
        flexWrap: 'wrap'
      }}>
        <span style={{
          fontWeight: '600',
          color: colors.text
        }}>
          — {wisdom.personality_display_name}
        </span>
        {wisdom.source_citation && (
          <span style={{
            fontSize: '0.85rem',
            color: '#64748b',
            fontStyle: 'italic'
          }}>
            ({wisdom.source_citation})
          </span>
        )}
      </div>

      {/* Context Toggle (non-compact only) */}
      {!compact && wisdom.context && (
        <>
          <button
            onClick={() => setShowContext(!showContext)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              background: 'none',
              border: 'none',
              color: '#64748b',
              fontSize: '0.85rem',
              cursor: 'pointer',
              padding: '0.25rem 0',
              marginBottom: showContext ? '0.75rem' : '1rem'
            }}
          >
            <BookOpen size={14} />
            {showContext ? 'Hide context' : 'Show context'}
          </button>

          {showContext && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.6)',
              borderRadius: '0.5rem',
              padding: '0.75rem 1rem',
              marginBottom: '1rem',
              fontSize: '0.9rem',
              color: '#475569',
              lineHeight: '1.5'
            }}>
              {wisdom.context}
            </div>
          )}
        </>
      )}

      {/* Reflection Prompt */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.7)',
        borderRadius: '0.5rem',
        padding: compact ? '0.65rem 0.85rem' : '0.85rem 1rem',
        marginBottom: compact ? '0.75rem' : '1rem',
        borderLeft: `3px solid ${colors.text}40`
      }}>
        <p style={{
          margin: 0,
          fontSize: compact ? '0.85rem' : '0.9rem',
          color: '#475569',
          fontStyle: 'italic',
          lineHeight: '1.4'
        }}>
          💭 {wisdom.reflection_prompt}
        </p>
      </div>

      {/* Actions */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={saved}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.4rem 0.75rem',
              background: saved ? '#fef2f2' : 'transparent',
              border: `1px solid ${saved ? '#fca5a5' : '#e2e8f0'}`,
              borderRadius: '0.5rem',
              color: saved ? '#dc2626' : '#64748b',
              fontSize: '0.8rem',
              fontWeight: '500',
              cursor: saved ? 'default' : 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <Heart size={14} fill={saved ? '#dc2626' : 'none'} />
            {saved ? 'Saved' : 'Save'}
          </button>

          {/* Share Button */}
          <SharingInterface
            content={{
              text: wisdom.wisdom_text,
              personality: wisdom.personality_display_name,
              citation: wisdom.source_citation,
              domain: wisdom.domain
            }}
            size="small"
          />
        </div>

        {/* Explore Button */}
        {onExplore && (
          <button
            onClick={handleExplore}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.4rem 0.85rem',
              background: colors.text,
              border: 'none',
              borderRadius: '0.5rem',
              color: 'white',
              fontSize: '0.8rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: `0 2px 8px ${colors.text}40`
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = `0 4px 12px ${colors.text}50`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = `0 2px 8px ${colors.text}40`;
            }}
          >
            Explore {wisdom.personality_display_name.split(' ')[0]}
            <ChevronRight size={14} />
          </button>
        )}
      </div>

      {/* Hashtags (non-compact only) */}
      {!compact && wisdom.hashtags && wisdom.hashtags.length > 0 && (
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '0.5rem',
          marginTop: '1rem'
        }}>
          {wisdom.hashtags.map((tag, i) => (
            <span
              key={i}
              style={{
                fontSize: '0.75rem',
                color: '#94a3b8',
                background: 'rgba(148, 163, 184, 0.1)',
                padding: '0.2rem 0.5rem',
                borderRadius: '0.25rem'
              }}
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* Pulse animation for loading skeleton */}
      <style>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 0.4;
          }
          50% {
            opacity: 0.8;
          }
        }
      `}</style>
    </div>
  );
};

export default WisdomOfDay;
