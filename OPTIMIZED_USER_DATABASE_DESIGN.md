# Optimized User Database Design - Two Container Approach

## 🎯 **Simplified Two-Container Design**

### **Container 1: `users` (User Profiles & Aggregated Data)**
```python
@dataclass
class UserDocument:
    """Consolidated user profile with embedded aggregated data"""
    # Cosmos DB required fields
    id: str                           # User ID (UUID)
    partition_key: str               # Same as id for single-user queries
    document_type: str = "user_profile"
    
    # Authentication & Identity
    auth_id: str                     # Microsoft Entra ID (oid field) - UNIQUE
    email: str                       # Primary email address - UNIQUE
    name: str                        # Display name from Entra ID
    given_name: Optional[str]
    family_name: Optional[str]
    auth_provider: str = "microsoft"
    tenant_id: Optional[str]
    
    # Profile Information
    profile_picture_url: Optional[str]
    job_title: Optional[str]
    company_name: Optional[str]
    preferred_language: str = "en"
    timezone: Optional[str]
    
    # User Preferences (Generic & Flexible)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Account Status & Metadata
    account_status: str = "active"
    created_at: datetime
    last_login: datetime
    last_activity: datetime
    
    # Aggregated Usage Statistics (Live Updated)
    usage_stats: Dict[str, Any] = field(default_factory=dict)
    # Example: {
    #   "total_sessions": 142,
    #   "total_queries": 856,
    #   "total_tokens": 25420,
    #   "total_cost_usd": 12.45,
    #   "avg_session_duration": 720,  # seconds
    #   "favorite_personalities": ["socrates", "einstein"],
    #   "common_topics": ["ethics", "science", "philosophy"],
    #   "monthly_usage": {
    #       "2025-07": {"queries": 45, "cost": 2.30}
    #   }
    # }
    
    # Recent Activity (Last 10 interactions for quick access)
    recent_activity: List[Dict[str, Any]] = field(default_factory=list)
    # Example: [
    #   {
    #       "interaction_id": "int_789",
    #       "timestamp": "2025-07-30T14:30:00Z",
    #       "query": "What is wisdom?",
    #       "personality": "socrates",
    #       "rating": 5,
    #       "bookmarked": true
    #   }
    # ]
    
    # User Bookmarks (Embedded for quick access)
    bookmarks: List[Dict[str, Any]] = field(default_factory=list)
    # Example: [
    #   {
    #       "bookmark_id": "bm_456",
    #       "title": "Socratic wisdom on knowledge",
    #       "query": "What does it mean to know nothing?",
    #       "response": "True wisdom comes from...",
    #       "personality": "socrates",
    #       "bookmarked_at": "2025-07-30T14:30:00Z",
    #       "tags": ["wisdom", "philosophy"],
    #       "notes": "Great insight for my philosophy study"
    #   }
    # ]
    
    # Risk & Admin
    risk_score: float = 0.0
    abuse_flags: List[str] = field(default_factory=list)
    is_admin: bool = False
    admin_notes: Optional[str] = None
    
    # Privacy & Compliance
    data_retention_consent: bool = True
    analytics_consent: bool = True
    last_consent_update: Optional[datetime] = None
```

### **Container 2: `user_activity` (All Detailed Activity)**
```python
@dataclass
class UserActivityDocument:
    """All user activity - sessions, interactions, detailed analytics"""
    # Cosmos DB required fields
    id: str                          # Activity ID (UUID)
    partition_key: str              # user_id for efficient querying
    document_type: str              # "session", "interaction", "analytics_snapshot"
    
    # Common fields
    user_id: str                    # Reference to user
    timestamp: datetime
    
    # Session Document (when document_type = "session")
    session_data: Optional[Dict[str, Any]] = None
    # Example: {
    #   "session_id": "sess_123",
    #   "start_time": "2025-07-30T14:00:00Z",
    #   "end_time": "2025-07-30T14:15:00Z",
    #   "duration_seconds": 900,
    #   "total_queries": 5,
    #   "personalities_used": ["socrates", "einstein"],
    #   "user_agent": "Mozilla/5.0...",
    #   "device_type": "desktop"
    # }
    
    # Interaction Document (when document_type = "interaction")
    interaction_data: Optional[Dict[str, Any]] = None
    # Example: {
    #   "session_id": "sess_123",
    #   "sequence": 1,
    #   "user_query": "What is the meaning of life?",
    #   "personality_used": "socrates",
    #   "response_text": "The unexamined life is not worth living...",
    #   "response_time_ms": 1200,
    #   "model_used": "gemini-pro",
    #   "input_tokens": 25,
    #   "output_tokens": 150,
    #   "cost_usd": 0.023,
    #   "user_rating": 5,
    #   "was_bookmarked": true,
    #   "content_themes": ["philosophy", "meaning", "ethics"]
    # }
    
    # Analytics Snapshot (when document_type = "analytics_snapshot")
    analytics_data: Optional[Dict[str, Any]] = None
    # Example: {
    #   "period": "daily",
    #   "date": "2025-07-30",
    #   "sessions_count": 3,
    #   "queries_count": 15,
    #   "total_cost": 0.45,
    #   "personality_usage": {"socrates": 8, "einstein": 7},
    #   "topic_distribution": {"philosophy": 10, "science": 5},
    #   "avg_rating": 4.3
    # }
```

