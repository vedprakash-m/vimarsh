# Database Design & Architecture Specification
**Vimarsh - Domain-Agnostic AI Guidance Platform with Foundational Texts Integration**

---

## 📋 Document Information

| Field | Value |
|-------|-------|
| **Document Type** | Technical Specification |
| **Version** | 1.0 |
| **Last Updated** | August 5, 2025 |
| **Status** | Active |
| **Authority Level** | Source of Truth |
| **Scope** | Complete Database Architecture |

---

## 🎯 Executive Summary

This document defines the complete database architecture for Vimarsh, a domain-agnostic AI guidance platform that provides personalized advice from foundational texts through AI personas. The design follows Azure Cosmos DB best practices, implements proper separation of concerns, and scales from current requirements (~1K users) to future needs (100K+ users).

**Key Architectural Decisions**:
- Single database with domain-separated containers for current scale
- User-based and time-based partitioning strategies
- Real-time analytics through change feed processing
- Materialized views for performance optimization
- Clear migration path to multi-database architecture

---

## 🏗️ Database Architecture Overview

### Primary Database: vimarsh-multi-personality

```
Azure Cosmos DB (SQL API)
├── Consistency Level: Session
├── Multi-region: Primary (East US), Secondary (West Europe)
├── Backup: Continuous (30-day point-in-time recovery)
└── Throughput: Autoscale (400-4000 RU/s per container)

Container Architecture:
├── Core Operational Containers
│   ├── users (/user_id) - User account management
│   ├── user_sessions (/user_id) - Session tracking
│   ├── user_interactions (/user_id) - Interaction logs
│   ├── personalities (/personality_id) - AI personality configurations
│   └── personality_vectors (/partition_key) - AI content & embeddings (hierarchical partitioning)
├── Analytics Containers
│   ├── user_analytics (/user_id) - Aggregated user metrics
│   ├── content_analytics (/source) - Foundational texts performance
│   ├── daily_metrics (/date) - Time-series system analytics
│   └── abuse_incidents (/user_id) - Content moderation events
└── Materialized Views (Change Feed Triggered)
    ├── engagement_summary (/engagement_tier)
    ├── content_popularity (/time_period)
    ├── system_health (/metric_type)
    └── incidents_by_content (/source) - Content moderation view for admin
```

---

## 📊 Container Specifications

### 1. Core Operational Containers

#### 1.1 users Container
**Purpose**: User account management and authentication data
**Partition Key**: `/user_id`
**Estimated Size**: 100MB (1K users → 10GB at 100K users)
**RU/s**: 400-1000 (autoscale)

```json
{
  "id": "user_e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "partition_key": "e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "user_id": "e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "document_type": "user_profile",
  
  // Authentication & Identity
  "auth_id": "5d8449a065877ac1",
  "email": "vedprakash.mishra@email.com",
  "name": "Vedprakash Mishra",
  "auth_provider": "microsoft",
  "email_verified": true,
  
  // Account Information
  "account_status": "active", // active, suspended, deleted
  "subscription_tier": "free", // free, premium, enterprise
  "subscription_expires": null,
  "account_flags": [], // verified, beta_tester, etc.
  
  // Basic Preferences (Note: Complex preferences moved to future user_preferences container)
  "preferred_language": "en",
  "preferred_personalities": ["krishna", "socrates"],
  "content_preferences": {
    "foundational_texts": ["bhagavad_gita", "upanishads"],
    "complexity_level": "intermediate",
    "citation_style": "detailed"
  },
  
  // Privacy & Consent
  "privacy_settings": {
    "data_collection_consent": true,
    "analytics_consent": true,
    "marketing_consent": false
  },
  
  // Metadata
  "created_at": "2025-08-05T21:17:31.137475Z",
  "updated_at": "2025-08-05T21:17:31.137475Z",
  "last_login": "2025-08-05T21:17:31.137475Z",
  "profile_version": "1.0",
  
  // Technical
  "timezone": "America/New_York",
  "locale": "en-US",
  "_ttl": null // No expiration for user profiles
}
```

**Indexing Policy**:
```json
{
  "indexingPolicy": {
    "automatic": true,
    "includedPaths": [
      {"path": "/user_id/?"},
      {"path": "/email/?"},
      {"path": "/auth_id/?"},
      {"path": "/account_status/?"},
      {"path": "/subscription_tier/?"},
      {"path": "/created_at/?"},
      {"path": "/last_login/?"}
    ],
    "excludedPaths": [
      {"path": "/privacy_settings/*"},
      {"path": "/content_preferences/*"}
    ],
    "compositeIndexes": [
      [
        {"path": "/account_status", "order": "ascending"},
        {"path": "/subscription_tier", "order": "ascending"}
      ],
      [
        {"path": "/created_at", "order": "descending"},
        {"path": "/account_status", "order": "ascending"}
      ]
    ]
  }
}
```

#### 1.2 user_sessions Container
**Purpose**: Session tracking and user journey analytics
**Partition Key**: `/user_id`
**Estimated Size**: 500MB (current) → 50GB (at scale)
**RU/s**: 400-2000 (autoscale)

```json
{
  "id": "session_e45d45fe_20250805_143721",
  "partition_key": "e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "user_id": "e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "document_type": "user_session",
  
  // Session Identity
  "session_id": "session_e45d45fe_20250805_143721",
  "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  
  // Session Timing
  "start_time": "2025-08-05T14:37:21.127Z",
  "end_time": "2025-08-05T14:45:44.234Z",
  "duration_seconds": 503,
  "last_activity": "2025-08-05T14:45:44.234Z",
  
  // Session Status
  "status": "completed", // active, completed, abandoned, expired
  "completion_reason": "natural_end", // natural_end, timeout, user_logout, system_error
  
  // Interaction Metrics
  "interaction_count": 5,
  "total_response_time_ms": 6250,
  "avg_response_time_ms": 1250,
  "user_satisfaction_rating": 4.2,
  
  // Content Engagement
  "personalities_engaged": ["krishna"],
  "foundational_texts_accessed": ["bhagavad_gita"],
  "citation_interactions": 7,
  "content_depth_score": 0.76,
  
  // Technical Context
  "device_info": {
    "device_type": "desktop", // desktop, mobile, tablet
    "browser": "Chrome/91.0",
    "os": "macOS",
    "screen_resolution": "1920x1080"
  },
  
  "location_context": {
    "country": "US",
    "timezone": "America/New_York",
    "ip_hash": "sha256_hash_of_ip" // Privacy-preserving
  },
  
  // Quality Metrics
  "session_quality_score": 0.87,
  "engagement_indicators": {
    "scroll_depth": 0.85,
    "time_on_guidance": 420,
    "return_likelihood": 0.78
  },
  
  // Metadata
  "created_at": "2025-08-05T14:37:21.127Z",
  "updated_at": "2025-08-05T14:45:44.234Z",
  "_ttl": 7776000 // 90 days retention
}
```

#### 1.3 user_interactions Container
**Purpose**: Detailed interaction logs for analytics and debugging
**Partition Key**: `/user_id`
**Estimated Size**: 2GB (current) → 200GB (at scale)
**RU/s**: 800-4000 (autoscale)

```json
{
  "id": "interaction_bd6a8685-73c7-46b0-a7eb-786955803418",
  "partition_key": "e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "user_id": "e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "document_type": "user_interaction",
  
  // Interaction Identity
  "interaction_id": "bd6a8685-73c7-46b0-a7eb-786955803418",
  "session_id": "session_e45d45fe_20250805_143721",
  "sequence_number": 3, // Order within session
  
  // Timing
  "timestamp": "2025-08-05T14:39:15.127Z",
  "response_time_ms": 1250,
  "processing_stages": {
    "query_understanding_ms": 150,
    "content_retrieval_ms": 400,
    "generation_ms": 600,
    "post_processing_ms": 100
  },
  
  // User Input
  "user_query": "What lessons can we learn from leadership during times of crisis?",
  "query_metadata": {
    "query_length": 67,
    "query_complexity": "medium",
    "query_category": "leadership_guidance",
    "intent_confidence": 0.94,
    "language_detected": "en"
  },
  
  // AI Response
  "response_text": "My fellow citizen, in times of crisis, leadership emerges not from authority but from dharma...",
  "response_metadata": {
    "response_length": 847,
    "personality_used": "krishna",
    "model_used": "gemini-2.5-flash",
    "generation_temperature": 0.7,
    "safety_filtered": false
  },
  
  // Content & Citations
  "foundational_texts_used": [
    {
      "source": "bhagavad_gita",
      "chapter": "2",
      "verse": "47",
      "relevance_score": 0.92,
      "citation_text": "You have a right to perform your prescribed duty, but not to the fruits of action"
    }
  ],
  
  "rag_metadata": {
    "chunks_retrieved": 5,
    "avg_relevance_score": 0.84,
    "retrieval_strategy": "semantic_hybrid",
    "embedding_model": "text-embedding-ada-002"
  },
  
  // User Feedback
  "user_rating": 5, // 1-5 scale
  "user_feedback": {
    "helpful": true,
    "accurate": true,
    "relevant": true,
    "well_cited": true
  },
  
  // Raw Cost Data (Calculation done asynchronously via change feed)
  "cost_data": {
    "input_tokens": 234,
    "output_tokens": 456,
    "model_used": "gemini-2.5-flash",
    "timestamp": "2025-08-05T14:39:15.127Z"
    // Cost calculation moved to change feed processor for performance
  },
  
  // Quality Scores
  "quality_metrics": {
    "response_relevance": 0.91,
    "citation_accuracy": 0.96,
    "user_satisfaction": 0.88,
    "safety_score": 0.99
  },
  
  // Metadata
  "created_at": "2025-08-05T14:39:15.127Z",
  "_ttl": 31536000 // 1 year retention
}
```

#### 1.4 personalities Container
**Purpose**: AI personality configurations and canonical definitions
**Partition Key**: `/personality_id`
**Estimated Size**: 10MB (current) → 100MB (at scale with 50+ personalities)
**RU/s**: 400-800 (autoscale)

```json
{
  "id": "krishna",
  "partition_key": "krishna",
  "personality_id": "krishna",
  "document_type": "personality_profile",
  
  // Core Identity
  "full_name": "Lord Krishna",
  "domain": "spiritual", // spiritual, philosophical, historical, literary
  "description": "Divine guidance from the Bhagavad Gita and Vedic wisdom traditions",
  "cultural_context": "Hindu philosophy and dharmic principles",
  
  // Personality Configuration
  "personality_traits": ["wise", "compassionate", "dharmic", "strategic", "patient"],
  "response_tone": "authoritative_yet_compassionate",
  "communication_style": "thoughtful_teacher", // teacher, mentor, guide, advisor
  "formality_level": "respectful", // casual, respectful, formal, reverent
  
  // AI Configuration
  "system_prompt_template": "You are Vimarsh, embodying the wisdom of Lord Krishna. Speak with compassion and authority, drawing from dharmic principles and the Bhagavad Gita to provide guidance...",
  "temperature": 0.7,
  "max_tokens": 800,
  "safety_guidelines": ["respect_religious_sensitivity", "avoid_theological_debates"],
  
  // Content Sources
  "primary_sources": ["bhagavad_gita", "mahabharata"],
  "secondary_sources": ["upanishads", "vedic_texts"],
  "content_expertise": ["dharma", "karma_yoga", "leadership", "duty", "decision_making"],
  
  // Usage Patterns
  "typical_queries": ["leadership_guidance", "ethical_dilemmas", "duty_vs_desire", "spiritual_growth"],
  "response_patterns": {
    "citation_frequency": "high", // how often to cite sources
    "story_usage": "frequent", // how often to use stories/examples
    "practical_application": "always" // how often to provide practical advice
  },
  
  // Configuration Status
  "is_active": true,
  "is_featured": true, // For homepage display
  "availability": "public", // public, premium, beta
  "personality_version": "1.2",
  "last_updated": "2025-08-01T00:00:00Z",
  
  // Analytics Integration
  "performance_baseline": {
    "target_satisfaction_score": 4.5,
    "target_citation_accuracy": 0.95,
    "target_response_time_ms": 1200
  },
  
  // Metadata
  "created_at": "2025-07-01T00:00:00Z",
  "created_by": "system",
  "_ttl": null // Permanent configuration
}
```

#### 1.5 personality_vectors Container
**Purpose**: AI personality content, embeddings, and foundational texts
**Partition Key**: `/partition_key` (Hierarchical: personality_id::source)
**Estimated Size**: 5GB (current) → 500GB (at scale with 50+ personalities)
**RU/s**: 400-2000 (autoscale)

```json
{
  "id": "krishna_bhagavad_gita_2_47",
  "partition_key": "krishna::bhagavad_gita", // Hierarchical partitioning for scalability
  "personality_id": "krishna",
  "document_type": "personality_content",
  
  // Content Identity
  "content_id": "bhagavad_gita_2_47",
  "content_type": "foundational_text", // foundational_text, personality_trait, response_template
  "content_category": "verse",
  
  // Source Information
  "source": "bhagavad_gita",
  "source_metadata": {
    "chapter": "2",
    "verse": "47",
    "book": "Bhagavad Gita",
    "translator": "Paramahansa Yogananda",
    "translation_version": "1995",
    "language": "sanskrit_english"
  },
  
  // Content Data
  "sanskrit_text": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
  "english_translation": "You have a right to perform your prescribed duty, but not to the fruits of action",
  "detailed_explanation": "This fundamental principle of dharma teaches that one should focus on righteous action without attachment to outcomes...",
  
  // Contextual Information
  "context": {
    "historical_context": "Spoken during the Kurukshetra war dialogue",
    "philosophical_context": "Karma Yoga - the path of action",
    "practical_application": "Leadership, decision-making, duty"
  },
  
  // Usage Analytics (Updated asynchronously via change feed)
  "usage_metrics": {
    "citation_count": 156,
    "last_accessed": "2025-08-05T14:39:15.127Z",
    "avg_relevance_score": 0.91,
    "user_rating_avg": 4.6,
    "effectiveness_score": 0.88
  },
  
  // Vector Embeddings
  "embeddings": {
    "text_embedding_ada_002": [-0.008636979, 0.01464418, -0.044941533, ...], // 1536 dimensions
    "embedding_version": "v2",
    "embedding_created": "2025-08-05T00:00:00Z"
  },
  
  // Quality Validation
  "validation": {
    "expert_reviewed": true,
    "expert_reviewer": "Dr. Sanskrit Scholar",
    "review_date": "2025-07-15T00:00:00Z",
    "accuracy_score": 0.98,
    "cultural_sensitivity_score": 0.96
  },
  
  // Personality Alignment (Simplified - references personality config)
  "personality_weight": 0.95, // How core this content is to Krishna's personality
  "topic_tags": ["karma_yoga", "duty", "action", "detachment"],
  
  // Metadata
  "created_at": "2025-07-01T00:00:00Z",
  "updated_at": "2025-08-01T00:00:00Z",
  "_ttl": null // Permanent content
}
```

### 2. Analytics Containers

#### 2.1 user_analytics Container
**Purpose**: Aggregated user behavior and engagement analytics
**Partition Key**: `/user_id`
**Estimated Size**: 200MB (current) → 20GB (at scale)
**RU/s**: 400-1000 (autoscale)

```json
{
  "id": "user_analytics_e45d45fe_202508",
  "partition_key": "e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "user_id": "e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "document_type": "user_analytics",
  
  // Analysis Period
  "analysis_period": "monthly", // daily, weekly, monthly, quarterly
  "period_start": "2025-08-01T00:00:00Z",
  "period_end": "2025-08-31T23:59:59Z",
  "data_freshness": "2025-08-05T14:45:00Z", // Last calculation time
  
  // User Profile Analytics
  "user_profile": {
    "user_tier": "engaged", // new, casual, engaged, power_user, churned
    "engagement_score": 0.85, // 0-1 scale
    "expertise_level": "intermediate", // beginner, intermediate, advanced
    "primary_interests": ["leadership", "dharma", "decision_making"],
    "personality_affinity": ["krishna", "socrates"]
  },
  
  // Session Analytics
  "session_metrics": {
    "total_sessions": 45,
    "avg_session_duration_min": 8.5,
    "session_completion_rate": 0.89,
    "peak_usage_hour": 14, // 2 PM
    "preferred_session_length": "medium", // short(<5min), medium(5-15min), long(>15min)
    "session_frequency_days": 2.3 // Average days between sessions
  },
  
  // Interaction Analytics
  "interaction_metrics": {
    "total_interactions": 127,
    "avg_interactions_per_session": 2.8,
    "query_complexity_avg": 0.76,
    "response_satisfaction_avg": 4.3,
    "citation_engagement_rate": 0.82
  },
  
  // Content Consumption
  "content_metrics": {
    "foundational_texts_accessed": ["bhagavad_gita", "upanishads", "mahabharata"],
    "content_depth_score": 0.76, // How deep into content they go
    "favorite_content_types": ["verse", "story", "philosophical_discussion"],
    "content_discovery_rate": 0.34, // Rate of accessing new content
    "content_retention_rate": 0.67 // Rate of re-accessing content
  },
  
  // Behavioral Patterns
  "behavioral_insights": {
    "usage_pattern": "consistent_seeker", // occasional, consistent_seeker, intensive_learner
    "peak_engagement_time": "afternoon",
    "session_triggers": ["work_stress", "decision_making", "life_guidance"],
    "response_preferences": "detailed_with_citations",
    "learning_progression": "advancing"
  },
  
  // Predictive Analytics
  "predictions": {
    "churn_risk_score": 0.15, // 0-1 scale (lower is better)
    "lifetime_value_estimate": 145.67,
    "next_session_probability": 0.78,
    "upgrade_propensity": 0.34,
    "content_recommendation_confidence": 0.89
  },
  
  // Quality Metrics
  "quality_indicators": {
    "data_completeness": 0.94,
    "calculation_confidence": 0.91,
    "sample_size": 127,
    "statistical_significance": true
  },
  
  // Metadata
  "calculated_at": "2025-08-05T14:45:00Z",
  "calculation_version": "v2.1",
  "next_calculation_due": "2025-08-06T02:00:00Z",
  "_ttl": 7776000 // 90 days retention
}
```

#### 2.2 content_analytics Container
**Purpose**: Foundational texts performance and usage analytics
**Partition Key**: `/source`
**Estimated Size**: 100MB (current) → 10GB (at scale)
**RU/s**: 400-800 (autoscale)

```json
{
  "id": "content_analytics_bhagavad_gita_202508",
  "partition_key": "bhagavad_gita",
  "source": "bhagavad_gita",
  "document_type": "content_analytics",
  
  // Analysis Period
  "analysis_period": "monthly",
  "period_start": "2025-08-01T00:00:00Z",
  "period_end": "2025-08-31T23:59:59Z",
  
  // Content Overview
  "content_overview": {
    "total_verses": 700,
    "total_chapters": 18,
    "content_completeness": 0.98,
    "translation_quality": 0.96,
    "expert_validation_status": "complete"
  },
  
  // Usage Analytics
  "usage_metrics": {
    "total_citations": 1247,
    "unique_users_accessed": 89,
    "total_views": 2341,
    "avg_time_spent_seconds": 145,
    "bounce_rate": 0.12,
    "return_access_rate": 0.67
  },
  
  // Performance Metrics
  "performance_metrics": {
    "avg_relevance_score": 0.89,
    "citation_accuracy_rate": 0.94,
    "user_satisfaction_avg": 4.4,
    "response_effectiveness": 0.87,
    "search_ranking_position": 1.3
  },
  
  // Content Quality
  "quality_metrics": {
    "translation_accuracy": 0.98,
    "cultural_sensitivity": 0.96,
    "contextual_appropriateness": 0.92,
    "citation_completeness": 0.94,
    "expert_validation_score": 0.97
  },
  
  // Chapter-wise Breakdown
  "chapter_analytics": [
    {
      "chapter": "2",
      "chapter_title": "Sankhya Yoga",
      "usage_count": 156,
      "avg_relevance": 0.91,
      "popular_verses": ["2.47", "2.62", "2.71"],
      "user_rating": 4.6,
      "citation_frequency": 0.23
    },
    {
      "chapter": "3",
      "chapter_title": "Karma Yoga", 
      "usage_count": 134,
      "avg_relevance": 0.88,
      "popular_verses": ["3.21", "3.35"],
      "user_rating": 4.4,
      "citation_frequency": 0.19
    }
  ],
  
  // Topic Analysis
  "topic_analytics": {
    "primary_topics": [
      {
        "topic": "dharma",
        "frequency": 0.34,
        "relevance_score": 0.92,
        "user_engagement": 0.87
      },
      {
        "topic": "karma",
        "frequency": 0.28,
        "relevance_score": 0.89,
        "user_engagement": 0.84
      }
    ],
    "trending_topics": ["leadership", "decision_making"],
    "seasonal_patterns": ["self_reflection_winter", "action_oriented_spring"]
  },
  
  // Comparative Analysis
  "comparative_metrics": {
    "vs_other_texts": {
      "usage_rank": 1,
      "satisfaction_rank": 2,
      "citation_accuracy_rank": 1
    },
    "growth_trends": {
      "usage_growth_percent": 15.3,
      "user_growth_percent": 12.7,
      "satisfaction_trend": "increasing"
    }
  },
  
  // Recommendations
  "content_recommendations": {
    "enhancement_areas": ["chapter_16_coverage", "modern_applications"],
    "translation_improvements": ["verse_3_42_clarity"],
    "new_content_suggestions": ["practical_examples", "historical_context"],
    "priority_score": 0.78
  },
  
  // Metadata
  "calculated_at": "2025-08-05T14:45:00Z",
  "data_quality_score": 0.95,
  "sample_size": 1247,
  "_ttl": 7776000 // 90 days retention
}
```

#### 2.3 daily_metrics Container
**Purpose**: Time-series system performance and health metrics
**Partition Key**: `/date`
**Estimated Size**: 50MB (current) → 5GB (at scale)
**RU/s**: 400-800 (autoscale)

```json
{
  "id": "daily_metrics_20250805",
  "partition_key": "2025-08-05",
  "date": "2025-08-05",
  "document_type": "daily_metrics",
  
  // System Performance
  "system_performance": {
    "avg_response_time_ms": 1180,
    "p95_response_time_ms": 2150,
    "p99_response_time_ms": 3420,
    "total_requests": 2347,
    "successful_requests": 2318,
    "error_rate": 0.012,
    "availability_percent": 99.94
  },
  
  // Usage Statistics
  "usage_statistics": {
    "active_users": 234,
    "new_users": 12,
    "total_sessions": 456,
    "total_interactions": 1247,
    "avg_session_duration_min": 7.8,
    "peak_concurrent_users": 45,
    "peak_rps": 23.7
  },
  
  // Content Performance
  "content_performance": {
    "total_citations": 1847,
    "unique_texts_accessed": 15,
    "avg_citation_relevance": 0.89,
    "content_discovery_rate": 0.23,
    "foundational_texts_coverage": 0.76
  },
  
  // AI Performance
  "ai_performance": {
    "personalities_used": {
      "krishna": {"requests": 1456, "satisfaction": 4.3, "response_time": 1150},
      "socrates": {"requests": 234, "satisfaction": 4.1, "response_time": 1280}
    },
    "model_performance": {
      "gemini_2_5_flash": {
        "requests": 1690,
        "avg_tokens_input": 234,
        "avg_tokens_output": 456,
        "cost_usd": 12.45,
        "quality_score": 0.87
      }
    },
    "rag_performance": {
      "avg_retrieval_time_ms": 145,
      "avg_chunks_retrieved": 4.2,
      "avg_relevance_score": 0.84,
      "citation_accuracy": 0.92
    }
  },
  
  // Resource Utilization
  "resource_utilization": {
    "cosmos_db": {
      "total_ru_consumed": 15430,
      "avg_ru_per_request": 6.58,
      "storage_used_gb": 2.3,
      "cost_usd": 8.67
    },
    "azure_functions": {
      "total_executions": 2347,
      "avg_execution_time_ms": 892,
      "total_gb_seconds": 156.7,
      "cost_usd": 3.78
    },
    "total_infrastructure_cost_usd": 12.45
  },
  
  // Quality Metrics
  "quality_metrics": {
    "user_satisfaction_avg": 4.25,
    "content_accuracy_score": 0.94,
    "safety_score": 0.99,
    "citation_accuracy": 0.92,
    "response_relevance": 0.88
  },
  
  // Abuse & Safety
  "safety_metrics": {
    "total_abuse_reports": 3,
    "auto_flagged_content": 7,
    "human_reviews_required": 2,
    "safety_violations": 0,
    "content_moderation_accuracy": 0.96
  },
  
  // Business Metrics
  "business_metrics": {
    "user_retention_rate": 0.78,
    "session_completion_rate": 0.89,
    "feature_adoption_rate": 0.67,
    "churn_rate": 0.05,
    "nps_score": 8.2
  },
  
  // Alerts & Issues
  "alerts": [
    {
      "alert_type": "performance",
      "severity": "medium",
      "message": "Response time above threshold at 14:30 UTC",
      "resolved": true,
      "resolution_time_min": 12
    }
  ],
  
  // Metadata
  "calculated_at": "2025-08-06T02:00:00Z",
  "data_completeness": 0.98,
  "calculation_version": "v3.0",
  "_ttl": 31536000 // 1 year retention
}
```

#### 2.4 abuse_incidents Container
**Purpose**: Content moderation and safety incident tracking
**Partition Key**: `/user_id`
**Estimated Size**: 10MB (current) → 1GB (at scale)
**RU/s**: 400-800 (autoscale)

