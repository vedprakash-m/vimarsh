/**
 * Enhanced Personality Selector Component for Vimarsh
 * Beautiful modal interface for selecting spiritual personalities
 */

import React, { useState } from 'react';
import { X, Sparkles, Brain, Clock, BookOpen } from 'lucide-react';
import { Personality } from '../contexts/PersonalityContext';

interface PersonalitySelectorProps {
  availablePersonalities: Personality[];
  selectedPersonalityId?: string;
  onPersonalitySelect: (personality: Personality) => void;
  onClose?: () => void;
  showAsDialog?: boolean;
}

const PersonalitySelector: React.FC<PersonalitySelectorProps> = ({
  availablePersonalities,
  selectedPersonalityId,
  onPersonalitySelect,
  onClose,
  showAsDialog = true
}) => {
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Get unique domains from available personalities
  const domains = Array.from(new Set((availablePersonalities || []).map(p => p.domain)));

  // Filter personalities based on domain and search
  const filteredPersonalities = (availablePersonalities || []).filter(personality => {
    const matchesDomain = selectedDomain === 'all' || personality.domain === selectedDomain;
    const matchesSearch = personality.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         personality.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesDomain && matchesSearch;
  });

  // Domain styling that matches landing page aesthetics
  const getDomainStyle = (domain: string) => {
    const styles = {
      spiritual: { icon: '🕉️', color: '#7c3aed', label: 'Spiritual Guidance' },
      scientific: { icon: '🔬', color: '#2563eb', label: 'Scientific' },
      historical: { icon: '📜', color: '#dc2626', label: 'Historical' },
      philosophical: { icon: '🤔', color: '#ea580c', label: 'Philosophical' },
      literary: { icon: '📚', color: '#059669', label: 'Literary' }
    };
    return styles[domain as keyof typeof styles] || styles.spiritual;
  };

  if (!showAsDialog) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '2rem'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '1.5rem',
        padding: '2rem',
        maxWidth: '900px',
        width: '100%',
        maxHeight: '80vh',
        overflowY: 'auto',
        position: 'relative',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        color: 'white',
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.5rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '1.5rem' }}>🎭</span>
            <h2 style={{
              margin: 0,
              fontSize: '1.5rem',
              fontWeight: '700',
              color: 'white',
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
            }}>
              Select Personality
            </h2>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              style={{
                background: 'rgba(255, 255, 255, 0.2)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '0.5rem',
                padding: '0.5rem',
                color: 'white',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
              }}
            >
              <X size={20} />
            </button>
          )}
        </div>

        {/* Search */}
        <div style={{
          position: 'relative',
          marginBottom: '1.5rem'
        }}>
          <input
            type="text"
            placeholder="Search personalities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              background: 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '1rem',
              padding: '1rem 1rem 1rem 3rem',
              color: 'white',
              fontSize: '1rem',
              outline: 'none',
              backdropFilter: 'blur(10px)',
              boxSizing: 'border-box'
            }}
          />
          <Sparkles
            size={18}
            style={{
              position: 'absolute',
              left: '1rem',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'rgba(255, 255, 255, 0.6)'
            }}
          />
        </div>

        {/* Domain Filters */}
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          marginBottom: '2rem',
          flexWrap: 'wrap'
        }}>
          <button
            onClick={() => setSelectedDomain('all')}
            style={{
              background: selectedDomain === 'all' 
                ? 'linear-gradient(135deg, #fbbf24, #f59e0b)' 
                : 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '1.5rem',
              padding: '0.5rem 1rem',
              color: 'white',
              fontSize: '0.9rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              backdropFilter: 'blur(10px)'
            }}
          >
            All
          </button>
          {domains.map(domain => {
            const domainStyle = getDomainStyle(domain);
            return (
              <button
                key={domain}
                onClick={() => setSelectedDomain(domain)}
                style={{
                  background: selectedDomain === domain 
                    ? 'linear-gradient(135deg, #fbbf24, #f59e0b)' 
                    : 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '1.5rem',
                  padding: '0.5rem 1rem',
                  color: 'white',
                  fontSize: '0.9rem',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  backdropFilter: 'blur(10px)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                <span>{domainStyle.icon}</span>
                {domainStyle.label}
              </button>
            );
          })}
        </div>

        {/* Personality Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '1rem'
        }}>
          {filteredPersonalities.map((personality) => {
            const domainStyle = getDomainStyle(personality.domain);
            const isSelected = selectedPersonalityId === personality.id;
            
            return (
              <div
                key={personality.id}
                onClick={() => onPersonalitySelect(personality)}
                style={{
                  background: isSelected 
                    ? 'linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))' 
                    : 'rgba(255, 255, 255, 0.1)',
                  border: isSelected 
                    ? '2px solid #fbbf24' 
                    : '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '1rem',
                  padding: '1.5rem',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  backdropFilter: 'blur(10px)',
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem'
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.2)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }
                }}
              >
                {/* Icon */}
                <div style={{
                  width: '4rem',
                  height: '4rem',
                  background: `linear-gradient(135deg, ${domainStyle.color}, ${domainStyle.color}CC)`,
                  borderRadius: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.5rem',
                  flexShrink: 0,
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
                }}>
                  {domainStyle.icon}
                </div>

                {/* Content */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h3 style={{
                    margin: '0 0 0.5rem 0',
                    fontSize: '1.25rem',
                    fontWeight: '700',
                    color: 'white',
                    textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)'
                  }}>
                    {personality.display_name || personality.name || 'Unknown'}
                  </h3>
                  
                  <p style={{
                    margin: '0 0 1rem 0',
                    fontSize: '0.9rem',
                    color: 'rgba(255, 255, 255, 0.8)',
                    lineHeight: '1.4',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}>
                    {personality.description}
                  </p>
                  
                  <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '1rem',
                    fontSize: '0.8rem',
                    color: 'rgba(255, 255, 255, 0.7)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Clock size={12} />
                      <span>{personality.time_period}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <BookOpen size={12} />
                      <span>{personality.expertise_areas?.slice(0, 2).join(', ') || 'General guidance'}</span>
                    </div>
                  </div>
                </div>

                {/* Domain Badge */}
                <div style={{
                  position: 'absolute',
                  top: '1rem',
                  right: '1rem',
                  background: `${domainStyle.color}22`,
                  border: `1px solid ${domainStyle.color}`,
                  borderRadius: '1rem',
                  padding: '0.25rem 0.75rem',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  color: domainStyle.color,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  {domainStyle.label}
                </div>

                {/* Selection Indicator */}
                {isSelected && (
                  <div style={{
                    position: 'absolute',
                    top: '-0.5rem',
                    right: '-0.5rem',
                    width: '2rem',
                    height: '2rem',
                    background: 'linear-gradient(135deg, #fbbf24, #f59e0b)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '0.8rem',
                    fontWeight: '700',
                    boxShadow: '0 4px 12px rgba(251, 191, 36, 0.4)'
                  }}>
                    ✓
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* No Results */}
        {filteredPersonalities.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '3rem 2rem',
            color: 'rgba(255, 255, 255, 0.7)'
          }}>
            <Brain size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
            <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.2rem' }}>No personalities found</h3>
            <p style={{ margin: 0, fontSize: '0.9rem' }}>
              Try adjusting your search or domain filter
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonalitySelector;