# Vimarsh Multi-Domain User Database Design & Schema

## 🎯 **Core Requirements Analysis**

Based on your needs, the user database must capture:
1. **User Identity & Profile** - Basic user information and preferences
2. **User Activity Tracking** - Every query, response, and interaction
3. **Analytics & Insights** - Usage patterns, popular content, engagement metrics
4. **Abuse Detection** - API token abuse, excessive usage, spam detection
5. **Cost Management** - Token usage, costs, budget tracking per user
6. **Conversation Continuity** - Session history, context preservation
7. **Content Personalization** - Favorite personalities, domain interests

**🔄 Design Philosophy:** Domain-agnostic schema that works for spiritual guidance, philosophical discussions, scientific explanations, historical insights, literary analysis, or any knowledge domain.

## 🗄️ **Database Schema Design**

### **Container 1: `users` (User Profiles)**
```python
@dataclass
class UserProfile:
    """Main user profile document"""
    # Cosmos DB required fields
    id: str                           # Cosmos DB document ID (UUID)
    partition_key: str               # For partitioning (email domain or user_id)
    
    # Authentication & Identity
    auth_id: str                     # Microsoft Entra ID (oid field) - UNIQUE
    email: str                       # Primary email address - UNIQUE
    name: str                        # Display name from Entra ID
    given_name: Optional[str]        # First name
    family_name: Optional[str]       # Last name
    auth_provider: str = "microsoft" # Authentication provider
    tenant_id: Optional[str]         # Organization tenant ID
    
    # Profile Information
    profile_picture_url: Optional[str]
    job_title: Optional[str]         # From Entra ID
    company_name: Optional[str]      # From Entra ID
    preferred_language: str = "en"
    timezone: Optional[str]
    
    # Application-Specific Preferences (Generic & Flexible)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    # Example: {
    #   "favorite_personalities": ["krishna", "buddha", "gandhi", "socrates", "einstein"],
    #   "content_interests": ["philosophy", "science", "history", "literature", "wisdom"],
    #   "preferred_response_style": "scholarly", # scholarly, conversational, practical, academic
    #   "preferred_sources": ["classical_texts", "modern_philosophy", "scientific_papers"],
    #   "language_preference": "english", # english, hindi, sanskrit, spanish, french
    #   "complexity_level": "intermediate", # beginner, intermediate, advanced, expert
    #   "content_domains": ["philosophy", "science", "literature", "history"], # Flexible domains
    #   "interaction_style": "socratic", # socratic, direct, exploratory, guided
    #   "learning_goals": ["understanding_ethics", "exploring_meaning", "practical_wisdom"]
    # }
    
    # Account Status & Metadata
    account_status: str = "active"   # active, suspended, blocked, deleted
    created_at: datetime
    last_login: datetime
    last_activity: datetime
    first_session_date: datetime
    
    # Usage Statistics (Summary - detailed in separate containers)
    total_sessions: int = 0
    total_queries: int = 0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    
    # Risk & Abuse Detection
    risk_score: float = 0.0          # 0-100, calculated based on usage patterns
    abuse_flags: List[str] = field(default_factory=list)
    # Example: ["excessive_usage", "suspicious_patterns", "token_abuse"]
    
    # Admin & Moderation
    is_admin: bool = False
    admin_notes: Optional[str]
    moderation_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # GDPR & Privacy
    data_retention_consent: bool = True
    analytics_consent: bool = True
    marketing_consent: bool = False
    last_consent_update: Optional[datetime]
```

