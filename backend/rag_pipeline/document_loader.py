"""
Spiritual Document Loader

Handles loading and initial processing of spiritual texts from various sources
with metadata extraction and format detection.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import mimetypes
import chardet
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Metadata for loaded spiritual documents"""
    filename: str
    file_size: int
    encoding: str
    mime_type: str
    language: Optional[str] = None
    source_tradition: Optional[str] = None  # e.g., "Hinduism", "Buddhism"
    text_type: Optional[str] = None  # e.g., "scripture", "commentary"
    author: Optional[str] = None
    translator: Optional[str] = None
    publication_info: Optional[str] = None


class SpiritualDocumentLoader:
    """
    Loads spiritual documents from various sources with proper encoding handling
    and metadata extraction for cultural context preservation.
    """
    
    def __init__(self):
        # Supported file types
        self.supported_extensions = {'.txt', '.md', '.json'}
        
        # Pattern recognition for spiritual texts
        self.text_patterns = {
            'bhagavad_gita': [
                r'bhagavad[- ]?gita',
                r'gita',
                r'krishna.*arjuna',
                r'chapter.*verse'
            ],
            'mahabharata': [
                r'mahabharata',
                r'bharata',
                r'pandava',
                r'kurukshetra'
            ],
            'srimad_bhagavatam': [
                r'srimad[- ]?bhagavatam',
                r'bhagavatam',
                r'bhagavata[- ]?purana'
            ],
            'upanishads': [
                r'upanishad',
                r'isa.*upanishad',
                r'mundaka',
                r'mandukya'
            ],
            'vedas': [
                r'rig[- ]?veda',
                r'sama[- ]?veda',
                r'yajur[- ]?veda',
                r'atharva[- ]?veda',
                r'vedic'
            ]
        }
        
        # Language detection patterns
        self.language_patterns = {
            'sanskrit': [
                r'[\u0900-\u097F]+',  # Devanagari
                r'\b(?:dharma|karma|moksha|samsara|brahman|atman)\b'
            ],
            'hindi': [
                r'[\u0900-\u097F]+',  # Also uses Devanagari
                r'\b(?:mai|hai|ke|ki|ka|se|me)\b'
            ],
            'english': [
                r'\b(?:the|and|or|but|in|on|at|to|for|of|with|by)\b'
            ]
        }
    
    def detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding, with special handling for Sanskrit/Hindi texts
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding string
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB for detection
            
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0)
            
            # For low confidence, default to UTF-8 (common for Sanskrit texts)
            if confidence < 0.7:
                logger.warning(f"Low encoding confidence ({confidence:.2f}) for {file_path}, defaulting to UTF-8")
                encoding = 'utf-8'
            
            logger.info(f"Detected encoding {encoding} with confidence {confidence:.2f} for {file_path}")
            return encoding
            
        except Exception as e:
            logger.warning(f"Encoding detection failed for {file_path}: {e}, defaulting to UTF-8")
            return 'utf-8'
    
    def identify_text_type(self, content: str, filename: str) -> Dict[str, str]:
        """
        Identify the type and tradition of spiritual text
        
        Args:
            content: Text content
            filename: Filename for additional context
            
        Returns:
            Dictionary with text_type and source_tradition
        """
        import re
        
        content_lower = content.lower()
        filename_lower = filename.lower()
        combined_text = f"{content_lower} {filename_lower}"
        
        identified_type = 'unknown'
        tradition = 'unknown'
        
        # Check against known text patterns
        for text_type, patterns in self.text_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    identified_type = text_type
                    if text_type in ['bhagavad_gita', 'mahabharata', 'srimad_bhagavatam', 'upanishads', 'vedas']:
                        tradition = 'hinduism'  # Most of our initial texts are Hindu
                    break
            if identified_type != 'unknown':
                break
        
        # Additional tradition detection (more specific first)
        if any(term in combined_text for term in ['krishna', 'arjuna', 'gita', 'bhagavad', 'mahabharata', 'vedas', 'upanishad']):
            tradition = 'hinduism'
        elif any(term in combined_text for term in ['buddha', 'sangha', 'nirvana', 'bodhisattva']):
            tradition = 'buddhism'
        elif any(term in combined_text for term in ['guru', 'sikh', 'waheguru']):
            tradition = 'sikhism'
        elif any(term in combined_text for term in ['jain', 'tirthankara', 'ahimsa']):
            tradition = 'jainism'
        
        return {
            'text_type': identified_type,
            'source_tradition': tradition
        }
    
    def detect_language(self, content: str) -> str:
        """
        Detect primary language of the text
        
        Args:
            content: Text content
            
        Returns:
            Detected language code
        """
        import re
        
        # Count matches for each language
        language_scores = {}
        
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches
            language_scores[lang] = score
        
        # Return language with highest score
        if language_scores:
            detected_lang = max(language_scores, key=language_scores.get)
            if language_scores[detected_lang] > 0:
                return detected_lang
        
        return 'english'  # Default fallback
    
    def load_text_file(self, file_path: Union[str, Path]) -> tuple[str, DocumentMetadata]:
        """
        Load a text file with proper encoding and metadata extraction
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Tuple of (content, metadata)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Detect encoding
        encoding = self.detect_encoding(file_path)
        
        try:
            # Load content
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Get file metadata
            file_stat = file_path.stat()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Analyze content
            text_info = self.identify_text_type(content, file_path.name)
            detected_language = self.detect_language(content)
            
            # Create metadata
            metadata = DocumentMetadata(
                filename=file_path.name,
                file_size=file_stat.st_size,
                encoding=encoding,
                mime_type=mime_type or 'text/plain',
                language=detected_language,
                source_tradition=text_info['source_tradition'],
                text_type=text_info['text_type']
            )
            
            logger.info(f"Loaded {file_path.name}: {len(content)} chars, "
                       f"type={metadata.text_type}, tradition={metadata.source_tradition}, "
                       f"language={metadata.language}")
            
            return content, metadata
            
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode {file_path} with {encoding}: {e}")
            # Try fallback encodings
            for fallback_encoding in ['utf-8', 'latin-1', 'cp1252']:
                if fallback_encoding != encoding:
                    try:
                        with open(file_path, 'r', encoding=fallback_encoding) as f:
                            content = f.read()
                        logger.warning(f"Successfully read {file_path} with fallback encoding {fallback_encoding}")
                        
                        # Update metadata with corrected encoding
                        file_stat = file_path.stat()
                        mime_type, _ = mimetypes.guess_type(str(file_path))
                        text_info = self.identify_text_type(content, file_path.name)
                        detected_language = self.detect_language(content)
                        
                        metadata = DocumentMetadata(
                            filename=file_path.name,
                            file_size=file_stat.st_size,
                            encoding=fallback_encoding,
                            mime_type=mime_type or 'text/plain',
                            language=detected_language,
                            source_tradition=text_info['source_tradition'],
                            text_type=text_info['text_type']
                        )
                        
                        return content, metadata
                        
                    except UnicodeDecodeError:
                        continue
            
            raise ValueError(f"Could not decode {file_path} with any supported encoding")
    
    def load_directory(self, directory_path: Union[str, Path]) -> List[tuple[str, DocumentMetadata]]:
        """
        Load all supported text files from a directory
        
        Args:
            directory_path: Path to directory containing text files
            
        Returns:
            List of (content, metadata) tuples
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not directory_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        documents = []
        
        # Find all supported files
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    content, metadata = self.load_text_file(file_path)
                    documents.append((content, metadata))
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")
                    continue
        
        logger.info(f"Loaded {len(documents)} documents from {directory_path}")
        return documents
    
    def validate_spiritual_content(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """
        Validate that content appears to be legitimate spiritual text
        
        Args:
            content: Text content
            metadata: Document metadata
            
        Returns:
            Validation results dictionary
        """
        validation = {
            'is_valid': True,
            'confidence': 1.0,
            'issues': [],
            'recommendations': []
        }
        
        # Basic content checks
        if len(content.strip()) < 100:
            validation['issues'].append('Content too short for spiritual text')
            validation['confidence'] *= 0.5
        
        # Check for spiritual vocabulary
        spiritual_terms = ['dharma', 'karma', 'god', 'divine', 'sacred', 'holy', 'spiritual']
        found_terms = sum(1 for term in spiritual_terms if term.lower() in content.lower())
        
        if found_terms == 0:
            validation['issues'].append('No spiritual vocabulary detected')
            validation['confidence'] *= 0.3
        elif found_terms < 3:
            validation['recommendations'].append('Limited spiritual vocabulary - verify content authenticity')
            validation['confidence'] *= 0.8
        
        # Check for proper structure
        if metadata.text_type in ['bhagavad_gita', 'srimad_bhagavatam']:
            if 'chapter' not in content.lower() and 'verse' not in content.lower():
                validation['issues'].append('Expected chapter/verse structure not found')
                validation['confidence'] *= 0.6
        
        # Flag if confidence is too low
        if validation['confidence'] < 0.5:
            validation['is_valid'] = False
        
        return validation