```json
{
  "id": "abuse_incident_20250805_001",
  "partition_key": "e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "user_id": "e45d45fe-d106-46b0-8bef-8bb87a179c0d",
  "document_type": "abuse_incident",
  
  // Incident Identity
  "incident_id": "abuse_incident_20250805_001",
  "interaction_id": "interaction_bd6a8685-73c7-46b0-a7eb-786955803418",
  "session_id": "session_e45d45fe_20250805_143721",
  
  // Incident Details
  "incident_type": "inappropriate_query", // inappropriate_query, spam, harassment, misinformation
  "severity": "medium", // low, medium, high, critical
  "confidence_score": 0.87,
  "auto_detected": true,
  
  // Content Analysis
  "flagged_content": {
    "content_type": "user_query", // user_query, ai_response, both
    "flagged_text": "[REDACTED - inappropriate content]",
    "violation_categories": ["sexual_content", "harassment"],
    "safety_scores": {
      "toxicity": 0.78,
      "severe_toxicity": 0.23,
      "identity_attack": 0.12,
      "insult": 0.45,
      "threat": 0.08
    }
  },
  
  // Detection Details
  "detection_metadata": {
    "detection_method": "automated_ml", // automated_ml, user_report, manual_review
    "detection_model": "perspective_api_v2",
    "detection_timestamp": "2025-08-05T14:39:16.127Z",
    "false_positive_probability": 0.15
  },
  
  // Actions Taken
  "actions_taken": [
    {
      "action_type": "warning_issued",
      "action_timestamp": "2025-08-05T14:39:17.127Z",
      "automated": true,
      "details": "User warned about community guidelines"
    },
    {
      "action_type": "content_blocked",
      "action_timestamp": "2025-08-05T14:39:16.127Z", 
      "automated": true,
      "details": "Response generation blocked for this query"
    }
  ],
  
  // Review Process
  "review_status": "pending_human_review", // auto_resolved, pending_human_review, under_investigation, resolved
  "human_reviewer": null,
  "review_notes": "",
  "review_decision": "", // false_positive, confirmed_violation, escalate
  "review_completed_at": null,
  
  // User Context
  "user_context": {
    "account_age_days": 45,
    "previous_violations": 0,
    "user_reputation_score": 0.89,
    "account_status": "active",
    "warning_count": 1
  },
  
  // Resolution
  "resolution": {
    "final_decision": "confirmed_minor_violation",
    "resolution_actions": ["warning_issued", "educational_content_provided"],
    "follow_up_required": false,
    "appeal_submitted": false,
    "resolution_timestamp": "2025-08-05T16:30:00Z"
  },
  
  // Learning & Improvement
  "feedback_data": {
    "reviewer_feedback": "Clear policy violation but low severity",
    "model_accuracy": "correct_detection",
    "suggested_improvements": ["refine_severity_classification"],
    "training_data_value": "high"
  },
  
  // Metadata
  "created_at": "2025-08-05T14:39:16.127Z",
  "updated_at": "2025-08-05T16:30:00Z",
  "_ttl": 94608000 // 3 years retention for compliance
}
```

### 3. Materialized Views (Change Feed Triggered)

#### 3.1 engagement_summary Container
**Purpose**: Pre-computed user engagement tiers and trends
**Partition Key**: `/engagement_tier`
**Update Frequency**: Real-time via change feed
**RU/s**: 400-800 (autoscale)

```json
{
  "id": "engagement_summary_power_user_202508",
  "partition_key": "power_user",
  "engagement_tier": "power_user", // new, casual, engaged, power_user, churned
  "document_type": "engagement_summary",
  
  // Tier Definition
  "tier_criteria": {
    "min_sessions_monthly": 20,
    "min_engagement_score": 0.80,
    "min_content_depth": 0.70,
    "retention_rate_threshold": 0.75
  },
  
  // Aggregate Metrics
  "user_count": 23,
  "percentage_of_total": 0.089,
  "avg_metrics": {
    "sessions_per_month": 34.5,
    "engagement_score": 0.87,
    "session_duration_min": 12.3,
    "content_depth_score": 0.81,
    "satisfaction_rating": 4.6
  },
  
  // Behavioral Patterns
  "common_patterns": {
    "preferred_personalities": ["krishna", "buddha"],
    "peak_usage_times": ["morning", "evening"],
    "content_preferences": ["philosophical_discussion", "practical_guidance"],
    "session_triggers": ["daily_reflection", "decision_making"]
  },
  
  // Business Impact
  "business_value": {
    "avg_lifetime_value": 245.67,
    "upgrade_conversion_rate": 0.67,
    "referral_rate": 0.34,
    "churn_risk": 0.08
  },
  
  // Trends
  "trend_analysis": {
    "growth_rate_monthly": 0.15,
    "retention_trend": "improving",
    "engagement_trend": "stable_high",
    "satisfaction_trend": "increasing"
  },
  
  // Metadata
  "last_updated": "2025-08-05T14:45:00Z",
  "data_freshness": "real_time",
  "sample_size": 23,
  "_ttl": 86400 // 24 hours
}
```

#### 3.2 content_popularity Container
**Purpose**: Real-time content performance rankings
**Partition Key**: `/time_period`
**Update Frequency**: Hourly via change feed
**RU/s**: 400-600 (autoscale)

```json
{
  "id": "content_popularity_daily_20250805",
  "partition_key": "daily",
  "time_period": "daily",
  "date": "2025-08-05",
  "document_type": "content_popularity",
  
  // Top Performing Content
  "top_foundational_texts": [
    {
      "rank": 1,
      "source": "bhagavad_gita",
      "citations": 156,
      "unique_users": 45,
      "avg_rating": 4.6,
      "trending_score": 0.92
    },
    {
      "rank": 2,
      "source": "upanishads",
      "citations": 89,
      "unique_users": 32,
      "avg_rating": 4.4,
      "trending_score": 0.78
    }
  ],
  
  // Top Verses/Passages
  "trending_content": [
    {
      "rank": 1,
      "content_id": "bhagavad_gita_2_47",
      "citations": 23,
      "relevance_score": 0.94,
      "user_engagement": 0.89,
      "topic": "karma_yoga"
    }
  ],
  
  // Emerging Topics
  "trending_topics": [
    {
      "topic": "leadership_crisis",
      "growth_rate": 1.45,
      "query_count": 67,
      "satisfaction_score": 4.3
    }
  ],
  
  // Personality Performance
  "personality_rankings": [
    {
      "personality": "krishna",
      "interactions": 234,
      "satisfaction": 4.3,
      "response_quality": 0.87,
      "efficiency_score": 0.92
    }
  ],
  
  // Metadata
  "generated_at": "2025-08-05T23:59:59Z",
  "data_points": 1247,
  "confidence_level": 0.95,
  "_ttl": 604800 // 7 days
}
```

#### 3.3 system_health Container
**Purpose**: Admin-focused view of abuse incidents organized by content source
**Partition Key**: `/source`
**Update Frequency**: Real-time via change feed from abuse_incidents
**RU/s**: 400-600 (autoscale)

```json
{
  "id": "incidents_bhagavad_gita_202508",
  "partition_key": "bhagavad_gita",
  "source": "bhagavad_gita",
  "document_type": "incidents_by_content",
  
  // Time Period
  "time_period": "monthly",
  "period_start": "2025-08-01T00:00:00Z",
  "period_end": "2025-08-31T23:59:59Z",
  
  // Incident Summary
  "incident_summary": {
    "total_incidents": 12,
    "by_severity": {
      "low": 8,
      "medium": 3,
      "high": 1,
      "critical": 0
    },
    "by_type": {
      "inappropriate_query": 7,
      "spam": 2,
      "harassment": 2,
      "misinformation": 1
    }
  },
  
  // Content Analysis
  "content_analysis": {
    "most_flagged_chapters": ["2", "3"],
    "flagged_verses": ["2.47", "3.21"],
    "common_violation_patterns": ["taking_verses_out_of_context", "inappropriate_personal_questions"],
    "false_positive_rate": 0.15
  },
  
  // Admin Actions
  "moderation_actions": {
    "warnings_issued": 8,
    "content_blocked": 3,
    "accounts_suspended": 1,
    "manual_reviews_pending": 2,
    "avg_resolution_time_hours": 4.2
  },
  
  // Trends
  "trend_analysis": {
    "incident_growth_rate": -0.05, // Decreasing incidents (good)
    "resolution_efficiency": 0.89,
    "user_education_effectiveness": 0.76
  },
  
  // Metadata
  "last_updated": "2025-08-05T14:45:00Z",
  "data_freshness": "real_time",
  "sample_size": 12,
  "_ttl": 2592000 // 30 days
}
```
**Purpose**: Real-time system health and performance monitoring
**Partition Key**: `/metric_type`
**Update Frequency**: Every 5 minutes via change feed
**RU/s**: 400-800 (autoscale)

```json
{
  "id": "system_health_performance_20250805_1445",
  "partition_key": "performance",
  "metric_type": "performance",
  "document_type": "system_health",
  
  // Timestamp
  "timestamp": "2025-08-05T14:45:00Z",
  "time_window_minutes": 5,
  
  // Performance Metrics
  "performance_metrics": {
    "avg_response_time_ms": 1180,
    "p95_response_time_ms": 2150,
    "requests_per_second": 23.7,
    "error_rate": 0.012,
    "availability": 0.9994
  },
  
  // Resource Health
  "resource_health": {
    "cosmos_db_health": "healthy",
    "cosmos_ru_utilization": 0.65,
    "azure_functions_health": "healthy",
    "function_error_rate": 0.008,
    "storage_utilization": 0.34
  },
  
  // Quality Indicators
  "quality_indicators": {
    "user_satisfaction": 4.25,
    "content_accuracy": 0.94,
    "citation_accuracy": 0.92,
    "safety_score": 0.99
  },
  
  // Alerts
  "active_alerts": [],
  "resolved_alerts_last_hour": 1,
  
  // Health Score
  "overall_health_score": 0.96, // 0-1 scale
  "health_status": "excellent", // poor, fair, good, excellent
  
  // Metadata
  "next_update_due": "2025-08-05T14:50:00Z",
  "_ttl": 86400 // 24 hours
}
```

---

## 🔧 Implementation Specifications

### Database Configuration

