/**
 * Memory Indicator Component
 * 
 * Visual indicator showing memory context usage percentage
 * and whether memory-enhanced responses are active.
 * 
 * Features:
 * - Circular progress indicator
 * - Token usage visualization
 * - Memory quality score
 * - Tooltip with details
 */

import React, { useState } from 'react';
import { useMemory } from '../contexts/MemoryContext';

interface MemoryIndicatorProps {
  compact?: boolean;
  showTooltip?: boolean;
  className?: string;
}

export const MemoryIndicator: React.FC<MemoryIndicatorProps> = ({
  compact = false,
  showTooltip = true,
  className = ''
}) => {
  const memory = useMemory();
  const [isHovered, setIsHovered] = useState(false);
  
  // Calculate memory usage percentage
  const maxTokens = 16000; // Working memory budget
  const currentTokens = memory.currentSession?.tokenCount || 0;
  const usagePercent = Math.min(100, (currentTokens / maxTokens) * 100);
  
  // Determine color based on usage
  const getColor = () => {
    if (usagePercent < 50) return '#22c55e'; // Green
    if (usagePercent < 80) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };
  
  // SVG circle calculations
  const radius = compact ? 10 : 18;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (usagePercent / 100) * circumference;
  
  if (!memory.isMemoryEnabled) {
    return null;
  }
  
  const indicator = (
    <div
      className={`memory-indicator ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        gap: compact ? '0.25rem' : '0.5rem',
        padding: compact ? '0.25rem 0.5rem' : '0.5rem 0.75rem',
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '9999px',
        cursor: 'pointer',
        transition: 'all 0.2s ease'
      }}
    >
      {/* Circular Progress */}
      <svg
        width={compact ? 24 : 40}
        height={compact ? 24 : 40}
        style={{ transform: 'rotate(-90deg)' }}
      >
        {/* Background circle */}
        <circle
          cx={compact ? 12 : 20}
          cy={compact ? 12 : 20}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={compact ? 2 : 3}
        />
        {/* Progress circle */}
        <circle
          cx={compact ? 12 : 20}
          cy={compact ? 12 : 20}
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth={compact ? 2 : 3}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: 'stroke-dashoffset 0.3s ease' }}
        />
      </svg>
      
      {/* Memory icon and label */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
        <span style={{ fontSize: compact ? '0.75rem' : '1rem' }}>🧠</span>
        {!compact && (
          <span style={{
            fontSize: '0.75rem',
            color: 'rgba(255, 255, 255, 0.8)',
            fontWeight: 500
          }}>
            {Math.round(usagePercent)}%
          </span>
        )}
      </div>
      
      {/* Tooltip */}
      {showTooltip && isHovered && (
        <div style={{
          position: 'absolute',
          bottom: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginBottom: '0.5rem',
          padding: '0.75rem 1rem',
          backgroundColor: 'rgba(30, 30, 50, 0.95)',
          borderRadius: '0.5rem',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          zIndex: 100,
          minWidth: '180px',
          whiteSpace: 'nowrap'
        }}>
          <div style={{ 
            fontSize: '0.8rem', 
            fontWeight: 600, 
            color: 'white',
            marginBottom: '0.5rem'
          }}>
            Memory Context
          </div>
          
          <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.7)' }}>
            <div style={{ marginBottom: '0.25rem' }}>
              📊 Tokens: {currentTokens.toLocaleString()} / {maxTokens.toLocaleString()}
            </div>
            <div style={{ marginBottom: '0.25rem' }}>
              💬 Messages: {memory.currentSession?.recentMessages.length || 0}
            </div>
            <div style={{ marginBottom: '0.25rem' }}>
              🎯 Topics: {memory.currentSession?.currentTopics.length || 0}
            </div>
            <div>
              💫 Emotion: {memory.currentSession?.emotionalState || 'neutral'}
            </div>
          </div>
          
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
  
  return indicator;
};

export default MemoryIndicator;