### **Container 2: `user_sessions` (Session Tracking)**
```python
@dataclass
class UserSession:
    """Individual user session document"""
    # Cosmos DB required fields
    id: str                          # Session ID (UUID)
    partition_key: str              # user_id for partitioning
    
    # Session Identity
    user_id: str                    # Reference to UserProfile.id
    session_id: str                 # Unique session identifier
    
    # Session Metadata
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    is_active: bool = True
    
    # Technical Context
    user_agent: Optional[str]
    ip_address: Optional[str]       # Hashed for privacy
    device_type: Optional[str]      # mobile, desktop, tablet
    browser: Optional[str]
    platform: Optional[str]         # windows, mac, linux, ios, android
    
    # Usage Summary
    total_queries: int = 0
    total_responses: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    
    # Content Engagement
    personalities_used: List[str] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    
    # Quality Metrics
    avg_response_time_ms: float = 0.0
    user_satisfaction_ratings: List[int] = field(default_factory=list)
    
    # Session Outcome
    session_quality: str = "unknown" # excellent, good, fair, poor
    completed_successfully: bool = True
    error_count: int = 0
```

### **Container 3: `user_interactions` (Query/Response Tracking)**
```python
@dataclass
class UserInteraction:
    """Individual query-response interaction"""
    # Cosmos DB required fields
    id: str                          # Interaction ID (UUID)
    partition_key: str              # user_id for efficient querying
    
    # Interaction Identity
    user_id: str                    # Reference to UserProfile.id
    session_id: str                 # Reference to UserSession.session_id
    interaction_sequence: int       # Order within session (1, 2, 3...)
    
    # Timing
    timestamp: datetime
    response_time_ms: int           # Time to generate response
    
    # User Input
    user_query: str                 # Original user question
    user_query_length: int          # Character count
    user_query_language: str        # Detected language
    query_category: str             # philosophy, science, history, literature, wisdom, etc.
    query_complexity: str           # simple, moderate, complex
    
    # System Response
    personality_used: str           # krishna, buddha, gandhi, socrates, einstein, etc.
    response_text: str              # Generated response
    response_length: int            # Character count
    response_quality: str           # high, medium, low, fallback
    
    # Technical Metrics
    model_used: str                 # gemini-pro, gpt-4, etc.
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    
    # RAG Context (if applicable)
    rag_sources_used: List[str] = field(default_factory=list)
    citations_provided: List[str] = field(default_factory=list)
    context_relevance_score: Optional[float]
    
    # User Feedback
    user_rating: Optional[int]      # 1-5 star rating
    user_feedback: Optional[str]    # Text feedback
    was_helpful: Optional[bool]     # Thumbs up/down
    was_bookmarked: bool = False
    was_shared: bool = False
    
    # Content Classification (Flexible)
    content_tags: List[str] = field(default_factory=list)
    content_themes: List[str] = field(default_factory=list)  # wisdom, ethics, meaning, etc.
    source_references: List[str] = field(default_factory=list)  # Any authoritative sources
    
    # Safety & Moderation
    safety_score: float = 1.0       # 0-1, content safety score
    moderation_flags: List[str] = field(default_factory=list)
    was_flagged: bool = False
```

### **Container 4: `user_analytics` (Aggregated Analytics)**
```python
@dataclass
class UserAnalytics:
    """Aggregated user analytics (updated periodically)"""
    # Cosmos DB required fields
    id: str                          # Analytics ID (user_id + date)
    partition_key: str              # user_id
    
    # Identity & Time Period
    user_id: str
    analytics_period: str           # daily, weekly, monthly, all_time
    period_start: datetime
    period_end: datetime
    last_updated: datetime
    
    # Usage Metrics
    total_sessions: int
    total_interactions: int
    total_tokens: int
    total_cost_usd: float
    avg_session_duration: float
    avg_queries_per_session: float
    
    # Content Preferences
    personality_usage: Dict[str, int]        # personality -> count
    topic_distribution: Dict[str, int]       # topic -> count
    query_complexity_breakdown: Dict[str, int] # complexity -> count
    response_quality_breakdown: Dict[str, int] # quality -> count
    
    # Engagement Patterns
    most_active_hours: List[int]            # Hours of day (0-23)
    most_active_days: List[str]             # Days of week
    avg_response_rating: float
    bookmark_rate: float                    # % of responses bookmarked
    share_rate: float                       # % of responses shared
    
    # Learning & Growth (Generic)
    learning_journey_progress: Dict[str, Any]  # Flexible learning tracking
    knowledge_areas_explored: List[str]        # Any knowledge domains
    favorite_sources: List[str]                # Preferred authoritative sources
    
    # Risk Assessment
    usage_anomalies: List[str]              # Detected unusual patterns
    risk_indicators: Dict[str, float]
    abuse_likelihood: float                 # 0-1 probability
```

