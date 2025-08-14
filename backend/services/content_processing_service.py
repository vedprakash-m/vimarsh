"""
Content Processing Service for Personality Content
Handles text processing, chunking, quality validation, and embedding preparation
"""

import os
import json
import logging
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import tiktoken

logger = logging.getLogger(__name__)

@dataclass
class ContentChunk:
    """Represents a processed content chunk"""
    chunk_id: str
    personality_id: str
    source_id: str
    chunk_text: str
    chunk_index: int
    token_count: int
    character_count: int
    quality_score: float
    relevance_score: float
    metadata: Dict[str, Any]
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class ProcessingMetrics:
    """Content processing metrics"""
    source_files_processed: int = 0
    total_chunks_created: int = 0
    total_tokens: int = 0
    total_characters: int = 0
    average_chunk_quality: float = 0.0
    processing_time_minutes: float = 0.0
    error_count: int = 0

class ContentProcessingService:
    """Service for processing personality content into chunks"""
    
    def __init__(self, data_dir: str = "/Users/ved/Apps/vimarsh/data"):
        self.data_dir = Path(data_dir)
        self.sources_dir = self.data_dir / "sources" / "personalities"
        self.processed_dir = self.data_dir / "processed" / "personalities"
        self.chunks_dir = self.data_dir / "chunks"
        
        # Create directories
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Could not load tiktoken encoder: {e}")
            self.tokenizer = None
        
        # Download required NLTK data
        self._setup_nltk()
        
        # Domain-specific processing strategies
        self.domain_strategies = {
            "literary": {
                "chunk_size": 800,  # Longer chunks for poetry/narrative
                "overlap": 100,
                "split_patterns": [r'\n\n\n+', r'\n\n', r'\. [A-Z]', r'\n[A-Z]'],
                "preserve_patterns": [r'Act \d+', r'Scene \d+', r'Chapter \d+', r'Sonnet \d+']
            },
            "philosophical": {
                "chunk_size": 600,  # Medium chunks for arguments
                "overlap": 80,
                "split_patterns": [r'\n\n+', r'\. [A-Z]', r'; [A-Z]', r'\?\s+[A-Z]'],
                "preserve_patterns": [r'Proposition \d+', r'Book \d+', r'Part \d+']
            },
            "scientific": {
                "chunk_size": 700,  # Technical content needs context
                "overlap": 90,
                "split_patterns": [r'\n\n+', r'\. [A-Z]', r'Theorem \d+', r'Proposition \d+'],
                "preserve_patterns": [r'Figure \d+', r'Diagram \d+', r'Experiment \d+']
            },
            "historical": {
                "chunk_size": 500,  # Shorter for speeches/letters
                "overlap": 60,
                "split_patterns": [r'\n\n+', r'\. [A-Z]', r'[.!?]\s+[A-Z]'],
                "preserve_patterns": [r'Chapter \d+', r'\d{4}-\d{2}-\d{2}', r'Letter to']
            },
            "spiritual": {
                "chunk_size": 400,  # Short for verses/teachings
                "overlap": 50,
                "split_patterns": [r'\n\n+', r'\. [A-Z]', r'Verse \d+', r'\d+\.\d+'],
                "preserve_patterns": [r'Chapter \d+', r'Verse \d+', r'Sutra \d+']
            }
        }

    def _setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                logger.info("✅ NLTK data downloaded")
            except Exception as e:
                logger.warning(f"Could not download NLTK data: {e}")

    def process_personality_content(self, personality_id: str) -> Tuple[bool, str, ProcessingMetrics]:
        """Process all content files for a personality into chunks"""
        logger.info(f"🔄 Processing content for {personality_id}")
        
        personality_source_dir = self.sources_dir / personality_id
        if not personality_source_dir.exists():
            return False, f"No source directory found for {personality_id}", ProcessingMetrics()
        
        personality_output_dir = self.processed_dir / personality_id
        personality_output_dir.mkdir(exist_ok=True)
        
        metrics = ProcessingMetrics()
        all_chunks = []
        errors = []
        
        # Get domain for processing strategy
        domain = self._detect_domain(personality_id)
        strategy = self.domain_strategies.get(domain, self.domain_strategies["philosophical"])
        
        # Process each source file
        for source_file in personality_source_dir.glob("*.txt"):
            try:
                logger.info(f"📄 Processing file: {source_file.name}")
                
                # Read source content
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Clean and preprocess content
                cleaned_content = self._clean_content(content, domain)
                
                # Create chunks
                chunks = self._create_chunks(
                    cleaned_content, 
                    personality_id,
                    source_file.stem,
                    strategy
                )
                
                all_chunks.extend(chunks)
                metrics.source_files_processed += 1
                metrics.total_chunks_created += len(chunks)
                
                logger.info(f"✅ Created {len(chunks)} chunks from {source_file.name}")
                
            except Exception as e:
                error_msg = f"Error processing {source_file.name}: {str(e)}"
                errors.append(error_msg)
                metrics.error_count += 1
                logger.error(error_msg)
        
        # Calculate quality scores and metrics
        if all_chunks:
            self._calculate_quality_scores(all_chunks, domain)
            metrics.total_tokens = sum(chunk.token_count for chunk in all_chunks)
            metrics.total_characters = sum(chunk.character_count for chunk in all_chunks)
            metrics.average_chunk_quality = sum(chunk.quality_score for chunk in all_chunks) / len(all_chunks)
        
        # Save processed chunks
        chunks_file = personality_output_dir / f"{personality_id}_chunks.jsonl"
        success = self._save_chunks(all_chunks, chunks_file)
        
        if not success:
            return False, "Failed to save processed chunks", metrics
        
        # Save processing summary
        summary = {
            "personality_id": personality_id,
            "domain": domain,
            "processing_strategy": strategy,
            "metrics": asdict(metrics),
            "chunks_file": str(chunks_file),
            "errors": errors,
            "processed_at": datetime.now().isoformat()
        }
        
        summary_file = personality_output_dir / f"{personality_id}_processing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        status = "success" if not errors else "partial_success"
        message = f"Processed {metrics.source_files_processed} files into {metrics.total_chunks_created} chunks"
        if errors:
            message += f" with {len(errors)} errors"
        
        return len(errors) == 0, message, metrics

    def _detect_domain(self, personality_id: str) -> str:
        """Detect personality domain based on ID"""
        domain_mapping = {
            "william_shakespeare": "literary",
            "rabindranath_tagore": "literary",
            "socrates": "philosophical", 
            "plato": "philosophical",
            "aristotle": "philosophical",
            "sigmund_freud": "philosophical",
            "leonardo_da_vinci": "scientific",
            "archimedes": "scientific",
            "benjamin_franklin": "historical",
            "martin_luther_king": "historical",
            "nelson_mandela": "historical",
            "george_washington": "historical",
            "gandhi": "historical",
            "swami_vivekananda": "historical"
        }
        return domain_mapping.get(personality_id, "philosophical")

    def _clean_content(self, content: str, domain: str) -> str:
        """Clean and preprocess content based on domain"""
        # Remove project gutenberg headers/footers
        content = re.sub(r'\*\*\* START OF .*? \*\*\*.*?\*\*\* END OF .*? \*\*\*', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Domain-specific cleaning
        if domain == "literary":
            # Preserve poetry formatting
            content = re.sub(r'\n([A-Z][A-Z ]+)\n', r'\n\n\1\n\n', content)  # Act/Scene headers
        elif domain == "philosophical":
            # Preserve numbered sections
            content = re.sub(r'\n(\d+\.)', r'\n\n\1', content)
        elif domain == "scientific":
            # Preserve mathematical notation
            content = re.sub(r'([a-z])\s*=\s*([a-z])', r'\1 = \2', content)
        
        # Remove page numbers and artifacts
        content = re.sub(r'\n\s*\d+\s*\n', '\n', content)
        content = re.sub(r'\[Pg \d+\]', '', content)
        content = re.sub(r'_+', '', content)
        
        return content.strip()

    def _create_chunks(self, content: str, personality_id: str, source_id: str, strategy: Dict[str, Any]) -> List[ContentChunk]:
        """Create chunks from content using domain-specific strategy"""
        chunks = []
        chunk_size = strategy["chunk_size"]
        overlap = strategy["overlap"]
        
        # Split into sentences first
        try:
            sentences = sent_tokenize(content)
        except:
            # Fallback if NLTK not available
            sentences = re.split(r'[.!?]+\s+', content)
        
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_tokens = self._count_tokens(sentence)
            
            # Check if adding this sentence would exceed chunk size
            if current_tokens + sentence_tokens > chunk_size and current_chunk:
                # Create chunk
                chunk = self._create_chunk(
                    current_chunk.strip(),
                    personality_id,
                    source_id,
                    chunk_index
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, overlap)
                current_chunk = overlap_text + " " + sentence
                current_tokens = self._count_tokens(current_chunk)
            else:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk(
                current_chunk.strip(),
                personality_id,
                source_id,
                chunk_index
            )
            chunks.append(chunk)
        
        return chunks

    def _create_chunk(self, text: str, personality_id: str, source_id: str, index: int) -> ContentChunk:
        """Create a ContentChunk object"""
        chunk_id = hashlib.md5(f"{personality_id}_{source_id}_{index}_{text[:100]}".encode()).hexdigest()[:16]
        
        return ContentChunk(
            chunk_id=chunk_id,
            personality_id=personality_id,
            source_id=source_id,
            chunk_text=text,
            chunk_index=index,
            token_count=self._count_tokens(text),
            character_count=len(text),
            quality_score=0.0,  # Will be calculated later
            relevance_score=0.0,  # Will be calculated later
            metadata={
                "domain": self._detect_domain(personality_id),
                "source_type": "text",
                "language": "en",
                "has_quotes": '"' in text or "'" in text,
                "has_dates": bool(re.search(r'\d{4}', text)),
                "word_count": len(text.split())
            }
        )

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except:
                pass
        
        # Fallback: approximate token count
        return len(text.split()) * 1.3  # Rough approximation

    def _get_overlap_text(self, text: str, max_tokens: int) -> str:
        """Get overlap text from the end of current chunk"""
        words = text.split()
        if len(words) <= max_tokens:
            return text
        
        # Take last max_tokens words
        overlap_words = words[-max_tokens:]
        return " ".join(overlap_words)

    def _calculate_quality_scores(self, chunks: List[ContentChunk], domain: str):
        """Calculate quality and relevance scores for chunks"""
        for chunk in chunks:
            chunk.quality_score = self._calculate_quality_score(chunk, domain)
            chunk.relevance_score = self._calculate_relevance_score(chunk, domain)

    def _calculate_quality_score(self, chunk: ContentChunk, domain: str) -> float:
        """Calculate quality score based on content characteristics"""
        score = 80.0  # Base score
        text = chunk.chunk_text.lower()
        
        # Length appropriateness (30-1000 tokens ideal)
        if 30 <= chunk.token_count <= 1000:
            score += 10
        elif chunk.token_count < 30:
            score -= 20
        elif chunk.token_count > 1000:
            score -= 10
        
        # Content depth indicators
        if any(word in text for word in ['because', 'therefore', 'however', 'moreover', 'furthermore']):
            score += 5  # Logical reasoning
        
        if any(word in text for word in ['example', 'instance', 'such as', 'namely']):
            score += 3  # Examples provided
        
        # Domain-specific quality indicators
        if domain == "literary":
            if any(word in text for word in ['metaphor', 'imagery', 'beauty', 'love', 'heart']):
                score += 5
        elif domain == "philosophical":
            if any(word in text for word in ['truth', 'wisdom', 'virtue', 'justice', 'good', 'knowledge']):
                score += 5
        elif domain == "scientific":
            if any(word in text for word in ['experiment', 'observation', 'theory', 'principle', 'law']):
                score += 5
        elif domain == "historical":
            if any(word in text for word in ['nation', 'people', 'freedom', 'justice', 'leadership']):
                score += 5
        
        # Penalize very repetitive content
        words = text.split()
        if len(set(words)) < len(words) * 0.4:  # Less than 40% unique words
            score -= 15
        
        # Penalize fragmented content
        if text.count('.') < 2 and chunk.token_count > 100:
            score -= 10
        
        return max(0.0, min(100.0, score))

    def _calculate_relevance_score(self, chunk: ContentChunk, domain: str) -> float:
        """Calculate relevance score for personality responses"""
        score = 70.0  # Base score
        text = chunk.chunk_text.lower()
        
        # First-person indicators (autobiography/direct speech)
        if any(pronoun in text for pronoun in [' i ', ' my ', ' me ', ' myself ']):
            score += 15
        
        # Question-answer format (dialogues)
        if '?' in chunk.chunk_text and any(word in text for word in ['answer', 'reply', 'respond']):
            score += 10
        
        # Teaching/advice patterns
        if any(word in text for word in ['should', 'must', 'important', 'remember', 'understand']):
            score += 8
        
        # Quotable content
        if len(chunk.chunk_text.split('.')) >= 2 and chunk.token_count < 300:
            score += 5  # Good for quotes
        
        return max(0.0, min(100.0, score))

    def _save_chunks(self, chunks: List[ContentChunk], output_file: Path) -> bool:
        """Save chunks to JSONL file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for chunk in chunks:
                    json.dump(asdict(chunk), f, ensure_ascii=False)
                    f.write('\n')
            
            logger.info(f"✅ Saved {len(chunks)} chunks to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save chunks: {e}")
            return False

    async def process_all_personalities(self) -> Dict[str, Any]:
        """Process content for all 14 new personalities"""
        logger.info("🚀 Starting bulk content processing for all personalities")
        
        personalities = [
            "william_shakespeare", "rabindranath_tagore",
            "socrates", "plato", "aristotle", "sigmund_freud",
            "leonardo_da_vinci", "archimedes",
            "benjamin_franklin", "martin_luther_king", "nelson_mandela",
            "george_washington", "gandhi", "swami_vivekananda"
        ]
        
        results = {}
        overall_metrics = ProcessingMetrics()
        
        for personality_id in personalities:
            success, message, metrics = self.process_personality_content(personality_id)
            
            results[personality_id] = {
                "success": success,
                "message": message,
                "metrics": asdict(metrics)
            }
            
            # Aggregate metrics
            overall_metrics.source_files_processed += metrics.source_files_processed
            overall_metrics.total_chunks_created += metrics.total_chunks_created
            overall_metrics.total_tokens += metrics.total_tokens
            overall_metrics.total_characters += metrics.total_characters
            overall_metrics.processing_time_minutes += metrics.processing_time_minutes
            overall_metrics.error_count += metrics.error_count
        
        if overall_metrics.total_chunks_created > 0:
            overall_metrics.average_chunk_quality = sum(
                result["metrics"].get("average_chunk_quality", 0) 
                for result in results.values()
            ) / len(results)
        
        summary = {
            "overall_success": overall_metrics.error_count == 0,
            "personalities_processed": len(results),
            "overall_metrics": asdict(overall_metrics),
            "individual_results": results,
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Bulk processing complete: {overall_metrics.total_chunks_created} chunks created")
        return summary

    def get_processing_status(self) -> Dict[str, Any]:
        """Get current status of content processing"""
        processed_personalities = []
        
        for personality_dir in self.processed_dir.glob("*"):
            if personality_dir.is_dir():
                summary_file = personality_dir / f"{personality_dir.name}_processing_summary.json"
                chunks_file = personality_dir / f"{personality_dir.name}_chunks.jsonl"
                
                if summary_file.exists():
                    try:
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            summary = json.load(f)
                        
                        chunks_count = 0
                        if chunks_file.exists():
                            with open(chunks_file, 'r', encoding='utf-8') as f:
                                chunks_count = sum(1 for _ in f)
                        
                        processed_personalities.append({
                            "personality_id": personality_dir.name,
                            "domain": summary.get("domain", "unknown"),
                            "chunks_count": chunks_count,
                            "metrics": summary.get("metrics", {}),
                            "processed_at": summary.get("processed_at", "unknown"),
                            "has_errors": len(summary.get("errors", [])) > 0
                        })
                        
                    except Exception as e:
                        logger.warning(f"Could not read summary for {personality_dir.name}: {e}")
        
        return {
            "total_personalities_processed": len(processed_personalities),
            "personalities": processed_personalities,
            "total_chunks": sum(p["chunks_count"] for p in processed_personalities),
            "processing_directory": str(self.processed_dir)
        }
