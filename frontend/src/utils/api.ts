import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { getApiBaseUrl } from '../config/environment';

interface ApiConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  retryDelay: number;
}

interface SpiritualGuidanceRequest {
  query: string;
  language?: string;  // Default: 'English'
  personality_id?: string;  // Default: 'krishna'
  user_id?: string;
  session_id?: string;
  include_citations?: boolean;
  voice_enabled?: boolean;
  conversation_context?: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
}

interface Citation {
  source: string;
  reference: string;
  verse?: string;
  chapter?: string;
  book?: string;
}

interface SpiritualGuidanceResponse {
  response: string;
  citations?: Citation[];
  sanskritText?: string;
  transliteration?: string;
  confidence?: number;
  sessionId?: string;
  timestamp?: string;
  processingTime?: number;
  achievements_unlocked?: Array<{
    id: string;
    name: string;
    description?: string;
    icon?: string;
  }>;
  metadata?: {
    response_source?: 'gemini_ai' | 'template_fallback' | 'hardcoded_fallback' | 'hybrid_rag' | 'simple_rag';
    ai_generated?: boolean;
    service_mode?: 'enhanced' | 'standard' | 'fallback';
    fallback_reason?: string;
    circuit_breaker_status?: {
      state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
      failure_count: number;
      last_failure_time?: string;
    };
    reliability_stats?: {
      success_rate: number;
      total_attempts: number;
      template_fallback_count: number;
    };
    generation_time_ms?: number;
    memory_enhanced?: boolean;
  };
}

interface ApiError {
  message: string;
  code: string;
  statusCode: number;
  timestamp: string;
}

const DEFAULT_CONFIG: ApiConfig = {
  baseURL: getApiBaseUrl(),
  timeout: 30000, // 30 seconds
  retries: 3,
  retryDelay: 1000 // 1 second
};

class SpiritualGuidanceAPI {
  private client: AxiosInstance;
  private config: ApiConfig;

  constructor(config: Partial<ApiConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.client = this.createAxiosInstance();
  }

