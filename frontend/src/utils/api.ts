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
  language: 'en' | 'hi';
  sessionId?: string;
  context?: Array<{
    text: string;
    sender: 'user' | 'ai';
    timestamp: string;
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
  citations: Citation[];
  sanskritText?: string;
  transliteration?: string;
  confidence: number;
  sessionId: string;
  timestamp: string;
  processingTime: number;
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
      (config) => {
        // Add timestamp to all requests
        (config as any).metadata = { startTime: Date.now() };
        
        // Add authentication if available
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
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

  private getAuthToken(): string | null {
    // This will be integrated with MSAL when authentication is implemented
    return localStorage.getItem('vimarsh_auth_token');
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
   * Get spiritual guidance from Lord Krishna
   */
  async getSpiritualGuidance(request: SpiritualGuidanceRequest): Promise<SpiritualGuidanceResponse> {
    try {
      const response: AxiosResponse<SpiritualGuidanceResponse> = await this.client.post(
        '/api/spiritual-guidance',
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
      const response = await this.client.get('/api/health');
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
      const response = await this.client.post('/api/feedback/collect', feedback);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get conversation history (if user is authenticated)
   */
  async getConversationHistory(limit: number = 50): Promise<{
    conversations: Array<{
      sessionId: string;
      messages: Array<{
        text: string;
        sender: 'user' | 'ai';
        timestamp: string;
      }>;
      createdAt: string;
    }>;
  }> {
    try {
      // TODO: Implement conversations endpoint in backend
      // const response = await this.client.get(`/api/conversations?limit=${limit}`);
      // return response.data;
      return { conversations: [] }; // Temporary placeholder
    } catch (error) {
      throw error;
    }
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
