import React, { useState, useEffect } from 'react';
import { Bot, Edit3, Eye, Plus, Search, Filter, Trash2, CheckCircle, XCircle, AlertTriangle, Users, Activity, TrendingUp } from 'lucide-react';
import { adminService } from '../../services/adminService';

interface Personality {
  id: string;
  name: string;
  domain: 'spiritual' | 'scientific' | 'historical' | 'philosophical' | 'literary' | 'leadership' | 'psychology';
  description: string;
  isActive: boolean;
  contentSources?: number;
  responseQuality?: number;
  usageCount?: number;
  lastUpdated?: string;
}

interface PersonalityStats {
  totalPersonalities: number;
  activePersonalities: number;
  domainBreakdown: Record<string, number>;
  topPerformers: Personality[];
  recentlyAdded: Personality[];
}

const PersonalityManagement: React.FC = () => {
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [stats, setStats] = useState<PersonalityStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [domainFilter, setDomainFilter] = useState<string>('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedPersonality, setSelectedPersonality] = useState<Personality | null>(null);

  useEffect(() => {
    loadPersonalities();
    loadPersonalityStats();
  }, []);

  const loadPersonalities = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await adminService.getContentOverview();
      
      if (data.personalities) {
        // Transform backend data to frontend format
        const transformedPersonalities: Personality[] = data.personalities.map((p: any) => ({
          id: p.id,
          name: p.name,
          domain: p.domain,
          description: p.description || `${p.name} - AI personality specialized in ${p.domain} domain`,
          isActive: p.status === 'processed' || p.status === 'active',
          contentSources: p.source_count || 0,
          responseQuality: p.rag_status === 'ready' ? 95 : p.processing_progress || 0,
          usageCount: Math.floor(Math.random() * 1000) + 100, // TODO: Get real usage data
          lastUpdated: p.last_update || new Date().toISOString().split('T')[0]
        }));
        
        setPersonalities(transformedPersonalities);
      } else {
        throw new Error('Unexpected API response format');
      }
    } catch (err) {
      console.error('❌ Failed to load personalities:', err);
      setError(err instanceof Error ? err.message : 'Failed to load personalities');
    } finally {
      setLoading(false);
    }
  };

  const loadPersonalityStats = async () => {
    try {
      // For now, calculate stats from loaded personalities
      // In the future, this could be a separate API endpoint
      const domains = personalities.reduce((acc, p) => {
        acc[p.domain] = (acc[p.domain] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      const newStats: PersonalityStats = {
        totalPersonalities: personalities.length,
        activePersonalities: personalities.filter(p => p.isActive).length,
        domainBreakdown: domains,
        topPerformers: personalities
          .sort((a, b) => (b.responseQuality || 0) - (a.responseQuality || 0))
          .slice(0, 3),
        recentlyAdded: personalities
          .sort((a, b) => new Date(b.lastUpdated || '').getTime() - new Date(a.lastUpdated || '').getTime())
          .slice(0, 3)
      };

      setStats(newStats);
    } catch (err) {
      console.error('❌ Failed to calculate personality stats:', err);
    }
  };

  // Update stats when personalities change
  useEffect(() => {
    if (personalities.length > 0) {
      loadPersonalityStats();
    }
  }, [personalities]);

  const filteredPersonalities = personalities.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         p.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDomain = domainFilter === 'all' || p.domain === domainFilter;
    return matchesSearch && matchesDomain;
  });

  const getDomainColor = (domain: string) => {
    const colors = {
      spiritual: '#8B5CF6',
      scientific: '#059669', 
      historical: '#DC2626',
      philosophical: '#2563EB',
      literary: '#7C2D12',
      leadership: '#DC2626',
      psychology: '#8b5cf6'
    };
    return colors[domain as keyof typeof colors] || '#6B7280';
  };

  const getDomainIcon = (domain: string) => {
    switch (domain) {
      case 'spiritual': return '🕯️';
      case 'scientific': return '🔬';
      case 'historical': return '📜';
      case 'philosophical': return '🤔';
      case 'literary': return '📚';
      case 'leadership': return '👑';
      case 'psychology': return '🧠';
      default: return '🤖';
    }
  };

  const formatDomainName = (domain: string) => {
    return domain.charAt(0).toUpperCase() + domain.slice(1);
  };

  if (loading && personalities.length === 0) {
    return (
      <div className="vimarsh-admin-loading" style={{ minHeight: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="loading-spinner"></div>
        <p style={{ marginLeft: '1rem' }}>Loading personality management...</p>
      </div>
    );
  }

  return (
    <div className="vimarsh-admin-dashboard">
      {/* Header */}
      <div className="vimarsh-admin-header">
        <div>
          <h1>🤖 Personality Management</h1>
          <p style={{ color: '#6b7280', marginTop: '0.5rem' }}>
            Manage all {personalities.length} AI personalities across 5 domains
          </p>
        </div>
        <button 
          className="vimarsh-btn-primary"
          onClick={() => setShowAddModal(true)}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Plus size={16} />
          Add Personality
        </button>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="vimarsh-admin-stats">
          <div className="stat-card">
            <Bot size={20} style={{ color: '#3B82F6' }} />
            <div>
              <span className="stat-value">{stats.totalPersonalities}</span>
              <span className="stat-label">Total Personalities</span>
            </div>
          </div>
          <div className="stat-card">
            <CheckCircle size={20} style={{ color: '#10B981' }} />
            <div>
              <span className="stat-value">{stats.activePersonalities}</span>
              <span className="stat-label">Active</span>
            </div>
          </div>
          <div className="stat-card">
            <TrendingUp size={20} style={{ color: '#F59E0B' }} />
            <div>
              <span className="stat-value">{Object.keys(stats.domainBreakdown).length}</span>
              <span className="stat-label">Domains</span>
            </div>
          </div>
          <div className="stat-card">
            <Activity size={20} style={{ color: '#8B5CF6' }} />
            <div>
              <span className="stat-value">{personalities.reduce((sum, p) => sum + (p.usageCount || 0), 0)}</span>
              <span className="stat-label">Total Usage</span>
            </div>
          </div>
        </div>
      )}

      {/* Domain Breakdown */}
      {stats && Object.keys(stats.domainBreakdown).length > 0 && (
        <div className="vimarsh-admin-card" style={{ marginBottom: '1.5rem' }}>
          <div className="card-header">
            <h3>📊 Domain Distribution</h3>
          </div>
          <div style={{ padding: '1rem' }}>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              {Object.entries(stats.domainBreakdown).map(([domain, count]) => (
                <div 
                  key={domain}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.5rem 1rem',
                    backgroundColor: `${getDomainColor(domain)}20`,
                    borderRadius: '0.5rem',
                    border: `1px solid ${getDomainColor(domain)}40`
                  }}
                >
                  <span style={{ fontSize: '1.2rem' }}>{getDomainIcon(domain)}</span>
                  <span style={{ fontWeight: '600', color: getDomainColor(domain) }}>
                    {formatDomainName(domain)}
                  </span>
                  <span style={{ 
                    backgroundColor: getDomainColor(domain),
                    color: 'white',
                    padding: '0.125rem 0.5rem',
                    borderRadius: '1rem',
                    fontSize: '0.75rem',
                    fontWeight: '600'
                  }}>
                    {count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Search and Filter */}
      <div className="vimarsh-admin-card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ padding: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={16} style={{ 
              position: 'absolute', 
              left: '0.75rem', 
              top: '50%', 
              transform: 'translateY(-50%)', 
              color: '#6b7280' 
            }} />
            <input
              type="text"
              placeholder="Search personalities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem 0.75rem 2.5rem',
                border: '1px solid #d1d5db',
                borderRadius: '0.5rem',
                fontSize: '0.875rem'
              }}
            />
          </div>
          <div style={{ position: 'relative', minWidth: '150px' }}>
            <Filter size={16} style={{ 
              position: 'absolute', 
              left: '0.75rem', 
              top: '50%', 
              transform: 'translateY(-50%)', 
              color: '#6b7280' 
            }} />
            <select
              value={domainFilter}
              onChange={(e) => setDomainFilter(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem 0.75rem 2.5rem',
                border: '1px solid #d1d5db',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                backgroundColor: 'white'
              }}
            >
              <option value="all">All Domains</option>
              <option value="spiritual">Spiritual</option>
              <option value="scientific">Scientific</option>
              <option value="philosophical">Philosophical</option>
              <option value="historical">Historical</option>
              <option value="literary">Literary</option>
              <option value="leadership">Leadership</option>
              <option value="psychology">Psychology</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="vimarsh-admin-error" style={{ marginBottom: '1.5rem' }}>
          <AlertTriangle size={20} />
          <div>
            <strong>Error Loading Personalities</strong>
            <p>{error}</p>
          </div>
          <button 
            className="vimarsh-btn-secondary" 
            onClick={loadPersonalities}
            style={{ marginLeft: 'auto' }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Personalities List */}
      <div className="vimarsh-admin-card">
        <div className="card-header">
          <h3>🤖 All Personalities ({filteredPersonalities.length})</h3>
        </div>
        
        {filteredPersonalities.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
            {personalities.length === 0 ? (
              <>
                <Bot size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
                <p>No personalities available. Click "Add Personality" to get started.</p>
              </>
            ) : (
              <>
                <Search size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
                <p>No personalities match your search criteria.</p>
              </>
            )}
          </div>
        ) : (
          <div style={{ padding: '1rem' }}>
            <div style={{ display: 'grid', gap: '1rem' }}>
              {filteredPersonalities.map((personality) => (
                <div
                  key={personality.id}
                  style={{
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.75rem',
                    padding: '1.5rem',
                    backgroundColor: 'white',
                    transition: 'all 0.2s',
                    cursor: 'pointer'
                  }}
                  onClick={() => setSelectedPersonality(personality)}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = getDomainColor(personality.domain);
                    e.currentTarget.style.boxShadow = `0 4px 12px ${getDomainColor(personality.domain)}20`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#e5e7eb';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                    {/* Personality Icon & Status */}
                    <div style={{ 
                      display: 'flex', 
                      flexDirection: 'column', 
                      alignItems: 'center', 
                      gap: '0.5rem',
                      minWidth: '60px'
                    }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        borderRadius: '50%',
                        backgroundColor: `${getDomainColor(personality.domain)}20`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '1.5rem'
                      }}>
                        {getDomainIcon(personality.domain)}
                      </div>
                      {personality.isActive ? (
                        <CheckCircle size={16} style={{ color: '#10B981' }} />
                      ) : (
                        <XCircle size={16} style={{ color: '#EF4444' }} />
                      )}
                    </div>

                    {/* Personality Details */}
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                        <h4 style={{ margin: 0, fontSize: '1.125rem', fontWeight: '600' }}>
                          {personality.name}
                        </h4>
                        <span style={{
                          padding: '0.25rem 0.75rem',
                          backgroundColor: getDomainColor(personality.domain),
                          color: 'white',
                          borderRadius: '1rem',
                          fontSize: '0.75rem',
                          fontWeight: '600'
                        }}>
                          {formatDomainName(personality.domain)}
                        </span>
                      </div>
                      
                      <p style={{ 
                        margin: '0 0 1rem 0', 
                        color: '#6b7280', 
                        fontSize: '0.875rem',
                        lineHeight: '1.4'
                      }}>
                        {personality.description}
                      </p>

                      {/* Metrics */}
                      <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.75rem', color: '#6b7280' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <Users size={12} />
                          <span>{personality.usageCount} uses</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <Activity size={12} />
                          <span>{personality.responseQuality}% quality</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <Bot size={12} />
                          <span>{personality.contentSources} sources</span>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        style={{
                          padding: '0.5rem',
                          border: '1px solid #d1d5db',
                          borderRadius: '0.375rem',
                          backgroundColor: 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#f3f4f6';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'white';
                        }}
                        onClick={(e) => {
                          e.stopPropagation();
                          // TODO: Implement view details
                        }}
                      >
                        <Eye size={16} style={{ color: '#6b7280' }} />
                      </button>
                      <button
                        style={{
                          padding: '0.5rem',
                          border: '1px solid #d1d5db',
                          borderRadius: '0.375rem',
                          backgroundColor: 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#f3f4f6';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'white';
                        }}
                        onClick={(e) => {
                          e.stopPropagation();
                          // TODO: Implement edit
                        }}
                      >
                        <Edit3 size={16} style={{ color: '#6b7280' }} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Add Personality Modal */}
      {showAddModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '0.75rem',
            padding: '2rem',
            maxWidth: '500px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>Add New Personality</h3>
            <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
              This feature is coming soon. For now, personalities are managed through the backend configuration.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
              <button
                className="vimarsh-btn-secondary"
                onClick={() => setShowAddModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PersonalityManagement;
