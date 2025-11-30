/**
 * WisdomArchive - Browse Past Wisdom Entries
 * 
 * Displays a paginated history of daily wisdom entries.
 * Users can filter by domain, personality, and date.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, Search, Filter, Heart, Share2, ChevronLeft, ChevronRight, Sparkles } from 'lucide-react';
import { SharingInterface } from '../components/SharingInterface';
import { getApiBaseUrl } from '../config/environment';

interface WisdomEntry {
  id: string;
  date: string;
  personality_id: string;
  personality_name: string;
  domain: string;
  wisdom_text: string;
  source_citation?: string;
  saved: boolean;
}

interface FilterState {
  domain: string;
  personality: string;
  month: string;
}

// Domain colors
const getDomainColors = (domain: string) => {
  const colorMap: Record<string, { bg: string; border: string; text: string; gradient: string }> = {
    spiritual: {
      bg: 'rgba(255, 107, 53, 0.08)',
      border: 'rgba(255, 107, 53, 0.25)',
      text: '#ea580c',
      gradient: 'linear-gradient(135deg, #FF6B35, #F7931E)'
    },
    scientific: {
      bg: 'rgba(59, 130, 246, 0.08)',
      border: 'rgba(59, 130, 246, 0.25)',
      text: '#2563eb',
      gradient: 'linear-gradient(135deg, #3B82F6, #1D4ED8)'
    },
    philosophical: {
      bg: 'rgba(147, 51, 234, 0.08)',
      border: 'rgba(147, 51, 234, 0.25)',
      text: '#9333ea',
      gradient: 'linear-gradient(135deg, #9333EA, #7C3AED)'
    },
    historical: {
      bg: 'rgba(34, 197, 94, 0.08)',
      border: 'rgba(34, 197, 94, 0.25)',
      text: '#16a34a',
      gradient: 'linear-gradient(135deg, #22C55E, #16A34A)'
    },
    leadership: {
      bg: 'rgba(239, 68, 68, 0.08)',
      border: 'rgba(239, 68, 68, 0.25)',
      text: '#dc2626',
      gradient: 'linear-gradient(135deg, #EF4444, #DC2626)'
    },
    literary: {
      bg: 'rgba(16, 185, 129, 0.08)',
      border: 'rgba(16, 185, 129, 0.25)',
      text: '#059669',
      gradient: 'linear-gradient(135deg, #10B981, #059669)'
    },
    psychology: {
      bg: 'rgba(139, 92, 246, 0.08)',
      border: 'rgba(139, 92, 246, 0.25)',
      text: '#8b5cf6',
      gradient: 'linear-gradient(135deg, #8B5CF6, #7C3AED)'
    }
  };
  return colorMap[domain] || colorMap.spiritual;
};

// Static wisdom archive for demo
const STATIC_ARCHIVE: WisdomEntry[] = [
  {
    id: 'w1',
    date: '2025-01-28',
    personality_id: 'krishna',
    personality_name: 'Lord Krishna',
    domain: 'spiritual',
    wisdom_text: 'You have the right to work, but never to the fruit of work.',
    source_citation: 'Bhagavad Gita 2.47',
    saved: true
  },
  {
    id: 'w2',
    date: '2025-01-27',
    personality_id: 'albert_einstein',
    personality_name: 'Albert Einstein',
    domain: 'scientific',
    wisdom_text: 'Imagination is more important than knowledge. Knowledge is limited. Imagination encircles the world.',
    source_citation: 'Interview, 1929',
    saved: false
  },
  {
    id: 'w3',
    date: '2025-01-26',
    personality_id: 'marcus_aurelius',
    personality_name: 'Marcus Aurelius',
    domain: 'philosophical',
    wisdom_text: 'Very little is needed to make a happy life; it is all within yourself, in your way of thinking.',
    source_citation: 'Meditations',
    saved: true
  },
  {
    id: 'w4',
    date: '2025-01-25',
    personality_id: 'mahatma_gandhi',
    personality_name: 'Mahatma Gandhi',
    domain: 'leadership',
    wisdom_text: 'Be the change you wish to see in the world.',
    source_citation: 'Personal Philosophy',
    saved: false
  },
  {
    id: 'w5',
    date: '2025-01-24',
    personality_id: 'buddha',
    personality_name: 'Gautama Buddha',
    domain: 'spiritual',
    wisdom_text: 'Peace comes from within. Do not seek it without.',
    source_citation: 'Buddhist Teachings',
    saved: true
  },
  {
    id: 'w6',
    date: '2025-01-23',
    personality_id: 'socrates',
    personality_name: 'Socrates',
    domain: 'philosophical',
    wisdom_text: 'The unexamined life is not worth living.',
    source_citation: 'Apology of Socrates',
    saved: false
  },
  {
    id: 'w7',
    date: '2025-01-22',
    personality_id: 'abraham_lincoln',
    personality_name: 'Abraham Lincoln',
    domain: 'leadership',
    wisdom_text: 'In the end, it\'s not the years in your life that count. It\'s the life in your years.',
    source_citation: 'Attributed',
    saved: false
  },
  {
    id: 'w8',
    date: '2025-01-21',
    personality_id: 'rumi',
    personality_name: 'Rumi',
    domain: 'spiritual',
    wisdom_text: 'The wound is the place where the Light enters you.',
    source_citation: 'Masnavi',
    saved: true
  }
];

const DOMAINS = ['All', 'spiritual', 'scientific', 'philosophical', 'leadership', 'literary', 'psychology'];

const WisdomArchive: React.FC = () => {
  const navigate = useNavigate();
  
  const [entries, setEntries] = useState<WisdomEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<FilterState>({
    domain: 'All',
    personality: 'All',
    month: 'All'
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [shareEntry, setShareEntry] = useState<WisdomEntry | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  const ITEMS_PER_PAGE = 6;

  // Fetch wisdom archive
  const fetchArchive = useCallback(async () => {
    setLoading(true);
    try {
      const apiUrl = getApiBaseUrl();
      const response = await fetch(`${apiUrl}/wisdom/history?page=${page}&limit=${ITEMS_PER_PAGE}`);
      
      if (response.ok) {
        const data = await response.json();
        setEntries(data.entries || STATIC_ARCHIVE);
        setTotalPages(data.total_pages || Math.ceil(STATIC_ARCHIVE.length / ITEMS_PER_PAGE));
      } else {
        // Use static data
        const start = (page - 1) * ITEMS_PER_PAGE;
        const filtered = filterEntries(STATIC_ARCHIVE);
        setEntries(filtered.slice(start, start + ITEMS_PER_PAGE));
        setTotalPages(Math.ceil(filtered.length / ITEMS_PER_PAGE));
      }
    } catch (err) {
      // Use static data
      const start = (page - 1) * ITEMS_PER_PAGE;
      const filtered = filterEntries(STATIC_ARCHIVE);
      setEntries(filtered.slice(start, start + ITEMS_PER_PAGE));
      setTotalPages(Math.ceil(filtered.length / ITEMS_PER_PAGE));
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  const filterEntries = (allEntries: WisdomEntry[]) => {
    return allEntries.filter(entry => {
      if (filters.domain !== 'All' && entry.domain !== filters.domain) return false;
      return true;
    });
  };

  useEffect(() => {
    fetchArchive();
  }, [fetchArchive]);

  const handleSave = async (entryId: string) => {
    setEntries(prev => prev.map(e => 
      e.id === entryId ? { ...e, saved: !e.saved } : e
    ));
    
    // Try to persist to backend
    try {
      const apiUrl = getApiBaseUrl();
      await fetch(`${apiUrl}/wisdom/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wisdom_id: entryId })
      });
    } catch (err) {
      // Silent fail
    }
  };

  const handleShare = (entry: WisdomEntry) => {
    setShareEntry(entry);
  };

  const handleExplore = (personalityId: string) => {
    navigate(`/guidance?personality=${personalityId}`);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #FFF8E1 0%, #FFE0B2 100%)',
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    }}>
      {/* Header */}
      <header style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(0, 0, 0, 0.05)',
        padding: '1rem 2rem',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{
          maxWidth: '1000px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button
              onClick={() => navigate(-1)}
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                padding: '0.5rem',
                display: 'flex',
                alignItems: 'center',
                color: '#64748b'
              }}
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 style={{ 
                fontSize: '1.25rem', 
                fontWeight: '600',
                color: '#1e293b',
                margin: 0
              }}>
                Wisdom Archive
              </h1>
              <p style={{ 
                fontSize: '0.8rem', 
                color: '#64748b',
                margin: 0
              }}>
                Browse past daily wisdom entries
              </p>
            </div>
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: showFilters ? '#FF6B35' : 'transparent',
              color: showFilters ? 'white' : '#64748b',
              border: `1px solid ${showFilters ? '#FF6B35' : '#e2e8f0'}`,
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            <Filter size={16} />
            Filters
          </button>
        </div>
      </header>

      {/* Filters Panel */}
      {showFilters && (
        <div style={{
          background: 'white',
          borderBottom: '1px solid #e2e8f0',
          padding: '1rem 2rem'
        }}>
          <div style={{
            maxWidth: '1000px',
            margin: '0 auto',
            display: 'flex',
            gap: '1rem',
            flexWrap: 'wrap'
          }}>
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: '0.75rem', 
                color: '#64748b', 
                marginBottom: '0.25rem' 
              }}>
                Domain
              </label>
              <select
                value={filters.domain}
                onChange={(e) => {
                  setFilters(prev => ({ ...prev, domain: e.target.value }));
                  setPage(1);
                }}
                style={{
                  padding: '0.5rem 1rem',
                  borderRadius: '0.5rem',
                  border: '1px solid #e2e8f0',
                  fontSize: '0.875rem',
                  minWidth: '150px'
                }}
              >
                {DOMAINS.map(d => (
                  <option key={d} value={d}>{d === 'All' ? 'All Domains' : d}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main style={{
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '2rem 1.5rem'
      }}>
        {loading ? (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '1.5rem'
          }}>
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div
                key={i}
                style={{
                  background: 'white',
                  borderRadius: '1rem',
                  padding: '1.5rem',
                  height: '200px',
                  animation: 'pulse 1.5s ease-in-out infinite'
                }}
              />
            ))}
          </div>
        ) : entries.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '4rem 2rem'
          }}>
            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📚</div>
            <h2 style={{ color: '#1e293b', marginBottom: '0.5rem' }}>No Wisdom Found</h2>
            <p style={{ color: '#64748b' }}>
              Try adjusting your filters or check back later for more wisdom.
            </p>
          </div>
        ) : (
          <>
            {/* Wisdom Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem'
            }}>
              {entries.map(entry => {
                const colors = getDomainColors(entry.domain);
                return (
                  <div
                    key={entry.id}
                    style={{
                      background: 'white',
                      borderRadius: '1rem',
                      padding: '1.5rem',
                      border: `2px solid ${colors.border}`,
                      boxShadow: '0 4px 15px rgba(0, 0, 0, 0.05)',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)';
                      e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.05)';
                    }}
                  >
                    {/* Date & Domain */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '1rem'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        color: '#64748b',
                        fontSize: '0.75rem'
                      }}>
                        <Calendar size={12} />
                        {formatDate(entry.date)}
                      </div>
                      <span style={{
                        background: colors.bg,
                        color: colors.text,
                        padding: '0.25rem 0.75rem',
                        borderRadius: '1rem',
                        fontSize: '0.7rem',
                        fontWeight: '500',
                        textTransform: 'capitalize'
                      }}>
                        {entry.domain}
                      </span>
                    </div>

                    {/* Quote */}
                    <p style={{
                      fontSize: '0.95rem',
                      lineHeight: '1.5',
                      color: '#1e293b',
                      marginBottom: '1rem',
                      fontStyle: 'italic'
                    }}>
                      "{entry.wisdom_text.length > 150 
                        ? entry.wisdom_text.substring(0, 150) + '...' 
                        : entry.wisdom_text}"
                    </p>

                    {/* Attribution */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      paddingTop: '1rem',
                      borderTop: '1px solid #f1f5f9'
                    }}>
                      <div>
                        <p style={{
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: colors.text,
                          margin: 0
                        }}>
                          {entry.personality_name}
                        </p>
                        {entry.source_citation && (
                          <p style={{
                            fontSize: '0.7rem',
                            color: '#94a3b8',
                            margin: 0
                          }}>
                            {entry.source_citation}
                          </p>
                        )}
                      </div>

                      {/* Actions */}
                      <div style={{
                        display: 'flex',
                        gap: '0.5rem'
                      }}>
                        <button
                          onClick={() => handleSave(entry.id)}
                          style={{
                            background: entry.saved ? '#fef2f2' : 'transparent',
                            border: 'none',
                            padding: '0.5rem',
                            borderRadius: '0.5rem',
                            cursor: 'pointer',
                            color: entry.saved ? '#ef4444' : '#94a3b8'
                          }}
                          title={entry.saved ? 'Remove from saved' : 'Save wisdom'}
                        >
                          <Heart size={16} fill={entry.saved ? '#ef4444' : 'none'} />
                        </button>
                        <button
                          onClick={() => handleShare(entry)}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            padding: '0.5rem',
                            borderRadius: '0.5rem',
                            cursor: 'pointer',
                            color: '#94a3b8'
                          }}
                          title="Share wisdom"
                        >
                          <Share2 size={16} />
                        </button>
                        <button
                          onClick={() => handleExplore(entry.personality_id)}
                          style={{
                            background: colors.gradient,
                            border: 'none',
                            padding: '0.5rem 0.75rem',
                            borderRadius: '0.5rem',
                            cursor: 'pointer',
                            color: 'white',
                            fontSize: '0.7rem',
                            fontWeight: '500'
                          }}
                        >
                          Explore
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '1rem'
              }}>
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    background: page === 1 ? '#f1f5f9' : 'white',
                    border: '1px solid #e2e8f0',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.5rem',
                    cursor: page === 1 ? 'not-allowed' : 'pointer',
                    color: page === 1 ? '#94a3b8' : '#64748b'
                  }}
                >
                  <ChevronLeft size={16} />
                  Previous
                </button>
                
                <span style={{ color: '#64748b', fontSize: '0.875rem' }}>
                  Page {page} of {totalPages}
                </span>
                
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    background: page === totalPages ? '#f1f5f9' : 'white',
                    border: '1px solid #e2e8f0',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.5rem',
                    cursor: page === totalPages ? 'not-allowed' : 'pointer',
                    color: page === totalPages ? '#94a3b8' : '#64748b'
                  }}
                >
                  Next
                  <ChevronRight size={16} />
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Share Modal */}
      {shareEntry && (
        <SharingInterface
          content={{
            text: shareEntry.wisdom_text,
            personality: shareEntry.personality_name,
            citation: shareEntry.source_citation,
            domain: shareEntry.domain
          }}
          onShareComplete={() => setShareEntry(null)}
        />
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.6; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
};

export default WisdomArchive;
