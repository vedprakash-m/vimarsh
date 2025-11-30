/**
 * Memory Dashboard Component
 * 
 * Displays the user's memory profile, relationships with personalities,
 * and session insights in a visually engaging way.
 * 
 * Features:
 * - Relationship depth visualization
 * - Session history with insights
 * - Memory statistics
 * - Journey progress tracking
 */

import React, { useState, useEffect } from 'react';
import { 
  useMemory, 
  RelationshipState, 
  SessionSummary,
  RelationshipDepth 
} from '../contexts/MemoryContext';
import './MemoryDashboard.css';

// Personality metadata for display
const PERSONALITY_INFO: Record<string, { name: string; domain: string; icon: string; color: string }> = {
  krishna: { name: 'Krishna', domain: 'Spiritual', icon: '🙏', color: '#FF9933' },
  buddha: { name: 'Buddha', domain: 'Spiritual', icon: '☸️', color: '#FFD700' },
  jesus_christ: { name: 'Jesus Christ', domain: 'Spiritual', icon: '✝️', color: '#87CEEB' },
  rumi: { name: 'Rumi', domain: 'Spiritual', icon: '🌹', color: '#DC143C' },
  swami_vivekananda: { name: 'Swami Vivekananda', domain: 'Spiritual', icon: '🕉️', color: '#FF6B35' },
  marcus_aurelius: { name: 'Marcus Aurelius', domain: 'Philosophical', icon: '🏛️', color: '#8B4513' },
  lao_tzu: { name: 'Lao Tzu', domain: 'Philosophical', icon: '☯️', color: '#228B22' },
  confucius: { name: 'Confucius', domain: 'Philosophical', icon: '📚', color: '#800000' },
  aristotle: { name: 'Aristotle', domain: 'Philosophical', icon: '🎓', color: '#4169E1' },
  plato: { name: 'Plato', domain: 'Philosophical', icon: '💭', color: '#6A5ACD' },
  socrates: { name: 'Socrates', domain: 'Philosophical', icon: '❓', color: '#708090' },
  chanakya: { name: 'Chanakya', domain: 'Leadership', icon: '👑', color: '#8B0000' },
  abraham_lincoln: { name: 'Abraham Lincoln', domain: 'Leadership', icon: '🎩', color: '#2F4F4F' },
  benjamin_franklin: { name: 'Benjamin Franklin', domain: 'Leadership', icon: '⚡', color: '#B8860B' },
  george_washington: { name: 'George Washington', domain: 'Leadership', icon: '🦅', color: '#1E3A5F' },
  mahatma_gandhi: { name: 'Mahatma Gandhi', domain: 'Leadership', icon: '🕊️', color: '#FFFAF0' },
  martin_luther_king_jr: { name: 'Martin Luther King Jr.', domain: 'Leadership', icon: '✊', color: '#2C3E50' },
  albert_einstein: { name: 'Albert Einstein', domain: 'Scientific', icon: '🔬', color: '#9370DB' },
  isaac_newton: { name: 'Isaac Newton', domain: 'Scientific', icon: '🍎', color: '#32CD32' },
  nikola_tesla: { name: 'Nikola Tesla', domain: 'Scientific', icon: '⚡', color: '#00CED1' },
  archimedes: { name: 'Archimedes', domain: 'Scientific', icon: '📐', color: '#DAA520' },
  leonardo_da_vinci: { name: 'Leonardo da Vinci', domain: 'Scientific', icon: '🎨', color: '#DEB887' },
  rabindranath_tagore: { name: 'Rabindranath Tagore', domain: 'Literary', icon: '✍️', color: '#CD853F' },
  william_shakespeare: { name: 'William Shakespeare', domain: 'Literary', icon: '🎭', color: '#9932CC' },
  sigmund_freud: { name: 'Sigmund Freud', domain: 'Psychology', icon: '🧠', color: '#483D8B' }
};