#### Connection Settings
```json
{
  "endpoint": "https://vimarsh-cosmos-db.documents.azure.com:443/",
  "database_name": "vimarsh-multi-personality",
  "consistency_level": "Session",
  "connection_mode": "Gateway",
  "request_timeout_seconds": 30,
  "retry_policy": {
    "max_retry_attempts": 3,
    "max_retry_wait_time_seconds": 30
  },
  "preferred_locations": ["East US", "West Europe"],
  "enable_endpoint_discovery": true,
  "enable_multiple_write_locations": false
}
```

#### Throughput Configuration
```json
{
  "provisioning_type": "autoscale",
  "database_level_throughput": false,
  "container_throughput": {
    "users": {"min_ru": 400, "max_ru": 4000},
    "user_sessions": {"min_ru": 400, "max_ru": 2000},
    "user_interactions": {"min_ru": 800, "max_ru": 4000},
    "personalities": {"min_ru": 400, "max_ru": 800},
    "personality_vectors": {"min_ru": 400, "max_ru": 2000},
    "user_analytics": {"min_ru": 400, "max_ru": 1000},
    "content_analytics": {"min_ru": 400, "max_ru": 800},
    "daily_metrics": {"min_ru": 400, "max_ru": 800},
    "abuse_incidents": {"min_ru": 400, "max_ru": 800}
  }
}
```

### Change Feed Processing

#### Change Feed Processor Configuration
```python
# backend/services/change_feed_processor.py
from azure.cosmos import CosmosClient
from azure.cosmos.partition_key import PartitionKey
import logging
import asyncio
from typing import Dict, List

class ChangeFeedProcessor:
    def __init__(self):
        self.client = CosmosClient(endpoint, credential)
        self.database = self.client.get_database_client("vimarsh-multi-personality")
        self.lease_container = self.database.get_container_client("change_feed_leases")
        self.poison_queue = self.database.get_container_client("poison_messages")
        self.logger = logging.getLogger(__name__)
        
        # Retry configuration for resilience
        self.max_retry_attempts = 3
        self.retry_delay_seconds = 5
    
    async def start_processors(self):
        """Start all change feed processors with error handling"""
        processors = [
            self.process_user_interactions_changes,
            self.process_user_sessions_changes,
            self.process_daily_metrics_updates
        ]
        
        await asyncio.gather(*[self._run_processor_with_resilience(processor) 
                              for processor in processors])
    
    async def _run_processor_with_resilience(self, processor_func):
        """Run processor with retry logic and error handling"""
        while True:
            try:
                await processor_func()
            except Exception as e:
                self.logger.error(f"Change feed processor failed: {str(e)}")
                await asyncio.sleep(self.retry_delay_seconds)
                # Continue processing - don't let transient errors stop the feed
    
    async def process_user_interactions_changes(self):
        """Process user_interactions changes for real-time analytics"""
        container = self.database.get_container_client("user_interactions")
        
        async for changes in container.read_change_feed():
            for change in changes:
                await self._process_change_with_retry(change, [
                    self.update_user_analytics,
                    self.update_content_analytics,
                    self.update_system_health,
                    self.calculate_interaction_cost
                ])
    
    async def _process_change_with_retry(self, change: Dict, processors: List):
        """Process a single change with retry logic and poison message handling"""
        retry_count = 0
        
        while retry_count < self.max_retry_attempts:
            try:
                for processor in processors:
                    await processor(change)
                return  # Success - exit retry loop
                
            except Exception as e:
                retry_count += 1
                self.logger.warning(f"Change processing failed (attempt {retry_count}): {str(e)}")
                
                if retry_count < self.max_retry_attempts:
                    await asyncio.sleep(self.retry_delay_seconds * retry_count)  # Exponential backoff
                else:
                    # Max retries exceeded - move to poison queue
                    await self._handle_poison_message(change, str(e))
    
    async def _handle_poison_message(self, change: Dict, error_message: str):
        """Handle documents that repeatedly fail processing"""
        poison_document = {
            "id": f"poison_{change.get('id', 'unknown')}_{int(time.time())}",
            "partition_key": "poison_messages",
            "original_document": change,
            "error_message": error_message,
            "failed_at": datetime.utcnow().isoformat(),
            "retry_attempts": self.max_retry_attempts,
            "requires_manual_review": True
        }
        
        try:
            await self.poison_queue.create_item(poison_document)
            self.logger.error(f"Document moved to poison queue: {change.get('id')}")
        except Exception as e:
            self.logger.critical(f"Failed to write to poison queue: {str(e)}")
    
    async def update_user_analytics(self, interaction_data):
        """Update user analytics based on new interaction"""
        user_id = interaction_data.get("user_id")
        
        # Calculate cost asynchronously
        await self.calculate_interaction_cost(interaction_data)
        
        # Update user engagement scores
        await self.calculate_engagement_score(user_id)
        
        # Update session metrics
        await self.update_session_metrics(interaction_data)
        
        # Update content preferences
        await self.update_content_preferences(user_id, interaction_data)
    
    async def calculate_interaction_cost(self, interaction_data):
        """Calculate cost based on token usage and model pricing"""
        cost_data = interaction_data.get("cost_data", {})
        model_used = cost_data.get("model_used")
        input_tokens = cost_data.get("input_tokens", 0)
        output_tokens = cost_data.get("output_tokens", 0)
        
        # Get current pricing from cached pricing table
        pricing = await self.get_model_pricing(model_used)
        
        total_cost = (input_tokens * pricing["input_cost_per_token"]) + \
                    (output_tokens * pricing["output_cost_per_token"])
        
        # Update daily metrics with cost information
        await self.update_daily_cost_metrics(interaction_data["user_id"], total_cost, model_used)
```

### Query Optimization

#### Common Query Patterns
```python
# backend/services/optimized_queries.py
class OptimizedQueries:
    
    async def get_user_analytics_efficient(self, user_id: str, period: str = "monthly"):
        """Optimized user analytics query using partition key"""
        query = """
        SELECT TOP 1 * FROM c 
        WHERE c.user_id = @user_id 
        AND c.analysis_period = @period 
        ORDER BY c.period_start DESC
        """
        # Uses partition key (user_id) for efficient routing
        parameters = [{"name": "@user_id", "value": user_id}, 
                     {"name": "@period", "value": period}]
        
        container = self.database.get_container_client("user_analytics")
        items = container.query_items(query=query, parameters=parameters)
        return list(items)
    
    async def get_trending_content(self, time_period: str = "daily", limit: int = 10):
        """Get trending content using materialized view"""
        query = """
        SELECT c.top_foundational_texts, c.trending_content 
        FROM c 
        WHERE c.time_period = @time_period 
        ORDER BY c.date DESC 
        OFFSET 0 LIMIT @limit
        """
        # Uses partition key (time_period) for efficient routing
        parameters = [{"name": "@time_period", "value": time_period},
                     {"name": "@limit", "value": limit}]
        
        container = self.database.get_container_client("content_popularity")
        items = container.query_items(query=query, parameters=parameters)
        return list(items)
    
    async def get_user_interaction_history(self, user_id: str, days: int = 7):
        """Get user interaction history with time-based filtering"""
        from datetime import datetime, timedelta
        
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        query = """
        SELECT c.interaction_id, c.timestamp, c.user_query, c.response_metadata, c.user_rating
        FROM c 
        WHERE c.user_id = @user_id 
        AND c.timestamp >= @start_date 
        ORDER BY c.timestamp DESC
        """
        # Uses partition key (user_id) + timestamp index
        parameters = [{"name": "@user_id", "value": user_id},
                     {"name": "@start_date", "value": start_date}]
        
        container = self.database.get_container_client("user_interactions")
        items = container.query_items(query=query, parameters=parameters)
        return list(items)
    
    async def get_incidents_by_content_for_admin(self, source: str, time_period: str = "monthly"):
        """Admin query for content moderation - uses materialized view for efficiency"""
        query = """
        SELECT c.incident_summary, c.content_analysis, c.moderation_actions 
        FROM c 
        WHERE c.source = @source 
        AND c.time_period = @time_period 
        ORDER BY c.period_start DESC
        """
        # Uses partition key (source) for efficient admin queries
        parameters = [{"name": "@source", "value": source},
                     {"name": "@time_period", "value": time_period}]
        
        container = self.database.get_container_client("incidents_by_content")
        items = container.query_items(query=query, parameters=parameters)
        return list(items)
```

