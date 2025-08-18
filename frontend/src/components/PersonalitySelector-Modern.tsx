/**
 * Enhanced Personality Selector Component for Vimarsh
 * Modern modal interface for selecting personalities
 */

import React, { useState } from 'react';
import { X, Search } from 'lucide-react';
import { Personality } from '../contexts/PersonalityContext';

interface PersonalitySelectorProps {
  availablePersonalities: Personality[];
  selectedPersonalityId?: string;
  onPersonalitySelect: (personality: Personality) => void;
  onClose?: () => void;
  showAsDialog?: boolean;
}

// Vimarsh Design System colors for domains (matching landing page)
const domainColors = {
  'Spiritual': '#007aff',
  'Scientific': '#34c759', 
  'Philosophical': '#5856d6',
  'Historical': '#ff9500',
  'Literary': '#af52de',
  'Leadership': '#ff3b30',
  'Psychology': '#8b5cf6'
};

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
  }).sort((a, b) => {
    // Sort alphabetically by display_name, fallback to name
    const nameA = (a.display_name || a.name || '').toLowerCase();
    const nameB = (b.display_name || b.name || '').toLowerCase();
    return nameA.localeCompare(nameB);
  });

  if (!showAsDialog) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.4)',
      backdropFilter: 'blur(20px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '2rem'
    }}>
      <div style={{
        background: '#ffffff',
        borderRadius: '20px',
        padding: '0',
        maxWidth: '900px',
        width: '100%',
        maxHeight: '80vh',
        overflowY: 'auto',
        position: 'relative',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
        border: '1px solid #e5e7eb',
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
      }}>
        {/* Header */}
        <div style={{
          padding: '1.5rem 2rem',
          borderBottom: '1px solid #f3f4f6',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: '#ffffff',
          borderRadius: '20px 20px 0 0'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #f97316, #f59e0b)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1rem'
            }}>🎭</div>
            <h2 style={{
              margin: 0,
              fontSize: '1.5rem',
              fontWeight: 600,
              color: '#1d1d1f'
            }}>Choose Your Guide</h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: '#f3f4f6',
              border: 'none',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              color: '#6e6e73',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#e5e7eb';
              e.currentTarget.style.color = '#1d1d1f';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#f3f4f6';
              e.currentTarget.style.color = '#6e6e73';
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Search and Filters */}
        <div style={{ padding: '1.5rem 2rem' }}>
          {/* Search Bar */}
          <div style={{
            position: 'relative',
            marginBottom: '1.5rem'
          }}>
            <Search size={18} style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#9ca3af'
            }} />
            <input
              type="text"
              placeholder="Search personalities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 12px 12px 40px',
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                fontSize: '1rem',
                fontFamily: 'inherit',
                background: '#f9fafb',
                outline: 'none',
                transition: 'all 0.2s ease'
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = '#007aff';
                e.currentTarget.style.background = '#ffffff';
                e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0, 122, 255, 0.1)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = '#e5e7eb';
                e.currentTarget.style.background = '#f9fafb';
                e.currentTarget.style.boxShadow = 'none';
              }}
            />
          </div>

          {/* Domain Filters */}
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.5rem',
            marginBottom: '1.5rem'
          }}>
            <button
              onClick={() => setSelectedDomain('all')}
              style={{
                background: selectedDomain === 'all' ? '#007aff' : '#f3f4f6',
                color: selectedDomain === 'all' ? 'white' : '#374151',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '20px',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              All
            </button>
            {domains.map((domain) => (
              <button
                key={domain}
                onClick={() => setSelectedDomain(domain)}
                style={{
                  background: selectedDomain === domain 
                    ? domainColors[domain as keyof typeof domainColors] 
                    : '#f3f4f6',
                  color: selectedDomain === domain ? 'white' : '#374151',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '20px',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {domain}
              </button>
            ))}
          </div>
        </div>

        {/* Personalities Grid */}
        <div style={{
          padding: '0 2rem 2rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1rem',
          maxHeight: '400px',
          overflowY: 'auto'
        }}>
          {filteredPersonalities.map((personality) => {
            const domainColor = domainColors[personality.domain as keyof typeof domainColors] || '#6b7280';
            const isSelected = personality.id === selectedPersonalityId;
            
            return (
              <div
                key={personality.id}
                onClick={() => onPersonalitySelect(personality)}
                style={{
                  background: isSelected ? '#f0f9ff' : '#ffffff',
                  border: isSelected ? `2px solid ${domainColor}` : '1px solid #e5e7eb',
                  borderRadius: '12px',
                  padding: '1.25rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  position: 'relative'
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.transform = 'translateY(-1px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
                    e.currentTarget.style.borderColor = domainColor;
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                    e.currentTarget.style.borderColor = '#e5e7eb';
                  }
                }}
              >
                {/* Personality Header */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  marginBottom: '0.75rem'
                }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: '#f8fafc',
                    border: `2px solid ${domainColor}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: domainColor,
                    fontWeight: '600',
                    fontSize: '1rem'
                  }}>
                    {personality.name.charAt(0)}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.5rem',
                      marginBottom: '0.25rem'
                    }}>
                      <h3 style={{ 
                        margin: 0, 
                        fontSize: '1rem', 
                        fontWeight: '600', 
                        color: '#1f2937' 
                      }}>
                        {personality.display_name || personality.name}
                      </h3>
                      <div style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        backgroundColor: domainColor
                      }} />
                    </div>
                    <p style={{ 
                      margin: 0, 
                      fontSize: '0.75rem', 
                      color: '#6b7280',
                      fontWeight: 500
                    }}>
                      {personality.domain}
                    </p>
                  </div>
                </div>

                {/* Description */}
                <p style={{ 
                  margin: '0 0 0.75rem 0', 
                  fontSize: '0.875rem', 
                  lineHeight: '1.4',
                  color: '#4b5563',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}>
                  {personality.description}
                </p>

                {/* Selected Indicator */}
                {isSelected && (
                  <div style={{
                    position: 'absolute',
                    top: '0.75rem',
                    right: '0.75rem',
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    background: domainColor,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '0.75rem'
                  }}>
                    ✓
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Empty State */}
        {filteredPersonalities.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '3rem 2rem',
            color: '#6b7280'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🔍</div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.5rem', color: '#374151' }}>
              No personalities found
            </h3>
            <p style={{ fontSize: '0.875rem' }}>
              Try adjusting your search or filter criteria
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonalitySelector;