// Depth progression info
const DEPTH_INFO: Record<RelationshipDepth, { label: string; description: string; threshold: number }> = {
  stranger: { label: 'New Seeker', description: 'Just beginning the journey', threshold: 0 },
  acquaintance: { label: 'Beginning Journey', description: 'Starting to understand', threshold: 3 },
  familiar: { label: 'Growing Understanding', description: 'Developing deeper insights', threshold: 10 },
  trusted: { label: 'Deep Connection', description: 'Profound wisdom exchange', threshold: 25 },
  kindred: { label: 'Spiritual Kinship', description: 'True meeting of minds', threshold: 50 }
};

interface MemoryDashboardProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MemoryDashboard: React.FC<MemoryDashboardProps> = ({ isOpen, onClose }) => {
  const memory = useMemory();
  const [activeTab, setActiveTab] = useState<'relationships' | 'sessions' | 'insights'>('relationships');
  const [selectedPersonality, setSelectedPersonality] = useState<string | null>(null);
  
  // Get sorted relationships by interaction count
  const sortedRelationships = React.useMemo(() => {
    return Array.from(memory.relationships.entries())
      .sort((a, b) => b[1].interactionCount - a[1].interactionCount);
  }, [memory.relationships]);
  
  if (!isOpen) return null;
  
  const renderRelationshipCard = (personalityId: string, relationship: RelationshipState) => {
    const info = PERSONALITY_INFO[personalityId] || { 
      name: personalityId, 
      domain: 'Unknown', 
      icon: '🌟', 
      color: '#666' 
    };
    const depthInfo = DEPTH_INFO[relationship.depth];
    const progress = memory.getRelationshipProgress(personalityId);
    
    return (
      <div 
        key={personalityId}
        className="memory-relationship-card"
        onClick={() => setSelectedPersonality(personalityId)}
        style={{ '--accent-color': info.color } as React.CSSProperties}
      >
        <div className="relationship-header">
          <span className="relationship-icon">{info.icon}</span>
          <div className="relationship-info">
            <h4 className="relationship-name">{info.name}</h4>
            <span className="relationship-domain">{info.domain}</span>
          </div>
        </div>
        
        <div className="relationship-depth">
          <span className="depth-label">{depthInfo.label}</span>
          <div className="depth-progress-bar">
            <div 
              className="depth-progress-fill" 
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="depth-count">{relationship.interactionCount} conversations</span>
        </div>
        
        {relationship.topicsExplored.length > 0 && (
          <div className="relationship-topics">
            {relationship.topicsExplored.slice(0, 3).map((topic, i) => (
              <span key={i} className="topic-tag">{topic}</span>
            ))}
            {relationship.topicsExplored.length > 3 && (
              <span className="topic-more">+{relationship.topicsExplored.length - 3}</span>
            )}
          </div>
        )}
        
        <div className="relationship-meta">
          <span className="last-interaction">
            Last: {new Date(relationship.lastInteraction).toLocaleDateString()}
          </span>
        </div>
      </div>
    );
  };
  