## 🔍 **Query Patterns**

### **Get User Profile with Recent Activity:**
```python
# Single query to get everything about a user
user_doc = await container.read_item(
    item=user_id, 
    partition_key=user_id
)

# User gets: profile + preferences + recent activity + bookmarks + stats
```

### **Get User's Detailed Activity History:**
```python
# Query user's activity container
query = """
SELECT * FROM user_activity ua 
WHERE ua.user_id = @user_id 
AND ua.document_type = 'interaction'
AND ua.timestamp >= @last_month
ORDER BY ua.timestamp DESC
"""

interactions = await container.query_items(query, parameters=[
    {"name": "@user_id", "value": user_id},
    {"name": "@last_month", "value": last_month}
])
```

### **Admin Analytics:**
```python
# Cross-partition query for admin dashboard
query = """
SELECT 
    COUNT(1) as total_interactions,
    AVG(ua.interaction_data.user_rating) as avg_rating,
    ua.interaction_data.personality_used
FROM user_activity ua 
WHERE ua.document_type = 'interaction'
AND ua.timestamp >= @last_week
GROUP BY ua.interaction_data.personality_used
"""
```

## 💰 **Cost Comparison (Serverless Mode)**

### **Cosmos DB Serverless Pricing:**
- **Request Units**: ~$0.000016 per RU
- **Storage**: ~$0.25 per GB/month

### **5 Container vs 2 Container Cost Analysis:**

**Storage Cost (Same for both approaches):**
- User profiles: ~100 KB per user
- User activity: ~10 KB per interaction
- For 1,000 users with 10 interactions each: ~110 MB total
- **Storage cost: ~$0.03/month** (negligible)

**Request Unit Cost (This is where container count matters):**

**5 Container Approach:**
- More cross-container queries required
- Example: Get user + recent activity + bookmarks = 3 separate queries
- Estimated: ~150 RU per user dashboard load
- **Operational complexity**: Higher RU consumption due to multiple queries

**2 Container Approach:**  
- Fewer, more efficient queries
- Example: Get user with embedded data = 1 query for most operations
- Estimated: ~50 RU per user dashboard load
- **Operational efficiency**: 60-70% fewer RUs for common operations

**Real Monthly Cost Estimate:**
- 1,000 active users, 100 interactions/month each
- **5 containers**: ~500,000 RU/month = ~$8/month
- **2 containers**: ~200,000 RU/month = ~$3.20/month
- **Savings: ~$4.80/month + reduced operational complexity**

**The main benefit isn't raw cost savings (both are cheap in serverless), but operational efficiency and query simplicity.**

## 🏆 **Benefits of 2-Container Design**

### **Performance:**
- ✅ **Faster user lookups** - everything in one document
- ✅ **Efficient activity queries** - partitioned by user_id
- ✅ **Reduced cross-container joins**

### **Cost:**
- ✅ **More efficient RU usage** - fewer cross-container queries
- ✅ **Lower operational costs** - simpler query patterns
- ✅ **Serverless-optimized** - pay only for what you use

### **Simplicity:**
- ✅ **Easier to manage** - fewer containers
- ✅ **Simpler queries** - less complex joins
- ✅ **Better for small-to-medium scale**

### **Flexibility:**
- ✅ **Easy to migrate** to more containers later if needed
- ✅ **Generic design** works for any content domain
- ✅ **Embedded data** for quick access, detailed data for analytics

## 🎯 **Recommendation**

**Start with the 2-container approach:**

1. **`users`** - User profiles with embedded recent activity and bookmarks
2. **`user_activity`** - All detailed activity history and analytics

This gives you:
- All the analytics capabilities you need
- 60% cost savings
- Better performance for common queries
- Easier implementation and maintenance

**You can always split into more containers later** if you need to scale specific data types independently.

**Should I implement this 2-container design?** 🚀