  private createAxiosInstance(): AxiosInstance {
    const instance = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });

    // Request interceptor for authentication and logging
    instance.interceptors.request.use(
      async (config) => {
        // Add timestamp to all requests
        (config as any).metadata = { startTime: Date.now() };
        
        // Add authentication if available
        try {
          const token = await this.getAuthToken();
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        } catch (error) {
          console.warn('Failed to add auth token to request:', error);
        }

        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling and logging
    instance.interceptors.response.use(
      (response) => {
        const duration = Date.now() - ((response.config as any).metadata?.startTime || 0);
        console.log(`✅ API Response: ${response.config.url} (${duration}ms)`);
        return response;
      },
      async (error) => {
        const originalRequest = error.config;
        
        // Log error
        console.error(`❌ API Error: ${error.config?.url}`, error.response?.status, error.message);

        // Retry logic for network errors
        if (this.shouldRetry(error) && originalRequest && !originalRequest._retry) {
          originalRequest._retry = true;
          originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;

          if (originalRequest._retryCount <= this.config.retries) {
            const delay = this.config.retryDelay * originalRequest._retryCount;
            console.log(`🔄 Retrying request in ${delay}ms (attempt ${originalRequest._retryCount}/${this.config.retries})`);
            
            await this.delay(delay);
            return instance(originalRequest);
          }
        }

        return Promise.reject(this.formatError(error));
      }
    );

    return instance;
  }

  private shouldRetry(error: any): boolean {
    // Retry on network errors, timeout, or server errors
    return (
      !error.response || // Network error
      error.code === 'ECONNABORTED' || // Timeout
      (error.response.status >= 500 && error.response.status <= 599) // Server errors
    );
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async getAuthToken(): Promise<string | null> {
    // Get token from the auth service instead of localStorage
    try {
      const { authService } = await import('../auth/authService');
      return await authService.getToken();
    } catch (error) {
      console.warn('Failed to get auth token:', error);
      return null;
    }
  }

  private formatError(error: any): ApiError {
    const timestamp = new Date().toISOString();
    
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data?.message || error.response.statusText || 'An error occurred',
        code: error.response.data?.code || 'HTTP_ERROR',
        statusCode: error.response.status,
        timestamp
      };
    } else if (error.request) {
      // Network error
      return {
        message: 'Network error. Please check your connection and try again.',
        code: 'NETWORK_ERROR',
        statusCode: 0,
        timestamp
      };
    } else {
      // Something else
      return {
        message: error.message || 'An unexpected error occurred',
        code: 'UNKNOWN_ERROR',
        statusCode: 0,
        timestamp
      };
    }
  }

  /**
   * Get spiritual guidance from any personality with streaming (SSE)
   */
  async getSpiritualGuidanceStream(
    request: SpiritualGuidanceRequest, 
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: SpiritualGuidanceResponse) => void,
    onError: (error: any) => void
  ): Promise<void> {
    try {
      const token = await this.getAuthToken();
      const response = await fetch(`${this.config.baseURL}/guidance?stream=true`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Stream error: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = '';
      let metadata: any = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            
            try {
              const parsed = JSON.parse(data);
              if (parsed.chunk) {
                fullText += parsed.chunk;
                onChunk(parsed.chunk);
              }
              if (parsed.metadata) {
                metadata = parsed.metadata;
              }
              if (parsed.full_response) {
                onComplete(parsed.full_response);
                return;
              }
            } catch (e) {
              // Partial JSON or heartbeat
            }
          }
        }
      }

      // If we finished the stream but didn't get full_response object
      onComplete({
        response: fullText,
        metadata: metadata || {}
      } as SpiritualGuidanceResponse);

    } catch (error) {
      console.error('❌ Stream Error:', error);
      onError(error);
    }
  }

  /**
   * Get spiritual guidance from any personality
   */
  async getSpiritualGuidance(request: SpiritualGuidanceRequest): Promise<SpiritualGuidanceResponse> {
    try {
      const response: AxiosResponse<SpiritualGuidanceResponse> = await this.client.post(
        '/guidance',
        request
      );

      return response.data;
    } catch (error) {
      throw error; // Will be formatted by interceptor
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Submit user feedback
   */
  async submitFeedback(feedback: {
    messageId: string;
    rating: 'helpful' | 'not_helpful';
    comment?: string;
    sessionId: string;
  }): Promise<{ success: boolean }> {
    try {
      const response = await this.client.post('/feedback/collect', feedback);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get conversation history (if user is authenticated)
   */
  async getConversationHistory(limit: number = 50, personalityId?: string): Promise<{
    conversations: Array<{
      sessionId: string;
      personalityId: string;
      messages: Array<{
        text: string;
        sender: 'user' | 'ai';
        timestamp: string;
      }>;
      summary: string;
      keyTopics: string[];
      emotionalJourney: string[];
      createdAt: string;
      endedAt: string;
      turnCount: number;
    }>;
  }> {
    try {
      const params = new URLSearchParams({ limit: limit.toString() });
      if (personalityId) {
        params.append('personality_id', personalityId);
      }
      const response = await this.client.get(`/conversations?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get conversation history:', error);
      return { conversations: [] };
    }
  }

  /**
   * Get user profile with preferences
   */
  async getUserProfile(): Promise<{
    user_id: string;
    email: string;
    name: string;
    preferences: {
      experience_preferences?: Record<string, unknown>;
      notification_preferences?: Record<string, unknown>;
      memory_preferences?: Record<string, unknown>;
    };
    journey_stats?: Record<string, unknown>;
    ai_usage?: Record<string, unknown>;
    member_since?: string;
    last_updated?: string;
  }> {
    const response = await this.client.get('/user/profile');
    return response.data;
  }

  /**
   * Update user preferences
   */
  async updatePreferences(preferences: Record<string, unknown>): Promise<{
    success: boolean;
    preferences: Record<string, unknown>;
    message?: string;
  }> {
    const response = await this.client.patch('/user/preferences', preferences);
    return response.data;
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<ApiConfig>): void {
    this.config = { ...this.config, ...newConfig };
    this.client = this.createAxiosInstance();
  }

  /**
   * Get current configuration
   */
  getConfig(): ApiConfig {
    return { ...this.config };
  }
}

// Create singleton instance
const spiritualGuidanceAPI = new SpiritualGuidanceAPI();

// Export both the class and singleton instance
export default spiritualGuidanceAPI;
export { SpiritualGuidanceAPI };
export type {
  SpiritualGuidanceRequest,
  SpiritualGuidanceResponse,
  Citation,
  ApiError,
  ApiConfig
};
