"""
Source Verification API Endpoints for Admin Content Management
Handles authentication verification, citation management, and content authenticity tracking
"""

import json
import os
import logging
from typing import Dict, List, Any
from datetime import datetime, timezone
from azure.functions import HttpRequest, HttpResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SourceVerificationManager:
    """Manages source verification and authenticity tracking for spiritual texts"""
    
    def __init__(self):
        self.sources_registry_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "docs", 
            "AUTHORITATIVE_SOURCES_REGISTRY.md"
        )
        self.spiritual_texts_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "data", 
            "spiritual-texts.json"
        )
    
    def get_authority_levels(self) -> Dict[str, List[str]]:
        """Get categorized authority levels for sources"""
        return {
            "primary": [
                "Bhagavad Gita",
                "Dhammapada", 
                "Gospel of Matthew",
                "Gospel of John",
                "Meditations (Marcus Aurelius)",
                "Tao Te Ching",
                "Essential Rumi (Barks translation)"
            ],
            "secondary": [
                "Srimad Bhagavatam",
                "Einstein's Letters to Born",
                "Lincoln's Speeches",
                "Rumi: Selected Poems"
            ],
            "tertiary": [
                "Commentary texts",
                "Secondary translations",
                "Scholarly interpretations"
            ]
        }
    
    def validate_source_citation(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate source citation for content authenticity"""
        try:
            # Extract source information
            source = content_data.get('source', '')
            chapter = content_data.get('chapter', '')
            verse = content_data.get('verse', '')
            personality = content_data.get('personality', '')
            
            # Determine authority level
            authority_levels = self.get_authority_levels()
            authority_level = 'unknown'
            
            for level, sources in authority_levels.items():
                if any(auth_source.lower() in source.lower() for auth_source in sources):
                    authority_level = level
                    break
            
            # Validation score based on completeness
            validation_score = 0
            if source:
                validation_score += 30
            if chapter:
                validation_score += 25
            if verse:
                validation_score += 25
            if authority_level != 'unknown':
                validation_score += 20
            
            validation_result = {
                "is_valid": validation_score >= 60,
                "authority_level": authority_level,
                "validation_score": validation_score,
                "missing_elements": [],
                "recommendations": []
            }
            
            # Add recommendations for improvement
            if not source:
                validation_result["missing_elements"].append("source")
                validation_result["recommendations"].append("Add primary source reference")
            
            if not chapter and personality in ['Krishna', 'Jesus', 'Marcus Aurelius', 'Lao Tzu']:
                validation_result["missing_elements"].append("chapter")
                validation_result["recommendations"].append("Include chapter reference for better authenticity")
            
            if not verse and personality in ['Krishna', 'Buddha', 'Jesus']:
                validation_result["missing_elements"].append("verse")
                validation_result["recommendations"].append("Include verse number for precise citation")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating source citation: {str(e)}")
            return {
                "is_valid": False,
                "authority_level": "unknown",
                "validation_score": 0,
                "error": str(e)
            }
    
    def get_personality_source_requirements(self, personality: str) -> Dict[str, Any]:
        """Get specific source requirements for each personality"""
        requirements = {
            "Krishna": {
                "primary_sources": ["Bhagavad Gita", "Srimad Bhagavatam"],
                "required_fields": ["source", "chapter", "verse"],
                "citation_format": "Bhagavad Gita Chapter X, Verse Y"
            },
            "Buddha": {
                "primary_sources": ["Dhammapada", "Tripitaka"],
                "required_fields": ["source", "verse"],
                "citation_format": "Dhammapada Verse X"
            },
            "Jesus": {
                "primary_sources": ["Gospel of Matthew", "Gospel of Mark", "Gospel of Luke", "Gospel of John"],
                "required_fields": ["source", "chapter", "verse"],
                "citation_format": "Gospel of John Chapter X:Y"
            },
            "Einstein": {
                "primary_sources": ["Scientific Papers", "Letters to Born", "Ideas and Opinions"],
                "required_fields": ["source", "date"],
                "citation_format": "Letter to Max Born, Date"
            },
            "Lincoln": {
                "primary_sources": ["Gettysburg Address", "Second Inaugural Address", "Presidential Papers"],
                "required_fields": ["source", "date"],
                "citation_format": "Speech/Document Title, Date"
            },
            "Marcus Aurelius": {
                "primary_sources": ["Meditations"],
                "required_fields": ["source", "book", "chapter"],
                "citation_format": "Meditations Book X, Chapter Y"
            },
            "Lao Tzu": {
                "primary_sources": ["Tao Te Ching"],
                "required_fields": ["source", "chapter"],
                "citation_format": "Tao Te Ching Chapter X"
            },
            "Rumi": {
                "primary_sources": ["Essential Rumi", "Selected Poems"],
                "required_fields": ["source", "poem_title"],
                "citation_format": "Poem Title from Collection"
            }
        }
        
        return requirements.get(personality, {
            "primary_sources": [],
            "required_fields": ["source"],
            "citation_format": "Source Title"
        })

def verify_source_citation(req: HttpRequest) -> HttpResponse:
    """Endpoint to verify source citation for content authenticity"""
    try:
        # Parse request
        if req.method != 'POST':
            return HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                headers={"Content-Type": "application/json"}
            )
        
        # Get request data
        try:
            content_data = req.get_json()
        except ValueError:
            return HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        if not content_data:
            return HttpResponse(
                json.dumps({"error": "No data provided"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Initialize source manager
        source_manager = SourceVerificationManager()
        
        # Validate citation
        validation_result = source_manager.validate_source_citation(content_data)
        
        # Add timestamp
        validation_result["verified_at"] = datetime.now(timezone.utc).isoformat()
        
        return HttpResponse(
            json.dumps(validation_result),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"Error in verify_source_citation: {str(e)}")
        return HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

def get_personality_requirements(req: HttpRequest) -> HttpResponse:
    """Endpoint to get source requirements for a specific personality"""
    try:
        # Parse query parameters
        personality = req.params.get('personality', '')
        
        if not personality:
            return HttpResponse(
                json.dumps({"error": "Personality parameter required"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Initialize source manager
        source_manager = SourceVerificationManager()
        
        # Get requirements
        requirements = source_manager.get_personality_source_requirements(personality)
        
        # Add authority levels
        requirements["authority_levels"] = source_manager.get_authority_levels()
        
        return HttpResponse(
            json.dumps(requirements),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"Error in get_personality_requirements: {str(e)}")
        return HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

def get_authority_levels(req: HttpRequest) -> HttpResponse:
    """Endpoint to get all authority levels and their associated sources"""
    try:
        # Initialize source manager
        source_manager = SourceVerificationManager()
        
        # Get authority levels
        authority_levels = source_manager.get_authority_levels()
        
        # Add metadata
        response_data = {
            "authority_levels": authority_levels,
            "description": {
                "primary": "Original texts and primary sources with highest authenticity",
                "secondary": "Authoritative secondary sources and reliable translations",
                "tertiary": "Commentary, interpretations, and scholarly works"
            },
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"Error in get_authority_levels: {str(e)}")
        return HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )
