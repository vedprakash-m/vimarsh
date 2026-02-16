import React, { useState, useEffect, useCallback } from 'react';
import { conversationHistory, ConversationSession } from '../utils/conversationHistory';
import { useLanguage } from '../contexts/LanguageContext';
import { useMsal } from '@azure/msal-react';
import spiritualGuidanceAPI from '../utils/api';

interface ConversationHistoryProps {
  onSessionSelect: (sessionId: string) => void;
  currentSessionId: string | null;
  onNewConversation: () => void;
}

const ConversationHistory: React.FC<ConversationHistoryProps> = ({
  onSessionSelect,
  currentSessionId,
  onNewConversation
}) => {
  const { t } = useLanguage();
  const { accounts } = useMsal();
  const user = accounts[0] || null;
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredSessions, setFilteredSessions] = useState<ConversationSession[]>([]);
  const [isExporting, setIsExporting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

  useEffect(() => {
    loadSessions();
  }, [user]);

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = conversationHistory.searchSessions(searchQuery);
      setFilteredSessions(filtered);
    } else {
      setFilteredSessions(sessions);
    }
  }, [searchQuery, sessions]);

  const loadSessions = useCallback(async () => {
    // For authenticated users, fetch from backend API
    if (user) {
      try {
        const response = await spiritualGuidanceAPI.getConversationHistory(50);
        // Map backend format to ConversationSession format
        const mappedSessions: ConversationSession[] = response.conversations.map(conv => ({
          id: conv.sessionId,
          title: conv.summary || `Conversation with ${conv.personalityId}`,
          messages: conv.messages.map((msg, idx) => ({
            id: `${conv.sessionId}-${idx}`,
            text: msg.text,
            sender: msg.sender,
            timestamp: new Date(msg.timestamp)
          })),
          createdAt: new Date(conv.createdAt),
          updatedAt: new Date(conv.endedAt || conv.createdAt),
          language: 'en' as const,
          metadata: {
            messageCount: conv.turnCount,
            lastActivity: new Date(conv.endedAt || conv.createdAt),
            topics: conv.keyTopics
          }
        }));
        setSessions(mappedSessions);
        return;
      } catch (error) {
        console.warn('Failed to load conversations from API, falling back to local storage:', error);
      }
    }
    
    // Fallback to localStorage for unauthenticated users or API failure
    const loadedSessions = conversationHistory.getSessions();
    setSessions(loadedSessions);
  }, [user]);

  const handleDeleteSession = (sessionId: string) => {
    conversationHistory.deleteSession(sessionId);
    loadSessions();
    setShowDeleteConfirm(null);
    
    // If the deleted session was current, trigger new conversation
    if (sessionId === currentSessionId) {
      onNewConversation();
    }
  };

  const handleExportSession = async (sessionId: string, format: 'txt' | 'json' = 'txt') => {
    setIsExporting(true);
    try {
      const content = conversationHistory.exportSession(sessionId, format);
      const session = conversationHistory.getSession(sessionId);
      
      if (session) {
        const filename = `vimarsh_${session.title.replace(/[^a-zA-Z0-9]/g, '_')}.${format}`;
        downloadFile(content, filename, format === 'json' ? 'application/json' : 'text/plain');
      }
    } catch (error) {
      console.error('Failed to export session:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportAll = async (format: 'txt' | 'json' = 'txt') => {
    setIsExporting(true);
    try {
      const content = conversationHistory.exportAllSessions(format);
      const filename = `vimarsh_all_conversations_${new Date().toISOString().split('T')[0]}.${format}`;
      downloadFile(content, filename, format === 'json' ? 'application/json' : 'text/plain');
    } catch (error) {
      console.error('Failed to export all sessions:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return t('today');
    } else if (diffDays === 1) {
      return t('yesterday');
    } else if (diffDays < 7) {
      return `${diffDays} ${t('daysAgo')}`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getStorageStats = () => {
    return conversationHistory.getStorageStats() || { totalSessions: 0, totalMessages: 0 };
  };

  const stats = getStorageStats();

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: '1rem',
      border: '1px solid #e2e8f0',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '1rem',
        borderBottom: '1px solid #e2e8f0'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1rem'
        }}>
          <h2 style={{
            margin: 0,
            fontSize: '1.25rem',
            fontWeight: '700',
            color: '#1e293b'
          }}>
            {t('conversationHistory')}
          </h2>
          <button
            onClick={onNewConversation}
            style={{
              background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
              border: 'none',
              borderRadius: '0.5rem',
              padding: '0.5rem 1rem',
              color: 'white',
              fontSize: '0.875rem',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s ease'
            }}
            title={t('newConversation')}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(255, 107, 53, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <span>✨</span>
            {t('new')}
          </button>
        </div>

        {/* Search */}
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            placeholder={t('searchConversations')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              paddingLeft: '2.5rem',
              paddingRight: '1rem',
              paddingTop: '0.5rem',
              paddingBottom: '0.5rem',
              border: '1px solid #e2e8f0',
              borderRadius: '0.5rem',
              outline: 'none',
              fontSize: '0.875rem',
              backgroundColor: '#f8fafc',
              boxSizing: 'border-box'
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = '#FF6B35';
              e.currentTarget.style.backgroundColor = '#ffffff';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = '#e2e8f0';
              e.currentTarget.style.backgroundColor = '#f8fafc';
            }}
          />
          <span style={{
            position: 'absolute',
            left: '0.75rem',
            top: '50%',
            transform: 'translateY(-50%)',
            color: '#64748b'
          }}>🔍</span>
        </div>

        {/* Stats */}
        <div style={{
          marginTop: '0.75rem',
          fontSize: '0.75rem',
          color: '#64748b',
          display: 'flex',
          justifyContent: 'space-between'
        }}>
          <span>{stats.totalSessions} {t('sessions')}</span>
          <span>{stats.totalMessages} {t('messages')}</span>
        </div>
      </div>

      {/* Export Controls */}
      <div style={{
        padding: '1rem',
        borderBottom: '1px solid #e2e8f0',
        backgroundColor: '#f8fafc'
      }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => handleExportAll('txt')}
            disabled={isExporting || sessions.length === 0}
            style={{
              flex: 1,
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '0.5rem',
              padding: '0.5rem',
              fontSize: '0.75rem',
              color: '#64748b',
              cursor: isExporting || sessions.length === 0 ? 'not-allowed' : 'pointer',
              opacity: isExporting || sessions.length === 0 ? 0.5 : 1,
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              if (!isExporting && sessions.length > 0) {
                e.currentTarget.style.backgroundColor = '#f1f5f9';
                e.currentTarget.style.borderColor = '#cbd5e1';
              }
            }}
            onMouseLeave={(e) => {
              if (!isExporting && sessions.length > 0) {
                e.currentTarget.style.backgroundColor = '#ffffff';
                e.currentTarget.style.borderColor = '#e2e8f0';
              }
            }}
          >
            📄 {t('exportTxt')}
          </button>
          <button
            onClick={() => handleExportAll('json')}
            disabled={isExporting || sessions.length === 0}
            style={{
              flex: 1,
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '0.5rem',
              padding: '0.5rem',
              fontSize: '0.75rem',
              color: '#64748b',
              cursor: isExporting || sessions.length === 0 ? 'not-allowed' : 'pointer',
              opacity: isExporting || sessions.length === 0 ? 0.5 : 1,
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              if (!isExporting && sessions.length > 0) {
                e.currentTarget.style.backgroundColor = '#f1f5f9';
                e.currentTarget.style.borderColor = '#cbd5e1';
              }
            }}
            onMouseLeave={(e) => {
              if (!isExporting && sessions.length > 0) {
                e.currentTarget.style.backgroundColor = '#ffffff';
                e.currentTarget.style.borderColor = '#e2e8f0';
              }
            }}
          >
            📊 {t('exportJson')}
          </button>
        </div>
        {isExporting && (
          <div style={{
            marginTop: '0.5rem',
            fontSize: '0.75rem',
            color: '#64748b',
            textAlign: 'center'
          }}>
            {t('exporting')}...
          </div>
        )}
      </div>

      {/* Session List */}
      <div style={{
        flex: 1,
        overflowY: 'auto'
      }}>
        {filteredSessions.length === 0 ? (
          <div style={{
            padding: '2rem',
            textAlign: 'center',
            color: '#64748b'
          }}>
            {searchQuery ? (
              <>
                <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🔍</div>
                <p style={{ margin: '0 0 0.5rem 0' }}>{t('noSearchResults')}</p>
                <p style={{ fontSize: '0.875rem', margin: 0 }}>{t('tryDifferentSearch')}</p>
              </>
            ) : (
              <>
                <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>💭</div>
                <p style={{ margin: '0 0 0.5rem 0' }}>{t('noConversations')}</p>
                <p style={{ fontSize: '0.875rem', margin: 0 }}>{t('startFirstConversation')}</p>
              </>
            )}
          </div>
        ) : (
          <div style={{
            padding: '0.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.25rem'
          }}>
            {filteredSessions.map((session) => (
              <div
                key={session.id}
                data-session={session.id}
                style={{
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  position: 'relative',
                  background: session.id === currentSessionId ? '#fef3e2' : 'transparent',
                  border: session.id === currentSessionId ? '1px solid #FF6B35' : '1px solid transparent'
                }}
                onClick={() => onSessionSelect(session.id)}
                onMouseEnter={(e) => {
                  if (session.id !== currentSessionId) {
                    e.currentTarget.style.backgroundColor = '#f8fafc';
                  }
                  // Show action buttons
                  const actionButtons = e.currentTarget.querySelector('[data-action-buttons]') as HTMLElement;
                  if (actionButtons) {
                    actionButtons.style.opacity = '1';
                  }
                }}
                onMouseLeave={(e) => {
                  if (session.id !== currentSessionId) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }
                  // Hide action buttons
                  const actionButtons = e.currentTarget.querySelector('[data-action-buttons]') as HTMLElement;
                  if (actionButtons) {
                    actionButtons.style.opacity = '0';
                  }
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start'
                }}>
                  <div style={{
                    flex: 1,
                    minWidth: 0
                  }}>
                    <h3 style={{
                      fontWeight: '500',
                      color: '#1e293b',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      fontSize: '0.875rem',
                      margin: 0
                    }}>
                      {session.title}
                    </h3>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      marginTop: '0.25rem',
                      fontSize: '0.75rem',
                      color: '#64748b'
                    }}>
                      <span>{formatDate(new Date(session.updatedAt))}</span>
                      <span>•</span>
                      <span>{session.metadata.messageCount} {t('messages')}</span>
                      <span>•</span>
                      <span>
                        {session.language === 'hi' ? '🇮🇳' : '🇬🇧'}
                      </span>
                    </div>
                    {session.metadata.topics && session.metadata.topics.length > 0 && (
                      <div style={{
                        marginTop: '0.5rem',
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: '0.25rem'
                      }}>
                        {session.metadata.topics.slice(0, 3).map((topic, index) => (
                          <span
                            key={index}
                            style={{
                              display: 'inline-block',
                              padding: '0.25rem 0.5rem',
                              backgroundColor: '#f1f5f9',
                              color: '#64748b',
                              fontSize: '0.75rem',
                              borderRadius: '0.25rem'
                            }}
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Action buttons */}
                  <div 
                    data-action-buttons="true"
                    style={{
                      display: 'flex',
                      gap: '0.25rem',
                      opacity: 0,
                      transition: 'opacity 0.2s ease'
                    }}
                  >
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleExportSession(session.id, 'txt');
                      }}
                      style={{
                        padding: '0.25rem',
                        background: 'none',
                        border: 'none',
                        color: '#94a3b8',
                        borderRadius: '0.25rem',
                        cursor: 'pointer',
                        transition: 'color 0.2s ease'
                      }}
                      title={t('exportSession')}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.color = '#64748b';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.color = '#94a3b8';
                      }}
                    >
                      📄
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowDeleteConfirm(session.id);
                      }}
                      style={{
                        padding: '0.25rem',
                        background: 'none',
                        border: 'none',
                        color: '#94a3b8',
                        borderRadius: '0.25rem',
                        cursor: 'pointer',
                        transition: 'color 0.2s ease'
                      }}
                      title={t('deleteSession')}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.color = '#ef4444';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.color = '#94a3b8';
                      }}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
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
          zIndex: 50
        }}>
          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '0.5rem',
            padding: '1.5rem',
            maxWidth: '24rem',
            margin: '1rem',
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)'
          }}>
            <h3 style={{
              fontSize: '1.125rem',
              fontWeight: '600',
              color: '#1e293b',
              marginBottom: '1rem',
              margin: 0
            }}>
              {t('confirmDelete')}
            </h3>
            <p style={{
              color: '#64748b',
              marginBottom: '1.5rem',
              lineHeight: '1.5',
              margin: '1rem 0 1.5rem 0'
            }}>
              {t('deleteSessionWarning')}
            </p>
            <div style={{
              display: 'flex',
              gap: '0.75rem'
            }}>
              <button
                onClick={() => setShowDeleteConfirm(null)}
                style={{
                  flex: 1,
                  background: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '0.5rem',
                  padding: '0.5rem 1rem',
                  color: '#64748b',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f1f5f9';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#f8fafc';
                }}
              >
                {t('cancel')}
              </button>
              <button
                onClick={() => handleDeleteSession(showDeleteConfirm)}
                style={{
                  flex: 1,
                  background: '#ef4444',
                  border: 'none',
                  borderRadius: '0.5rem',
                  padding: '0.5rem 1rem',
                  color: 'white',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#dc2626';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#ef4444';
                }}
              >
                {t('delete')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConversationHistory;
