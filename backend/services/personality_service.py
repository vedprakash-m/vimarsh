"""
Personality Management Service for Vimarsh Multi-Personality Platform

This service provides comprehensive personality management capabilities including:
- CRUD operations for AI personalities
- Domain classification (spiritual, scientific, historical, philosophical)
- Personality validation and authenticity checks
- Knowledge base association and management
- Personality-specific configuration and settings
- Expert review integration
- Personality discovery and search
"""

import logging
import os
import uuid
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

# Import database service
try:
    from .database_service import DatabaseService, PersonalityConfig
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)


class PersonalityDomain(Enum):
    """Personality domains for classification"""
    SPIRITUAL = "spiritual"
    SCIENTIFIC = "scientific"
    HISTORICAL = "historical"
    PHILOSOPHICAL = "philosophical"
    LITERARY = "literary"
    POLITICAL = "political"


class PersonalityStatus(Enum):
    """Personality status for lifecycle management"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


@dataclass
class PersonalityProfile:
    """Comprehensive personality profile with all attributes"""
    id: str
    name: str
    display_name: str
    domain: PersonalityDomain
    time_period: str
    description: str
    
    # Core personality attributes
    tone_characteristics: Dict[str, Any] = field(default_factory=dict)
    vocabulary_preferences: Dict[str, Any] = field(default_factory=dict)
    response_patterns: Dict[str, Any] = field(default_factory=dict)
    expertise_areas: List[str] = field(default_factory=list)
    cultural_context: str = ""
    language_style: str = ""
    
    # Knowledge base and content
    knowledge_base_ids: List[str] = field(default_factory=list)
    associated_books: List[str] = field(default_factory=list)
    vector_namespace: str = ""
    
    # Voice and interaction settings
    voice_settings: Dict[str, Any] = field(default_factory=dict)
    greeting_patterns: List[str] = field(default_factory=list)
    farewell_patterns: List[str] = field(default_factory=list)
    uncertainty_responses: List[str] = field(default_factory=list)
    
    # System and management
    system_prompt: str = ""
    prompt_template_ids: List[str] = field(default_factory=list)
    status: PersonalityStatus = PersonalityStatus.DRAFT
    is_active: bool = False
    
    # Metadata
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    
    # Analytics and quality
    usage_count: int = 0
    quality_score: float = 0.0
    expert_approved: bool = False
    expert_reviewer: str = ""
    review_notes: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if not self.vector_namespace:
            self.vector_namespace = self.id
        if not self.display_name:
            self.display_name = self.name


@dataclass
class PersonalityValidationResult:
    """Result of personality validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class PersonalitySearchFilter:
    """Search and filter criteria for personalities"""
    domain: Optional[PersonalityDomain] = None
    status: Optional[PersonalityStatus] = None
    is_active: Optional[bool] = None
    expert_approved: Optional[bool] = None
    tags: List[str] = field(default_factory=list)
    time_period: Optional[str] = None
    min_quality_score: Optional[float] = None
    search_query: Optional[str] = None


