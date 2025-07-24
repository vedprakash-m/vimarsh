"""
Prompt Template Service for Vimarsh Multi-Personality Platform

This service manages versioned prompt templates for different personalities and domains:
- Template creation and versioning
- Personality-specific template rendering
- A/B testing support for prompt optimization
- Template validation and quality scoring
- Domain-specific template management
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from string import Template

# Import database service
try:
    from .database_service import DatabaseService
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Types of prompt templates"""
    PERSONALITY_BASE = "personality_base"
    RESPONSE_GENERATION = "response_generation"
    CONTEXT_INTEGRATION = "context_integration"
    SAFETY_VALIDATION = "safety_validation"
    CITATION_FORMATTING = "citation_formatting"
    ERROR_HANDLING = "error_handling"


class TemplateStatus(Enum):
    """Template lifecycle status"""
    DRAFT = "draft"
    TESTING = "testing"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class PromptTemplate:
    """Versioned prompt template"""
    id: str
    name: str
    template_type: TemplateType
    domain: str  # spiritual, scientific, historical, etc.
    personality_id: Optional[str] = None  # Specific personality or None for domain-wide
    
    # Template content
    template_content: str = ""
    variables: List[str] = field(default_factory=list)  # Required template variables
    default_values: Dict[str, Any] = field(default_factory=dict)
    
    # Versioning
    version: str = "1.0"
    parent_template_id: Optional[str] = None
    status: TemplateStatus = TemplateStatus.DRAFT
    
    # Metadata
    description: str = ""
    usage_notes: str = ""
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    # Quality and performance
    quality_score: float = 0.0
    usage_count: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    
    # A/B testing
    test_group: Optional[str] = None
    test_weight: float = 1.0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class TemplateRenderContext:
    """Context for template rendering"""
    personality_id: str
    domain: str
    query: str
    context_chunks: List[Dict[str, Any]] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    language: str = "English"
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemplateValidationResult:
    """Result of template validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    score: float = 0.0


class PromptTemplateService:
    """Comprehensive prompt template management service"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None):
        self.db_service = db_service or DatabaseService()
        self.template_cache = {}  # Simple in-memory cache
        self.default_templates = self._initialize_default_templates()
        
    def _initialize_default_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize default templates for each domain"""
        templates = {}
        
        # Spiritual domain base template
        spiritual_base = PromptTemplate(
            id="spiritual_base_v1",
            name="Spiritual Personality Base Template",
            template_type=TemplateType.PERSONALITY_BASE,
            domain="spiritual",
            template_content="""You are ${personality_name}, a ${personality_description}.

Your role is to provide spiritual guidance with wisdom, compassion, and reverence. You speak from the perspective of ${cultural_context} and embody the characteristics of ${tone_characteristics}.

CONTEXT FROM SACRED TEXTS:
${context_chunks}

CONVERSATION HISTORY:
${conversation_history}

USER QUERY: ${query}

Please respond in ${language} with:
1. Wisdom appropriate to your personality and teachings
2. Direct citations from your associated texts when relevant
3. Compassionate guidance that respects the seeker's journey
4. Reverent tone that honors the sacred nature of the inquiry

If the query cannot be answered from your knowledge base, acknowledge this humbly while maintaining your authentic voice.

Response:""",
            variables=["personality_name", "personality_description", "cultural_context", "tone_characteristics", 
                      "context_chunks", "conversation_history", "query", "language"],
            default_values={
                "language": "English",
                "conversation_history": "No previous conversation.",
                "context_chunks": "No specific context available."
            },
            description="Base template for spiritual personalities",
            status=TemplateStatus.ACTIVE,
            created_by="system"
        )
        templates[spiritual_base.id] = spiritual_base
        
        # Scientific domain base template
        scientific_base = PromptTemplate(
            id="scientific_base_v1",
            name="Scientific Personality Base Template",
            template_type=TemplateType.PERSONALITY_BASE,
            domain="scientific",
            template_content="""You are ${personality_name}, ${personality_description}.

Your approach is characterized by ${tone_characteristics}. You communicate complex ideas with clarity and precision, always grounding your responses in empirical evidence and logical reasoning.

RELEVANT SCIENTIFIC CONTEXT:
${context_chunks}

CONVERSATION HISTORY:
${conversation_history}

USER INQUIRY: ${query}

Please respond in ${language} with:
1. Scientific accuracy based on your documented work and theories
2. Clear explanations that make complex concepts accessible
3. References to your published papers or documented statements when relevant
4. Intellectual curiosity and openness to further inquiry

