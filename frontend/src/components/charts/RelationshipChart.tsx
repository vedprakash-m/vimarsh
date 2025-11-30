/**
 * Relationship Evolution Chart Component
 * 
 * Visualizes the growth of relationship depth over time with a personality.
 * Uses SVG-based chart for lightweight rendering without external dependencies.
 * 
 * Part of Phase 3: Frontend Memory UX - Visualization Charts.
 * 
 * Features:
 * - Line chart showing depth progression
 * - Milestone markers
 * - Interactive hover states
 * - Responsive design
 */

import React, { useMemo, useState } from 'react';
import { useMemory, RelationshipDepth } from '../../contexts/MemoryContext';

interface DataPoint {
  date: string;
  depth: RelationshipDepth;
  interactionCount: number;
  milestone?: string;
}

interface RelationshipChartProps {
  personalityId: string;
  personalityName?: string;
  data?: DataPoint[];
  height?: number;
  showMilestones?: boolean;
  className?: string;
}

// Depth level to numeric value for charting
const DEPTH_VALUES: Record<RelationshipDepth, number> = {
  stranger: 0,
  acquaintance: 1,
  familiar: 2,
  trusted: 3,
  kindred: 4,
};

// Depth level labels
const DEPTH_LABELS: Record<RelationshipDepth, string> = {
  stranger: 'New Seeker',
  acquaintance: 'Awakening',
  familiar: 'Growing Bond',
  trusted: 'Deep Trust',
  kindred: 'Kindred Spirit',
};

// Domain colors for chart
const getDomainColor = (domain: string) => {
  const colors: Record<string, { primary: string; gradient: string }> = {
    spiritual: { 
      primary: '#f97316', 
      gradient: 'url(#spiritualGradient)' 
    },
    philosophical: { 
      primary: '#8b5cf6', 
      gradient: 'url(#philosophicalGradient)' 
    },
    leadership: { 
      primary: '#3b82f6', 
      gradient: 'url(#leadershipGradient)' 
    },
    scientific: { 
      primary: '#10b981', 
      gradient: 'url(#scientificGradient)' 
    },
    literary: { 
      primary: '#ec4899', 
      gradient: 'url(#literaryGradient)' 
    },
    psychology: { 
      primary: '#f59e0b', 
      gradient: 'url(#psychologyGradient)' 
    },
  };
  return colors[domain] || colors.spiritual;
};

// Get personality domain
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

// Format date for display
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

