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
    <div className={`session-manager relative ${className}`}>
      {/* Session Dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          className="flex items-center gap-2 px-3 py-2 bg-white border border-neutral-300 rounded-lg hover:bg-neutral-50 transition-colors min-w-[200px] text-left"
        >
          <span className="flex-1 truncate text-sm font-medium text-neutral-700">
            {getCurrentSessionTitle()}
          </span>
          <span className={`transform transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}>
            ▼
          </span>
        </button>

        {isDropdownOpen && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-neutral-200 rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto">
            {/* New Session Option */}
            <button
              onClick={handleNewSession}
              className="w-full px-4 py-3 text-left hover:bg-neutral-50 border-b border-neutral-100 flex items-center gap-2"
            >
              <span className="text-saffron-primary">✨</span>
              <span className="font-medium text-neutral-800">{t('newConversation')}</span>
            </button>

            {/* Recent Sessions */}
            {recentSessions.length > 0 && (
              <>
                <div className="px-4 py-2 text-xs font-medium text-neutral-500 bg-neutral-50">
                  {t('recentConversations')}
                </div>
                {recentSessions.map((session) => (
                  <button
                    key={session.id}
                    onClick={() => handleSessionSelect(session.id)}
                    className={`w-full px-4 py-3 text-left hover:bg-neutral-50 flex items-center justify-between group ${
                      session.id === currentSessionId ? 'bg-saffron-light' : ''
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-neutral-800 truncate">
                        {session.title}
                      </div>
                      <div className="text-xs text-neutral-500 flex items-center gap-2 mt-1">
                        <span>{new Date(session.updatedAt).toLocaleDateString()}</span>
                        <span>•</span>
                        <span>{session.metadata.messageCount} {t('messages')}</span>
                        <span className="ml-1">
                          {session.language === 'hi' ? '🇮🇳' : '🇬🇧'}
                        </span>
                      </div>
                    </div>
                    {session.id === currentSessionId && (
                      <span className="text-saffron-primary text-sm">✓</span>
                    )}
                  </button>
                ))}
              </>
            )}

            {recentSessions.length === 0 && (
              <div className="px-4 py-6 text-center text-neutral-500">
                <div className="text-2xl mb-2">💭</div>
                <p className="text-sm">{t('noConversations')}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Click outside to close */}
      {isDropdownOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsDropdownOpen(false)}
        />
      )}
    </div>
  );
};

export default SessionManager;
