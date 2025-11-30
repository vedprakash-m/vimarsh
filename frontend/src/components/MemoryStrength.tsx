/**
 * Memory Strength Indicator Component
 * 
 * Visual indicator showing the strength and quality of memory context
 * for the current conversation. Displays token usage, context depth,
 * and memory layer breakdown.
 * 
 * Part of Phase 3: Frontend Memory UX - Visualization Charts.
 * 
 * Features:
 * - Overall memory strength meter
 * - Layer breakdown (working, core, episodic, semantic)
 * - Token budget visualization
 * - Context quality score
 */

import React, { useMemo } from 'react';
import { useMemory, WorkingMemoryContext } from '../contexts/MemoryContext';

interface MemoryLayerBreakdown {
  working: number;
  core: number;
  episodic: number;
  semantic: number;
}

interface MemoryStrengthProps {
  context?: WorkingMemoryContext | null;
  breakdown?: MemoryLayerBreakdown;
  compact?: boolean;
  showDetails?: boolean;
  className?: string;
}

// Token budgets per layer (from architecture spec)
const TOKEN_BUDGETS = {
  working: 16000,
  core: 4000,
  episodic: 8000,
  semantic: 4000,
  total: 32000,
};

// Layer configurations
const LAYER_CONFIG = {
  working: {
    name: 'Working Memory',
    icon: '⚡',
    color: '#3b82f6',
    description: 'Active conversation context',
  },
  core: {
    name: 'Core Memory',
    icon: '💎',
    color: '#f97316',
    description: 'Your profile & preferences',
  },
  episodic: {
    name: 'Episodic Memory',
    icon: '📚',
    color: '#8b5cf6',
    description: 'Past session summaries',
  },
  semantic: {
    name: 'Semantic Archive',
    icon: '🔮',
    color: '#10b981',
    description: 'Deep knowledge retrieval',
  },
};

// Calculate strength percentage
const calculateStrength = (usedTokens: number, totalBudget: number): number => {
  // Strength is higher when we're using more context effectively
  // but not maxing out the budget (which could mean truncation)
  const usage = usedTokens / totalBudget;
  
  if (usage < 0.2) return usage * 2; // Low usage = lower strength
  if (usage < 0.7) return 0.4 + (usage - 0.2) * 1.2; // Sweet spot
  if (usage < 0.9) return 1.0; // Optimal
  return 1.0 - (usage - 0.9) * 2; // Over 90% = diminishing returns
};

// Get strength label
const getStrengthLabel = (strength: number): { label: string; color: string } => {
  if (strength >= 0.8) return { label: 'Excellent', color: '#22c55e' };
  if (strength >= 0.6) return { label: 'Strong', color: '#84cc16' };
  if (strength >= 0.4) return { label: 'Good', color: '#f59e0b' };
  if (strength >= 0.2) return { label: 'Building', color: '#f97316' };
  return { label: 'New', color: '#94a3b8' };
};

