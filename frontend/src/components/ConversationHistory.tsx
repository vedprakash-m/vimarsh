import React, { useState, useEffect } from 'react';
import { conversationHistory, ConversationSession } from '../utils/conversationHistory';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from './AuthenticationWrapper';

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
  const { user } = useAuth();
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredSessions, setFilteredSessions] = useState<ConversationSession[]>([]);
  const [isExporting, setIsExporting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = conversationHistory.searchSessions(searchQuery);
      setFilteredSessions(filtered);
    } else {
      setFilteredSessions(sessions);
    }
  }, [searchQuery, sessions]);

  const loadSessions = () => {
    const loadedSessions = conversationHistory.getSessions();
    setSessions(loadedSessions);
  };

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
    return conversationHistory.getStorageStats();
  };

  const stats = getStorageStats();

  return (
    <div className="conversation-history">
      {/* Header */}
      <div className="p-4 border-b border-neutral-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="heading-3 text-neutral-800">
            {t('conversationHistory')}
          </h2>
          <button
            onClick={onNewConversation}
            className="btn-primary text-sm"
            title={t('newConversation')}
          >
            <span className="mr-2">✨</span>
            {t('new')}
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder={t('searchConversations')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-saffron-primary focus:border-transparent"
          />
          <span className="absolute left-3 top-2.5 text-neutral-400">🔍</span>
        </div>

        {/* Stats */}
        <div className="mt-3 text-xs text-neutral-500 flex justify-between">
          <span>{stats.totalSessions} {t('sessions')}</span>
          <span>{stats.totalMessages} {t('messages')}</span>
        </div>
      </div>

      {/* Export Controls */}
      <div className="p-4 border-b border-neutral-200 bg-neutral-50">
        <div className="flex gap-2">
          <button
            onClick={() => handleExportAll('txt')}
            disabled={isExporting || sessions.length === 0}
            className="btn-secondary text-xs flex-1"
          >
            📄 {t('exportTxt')}
          </button>
          <button
            onClick={() => handleExportAll('json')}
            disabled={isExporting || sessions.length === 0}
            className="btn-secondary text-xs flex-1"
          >
            📊 {t('exportJson')}
          </button>
        </div>
        {isExporting && (
          <div className="mt-2 text-xs text-neutral-600 text-center">
            {t('exporting')}...
          </div>
        )}
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto">
        {filteredSessions.length === 0 ? (
          <div className="p-8 text-center text-neutral-500">
            {searchQuery ? (
              <>
                <div className="text-4xl mb-4">🔍</div>
                <p>{t('noSearchResults')}</p>
                <p className="text-sm mt-2">{t('tryDifferentSearch')}</p>
              </>
            ) : (
              <>
                <div className="text-4xl mb-4">💭</div>
                <p>{t('noConversations')}</p>
                <p className="text-sm mt-2">{t('startFirstConversation')}</p>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {filteredSessions.map((session) => (
              <div
                key={session.id}
                className={`session-item p-3 rounded-lg cursor-pointer transition-colors relative group ${
                  session.id === currentSessionId
                    ? 'bg-saffron-light border border-saffron-primary'
                    : 'hover:bg-neutral-100'
                }`}
                onClick={() => onSessionSelect(session.id)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-neutral-800 truncate text-sm">
                      {session.title}
                    </h3>
                    <div className="flex items-center gap-2 mt-1 text-xs text-neutral-500">
                      <span>{formatDate(new Date(session.updatedAt))}</span>
                      <span>•</span>
                      <span>{session.metadata.messageCount} {t('messages')}</span>
                      <span>•</span>
                      <span className={`flag flag-${session.language}`}>
                        {session.language === 'hi' ? '🇮🇳' : '🇬🇧'}
                      </span>
                    </div>
                    {session.metadata.topics && session.metadata.topics.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {session.metadata.topics.slice(0, 3).map((topic, index) => (
                          <span
                            key={index}
                            className="inline-block px-2 py-1 bg-neutral-200 text-neutral-600 text-xs rounded"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Action buttons */}
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleExportSession(session.id, 'txt');
                      }}
                      className="p-1 text-neutral-400 hover:text-neutral-600 rounded"
                      title={t('exportSession')}
                    >
                      📄
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowDeleteConfirm(session.id);
                      }}
                      className="p-1 text-neutral-400 hover:text-red-600 rounded"
                      title={t('deleteSession')}
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-4">
            <h3 className="heading-4 text-neutral-800 mb-4">
              {t('confirmDelete')}
            </h3>
            <p className="body-text text-neutral-600 mb-6">
              {t('deleteSessionWarning')}
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="btn-secondary flex-1"
              >
                {t('cancel')}
              </button>
              <button
                onClick={() => handleDeleteSession(showDeleteConfirm)}
                className="btn-danger flex-1"
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
