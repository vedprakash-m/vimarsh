---
file: .github/copilot-instructions.md
purpose: LLM-context injection for repository-specific grounding
audience: GitHub Copilot / LLM agents
scope: High-signal summary of conventions, architecture, and boilerplate
format: Markdown (token-optimized)
---

# Repository Context for GitHub Copilot

## ⚙️ Architecture & Stack

**Purpose**: AI-powered spiritual guidance system providing personalized advice from Hindu sacred texts through Lord Krishna's divine persona using RAG architecture.

**Stack**: Python 3.12, Azure Functions, React 18, TypeScript, Google Gemini Pro, Azure Cosmos DB, Microsoft Entra ID, Azure Key Vault, Bicep IaC, GitHub Actions

**Architecture**: Serverless RAG pipeline, Two-resource-group pause-resume cost architecture, Single production environment, Vector search with citation system

## 🔤 Naming Conventions

**TypeScript**: camelCase for variables/functions, PascalCase for components/types/interfaces, SCREAMING_SNAKE_CASE for constants

**CSS**: BEM methodology with spiritual prefix: .vimarsh-block__element--modifier, Sacred color variables: --sacred-saffron, --krishna-blue

**Python**: snake_case for functions/variables, PascalCase for classes, UPPERCASE for constants, Module names: spiritual_guidance, rag_pipeline

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
# Standard Azure Functions pattern with spiritual guidance logging
import azure.functions as func
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

@app.route(route="spiritual_guidance", methods=["POST"])
async def spiritual_guidance_handler(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Spiritual guidance processing
        logger.info("🕉️ Processing spiritual guidance request")
        return func.HttpResponse(json.dumps(response), mimetype="application/json")
    except Exception as e:
        logger.error(f"❌ Spiritual guidance error: {str(e)}")
        return func.HttpResponse("Error processing request", status_code=500)
```

**React Spiritual Component**:
```tsx
// All spiritual components follow Sacred Harmony design system
import React from 'react';
import { cn } from '@/lib/utils';

interface SpiritualComponentProps {
  className?: string;
  guidance?: string;
  citation?: string;
}

export const SpiritualComponent: React.FC<SpiritualComponentProps> = ({ 
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
# Standard pattern for RAG pipeline with spiritual context preservation
from typing import List, Dict, Any
from spiritual_guidance.enhanced_service import EnhancedSpiritualGuidanceService

class SpiritualRAGService:
    def __init__(self):
        self.spiritual_service = EnhancedSpiritualGuidanceService()
    
    async def get_krishna_guidance(self, query: str, context: str = "general") -> Dict[str, Any]:
        try:
            # Preserve Sanskrit terms and spiritual context
            response = await self.spiritual_service.generate_guidance(query, context)
            return {"guidance": response.text, "citations": response.citations}
        except Exception as e:
            logger.error(f"🕉️ RAG pipeline error: {str(e)}")
            raise SpiritualGuidanceError("Failed to retrieve divine wisdom")
```

## 🐞 Known Issues

**Refactor Targets**: 
- backend/fix_imports.py (temporary import resolution utility)
- frontend/src/components/ConversationInterface-old.tsx (legacy component)
- backend/test_error_handling.py (validation script, should be in tests/)

**Known Bugs**:
- Test failures: 247 failing tests in CI/CD pipeline
- LLM Integration: Currently using placeholder responses, Gemini Pro not connected
- RAG Pipeline: Vector database queries not implemented, using static responses
- Authentication: Disabled for clean UX during development phase
