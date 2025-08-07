"""
Enhanced Database Models for Comprehensive Admin Analytics
Supports detailed user tracking, content management, and abuse prevention
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# ============================================================================
# USER ANALYTICS & BEHAVIOR TRACKING
# ============================================================================

@dataclass
class UserProfile:
    """Master user profile with comprehensive tracking"""
    # Primary identifiers
    email: str                              # PRIMARY KEY
    user_id: str                           # Generated UUID for internal use
    
    # Authentication details
    auth_provider: str                     # "microsoft", "google", "anonymous"
    tenant_id: Optional[str] = None
    first_login: str = None                # ISO timestamp of very first login
    
    # Personal information
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    preferred_language: str = "en"
    timezone: Optional[str] = None
    
    # Account management
    account_status: str = "active"         # "active", "suspended", "deleted"
    subscription_tier: str = "free"        # "free", "premium", "enterprise"
    created_at: str = None
    last_login: str = None
    
    # Usage statistics (aggregated)
    total_sessions: int = 0
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_session_duration_minutes: float = 0.0
    
    # Behavioral patterns
    favorite_personalities: List[str] = field(default_factory=list)
    common_topics: List[str] = field(default_factory=list)
    usage_patterns: Dict[str, Any] = field(default_factory=dict)  # Peak hours, frequency
    
    # Risk management
    risk_score: float = 0.0               # 0-1 scale for abuse detection
    is_blocked: bool = False
    block_reason: Optional[str] = None
    abuse_flags: List[str] = field(default_factory=list)
    
    # Admin tracking
    is_admin: bool = False
    admin_notes: Optional[str] = None
    
    # Compliance
    data_retention_consent: bool = True
    analytics_consent: bool = True
    last_consent_update: str = None
    
    type: str = "user_profile"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.last_consent_update is None:
            self.last_consent_update = self.created_at

@dataclass
class UserSession:
    """Individual user session tracking"""
    # Session identifiers
    session_id: str                        # PRIMARY KEY
    email: str                            # Foreign key to UserProfile
    user_id: str
    
    # Session details
    start_time: str
    end_time: Optional[str] = None
    duration_minutes: float = 0.0
    
    # Session metrics
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    
    # Technical details
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None      # "desktop", "mobile", "tablet"
    browser: Optional[str] = None
    
    # Session patterns
    personalities_used: List[str] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    
    type: str = "user_session"

@dataclass 
class UserInteraction:
    """Individual request/response interaction with comprehensive analytics"""
    # Interaction identifiers
    interaction_id: str                    # PRIMARY KEY
    email: str                            # Foreign key to UserProfile
    user_id: str
    session_id: str                       # Foreign key to UserSession
    sequence_number: int                  # Order within session
    
    # Request details
    timestamp: str
    user_query: str
    personality_used: str
    
    # Response details
    response_text: str
    
    # Performance metrics (required fields)
    total_response_time_ms: int
    rag_search_time_ms: int
    llm_generation_time_ms: int
    
    # Token economics (required fields)
    model_used: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    
    # Optional metrics with defaults
    response_quality_score: float = 0.0   # 0-1 quality assessment
    
    # RAG Analytics (DETAILED)
    rag_query_rewritten: Optional[str] = None
    rag_chunks_retrieved: List[Dict[str, Any]] = field(default_factory=list)
    rag_sources_used: List[str] = field(default_factory=list)
    rag_relevance_scores: List[float] = field(default_factory=list)
    rag_chunk_count: int = 0
    vector_search_similarity_threshold: float = 0.0
    
    # Content analysis
    content_themes: List[str] = field(default_factory=list)
    extracted_keywords: List[str] = field(default_factory=list)
    sentiment_score: float = 0.0          # -1 to 1
    
    # User feedback
    user_rating: Optional[int] = None      # 1-5 stars
    was_bookmarked: bool = False
    feedback_text: Optional[str] = None
    
    # Quality flags
    required_fallback: bool = False
    content_flagged: bool = False
    flag_reasons: List[str] = field(default_factory=list)
    
    type: str = "user_interaction"

# ============================================================================
# CONTENT MANAGEMENT & PERSONALITY TRACKING
# ============================================================================

@dataclass
class PersonalityConfig:
    """Comprehensive personality configuration and analytics"""
    # Core identity
    personality_id: str                    # PRIMARY KEY: "krishna", "buddha", etc.
    display_name: str                     # "Lord Krishna", "Buddha"
    description: str
    domain: str                           # "spiritual", "philosophical", "historical"
    
    # Configuration
    system_prompt: str
    max_response_length: int = 500
    temperature: float = 0.7
    is_active: bool = True
    
    # Associated content
    associated_books: List[str] = field(default_factory=list)
    vector_namespace: str = ""            # For vector DB partitioning
    total_chunks: int = 0
    
    # Usage analytics
    total_requests: int = 0
    total_tokens: int = 0
    avg_response_time_ms: float = 0.0
    user_satisfaction_score: float = 0.0  # Average rating
    
    # Popular patterns
    top_keywords: List[Dict[str, Any]] = field(default_factory=list)  # {"keyword": "dharma", "count": 150}
    common_themes: List[Dict[str, Any]] = field(default_factory=list)
    peak_usage_hours: List[int] = field(default_factory=list)
    
    # Content performance
    most_retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    avg_rag_relevance: float = 0.0
    content_gaps: List[str] = field(default_factory=list)  # Topics with poor responses
    
    # Administrative
    created_at: str = None
    last_updated: str = None
    created_by: str = ""                  # Admin email
    
    type: str = "personality_config"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.vector_namespace == "":
            self.vector_namespace = self.personality_id

@dataclass
class ContentSource:
    """Books, papers, and content sources with metadata"""
    # Content identification
    source_id: str                        # PRIMARY KEY
    title: str
    author: str
    source_type: str                      # "book", "paper", "scripture", "article"
    
    # Content details
    language: str = "English"
    publication_date: Optional[str] = None
    isbn: Optional[str] = None
    url: Optional[str] = None
    
    # Processing status
    processing_status: str = "pending"    # "pending", "processing", "completed", "failed"
    total_chunks: int = 0
    total_characters: int = 0
    
    # Associations
    associated_personalities: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Performance analytics
    total_retrievals: int = 0
    avg_relevance_score: float = 0.0
    
    # Administrative
    uploaded_by: str = ""                 # Admin email
    upload_date: str = None
    last_updated: str = None
    
    type: str = "content_source"
    
    def __post_init__(self):
        if self.upload_date is None:
            self.upload_date = datetime.utcnow().isoformat()

@dataclass
class ContentChunk:
    """Individual text chunks with detailed analytics"""
    # Chunk identification
    chunk_id: str                         # PRIMARY KEY
    source_id: str                        # Foreign key to ContentSource
    personality_id: str                   # Associated personality
    
    # Content
    text_content: str
    chunk_index: int                      # Position in source document
    character_count: int
    token_estimate: int
    
    # Metadata
    chapter: Optional[str] = None
    section: Optional[str] = None
    verse: Optional[str] = None
    page_number: Optional[int] = None
    
    # Vector embeddings
    embedding_model: str = ""
    embedding_dimensions: int = 0
    embedding_created_at: str = None
    
    # Performance analytics
    retrieval_count: int = 0
    avg_relevance_score: float = 0.0
    last_retrieved: Optional[str] = None
    
    # Quality metrics
    content_quality_score: float = 0.0   # AI-assessed quality
    user_feedback_score: float = 0.0     # Based on user ratings when this chunk is used
    
    type: str = "content_chunk"

# ============================================================================
# ANALYTICS AGGREGATIONS
# ============================================================================

@dataclass
class DailyAnalytics:
    """Daily aggregated analytics for trends"""
    date: str                             # PRIMARY KEY: "2025-08-05"
    
    # User metrics
    total_users: int = 0
    new_users: int = 0
    active_users: int = 0
    returning_users: int = 0
    
    # Usage metrics
    total_sessions: int = 0
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    
    # Performance metrics
    avg_response_time_ms: float = 0.0
    avg_rag_time_ms: float = 0.0
    avg_user_satisfaction: float = 0.0
    
    # Content metrics
    top_personalities: List[Dict[str, Any]] = field(default_factory=list)
    top_keywords: List[Dict[str, Any]] = field(default_factory=list)
    
    # System health
    error_rate: float = 0.0
    fallback_rate: float = 0.0
    
    type: str = "daily_analytics"

@dataclass
class PersonalityAnalytics:
    """Detailed analytics per personality"""
    personality_id: str                   # PRIMARY KEY
    date: str                            # Date for this analytics snapshot
    
    # Usage patterns
    total_requests: int = 0
    unique_users: int = 0
    avg_requests_per_user: float = 0.0
    
    # Popular content
    top_keywords: List[Dict[str, Any]] = field(default_factory=list)
    popular_themes: List[Dict[str, Any]] = field(default_factory=list)
    most_retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Performance metrics
    avg_response_time_ms: float = 0.0
    avg_rag_relevance: float = 0.0
    user_satisfaction: float = 0.0
    
    # Content gaps (topics with poor performance)
    content_gaps: List[str] = field(default_factory=list)
    
    type: str = "personality_analytics"

# ============================================================================
# ABUSE PREVENTION & MONITORING
# ============================================================================

@dataclass
class AbuseAlert:
    """Real-time abuse detection alerts"""
    alert_id: str                         # PRIMARY KEY
    email: str                           # User being flagged
    user_id: str
    
    # Alert details
    alert_type: str                       # "high_volume", "inappropriate_content", "rate_limit"
    severity: str                         # "low", "medium", "high", "critical"
    description: str
    triggered_at: str
    
    # Metrics that triggered alert
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    
    # Admin response
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    action_taken: Optional[str] = None    # "no_action", "warning", "temporary_block", "permanent_block"
    admin_notes: Optional[str] = None
    
    # Status
    status: str = "open"                  # "open", "investigating", "resolved", "dismissed"
    
    type: str = "abuse_alert"

@dataclass
class UsageThreshold:
    """Configurable thresholds for abuse detection"""
    threshold_id: str                     # PRIMARY KEY
    threshold_type: str                   # "daily_requests", "hourly_tokens", "monthly_cost"
    
    # Threshold values
    warning_level: float
    alert_level: float
    block_level: float
    
    # Time windows
    time_window_hours: int = 24
    
    # Status
    is_active: bool = True
    created_by: str = ""
    created_at: str = None
    
    type: str = "usage_threshold"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
