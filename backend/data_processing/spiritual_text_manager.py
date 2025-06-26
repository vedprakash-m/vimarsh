"""
Spiritual Text Data Source Manager
Task 8.8: Load and chunk source texts into production Cosmos DB

Manages the loading and validation of spiritual text sources,
ensuring proper format, metadata, and spiritual content authenticity.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SpiritualTextSource:
    """Represents a spiritual text source with metadata."""
    
    source_id: str
    title: str
    author: str
    translator: str
    source_type: str  # 'bhagavad_gita', 'mahabharata', 'srimad_bhagavatam', etc.
    language: str
    file_path: str
    
    # Legal and attribution information
    copyright_status: str  # 'public_domain', 'fair_use', 'licensed'
    publication_year: Optional[int] = None
    attribution_required: bool = True
    attribution_text: Optional[str] = None
    
    # Content metadata
    chapters: Optional[List[str]] = None
    verses_count: Optional[int] = None
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    
    # Quality and validation
    content_hash: Optional[str] = None
    validated: bool = False
    validation_date: Optional[str] = None
    expert_reviewed: bool = False
    
    # Processing metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at


class SpiritualTextDataManager:
    """
    Manages spiritual text sources for production data loading.
    Handles validation, metadata extraction, and content preparation.
    """
    
    def __init__(self, sources_directory: str = "data/sources"):
        """
        Initialize the data manager.
        
        Args:
            sources_directory: Directory containing spiritual text files
        """
        self.sources_directory = Path(sources_directory)
        self.sources_directory.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.sources_directory / "sources_metadata.json"
        self.sources: Dict[str, SpiritualTextSource] = {}
        
        # Load existing metadata
        self._load_metadata()
        
        logger.info(f"Initialized SpiritualTextDataManager with {len(self.sources)} sources")
    
    def register_source(self, source: SpiritualTextSource) -> bool:
        """
        Register a new spiritual text source.
        
        Args:
            source: SpiritualTextSource instance
            
        Returns:
            True if successfully registered, False otherwise
        """
        try:
            # Validate file exists
            file_path = self.sources_directory / source.file_path
            if not file_path.exists():
                logger.error(f"Source file not found: {file_path}")
                return False
            
            # Calculate content hash
            source.content_hash = self._calculate_file_hash(file_path)
            
            # Extract content metadata
            content_stats = self._analyze_content(file_path)
            source.word_count = content_stats['word_count']
            source.character_count = content_stats['character_count']
            source.verses_count = content_stats.get('verses_count')
            
            # Update timestamp
            source.updated_at = datetime.now(timezone.utc).isoformat()
            
            # Register source
            self.sources[source.source_id] = source
            self._save_metadata()
            
            logger.info(f"Registered source: {source.title} ({source.source_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register source {source.source_id}: {str(e)}")
            return False
    
    def get_source(self, source_id: str) -> Optional[SpiritualTextSource]:
        """Get a registered source by ID."""
        return self.sources.get(source_id)
    
    def list_sources(self, source_type: str = None, validated_only: bool = False) -> List[SpiritualTextSource]:
        """
        List registered sources with optional filtering.
        
        Args:
            source_type: Filter by source type (e.g., 'bhagavad_gita')
            validated_only: Only return validated sources
            
        Returns:
            List of matching sources
        """
        sources = list(self.sources.values())
        
        if source_type:
            sources = [s for s in sources if s.source_type == source_type]
        
        if validated_only:
            sources = [s for s in sources if s.validated]
        
        return sources
    
    def validate_source(self, source_id: str) -> Dict[str, Any]:
        """
        Validate a spiritual text source for production readiness.
        
        Args:
            source_id: ID of the source to validate
            
        Returns:
            Validation results with details
        """
        source = self.get_source(source_id)
        if not source:
            return {"valid": False, "error": "Source not found"}
        
        validation_results = {
            "source_id": source_id,
            "valid": True,
            "warnings": [],
            "errors": [],
            "checks": {}
        }
        
        try:
            file_path = self.sources_directory / source.file_path
            
            # Check 1: File accessibility
            validation_results["checks"]["file_accessible"] = file_path.exists() and file_path.is_file()
            if not validation_results["checks"]["file_accessible"]:
                validation_results["errors"].append("Source file not accessible")
                validation_results["valid"] = False
            
            # Check 2: Content hash integrity
            current_hash = self._calculate_file_hash(file_path)
            validation_results["checks"]["content_integrity"] = current_hash == source.content_hash
            if not validation_results["checks"]["content_integrity"]:
                validation_results["warnings"].append("Content hash mismatch - file may have been modified")
            
            # Check 3: Copyright status
            validation_results["checks"]["copyright_clear"] = source.copyright_status == "public_domain"
            if not validation_results["checks"]["copyright_clear"]:
                validation_results["warnings"].append(f"Copyright status: {source.copyright_status}")
            
            # Check 4: Content quality
            content_quality = self._validate_content_quality(file_path, source.source_type)
            validation_results["checks"]["content_quality"] = content_quality["score"] >= 0.8
            validation_results["content_quality_details"] = content_quality
            
            if not validation_results["checks"]["content_quality"]:
                validation_results["warnings"].append("Content quality below threshold")
            
            # Check 5: Spiritual authenticity markers
            authenticity_check = self._validate_spiritual_authenticity(file_path, source.source_type)
            validation_results["checks"]["spiritual_authenticity"] = authenticity_check["authentic"]
            validation_results["authenticity_details"] = authenticity_check
            
            # Update validation status
            if validation_results["valid"] and len(validation_results["errors"]) == 0:
                source.validated = True
                source.validation_date = datetime.now(timezone.utc).isoformat()
                self._save_metadata()
                logger.info(f"Source {source_id} validated successfully")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Validation failed for source {source_id}: {str(e)}")
            return {
                "valid": False,
                "error": str(e),
                "source_id": source_id
            }
    
    def load_source_content(self, source_id: str) -> Optional[str]:
        """
        Load the content of a registered source.
        
        Args:
            source_id: ID of the source to load
            
        Returns:
            Source content as string, or None if not found
        """
        source = self.get_source(source_id)
        if not source:
            logger.error(f"Source not found: {source_id}")
            return None
        
        try:
            file_path = self.sources_directory / source.file_path
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Loaded content for {source_id}: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Failed to load content for {source_id}: {str(e)}")
            return None
    
    def get_production_ready_sources(self) -> List[SpiritualTextSource]:
        """Get all sources that are ready for production loading."""
        return [
            source for source in self.sources.values()
            if source.validated and source.copyright_status == "public_domain"
        ]
    
    def _load_metadata(self):
        """Load sources metadata from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                for source_data in metadata.get('sources', []):
                    source = SpiritualTextSource(**source_data)
                    self.sources[source.source_id] = source
                
                logger.info(f"Loaded metadata for {len(self.sources)} sources")
                
            except Exception as e:
                logger.warning(f"Failed to load metadata: {str(e)}")
    
    def _save_metadata(self):
        """Save sources metadata to file."""
        try:
            metadata = {
                "version": "1.0",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "sources": [asdict(source) for source in self.sources.values()]
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Failed to save metadata: {str(e)}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _analyze_content(self, file_path: Path) -> Dict[str, Any]:
        """Analyze content to extract basic statistics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            words = content.split()
            lines = content.split('\\n')
            
            # Count verses (lines that match verse patterns)
            verse_patterns = [
                lambda line: any(c.isdigit() for c in line[:10]),  # Lines starting with numbers
                lambda line: line.strip().endswith(':'),           # Lines ending with colons
            ]
            
            verses_count = 0
            for line in lines:
                line = line.strip()
                if line and any(pattern(line) for pattern in verse_patterns):
                    verses_count += 1
            
            return {
                "word_count": len(words),
                "character_count": len(content),
                "line_count": len(lines),
                "verses_count": verses_count if verses_count > 0 else None
            }
            
        except Exception as e:
            logger.warning(f"Content analysis failed: {str(e)}")
            return {"word_count": 0, "character_count": 0}
    
    def _validate_content_quality(self, file_path: Path, source_type: str) -> Dict[str, Any]:
        """Validate content quality based on source type."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            quality_score = 1.0
            issues = []
            
            # Basic quality checks
            if len(content) < 1000:
                quality_score -= 0.3
                issues.append("Content too short")
            
            # Check for proper structure
            if source_type == "bhagavad_gita":
                if "Chapter" not in content and "Shloka" not in content:
                    quality_score -= 0.2
                    issues.append("Missing chapter/verse structure")
            
            elif source_type == "mahabharata":
                if "Book" not in content and "Parva" not in content:
                    quality_score -= 0.2
                    issues.append("Missing book/parva structure")
            
            # Check for Sanskrit terms (indicates authentic content)
            sanskrit_terms = ["dharma", "karma", "Arjuna", "Krishna", "yoga", "atman"]
            found_terms = sum(1 for term in sanskrit_terms if term in content)
            if found_terms < 3:
                quality_score -= 0.1
                issues.append("Few Sanskrit terms found")
            
            return {
                "score": max(0.0, quality_score),
                "issues": issues,
                "sanskrit_terms_found": found_terms
            }
            
        except Exception as e:
            return {"score": 0.0, "error": str(e)}
    
    def _validate_spiritual_authenticity(self, file_path: Path, source_type: str) -> Dict[str, Any]:
        """Validate spiritual authenticity of content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            authenticity_markers = {
                "bhagavad_gita": [
                    "krishna", "arjuna", "kurukshetra", "dharma", "yoga",
                    "supreme personality", "bhagavan", "karma"
                ],
                "mahabharata": [
                    "pandava", "kaurava", "bhishma", "vyasa", "dharma",
                    "yudhishthira", "duryodhana", "kurukshetra"
                ],
                "srimad_bhagavatam": [
                    "krishna", "vrindavan", "gopi", "bhakti", "vishnu",
                    "narada", "brahma", "devotee"
                ]
            }
            
            expected_markers = authenticity_markers.get(source_type, [])
            found_markers = [marker for marker in expected_markers if marker in content]
            
            authenticity_score = len(found_markers) / len(expected_markers) if expected_markers else 0.0
            
            return {
                "authentic": authenticity_score >= 0.6,
                "score": authenticity_score,
                "expected_markers": expected_markers,
                "found_markers": found_markers
            }
            
        except Exception as e:
            return {"authentic": False, "error": str(e)}


def create_default_sources() -> List[SpiritualTextSource]:
    """Create default source configurations for available texts."""
    
    return [
        SpiritualTextSource(
            source_id="bhagavad_gita_sample",
            title="Bhagavad Gita (Sample Chapters)",
            author="Vyasa",
            translator="A.C. Bhaktivedanta Swami Prabhupada",
            source_type="bhagavad_gita",
            language="English",
            file_path="bhagavad_gita_sample.txt",
            copyright_status="public_domain",
            publication_year=1972,
            attribution_text="Bhagavad-gita As It Is by A.C. Bhaktivedanta Swami Prabhupada"
        ),
        
        SpiritualTextSource(
            source_id="mahabharata_sample",
            title="Mahabharata (Sample Books)",
            author="Vyasa",
            translator="Kisari Mohan Ganguli",
            source_type="mahabharata",
            language="English",
            file_path="mahabharata_sample.txt",
            copyright_status="public_domain",
            publication_year=1896,
            attribution_text="The Mahabharata translated by Kisari Mohan Ganguli (1883-1896)"
        )
    ]


if __name__ == "__main__":
    # Demo usage
    manager = SpiritualTextDataManager()
    
    # Register default sources
    default_sources = create_default_sources()
    for source in default_sources:
        success = manager.register_source(source)
        print(f"Registered {source.source_id}: {success}")
    
    # Validate sources
    for source_id in ["bhagavad_gita_sample", "mahabharata_sample"]:
        validation = manager.validate_source(source_id)
        print(f"\\nValidation for {source_id}:")
        print(f"  Valid: {validation['valid']}")
        print(f"  Warnings: {len(validation.get('warnings', []))}")
        print(f"  Errors: {len(validation.get('errors', []))}")
