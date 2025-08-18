import React, { useState, useEffect } from 'react';
import { conversationHistory } from '../utils/conversationHistory';
import { useLanguage } from '../contexts/LanguageContext';

interface SessionManagerProps {
  currentSessionId: string | null;
  onSessionChange: (sessionId: string) => void;
  onNewSession: () => void;
  className?: string;
}

const SessionManager: React.FC<SessionManagerProps> = ({
  currentSessionId,
  onSessionChange,
  onNewSession,
  className = ''
}) => {
  const { t } = useLanguage();
  const [recentSessions, setRecentSessions] = useState<any[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    loadRecentSessions();
  }, [currentSessionId]);

  const loadRecentSessions = () => {
    const sessions = conversationHistory.getSessions().slice(0, 5); // Get 5 most recent
    setRecentSessions(sessions);
  };

  const handleSessionSelect = (sessionId: string) => {
    onSessionChange(sessionId);
    setIsDropdownOpen(false);
  };

  const handleNewSession = () => {
    onNewSession();
    setIsDropdownOpen(false);
  };

  const getCurrentSessionTitle = () => {
    if (!currentSessionId) return t('newConversation');
    
    const session = conversationHistory.getSession(currentSessionId);
    return session ? session.title : t('newConversation');
  };

  return (
    <div style={{ position: 'relative' }}>
      {/* Session Dropdown */}
      <div style={{ position: 'relative' }}>
        <button
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem',
            background: '#ffffff',
            border: '2px solid #e2e8f0',
            borderRadius: '0.75rem',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            minWidth: '200px',
            textAlign: 'left',
            fontSize: '0.875rem',
            fontWeight: '500',
            color: '#334155'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#f8fafc';
            e.currentTarget.style.borderColor = '#FF6B35';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(255, 107, 53, 0.15)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#ffffff';
            e.currentTarget.style.borderColor = '#e2e8f0';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <span style={{
            flex: 1,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {getCurrentSessionTitle()}
          </span>
          <span style={{
            transform: isDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s ease',
            color: '#FF6B35'
          }}>
            ▼
          </span>
        </button>

        {isDropdownOpen && (
          <div style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            marginTop: '0.5rem',
            background: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '0.75rem',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.15)',
            zIndex: 50,
            maxHeight: '320px',
            overflowY: 'auto'
          }}>
            {/* New Session Option */}
            <button
              onClick={handleNewSession}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                textAlign: 'left',
                background: 'none',
                border: 'none',
                borderBottom: '1px solid #f1f5f9',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'background-color 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#fef7f3';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <span style={{ color: '#FF6B35' }}>✨</span>
              <span style={{
                fontWeight: '500',
                color: '#1e293b'
              }}>{t('newConversation')}</span>
            </button>

            {/* Recent Sessions */}
            {recentSessions.length > 0 && (
              <>
                <div style={{
                  padding: '0.5rem 1rem',
                  fontSize: '0.75rem',
                  fontWeight: '500',
                  color: '#64748b',
                  background: '#f8fafc',
                  borderBottom: '1px solid #f1f5f9'
                }}>
                  {t('recentConversations')}
                </div>
                {recentSessions.map((session) => (
                  <button
                    key={session.id}
                    onClick={() => handleSessionSelect(session.id)}
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem',
                      textAlign: 'left',
                      background: session.id === currentSessionId ? 'rgba(255, 107, 53, 0.1)' : 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                      if (session.id !== currentSessionId) {
                        e.currentTarget.style.backgroundColor = '#f8fafc';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (session.id !== currentSessionId) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }
                    }}
                  >
                    <div style={{
                      flex: 1,
                      minWidth: 0
                    }}>
                      <div style={{
                        fontSize: '0.875rem',
                        fontWeight: '500',
                        color: '#1e293b',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        {session.title}
                      </div>
                      <div style={{
                        fontSize: '0.75rem',
                        color: '#64748b',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        marginTop: '0.25rem'
                      }}>
                        <span>{new Date(session.updatedAt).toLocaleDateString()}</span>
                        <span>•</span>
                        <span>{session.metadata.messageCount} {t('messages')}</span>
                        <span style={{ marginLeft: '0.25rem' }}>
                          {session.language === 'hi' ? '🇮🇳' : '🇬🇧'}
                        </span>
                      </div>
                    </div>
                    {session.id === currentSessionId && (
                      <span style={{
                        color: '#FF6B35',
                        fontSize: '0.875rem'
                      }}>✓</span>
                    )}
                  </button>
                ))}
              </>
            )}

            {recentSessions.length === 0 && (
              <div style={{
                padding: '1.5rem 1rem',
                textAlign: 'center',
                color: '#64748b'
              }}>
                <div style={{
                  fontSize: '2rem',
                  marginBottom: '0.5rem'
                }}>💭</div>
                <p style={{
                  fontSize: '0.875rem',
                  margin: 0
                }}>{t('noConversations')}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Click outside to close */}
      {isDropdownOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 40
          }}
          onClick={() => setIsDropdownOpen(false)}
        />
      )}
    </div>
  );
};

export default SessionManager;
