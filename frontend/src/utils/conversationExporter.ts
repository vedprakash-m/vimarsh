import { ConversationSession, conversationHistory } from './conversationHistory';
import { Message } from '../hooks/useSpiritualChat';

export interface ExportOptions {
  format: 'txt' | 'json' | 'csv' | 'markdown' | 'pdf';
  includeMetadata: boolean;
  includeCitations: boolean;
  includeSanskrit: boolean;
  dateRange?: {
    start: Date;
    end: Date;
  };
  language?: 'en' | 'hi' | 'all';
}

export interface ExportProgress {
  current: number;
  total: number;
  status: string;
}

class ConversationExporter {
  
  /**
   * Export multiple sessions with progress tracking
   */
  async exportSessions(
    sessionIds: string[], 
    options: ExportOptions,
    onProgress?: (progress: ExportProgress) => void
  ): Promise<string> {
    const sessions = sessionIds
      .map(id => conversationHistory.getSession(id))
      .filter(Boolean) as ConversationSession[];

    if (sessions.length === 0) {
      throw new Error('No valid sessions found for export');
    }

    // Filter by options
    const filteredSessions = this.filterSessions(sessions, options);
    
    onProgress?.({ current: 0, total: filteredSessions.length, status: 'Starting export...' });

    switch (options.format) {
      case 'json':
        return this.exportAsJSON(filteredSessions, options, onProgress);
      case 'csv':
        return this.exportAsCSV(filteredSessions, options, onProgress);
      case 'markdown':
        return this.exportAsMarkdown(filteredSessions, options, onProgress);
      case 'pdf':
        return this.exportAsPDF(filteredSessions, options, onProgress);
      case 'txt':
      default:
        return this.exportAsText(filteredSessions, options, onProgress);
    }
  }

  /**
   * Export all conversations
   */
  async exportAllConversations(
    options: ExportOptions,
    onProgress?: (progress: ExportProgress) => void
  ): Promise<string> {
    const allSessions = conversationHistory.getSessions();
    const sessionIds = allSessions.map(s => s.id);
    return this.exportSessions(sessionIds, options, onProgress);
  }

