# Vimarsh API Documentation

**Version:** 1.0.0  
**Base URL:** `https://vimarsh-functions.azurewebsites.net/api`  
**Local Development:** `http://localhost:7071/api`

## Overview

The Vimarsh API provides spiritual guidance through Lord Krishna's divine wisdom, leveraging advanced AI technology to deliver authentic, reverent responses based on sacred texts like the Bhagavad Gita, Mahabharata, and Srimad Bhagavatam.

## Authentication

All API endpoints require Azure Functions authentication:

```http
Authorization: Bearer <function-key>
```

For local development, use the default function key or configure in `local.settings.json`.

## Content Types

- **Request:** `application/json`
- **Response:** `application/json; charset=utf-8`
- **Error Format:** Standard HTTP status codes with JSON error details

## Rate Limiting

- **Production:** 100 requests per minute per user
- **Development:** No rate limiting

---

## Endpoints

### 1. Health Check

Check service availability and status.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "vimarsh-spiritual-guidance", 
  "version": "1.0.0",
  "timestamp": "2025-06-24T10:30:00Z",
  "environment": "production"
}
```

**Status Codes:**
- `200` - Service healthy
- `500` - Service issues detected

---

### 2. Spiritual Guidance

Main endpoint for receiving Lord Krishna's spiritual guidance.

**Endpoint:** `POST /api/spiritual_guidance`

**Request Body:**
```json
{
  "query": "How do I find inner peace during difficult times?",
  "language": "English",
  "include_citations": true,
  "voice_enabled": false
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | ✅ | - | User's spiritual question or concern |
| `language` | string | ❌ | "English" | Response language: "English" or "Hindi" |
| `include_citations` | boolean | ❌ | true | Include sacred text citations |
| `voice_enabled` | boolean | ❌ | false | Generate audio response (future feature) |

**Response:**
```json
{
  "response": "Dear devotee, your question touches the very essence of spiritual wisdom. As I taught Arjuna on the battlefield of Kurukshetra, life's challenges are opportunities for spiritual growth. Remember that you have the right to perform your duties, but never to the fruits of action. Let Me guide you toward the path of righteousness and inner peace.",
  "citations": [
    {
      "source": "Bhagavad Gita",
      "chapter": 2,
      "verse": 47,
      "text": "You have a right to perform your prescribed duty, but not to the fruits of action.",
      "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
      "relevance_score": 0.92
    }
  ],
  "metadata": {
    "query_processed": "How do I find inner peace during difficult times?",
    "language": "English",
    "processing_time_ms": 150,
    "model_version": "gemini-pro-1.0",
    "persona": "Lord Krishna",
    "confidence_score": 0.85,
    "spiritual_authenticity": "validated"
  },
  "audio_url": "https://vimarsh-audio.blob.core.windows.net/responses/abc123.mp3"
}
```

**Example Hindi Request:**
```json
{
  "query": "कैसे मैं अपने मन को शांत कर सकता हूँ?",
  "language": "Hindi",
  "include_citations": true
}
```

**Example Hindi Response:**
```json
{
  "response": "प्रिय भक्त, आपका प्रश्न अत्यंत महत्वपूर्ण है। गीता के अनुसार, जीवन में आने वाली चुनौतियों का सामना धैर्य और स्थिर बुद्धि से करना चाहिए। मैं आपको सदैव सत्य के मार्ग पर चलने की प्रेरणा देता हूँ।",
  "citations": [
    {
      "source": "भगवद्गीता",
      "chapter": 2,
      "verse": 47,
      "text": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
      "relevance_score": 0.92
    }
  ],
  "metadata": {
    "query_processed": "कैसे मैं अपने मन को शांत कर सकता हूँ?",
    "language": "Hindi",
    "processing_time_ms": 165,
    "model_version": "gemini-pro-1.0",
    "persona": "Lord Krishna",
    "confidence_score": 0.88,
    "spiritual_authenticity": "validated"
  }
}
```

**Status Codes:**
- `200` - Successful guidance response
- `400` - Invalid request (missing query, invalid language)
- `429` - Rate limit exceeded
- `500` - Internal server error

---

### 3. Supported Languages

Get list of supported languages for spiritual guidance.

**Endpoint:** `GET /api/languages`

**Response:**
```json
{
  "languages": [
    {
      "code": "English",
      "name": "English",
      "native_name": "English",
      "supported_features": ["text", "voice", "citations"]
    },
    {
      "code": "Hindi", 
      "name": "Hindi",
      "native_name": "हिन्दी",
      "supported_features": ["text", "voice", "citations", "sanskrit_terminology"]
    }
  ],
  "default_language": "English",
  "special_features": {
    "sanskrit_pronunciation": "Optimized Sanskrit pronunciation in voice responses",
    "sanskrit_citations": "Original Sanskrit verses with transliteration"
  }
}
```

**Status Codes:**
- `200` - Successful response
- `500` - Server error

---

### 4. CORS Support

All endpoints support CORS for web application integration.

**Endpoint:** `OPTIONS /{any-route}`

**Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, x-request-id
Access-Control-Max-Age: 86400
```

---

## Error Handling

### Error Response Format

```json
{
  "error": "Invalid request",
  "message": "Query parameter is required and cannot be empty",
  "timestamp": "2025-06-24T10:30:00Z",
  "request_id": "abc-123-def"
}
```

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `400` | Bad Request | Check request format and required parameters |
| `401` | Unauthorized | Verify function key in Authorization header |
| `429` | Rate Limited | Reduce request frequency |
| `500` | Server Error | Contact support or check logs |

---

## SDK Examples

### JavaScript/TypeScript

```typescript
interface SpiritualGuidanceRequest {
  query: string;
  language?: 'English' | 'Hindi';
  include_citations?: boolean;
  voice_enabled?: boolean;
}

interface SpiritualGuidanceResponse {
  response: string;
  citations: Array<{
    source: string;
    chapter: number;
    verse: number;
    text: string;
    sanskrit?: string;
    relevance_score: number;
  }>;
  metadata: {
    query_processed: string;
    language: string;
    processing_time_ms: number;
    model_version: string;
    persona: string;
    confidence_score: number;
    spiritual_authenticity: string;
  };
  audio_url?: string;
}

class VimarshAPI {
  constructor(private baseUrl: string, private functionKey: string) {}

  async getSpiritualGuidance(request: SpiritualGuidanceRequest): Promise<SpiritualGuidanceResponse> {
    const response = await fetch(`${this.baseUrl}/spiritual_guidance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.functionKey}`
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async getHealthStatus() {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }

  async getSupportedLanguages() {
    const response = await fetch(`${this.baseUrl}/languages`);
    return response.json();
  }
}

// Usage Example
const api = new VimarshAPI('https://vimarsh-functions.azurewebsites.net/api', 'your-function-key');

const guidance = await api.getSpiritualGuidance({
  query: 'How can I overcome fear and anxiety?',
  language: 'English',
  include_citations: true
});

console.log(guidance.response);
```

### Python

```python
import requests
import json
from typing import Optional, Dict, Any

class VimarshAPI:
    def __init__(self, base_url: str, function_key: str):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {function_key}'
        }

    def get_spiritual_guidance(
        self, 
        query: str, 
        language: str = 'English',
        include_citations: bool = True,
        voice_enabled: bool = False
    ) -> Dict[str, Any]:
        """Get spiritual guidance from Lord Krishna."""
        
        payload = {
            'query': query,
            'language': language,
            'include_citations': include_citations,
            'voice_enabled': voice_enabled
        }
        
        response = requests.post(
            f'{self.base_url}/spiritual_guidance',
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()

    def get_health_status(self) -> Dict[str, Any]:
        """Check API health status."""
        response = requests.get(f'{self.base_url}/health')
        response.raise_for_status()
        return response.json()

    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages."""
        response = requests.get(f'{self.base_url}/languages')
        response.raise_for_status()
        return response.json()

# Usage Example
api = VimarshAPI('https://vimarsh-functions.azurewebsites.net/api', 'your-function-key')

guidance = api.get_spiritual_guidance(
    query='What is the meaning of dharma?',
    language='English',
    include_citations=True
)

print(guidance['response'])
for citation in guidance['citations']:
    print(f"- {citation['source']} {citation['chapter']}.{citation['verse']}")
```

---

## Examples

### Simple Spiritual Query

```bash
curl -X POST https://vimarsh-functions.azurewebsites.net/api/spiritual_guidance \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_FUNCTION_KEY" \
  -d '{
    "query": "How can I find peace in troubled times?",
    "language": "English",
    "include_citations": true
  }'
```

### Sanskrit Terminology Query

```bash
curl -X POST https://vimarsh-functions.azurewebsites.net/api/spiritual_guidance \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_FUNCTION_KEY" \
  -d '{
    "query": "What is the meaning of dharma?",
    "language": "English",
    "include_citations": true,
    "voice_enabled": false
  }'
```

### Hindi Language Query

```bash
curl -X POST https://vimarsh-functions.azurewebsites.net/api/spiritual_guidance \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_FUNCTION_KEY" \
  -d '{
    "query": "मुझे जीवन का उद्देश्य कैसे मिलेगा?",
    "language": "Hindi",
    "include_citations": true
  }'
```

---

## Testing

### Health Check Test

```bash
curl -X GET https://vimarsh-functions.azurewebsites.net/api/health
```

### Spiritual Guidance Test

```bash
curl -X POST https://vimarsh-functions.azurewebsites.net/api/spiritual_guidance \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_FUNCTION_KEY" \
  -d '{
    "query": "How do I find my life purpose?",
    "language": "English",
    "include_citations": true
  }'
```

---

## Performance Characteristics

- **Response Time:** < 1 second for most queries
- **Throughput:** 100+ concurrent requests
- **Availability:** 99.9% uptime SLA
- **Regional:** Azure regions for optimal latency

## Monitoring & Analytics

- **Application Insights:** Real-time monitoring and analytics
- **Custom Metrics:** Spiritual guidance quality, response accuracy
- **Privacy:** No personal data stored, anonymous analytics only

---

**Support:** For API support, contact [vedprakash.m@me.com](mailto:vedprakash.m@me.com)  
**Documentation:** [Full Documentation](../README.md) | [Deployment Guide](../deployment/)

*"सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज" - Abandon all varieties of religion and surrender unto Me*