export const MemoryStrength: React.FC<MemoryStrengthProps> = ({
  context,
  breakdown,
  compact = false,
  showDetails = true,
  className = '',
}) => {
  const { currentSession, memoryProfile, recentSessions } = useMemory();
  
  // Use provided context or current session
  const activeContext = context || currentSession;

  // Calculate layer breakdown
  const layerBreakdown = useMemo((): MemoryLayerBreakdown => {
    if (breakdown) return breakdown;

    // Estimate from available data
    const workingTokens = activeContext?.tokenCount || 0;
    const coreTokens = memoryProfile 
      ? Math.min(500 + (memoryProfile.totalMessages * 2), TOKEN_BUDGETS.core)
      : 0;
    const episodicTokens = recentSessions.length * 300; // ~300 tokens per session summary
    const semanticTokens = activeContext?.activeMemories?.length 
      ? activeContext.activeMemories.length * 200 
      : 0;

    return {
      working: workingTokens,
      core: coreTokens,
      episodic: Math.min(episodicTokens, TOKEN_BUDGETS.episodic),
      semantic: Math.min(semanticTokens, TOKEN_BUDGETS.semantic),
    };
  }, [breakdown, activeContext, memoryProfile, recentSessions]);

  // Calculate total tokens and strength
  const totalTokens = Object.values(layerBreakdown).reduce((a, b) => a + b, 0);
  const strength = calculateStrength(totalTokens, TOKEN_BUDGETS.total);
  const strengthInfo = getStrengthLabel(strength);

  // Compact view
  if (compact) {
    return (
      <div style={styles.compactContainer} className={className}>
        <div style={styles.compactMeter}>
          <div 
            style={{
              ...styles.compactFill,
              width: `${strength * 100}%`,
              background: strengthInfo.color,
            }}
          />
        </div>
        <span 
          style={{
            ...styles.compactLabel,
            color: strengthInfo.color,
          }}
        >
          🧠 {strengthInfo.label}
        </span>
      </div>
    );
  }

  return (
    <div style={styles.container} className={className}>
      {/* Header with overall strength */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <span style={styles.headerIcon}>🧠</span>
          <div>
            <h3 style={styles.title}>Memory Strength</h3>
            <p style={styles.subtitle}>
              {totalTokens.toLocaleString()} / {TOKEN_BUDGETS.total.toLocaleString()} tokens
            </p>
          </div>
        </div>
        <div 
          style={{
            ...styles.strengthBadge,
            backgroundColor: strengthInfo.color + '20',
            color: strengthInfo.color,
            borderColor: strengthInfo.color,
          }}
        >
          {strengthInfo.label}
        </div>
      </div>

      {/* Overall strength meter */}
      <div style={styles.meterContainer}>
        <div style={styles.meter}>
          <div 
            style={{
              ...styles.meterFill,
              width: `${strength * 100}%`,
              background: `linear-gradient(90deg, ${strengthInfo.color}80, ${strengthInfo.color})`,
            }}
          />
          {/* Optimal zone indicator */}
          <div style={styles.optimalZone} />
        </div>
        <div style={styles.meterLabels}>
          <span>0%</span>
          <span>Optimal Zone</span>
          <span>100%</span>
        </div>
      </div>

      {/* Layer breakdown */}
      {showDetails && (
        <div style={styles.layersContainer}>
          <h4 style={styles.layersTitle}>Memory Layers</h4>
          
          {(Object.entries(LAYER_CONFIG) as Array<[keyof typeof LAYER_CONFIG, typeof LAYER_CONFIG[keyof typeof LAYER_CONFIG]]>).map(([key, config]) => {
            const tokens = layerBreakdown[key];
            const budget = TOKEN_BUDGETS[key];
            const percentage = (tokens / budget) * 100;

            return (
              <div key={key} style={styles.layerRow}>
                <div style={styles.layerInfo}>
                  <span style={styles.layerIcon}>{config.icon}</span>
                  <div style={styles.layerText}>
                    <span style={styles.layerName}>{config.name}</span>
                    <span style={styles.layerDesc}>{config.description}</span>
                  </div>
                </div>
                <div style={styles.layerMeter}>
                  <div style={styles.layerBar}>
                    <div 
                      style={{
                        ...styles.layerFill,
                        width: `${Math.min(percentage, 100)}%`,
                        backgroundColor: config.color,
                      }}
                    />
                  </div>
                  <span style={styles.layerTokens}>
                    {tokens.toLocaleString()}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Context quality indicators */}
      {showDetails && activeContext && (
        <div style={styles.qualityContainer}>
          <h4 style={styles.layersTitle}>Context Quality</h4>
          <div style={styles.qualityGrid}>
            <div style={styles.qualityItem}>
              <span style={styles.qualityValue}>
                {activeContext.recentMessages?.length || 0}
              </span>
              <span style={styles.qualityLabel}>Messages</span>
            </div>
            <div style={styles.qualityItem}>
              <span style={styles.qualityValue}>
                {activeContext.currentTopics?.length || 0}
              </span>
              <span style={styles.qualityLabel}>Topics</span>
            </div>
            <div style={styles.qualityItem}>
              <span style={styles.qualityValue}>
                {activeContext.activeMemories?.length || 0}
              </span>
              <span style={styles.qualityLabel}>Memories</span>
            </div>
            <div style={styles.qualityItem}>
              <span style={styles.qualityEmoji}>
                {activeContext.emotionalState === 'peaceful' ? '😌' :
                 activeContext.emotionalState === 'curious' ? '🤔' :
                 activeContext.emotionalState === 'grateful' ? '🙏' :
                 activeContext.emotionalState === 'inspired' ? '✨' :
                 '💭'}
              </span>
              <span style={styles.qualityLabel}>Mood</span>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {showDetails && strength < 0.6 && (
        <div style={styles.recommendations}>
          <h4 style={styles.recTitle}>💡 Tips to Strengthen Memory</h4>
          <ul style={styles.recList}>
            {layerBreakdown.core < 500 && (
              <li>Share more about your interests to build your profile</li>
            )}
            {layerBreakdown.episodic < 1000 && (
              <li>Have more conversations to build session history</li>
            )}
            {layerBreakdown.working < 2000 && (
              <li>Continue this conversation to deepen context</li>
            )}
          </ul>
        </div>
      )}
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
    alignItems: 'flex-start',
    marginBottom: '1rem',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  },
  headerIcon: {
    fontSize: '2rem',
  },
  title: {
    margin: 0,
    fontSize: '1rem',
    fontWeight: '600',
    color: '#1e293b',
  },
  subtitle: {
    margin: '0.125rem 0 0 0',
    fontSize: '0.75rem',
    color: '#64748b',
  },
  strengthBadge: {
    padding: '0.375rem 0.75rem',
    borderRadius: '0.5rem',
    fontSize: '0.8rem',
    fontWeight: '600',
    border: '1px solid',
  },
  meterContainer: {
    marginBottom: '1.25rem',
  },
  meter: {
    height: '8px',
    backgroundColor: '#f1f5f9',
    borderRadius: '4px',
    overflow: 'hidden',
    position: 'relative',
  },
  meterFill: {
    height: '100%',
    borderRadius: '4px',
    transition: 'width 0.5s ease',
  },
  optimalZone: {
    position: 'absolute',
    left: '60%',
    right: '10%',
    top: 0,
    bottom: 0,
    backgroundColor: 'rgba(34, 197, 94, 0.1)',
    borderLeft: '2px dashed rgba(34, 197, 94, 0.3)',
    borderRight: '2px dashed rgba(34, 197, 94, 0.3)',
  },
  meterLabels: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '0.25rem',
    fontSize: '0.65rem',
    color: '#94a3b8',
  },
  layersContainer: {
    marginBottom: '1rem',
  },
  layersTitle: {
    margin: '0 0 0.75rem 0',
    fontSize: '0.75rem',
    fontWeight: '600',
    color: '#64748b',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
  },
  layerRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '0.5rem 0',
    borderBottom: '1px solid #f8fafc',
  },
  layerInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    flex: 1,
  },
  layerIcon: {
    fontSize: '1rem',
    width: '1.5rem',
    textAlign: 'center' as const,
  },
  layerText: {
    display: 'flex',
    flexDirection: 'column',
  },
  layerName: {
    fontSize: '0.8rem',
    fontWeight: '500',
    color: '#1e293b',
  },
  layerDesc: {
    fontSize: '0.65rem',
    color: '#94a3b8',
  },
  layerMeter: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    width: '120px',
  },
  layerBar: {
    flex: 1,
    height: '4px',
    backgroundColor: '#f1f5f9',
    borderRadius: '2px',
    overflow: 'hidden',
  },
  layerFill: {
    height: '100%',
    borderRadius: '2px',
    transition: 'width 0.3s ease',
  },
  layerTokens: {
    fontSize: '0.7rem',
    color: '#64748b',
    minWidth: '32px',
    textAlign: 'right' as const,
  },
  qualityContainer: {
    marginTop: '1rem',
    paddingTop: '1rem',
    borderTop: '1px solid #f1f5f9',
  },
  qualityGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '0.5rem',
  },
  qualityItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '0.5rem',
    background: '#f8fafc',
    borderRadius: '0.5rem',
  },
  qualityValue: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#1e293b',
  },
  qualityEmoji: {
    fontSize: '1.25rem',
  },
  qualityLabel: {
    fontSize: '0.65rem',
    color: '#64748b',
    marginTop: '0.125rem',
  },
  recommendations: {
    marginTop: '1rem',
    padding: '0.75rem',
    background: 'rgba(59, 130, 246, 0.05)',
    borderRadius: '0.5rem',
    border: '1px solid rgba(59, 130, 246, 0.1)',
  },
  recTitle: {
    margin: '0 0 0.5rem 0',
    fontSize: '0.8rem',
    fontWeight: '600',
    color: '#3b82f6',
  },
  recList: {
    margin: 0,
    padding: '0 0 0 1.25rem',
    fontSize: '0.75rem',
    color: '#64748b',
    lineHeight: 1.6,
  },
  compactContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  compactMeter: {
    width: '40px',
    height: '4px',
    backgroundColor: '#f1f5f9',
    borderRadius: '2px',
    overflow: 'hidden',
  },
  compactFill: {
    height: '100%',
    borderRadius: '2px',
    transition: 'width 0.3s ease',
  },
  compactLabel: {
    fontSize: '0.7rem',
    fontWeight: '500',
  },
};

export default MemoryStrength;