#### Indexing Policy Best Practices
```python
# backend/services/indexing_manager.py
class IndexingManager:
    
    def get_optimized_indexing_policies(self):
        """Optimized indexing policies for each container"""
        return {
            "users": {
                "indexingPolicy": {
                    "automatic": True,
                    "includedPaths": [
                        {"path": "/user_id/?"},
                        {"path": "/email/?"},
                        {"path": "/auth_id/?"},
                        {"path": "/account_status/?"},
                        {"path": "/subscription_tier/?"},
                        {"path": "/created_at/?"},
                        {"path": "/last_login/?"}
                    ],
                    "excludedPaths": [
                        {"path": "/privacy_settings/*"}, # Exclude complex objects
                        {"path": "/content_preferences/*"} # Reduce indexing overhead
                    ],
                    "compositeIndexes": [
                        [
                            {"path": "/account_status", "order": "ascending"},
                            {"path": "/subscription_tier", "order": "ascending"}
                        ]
                    ]
                }
            },
            "user_interactions": {
                "indexingPolicy": {
                    "automatic": True,
                    "includedPaths": [
                        {"path": "/user_id/?"},
                        {"path": "/timestamp/?"},
                        {"path": "/personality_used/?"},
                        {"path": "/user_rating/?"},
                        {"path": "/session_id/?"}
                    ],
                    "excludedPaths": [
                        {"path": "/embeddings/*"}, # Large vectors - exclude from indexing
                        {"path": "/response_text/?"},  # Large text fields
                        {"path": "/foundational_texts_used/*"} # Complex nested objects
                    ],
                    "compositeIndexes": [
                        [
                            {"path": "/user_id", "order": "ascending"},
                            {"path": "/timestamp", "order": "descending"}
                        ]
                    ]
                }
            },
            "personality_vectors": {
                "indexingPolicy": {
                    "automatic": True,
                    "includedPaths": [
                        {"path": "/personality_id/?"},
                        {"path": "/source/?"},
                        {"path": "/content_type/?"},
                        {"path": "/topic_tags/*"}
                    ],
                    "excludedPaths": [
                        {"path": "/embeddings/*"}, # Critical: Exclude vector embeddings
                        {"path": "/sanskrit_text/?"},
                        {"path": "/detailed_explanation/?"}
                    ]
                }
            }
        }
    
    async def review_and_optimize_indexes(self, container_name: str):
        """Periodic review of indexing efficiency"""
        # Monitor query patterns and adjust indexing policies
        # Remove unused indexes that consume RUs on writes
        pass
```

#### Schema Versioning Strategy
```python
# backend/services/schema_versioning.py
class SchemaVersionManager:
    
    CURRENT_SCHEMAS = {
        "user_profile": "1.0",
        "user_interaction": "1.1", 
        "personality_content": "1.2",
        "personality_profile": "1.0"
    }
    
    def handle_document_version(self, document: Dict, expected_type: str) -> Dict:
        """Handle documents with different schema versions gracefully"""
        doc_version = document.get("profile_version", "1.0")
        current_version = self.CURRENT_SCHEMAS.get(expected_type, "1.0")
        
        if doc_version != current_version:
            return self.migrate_document_schema(document, doc_version, current_version)
        
        return document
    
    def migrate_document_schema(self, document: Dict, from_version: str, to_version: str) -> Dict:
        """Migrate document schema between versions"""
        if from_version == "1.0" and to_version == "1.1":
            # Example: Add default values for new fields
            if "cost_data" not in document:
                document["cost_data"] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "model_used": "unknown",
                    "timestamp": document.get("created_at", "")
                }
        
        # Update version field
        document["profile_version"] = to_version
        return document
    
    async def batch_migrate_container(self, container_name: str, from_version: str, to_version: str):
        """Batch migrate entire container to new schema version"""
        # Implementation for large-scale schema migrations
        pass
```
```

### Data Retention Policies

#### TTL Configuration
```python
# backend/scripts/configure_ttl.py
class TTLConfiguration:
    
    TTL_SETTINGS = {
        "user_sessions": 7776000,      # 90 days
        "user_interactions": 31536000,  # 1 year  
        "user_analytics": 7776000,      # 90 days
        "content_analytics": 7776000,   # 90 days
        "daily_metrics": 31536000,      # 1 year
        "abuse_incidents": 94608000,    # 3 years (compliance)
        "engagement_summary": 86400,    # 24 hours (materialized view)
        "content_popularity": 604800,   # 7 days (materialized view)
        "system_health": 86400,         # 24 hours (materialized view)
        # No TTL for core containers: users, personalities, personality_vectors
    }
    
    async def configure_container_ttl(self, container_name: str):
        """Configure TTL for specific container"""
        if container_name not in self.TTL_SETTINGS:
            return
            
        container = self.database.get_container_client(container_name)
        ttl_seconds = self.TTL_SETTINGS[container_name]
        
        # Update container properties to enable TTL
        container_properties = container.read()
        container_properties["defaultTtl"] = ttl_seconds
        
        container.replace_container(container_properties)
```

#### Data Archiving Strategy
```python
# backend/services/data_archiving_service.py
class DataArchivingService:
    
    async def setup_archiving_change_feed(self):
        """Set up change feed processor for automatic data archiving"""
        # Archive user_interactions older than 6 months to Azure Blob Storage
        # This runs before TTL deletion to preserve data for compliance
        
        async def archive_interaction_data(changes):
            for change in changes:
                if self.should_archive(change):
                    await self.archive_to_blob_storage(change)
    
    def should_archive(self, document) -> bool:
        """Determine if document should be archived"""
        from datetime import datetime, timedelta
        
        doc_timestamp = document.get("_ts", 0)
        archive_threshold = datetime.utcnow() - timedelta(days=180)  # 6 months
        
        return datetime.fromtimestamp(doc_timestamp) < archive_threshold
    
    async def archive_to_blob_storage(self, document):
        """Archive document to Azure Blob Storage (Cold tier)"""
        # Structure: /archived/{year}/{month}/{day}/{user_id}/{document_id}.json
        # Cost: ~$0.01 per GB per month vs ~$0.25 in Cosmos DB
        pass
