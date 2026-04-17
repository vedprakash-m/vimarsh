/**
 * Enhanced Personality Selector Component for Vimarsh
 * Beautiful modal interface for selecting spiritual personalities
 * Integrates with user preferences to show favorites at the top
 */

import React, { useState } from 'react';
import { X, Sparkles, Brain, Star } from 'lucide-react';
import { Personality } from '../contexts/PersonalityContext';
import { useSettings } from '../contexts/SettingsContext';

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
  const { settings } = useSettings();

  // Get favorite personalities from settings
  const favoritePersonalityIds = settings?.experience_preferences?.favorite_personalities || [];

  // Get unique domains from available personalities
  const domains = Array.from(new Set((availablePersonalities || []).map(p => p.domain)));

  // Filter personalities based on domain and search
  const filteredPersonalities = (availablePersonalities || []).filter(personality => {
    const matchesDomain = selectedDomain === 'all' || personality.domain === selectedDomain;
    const matchesSearch = personality.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         personality.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesDomain && matchesSearch;
  }).sort((a, b) => {
    // Sort with favorites first, then alphabetically
    const aIsFavorite = favoritePersonalityIds.includes(a.id);
    const bIsFavorite = favoritePersonalityIds.includes(b.id);
    
    // If one is favorite and other isn't, favorite comes first
    if (aIsFavorite && !bIsFavorite) return -1;
    if (!aIsFavorite && bIsFavorite) return 1;
    
    // Otherwise, sort alphabetically by display_name, fallback to name
    const nameA = (a.display_name || a.name || '').toLowerCase();
    const nameB = (b.display_name || b.name || '').toLowerCase();
    return nameA.localeCompare(nameB);
  });

  // Domain styling that matches landing page aesthetics
  const getDomainStyle = (domain: string) => {
    const styles = {
      spiritual: { icon: '🕉️', color: '#7c3aed', label: 'Spiritual' },
      scientific: { icon: '🔬', color: '#2563eb', label: 'Scientific' },
      historical: { icon: '📜', color: '#dc2626', label: 'Historical' },
      philosophical: { icon: '🤔', color: '#ea580c', label: 'Philosophical' },
      literary: { icon: '📚', color: '#059669', label: 'Literary' },
      leadership: { icon: '👑', color: '#dc2626', label: 'Leadership' },
      psychology: { icon: '🧠', color: '#8b5cf6', label: 'Psychology' }
    };
    return styles[domain as keyof typeof styles] || styles.spiritual;
  };

  if (!showAsDialog) return null;

  return (
      <style>{`
        .personality-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 1rem;
        }
        .selector-dialog {
          background: #ffffff;
          border-radius: 1.5rem;
          padding: 2rem;
          maxWidth: 900px;
          width: 100%;
          maxHeight: 80vh;
          overflowY: auto;
          position: relative;
          boxShadow: 0 10px 40px rgba(0, 0, 0, 0.15);
          border: 1px solid #e2e8f0;
          color: #1e293b;
          font-family: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
        }
        @media (max-width: 768px) {
          .personality-grid {
            grid-template-columns: 1fr !important;
          }
          .selector-wrapper {
            padding: 1rem !important;
          }
          .selector-dialog {
            padding: 1.25rem !important;
            max-height: 90vh !important;
            border-radius: 1rem !important;
          }
          .personality-card {
            padding: 1rem !important;
            flex-direction: column !important;
            align-items: flex-start !important;
          }
          .card-icon {
            width: 3rem !important;
            height: 3rem !important;
            font-size: 1.25rem !important;
          }
          .domain-badge {
            top: 1rem !important;
            right: 1rem !important;
            padding: 0.15rem 0.5rem !important;
            font-size: 0.65rem !important;
          }
        }
      `}</style>
      <div className="selector-wrapper" style={{
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
        <div className="selector-dialog" style={{
          background: '#ffffff',
          borderRadius: '1.5rem',
          padding: '2rem',
          maxWidth: '900px',
          width: '100%',
          maxHeight: '80vh',
          overflowY: 'auto',
          position: 'relative',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
          border: '1px solid #e2e8f0',
          color: '#1e293b',
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
                color: '#1e293b'
              }}>
                Select Personality
              </h2>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                style={{
                  background: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '0.5rem',
                  padding: '0.5rem',
                  color: '#64748b',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#f1f5f9';
                  e.currentTarget.style.borderColor = '#cbd5e1';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#f8fafc';
                  e.currentTarget.style.borderColor = '#e2e8f0';
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
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '1rem',
                padding: '1rem 1rem 1rem 3rem',
                color: '#1e293b',
                fontSize: '1rem',
                outline: 'none',
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
                color: '#64748b'
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
                  ? 'linear-gradient(135deg, #FF6B35, #F7931E)' 
                  : '#f8fafc',
                border: selectedDomain === 'all' ? 'none' : '1px solid #e2e8f0',
                borderRadius: '1.5rem',
                padding: '0.5rem 1rem',
                color: selectedDomain === 'all' ? 'white' : '#64748b',
                fontSize: '0.9rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
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
                      ? 'linear-gradient(135deg, #FF6B35, #F7931E)' 
                      : '#f8fafc',
                    border: selectedDomain === domain ? 'none' : '1px solid #e2e8f0',
                    borderRadius: '1.5rem',
                    padding: '0.5rem 1rem',
                    color: selectedDomain === domain ? 'white' : '#64748b',
                    fontSize: '0.9rem',
                    fontWeight: '500',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
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
          <div className="personality-grid">
            {filteredPersonalities.map((personality) => {
              const domainStyle = getDomainStyle(personality.domain);
              const isSelected = selectedPersonalityId === personality.id;
              
              return (
                <div
                  key={personality.id}
                  className="personality-card"
                  onClick={() => onPersonalitySelect(personality)}
                  style={{
                    background: isSelected 
                      ? '#fef3e2' 
                      : favoritePersonalityIds.includes(personality.id)
                        ? '#fffef5'  // Subtle gold tint for favorites
                        : '#ffffff',
                    border: isSelected 
                      ? '2px solid #FF6B35' 
                      : favoritePersonalityIds.includes(personality.id)
                        ? '2px solid #FFD700'  // Gold border for favorites
                        : '1px solid #e2e8f0',
                    borderRadius: '1rem',
                    padding: '1.5rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    position: 'relative',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    boxShadow: favoritePersonalityIds.includes(personality.id)
                      ? '0 2px 8px rgba(255, 215, 0, 0.15)'  // Gold shadow for favorites
                      : '0 1px 3px rgba(0, 0, 0, 0.05)'
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.background = '#f8fafc';
                      e.currentTarget.style.transform = 'translateY(-1px)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.background = '#ffffff';
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
                    }
                  }}
                >
                  {/* Icon */}
                  <div className="card-icon" style={{
                    width: '4rem',
                    height: '4rem',
                    background: `linear-gradient(135deg, ${domainStyle.color}, ${domainStyle.color}CC)`,
                    borderRadius: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.5rem',
                    flexShrink: 0,
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
                  }}>
                    {domainStyle.icon}
                  </div>

                  {/* Content */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h3 style={{
                      margin: '0 0 0.5rem 0',
                      fontSize: '1.25rem',
                      fontWeight: '700',
                      color: '#1e293b'
                    }}>
                      {personality.display_name || personality.name || 'Unknown'}
                    </h3>
                    
                    <p style={{
                      margin: '0 0 1rem 0',
                      fontSize: '0.9rem',
                      color: '#64748b',
                      lineHeight: '1.4',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}>
                      {personality.description}
                    </p>
                  </div>

                  {/* Favorite Star */}
                  {favoritePersonalityIds.includes(personality.id) && (
                    <div style={{
                      position: 'absolute',
                      top: '0.75rem',
                      left: '0.75rem',
                      width: '1.75rem',
                      height: '1.75rem',
                      background: 'linear-gradient(135deg, #FFD700, #FFA500)',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 2px 6px rgba(255, 215, 0, 0.4)',
                      zIndex: 10
                    }}>
                      <Star size={14} fill="#FFFFFF" color="#FFFFFF" strokeWidth={2} />
                    </div>
                  )}

                  {/* Domain Badge */}
                  <div className="domain-badge" style={{
                    position: 'absolute',
                    top: '1rem',
                    right: '1rem',
                    background: `${domainStyle.color}15`,
                    border: `1px solid ${domainStyle.color}40`,
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
                      background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: '0.8rem',
                      fontWeight: '700',
                      boxShadow: '0 2px 8px rgba(255, 107, 53, 0.3)'
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
            color: '#64748b'
          }}>
            <Brain size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
            <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.2rem', color: '#475569' }}>No personalities found</h3>
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