  /**
   * Export conversation statistics
   */
  generateStatistics(sessions: ConversationSession[]): any {
    const stats = {
      totalSessions: sessions.length,
      totalMessages: 0,
      userMessages: 0,
      aiMessages: 0,
      languages: { en: 0, hi: 0 },
      dateRange: {
        earliest: null as Date | null,
        latest: null as Date | null
      },
      averageSessionLength: 0,
      topTopics: [] as { topic: string; count: number }[],
      totalCitations: 0,
      citationSources: new Set<string>(),
      averageResponseTime: 0,
      sessionDurations: [] as number[]
    };

    const topicCounts = new Map<string, number>();

    sessions.forEach(session => {
      stats.totalMessages += session.metadata.messageCount;
      stats.languages[session.language]++;
      
      if (!stats.dateRange.earliest || session.createdAt < stats.dateRange.earliest) {
        stats.dateRange.earliest = session.createdAt;
      }
      if (!stats.dateRange.latest || session.updatedAt > stats.dateRange.latest) {
        stats.dateRange.latest = session.updatedAt;
      }

      if (session.metadata.duration) {
        stats.sessionDurations.push(session.metadata.duration);
      }

      session.messages.forEach(message => {
        if (message.sender === 'user') {
          stats.userMessages++;
        } else {
          stats.aiMessages++;
          if (message.citations) {
            stats.totalCitations += message.citations.length;
            message.citations.forEach(citation => {
              stats.citationSources.add(citation.source);
            });
          }
        }
      });

      // Count topics
      session.metadata.topics?.forEach(topic => {
        topicCounts.set(topic, (topicCounts.get(topic) || 0) + 1);
      });
    });

    stats.averageSessionLength = stats.totalMessages / stats.totalSessions;
    stats.topTopics = Array.from(topicCounts.entries())
      .map(([topic, count]) => ({ topic, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    if (stats.sessionDurations.length > 0) {
      const avgDuration = stats.sessionDurations.reduce((a, b) => a + b, 0) / stats.sessionDurations.length;
      stats.averageResponseTime = avgDuration;
    }

    return stats;
  }

  private filterSessions(sessions: ConversationSession[], options: ExportOptions): ConversationSession[] {
    return sessions.filter(session => {
      // Language filter
      if (options.language && options.language !== 'all' && session.language !== options.language) {
        return false;
      }

      // Date range filter
      if (options.dateRange) {
        const sessionDate = new Date(session.updatedAt);
        if (sessionDate < options.dateRange.start || sessionDate > options.dateRange.end) {
          return false;
        }
      }

      return true;
    });
  }

  private async exportAsJSON(
    sessions: ConversationSession[], 
    options: ExportOptions,
    onProgress?: (progress: ExportProgress) => void
  ): Promise<string> {
    onProgress?.({ current: 0, total: sessions.length, status: 'Preparing JSON export...' });

    const exportData = {
      metadata: {
        exportDate: new Date().toISOString(),
        vimarshVersion: '1.0',
        exportOptions: options,
        statistics: options.includeMetadata ? this.generateStatistics(sessions) : undefined
      },
      sessions: sessions.map((session, index) => {
        onProgress?.({ 
          current: index + 1, 
          total: sessions.length, 
          status: `Processing session: ${session.title}` 
        });

        return {
          id: session.id,
          title: session.title,
          language: session.language,
          createdAt: session.createdAt.toISOString(),
          updatedAt: session.updatedAt.toISOString(),
          metadata: options.includeMetadata ? session.metadata : undefined,
          messages: session.messages.map(message => ({
            id: message.id,
            text: message.text,
            sender: message.sender,
            timestamp: message.timestamp.toISOString(),
            sanskritText: options.includeSanskrit ? message.sanskritText : undefined,
            transliteration: options.includeSanskrit ? message.transliteration : undefined,
            citations: options.includeCitations ? message.citations : undefined,
            confidence: message.confidence
          })).filter(msg => msg.text) // Remove empty messages
        };
      })
    };

    return JSON.stringify(exportData, null, 2);
  }

  private async exportAsText(
    sessions: ConversationSession[], 
    options: ExportOptions,
    onProgress?: (progress: ExportProgress) => void
  ): Promise<string> {
    let content = `# Vimarsh Spiritual Guidance Export\n\n`;
    content += `Export Date: ${new Date().toLocaleString()}\n`;
    content += `Total Sessions: ${sessions.length}\n`;
    content += `Export Format: Plain Text\n\n`;

    if (options.includeMetadata) {
      const stats = this.generateStatistics(sessions);
      content += `## Statistics\n`;
      content += `- Total Messages: ${stats.totalMessages}\n`;
      content += `- User Messages: ${stats.userMessages}\n`;
      content += `- AI Responses: ${stats.aiMessages}\n`;
      content += `- Languages: English (${stats.languages.en}), Hindi (${stats.languages.hi})\n`;
      content += `- Average Session Length: ${stats.averageSessionLength.toFixed(1)} messages\n`;
      content += `- Total Citations: ${stats.totalCitations}\n\n`;
    }

    content += '='.repeat(80) + '\n\n';

    for (let i = 0; i < sessions.length; i++) {
      const session = sessions[i];
      onProgress?.({ 
        current: i + 1, 
        total: sessions.length, 
        status: `Exporting: ${session.title}` 
      });

      content += `## Session ${i + 1}: ${session.title}\n\n`;
      content += `**Created:** ${new Date(session.createdAt).toLocaleString()}\n`;
      content += `**Updated:** ${new Date(session.updatedAt).toLocaleString()}\n`;
      content += `**Language:** ${session.language === 'hi' ? 'Hindi (हिंदी)' : 'English'}\n`;
      content += `**Messages:** ${session.metadata.messageCount}\n\n`;

      if (options.includeMetadata && session.metadata.topics && session.metadata.topics.length > 0) {
        content += `**Topics:** ${session.metadata.topics.join(', ')}\n\n`;
      }

      content += '### Conversation\n\n';

      session.messages.forEach((message, msgIndex) => {
        const timestamp = new Date(message.timestamp).toLocaleString();
        const sender = message.sender === 'user' ? '**You**' : '**Lord Krishna**';
        
        content += `${sender} (${timestamp}):\n`;
        content += `${message.text}\n\n`;
        
        if (options.includeSanskrit && message.sanskritText) {
          content += `*Sanskrit:* ${message.sanskritText}\n\n`;
        }
        
        if (options.includeCitations && message.citations && message.citations.length > 0) {
          content += `*Sources:*\n`;
          message.citations.forEach(citation => {
            content += `- ${citation.source} ${citation.reference}\n`;
          });
          content += '\n';
        }
        
        content += '---\n\n';
      });

      content += '='.repeat(80) + '\n\n';
    }

    return content;
  }

  private async exportAsMarkdown(
    sessions: ConversationSession[], 
    options: ExportOptions,
    onProgress?: (progress: ExportProgress) => void
  ): Promise<string> {
    let content = `# 🕉️ Vimarsh Spiritual Guidance Export\n\n`;
    content += `**Export Date:** ${new Date().toLocaleString()}  \n`;
    content += `**Total Sessions:** ${sessions.length}  \n`;
    content += `**Format:** Markdown\n\n`;

    if (options.includeMetadata) {
      const stats = this.generateStatistics(sessions);
      content += `## 📊 Statistics\n\n`;
      content += `| Metric | Value |\n`;
      content += `|--------|-------|\n`;
      content += `| Total Messages | ${stats.totalMessages} |\n`;
      content += `| User Messages | ${stats.userMessages} |\n`;
      content += `| AI Responses | ${stats.aiMessages} |\n`;
      content += `| English Sessions | ${stats.languages.en} |\n`;
      content += `| Hindi Sessions | ${stats.languages.hi} |\n`;
      content += `| Average Session Length | ${stats.averageSessionLength.toFixed(1)} messages |\n`;
      content += `| Total Citations | ${stats.totalCitations} |\n`;
      content += `| Unique Sources | ${stats.citationSources.size} |\n\n`;

      if (stats.topTopics.length > 0) {
        content += `### 🏷️ Top Discussion Topics\n\n`;
        stats.topTopics.forEach((topic: { topic: string; count: number }, index: number) => {
          content += `${index + 1}. **${topic.topic}** (${topic.count} sessions)\n`;
        });
        content += '\n';
      }
    }

    content += `---\n\n`;

    for (let i = 0; i < sessions.length; i++) {
      const session = sessions[i];
      onProgress?.({ 
        current: i + 1, 
        total: sessions.length, 
        status: `Converting to Markdown: ${session.title}` 
      });

      const flag = session.language === 'hi' ? '🇮🇳' : '🇺🇸';
      content += `## ${flag} Session ${i + 1}: ${session.title}\n\n`;
      
      content += `> **Created:** ${new Date(session.createdAt).toLocaleString()}  \n`;
      content += `> **Updated:** ${new Date(session.updatedAt).toLocaleString()}  \n`;
      content += `> **Language:** ${session.language === 'hi' ? 'Hindi (हिंदी)' : 'English'}  \n`;
      content += `> **Messages:** ${session.metadata.messageCount}\n\n`;

      if (options.includeMetadata && session.metadata.topics && session.metadata.topics.length > 0) {
        content += `**Topics:** `;
        content += session.metadata.topics.map(topic => `\`${topic}\``).join(', ');
        content += '\n\n';
      }

      session.messages.forEach((message, msgIndex) => {
        const timestamp = new Date(message.timestamp).toLocaleString();
        
        if (message.sender === 'user') {
          content += `### 👤 You *(${timestamp})*\n\n`;
          content += `${message.text}\n\n`;
        } else {
          content += `### 🕉️ Lord Krishna *(${timestamp})*\n\n`;
          content += `${message.text}\n\n`;
          
          if (options.includeSanskrit && message.sanskritText) {
            content += `> **Sanskrit:** ${message.sanskritText}\n\n`;
          }
          
          if (options.includeCitations && message.citations && message.citations.length > 0) {
            content += `**📚 Sources:**\n`;
            message.citations.forEach(citation => {
              content += `- [${citation.source} ${citation.reference}]\n`;
            });
            content += '\n';
          }
        }
      });

      content += `---\n\n`;
    }

    return content;
  }

  private async exportAsCSV(
    sessions: ConversationSession[], 
    options: ExportOptions,
    onProgress?: (progress: ExportProgress) => void
  ): Promise<string> {
    onProgress?.({ current: 0, total: sessions.length, status: 'Generating CSV headers...' });

    // CSV Headers
    let headers = [
      'Session ID',
      'Session Title',
      'Language',
      'Created Date',
      'Updated Date',
      'Message Index',
      'Sender',
      'Message Text',
      'Timestamp'
    ];

    if (options.includeSanskrit) {
      headers.push('Sanskrit Text', 'Transliteration');
    }

    if (options.includeCitations) {
      headers.push('Citations');
    }

    if (options.includeMetadata) {
      headers.push('Session Topics', 'Message Count');
    }

    let csvContent = headers.join(',') + '\n';

    // Data rows
    for (let i = 0; i < sessions.length; i++) {
      const session = sessions[i];
      onProgress?.({ 
        current: i + 1, 
        total: sessions.length, 
        status: `Processing CSV data: ${session.title}` 
      });

      session.messages.forEach((message, msgIndex) => {
        let row = [
          this.escapeCsvValue(session.id),
          this.escapeCsvValue(session.title),
          session.language,
          session.createdAt.toISOString(),
          session.updatedAt.toISOString(),
          msgIndex.toString(),
          message.sender,
          this.escapeCsvValue(message.text),
          message.timestamp.toISOString()
        ];

        if (options.includeSanskrit) {
          row.push(
            this.escapeCsvValue(message.sanskritText || ''),
            this.escapeCsvValue(message.transliteration || '')
          );
        }

        if (options.includeCitations) {
          const citations = message.citations 
            ? message.citations.map(c => `${c.source} ${c.reference}`).join('; ')
            : '';
          row.push(this.escapeCsvValue(citations));
        }

        if (options.includeMetadata) {
          row.push(
            this.escapeCsvValue(session.metadata.topics?.join('; ') || ''),
            session.metadata.messageCount.toString()
          );
        }

        csvContent += row.join(',') + '\n';
      });
    }

    return csvContent;
  }

  private async exportAsPDF(
    sessions: ConversationSession[], 
    options: ExportOptions,
    onProgress?: (progress: ExportProgress) => void
  ): Promise<string> {
    // For now, return a placeholder. PDF generation would require a library like jsPDF
    onProgress?.({ current: sessions.length, total: sessions.length, status: 'PDF export not yet implemented' });
    
    throw new Error('PDF export is not yet implemented. Please use Text or Markdown format for now.');
  }

  private escapeCsvValue(value: string): string {
    if (value.includes(',') || value.includes('"') || value.includes('\n')) {
      return `"${value.replace(/"/g, '""')}"`;
    }
    return value;
  }
}

export const conversationExporter = new ConversationExporter();
export default ConversationExporter;
