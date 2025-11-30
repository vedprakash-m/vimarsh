/**
 * ConversationTimeline Component
 * 
 * Visual history of conversations across sessions with filtering and navigation.
 * Part of Phase 3: Frontend Memory UX implementation.
 * 
 * Features:
 * - Timeline view of past sessions
 * - Filter by personality and date range
 * - Session summary cards with key topics
 * - Emotional arc visualization
 * - Quick navigation to specific sessions
 */

import React, { useState, useMemo, useCallback } from 'react';
import { useMemory, SessionSummary as MemorySessionSummary } from '../contexts/MemoryContext';
import { useNavigate } from 'react-router-dom';
import { RelationshipBadge } from './RelationshipBadge';

interface SessionSummaryDisplay {
  session_id: string;
  personality_id: string;
  personality_name?: string;
  start_time: string;
  end_time: string;
  message_count: number;
  key_topics: string[];
  emotional_arc: Array<{
    timestamp: string;
    emotion: string;
    intensity: number;
  }>;
  summary: string;
  insights: string[];
  milestone_achieved?: string;
}

interface ConversationTimelineProps {
  sessions?: SessionSummaryDisplay[];
  onSessionSelect?: (sessionId: string) => void;
  compact?: boolean;
  maxSessions?: number;
  filterPersonality?: string;
}

// Domain color mapping
const getDomainColors = (domain: string) => {
  const colorMap: Record<string, { primary: string; secondary: string; bg: string }> = {
    spiritual: { primary: '#f97316', secondary: '#fdba74', bg: 'rgba(249, 115, 22, 0.1)' },
    philosophical: { primary: '#8b5cf6', secondary: '#c4b5fd', bg: 'rgba(139, 92, 246, 0.1)' },
    leadership: { primary: '#3b82f6', secondary: '#93c5fd', bg: 'rgba(59, 130, 246, 0.1)' },
    scientific: { primary: '#10b981', secondary: '#6ee7b7', bg: 'rgba(16, 185, 129, 0.1)' },
    literary: { primary: '#ec4899', secondary: '#f9a8d4', bg: 'rgba(236, 72, 153, 0.1)' },
    psychology: { primary: '#f59e0b', secondary: '#fcd34d', bg: 'rgba(245, 158, 11, 0.1)' },
  };
  return colorMap[domain] || colorMap.spiritual;
};

// Get personality domain from personality_id
const getPersonalityDomain = (personalityId: string): string => {
  const domainMap: Record<string, string> = {
    krishna: 'spiritual',
    buddha: 'spiritual',
    jesus: 'spiritual',
    rumi: 'spiritual',
    vivekananda: 'spiritual',
    marcus_aurelius: 'philosophical',
    lao_tzu: 'philosophical',
    confucius: 'philosophical',
    aristotle: 'philosophical',
    plato: 'philosophical',
    socrates: 'philosophical',
    chanakya: 'leadership',
    lincoln: 'leadership',
    franklin: 'leadership',
    washington: 'leadership',
    gandhi: 'leadership',
    mlk: 'leadership',
    einstein: 'scientific',
    newton: 'scientific',
    tesla: 'scientific',
    archimedes: 'scientific',
    davinci: 'scientific',
    tagore: 'literary',
    shakespeare: 'literary',
    freud: 'psychology',
  };
  return domainMap[personalityId] || 'spiritual';
};

// Format relative time
const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
  return date.toLocaleDateString();
};

// Calculate session duration
const formatDuration = (start: string, end: string): string => {
  const startDate = new Date(start);
  const endDate = new Date(end);
  const diffMs = endDate.getTime() - startDate.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return '<1 min';
  if (diffMins < 60) return `${diffMins} min`;
  const hours = Math.floor(diffMins / 60);
  const mins = diffMins % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
};

// Get emotion emoji
const getEmotionEmoji = (emotion: string): string => {
  const emojiMap: Record<string, string> = {
    joy: '😊',
    serenity: '😌',
    curiosity: '🤔',
    gratitude: '🙏',
    love: '❤️',
    hope: '✨',
    sadness: '😢',
    anxiety: '😰',
    confusion: '😕',
    anger: '😠',
    fear: '😨',
    neutral: '😐',
  };
  return emojiMap[emotion.toLowerCase()] || '💭';
};

