import React, { useState, useEffect } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
import '../../styles/admin.css';

interface ContentItem {
  id: string;
  title: string;
  type: string;
  source: string;
  author: string;
  description: string;
  content_preview: string;
  file_size: number;
  upload_date: string;
  status: 'pending' | 'approved' | 'rejected';
  quality_score: number;
  associated_personalities: string[];
  domain: string;
  language: string;
  tags: string[];
  metadata: any;
}

interface SourceVerification {
  source_name: string;
  author: string;
  publication_year?: number;
  publisher?: string;
  isbn?: string;
  authority_level: 'primary' | 'secondary' | 'tertiary';
  verification_status: 'verified' | 'pending' | 'disputed';
  scholarly_citations: string[];
  authenticity_notes: string;
}

const ContentManagement: React.FC = () => {
  const { user } = useAdmin();
  const [content, setContent] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [filter, setFilter] = useState({
    domain: '',
    status: '',
    personality: '',
    search: ''
  });

  // New content form state
  const [newContent, setNewContent] = useState({
    title: '',
    type: 'book',
    source: '',
    author: '',
    description: '',
    domain: 'spiritual',
    language: 'English',
    tags: [],
    content: '',
    citation: {
      book: '',
      chapter: '',
      verse: '',
      page: ''
    },
    verification: {
      source_name: '',
      author: '',
      authority_level: 'primary' as 'primary' | 'secondary' | 'tertiary',
      scholarly_citations: [''],
      authenticity_notes: ''
    }
  });

  useEffect(() => {
    if (user?.permissions.can_access_admin_endpoints) {
      loadContent();
    }
  }, [user]);

  const loadContent = async () => {
    try {
      setLoading(true);
      // This would call the backend API
      const response = await fetch('/api/admin/content', {
        headers: {
          'Authorization': `Bearer ${await getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setContent(data.content || []);
    } catch (error) {
      console.error('Failed to load content:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAccessToken = async (): Promise<string> => {
    // Implementation would get token from MSAL
    return 'mock-token';
  };

  const handleAddContent = async () => {
    try {
      const contentData = {
        ...newContent,
        tags: newContent.tags,
        metadata: {
          citation: newContent.citation,
          verification: newContent.verification
        }
      };

      const response = await fetch('/api/admin/content', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await getAccessToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(contentData)
      });

      if (response.ok) {
        setShowAddForm(false);
        setNewContent({
          title: '',
          type: 'book',
          source: '',
          author: '',
          description: '',
          domain: 'spiritual',
          language: 'English',
          tags: [],
          content: '',
          citation: { book: '', chapter: '', verse: '', page: '' },
          verification: {
            source_name: '',
            author: '',
            authority_level: 'primary',
            scholarly_citations: [''],
            authenticity_notes: ''
          }
        });
        loadContent();
      }
    } catch (error) {
      console.error('Failed to add content:', error);
    }
  };

  const handleDeleteContent = async (contentId: string) => {
    if (!confirm('Are you sure you want to delete this content?')) return;

    try {
      const response = await fetch(`/api/admin/content/${contentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${await getAccessToken()}`
        }
      });

      if (response.ok) {
        loadContent();
      }
    } catch (error) {
      console.error('Failed to delete content:', error);
    }
  };

  const handleApproveContent = async (contentId: string) => {
    try {
      const response = await fetch(`/api/admin/content/${contentId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await getAccessToken()}`
        }
      });

      if (response.ok) {
        loadContent();
      }
    } catch (error) {
      console.error('Failed to approve content:', error);
    }
  };

  const filteredContent = content.filter(item => {
    return (
      (!filter.domain || item.domain === filter.domain) &&
      (!filter.status || item.status === filter.status) &&
      (!filter.search || 
        item.title.toLowerCase().includes(filter.search.toLowerCase()) ||
        item.author.toLowerCase().includes(filter.search.toLowerCase()) ||
        item.source.toLowerCase().includes(filter.search.toLowerCase())
      )
    );
  });

  if (!user?.permissions.can_access_admin_endpoints) {
    return <div className="admin-error">Access denied: Admin permissions required</div>;
  }

  return (
    <div className="content-management">
      <div className="content-header">
        <h2>📚 Content Management</h2>
        <div className="content-actions">
          <button 
            className="btn-primary"
            onClick={() => setShowAddForm(true)}
          >
            ➕ Add New Content
          </button>
          <button 
            className="btn-secondary"
            onClick={loadContent}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="content-filters">
        <select 
          value={filter.domain} 
          onChange={(e) => setFilter({...filter, domain: e.target.value})}
        >
          <option value="">All Domains</option>
          <option value="spiritual">🕉️ Spiritual</option>
          <option value="scientific">🔬 Scientific</option>
          <option value="historical">🏛️ Historical</option>
          <option value="philosophical">💭 Philosophical</option>
        </select>

        <select 
          value={filter.status} 
          onChange={(e) => setFilter({...filter, status: e.target.value})}
        >
          <option value="">All Status</option>
          <option value="pending">⏳ Pending</option>
          <option value="approved">✅ Approved</option>
          <option value="rejected">❌ Rejected</option>
        </select>

        <input
          type="text"
          placeholder="Search content..."
          value={filter.search}
          onChange={(e) => setFilter({...filter, search: e.target.value})}
        />
      </div>

      {/* Content List */}
      <div className="content-list">
        {loading ? (
          <div className="loading">Loading content...</div>
        ) : (
          <table className="content-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Source</th>
                <th>Author</th>
                <th>Domain</th>
                <th>Status</th>
                <th>Quality</th>
                <th>Personalities</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredContent.map(item => (
                <tr key={item.id}>
                  <td>
                    <div className="content-title">
                      {item.title}
                      <div className="content-preview">{item.content_preview}</div>
                    </div>
                  </td>
                  <td>{item.source}</td>
                  <td>{item.author}</td>
                  <td>
                    <span className={`domain-badge ${item.domain}`}>
                      {item.domain}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${item.status}`}>
                      {item.status}
                    </span>
                  </td>
                  <td>{item.quality_score.toFixed(1)}</td>
                  <td>
                    {item.associated_personalities.map(p => (
                      <span key={p} className="personality-tag">{p}</span>
                    ))}
                  </td>
                  <td>
                    <div className="content-actions">
                      {item.status === 'pending' && (
                        <button 
                          className="btn-approve"
                          onClick={() => handleApproveContent(item.id)}
                        >
                          ✅
                        </button>
                      )}
                      <button 
                        className="btn-edit"
                        onClick={() => setSelectedContent(item)}
                      >
                        ✏️
                      </button>
                      <button 
                        className="btn-delete"
                        onClick={() => handleDeleteContent(item.id)}
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Add Content Modal */}
      {showAddForm && (
        <div className="modal-overlay">
          <div className="modal-content add-content-modal">
            <div className="modal-header">
              <h3>📚 Add New Authentic Content</h3>
              <button onClick={() => setShowAddForm(false)}>✕</button>
            </div>
            
            <form onSubmit={(e) => { e.preventDefault(); handleAddContent(); }}>
              <div className="form-section">
                <h4>📋 Basic Information</h4>
                <div className="form-row">
                  <div className="form-group">
                    <label>Title *</label>
                    <input
                      type="text"
                      value={newContent.title}
                      onChange={(e) => setNewContent({...newContent, title: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Content Type *</label>
                    <select
                      value={newContent.type}
                      onChange={(e) => setNewContent({...newContent, type: e.target.value})}
                    >
                      <option value="book">📖 Book/Scripture</option>
                      <option value="article">📄 Article/Paper</option>
                      <option value="speech">🗣️ Speech</option>
                      <option value="letter">✉️ Letter</option>
                      <option value="poem">📝 Poem</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Source/Book Name *</label>
                    <input
                      type="text"
                      value={newContent.source}
                      onChange={(e) => setNewContent({...newContent, source: e.target.value})}
                      placeholder="e.g., Bhagavad Gita, Meditations, Theory of Relativity"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Author *</label>
                    <input
                      type="text"
                      value={newContent.author}
                      onChange={(e) => setNewContent({...newContent, author: e.target.value})}
                      placeholder="e.g., Vyasa, Marcus Aurelius, Albert Einstein"
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Description *</label>
                  <textarea
                    value={newContent.description}
                    onChange={(e) => setNewContent({...newContent, description: e.target.value})}
                    placeholder="Brief description of the content and its significance"
                    required
                  />
                </div>
              </div>

              <div className="form-section">
                <h4>📚 Source Citation</h4>
                <div className="form-row">
                  <div className="form-group">
                    <label>Chapter/Book</label>
                    <input
                      type="text"
                      value={newContent.citation.chapter}
                      onChange={(e) => setNewContent({
                        ...newContent, 
                        citation: {...newContent.citation, chapter: e.target.value}
                      })}
                      placeholder="e.g., Chapter 2, Book IV"
                    />
                  </div>
                  <div className="form-group">
                    <label>Verse/Section</label>
                    <input
                      type="text"
                      value={newContent.citation.verse}
                      onChange={(e) => setNewContent({
                        ...newContent, 
                        citation: {...newContent.citation, verse: e.target.value}
                      })}
                      placeholder="e.g., Verse 47, Section 12"
                    />
                  </div>
                </div>
              </div>

              <div className="form-section">
                <h4>🛡️ Source Verification</h4>
                <div className="form-group">
                  <label>Authority Level *</label>
                  <select
                    value={newContent.verification.authority_level}
                    onChange={(e) => setNewContent({
                      ...newContent,
                      verification: {
                        ...newContent.verification,
                        authority_level: e.target.value as 'primary' | 'secondary' | 'tertiary'
                      }
                    })}
                  >
                    <option value="primary">🔴 Primary Source (Original text/translation)</option>
                    <option value="secondary">🟡 Secondary Source (Scholarly commentary)</option>
                    <option value="tertiary">🟢 Tertiary Source (Popular adaptation)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Authenticity Notes</label>
                  <textarea
                    value={newContent.verification.authenticity_notes}
                    onChange={(e) => setNewContent({
                      ...newContent,
                      verification: {
                        ...newContent.verification,
                        authenticity_notes: e.target.value
                      }
                    })}
                    placeholder="Notes about source authenticity, translation quality, scholarly consensus, etc."
                  />
                </div>
              </div>

              <div className="form-section">
                <h4>📝 Content Text</h4>
                <div className="form-group">
                  <label>Full Content *</label>
                  <textarea
                    value={newContent.content}
                    onChange={(e) => setNewContent({...newContent, content: e.target.value})}
                    placeholder="Enter the complete authentic text..."
                    rows={10}
                    required
                  />
                </div>
              </div>

              <div className="form-actions">
                <button type="button" onClick={() => setShowAddForm(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  ✅ Add Authentic Content
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="content-stats">
        <div className="stat-card">
          <h4>📊 Content Statistics</h4>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Total Content:</span>
              <span className="stat-value">{content.length}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Approved:</span>
              <span className="stat-value approved">
                {content.filter(c => c.status === 'approved').length}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Pending:</span>
              <span className="stat-value pending">
                {content.filter(c => c.status === 'pending').length}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Personalities:</span>
              <span className="stat-value">8 Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContentManagement;