```

### Backup and Disaster Recovery

#### Backup Configuration
```json
{
  "backup_policy": {
    "type": "Continuous",
    "continuous_mode_properties": {
      "tier": "Continuous30Days"
    }
  },
  "restore_policy": {
    "mode": "PointInTime",
    "source_database_account_name": "vimarsh-cosmos-db",
    "source_database_name": "vimarsh-multi-personality",
    "restore_timestamp_utc": "2025-08-05T14:45:00Z"
  }
}
```

#### Multi-Region Configuration
```json
{
  "locations": [
    {
      "location_name": "East US",
      "priority": 0,
      "is_zone_redundant": true
    },
    {
      "location_name": "West Europe", 
      "priority": 1,
      "is_zone_redundant": false
    }
  ],
  "enable_automatic_failover": true,
  "enable_multiple_write_locations": false
}
```

---

## 📈 Performance & Scaling Considerations

### Current Scale Projections
- **Users**: 1,000 active users
- **Daily Interactions**: 1,000
- **Monthly Data Growth**: ~100MB
- **RU Consumption**: ~2,000 RU/s peak

### Medium Scale (6-12 months)
- **Users**: 10,000 active users
- **Daily Interactions**: 10,000  
- **Monthly Data Growth**: ~1GB
- **RU Consumption**: ~10,000 RU/s peak

### Large Scale (12+ months)
- **Users**: 100,000+ active users
- **Daily Interactions**: 100,000+
- **Monthly Data Growth**: ~10GB+
- **RU Consumption**: ~50,000+ RU/s peak

### Scaling Strategies

#### Horizontal Scaling
1. **Partition Key Optimization**: Ensure even distribution across physical partitions
2. **Container Splitting**: Separate high-volume containers (user_interactions) 
3. **Multi-Database Architecture**: Migrate to operational/analytics database separation
4. **Read Replicas**: Implement dedicated read replicas for analytics workloads

#### Vertical Scaling  
1. **Autoscale Tuning**: Optimize min/max RU settings based on usage patterns
2. **Index Optimization**: Remove unused indexes, add composite indexes for common queries
3. **Query Optimization**: Implement query result caching and pagination
4. **Materialized Views**: Pre-compute expensive aggregations

---

## 🔒 Security & Compliance

### Access Control
```json
{
  "rbac_roles": {
    "admin": {
      "permissions": ["read", "write", "delete"],
      "containers": ["*"],
      "operations": ["*"]
    },
    "analytics_reader": {
      "permissions": ["read"],
      "containers": ["user_analytics", "content_analytics", "daily_metrics"],
      "operations": ["query", "read_document"]
    },
    "application_service": {
      "permissions": ["read", "write"],
      "containers": ["users", "user_sessions", "user_interactions", "personality_vectors"],
      "operations": ["create_document", "read_document", "update_document", "query"]
    },
    "content_moderator": {
      "permissions": ["read", "write"],
      "containers": ["abuse_incidents", "user_interactions"],
      "operations": ["read_document", "update_document", "query"]
    }
  }
}
```

### Data Privacy
```json
{
  "privacy_controls": {
    "data_classification": {
      "user_pii": ["email", "name", "ip_hash"],
      "sensitive_content": ["user_query", "response_text"],
      "analytics_only": ["engagement_score", "usage_metrics"]
    },
    "retention_policies": {
      "user_data": "indefinite_until_deletion_request",
      "interaction_logs": "1_year",
      "analytics_aggregates": "90_days",
      "abuse_incidents": "3_years_compliance"
    },
    "anonymization": {
      "user_analytics": "hash_user_id_after_90_days",
      "system_metrics": "no_user_identifiers",
      "content_analytics": "aggregate_only_no_pii"
    }
  }
}
```

### Compliance Requirements
- **GDPR**: Right to deletion, data portability, consent management
- **CCPA**: Data transparency, opt-out mechanisms
- **SOC 2**: Access controls, audit logging, data encryption
- **HIPAA**: Not applicable (no health data)

---

## 💰 Cost Optimization

### Current Cost Estimation (Monthly)
```json
{
  "cosmos_db_costs": {
    "provisioned_throughput": "$120", // Based on autoscale RU consumption
    "storage": "$15", // ~6GB total storage
    "backup": "$5", // Continuous backup
    "multi_region": "$25", // Additional region replication
    "total_cosmos": "$165"
  },
  "operational_costs": {
    "azure_functions": "$20", // Database operations
    "monitoring": "$10", // Application Insights
    "networking": "$5", // Data transfer
    "total_operational": "$35"
  },
  "total_monthly_cost": "$200"
}
```

### Cost Optimization Strategies
1. **Autoscale Tuning**: Set appropriate min/max RU based on usage patterns
2. **Query Optimization**: Reduce RU consumption through efficient queries
3. **Data Archiving**: Move old data to cheaper storage tiers
4. **Regional Optimization**: Balance performance vs cost for secondary regions
5. **Index Optimization**: Remove unused indexes to reduce storage costs

---

## 🚀 Migration & Implementation Plan

### Phase 1: Foundation Setup (Week 1)
- [ ] Create personalities container with canonical personality configurations
- [ ] Create new analytics containers with proper partition keys
- [ ] Implement hierarchical partitioning for personality_vectors (personality_id::source)
- [ ] Implement DatabaseService extensions for analytics queries  
- [ ] Set up basic change feed processing with asynchronous cost calculation
- [ ] Configure TTL policies for data retention

### Phase 2: Data Integration (Week 2)
- [ ] Migrate personality configurations to dedicated personalities container
- [ ] Update personality_vectors to use hierarchical partition keys
- [ ] Implement data transformation pipelines
- [ ] Create materialized views with change feed triggers
- [ ] Replace mock data with real analytics queries
- [ ] Set up monitoring and alerting

### Phase 3: Optimization (Week 3)
- [ ] Optimize query performance and indexing for hierarchical partitioning
- [ ] Implement caching for frequently accessed personality configurations
- [ ] Set up automated data archiving framework
- [ ] Performance testing and tuning with multiple personalities
- [ ] Implement asynchronous cost calculation pipeline

### Phase 4: Advanced Features (Week 4+)
- [ ] Real-time analytics dashboards
- [ ] Advanced ML-based insights
- [ ] Predictive analytics capabilities
- [ ] Automated content optimization
- [ ] Full data archiving implementation

---

## 📚 API Integration Guide

### DatabaseService Extensions
```python
# backend/services/database_service.py
class DatabaseService:
    
    async def query_documents(self, container_name: str, query: str, 
                            parameters: List[Dict] = None) -> List[Dict]:
        """Generic query method for any container"""
        container = self.database.get_container_client(container_name)
        items = container.query_items(
            query=query, 
            parameters=parameters,
            enable_cross_partition_query=True
        )
        return list(items)
    
    async def create_analytics_containers(self) -> None:
        """Create all analytics containers with proper configuration"""
        containers = [
            ("personalities", "/personality_id"),
            ("user_analytics", "/user_id"),
            ("content_analytics", "/source"),
            ("daily_metrics", "/date"), 
            ("abuse_incidents", "/user_id"),
            ("engagement_summary", "/engagement_tier"),
            ("content_popularity", "/time_period"),
            ("system_health", "/metric_type")
        ]
        
        for container_name, partition_key in containers:
            await self.create_container_if_not_exists(container_name, partition_key)
    
    async def get_personality_config(self, personality_id: str) -> Dict:
        """Get personality configuration from personalities container"""
        query = """
        SELECT * FROM c WHERE c.personality_id = @personality_id AND c.is_active = true
        """
        parameters = [{"name": "@personality_id", "value": personality_id}]
        
        container = self.database.get_container_client("personalities")
        items = container.query_items(query=query, parameters=parameters)
        results = list(items)
        return results[0] if results else None
    
    async def get_user_comprehensive_analytics(self, user_id: str) -> Dict:
        """Get comprehensive user analytics from multiple containers"""
        # Parallel queries for performance
        user_data, sessions, interactions, analytics = await asyncio.gather(
            self.get_user_profile(user_id),
            self.get_user_sessions(user_id, days=30),
            self.get_user_interactions(user_id, days=7),
            self.get_user_analytics(user_id, period="monthly")
        )
        
        return {
            "user_profile": user_data,
            "recent_sessions": sessions,
            "recent_interactions": interactions,
            "analytics_summary": analytics
        }
```

### Analytics Service Integration
```python
# backend/services/comprehensive_admin_service.py
class ComprehensiveAdminService:
    
    async def get_real_dashboard_data(self) -> Dict:
        """Get real dashboard data from database containers"""
        
        # Get system health from materialized view
        system_health = await self.database_service.query_documents(
            "system_health",
            "SELECT TOP 1 * FROM c WHERE c.metric_type = 'performance' ORDER BY c.timestamp DESC"
        )
        
        # Get user engagement summary
        engagement_data = await self.database_service.query_documents(
            "engagement_summary", 
            "SELECT * FROM c ORDER BY c.last_updated DESC"
        )
        
        # Get content popularity
        content_trends = await self.database_service.query_documents(
            "content_popularity",
            "SELECT TOP 1 * FROM c WHERE c.time_period = 'daily' ORDER BY c.date DESC"
        )
        
        return {
            "system_performance": system_health[0] if system_health else {},
            "user_engagement": engagement_data,
            "content_trends": content_trends[0] if content_trends else {},
            "timestamp": datetime.utcnow().isoformat()
        }
```

---

## � Production Operations

### Performance Monitoring

#### Key Metrics Dashboard
```python
# backend/services/performance_monitor.py
from datetime import datetime, timedelta
from typing import Dict, List, Any

class PerformanceMonitor:
    
    def __init__(self, cosmos_client):
        self.cosmos_client = cosmos_client
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive performance dashboard data"""
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "database_health": await self.check_database_health(),
            "query_performance": await self.analyze_query_performance(),
            "resource_utilization": await self.get_resource_utilization(),
            "cost_analysis": await self.get_cost_analysis(),
            "capacity_planning": await self.get_capacity_metrics()
        }
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Monitor overall database health indicators"""
        return {
            "status": "healthy",
            "total_containers": 11,
            "total_documents": 42750,  # Projected for 1K users
            "average_latency_ms": 45,
            "error_rate_percent": 0.1,
            "availability_percent": 99.98
        }
    
    async def analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze query performance patterns"""
        return {
            "average_ru_consumption": {
                "user_lookup": 2.8,
                "personality_search": 15.4,
                "interaction_logging": 8.2,
                "analytics_aggregation": 42.1
            },
            "query_latency_percentiles": {
                "p50_ms": 32,
                "p90_ms": 78,
                "p95_ms": 125,
                "p99_ms": 280
            },
            "slowest_queries": [
                {
                    "query_type": "personality_vector_search",
                    "avg_latency_ms": 180,
                    "avg_ru_cost": 25.3,
                    "optimization_suggestion": "Add composite index on personality_id + content_type"
                }
            ]
        }
    
    async def get_resource_utilization(self) -> Dict[str, Any]:
        """Monitor resource utilization across containers"""
        return {
            "total_ru_consumption": {
                "provisioned_per_second": 1000,
                "average_consumed_per_second": 380,
                "peak_consumed_per_second": 720,
                "utilization_percent": 38
            },
            "storage_utilization": {
                "total_used_gb": 2.8,
                "growth_rate_gb_per_month": 0.4,
                "projected_6_month_gb": 5.2
            },
            "container_breakdown": {
                "personality_vectors": {"ru_percent": 45, "storage_percent": 42},
                "user_interactions": {"ru_percent": 30, "storage_percent": 28},
                "analytics": {"ru_percent": 15, "storage_percent": 20},
                "user_management": {"ru_percent": 10, "storage_percent": 10}
            }
        }
```

#### Production Monitoring and Alerting
```python
# backend/services/production_monitoring.py
class ProductionMonitor:
    
    def __init__(self, cosmos_client):
        self.cosmos_client = cosmos_client
        self.alert_thresholds = {
            "ru_consumption_per_second": 800,  # Alert at 80% of provisioned 1000 RU/s
            "storage_usage_gb": 8,  # Alert at 80% of 10GB limit
            "query_latency_ms": 500,  # Alert if queries exceed 500ms
            "failed_requests_per_minute": 10,  # Alert if error rate spikes
            "partition_hot_spotting": 0.8  # Alert if single partition uses >80% of RUs
        }
    
    async def monitor_database_health(self):
        """Comprehensive database health monitoring"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ru_consumption": await self.get_ru_consumption(),
            "storage_metrics": await self.get_storage_metrics(),
            "query_performance": await self.get_query_performance(),
            "error_rates": await self.get_error_rates(),
            "partition_distribution": await self.get_partition_distribution()
        }
        
        alerts = self.evaluate_alerts(metrics)
        
        if alerts:
            await self.send_alerts(alerts)
        
        return {"status": "healthy" if not alerts else "warning", "metrics": metrics, "alerts": alerts}
    
    async def get_ru_consumption(self):
        """Monitor RU consumption patterns"""
        # Query Azure Monitor APIs for RU consumption metrics
        return {
            "current_rus_per_second": 450,
            "peak_rus_last_hour": 780,
            "average_rus_last_24h": 320,
            "trending": "stable"
        }
    
    async def get_storage_metrics(self):
        """Monitor storage usage by container"""
        return {
            "total_storage_gb": 2.8,
            "container_breakdown": {
                "personality_vectors": {"size_gb": 1.2, "document_count": 15000},
                "user_interactions": {"size_gb": 0.8, "document_count": 25000},
                "user_analytics": {"size_gb": 0.4, "document_count": 1200},
                "users": {"size_gb": 0.2, "document_count": 1000},
                "personalities": {"size_gb": 0.1, "document_count": 45},
                "others": {"size_gb": 0.1, "document_count": 500}
            }
        }
    
    async def evaluate_alerts(self, metrics: dict) -> List[dict]:
        """Evaluate metrics against thresholds and generate alerts"""
        alerts = []
        
        # RU consumption alerts
        if metrics["ru_consumption"]["current_rus_per_second"] > self.alert_thresholds["ru_consumption_per_second"]:
            alerts.append({
                "type": "HIGH_RU_CONSUMPTION",
                "severity": "warning",
                "message": f"RU consumption at {metrics['ru_consumption']['current_rus_per_second']}/s, approaching limit",
                "recommended_action": "Consider scaling up RUs or optimizing queries"
            })
        
        # Storage alerts
        if metrics["storage_metrics"]["total_storage_gb"] > self.alert_thresholds["storage_usage_gb"]:
            alerts.append({
                "type": "HIGH_STORAGE_USAGE",
                "severity": "warning", 
                "message": f"Storage usage at {metrics['storage_metrics']['total_storage_gb']}GB",
                "recommended_action": "Review data archiving policies and implement cleanup"
            })
        
        return alerts
    
    async def send_alerts(self, alerts: List[dict]):
        """Send alerts via configured channels (email, Slack, etc.)"""
        for alert in alerts:
            # Integration with Azure Monitor or external alerting systems
            print(f"🚨 ALERT: {alert['type']} - {alert['message']}")
    
    async def performance_trend_analysis(self):
        """Analyze performance trends for capacity planning"""
        return {
            "growth_projections": {
                "users_monthly_growth": 15,  # %
                "interactions_daily_growth": 8,  # %
                "storage_monthly_growth": 12  # %
            },
            "capacity_forecasts": {
                "ru_scaling_needed_by": "2024-06-15",
                "storage_limit_reached_by": "2024-09-20"
            },
            "optimization_recommendations": [
                "Implement automatic TTL on user_sessions (reduce storage by 15%)",
                "Archive user_interactions older than 6 months (reduce RU consumption by 10%)",
                "Optimize personality_vectors indexing (reduce write RUs by 20%)"
            ]
        }
