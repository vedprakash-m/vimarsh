import React, { useState, useEffect, useMemo } from 'react';
import { conversationHistory, ConversationSession } from '../utils/conversationHistory';
import { conversationExporter, ExportOptions } from '../utils/conversationExporter';
import { useLanguage } from '../contexts/LanguageContext';
import { Message } from '../hooks/useSpiritualChat';

interface ConversationArchiveProps {
  onSessionSelect: (sessionId: string) => void;
  currentSessionId: string | null;
  className?: string;
}

interface SearchFilters {
  query: string;
  language: 'all' | 'en' | 'hi';
  dateRange: 'all' | 'today' | 'week' | 'month' | 'year';
  topics: string[];
  minMessages: number;
}

interface SearchResult {
  session: ConversationSession;
  matchedMessages: Message[];
  relevanceScore: number;
  highlightedTitle: string;
}

const ConversationArchive: React.FC<ConversationArchiveProps> = ({
  onSessionSelect,
  currentSessionId,
  className = ''
}) => {
  const { t } = useLanguage();
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({
    query: '',
    language: 'all',
    dateRange: 'all',
    topics: [],
    minMessages: 0
  });
  const [isAdvancedSearch, setIsAdvancedSearch] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedSessions, setSelectedSessions] = useState<Set<string>>(new Set());
  const [exportFormat, setExportFormat] = useState<'txt' | 'json' | 'csv' | 'markdown' | 'pdf'>('txt');
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    performSearch();
  }, [searchFilters, sessions]);

  const loadSessions = () => {
    const loadedSessions = conversationHistory.getSessions();
    setSessions(loadedSessions);
  };

  const performSearch = useMemo(() => {
    return debounce(async () => {
      if (!searchFilters.query.trim() && searchFilters.language === 'all' && searchFilters.dateRange === 'all') {
        setSearchResults(sessions.map(session => ({
          session,
          matchedMessages: [],
          relevanceScore: 1,
          highlightedTitle: session.title
        })));
        return;
      }

      setIsSearching(true);
      
      try {
        const results = await searchConversations(sessions, searchFilters);
        setSearchResults(results);
      } catch (error) {
        console.error('Search error:', error);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);
  }, [sessions, searchFilters]);

  const searchConversations = async (
    allSessions: ConversationSession[], 
    filters: SearchFilters
  ): Promise<SearchResult[]> => {
    const results: SearchResult[] = [];
    const query = filters.query.toLowerCase().trim();
    
    for (const session of allSessions) {
      // Apply filters
      if (filters.language !== 'all' && session.language !== filters.language) continue;
      if (session.metadata.messageCount < filters.minMessages) continue;
      if (!isWithinDateRange(session.updatedAt, filters.dateRange)) continue;

      let relevanceScore = 0;
      const matchedMessages: Message[] = [];
      let highlightedTitle = session.title;

      // Title matching (higher weight)
      if (query && session.title.toLowerCase().includes(query)) {
        relevanceScore += 3;
        highlightedTitle = highlightText(session.title, query);
      }

      // Message content matching
      if (query) {
        for (const message of session.messages) {
          if (message.text.toLowerCase().includes(query)) {
            matchedMessages.push(message);
            relevanceScore += message.sender === 'user' ? 1 : 2; // AI responses weighted higher
          }
          
          // Sanskrit text matching (if present)
          if (message.sanskritText && message.sanskritText.toLowerCase().includes(query)) {
            relevanceScore += 1.5;
          }

          // Citation matching
          if (message.citations) {
            for (const citation of message.citations) {
              if (citation.source.toLowerCase().includes(query) || 
                  citation.reference.toLowerCase().includes(query)) {
                relevanceScore += 2;
              }
            }
          }
        }
      }

      // Topic matching
      if (filters.topics.length > 0 && session.metadata.topics) {
        const matchingTopics = session.metadata.topics.filter(topic =>
          filters.topics.some(filterTopic => topic.toLowerCase().includes(filterTopic.toLowerCase()))
        );
        if (matchingTopics.length > 0) {
          relevanceScore += matchingTopics.length;
        } else if (filters.topics.length > 0) {
          continue; // Skip if specific topics are selected but none match
        }
      }

      // Recent activity boost
      const daysSinceUpdate = (Date.now() - new Date(session.updatedAt).getTime()) / (1000 * 60 * 60 * 24);
      if (daysSinceUpdate < 7) relevanceScore += 0.5;

      // Length boost (more substantial conversations)
      if (session.metadata.messageCount > 10) relevanceScore += 0.3;

      if (relevanceScore > 0 || !query) {
        results.push({
          session,
          matchedMessages,
          relevanceScore: relevanceScore || 1,
          highlightedTitle
        });
      }
    }

    // Sort by relevance score
    return results.sort((a, b) => b.relevanceScore - a.relevanceScore);
  };

  const isWithinDateRange = (date: Date, range: string): boolean => {
    const now = new Date();
    const sessionDate = new Date(date);
    
    switch (range) {
      case 'today':
        return sessionDate.toDateString() === now.toDateString();
      case 'week':
        return (now.getTime() - sessionDate.getTime()) <= (7 * 24 * 60 * 60 * 1000);
      case 'month':
        return (now.getTime() - sessionDate.getTime()) <= (30 * 24 * 60 * 60 * 1000);
      case 'year':
        return (now.getTime() - sessionDate.getTime()) <= (365 * 24 * 60 * 60 * 1000);
      default:
        return true;
    }
  };

  const highlightText = (text: string, query: string): string => {
    if (!query) return text;
    const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  };

  const escapeRegExp = (string: string): string => {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  };

  const debounce = (func: Function, wait: number) => {
    let timeout: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(null, args), wait);
    };
  };

  const handleBulkExport = async () => {
    if (selectedSessions.size === 0) return;
    
    setIsExporting(true);
    try {
      const sessionIds = Array.from(selectedSessions);
      const exportOptions: ExportOptions = {
        format: exportFormat,
        includeMetadata: true,
        includeCitations: true,
        includeSanskrit: true,
        language: 'all'
      };
      
      const content = await conversationExporter.exportSessions(sessionIds, exportOptions);
      const filename = `vimarsh_archive_${selectedSessions.size}_conversations_${new Date().toISOString().split('T')[0]}.${exportFormat}`;
      downloadFile(content, filename, getContentType(exportFormat));
      
      setSelectedSessions(new Set());
    } catch (error) {
      console.error('Export failed:', error);
      alert(`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsExporting(false);
    }
  };

  const getContentType = (format: string): string => {
    switch (format) {
      case 'json': return 'application/json';
      case 'csv': return 'text/csv';
      case 'markdown': return 'text/markdown';
      case 'pdf': return 'application/pdf';
      default: return 'text/plain';
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

  const toggleSessionSelection = (sessionId: string) => {
    const newSelection = new Set(selectedSessions);
    if (newSelection.has(sessionId)) {
      newSelection.delete(sessionId);
    } else {
      newSelection.add(sessionId);
    }
    setSelectedSessions(newSelection);
  };

  const selectAllFiltered = () => {
    const allFilteredIds = new Set(searchResults.map(r => r.session.id));
    setSelectedSessions(allFilteredIds);
  };

  const clearSelection = () => {
    setSelectedSessions(new Set());
  };

  const getAvailableTopics = (): string[] => {
    const allTopics = new Set<string>();
    sessions.forEach(session => {
      session.metadata.topics?.forEach(topic => allTopics.add(topic));
    });
    return Array.from(allTopics).sort();
  };

  return (
    <div className={`conversation-archive ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-neutral-200">
        <h2 className="heading-3 text-neutral-800 mb-4">
          {t('conversationArchive')}
        </h2>

        {/* Search Section */}
        <div className="space-y-4">
          <div className="relative">
            <input
              type="text"
              placeholder={t('searchConversations')}
              value={searchFilters.query}
              onChange={(e) => setSearchFilters(prev => ({ ...prev, query: e.target.value }))}
              className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-saffron-primary focus:border-transparent"
            />
            <span className="absolute left-3 top-2.5 text-neutral-400">🔍</span>
            {isSearching && (
              <div className="absolute right-3 top-2.5">
                <div className="animate-spin w-4 h-4 border-2 border-saffron-primary border-t-transparent rounded-full"></div>
              </div>
            )}
          </div>

          {/* Advanced Search Toggle */}
          <button
            onClick={() => setIsAdvancedSearch(!isAdvancedSearch)}
            className="text-sm text-saffron-primary hover:text-saffron-dark flex items-center gap-2"
          >
            <span>{isAdvancedSearch ? '▼' : '▶'}</span>
            {t('advancedSearch')}
          </button>

          {/* Advanced Search Filters */}
          {isAdvancedSearch && (
            <div className="bg-neutral-50 p-4 rounded-lg space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">
                    {t('language')}
                  </label>
                  <select
                    value={searchFilters.language}
                    onChange={(e) => setSearchFilters(prev => ({ 
                      ...prev, 
                      language: e.target.value as 'all' | 'en' | 'hi' 
                    }))}
                    className="w-full p-2 border border-neutral-300 rounded text-sm"
                  >
                    <option value="all">{t('allLanguages')}</option>
                    <option value="en">English</option>
                    <option value="hi">Hindi</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">
                    {t('dateRange')}
                  </label>
                  <select
                    value={searchFilters.dateRange}
                    onChange={(e) => setSearchFilters(prev => ({ 
                      ...prev, 
                      dateRange: e.target.value as any 
                    }))}
                    className="w-full p-2 border border-neutral-300 rounded text-sm"
                  >
                    <option value="all">{t('allTime')}</option>
                    <option value="today">{t('today')}</option>
                    <option value="week">{t('thisWeek')}</option>
                    <option value="month">{t('thisMonth')}</option>
                    <option value="year">{t('thisYear')}</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">
                  {t('minimumMessages')}
                </label>
                <input
                  type="range"
                  min="0"
                  max="50"
                  value={searchFilters.minMessages}
                  onChange={(e) => setSearchFilters(prev => ({ 
                    ...prev, 
                    minMessages: parseInt(e.target.value) 
                  }))}
                  className="w-full"
                />
                <div className="text-xs text-neutral-500 mt-1">
                  {searchFilters.minMessages} {t('messages')}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bulk Actions */}
      <div className="p-4 border-b border-neutral-200 bg-neutral-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-sm text-neutral-600">
              {searchResults.length} {t('conversationsFound')}
            </span>
            {selectedSessions.size > 0 && (
              <span className="text-sm font-medium text-saffron-primary">
                {selectedSessions.size} {t('selected')}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {searchResults.length > 0 && (
              <>
                <button
                  onClick={selectAllFiltered}
                  className="btn-secondary text-xs"
                  disabled={selectedSessions.size === searchResults.length}
                >
                  {t('selectAll')}
                </button>
                <button
                  onClick={clearSelection}
                  className="btn-secondary text-xs"
                  disabled={selectedSessions.size === 0}
                >
                  {t('clearSelection')}
                </button>
              </>
            )}
            
            {selectedSessions.size > 0 && (
              <>
                <select
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value as any)}
                  className="text-xs border border-neutral-300 rounded px-2 py-1"
                >
                  <option value="txt">TXT</option>
                  <option value="json">JSON</option>
                  <option value="csv">CSV</option>
                  <option value="markdown">Markdown</option>
                  <option value="pdf">PDF</option>
                </select>
                <button
                  onClick={handleBulkExport}
                  disabled={isExporting}
                  className="btn-primary text-xs"
                >
                  {isExporting ? t('exporting') + '...' : t('exportSelected')}
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto">
        {searchResults.length === 0 ? (
          <div className="p-8 text-center text-neutral-500">
            <div className="text-4xl mb-4">🔍</div>
            <p>{t('noSearchResults')}</p>
            <p className="text-sm mt-2">{t('tryDifferentSearch')}</p>
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {searchResults.map((result) => (
              <div
                key={result.session.id}
                className={`archive-item p-3 rounded-lg cursor-pointer transition-colors relative group ${
                  result.session.id === currentSessionId
                    ? 'bg-saffron-light border border-saffron-primary'
                    : selectedSessions.has(result.session.id)
                    ? 'bg-blue-50 border border-blue-200'
                    : 'hover:bg-neutral-100'
                }`}
              >
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={selectedSessions.has(result.session.id)}
                    onChange={() => toggleSessionSelection(result.session.id)}
                    className="mt-1"
                    onClick={(e) => e.stopPropagation()}
                  />
                  
                  <div 
                    className="flex-1 min-w-0"
                    onClick={() => onSessionSelect(result.session.id)}
                  >
                    <h3 
                      className="font-medium text-neutral-800 text-sm mb-1"
                      dangerouslySetInnerHTML={{ __html: result.highlightedTitle }}
                    />
                    
                    <div className="flex items-center gap-2 text-xs text-neutral-500 mb-2">
                      <span>{new Date(result.session.updatedAt).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{result.session.metadata.messageCount} {t('messages')}</span>
                      <span>•</span>
                      <span>{result.session.language === 'hi' ? '🇮🇳' : '🇬🇧'}</span>
                      {result.relevanceScore > 1 && (
                        <>
                          <span>•</span>
                          <span className="text-saffron-primary font-medium">
                            {result.relevanceScore.toFixed(1)} ⭐
                          </span>
                        </>
                      )}
                    </div>

                    {/* Matched Messages Preview */}
                    {result.matchedMessages.length > 0 && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded p-2 mt-2">
                        <div className="text-xs font-medium text-yellow-700 mb-1">
                          {result.matchedMessages.length} {t('matchingMessages')}:
                        </div>
                        {result.matchedMessages.slice(0, 2).map((message, index) => (
                          <div key={index} className="text-xs text-neutral-600 truncate">
                            <span className="font-medium">
                              {message.sender === 'user' ? t('you') : t('lordKrishna')}:
                            </span> 
                            {message.text.substring(0, 80)}...
                          </div>
                        ))}
                        {result.matchedMessages.length > 2 && (
                          <div className="text-xs text-yellow-600 mt-1">
                            +{result.matchedMessages.length - 2} {t('moreMatches')}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Topics */}
                    {result.session.metadata.topics && result.session.metadata.topics.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {result.session.metadata.topics.slice(0, 3).map((topic, index) => (
                          <span
                            key={index}
                            className="inline-block px-2 py-1 bg-neutral-200 text-neutral-600 text-xs rounded"
                          >
                            {topic}
                          </span>
                        ))}
                        {result.session.metadata.topics.length > 3 && (
                          <span className="text-xs text-neutral-500">
                            +{result.session.metadata.topics.length - 3}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversationArchive;
