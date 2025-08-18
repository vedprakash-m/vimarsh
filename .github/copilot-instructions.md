---
file: .github/copilot-instructions.md
purpose: LLM-context injection for repository-specific grounding
audience: GitHub Copilot / LLM agents
scope: High-signal summary of conventions, architecture, and boilerplate
format: Markdown (token-optimized)
---

# Repository Context for GitHub Copilot

## ⚙️ Architecture & Stack

**Purpose**: AI-powered conversational platform providing personalized wisdom from history's greatest minds across 6 domains (spiritual, philosophical, leadership, scientific, literary, psychology) using RAG architecture.

**Stack**: Python 3.12, Azure Functions, React 18, TypeScript, Google Gemini 2.5 Flash, Azure Cosmos DB, Microsoft Entra ID, Azure Key Vault, Bicep IaC, GitHub Actions

**Architecture**: Serverless RAG pipeline, Azure Static Web Apps frontend, Single production environment, Vector search with citation system, PWA capabilities

**Current Implementation**: 
- 25 operational personalities across 6 domains
- Spiritual (5): Krishna, Buddha, Jesus Christ, Rumi, Swami Vivekananda
- Philosophical (6): Marcus Aurelius, Lao Tzu, Confucius, Aristotle, Plato, Socrates  
- Leadership (6): Chanakya, Abraham Lincoln, Benjamin Franklin, George Washington, Mahatma Gandhi, Martin Luther King Jr.
- Scientific (5): Albert Einstein, Isaac Newton, Nikola Tesla, Archimedes, Leonardo da Vinci
- Literary (2): Rabindranath Tagore, William Shakespeare
- Psychology (1): Sigmund Freud

## 🔤 Naming Conventions

**TypeScript**: camelCase for variables/functions, PascalCase for components/types/interfaces, SCREAMING_SNAKE_CASE for constants

**CSS**: BEM methodology with spiritual prefix: .vimarsh-block__element--modifier, Sacred color variables: --sacred-saffron, --krishna-blue

**Python**: snake_case for functions/variables, PascalCase for classes, UPPERCASE for constants, Module names: multi_domain_guidance, rag_pipeline

**Database**: snake_case for all Cosmos DB collections and properties

## 🎨 Style & Patterns

**Indentation**: 2 spaces for TS/JS/CSS, 4 spaces for Python
**Line Length**: max 120 characters
**Imports**: Absolute imports from 'src/' directory for frontend, relative imports for backend modules
**Asynchronicity**: Prefer async/await over Promises
**State Management**: React hooks for local state, Context API for global spiritual guidance state
**Component Design**: Functional components with hooks, Sacred Harmony design system
**Type Safety**: Strict TypeScript, Python type hints, Zod validation for API schemas

## 🧩 Common Snippets

**Azure Function Handler**:
```python
# Standard Azure Functions pattern with multi-domain guidance logging
import azure.functions as func
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

@app.route(route="multi_domain_guidance", methods=["POST"])
async def multi_domain_guidance_handler(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Multi-domain guidance processing
        logger.info("🕉️ Processing multi-domain guidance request")
        return func.HttpResponse(json.dumps(response), mimetype="application/json")
    except Exception as e:
        logger.error(f"❌ Multi-domain guidance error: {str(e)}")
        return func.HttpResponse("Error processing request", status_code=500)
```

**React Multi-Domain Component**:
```tsx
// All multi-domain components follow Sacred Harmony design system
import React from 'react';
import { cn } from '@/lib/utils';

interface MultiDomainComponentProps {
  className?: string;
  guidance?: string;
  citation?: string;
}

export const MultiDomainComponent: React.FC<MultiDomainComponentProps> = ({ 
  className, 
  guidance, 
  citation 
}) => {
  return (
    <div className={cn('vimarsh-guidance', className)}>
      <div className="guidance-text">{guidance}</div>
      {citation && <cite className="sacred-citation">{citation}</cite>}
    </div>
  );
};
```

**RAG Pipeline Service**:
```python
# Standard pattern for RAG pipeline with multi-domain context preservation
from typing import List, Dict, Any
from multi_domain_guidance.enhanced_service import EnhancedMultiDomainGuidanceService

class MultiDomainRAGService:
    def __init__(self):
        self.guidance_service = EnhancedMultiDomainGuidanceService()
    
    async def get_personality_guidance(self, query: str, personality: str = "krishna") -> Dict[str, Any]:
        try:
            # Preserve domain-specific terms and cultural context
            response = await self.guidance_service.generate_guidance(query, personality)
            return {"guidance": response.text, "citations": response.citations}
        except Exception as e:
            logger.error(f"🕉️ RAG pipeline error: {str(e)}")
            raise MultiDomainGuidanceError("Failed to retrieve wisdom")
```

## 🐞 Known Issues

**Refactor Targets**: 
- backend/fix_imports.py (temporary import resolution utility)
- frontend/src/components/ConversationInterface-old.tsx (legacy component)
- backend/test_error_handling.py (validation script, should be in tests/)

**Current Status**:
- Production Ready: 25 personalities across 6 domains operational
- Enhanced RAG Service V6: Fully implemented with citation grounding
- Authentication: Microsoft Entra ID integrated and operational
- PWA Features: Offline capability and app installation working
- Performance: 2.3s response time, 98.7% uptime, 45% cache hit rate
- Test Coverage: CI/CD pipeline optimization in progress