export const ConversationTimeline: React.FC<ConversationTimelineProps> = ({
  sessions = [],
  onSessionSelect,
  compact = false,
  maxSessions = 10,
  filterPersonality,
}) => {
  const { recentSessions, relationships, getRelationship } = useMemory();
  const navigate = useNavigate();
  
  const [filter, setFilter] = useState<string>(filterPersonality || 'all');
  const [expandedSession, setExpandedSession] = useState<string | null>(null);

  // Use provided sessions or fall back to context recent sessions
  const allSessions: SessionSummaryDisplay[] = useMemo(() => {
    if (sessions.length > 0) return sessions;
    
    // Convert memory session summaries to display format
    return recentSessions.map((session: MemorySessionSummary) => ({
      session_id: session.id,
      personality_id: session.personalityId,
      start_time: session.sessionStart,
      end_time: session.sessionEnd,
      message_count: session.messageCount,
      key_topics: session.topicsDiscussed,
      emotional_arc: [{
        timestamp: session.sessionStart,
        emotion: session.emotionalArc.start,
        intensity: 0.5,
      }, {
        timestamp: session.sessionEnd,
        emotion: session.emotionalArc.end,
        intensity: 0.8,
      }],
      summary: session.summary,
      insights: session.keyInsights,
    }));
  }, [sessions, recentSessions]);

  // Filter sessions
  const filteredSessions = useMemo(() => {
    let result = [...allSessions];
    
    if (filter !== 'all') {
      result = result.filter((s: SessionSummaryDisplay) => s.personality_id === filter);
    }
    
    // Sort by most recent first
    result.sort((a: SessionSummaryDisplay, b: SessionSummaryDisplay) => 
      new Date(b.start_time).getTime() - new Date(a.start_time).getTime()
    );
    
    return result.slice(0, maxSessions);
  }, [allSessions, filter, maxSessions]);

  // Get unique personalities from sessions
  const personalities = useMemo(() => {
    const unique = new Set<string>(allSessions.map((s: SessionSummaryDisplay) => s.personality_id));
    return Array.from(unique);
  }, [allSessions]);

  const handleSessionClick = useCallback((sessionId: string) => {
    if (onSessionSelect) {
      onSessionSelect(sessionId);
    } else {
      setExpandedSession(expandedSession === sessionId ? null : sessionId);
    }
  }, [onSessionSelect, expandedSession]);

  if (allSessions.length === 0) {
    return (
      <div style={styles.emptyState}>
        <div style={styles.emptyIcon}>📜</div>
        <h3 style={styles.emptyTitle}>No Conversations Yet</h3>
        <p style={styles.emptyText}>
          Start a conversation with a personality to see your history here.
        </p>
        <button 
          style={styles.startButton}
          onClick={() => navigate('/guidance')}
        >
          Begin Your Journey
        </button>
      </div>
    );
  }

  return (
    <div style={compact ? styles.containerCompact : styles.container}>
      {/* Header with Filters */}
      {!compact && (
        <div style={styles.header}>
          <h2 style={styles.title}>
            <span style={styles.titleIcon}>🕰️</span>
            Conversation History
          </h2>
          
          <div style={styles.filters}>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              style={styles.filterSelect}
            >
              <option value="all">All Personalities</option>
              {personalities.map((p) => (
                <option key={p} value={p}>
                  {p.charAt(0).toUpperCase() + p.slice(1).replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Timeline */}
      <div style={styles.timeline}>
        {filteredSessions.map((session, index) => {
          const domain = getPersonalityDomain(session.personality_id);
          const colors = getDomainColors(domain);
          const isExpanded = expandedSession === session.session_id;
          const relationship = getRelationship(session.personality_id);

          return (
            <div 
              key={session.session_id} 
              style={{
                ...styles.sessionCard,
                borderLeftColor: colors.primary,
                backgroundColor: isExpanded ? colors.bg : '#ffffff',
              }}
              onClick={() => handleSessionClick(session.session_id)}
            >
              {/* Session Header */}
              <div style={styles.sessionHeader}>
                <div style={styles.sessionMeta}>
                  <span style={styles.timeAgo}>
                    {formatRelativeTime(session.start_time)}
                  </span>
                  <span 
                    style={{
                      ...styles.personalityTag,
                      backgroundColor: colors.bg,
                      color: colors.primary,
                    }}
                  >
                    {session.personality_name || 
                      session.personality_id.charAt(0).toUpperCase() + 
                      session.personality_id.slice(1).replace(/_/g, ' ')}
                  </span>
                </div>
                
                <div style={styles.sessionStats}>
                  <span style={styles.stat}>
                    💬 {session.message_count}
                  </span>
                  <span style={styles.stat}>
                    ⏱️ {formatDuration(session.start_time, session.end_time)}
                  </span>
                </div>
              </div>

              {/* Summary */}
              <p style={styles.summary}>
                {session.summary.length > (compact ? 100 : 200)
                  ? session.summary.slice(0, compact ? 100 : 200) + '...'
                  : session.summary}
              </p>

              {/* Topics */}
              {session.key_topics.length > 0 && (
                <div style={styles.topics}>
                  {session.key_topics.slice(0, compact ? 3 : 5).map((topic: string, i: number) => (
                    <span 
                      key={i} 
                      style={{
                        ...styles.topicTag,
                        backgroundColor: colors.bg,
                        color: colors.primary,
                      }}
                    >
                      {topic}
                    </span>
                  ))}
                  {session.key_topics.length > (compact ? 3 : 5) && (
                    <span style={styles.moreTopics}>
                      +{session.key_topics.length - (compact ? 3 : 5)} more
                    </span>
                  )}
                </div>
              )}

              {/* Milestone Badge */}
              {session.milestone_achieved && (
                <div style={styles.milestone}>
                  🏆 {session.milestone_achieved}
                </div>
              )}

              {/* Expanded Details */}
              {isExpanded && !compact && (
                <div style={styles.expandedContent}>
                  {/* Emotional Arc */}
                  {session.emotional_arc.length > 0 && (
                    <div style={styles.emotionalArc}>
                      <h4 style={styles.arcTitle}>Emotional Journey</h4>
                      <div style={styles.arcTrack}>
                        {session.emotional_arc.map((point: { timestamp: string; emotion: string; intensity: number }, i: number) => (
                          <div 
                            key={i} 
                            style={{
                              ...styles.arcPoint,
                              opacity: 0.5 + (point.intensity * 0.5),
                            }}
                            title={`${point.emotion} (${Math.round(point.intensity * 100)}%)`}
                          >
                            {getEmotionEmoji(point.emotion)}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Insights */}
                  {session.insights.length > 0 && (
                    <div style={styles.insights}>
                      <h4 style={styles.insightsTitle}>Key Insights</h4>
                      <ul style={styles.insightsList}>
                        {session.insights.map((insight: string, i: number) => (
                          <li key={i} style={styles.insightItem}>
                            💡 {insight}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Relationship Badge */}
                  {relationship && (
                    <div style={styles.relationshipSection}>
                      <RelationshipBadge
                        personalityId={session.personality_id}
                        personalityName={session.personality_name}
                        compact={false}
                        showProgress={true}
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Expand Indicator */}
              {!compact && (
                <div style={styles.expandIndicator}>
                  {isExpanded ? '▲ Less' : '▼ More'}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Load More Button */}
      {!compact && filteredSessions.length === maxSessions && allSessions.length > maxSessions && (
        <button 
          style={styles.loadMoreButton}
          onClick={() => {/* Would load more sessions */}}
        >
          Load More Sessions
        </button>
      )}
    </div>
  );
};

// Styles
const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: '1.5rem',
    maxWidth: '800px',
    margin: '0 auto',
  },
  containerCompact: {
    padding: '1rem',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1.5rem',
  },
  title: {
    margin: 0,
    fontSize: '1.5rem',
    fontWeight: '600',
    color: '#1e293b',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  titleIcon: {
    fontSize: '1.25rem',
  },
  filters: {
    display: 'flex',
    gap: '0.75rem',
  },
  filterSelect: {
    padding: '0.5rem 1rem',
    borderRadius: '0.5rem',
    border: '1px solid #e2e8f0',
    backgroundColor: '#ffffff',
    fontSize: '0.875rem',
    color: '#1e293b',
    cursor: 'pointer',
  },
  timeline: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  sessionCard: {
    background: '#ffffff',
    borderRadius: '0.75rem',
    padding: '1rem',
    borderLeft: '4px solid',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  sessionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '0.75rem',
  },
  sessionMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  },
  timeAgo: {
    fontSize: '0.75rem',
    color: '#64748b',
    fontWeight: '500',
  },
  personalityTag: {
    padding: '0.25rem 0.5rem',
    borderRadius: '0.375rem',
    fontSize: '0.75rem',
    fontWeight: '600',
    textTransform: 'capitalize' as const,
  },
  sessionStats: {
    display: 'flex',
    gap: '0.75rem',
  },
  stat: {
    fontSize: '0.75rem',
    color: '#64748b',
  },
  summary: {
    margin: '0 0 0.75rem 0',
    fontSize: '0.875rem',
    color: '#475569',
    lineHeight: '1.5',
  },
  topics: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '0.375rem',
    marginBottom: '0.5rem',
  },
  topicTag: {
    padding: '0.25rem 0.5rem',
    borderRadius: '0.25rem',
    fontSize: '0.7rem',
    fontWeight: '500',
  },
  moreTopics: {
    fontSize: '0.7rem',
    color: '#64748b',
    padding: '0.25rem 0.5rem',
  },
  milestone: {
    padding: '0.5rem 0.75rem',
    background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
    borderRadius: '0.5rem',
    fontSize: '0.75rem',
    fontWeight: '600',
    color: '#92400e',
    marginTop: '0.5rem',
  },
  expandedContent: {
    marginTop: '1rem',
    paddingTop: '1rem',
    borderTop: '1px solid #e2e8f0',
  },
  emotionalArc: {
    marginBottom: '1rem',
  },
  arcTitle: {
    margin: '0 0 0.5rem 0',
    fontSize: '0.8rem',
    fontWeight: '600',
    color: '#64748b',
  },
  arcTrack: {
    display: 'flex',
    gap: '0.5rem',
    flexWrap: 'wrap' as const,
  },
  arcPoint: {
    fontSize: '1.25rem',
    cursor: 'help',
    transition: 'transform 0.2s',
  },
  insights: {
    marginBottom: '1rem',
  },
  insightsTitle: {
    margin: '0 0 0.5rem 0',
    fontSize: '0.8rem',
    fontWeight: '600',
    color: '#64748b',
  },
  insightsList: {
    margin: 0,
    padding: '0 0 0 1rem',
    listStyle: 'none',
  },
  insightItem: {
    fontSize: '0.8rem',
    color: '#475569',
    marginBottom: '0.375rem',
    lineHeight: '1.4',
  },
  relationshipSection: {
    marginTop: '0.75rem',
  },
  expandIndicator: {
    textAlign: 'center' as const,
    fontSize: '0.7rem',
    color: '#94a3b8',
    marginTop: '0.5rem',
    fontWeight: '500',
  },
  loadMoreButton: {
    width: '100%',
    padding: '0.75rem',
    marginTop: '1rem',
    background: '#f8fafc',
    border: '1px dashed #cbd5e1',
    borderRadius: '0.5rem',
    color: '#64748b',
    fontSize: '0.875rem',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: '3rem 1.5rem',
  },
  emptyIcon: {
    fontSize: '3rem',
    marginBottom: '1rem',
  },
  emptyTitle: {
    margin: '0 0 0.5rem 0',
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#1e293b',
  },
  emptyText: {
    margin: '0 0 1.5rem 0',
    fontSize: '0.9rem',
    color: '#64748b',
  },
  startButton: {
    padding: '0.75rem 1.5rem',
    background: 'linear-gradient(135deg, #f97316 0%, #f59e0b 100%)',
    border: 'none',
    borderRadius: '0.5rem',
    color: '#ffffff',
    fontSize: '0.9rem',
    fontWeight: '600',
    cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(249, 115, 22, 0.3)',
    transition: 'all 0.2s',
  },
};

export default ConversationTimeline;