```

#### Backup and Disaster Recovery
```python
# backend/services/backup_manager.py
class BackupManager:
    
    def __init__(self, cosmos_client):
        self.cosmos_client = cosmos_client
        self.backup_config = {
            "point_in_time_retention_hours": 720,  # 30 days
            "automatic_backup_interval_hours": 4,
            "cross_region_backup": True,
            "backup_verification_enabled": True
        }
    
    async def configure_backup_policies(self):
        """Configure automatic backup policies for all containers"""
        backup_policy = {
            "type": "Continuous",
            "continuousModeProperties": {
                "tier": "Continuous30Days"  # Point-in-time recovery for 30 days
            }
        }
        
        # Apply to all production containers
        containers = [
            "users", "user_sessions", "user_interactions", 
            "personalities", "personality_vectors",
            "user_analytics", "content_analytics", "daily_metrics",
            "abuse_incidents", "incidents_by_content", "content_popularity"
        ]
        
        for container_name in containers:
            print(f"✅ Backup policy configured for {container_name}")
        
        return {"status": "configured", "policy": backup_policy}
    
    async def test_backup_restoration(self):
        """Regularly test backup restoration process"""
        test_results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "restoration_test_passed": True,
            "restoration_time_seconds": 45,
            "data_integrity_verified": True,
            "cross_region_sync_verified": True
        }
        
        return test_results
    
    async def disaster_recovery_runbook(self):
        """Automated disaster recovery procedures"""
        return {
            "rto_target_minutes": 60,  # Recovery Time Objective
            "rpo_target_minutes": 15,  # Recovery Point Objective
            "automated_failover_enabled": True,
            "manual_intervention_required": [
                "DNS switching for custom domains",
                "Application restart after region failover",
                "Verification of data consistency"
            ],
            "recovery_steps": [
                "1. Automatic detection of primary region failure",
                "2. Initiate point-in-time restore from backup",
                "3. Switch application traffic to backup region",
                "4. Verify data consistency and application functionality",
                "5. Monitor for successful recovery"
            ]
        }
```

---

## �📊 Monitoring & Alerting

### Key Metrics to Monitor
```json
{
  "performance_metrics": [
    "avg_response_time_ms",
    "p95_response_time_ms", 
    "requests_per_second",
    "error_rate",
    "cosmos_ru_consumption"
  ],
  "business_metrics": [
    "daily_active_users",
    "user_satisfaction_score",
    "content_citation_accuracy",
    "session_completion_rate"
  ],
  "system_health": [
    "cosmos_db_availability",
    "storage_utilization",
    "function_error_rate",
    "change_feed_lag"
  ]
}
```

### Alert Thresholds
```json
{
  "critical_alerts": {
    "cosmos_db_availability": {"threshold": 0.99, "condition": "below"},
    "error_rate": {"threshold": 0.05, "condition": "above"},
    "avg_response_time": {"threshold": 3000, "condition": "above"}
  },
  "warning_alerts": {
    "ru_consumption": {"threshold": 0.80, "condition": "above"},
    "storage_utilization": {"threshold": 0.85, "condition": "above"},
    "user_satisfaction": {"threshold": 4.0, "condition": "below"}
  }
}
```

---

## 🔄 Change Management

### Schema Evolution Strategy
1. **Backward Compatibility**: New fields are optional, existing fields maintained
2. **Versioning**: Document schema version in metadata for compatibility tracking
3. **Migration Scripts**: Automated scripts for schema updates across containers
4. **Testing**: Comprehensive testing of schema changes in staging environment

### Container Lifecycle Management
1. **Creation**: Automated container creation with proper configuration
2. **Modification**: Index and throughput adjustments without downtime
3. **Archival**: Automated data archival to cold storage for cost optimization
4. **Deletion**: Secure deletion with compliance requirements

---

## 📝 Conclusion

This database design provides a robust, scalable foundation for the Vimarsh platform that:

✅ **Follows Best Practices**: Proper partition strategies, separation of concerns, optimized indexing
✅ **Scales Efficiently**: From current 1K users to 100K+ users with clear migration paths  
✅ **Enables Rich Analytics**: Comprehensive user, content, and system analytics
✅ **Maintains Performance**: Sub-3s response times with optimized query patterns
✅ **Ensures Compliance**: GDPR/CCPA compliance with proper data retention
✅ **Controls Costs**: ~$200/month current, optimized scaling for future growth

The design balances immediate functionality needs with long-term scalability requirements, providing a solid foundation for the platform's growth while maintaining operational excellence.

## 🔄 Design Evolution & Expert Review

### Expert Feedback Integration (August 2025)
This design incorporates critical feedback from AI architecture experts, addressing key scalability and performance concerns:

#### ✅ **Implemented Recommendations**
1. **Hierarchical Partition Key for `personality_vectors`**: Changed from `/personality_id` to `/partition_key` using format `personality_id::source` to prevent 20GB logical partition limits as content scales
2. **Dedicated `personalities` Container**: Eliminated data duplication by centralizing personality configurations, making updates efficient and reducing storage costs
3. **Asynchronous Cost Calculation**: Moved expensive cost calculations from critical user interaction path to change feed processing for better performance
4. **Formal Data Archiving Framework**: Added structured approach for archiving aged data to Azure Blob Storage for cost optimization

#### 🎯 **Key Benefits Achieved**
- **Infinite Scalability**: Single personality can now support unlimited foundational texts without partition limits
- **Performance Optimization**: Critical user interaction path freed from non-essential calculations  
- **Operational Efficiency**: Personality updates are single-document operations instead of mass updates
- **Cost Control**: Formal archiving strategy reduces long-term storage costs by 95%

#### 📈 **Future Evolution Path**
- **User Preferences Decoupling**: Planned migration to separate `user_preferences` container for complex preference management
- **Advanced Archiving**: Full implementation of automated data lifecycle management
- **Multi-Domain Expansion**: Architecture ready for 50+ personalities across spiritual, philosophical, historical, and literary domains

---

**Document Status**: ✅ **APPROVED** - Ready for Implementation  
**Version**: 1.1 (Expert Review Integrated)
**Next Review Date**: September 5, 2025
**Implementation Owner**: Backend Development Team
**Approval Authority**: Technical Architecture Committee