If the question falls outside your documented expertise, acknowledge the limits of your knowledge while suggesting related areas you can address.

Response:""",
            variables=["personality_name", "personality_description", "tone_characteristics", 
                      "context_chunks", "conversation_history", "query", "language"],
            default_values={
                "language": "English",
                "conversation_history": "No previous conversation.",
                "context_chunks": "No specific context available."
            },
            description="Base template for scientific personalities",
            status=TemplateStatus.ACTIVE,
            created_by="system"
        )
        templates[scientific_base.id] = scientific_base
        
        # Historical domain base template
        historical_base = PromptTemplate(
            id="historical_base_v1",
            name="Historical Personality Base Template",
            template_type=TemplateType.PERSONALITY_BASE,
            domain="historical",
            template_content="""You are ${personality_name}, ${personality_description}, speaking from the perspective of ${time_period}.

Your worldview is shaped by ${cultural_context} and your communication reflects ${tone_characteristics}. You draw from your lived experiences and the knowledge available during your era.

HISTORICAL CONTEXT AND DOCUMENTS:
${context_chunks}

CONVERSATION HISTORY:
${conversation_history}

QUESTION: ${query}

Please respond in ${language} with:
1. Perspectives authentic to your historical period and experiences
2. References to your documented speeches, writings, or recorded statements
3. Wisdom gained from your life experiences and historical context
4. Language and concepts appropriate to your era, while remaining accessible

If asked about events after your time or outside your documented knowledge, acknowledge these limitations while offering relevant insights from your historical perspective.