class PersonalityService:
    """Comprehensive personality management service"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None):
        self.db_service = db_service or DatabaseService()
        self.domain_validators = self._initialize_domain_validators()
        self.personality_cache = {}  # Simple in-memory cache
        
    def _initialize_domain_validators(self) -> Dict[PersonalityDomain, Any]:
        """Initialize domain-specific validators"""
        return {
            PersonalityDomain.SPIRITUAL: self._validate_spiritual_personality,
            PersonalityDomain.SCIENTIFIC: self._validate_scientific_personality,
            PersonalityDomain.HISTORICAL: self._validate_historical_personality,
            PersonalityDomain.PHILOSOPHICAL: self._validate_philosophical_personality,
            PersonalityDomain.LITERARY: self._validate_literary_personality,
            PersonalityDomain.POLITICAL: self._validate_political_personality,
        }
    
    # ==========================================
    # CORE CRUD OPERATIONS
    # ==========================================
    
    async def create_personality(
        self,
        personality_data: Dict[str, Any],
        created_by: str
    ) -> PersonalityProfile:
        """Create a new personality with validation"""
        try:
            # Generate unique ID
            personality_id = personality_data.get('id') or f"{personality_data['name'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
            
            # Create personality profile
            personality = PersonalityProfile(
                id=personality_id,
                name=personality_data['name'],
                display_name=personality_data.get('display_name', personality_data['name']),
                domain=PersonalityDomain(personality_data['domain']),
                time_period=personality_data.get('time_period', ''),
                description=personality_data.get('description', ''),
                created_by=created_by,
                **{k: v for k, v in personality_data.items() if k not in ['id', 'name', 'domain', 'display_name', 'time_period', 'description']}
            )
            
            # Validate personality
            validation_result = await self.validate_personality(personality)
            if not validation_result.is_valid:
                raise ValueError(f"Personality validation failed: {', '.join(validation_result.errors)}")
            
            # Save to database
            config = self._personality_to_config(personality)
            success = await self.db_service.save_personality_config(config)
            
            if not success:
                raise RuntimeError("Failed to save personality to database")
            
            # Update cache
            self.personality_cache[personality_id] = personality
            
            logger.info(f"✅ Created personality: {personality_id} ({personality.name})")
            return personality
            
        except Exception as e:
            logger.error(f"❌ Failed to create personality: {str(e)}")
            raise
    
    async def get_personality(self, personality_id: str) -> Optional[PersonalityProfile]:
        """Get personality by ID with caching"""
        try:
            # Check cache first
            if personality_id in self.personality_cache:
                return self.personality_cache[personality_id]
            
            # Get from database
            config = await self.db_service.get_personality_config(personality_id)
            if not config:
                return None
            
            # Convert to personality profile
            personality = self._config_to_personality(config)
            
            # Update cache
            self.personality_cache[personality_id] = personality
            
            return personality
            
        except Exception as e:
            logger.error(f"❌ Failed to get personality {personality_id}: {str(e)}")
            return None
    
    async def update_personality(
        self,
        personality_id: str,
        updates: Dict[str, Any],
        updated_by: str
    ) -> Optional[PersonalityProfile]:
        """Update personality with validation"""
        try:
            # Get existing personality
            personality = await self.get_personality(personality_id)
            if not personality:
                raise ValueError(f"Personality {personality_id} not found")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(personality, key):
                    setattr(personality, key, value)
            
            # Update metadata
            personality.updated_at = datetime.now().isoformat()
            
            # Validate updated personality
            validation_result = await self.validate_personality(personality)
            if not validation_result.is_valid:
                raise ValueError(f"Updated personality validation failed: {', '.join(validation_result.errors)}")
            
            # Save to database
            config = self._personality_to_config(personality)
            success = await self.db_service.save_personality_config(config)
            
            if not success:
                raise RuntimeError("Failed to update personality in database")
            
            # Update cache
            self.personality_cache[personality_id] = personality
            
            logger.info(f"✅ Updated personality: {personality_id}")
            return personality
            
        except Exception as e:
            logger.error(f"❌ Failed to update personality {personality_id}: {str(e)}")
            raise
    
    async def delete_personality(
        self,
        personality_id: str,
        deleted_by: str,
        force: bool = False
    ) -> bool:
        """Delete personality with safety checks"""
        try:
            # Get personality to check dependencies
            personality = await self.get_personality(personality_id)
            if not personality:
                logger.warning(f"Personality {personality_id} not found for deletion")
                return True  # Already deleted
            
            # Check for dependencies unless forced
            if not force:
                dependencies = await self._check_personality_dependencies(personality_id)
                if dependencies:
                    raise ValueError(f"Cannot delete personality with dependencies: {dependencies}")
            
            # Archive instead of hard delete for safety
            personality.status = PersonalityStatus.ARCHIVED
            personality.is_active = False
            personality.updated_at = datetime.now().isoformat()
            
            # Save archived state
            config = self._personality_to_config(personality)
            success = await self.db_service.save_personality_config(config)
            
            if success:
                # Remove from cache
                self.personality_cache.pop(personality_id, None)
                logger.info(f"✅ Archived personality: {personality_id}")
                return True
            else:
                raise RuntimeError("Failed to archive personality in database")
                
        except Exception as e:
            logger.error(f"❌ Failed to delete personality {personality_id}: {str(e)}")
            raise
    
    # ==========================================
    # PERSONALITY DISCOVERY AND SEARCH
    # ==========================================
    
    async def search_personalities(
        self,
        filters: PersonalitySearchFilter,
        limit: int = 50,
        offset: int = 0
    ) -> List[PersonalityProfile]:
        """Search personalities with advanced filtering"""
        try:
            # Get all personalities from database
            configs = await self.db_service.get_all_personalities()
            personalities = [self._config_to_personality(config) for config in configs]
            
            # Apply filters
            filtered = self._apply_search_filters(personalities, filters)
            
            # Apply pagination
            return filtered[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to search personalities: {str(e)}")
            return []
    
    async def get_personalities_by_domain(
        self,
        domain: PersonalityDomain,
        active_only: bool = True
    ) -> List[PersonalityProfile]:
        """Get personalities by domain"""
        filters = PersonalitySearchFilter(
            domain=domain,
            is_active=active_only if active_only else None
        )
        return await self.search_personalities(filters)
    
    async def get_active_personalities(self) -> List[PersonalityProfile]:
        """Get all active personalities"""
        filters = PersonalitySearchFilter(
            is_active=True
        )
        return await self.search_personalities(filters)
    
    async def discover_personalities(
        self,
        user_query: str,
        max_results: int = 10
    ) -> List[PersonalityProfile]:
        """Discover personalities based on user query"""
        try:
            # Simple keyword-based discovery
            # In production, this could use semantic search
            filters = PersonalitySearchFilter(
                search_query=user_query,
                is_active=True
            )
            
            personalities = await self.search_personalities(filters, limit=max_results)
            
            # Sort by relevance (simple implementation)
            return sorted(personalities, key=lambda p: self._calculate_relevance(p, user_query), reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Failed to discover personalities: {str(e)}")
            return []
    
    # ==========================================
    # PERSONALITY VALIDATION
    # ==========================================
    
    async def validate_personality(self, personality: PersonalityProfile) -> PersonalityValidationResult:
        """Comprehensive personality validation"""
        errors = []
        warnings = []
        suggestions = []
        
        # Basic validation
        if not personality.name or len(personality.name.strip()) < 2:
            errors.append("Personality name must be at least 2 characters")
        
        if not personality.description or len(personality.description.strip()) < 10:
            errors.append("Personality description must be at least 10 characters")
        
        if not personality.domain:
            errors.append("Personality domain is required")
        
        # Domain-specific validation
        if personality.domain in self.domain_validators:
            domain_result = await self.domain_validators[personality.domain](personality)
            errors.extend(domain_result.get('errors', []))
            warnings.extend(domain_result.get('warnings', []))
            suggestions.extend(domain_result.get('suggestions', []))
        
        # Knowledge base validation
        if not personality.knowledge_base_ids and not personality.associated_books:
            warnings.append("Personality has no associated knowledge base")
        
        # System prompt validation
        if not personality.system_prompt or len(personality.system_prompt.strip()) < 50:
            warnings.append("System prompt should be more detailed for better responses")
        
        # Calculate validation score
        score = self._calculate_validation_score(personality, errors, warnings)
        
        return PersonalityValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            score=score
        )
    
    # ==========================================
    # KNOWLEDGE BASE MANAGEMENT
    # ==========================================
    
    async def associate_knowledge_base(
        self,
        personality_id: str,
        knowledge_base_ids: List[str]
    ) -> bool:
        """Associate knowledge base with personality"""
        try:
            personality = await self.get_personality(personality_id)
            if not personality:
                raise ValueError(f"Personality {personality_id} not found")
            
            # Add new knowledge base IDs
            existing_ids = set(personality.knowledge_base_ids)
            new_ids = set(knowledge_base_ids)
            personality.knowledge_base_ids = list(existing_ids.union(new_ids))
            
            # Update personality
            await self.update_personality(personality_id, {'knowledge_base_ids': personality.knowledge_base_ids}, "system")
            
            logger.info(f"✅ Associated knowledge base with personality: {personality_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to associate knowledge base: {str(e)}")
            return False
    
    async def get_personality_knowledge_base(self, personality_id: str) -> List[str]:
        """Get knowledge base IDs for personality"""
        personality = await self.get_personality(personality_id)
        return personality.knowledge_base_ids if personality else []
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def _personality_to_config(self, personality: PersonalityProfile) -> PersonalityConfig:
        """Convert PersonalityProfile to PersonalityConfig for database storage"""
        return PersonalityConfig(
            id=personality.id,
            personalityName=personality.id,
            displayName=personality.display_name,
            description=personality.description,
            systemPrompt=personality.system_prompt,
            associatedBooks=personality.associated_books,
            vectorNamespace=personality.vector_namespace,
            isActive=personality.is_active,
            domain=personality.domain.value
        )
    
    def _config_to_personality(self, config: PersonalityConfig) -> PersonalityProfile:
        """Convert PersonalityConfig to PersonalityProfile"""
        # Use domain from config or detect from name
        try:
            domain = PersonalityDomain(config.domain)
        except (ValueError, AttributeError):
            # Fallback domain detection
            name_lower = config.personalityName.lower()
            if 'einstein' in name_lower:
                domain = PersonalityDomain.SCIENTIFIC
            elif 'lincoln' in name_lower:
                domain = PersonalityDomain.HISTORICAL
            elif 'marcus' in name_lower or 'aurelius' in name_lower:
                domain = PersonalityDomain.PHILOSOPHICAL
            else:
                domain = PersonalityDomain.SPIRITUAL
        
        return PersonalityProfile(
            id=config.id,
            name=config.personalityName,
            display_name=config.displayName,
            domain=domain,
            time_period="",
            description=config.description,
            system_prompt=config.systemPrompt,
            associated_books=config.associatedBooks,
            vector_namespace=config.vectorNamespace,
            is_active=config.isActive,
            created_at=config.createdAt or datetime.now().isoformat()
        )
    
    def _apply_search_filters(
        self,
        personalities: List[PersonalityProfile],
        filters: PersonalitySearchFilter
    ) -> List[PersonalityProfile]:
        """Apply search filters to personality list"""
        filtered = personalities
        
        if filters.domain:
            filtered = [p for p in filtered if p.domain == filters.domain]
        
        if filters.status:
            filtered = [p for p in filtered if p.status == filters.status]
        
        if filters.is_active is not None:
            filtered = [p for p in filtered if p.is_active == filters.is_active]
        
        if filters.expert_approved is not None:
            filtered = [p for p in filtered if p.expert_approved == filters.expert_approved]
        
        if filters.tags:
            filtered = [p for p in filtered if any(tag in p.tags for tag in filters.tags)]
        
        if filters.min_quality_score:
            filtered = [p for p in filtered if p.quality_score >= filters.min_quality_score]
        
        if filters.search_query:
            query_lower = filters.search_query.lower()
            filtered = [
                p for p in filtered
                if query_lower in p.name.lower() or
                   query_lower in p.description.lower() or
                   any(query_lower in area.lower() for area in p.expertise_areas)
            ]
        
        return filtered
    
    def _calculate_relevance(self, personality: PersonalityProfile, query: str) -> float:
        """Calculate personality relevance to query"""
        query_lower = query.lower()
        score = 0.0
        
        # Name match
        if query_lower in personality.name.lower() or query_lower in personality.display_name.lower():
            score += 10.0
        
        # Description match
        if query_lower in personality.description.lower():
            score += 5.0
        
        # Domain match
        if query_lower in personality.domain.value.lower():
            score += 8.0
        
        # Expertise area match
        for area in personality.expertise_areas:
            if query_lower in area.lower() or area.lower() in query_lower:
                score += 3.0
        
        # Cultural context match
        if personality.cultural_context and query_lower in personality.cultural_context.lower():
            score += 4.0
        
        # Keyword matching
        spiritual_keywords = ['spiritual', 'divine', 'god', 'meditation', 'dharma', 'karma']
        scientific_keywords = ['science', 'physics', 'theory', 'research', 'experiment']
        historical_keywords = ['history', 'leadership', 'democracy', 'president', 'war']
        philosophical_keywords = ['philosophy', 'wisdom', 'virtue', 'ethics', 'meaning']
        
        if personality.domain.value == 'spiritual' and any(kw in query_lower for kw in spiritual_keywords):
            score += 6.0
        elif personality.domain.value == 'scientific' and any(kw in query_lower for kw in scientific_keywords):
            score += 6.0
        elif personality.domain.value == 'historical' and any(kw in query_lower for kw in historical_keywords):
            score += 6.0
        elif personality.domain.value == 'philosophical' and any(kw in query_lower for kw in philosophical_keywords):
            score += 6.0
        
        # Quality bonus
        score += personality.quality_score / 20.0  # Normalize to 0-5 range
        
        return score
    
    def _calculate_validation_score(
        self,
        personality: PersonalityProfile,
        errors: List[str],
        warnings: List[str]
    ) -> float:
        """Calculate personality validation score"""
        base_score = 100.0
        
        # Deduct for errors
        base_score -= len(errors) * 20.0
        
        # Deduct for warnings
        base_score -= len(warnings) * 5.0
        
        # Bonus for completeness
        if personality.system_prompt and len(personality.system_prompt) > 100:
            base_score += 10.0
        
        if personality.knowledge_base_ids:
            base_score += 10.0
        
        if personality.expertise_areas:
            base_score += 5.0
        
        return max(0.0, min(100.0, base_score))
    
    async def _check_personality_dependencies(self, personality_id: str) -> List[str]:
        """Check for personality dependencies before deletion"""
        dependencies = []
        
        try:
            # Check for active conversations
            conversations = await self.db_service.get_conversations_by_personality(personality_id, limit=1)
            if conversations:
                dependencies.append("active_conversations")
            
            # Check for associated content
            texts = await self.db_service.get_texts_by_personality(personality_id, limit=1)
            if texts:
                dependencies.append("associated_content")
            
        except Exception as e:
            logger.warning(f"Failed to check dependencies for {personality_id}: {str(e)}")
        
        return dependencies
    
    # ==========================================
    # DOMAIN-SPECIFIC VALIDATORS
    # ==========================================
    
    async def _validate_spiritual_personality(self, personality: PersonalityProfile) -> Dict[str, List[str]]:
        """Validate spiritual personality"""
        errors = []
        warnings = []
        suggestions = []
        
        # Check for spiritual-specific attributes
        if not any(area in ['dharma', 'karma', 'devotion', 'meditation'] for area in personality.expertise_areas):
            warnings.append("Consider adding traditional spiritual expertise areas")
        
        if personality.cultural_context and 'spiritual' not in personality.cultural_context.lower():
            suggestions.append("Consider emphasizing spiritual cultural context")
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    async def _validate_scientific_personality(self, personality: PersonalityProfile) -> Dict[str, List[str]]:
        """Validate scientific personality"""
        errors = []
        warnings = []
        suggestions = []
        
        # Check for scientific rigor
        if not any(area in ['physics', 'chemistry', 'biology', 'mathematics'] for area in personality.expertise_areas):
            warnings.append("Consider adding specific scientific disciplines")
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    async def _validate_historical_personality(self, personality: PersonalityProfile) -> Dict[str, List[str]]:
        """Validate historical personality"""
        errors = []
        warnings = []
        suggestions = []
        
        # Check for historical context
        if not personality.time_period:
            errors.append("Historical personalities must have a time period specified")
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    async def _validate_philosophical_personality(self, personality: PersonalityProfile) -> Dict[str, List[str]]:
        """Validate philosophical personality"""
        errors = []
        warnings = []
        suggestions = []
        
        # Check for philosophical depth
        if not any(area in ['ethics', 'metaphysics', 'logic', 'epistemology'] for area in personality.expertise_areas):
            warnings.append("Consider adding specific philosophical areas")
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    async def _validate_literary_personality(self, personality: PersonalityProfile) -> Dict[str, List[str]]:
        """Validate literary personality"""
        return {'errors': [], 'warnings': [], 'suggestions': []}
    
    async def _validate_political_personality(self, personality: PersonalityProfile) -> Dict[str, List[str]]:
        """Validate political personality"""
        return {'errors': [], 'warnings': [], 'suggestions': []}


# Global personality service instance
personality_service = PersonalityService()