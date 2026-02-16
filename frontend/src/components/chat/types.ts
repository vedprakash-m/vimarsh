/**
 * Shared types for chat components
 */

export interface MessageMetadata {
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
}

export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  personality?: string;
  metadata?: MessageMetadata;
}
