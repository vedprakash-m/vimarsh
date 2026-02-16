import React from 'react';
import { MessageMetadata } from './types';

interface MessageSourceBadgeProps {
  metadata: MessageMetadata;
  compact?: boolean;
}

/**
 * Badge component showing the source/type of AI response
 * Used for transparency in admin views
 */
export const MessageSourceBadge: React.FC<MessageSourceBadgeProps> = ({ metadata, compact = true }) => {
  const getSourceInfo = () => {
    const isAI = metadata.ai_generated === true;
    const source = metadata.response_source;
    
    if (isAI && source === 'gemini_ai') {
      return {
        icon: '🤖',
        label: 'AI',
        color: 'rgba(59, 130, 246, 0.7)',
        bgColor: 'rgba(59, 130, 246, 0.1)'
      };
    }
    
    if (source === 'template_fallback' || source === 'hardcoded_fallback') {
      return {
        icon: '📜',
        label: 'Traditional',
        color: 'rgba(245, 158, 11, 0.7)',
        bgColor: 'rgba(245, 158, 11, 0.1)'
      };
    }
    
    if (source === 'hybrid_rag' || source === 'simple_rag') {
      return {
        icon: '📚',
        label: 'Enhanced',
        color: 'rgba(147, 51, 234, 0.7)',
        bgColor: 'rgba(147, 51, 234, 0.1)'
      };
    }
    
    return {
      icon: '🎭',
      label: 'Wisdom',
      color: 'rgba(107, 114, 128, 0.7)',
      bgColor: 'rgba(107, 114, 128, 0.1)'
    };
  };
  
  const sourceInfo = getSourceInfo();
  
  if (compact) {
    return (
      <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.25rem',
        padding: '0.25rem 0.5rem',
        backgroundColor: sourceInfo.bgColor,
        border: `1px solid ${sourceInfo.color}`,
        borderRadius: '0.5rem',
        fontSize: '0.7rem',
        color: sourceInfo.color
      }}>
        <span>{sourceInfo.icon}</span>
        <span>{sourceInfo.label}</span>
        {metadata.generation_time_ms && (
          <span style={{ opacity: 0.7 }}>
            {metadata.generation_time_ms}ms
          </span>
        )}
      </div>
    );
  }
  
  return (
    <div style={{
      padding: '0.5rem',
      backgroundColor: sourceInfo.bgColor,
      border: `1px solid ${sourceInfo.color}`,
      borderRadius: '0.5rem',
      fontSize: '0.8rem',
      color: sourceInfo.color
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span>{sourceInfo.icon}</span>
        <span>{sourceInfo.label} Response</span>
        {metadata.generation_time_ms && (
          <span style={{ opacity: 0.7 }}>
            ({metadata.generation_time_ms}ms)
          </span>
        )}
      </div>
      {metadata.fallback_reason && (
        <div style={{ fontSize: '0.7rem', opacity: 0.8, marginTop: '0.25rem' }}>
          Reason: {metadata.fallback_reason}
        </div>
      )}
    </div>
  );
};

export default MessageSourceBadge;