export const RelationshipChart: React.FC<RelationshipChartProps> = ({
  personalityId,
  personalityName,
  data = [],
  height = 200,
  showMilestones = true,
  className = '',
}) => {
  const { getRelationship, recentSessions } = useMemory();
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);

  const relationship = getRelationship(personalityId);
  const domain = getPersonalityDomain(personalityId);
  const colors = getDomainColor(domain);

  // Generate sample data if not provided
  const chartData: DataPoint[] = useMemo(() => {
    if (data.length > 0) return data;

    // Build data from recent sessions for this personality
    const personalitySessions = recentSessions.filter(
      (s) => s.personalityId === personalityId
    );

    if (personalitySessions.length === 0) {
      // Generate sample progression
      const now = new Date();
      return [
        {
          date: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          depth: 'stranger' as RelationshipDepth,
          interactionCount: 0,
        },
        {
          date: now.toISOString(),
          depth: relationship?.depth || 'stranger',
          interactionCount: relationship?.interactionCount || 0,
        },
      ];
    }

    // Map sessions to data points
    return personalitySessions.map((session, index) => ({
      date: session.sessionStart,
      depth: calculateDepthAtSession(index, personalitySessions.length),
      interactionCount: session.messageCount,
      milestone: session.keyInsights[0],
    }));
  }, [data, recentSessions, personalityId, relationship]);

  // SVG dimensions
  const width = 300;
  const padding = { top: 20, right: 20, bottom: 40, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Calculate scales
  const xScale = useMemo(() => {
    const dates = chartData.map((d) => new Date(d.date).getTime());
    const minDate = Math.min(...dates);
    const maxDate = Math.max(...dates);
    const range = maxDate - minDate || 1;
    
    return (date: string) => {
      const timestamp = new Date(date).getTime();
      return ((timestamp - minDate) / range) * chartWidth;
    };
  }, [chartData, chartWidth]);

  const yScale = useMemo(() => {
    return (depth: RelationshipDepth) => {
      const value = DEPTH_VALUES[depth];
      return chartHeight - (value / 4) * chartHeight;
    };
  }, [chartHeight]);

  // Generate path
  const linePath = useMemo(() => {
    if (chartData.length < 2) return '';
    
    const points = chartData.map((d) => ({
      x: padding.left + xScale(d.date),
      y: padding.top + yScale(d.depth),
    }));

    return points
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
      .join(' ');
  }, [chartData, xScale, yScale, padding]);

  // Area fill path
  const areaPath = useMemo(() => {
    if (chartData.length < 2) return '';
    
    const points = chartData.map((d) => ({
      x: padding.left + xScale(d.date),
      y: padding.top + yScale(d.depth),
    }));

    const bottomY = padding.top + chartHeight;
    const startX = points[0].x;
    const endX = points[points.length - 1].x;

    return `${linePath} L ${endX} ${bottomY} L ${startX} ${bottomY} Z`;
  }, [linePath, chartData, xScale, chartHeight, padding]);

  return (
    <div style={styles.container} className={className}>
      <div style={styles.header}>
        <h3 style={styles.title}>
          {personalityName || personalityId.charAt(0).toUpperCase() + personalityId.slice(1).replace(/_/g, ' ')}
        </h3>
        <span 
          style={{
            ...styles.currentLevel,
            backgroundColor: colors.primary + '20',
            color: colors.primary,
          }}
        >
          {DEPTH_LABELS[relationship?.depth || 'stranger']}
        </span>
      </div>

      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} style={styles.svg}>
        {/* Gradients */}
        <defs>
          <linearGradient id="spiritualGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#f97316" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#f97316" stopOpacity="0.05" />
          </linearGradient>
          <linearGradient id="philosophicalGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.05" />
          </linearGradient>
          <linearGradient id="leadershipGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.05" />
          </linearGradient>
          <linearGradient id="scientificGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0.05" />
          </linearGradient>
          <linearGradient id="literaryGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#ec4899" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#ec4899" stopOpacity="0.05" />
          </linearGradient>
          <linearGradient id="psychologyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.05" />
          </linearGradient>
        </defs>

        {/* Y-axis grid lines and labels */}
        {Object.entries(DEPTH_VALUES).map(([depth, value]) => {
          const y = padding.top + chartHeight - (value / 4) * chartHeight;
          return (
            <g key={depth}>
              <line
                x1={padding.left}
                y1={y}
                x2={padding.left + chartWidth}
                y2={y}
                stroke="#e2e8f0"
                strokeDasharray="4"
              />
              <text
                x={padding.left - 8}
                y={y}
                textAnchor="end"
                dominantBaseline="middle"
                style={styles.axisLabel}
              >
                {DEPTH_LABELS[depth as RelationshipDepth].split(' ')[0]}
              </text>
            </g>
          );
        })}

        {/* Area fill */}
        {areaPath && (
          <path
            d={areaPath}
            fill={colors.gradient}
          />
        )}

        {/* Line */}
        {linePath && (
          <path
            d={linePath}
            fill="none"
            stroke={colors.primary}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Data points */}
        {chartData.map((point, index) => {
          const x = padding.left + xScale(point.date);
          const y = padding.top + yScale(point.depth);
          const isHovered = hoveredPoint === index;

          return (
            <g key={index}>
              {/* Point */}
              <circle
                cx={x}
                cy={y}
                r={isHovered ? 8 : 5}
                fill={colors.primary}
                stroke="#ffffff"
                strokeWidth="2"
                style={{ cursor: 'pointer', transition: 'all 0.2s' }}
                onMouseEnter={() => setHoveredPoint(index)}
                onMouseLeave={() => setHoveredPoint(null)}
              />

              {/* Milestone marker */}
              {showMilestones && point.milestone && (
                <text
                  x={x}
                  y={y - 15}
                  textAnchor="middle"
                  style={styles.milestoneMarker}
                >
                  🏆
                </text>
              )}

              {/* Hover tooltip */}
              {isHovered && (
                <g>
                  <rect
                    x={x - 60}
                    y={y - 55}
                    width={120}
                    height={45}
                    rx={6}
                    fill="#1e293b"
                    fillOpacity={0.95}
                  />
                  <text
                    x={x}
                    y={y - 38}
                    textAnchor="middle"
                    style={styles.tooltipText}
                  >
                    {DEPTH_LABELS[point.depth]}
                  </text>
                  <text
                    x={x}
                    y={y - 22}
                    textAnchor="middle"
                    style={styles.tooltipSubtext}
                  >
                    {formatDate(point.date)} • {point.interactionCount} msgs
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* X-axis labels */}
        {chartData.length > 1 && (
          <>
            <text
              x={padding.left}
              y={height - 10}
              textAnchor="start"
              style={styles.axisLabel}
            >
              {formatDate(chartData[0].date)}
            </text>
            <text
              x={padding.left + chartWidth}
              y={height - 10}
              textAnchor="end"
              style={styles.axisLabel}
            >
              {formatDate(chartData[chartData.length - 1].date)}
            </text>
          </>
        )}
      </svg>

      {/* Legend */}
      <div style={styles.legend}>
        <div style={styles.legendItem}>
          <span 
            style={{
              ...styles.legendDot,
              backgroundColor: colors.primary,
            }}
          />
          <span>Relationship Growth</span>
        </div>
        {showMilestones && (
          <div style={styles.legendItem}>
            <span>🏆</span>
            <span>Milestone</span>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function to estimate depth at a session
function calculateDepthAtSession(sessionIndex: number, totalSessions: number): RelationshipDepth {
  const progress = sessionIndex / totalSessions;
  if (progress < 0.1) return 'stranger';
  if (progress < 0.25) return 'acquaintance';
  if (progress < 0.5) return 'familiar';
  if (progress < 0.75) return 'trusted';
  return 'kindred';
}

// Styles
const styles: Record<string, React.CSSProperties> = {
  container: {
    background: '#ffffff',
    borderRadius: '0.75rem',
    padding: '1rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.75rem',
  },
  title: {
    margin: 0,
    fontSize: '0.9rem',
    fontWeight: '600',
    color: '#1e293b',
  },
  currentLevel: {
    padding: '0.25rem 0.5rem',
    borderRadius: '0.375rem',
    fontSize: '0.7rem',
    fontWeight: '600',
  },
  svg: {
    display: 'block',
    overflow: 'visible',
  },
  axisLabel: {
    fontSize: '10px',
    fill: '#94a3b8',
    fontWeight: 500,
  },
  milestoneMarker: {
    fontSize: '14px',
  },
  tooltipText: {
    fontSize: '11px',
    fill: '#ffffff',
    fontWeight: 600,
  },
  tooltipSubtext: {
    fontSize: '9px',
    fill: '#94a3b8',
  },
  legend: {
    display: 'flex',
    justifyContent: 'center',
    gap: '1rem',
    marginTop: '0.75rem',
    paddingTop: '0.75rem',
    borderTop: '1px solid #f1f5f9',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.375rem',
    fontSize: '0.7rem',
    color: '#64748b',
  },
  legendDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
};

export default RelationshipChart;