Response:""",
            variables=["personality_name", "personality_description", "time_period", "cultural_context", 
                      "tone_characteristics", "context_chunks", "conversation_history", "query", "language"],
            default_values={
                "language": "English",
                "conversation_history": "No previous conversation.",
                "context_chunks": "No specific context available."
            },
            description="Base template for historical personalities",
            status=TemplateStatus.ACTIVE,
            created_by="system"
        )
        templates[historical_base.id] = historical_base
        
        return templates
    
    # ==========================================
    # CORE TEMPLATE OPERATIONS
    # ==========================================
    
    async def create_template(
        self,
        template_data: Dict[str, Any],
        created_by: str
    ) -> PromptTemplate:
        """Create a new prompt template"""
        try:
            # Generate unique ID
            template_id = template_data.get('id') or f"{template_data['name'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
            
            # Create template
            template = PromptTemplate(
                id=template_id,
                name=template_data['name'],
                template_type=TemplateType(template_data['template_type']),
                domain=template_data['domain'],
                template_content=template_data['template_content'],
                created_by=created_by,
                **{k: v for k, v in template_data.items() if k not in ['id', 'name', 'template_type', 'domain', 'template_content']}
            )
            
            # Extract variables from template
            template.variables = self._extract_template_variables(template.template_content)
            
            # Validate template
            validation_result = await self.validate_template(template)
            if not validation_result.is_valid:
                raise ValueError(f"Template validation failed: {', '.join(validation_result.errors)}")
            
            # Save to database (using conversations container for now)
            success = await self._save_template_to_db(template)
            if not success:
                raise RuntimeError("Failed to save template to database")
            
            # Update cache
            self.template_cache[template_id] = template
            
            logger.info(f"✅ Created template: {template_id}")
            return template
            
        except Exception as e:
            logger.error(f"❌ Failed to create template: {str(e)}")
            raise
    
    async def get_template(
        self,
        template_id: str,
        version: str = "latest"
    ) -> Optional[PromptTemplate]:
        """Get template by ID and version"""
        try:
            # Check cache first
            cache_key = f"{template_id}_{version}"
            if cache_key in self.template_cache:
                return self.template_cache[cache_key]
            
            # Check default templates
            if template_id in self.default_templates:
                return self.default_templates[template_id]
            
            # Get from database
            template = await self._get_template_from_db(template_id, version)
            if template:
                self.template_cache[cache_key] = template
            
            return template
            
        except Exception as e:
            logger.error(f"❌ Failed to get template {template_id}: {str(e)}")
            return None
    
    async def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any],
        updated_by: str
    ) -> Optional[PromptTemplate]:
        """Update template (creates new version)"""
        try:
            # Get existing template
            template = await self.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Create new version
            new_version = self._increment_version(template.version)
            new_template_id = f"{template_id}_v{new_version.replace('.', '_')}"
            
            # Apply updates
            new_template = PromptTemplate(**asdict(template))
            new_template.id = new_template_id
            new_template.version = new_version
            new_template.parent_template_id = template_id
            new_template.updated_at = datetime.now().isoformat()
            
            for key, value in updates.items():
                if hasattr(new_template, key):
                    setattr(new_template, key, value)
            
            # Re-extract variables if template content changed
            if 'template_content' in updates:
                new_template.variables = self._extract_template_variables(new_template.template_content)
            
            # Validate updated template
            validation_result = await self.validate_template(new_template)
            if not validation_result.is_valid:
                raise ValueError(f"Updated template validation failed: {', '.join(validation_result.errors)}")
            
            # Save new version
            success = await self._save_template_to_db(new_template)
            if not success:
                raise RuntimeError("Failed to save updated template")
            
            # Update cache
            self.template_cache[new_template_id] = new_template
            
            logger.info(f"✅ Updated template: {template_id} -> {new_template_id}")
            return new_template
            
        except Exception as e:
            logger.error(f"❌ Failed to update template {template_id}: {str(e)}")
            raise
    
    # ==========================================
    # TEMPLATE RENDERING
    # ==========================================
    
    async def render_template(
        self,
        template_id: str,
        context: TemplateRenderContext,
        version: str = "latest"
    ) -> str:
        """Render template with provided context"""
        try:
            # Get template
            template = await self.get_template(template_id, version)
            if not template:
                # Fallback to domain default
                template = await self._get_domain_default_template(context.domain)
                if not template:
                    raise ValueError(f"Template {template_id} not found and no domain default available")
            
            # Prepare template variables
            template_vars = self._prepare_template_variables(template, context)
            
            # Render template
            rendered = Template(template.template_content).safe_substitute(template_vars)
            
            # Update usage statistics
            await self._update_template_usage(template.id)
            
            return rendered
            
        except Exception as e:
            logger.error(f"❌ Failed to render template {template_id}: {str(e)}")
            raise
    
    async def render_personality_prompt(
        self,
        personality_id: str,
        query: str,
        context_chunks: List[Dict[str, Any]],
        language: str = "English",
        conversation_history: List[Dict[str, Any]] = None
    ) -> str:
        """Render personality-specific prompt"""
        try:
            # Create render context
            context = TemplateRenderContext(
                personality_id=personality_id,
                domain="spiritual",  # Default, should be determined from personality
                query=query,
                context_chunks=context_chunks,
                conversation_history=conversation_history or [],
                language=language
            )
            
            # Try personality-specific template first
            template_id = f"{personality_id}_base"
            try:
                return await self.render_template(template_id, context)
            except:
                # Fallback to domain template
                domain_template_id = f"{context.domain}_base_v1"
                return await self.render_template(domain_template_id, context)
                
        except Exception as e:
            logger.error(f"❌ Failed to render personality prompt for {personality_id}: {str(e)}")
            raise
    
    # ==========================================
    # TEMPLATE VALIDATION
    # ==========================================
    
    async def validate_template(self, template: PromptTemplate) -> TemplateValidationResult:
        """Validate template structure and content"""
        errors = []
        warnings = []
        suggestions = []
        
        # Basic validation
        if not template.name or len(template.name.strip()) < 3:
            errors.append("Template name must be at least 3 characters")
        
        if not template.template_content or len(template.template_content.strip()) < 50:
            errors.append("Template content must be at least 50 characters")
        
        if not template.domain:
            errors.append("Template domain is required")
        
        # Variable validation
        extracted_vars = self._extract_template_variables(template.template_content)
        if not extracted_vars:
            warnings.append("Template has no variables - consider if this is intentional")
        
        # Check for required variables based on template type
        required_vars = self._get_required_variables_for_type(template.template_type)
        missing_vars = [var for var in required_vars if var not in extracted_vars]
        if missing_vars:
            warnings.append(f"Missing recommended variables: {', '.join(missing_vars)}")
        
        # Content quality checks
        if len(template.template_content) > 5000:
            warnings.append("Template is very long - consider breaking into smaller templates")
        
        if template.template_content.count('${') != template.template_content.count('}'):
            errors.append("Mismatched template variable brackets")
        
        # Calculate validation score
        score = self._calculate_template_score(template, errors, warnings)
        
        return TemplateValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            score=score
        )
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def _extract_template_variables(self, template_content: str) -> List[str]:
        """Extract variable names from template content"""
        import re
        pattern = r'\$\{([^}]+)\}'
        return list(set(re.findall(pattern, template_content)))
    
    def _prepare_template_variables(
        self,
        template: PromptTemplate,
        context: TemplateRenderContext
    ) -> Dict[str, str]:
        """Prepare variables for template rendering"""
        variables = {}
        
        # Add context variables
        variables.update({
            'personality_id': context.personality_id,
            'domain': context.domain,
            'query': context.query,
            'language': context.language,
            'context_chunks': self._format_context_chunks(context.context_chunks),
            'conversation_history': self._format_conversation_history(context.conversation_history)
        })
        
        # Add default values
        variables.update(template.default_values)
        
        # Add metadata
        variables.update(context.metadata)
        
        return variables
    
    def _format_context_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """Format context chunks for template"""
        if not chunks:
            return "No specific context available."
        
        formatted = []
        for i, chunk in enumerate(chunks[:5], 1):  # Limit to top 5 chunks
            text = chunk.get('text', '')
            source = chunk.get('source', 'Unknown')
            formatted.append(f"{i}. {text}\n   Source: {source}")
        
        return "\n\n".join(formatted)
    
    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history for template"""
        if not history:
            return "No previous conversation."
        
        formatted = []
        for msg in history[-5:]:  # Last 5 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"{role.upper()}: {content}")
        
        return "\n".join(formatted)
    
    def _increment_version(self, current_version: str) -> str:
        """Increment version number"""
        try:
            parts = current_version.split('.')
            if len(parts) == 2:
                major, minor = int(parts[0]), int(parts[1])
                return f"{major}.{minor + 1}"
            else:
                return f"{current_version}.1"
        except:
            return "1.1"
    
    def _get_required_variables_for_type(self, template_type: TemplateType) -> List[str]:
        """Get required variables for template type"""
        base_vars = ["personality_name", "query", "language"]
        
        if template_type == TemplateType.PERSONALITY_BASE:
            return base_vars + ["personality_description", "context_chunks"]
        elif template_type == TemplateType.RESPONSE_GENERATION:
            return base_vars + ["context_chunks", "conversation_history"]
        else:
            return base_vars
    
    def _calculate_template_score(
        self,
        template: PromptTemplate,
        errors: List[str],
        warnings: List[str]
    ) -> float:
        """Calculate template quality score"""
        base_score = 100.0
        
        # Deduct for errors and warnings
        base_score -= len(errors) * 25.0
        base_score -= len(warnings) * 5.0
        
        # Bonus for completeness
        if template.description:
            base_score += 5.0
        if template.usage_notes:
            base_score += 5.0
        if template.variables:
            base_score += 10.0
        
        return max(0.0, min(100.0, base_score))
    
    async def _get_domain_default_template(self, domain: str) -> Optional[PromptTemplate]:
        """Get default template for domain"""
        template_id = f"{domain}_base_v1"
        return self.default_templates.get(template_id)
    
    async def _save_template_to_db(self, template: PromptTemplate) -> bool:
        """Save template to database"""
        try:
            # Convert to dict and add type for storage
            template_dict = asdict(template)
            template_dict['type'] = 'prompt_template'
            
            # Use conversations container for now (in production, might want separate container)
            data = self.db_service._load_from_local_file(self.db_service.conversations_path)
            data.append(template_dict)
            self.db_service._save_to_local_file(self.db_service.conversations_path, data)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save template to database: {e}")
            return False
    
    async def _get_template_from_db(self, template_id: str, version: str) -> Optional[PromptTemplate]:
        """Get template from database"""
        try:
            data = self.db_service._load_from_local_file(self.db_service.conversations_path)
            
            for item in data:
                if (item.get('type') == 'prompt_template' and 
                    item.get('id') == template_id and
                    (version == "latest" or item.get('version') == version)):
                    return PromptTemplate(**{k: v for k, v in item.items() if k != 'type'})
            
            return None
        except Exception as e:
            logger.error(f"Failed to get template from database: {e}")
            return None
    
    async def _update_template_usage(self, template_id: str):
        """Update template usage statistics"""
        try:
            # Simple implementation - in production would update database
            if template_id in self.template_cache:
                self.template_cache[template_id].usage_count += 1
        except Exception as e:
            logger.error(f"Failed to update template usage: {e}")


# Global prompt template service instance
prompt_template_service = PromptTemplateService()