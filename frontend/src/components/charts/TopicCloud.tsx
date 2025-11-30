/**
 * Topic Cloud Component
 * 
 * Word cloud visualization of conversation themes and topics.
 * Uses weighted sizing based on topic frequency.
 * 
 * Part of Phase 3: Frontend Memory UX - Visualization Charts.
 * 
 * Features:
 * - Dynamic word sizing based on frequency
 * - Domain-colored topics
 * - Interactive hover states
 * - Responsive layout
 */

import React, { useMemo, useState, useCallback } from 'react';
import { useMemory } from '../../contexts/MemoryContext';

interface TopicWeight {
  topic: string;
  weight: number;
  domain?: string;
  lastDiscussed?: string;
}

interface TopicCloudProps {
  topics?: TopicWeight[];
  personalityId?: string;
  maxTopics?: number;
  onTopicClick?: (topic: string) => void;
  className?: string;
}

// Domain color mapping
const getDomainColor = (domain?: string): string => {
  const colors: Record<string, string> = {
    spiritual: '#f97316',
    philosophical: '#8b5cf6',
    leadership: '#3b82f6',
    scientific: '#10b981',
    literary: '#ec4899',
    psychology: '#f59e0b',
    default: '#64748b',
  };
  return colors[domain || 'default'] || colors.default;
};

// Categorize topics into domains based on keywords
const categorizeTopic = (topic: string): string => {
  const lowerTopic = topic.toLowerCase();
  
  const domainKeywords: Record<string, string[]> = {
    spiritual: ['dharma', 'karma', 'soul', 'meditation', 'enlightenment', 'divine', 'peace', 'prayer', 'faith', 'god', 'moksha', 'nirvana', 'spiritual', 'sacred', 'devotion'],
    philosophical: ['ethics', 'virtue', 'truth', 'wisdom', 'meaning', 'existence', 'morality', 'logic', 'knowledge', 'reality', 'stoic', 'philosophy', 'reason', 'justice'],
    leadership: ['leadership', 'strategy', 'governance', 'decision', 'power', 'influence', 'management', 'politics', 'reform', 'revolution', 'vision', 'success'],
    scientific: ['science', 'physics', 'mathematics', 'experiment', 'theory', 'discovery', 'universe', 'nature', 'energy', 'matter', 'logic', 'reason', 'invention'],
    literary: ['poetry', 'art', 'beauty', 'creativity', 'expression', 'writing', 'literature', 'drama', 'story', 'metaphor', 'imagination', 'culture'],
    psychology: ['mind', 'psychology', 'behavior', 'emotion', 'unconscious', 'consciousness', 'mental', 'personality', 'therapy', 'dream', 'anxiety', 'happiness'],
  };

  for (const [domain, keywords] of Object.entries(domainKeywords)) {
    if (keywords.some((kw) => lowerTopic.includes(kw))) {
      return domain;
    }
  }
  return 'default';
};

// Calculate font size based on weight
const calculateFontSize = (weight: number, minWeight: number, maxWeight: number): number => {
  const minSize = 12;
  const maxSize = 28;
  
  if (maxWeight === minWeight) return (minSize + maxSize) / 2;
  
  const normalized = (weight - minWeight) / (maxWeight - minWeight);
  return minSize + normalized * (maxSize - minSize);
};

// Format relative time
const formatRelativeTime = (dateString?: string): string => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffDays < 1) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
  return `${Math.floor(diffDays / 30)}mo ago`;
};