  const renderSessionCard = (session: SessionSummary) => {
    const info = PERSONALITY_INFO[session.personalityId] || {
      name: session.personalityId,
      icon: '🌟',
      color: '#666'
    };
    
    return (
      <div key={session.id} className="memory-session-card">
        <div className="session-header">
          <span className="session-icon">{info.icon}</span>
          <div className="session-info">
            <span className="session-personality">{info.name}</span>
            <span className="session-date">
              {new Date(session.sessionStart).toLocaleDateString()}
            </span>
          </div>
          <span className="session-messages">{session.messageCount} messages</span>
        </div>
        
        <p className="session-summary">{session.summary}</p>
        
        {session.keyInsights.length > 0 && (
          <div className="session-insights">
            <h5>Key Insights</h5>
            <ul>
              {session.keyInsights.slice(0, 2).map((insight, i) => (
                <li key={i}>{insight}</li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="session-emotional-arc">
          <span className="arc-label">Emotional Journey:</span>
          <span className="arc-value">
            {session.emotionalArc.start} → {session.emotionalArc.end}
          </span>
        </div>
      </div>
    );
  };
  
  const renderInsightsTab = () => {
    const { memoryStats, memoryProfile } = memory;
    
    return (
      <div className="memory-insights-tab">
        <div className="insights-overview">
          <div className="insight-stat">
            <span className="stat-value">{memoryStats.totalConversations}</span>
            <span className="stat-label">Conversations</span>
          </div>
          <div className="insight-stat">
            <span className="stat-value">{memoryStats.totalPersonalities}</span>
            <span className="stat-label">Guides Consulted</span>
          </div>
          <div className="insight-stat">
            <span className="stat-value">{memoryStats.averageSessionLength}m</span>
            <span className="stat-label">Avg. Session</span>
          </div>
        </div>
        
        {memoryProfile && (
          <div className="insights-profile">
            <h4>Your Journey</h4>
            <div className="profile-section">
              <h5>Life Concerns</h5>
              <div className="concern-tags">
                {memoryProfile.lifeConcerns.length > 0 ? (
                  memoryProfile.lifeConcerns.map((concern, i) => (
                    <span key={i} className="concern-tag">{concern}</span>
                  ))
                ) : (
                  <span className="no-data">No concerns tracked yet</span>
                )}
              </div>
            </div>
            
            <div className="profile-section">
              <h5>Philosophical Interests</h5>
              <div className="interest-tags">
                {memoryProfile.philosophicalInterests.length > 0 ? (
                  memoryProfile.philosophicalInterests.map((interest, i) => (
                    <span key={i} className="interest-tag">{interest}</span>
                  ))
                ) : (
                  <span className="no-data">Explore more to discover</span>
                )}
              </div>
            </div>
          </div>
        )}
        
        {memoryStats.topTopics.length > 0 && (
          <div className="insights-topics">
            <h4>Most Explored Topics</h4>
            <div className="topic-cloud">
              {memoryStats.topTopics.map((topic, i) => (
                <span 
                  key={i} 
                  className="topic-cloud-item"
                  style={{ fontSize: `${1.2 - i * 0.1}rem` }}
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className="memory-dashboard-overlay" onClick={onClose}>
      <div className="memory-dashboard" onClick={e => e.stopPropagation()}>
        <div className="dashboard-header">
          <h2>🧠 Your Memory Journey</h2>
          <button className="dashboard-close" onClick={onClose}>×</button>
        </div>
        
        <div className="dashboard-tabs">
          <button 
            className={`tab-button ${activeTab === 'relationships' ? 'active' : ''}`}
            onClick={() => setActiveTab('relationships')}
          >
            Relationships
          </button>
          <button 
            className={`tab-button ${activeTab === 'sessions' ? 'active' : ''}`}
            onClick={() => setActiveTab('sessions')}
          >
            Sessions
          </button>
          <button 
            className={`tab-button ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            Insights
          </button>
        </div>
        
        <div className="dashboard-content">
          {activeTab === 'relationships' && (
            <div className="relationships-grid">
              {sortedRelationships.length > 0 ? (
                sortedRelationships.map(([id, rel]) => renderRelationshipCard(id, rel))
              ) : (
                <div className="empty-state">
                  <span className="empty-icon">🌱</span>
                  <h3>Begin Your Journey</h3>
                  <p>Start conversations with our wise guides to build relationships.</p>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'sessions' && (
            <div className="sessions-list">
              {memory.recentSessions.length > 0 ? (
                memory.recentSessions.map(session => renderSessionCard(session))
              ) : (
                <div className="empty-state">
                  <span className="empty-icon">📜</span>
                  <h3>No Sessions Yet</h3>
                  <p>Your conversation history will appear here.</p>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'insights' && renderInsightsTab()}
        </div>
        
        {memory.isLoading && (
          <div className="dashboard-loading">
            <div className="loading-spinner" />
            <span>Loading your memories...</span>
          </div>
        )}
        
        {memory.memoryError && (
          <div className="dashboard-error">
            <span>⚠️ {memory.memoryError}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MemoryDashboard;