### **Container 5: `user_bookmarks` (Saved Content)**
```python
@dataclass
class UserBookmark:
    """User bookmarked content"""
    # Cosmos DB required fields
    id: str                          # Bookmark ID (UUID)
    partition_key: str              # user_id
    
    # Identity
    user_id: str
    interaction_id: str             # Reference to original UserInteraction
    
    # Bookmark Metadata
    bookmarked_at: datetime
    bookmark_title: str             # User-provided or auto-generated
    bookmark_tags: List[str] = field(default_factory=list)
    bookmark_notes: Optional[str]   # User notes
    
    # Content
    original_query: str
    bookmarked_response: str
    personality: str
    source_references: List[str] = field(default_factory=list)  # Any authoritative sources
    
    # Organization
    bookmark_collection: Optional[str] # User-created collections
    is_favorite: bool = False
    access_count: int = 0           # How many times accessed
    last_accessed: Optional[datetime]
```

## 📊 **Analytics & Insights Capabilities**

### **User Analytics Dashboard:**
```python
# What you can build with this schema:

class UserAnalyticsService:
    async def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Complete user dashboard analytics"""
        return {
            # Personal Journey (Generic)
            "learning_growth_metrics": {
                "total_sessions": 142,
                "topics_explored": ["philosophy", "ethics", "meaning_of_life"],
                "favorite_personality": "socrates",  # Could be any personality
                "knowledge_progression": "beginner -> intermediate"
            },
            
            # Usage Patterns
            "usage_insights": {
                "most_active_time": "evenings (7-9 PM)",
                "avg_session_duration": "12 minutes",
                "consistency_score": 8.5,  # How regularly they engage
                "deep_dive_topics": ["ethics", "practical_philosophy"]
            },
            
            # Content Quality
            "interaction_quality": {
                "avg_rating": 4.3,
                "bookmark_rate": 0.23,  # 23% of responses bookmarked
                "share_rate": 0.08,     # 8% shared
                "return_rate": 0.67     # 67% return for follow-up questions
            },
            
            # Recommendations (Domain-Agnostic)
            "personalized_suggestions": [
                "Try exploring Einstein's thoughts on science and philosophy",
                "Your interest in ethics suggests you'd enjoy Aristotle's teachings",
                "Consider morning reflection sessions based on your evening patterns"
            ]
        }
```

### **Admin Analytics & Abuse Detection:**
```python
class AdminAnalyticsService:
    async def get_abuse_detection_insights(self) -> Dict[str, Any]:
        """Comprehensive abuse detection analytics"""
        return {
            # Usage Anomalies
            "high_risk_users": [
                {
                    "user_id": "user_123",
                    "risk_score": 85,
                    "red_flags": ["excessive_api_calls", "repetitive_queries", "bot_like_patterns"],
                    "daily_query_count": 1500,  # Way above normal
                    "cost_impact": "$45.23"
                }
            ],
            
            # System Health
            "platform_health": {
                "avg_response_time": "1.2s",
                "error_rate": 0.02,  # 2% error rate
                "user_satisfaction": 4.4,
                "cost_per_interaction": "$0.023"
            },
            
            # Content Insights (Domain-Agnostic)
            "common_questions": [
                {"question": "What is the meaning of life?", "frequency": 234, "avg_rating": 4.6},
                {"question": "How to find purpose?", "frequency": 189, "avg_rating": 4.3},
                {"question": "What is wisdom?", "frequency": 156, "avg_rating": 4.5}
            ],
            
            # Usage Trends
            "growth_metrics": {
                "new_users_this_month": 67,
                "retention_rate": 0.73,  # 73% return after first week
                "feature_adoption": {
                    "bookmarking": 0.45,  # 45% of users bookmark content
                    "multiple_personalities": 0.62,  # 62% try different personalities
                    "follow_up_questions": 0.78   # 78% ask follow-up questions
                }
            }
        }
```