export const TopicCloud: React.FC<TopicCloudProps> = ({
  topics = [],
  personalityId,
  maxTopics = 30,
  onTopicClick,
  className = '',
}) => {
  const { recentSessions, memoryProfile } = useMemory();
  const [hoveredTopic, setHoveredTopic] = useState<string | null>(null);

  // Aggregate topics from sessions if not provided
  const aggregatedTopics = useMemo((): TopicWeight[] => {
    if (topics.length > 0) return topics;

    // Collect topics from recent sessions
    const topicCounts = new Map<string, { count: number; lastSeen: string }>();

    // Filter sessions by personality if specified
    const filteredSessions = personalityId
      ? recentSessions.filter((s) => s.personalityId === personalityId)
      : recentSessions;

    filteredSessions.forEach((session) => {
      session.topicsDiscussed.forEach((topic) => {
        const existing = topicCounts.get(topic);
        if (existing) {
          existing.count++;
          if (new Date(session.sessionEnd) > new Date(existing.lastSeen)) {
            existing.lastSeen = session.sessionEnd;
          }
        } else {
          topicCounts.set(topic, { count: 1, lastSeen: session.sessionEnd });
        }
      });
    });

    // Also include topics from memory profile if available
    if (memoryProfile?.philosophicalInterests) {
      memoryProfile.philosophicalInterests.forEach((interest) => {
        const existing = topicCounts.get(interest);
        if (!existing) {
          topicCounts.set(interest, { count: 2, lastSeen: memoryProfile.lastActiveAt });
        }
      });
    }

    // Convert to array and sort by count
    return Array.from(topicCounts.entries())
      .map(([topic, data]) => ({
        topic,
        weight: data.count,
        domain: categorizeTopic(topic),
        lastDiscussed: data.lastSeen,
      }))
      .sort((a, b) => b.weight - a.weight)
      .slice(0, maxTopics);
  }, [topics, recentSessions, personalityId, memoryProfile, maxTopics]);

  // Calculate min/max weights for sizing
  const [minWeight, maxWeight] = useMemo(() => {
    if (aggregatedTopics.length === 0) return [1, 1];
    const weights = aggregatedTopics.map((t) => t.weight);
    return [Math.min(...weights), Math.max(...weights)];
  }, [aggregatedTopics]);

  // Handle topic click
  const handleTopicClick = useCallback((topic: string) => {
    if (onTopicClick) {
      onTopicClick(topic);
    }
  }, [onTopicClick]);

  if (aggregatedTopics.length === 0) {
    return (
      <div style={styles.emptyState} className={className}>
        <div style={styles.emptyIcon}>🏷️</div>
        <p style={styles.emptyText}>
          No topics yet. Start exploring wisdom to see your interests here.
        </p>
      </div>
    );
  }

  return (
    <div style={styles.container} className={className}>
      <div style={styles.header}>
        <h3 style={styles.title}>
          <span style={styles.titleIcon}>🏷️</span>
          Your Topics of Interest
        </h3>
        <span style={styles.topicCount}>
          {aggregatedTopics.length} topics explored
        </span>
      </div>

      <div style={styles.cloudContainer}>
        {aggregatedTopics.map((topicData, index) => {
          const fontSize = calculateFontSize(topicData.weight, minWeight, maxWeight);
          const color = getDomainColor(topicData.domain);
          const isHovered = hoveredTopic === topicData.topic;

          return (
            <div
              key={index}
              style={{
                ...styles.topicTag,
                fontSize: `${fontSize}px`,
                color: isHovered ? '#ffffff' : color,
                backgroundColor: isHovered ? color : `${color}15`,
                borderColor: color,
                transform: isHovered ? 'scale(1.1)' : 'scale(1)',
                cursor: onTopicClick ? 'pointer' : 'default',
              }}
              onMouseEnter={() => setHoveredTopic(topicData.topic)}
              onMouseLeave={() => setHoveredTopic(null)}
              onClick={() => handleTopicClick(topicData.topic)}
              title={`${topicData.topic} (${topicData.weight} mentions${topicData.lastDiscussed ? `, last: ${formatRelativeTime(topicData.lastDiscussed)}` : ''})`}
            >
              {topicData.topic}
              {topicData.weight > 3 && (
                <span style={styles.weightBadge}>
                  {topicData.weight}
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Domain Legend */}
      <div style={styles.legend}>
        {[
          { domain: 'spiritual', label: 'Spiritual' },
          { domain: 'philosophical', label: 'Philosophical' },
          { domain: 'leadership', label: 'Leadership' },
          { domain: 'scientific', label: 'Scientific' },
          { domain: 'literary', label: 'Literary' },
          { domain: 'psychology', label: 'Psychology' },
        ].map(({ domain, label }) => (
          <div key={domain} style={styles.legendItem}>
            <span 
              style={{
                ...styles.legendDot,
                backgroundColor: getDomainColor(domain),
              }}
            />
            <span>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Styles
const styles: Record<string, React.CSSProperties> = {
  container: {
    background: '#ffffff',
    borderRadius: '0.75rem',
    padding: '1.25rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  title: {
    margin: 0,
    fontSize: '1rem',
    fontWeight: '600',
    color: '#1e293b',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  titleIcon: {
    fontSize: '1.125rem',
  },
  topicCount: {
    fontSize: '0.75rem',
    color: '#64748b',
    fontWeight: '500',
  },
  cloudContainer: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '0.5rem',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '120px',
    padding: '0.5rem',
  },
  topicTag: {
    padding: '0.375rem 0.75rem',
    borderRadius: '0.5rem',
    border: '1px solid',
    fontWeight: 500,
    transition: 'all 0.2s ease',
    whiteSpace: 'nowrap' as const,
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.25rem',
  },
  weightBadge: {
    fontSize: '10px',
    fontWeight: 600,
    padding: '0 4px',
    borderRadius: '4px',
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    marginLeft: '4px',
  },
  legend: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    justifyContent: 'center',
    gap: '0.75rem',
    marginTop: '1rem',
    paddingTop: '1rem',
    borderTop: '1px solid #f1f5f9',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.25rem',
    fontSize: '0.65rem',
    color: '#64748b',
  },
  legendDot: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
  },
  emptyState: {
    background: '#ffffff',
    borderRadius: '0.75rem',
    padding: '2rem',
    textAlign: 'center' as const,
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
  },
  emptyIcon: {
    fontSize: '2rem',
    marginBottom: '0.75rem',
  },
  emptyText: {
    margin: 0,
    fontSize: '0.875rem',
    color: '#64748b',
    lineHeight: '1.5',
  },
};

export default TopicCloud;
