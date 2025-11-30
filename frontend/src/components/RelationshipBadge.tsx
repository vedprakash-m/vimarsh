/**
 * Relationship Badge Component
 * 
 * Displays the relationship depth between user and personality
 * with visual progression and spiritual theming.
 * 
 * Features:
 * - Depth level visualization (5 levels)
 * - Progress bar to next level
 * - Interaction count
 * - Last interaction time
 */

import React, { useState } from 'react';
import { useMemory, RelationshipDepth } from '../contexts/MemoryContext';

// Relationship depth configurations
const DEPTH_CONFIG: Record<RelationshipDepth, {
  label: string;
  emoji: string;
  color: string;
  bgColor: string;
  description: string;
  threshold: number;
}> = {
  stranger: {
    label: 'New Seeker',
    emoji: '🌱',
    color: '#94a3b8',
    bgColor: 'rgba(148, 163, 184, 0.15)',
    description: 'Beginning the journey',
    threshold: 0
  },
  acquaintance: {
    label: 'Awakening',
    emoji: '🌿',
    color: '#22c55e',
    bgColor: 'rgba(34, 197, 94, 0.15)',
    description: 'Seeds of understanding',
    threshold: 3
  },
  familiar: {
    label: 'Growing Bond',
    emoji: '🌸',
    color: '#f59e0b',
    bgColor: 'rgba(245, 158, 11, 0.15)',
    description: 'Deepening connection',
    threshold: 10
  },
  trusted: {
    label: 'Deep Trust',
    emoji: '🔥',
    color: '#ef4444',
    bgColor: 'rgba(239, 68, 68, 0.15)',
    description: 'Profound understanding',
    threshold: 25
  },
  kindred: {
    label: 'Kindred Spirit',
    emoji: '✨',
    color: '#a855f7',
    bgColor: 'rgba(168, 85, 247, 0.15)',
    description: 'Spiritual kinship',
    threshold: 50
  }
};

// Thresholds for progression
const THRESHOLDS = [0, 3, 10, 25, 50];
const DEPTH_LEVELS: RelationshipDepth[] = ['stranger', 'acquaintance', 'familiar', 'trusted', 'kindred'];

interface RelationshipBadgeProps {
  personalityId: string;
  personalityName?: string;
  compact?: boolean;
  showProgress?: boolean;
  className?: string;
}

export const RelationshipBadge: React.FC<RelationshipBadgeProps> = ({
  personalityId,
  personalityName,
  compact = false,
  showProgress = true,
  className = ''
}) => {
  const memory = useMemory();
  const [isHovered, setIsHovered] = useState(false);
  
  const relationship = memory.getRelationship(personalityId);
  const depth: RelationshipDepth = relationship?.depth || 'stranger';
  const config = DEPTH_CONFIG[depth];
  const interactionCount = relationship?.interactionCount || 0;
  
  // Calculate progress to next level
  const currentLevelIndex = DEPTH_LEVELS.indexOf(depth);
  const nextLevelIndex = Math.min(currentLevelIndex + 1, DEPTH_LEVELS.length - 1);
  const currentThreshold = THRESHOLDS[currentLevelIndex];
  const nextThreshold = THRESHOLDS[nextLevelIndex];
  
  let progress = 100;
  if (currentLevelIndex < DEPTH_LEVELS.length - 1) {
    const range = nextThreshold - currentThreshold;
    const current = interactionCount - currentThreshold;
    progress = Math.min(100, (current / range) * 100);
  }
  
  if (compact) {
    return (
      <div
        className={`relationship-badge relationship-badge--compact ${className}`}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
          padding: '0.25rem 0.5rem',
          backgroundColor: config.bgColor,
          border: `1px solid ${config.color}`,
          borderRadius: '9999px',
          fontSize: '0.7rem',
          color: config.color,
          cursor: 'default'
        }}
        title={`${config.label}: ${config.description}`}
      >
        <span>{config.emoji}</span>
        <span>{config.label}</span>
      </div>
    );
  }
  
  return (
    <div
      className={`relationship-badge ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
        padding: '0.75rem 1rem',
        backgroundColor: config.bgColor,
        border: `1px solid ${config.color}`,
        borderRadius: '0.75rem',
        transition: 'all 0.2s ease'
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.25rem' }}>{config.emoji}</span>
          <div>
            <div style={{
              fontSize: '0.85rem',
              fontWeight: 600,
              color: config.color
            }}>
              {config.label}
            </div>
            {personalityName && (
              <div style={{
                fontSize: '0.7rem',
                color: 'rgba(255, 255, 255, 0.6)'
              }}>
                with {personalityName}
              </div>
            )}
          </div>
        </div>
        
        {/* Interaction count */}
        <div style={{
          fontSize: '0.7rem',
          color: 'rgba(255, 255, 255, 0.5)',
          textAlign: 'right'
        }}>
          <div>{interactionCount} conversations</div>
        </div>
      </div>
      
      {/* Progress bar */}
      {showProgress && currentLevelIndex < DEPTH_LEVELS.length - 1 && (
        <div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '0.25rem',
            fontSize: '0.65rem',
            color: 'rgba(255, 255, 255, 0.5)'
          }}>
            <span>{config.label}</span>
            <span>{DEPTH_CONFIG[DEPTH_LEVELS[nextLevelIndex]].label}</span>
          </div>
          <div style={{
            height: '4px',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '2px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${progress}%`,
              height: '100%',
              backgroundColor: config.color,
              borderRadius: '2px',
              transition: 'width 0.5s ease'
            }} />
          </div>
          <div style={{
            marginTop: '0.25rem',
            fontSize: '0.6rem',
            color: 'rgba(255, 255, 255, 0.4)',
            textAlign: 'center'
          }}>
            {nextThreshold - interactionCount} more to reach {DEPTH_CONFIG[DEPTH_LEVELS[nextLevelIndex]].label}
          </div>
        </div>
      )}
      
      {/* Max level celebration */}
      {currentLevelIndex === DEPTH_LEVELS.length - 1 && (
        <div style={{
          fontSize: '0.7rem',
          color: config.color,
          textAlign: 'center',
          fontStyle: 'italic'
        }}>
          ✨ You have achieved spiritual kinship ✨
        </div>
      )}
      
      {/* Tooltip on hover */}
      {isHovered && (
        <div style={{
          position: 'absolute',
          bottom: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginBottom: '0.5rem',
          padding: '0.5rem 0.75rem',
          backgroundColor: 'rgba(30, 30, 50, 0.95)',
          borderRadius: '0.5rem',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          zIndex: 100,
          whiteSpace: 'nowrap',
          fontSize: '0.7rem',
          color: 'rgba(255, 255, 255, 0.8)'
        }}>
          {config.description}
          
          {/* Tooltip arrow */}
          <div style={{
            position: 'absolute',
            bottom: '-6px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 0,
            height: 0,
            borderLeft: '6px solid transparent',
            borderRight: '6px solid transparent',
            borderTop: '6px solid rgba(30, 30, 50, 0.95)'
          }} />
        </div>
      )}
    </div>
  );
};

export default RelationshipBadge;