## 🔍 **Query Patterns for Key Features**

### **1. User Activity Tracking:**
```sql
-- Get user's recent activity (Cosmos DB SQL API)
SELECT * FROM user_interactions ui 
WHERE ui.user_id = @user_id 
AND ui.timestamp >= @last_week
ORDER BY ui.timestamp DESC
```

### **2. Abuse Detection:**
```sql
-- Find users with excessive API usage
SELECT u.id, u.email, COUNT(ui.id) as daily_queries
FROM users u 
JOIN user_interactions ui ON u.id = ui.user_id
WHERE ui.timestamp >= @today
GROUP BY u.id, u.email
HAVING COUNT(ui.id) > 100  -- Threshold for suspicious activity
```

### **3. Popular Content Analysis:**
```sql
-- Most common questions and their success rates
SELECT 
    ui.query_category,
    COUNT(*) as frequency,
    AVG(ui.user_rating) as avg_rating,
    AVG(ui.response_time_ms) as avg_response_time
FROM user_interactions ui
WHERE ui.timestamp >= @last_month
GROUP BY ui.query_category
ORDER BY frequency DESC
```

## 💾 **Storage & Performance Considerations**

### **Partitioning Strategy:**
- **users**: Partition by `email_domain` or `user_id`
- **user_sessions**: Partition by `user_id` 
- **user_interactions**: Partition by `user_id` (enables efficient user-specific queries)
- **user_analytics**: Partition by `user_id`
- **user_bookmarks**: Partition by `user_id`

### **Indexing Strategy:**
```python
# Key indexes needed:
{
    "users": [
        {"email": 1},           # Unique index for login
        {"auth_id": 1},         # Unique index for Entra ID
        {"created_at": -1},     # For new user analytics
        {"last_activity": -1}   # For active user queries
    ],
    "user_interactions": [
        {"user_id": 1, "timestamp": -1},  # User activity timeline
        {"timestamp": -1},                # Recent activity across all users
        {"user_query": "text"},           # Full-text search on questions
        {"personality_used": 1},          # Personality usage analytics
        {"query_category": 1}             # Category-based analytics
    ]
}
```

### **Data Retention Policy:**
```python
# Automatic cleanup for performance and privacy
RETENTION_POLICY = {
    "user_interactions": "2 years",      # Detailed interactions
    "user_sessions": "1 year",           # Session data
    "user_analytics": "5 years",         # Aggregated analytics (longer retention)
    "user_bookmarks": "permanent",       # User-saved content
    "users": "permanent"                 # User profiles
}
```

## 🎯 **Does This Design Cover All Your Needs?**

This schema captures:
- ✅ **Complete user activity** - Every query, response, and interaction
- ✅ **Advanced analytics** - Usage patterns, preferences, engagement metrics
- ✅ **Abuse detection** - Excessive usage, suspicious patterns, token abuse
- ✅ **Cost tracking** - Per-user token usage and costs
- ✅ **Content insights** - Popular questions, response quality, user satisfaction
- ✅ **Personalization** - User preferences, spiritual journey tracking
- ✅ **Admin tools** - User management, moderation, system health

**Questions for you:**
1. Are there any specific analytics or tracking requirements I missed?
2. Do you want to add social features (user-to-user interactions, community features)?
3. Any specific compliance requirements (GDPR, HIPAA, etc.) to consider?
4. Should we include A/B testing capabilities for different response styles?

**Ready to implement this design?** 🚀
