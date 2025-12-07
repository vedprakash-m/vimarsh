# User Settings API Documentation

**Version**: 1.0  
**Base URL**: `https://vimarsh.vedprakash.net/api`  
**Authentication**: JWT Bearer Token (Microsoft Entra ID)  
**Content-Type**: `application/json`  

---

## Table of Contents

1. [Authentication](#authentication)
2. [API Endpoints](#api-endpoints)
   - [GET /api/user/profile](#get-apiuserprofile)
   - [PATCH /api/user/preferences](#patch-apiuserpreferences)
   - [GET /api/user/usage-summary](#get-apiuserusage-summary)
   - [POST /api/user/export](#post-apiuserexport)
   - [DELETE /api/user/account](#delete-apiuseraccount)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Versioning](#versioning)

---

## Authentication

All endpoints require JWT authentication via Microsoft Entra ID.

### Request Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Token Extraction

The API extracts `user_id` from JWT claims using:
- `sub` claim (standard)
- `oid` claim (Microsoft Entra ID fallback)

### Authentication Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 401 | `missing_authorization` | No Authorization header provided |
| 401 | `invalid_token` | JWT token expired or malformed |
| 401 | `missing_user_id` | Token lacks sub/oid claim |

---

## API Endpoints

### GET /api/user/profile

Retrieve complete user profile including identity, preferences, journey statistics, and AI usage.

#### Request

```http
GET /api/user/profile HTTP/1.1
Host: vimarsh.vedprakash.net
Authorization: Bearer <YOUR_JWT_TOKEN>
```

#### Response (200 OK)

```json
{
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "seeker@vimarsh.app",
    "name": "Spiritual Seeker",
    "profile_picture": "https://graph.microsoft.com/v1.0/me/photo/$value",
    "member_since": "2024-01-01T00:00:00Z"
  },
  "preferences": {
    "experience_preferences": {
      "conversation_style": "balanced",
      "language": "english",
      "formality": "respectful",
      "favorite_personalities": ["krishna", "marcus-aurelius"],
      "theme": "light",
      "text_size": "medium",
      "reduce_animations": false,
      "show_citations": true
    },
    "notification_preferences": {
      "enabled": true,
      "daily_wisdom_enabled": true,
      "preferred_time": "09:00",
      "timezone": "America/Los_Angeles",
      "quiet_hours_enabled": false,
      "quiet_start": "22:00",
      "quiet_end": "07:00",
      "notification_types": {
        "daily_wisdom": true,
        "streak_reminders": true,
        "achievements": true,
        "weekly_summary": false
      }
    },
    "memory_preferences": {
      "remember_conversations": true,
      "connect_insights": true,
      "track_emotions": false,
      "suggest_topics": true,
      "privacy_mode": "standard",
      "allow_analytics": true,
      "allow_research": false,
      "data_retention_days": 90
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-12-07T10:30:00Z"
  },
  "journey_stats": {
    "current_streak": 14,
    "longest_streak": 21,
    "total_conversations": 87,
    "achievements_unlocked": 5,
    "wisdom_level": "Student",
    "domain_breakdown": {
      "spiritual": 35,
      "philosophical": 22,
      "leadership": 10,
      "scientific": 12,
      "literary": 5,
      "psychology": 3
    }
  },
  "ai_usage": {
    "monthly_cost_usd": 2.15,
    "monthly_limit_usd": 10.00,
    "usage_percentage": 21.5,
    "status": "well_within_limits",
    "billing_cycle_start": "2024-12-01T00:00:00Z",
    "billing_cycle_end": "2024-12-31T23:59:59Z",
    "trend": {
      "previous_month_cost": 1.85,
      "change_percentage": 16.2,
      "direction": "up"
    }
  }
}
```

#### Response Codes

| Code | Description |
|------|-------------|
| 200 | Success - Profile retrieved |
| 401 | Unauthorized - Invalid/missing token |
| 500 | Internal Server Error - Service failure |

#### Example Usage (JavaScript)

```javascript
const response = await fetch('https://vimarsh.vedprakash.net/api/user/profile', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
});

const profile = await response.json();
console.log(`Welcome, ${profile.user.name}!`);
console.log(`Current streak: ${profile.journey_stats.current_streak} days`);
```

---

### PATCH /api/user/preferences

Update user preferences with partial updates (auto-save friendly).

#### Request

```http
PATCH /api/user/preferences HTTP/1.1
Host: vimarsh.vedprakash.net
Authorization: Bearer <YOUR_JWT_TOKEN>
Content-Type: application/json

{
  "experience_preferences": {
    "conversation_style": "detailed"
  },
  "notification_preferences": {
    "preferred_time": "18:00"
  }
}
```

**Note:** Only include preferences you want to update. Omitted preferences remain unchanged (deep merge).

#### Request Body Schema

```typescript
{
  experience_preferences?: {
    conversation_style?: "brief" | "balanced" | "detailed"
    language?: "english" | "hindi"
    formality?: "very_formal" | "respectful" | "friendly" | "casual"
    favorite_personalities?: string[]  // Max 5, must be valid personality IDs
    theme?: "light" | "dark" | "auto"
    text_size?: "small" | "medium" | "large"
    reduce_animations?: boolean
    show_citations?: boolean
  }
  notification_preferences?: {
    enabled?: boolean
    daily_wisdom_enabled?: boolean
    preferred_time?: string  // HH:MM format (24-hour)
    timezone?: string  // IANA timezone (e.g., "America/New_York")
    quiet_hours_enabled?: boolean
    quiet_start?: string  // HH:MM format
    quiet_end?: string  // HH:MM format
    notification_types?: {
      daily_wisdom?: boolean
      streak_reminders?: boolean
      achievements?: boolean
      weekly_summary?: boolean
    }
  }
  memory_preferences?: {
    remember_conversations?: boolean
    connect_insights?: boolean
    track_emotions?: boolean
    suggest_topics?: boolean
    privacy_mode?: "standard" | "private" | "minimal"
    allow_analytics?: boolean
    allow_research?: boolean
    data_retention_days?: number  // 30-365
  }
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "preferences": {
    "experience_preferences": {
      "conversation_style": "detailed",
      "language": "english",
      "formality": "respectful",
      "favorite_personalities": ["krishna", "marcus-aurelius"],
      "theme": "light",
      "text_size": "medium",
      "reduce_animations": false,
      "show_citations": true
    },
    "notification_preferences": {
      "enabled": true,
      "daily_wisdom_enabled": true,
      "preferred_time": "18:00",
      "timezone": "America/Los_Angeles",
      "quiet_hours_enabled": false,
      "quiet_start": "22:00",
      "quiet_end": "07:00",
      "notification_types": {
        "daily_wisdom": true,
        "streak_reminders": true,
        "achievements": true,
        "weekly_summary": false
      }
    },
    "memory_preferences": {
      "remember_conversations": true,
      "connect_insights": true,
      "track_emotions": false,
      "suggest_topics": true,
      "privacy_mode": "standard",
      "allow_analytics": true,
      "allow_research": false,
      "data_retention_days": 90
    },
    "updated_at": "2024-12-07T10:35:15Z"
  }
}
```

#### Validation Errors (400 Bad Request)

```json
{
  "error": "validation_error",
  "message": "Invalid preferences provided",
  "details": {
    "favorite_personalities": "Maximum 5 favorites allowed (found 6)",
    "data_retention_days": "Must be between 30 and 365 (found 20)"
  }
}
```

#### Response Codes

| Code | Description |
|------|-------------|
| 200 | Success - Preferences updated |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized - Invalid/missing token |
| 500 | Internal Server Error - Database failure |

#### Example Usage (JavaScript)

```javascript
// Auto-save after 500ms debounce
const updatePreferences = async (updates) => {
  const response = await fetch('https://vimarsh.vedprakash.net/api/user/preferences', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updates)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }

  return await response.json();
};

// Update conversation style
await updatePreferences({
  experience_preferences: {
    conversation_style: 'detailed'
  }
});
```

---

### GET /api/user/usage-summary

Retrieve detailed AI usage summary with user-friendly language and trend analysis.

#### Request

```http
GET /api/user/usage-summary HTTP/1.1
Host: vimarsh.vedprakash.net
Authorization: Bearer <YOUR_JWT_TOKEN>
```

#### Response (200 OK)

```json
{
  "monthly_cost_usd": 2.15,
  "monthly_limit_usd": 10.00,
  "usage_percentage": 21.5,
  "status": "well_within_limits",
  "total_conversations": 87,
  "total_tokens": 125430,
  "billing_cycle": {
    "start": "2024-12-01T00:00:00Z",
    "end": "2024-12-31T23:59:59Z",
    "days_remaining": 24
  },
  "trend": {
    "previous_month_cost": 1.85,
    "change_usd": 0.30,
    "change_percentage": 16.2,
    "direction": "up"
  },
  "daily_breakdown": [
    {
      "date": "2024-12-01",
      "conversations": 3,
      "cost_usd": 0.08
    },
    {
      "date": "2024-12-02",
      "conversations": 4,
      "cost_usd": 0.11
    }
    // ... (30 days total)
  ]
}
```

#### Status Values

| Status | Usage Range | Color | Description |
|--------|-------------|-------|-------------|
| `well_within_limits` | 0-50% | Green | Healthy usage |
| `moderate` | 50-80% | Blue | Moderate usage |
| `approaching_limit` | 80-95% | Amber | Near limit warning |
| `at_limit` | 95-100% | Red | At or over limit |

#### Response Codes

| Code | Description |
|------|-------------|
| 200 | Success - Usage summary retrieved |
| 401 | Unauthorized - Invalid/missing token |
| 500 | Internal Server Error - Analytics service failure |

#### Example Usage (JavaScript)

```javascript
const response = await fetch('https://vimarsh.vedprakash.net/api/user/usage-summary', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
});

const usage = await response.json();

// Display user-friendly message
const message = `This month: $${usage.monthly_cost_usd.toFixed(2)} covered for you`;
const percentage = `${usage.usage_percentage.toFixed(0)}% of monthly limit`;
const status = usage.status.replace(/_/g, ' ').toUpperCase();

console.log(`${message} (${percentage}) - ${status}`);
```

---

### POST /api/user/export

Create GDPR-compliant data export containing all user data.

#### Request

```http
POST /api/user/export HTTP/1.1
Host: vimarsh.vedprakash.net
Authorization: Bearer <YOUR_JWT_TOKEN>
Content-Type: application/json

{
  "format": "json"
}
```

#### Request Body Schema

```typescript
{
  format?: "json"  // Currently only JSON supported
}
```

#### Response (200 OK)

```json
{
  "export_id": "export_20241207_103045_550e8400",
  "status": "completed",
  "download_url": "https://vimarsh.blob.core.windows.net/exports/export_20241207_103045_550e8400.json?sv=...",
  "expires_at": "2024-12-14T10:30:45Z",
  "metadata": {
    "export_version": "1.0",
    "export_timestamp": "2024-12-07T10:30:45Z",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "total_containers": 5,
    "items_exported": 342,
    "item_counts": {
      "user_preferences": 1,
      "engagement_tracking": 87,
      "conversation_memory": 234,
      "user_activity": 15,
      "bookmarks": 5
    }
  }
}
```

#### Export Data Structure

```json
{
  "metadata": {
    "export_version": "1.0",
    "export_timestamp": "2024-12-07T10:30:45Z",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "user_preferences": {
    // Full preferences object
  },
  "conversations": [
    {
      "conversation_id": "conv_123",
      "personality": "krishna",
      "timestamp": "2024-12-01T09:15:00Z",
      "messages": [
        {
          "role": "user",
          "content": "What is dharma?",
          "timestamp": "2024-12-01T09:15:00Z"
        },
        {
          "role": "assistant",
          "content": "Dharma is your sacred duty...",
          "timestamp": "2024-12-01T09:15:05Z",
          "citations": [...]
        }
      ]
    }
  ],
  "bookmarks": [
    {
      "bookmark_id": "bm_456",
      "conversation_id": "conv_123",
      "message_index": 1,
      "note": "Beautiful explanation of dharma",
      "created_at": "2024-12-01T09:16:00Z"
    }
  ],
  "engagement_stats": {
    "total_conversations": 87,
    "current_streak": 14,
    "achievements": [...]
  },
  "user_activity": [
    {
      "activity_type": "conversation_started",
      "timestamp": "2024-12-01T09:15:00Z",
      "metadata": {...}
    }
  ]
}
```

#### Response Codes

| Code | Description |
|------|-------------|
| 200 | Success - Export created |
| 401 | Unauthorized - Invalid/missing token |
| 500 | Internal Server Error - Export service failure |

#### Example Usage (JavaScript)

```javascript
const response = await fetch('https://vimarsh.vedprakash.net/api/user/export', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ format: 'json' })
});

const exportData = await response.json();

// Download file
const link = document.createElement('a');
link.href = exportData.download_url;
link.download = `vimarsh_export_${new Date().toISOString()}.json`;
link.click();

console.log(`Export contains ${exportData.metadata.items_exported} items`);
```

---

### DELETE /api/user/account

Permanently delete user account and all associated data (soft delete with 30-day recovery).

#### Request

```http
DELETE /api/user/account HTTP/1.1
Host: vimarsh.vedprakash.net
Authorization: Bearer <YOUR_JWT_TOKEN>
Content-Type: application/json

{
  "confirmation": "DELETE",
  "email": "seeker@vimarsh.app"
}
```

#### Request Body Schema

```typescript
{
  confirmation: "DELETE"  // Must be exact string "DELETE"
  email: string  // Must match user's email exactly
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Account scheduled for deletion",
  "deletion_summary": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "deletion_scheduled_at": "2024-12-07T10:40:00Z",
    "permanent_deletion_at": "2025-01-06T10:40:00Z",
    "recovery_period_days": 30,
    "items_deleted": {
      "user_preferences": 1,
      "engagement_tracking": 87,
      "conversation_memory": 234,
      "user_activity": 15,
      "bookmarks": 5
    },
    "total_items": 342
  },
  "recovery_instructions": "Contact support@vimarsh.vedprakash.net within 30 days to restore your account."
}
```

#### Validation Errors (400 Bad Request)

```json
{
  "error": "confirmation_mismatch",
  "message": "Confirmation text must be exactly 'DELETE'"
}
```

```json
{
  "error": "email_mismatch",
  "message": "Email does not match account email"
}
```

#### Response Codes

| Code | Description |
|------|-------------|
| 200 | Success - Account deletion scheduled |
| 400 | Bad Request - Confirmation/email mismatch |
| 401 | Unauthorized - Invalid/missing token |
| 500 | Internal Server Error - Deletion service failure |

#### Example Usage (JavaScript)

```javascript
const deleteAccount = async (userEmail) => {
  // Require explicit user confirmation
  const confirmText = prompt('Type DELETE to confirm account deletion:');
  if (confirmText !== 'DELETE') {
    throw new Error('Deletion cancelled - confirmation mismatch');
  }

  const response = await fetch('https://vimarsh.vedprakash.net/api/user/account', {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      confirmation: 'DELETE',
      email: userEmail
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }

  const result = await response.json();
  console.log(`Account deletion scheduled. Recovery possible until ${result.deletion_summary.permanent_deletion_at}`);
  
  // Redirect to goodbye page
  window.location.href = '/goodbye';
};
```

---

## Data Models

### UserPreferences

```typescript
interface UserPreferences {
  user_id: string
  experience_preferences: ExperiencePreferences
  notification_preferences: NotificationPreferences
  memory_preferences: MemoryPreferences
  created_at: string  // ISO 8601 timestamp
  updated_at: string  // ISO 8601 timestamp
}

interface ExperiencePreferences {
  conversation_style: "brief" | "balanced" | "detailed"
  language: "english" | "hindi"
  formality: "very_formal" | "respectful" | "friendly" | "casual"
  favorite_personalities: string[]  // Max 5
  theme: "light" | "dark" | "auto"
  text_size: "small" | "medium" | "large"
  reduce_animations: boolean
  show_citations: boolean
}

interface NotificationPreferences {
  enabled: boolean
  daily_wisdom_enabled: boolean
  preferred_time: string  // HH:MM format
  timezone: string  // IANA timezone
  quiet_hours_enabled: boolean
  quiet_start: string  // HH:MM format
  quiet_end: string  // HH:MM format
  notification_types: {
    daily_wisdom: boolean
    streak_reminders: boolean
    achievements: boolean
    weekly_summary: boolean
  }
}

interface MemoryPreferences {
  remember_conversations: boolean
  connect_insights: boolean
  track_emotions: boolean
  suggest_topics: boolean
  privacy_mode: "standard" | "private" | "minimal"
  allow_analytics: boolean
  allow_research: boolean
  data_retention_days: number  // 30-365
}
```

### JourneyStats

```typescript
interface JourneyStats {
  current_streak: number
  longest_streak: number
  total_conversations: number
  achievements_unlocked: number
  wisdom_level: "Seeker" | "Student" | "Practitioner" | "Scholar" | "Sage" | "Master"
  domain_breakdown: {
    spiritual: number
    philosophical: number
    leadership: number
    scientific: number
    literary: number
    psychology: number
  }
}
```

### AIUsageSummary

```typescript
interface AIUsageSummary {
  monthly_cost_usd: number
  monthly_limit_usd: number
  usage_percentage: number
  status: "well_within_limits" | "moderate" | "approaching_limit" | "at_limit"
  total_conversations: number
  total_tokens: number
  billing_cycle: {
    start: string  // ISO 8601
    end: string  // ISO 8601
    days_remaining: number
  }
  trend: {
    previous_month_cost: number
    change_usd: number
    change_percentage: number
    direction: "up" | "down" | "stable"
  }
  daily_breakdown: DailyUsage[]
}

interface DailyUsage {
  date: string  // YYYY-MM-DD
  conversations: number
  cost_usd: number
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field1": "Field-specific error",
    "field2": "Another error"
  },
  "timestamp": "2024-12-07T10:45:00Z",
  "request_id": "req_abc123def456"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `missing_authorization` | 401 | No Authorization header |
| `invalid_token` | 401 | JWT expired or malformed |
| `missing_user_id` | 401 | Token lacks user identifier |
| `validation_error` | 400 | Invalid request payload |
| `not_found` | 404 | Resource not found |
| `rate_limit_exceeded` | 429 | Too many requests |
| `internal_error` | 500 | Unexpected server error |
| `service_unavailable` | 503 | Service temporarily down |

### Retry Logic

**Exponential Backoff:**
- Initial retry: 1 second
- Second retry: 2 seconds
- Third retry: 4 seconds
- Maximum retries: 3

**Idempotent Endpoints:**
- GET requests: Always safe to retry
- PATCH requests: Idempotent with same payload
- DELETE requests: Idempotent (deleting already-deleted is no-op)

**Non-Idempotent:**
- POST /api/user/export: May create duplicate exports (check export_id)

---

## Rate Limiting

### Limits Per User

| Endpoint | Limit | Window |
|----------|-------|--------|
| GET /api/user/profile | 60 requests | per minute |
| PATCH /api/user/preferences | 30 requests | per minute |
| GET /api/user/usage-summary | 60 requests | per minute |
| POST /api/user/export | 5 requests | per hour |
| DELETE /api/user/account | 3 requests | per day |

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701954000
```

### Rate Limit Exceeded (429)

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again in 30 seconds.",
  "retry_after": 30
}
```

---

## Versioning

### Current Version: v1

**Base URL:** `https://vimarsh.vedprakash.net/api`

### Future Versioning Strategy

When breaking changes are needed:
- **v2 Base URL:** `https://vimarsh.vedprakash.net/api/v2`
- **v1 Support:** 12 months deprecation period
- **Migration Guide:** Published before v1 EOL

### API Stability Promise

**Stable (Won't Change):**
- Endpoint paths
- Required fields
- Status codes
- Authentication mechanism

**May Change (Additive):**
- New optional fields
- New endpoints
- New enum values
- New response metadata

**Deprecated Fields:**
- Marked with `@deprecated` in docs
- Still functional for 12 months
- Migration path documented

---

## Support & Feedback

### Getting Help

**Technical Support:**
- Email: api-support@vimarsh.vedprakash.net
- Response Time: 24-48 hours
- Include: Request ID, timestamp, error message

**API Status:**
- Status Page: https://status.vimarsh.vedprakash.net
- Incident History: https://status.vimarsh.vedprakash.net/history

### Reporting Issues

**Bug Reports:**
1. Check API status page
2. Verify request format
3. Check authentication
4. Email with:
   - Endpoint called
   - Request payload (redact sensitive data)
   - Response received
   - Expected behavior
   - Request ID (from error response)

**Feature Requests:**
- GitHub Discussions: https://github.com/vedprakash-m/vimarsh/discussions
- Tag with `api-enhancement`

---

**Last Updated: December 7, 2025**  
**Maintained by: Vimarsh Engineering Team**
