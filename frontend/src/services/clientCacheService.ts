/**
 * Client-Side Caching Service for Vimarsh Multi-Personality Platform
 * 
 * Provides intelligent caching for personality data, responses, and user preferences
 * with automatic cache warming and invalidation strategies.
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  accessCount: number;
  lastAccessed: number;
  personalityId?: string;
}

interface CacheMetrics {
  hits: number;
  misses: number;
  hitRate: number;
  totalSize: number;
  entryCount: number;
}

class ClientCacheService {
  private cache = new Map<string, CacheEntry<any>>();
  private metrics: CacheMetrics = {
    hits: 0,
    misses: 0,
    hitRate: 0,
    totalSize: 0,
    entryCount: 0
  };
  
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes
  private readonly MAX_CACHE_SIZE = 100; // Maximum number of entries
  private readonly CLEANUP_INTERVAL = 60 * 1000; // 1 minute
  
  private cleanupTimer?: NodeJS.Timeout;

  constructor() {
    this.startCleanupTimer();
    this.warmPopularData();
  }

  /**
   * Get data from cache
   */
  get<T>(key: string, personalityId?: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      this.metrics.misses++;
      this.updateHitRate();
      return null;
    }

    // Check if entry has expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      this.metrics.misses++;
      this.updateHitRate();
      return null;
    }

    // Update access statistics
    entry.accessCount++;
    entry.lastAccessed = Date.now();
    
    this.metrics.hits++;
    this.updateHitRate();
    
    return entry.data;
  }

  /**
   * Set data in cache
   */
  set<T>(
    key: string, 
    data: T, 
    ttl: number = this.DEFAULT_TTL,
    personalityId?: string
  ): void {
    // Remove oldest entries if cache is full
    if (this.cache.size >= this.MAX_CACHE_SIZE) {
      this.evictLeastRecentlyUsed();
    }

    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl,
      accessCount: 0,
      lastAccessed: Date.now(),
      personalityId
    };

    this.cache.set(key, entry);
    this.updateMetrics();
  }

  /**
   * Remove specific key from cache
   */
  delete(key: string): boolean {
    const deleted = this.cache.delete(key);
    if (deleted) {
      this.updateMetrics();
    }
    return deleted;
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear();
    this.updateMetrics();
  }

  /**
   * Clear cache entries for specific personality
   */
  clearPersonality(personalityId: string): void {
    const keysToDelete: string[] = [];
    
    for (const [key, entry] of this.cache.entries()) {
      if (entry.personalityId === personalityId) {
        keysToDelete.push(key);
      }
    }
    
    keysToDelete.forEach(key => this.cache.delete(key));
    this.updateMetrics();
  }

  /**
   * Get cache metrics
   */
  getMetrics(): CacheMetrics {
    return { ...this.metrics };
  }

  /**
   * Get cache statistics by personality
   */
  getPersonalityStats(): Record<string, { entries: number; size: number }> {
    const stats: Record<string, { entries: number; size: number }> = {};
    
    for (const [key, entry] of this.cache.entries()) {
      if (entry.personalityId) {
        if (!stats[entry.personalityId]) {
          stats[entry.personalityId] = { entries: 0, size: 0 };
        }
        stats[entry.personalityId].entries++;
        stats[entry.personalityId].size += this.estimateSize(entry.data);
      }
    }
    
    return stats;
  }

  /**
   * Warm cache with popular data
   */
  private async warmPopularData(): Promise<void> {
    try {
      // Warm personality data
      const popularPersonalities = ['krishna', 'einstein', 'lincoln', 'marcus_aurelius'];
      
      for (const personalityId of popularPersonalities) {
        // Cache personality profile
        const personalityKey = `personality:${personalityId}`;
        if (!this.get(personalityKey)) {
          // In a real implementation, this would fetch from API
          const mockPersonalityData = {
            id: personalityId,
            name: personalityId.charAt(0).toUpperCase() + personalityId.slice(1),
            domain: this.getDomainForPersonality(personalityId),
            voice_settings: this.getDefaultVoiceSettings(personalityId)
          };
          
          this.set(personalityKey, mockPersonalityData, 30 * 60 * 1000, personalityId); // 30 minutes
        }
      }
      
      // Warm common responses
      await this.warmCommonResponses();
      
    } catch (error) {
      console.warn('Cache warming failed:', error);
    }
  }

  /**
   * Warm common responses
   */
  private async warmCommonResponses(): Promise<void> {
    const commonQueries = [
      'What is the meaning of life?',
      'How can I find happiness?',
      'What is wisdom?',
      'How should I live?'
    ];

    for (const query of commonQueries) {
      const queryKey = `response:${this.hashQuery(query)}`;
      if (!this.get(queryKey)) {
        // Mock response - in real implementation, this would be fetched
        const mockResponse = {
          text: `This is a response to: ${query}`,
          citations: [],
          timestamp: Date.now()
        };
        
        this.set(queryKey, mockResponse, 15 * 60 * 1000); // 15 minutes
      }
    }
  }

  /**
   * Cache personality-specific response
   */
  cacheResponse(
    query: string,
    response: any,
    personalityId: string,
    ttl: number = 15 * 60 * 1000 // 15 minutes
  ): void {
    const key = `response:${personalityId}:${this.hashQuery(query)}`;
    this.set(key, response, ttl, personalityId);
  }

  /**
   * Get cached response
   */
  getCachedResponse(query: string, personalityId: string): any | null {
    const key = `response:${personalityId}:${this.hashQuery(query)}`;
    return this.get(key, personalityId);
  }

  /**
   * Cache user preferences
   */
  cacheUserPreferences(userId: string, preferences: any): void {
    const key = `preferences:${userId}`;
    this.set(key, preferences, 60 * 60 * 1000); // 1 hour
  }

  /**
   * Get cached user preferences
   */
  getCachedUserPreferences(userId: string): any | null {
    const key = `preferences:${userId}`;
    return this.get(key);
  }

  /**
   * Cache conversation history
   */
  cacheConversation(conversationId: string, messages: any[], personalityId: string): void {
    const key = `conversation:${conversationId}`;
    this.set(key, messages, 30 * 60 * 1000, personalityId); // 30 minutes
  }

  /**
   * Get cached conversation
   */
  getCachedConversation(conversationId: string): any[] | null {
    const key = `conversation:${conversationId}`;
    return this.get(key);
  }

  /**
   * Preload data for personality switching
   */
  async preloadPersonality(personalityId: string): Promise<void> {
    try {
      // Preload personality data
      const personalityKey = `personality:${personalityId}`;
      if (!this.get(personalityKey)) {
        // Mock data - in real implementation, fetch from API
        const personalityData = {
          id: personalityId,
          name: personalityId.charAt(0).toUpperCase() + personalityId.slice(1),
          domain: this.getDomainForPersonality(personalityId),
          voice_settings: this.getDefaultVoiceSettings(personalityId)
        };
        
        this.set(personalityKey, personalityData, 30 * 60 * 1000, personalityId);
      }

      // Preload common responses for this personality
      const commonQueries = [
        'Hello',
        'What is your philosophy?',
        'Can you help me?'
      ];

      for (const query of commonQueries) {
        const responseKey = `response:${personalityId}:${this.hashQuery(query)}`;
        if (!this.get(responseKey)) {
          // Mock response
          const response = {
            text: `${personalityId} response to: ${query}`,
            personalityId,
            timestamp: Date.now()
          };
          
          this.set(responseKey, response, 15 * 60 * 1000, personalityId);
        }
      }
      
    } catch (error) {
      console.warn(`Failed to preload personality ${personalityId}:`, error);
    }
  }

  /**
   * Optimize cache performance
   */
  optimize(): { cleaned: number; memoryFreed: number } {
    let cleaned = 0;
    let memoryFreed = 0;
    
    const now = Date.now();
    const keysToDelete: string[] = [];
    
    // Remove expired entries
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        keysToDelete.push(key);
        memoryFreed += this.estimateSize(entry.data);
        cleaned++;
      }
    }
    
    keysToDelete.forEach(key => this.cache.delete(key));
    
    // If still over capacity, remove least recently used
    if (this.cache.size > this.MAX_CACHE_SIZE * 0.8) {
      const additionalCleaned = this.evictLeastRecentlyUsed(this.cache.size - Math.floor(this.MAX_CACHE_SIZE * 0.7));
      cleaned += additionalCleaned;
    }
    
    this.updateMetrics();
    
    return { cleaned, memoryFreed };
  }

  /**
   * Private helper methods
   */
  private evictLeastRecentlyUsed(count: number = 1): number {
    const entries = Array.from(this.cache.entries())
      .sort(([, a], [, b]) => a.lastAccessed - b.lastAccessed);
    
    let evicted = 0;
    for (let i = 0; i < Math.min(count, entries.length); i++) {
      this.cache.delete(entries[i][0]);
      evicted++;
    }
    
    return evicted;
  }

  private updateMetrics(): void {
    this.metrics.entryCount = this.cache.size;
    this.metrics.totalSize = Array.from(this.cache.values())
      .reduce((total, entry) => total + this.estimateSize(entry.data), 0);
    this.updateHitRate();
  }

  private updateHitRate(): void {
    const total = this.metrics.hits + this.metrics.misses;
    this.metrics.hitRate = total > 0 ? (this.metrics.hits / total) * 100 : 0;
  }

  private estimateSize(data: any): number {
    try {
      return JSON.stringify(data).length * 2; // Rough estimate in bytes
    } catch {
      return 1000; // Default estimate
    }
  }

  private hashQuery(query: string): string {
    // Simple hash function for query keys
    let hash = 0;
    for (let i = 0; i < query.length; i++) {
      const char = query.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36);
  }

  private getDomainForPersonality(personalityId: string): string {
    const domains: Record<string, string> = {
      'krishna': 'spiritual',
      'einstein': 'scientific',
      'lincoln': 'historical',
      'marcus_aurelius': 'philosophical'
    };
    return domains[personalityId] || 'general';
  }

  private getDefaultVoiceSettings(personalityId: string): any {
    const voiceSettings: Record<string, any> = {
      'krishna': {
        speaking_rate: 0.75,
        pitch: -1.5,
        volume: 0.9,
        voice_characteristics: { gender: 'male', age: 'middle', tone: 'reverent' }
      },
      'einstein': {
        speaking_rate: 0.85,
        pitch: 0.0,
        volume: 0.9,
        voice_characteristics: { gender: 'male', age: 'elderly', tone: 'scholarly' }
      },
      'lincoln': {
        speaking_rate: 0.8,
        pitch: -0.5,
        volume: 0.95,
        voice_characteristics: { gender: 'male', age: 'middle', tone: 'authoritative' }
      },
      'marcus_aurelius': {
        speaking_rate: 0.7,
        pitch: -1.0,
        volume: 0.85,
        voice_characteristics: { gender: 'male', age: 'middle', tone: 'contemplative' }
      }
    };
    return voiceSettings[personalityId] || voiceSettings['krishna'];
  }

  private startCleanupTimer(): void {
    this.cleanupTimer = setInterval(() => {
      this.optimize();
    }, this.CLEANUP_INTERVAL);
  }

  /**
   * Cleanup resources
   */
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
    }
    this.clear();
  }
}

// Export singleton instance
export const clientCacheService = new ClientCacheService();
export default clientCacheService;