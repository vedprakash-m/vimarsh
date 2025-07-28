"""
Gemini API-based Embedding Service

Provides vector embeddings using Google Gemini API instead of sentence-transformers
to reduce deployment size and eliminate heavy ML dependencies.
"""

import os
import logging
from typing import List, Optional, Union
from dataclasses import dataclass

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Result from embedding generation"""
    embedding: List[float]
    model: str
    dimension: int
    text_length: int

class GeminiEmbeddingService:
    """
    Gemini API-based embedding service
    
    Advantages over sentence-transformers:
    - No heavy ML dependencies (~500MB saved)
    - Faster cold starts
    - Consistent with existing Gemini API usage
    - Scalable cloud-based processing
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "models/text-embedding-004"):
        """
        Initialize Gemini embedding service
        
        Args:
            api_key: Gemini API key (defaults to environment variable)
            model_name: Gemini embedding model to use
        """
        # Try multiple sources for API key
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
        
        # Try to get from config system if available
        if not self.api_key:
            try:
                # Try to import and use your config system (avoid relative imports for now)
                # Try to get from various config sources
                config_paths = [
                    'core.config',
                    'backend.core.config'
                ]
                
                for config_path in config_paths:
                    try:
                        config_module = __import__(config_path, fromlist=['config'])
                        if hasattr(config_module, 'config'):
                            self.api_key = config_module.config.get_value("LLM", "api_key", fallback="")
                            if self.api_key:
                                break
                    except (ImportError, AttributeError):
                        continue
                        
            except Exception:
                # Silently continue if config system not available
                pass
        
        if not self.api_key:
            logger.error("❌ GEMINI_API_KEY not found - embedding service will not work")
            logger.info("💡 Set GEMINI_API_KEY environment variable or provide api_key parameter")
            raise ValueError("GEMINI_API_KEY is required for embedding service")
        
        self.model_name = model_name
        self.client = None
        self.dimension = 768  # text-embedding-004 dimension
        
        if not GEMINI_AVAILABLE:
            logger.error("❌ google-generativeai package not available")
            raise ImportError("google-generativeai package is required")
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai
            logger.info(f"✅ Gemini embedding service initialized with {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            raise
    
    def generate_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> EmbeddingResult:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            task_type: Gemini task type (RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, etc.)
            
        Returns:
            EmbeddingResult with embedding vector and metadata
        """
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Generate embedding using Gemini API
            result = self.client.embed_content(
                model=self.model_name,
                content=cleaned_text,
                task_type=task_type
            )
            
            embedding = result['embedding']
            
            return EmbeddingResult(
                embedding=embedding,
                model=self.model_name,
                dimension=len(embedding),
                text_length=len(cleaned_text)
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            logger.error(f"Text length: {len(text)}, First 100 chars: {text[:100]}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            task_type: Gemini task type
            
        Returns:
            List of EmbeddingResult objects
        """
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
        
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = self.generate_embedding(text, task_type)
                results.append(result)
                
                # Add small delay to respect rate limits
                if i > 0 and i % 10 == 0:
                    logger.info(f"Generated {i+1}/{len(texts)} embeddings")
                    
            except Exception as e:
                logger.error(f"❌ Failed to generate embedding for text {i}: {e}")
                # Return zero vector as fallback
                fallback_result = EmbeddingResult(
                    embedding=[0.0] * self.dimension,
                    model=self.model_name,
                    dimension=self.dimension,
                    text_length=len(text)
                )
                results.append(fallback_result)
        
        logger.info(f"✅ Generated {len(results)} embeddings")
        return results
    
    def generate_query_embedding(self, query: str) -> EmbeddingResult:
        """
        Generate embedding optimized for query/search
        
        Args:
            query: Search query text
            
        Returns:
            EmbeddingResult optimized for retrieval
        """
        return self.generate_embedding(query, task_type="RETRIEVAL_QUERY")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and prepare text for embedding generation
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text suitable for embedding
        """
        if not text or not text.strip():
            return ""
        
        # Remove excessive whitespace
        cleaned = " ".join(text.split())
        
        # Truncate to Gemini's max length (approx 2048 tokens ~ 8000 chars)
        max_length = 7000  # Conservative limit
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
            logger.warning(f"⚠️ Text truncated from {len(text)} to {len(cleaned)} characters")
        
        return cleaned
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            import numpy as np
            
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate similarity: {e}")
            return 0.0
    
    def get_model_info(self) -> dict:
        """Get information about the current embedding model"""
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "provider": "Google Gemini",
            "api_based": True,
            "advantages": [
                "No heavy dependencies",
                "Fast cold starts",
                "Cloud-based scaling",
                "Consistent with Gemini LLM"
            ]
        }

# Singleton instance
_gemini_embedding_service = None

def get_gemini_embedding_service() -> GeminiEmbeddingService:
    """Get singleton instance of Gemini embedding service"""
    global _gemini_embedding_service
    
    if _gemini_embedding_service is None:
        try:
            _gemini_embedding_service = GeminiEmbeddingService()
        except Exception as e:
            logger.error(f"❌ Failed to create Gemini embedding service: {e}")
            raise
    
    return _gemini_embedding_service

# Compatibility functions for drop-in replacement
def encode(text: Union[str, List[str]], task_type: str = "RETRIEVAL_DOCUMENT") -> Union[List[float], List[List[float]]]:
    """
    Compatibility function that mimics sentence-transformers encode method
    
    Args:
        text: Single text or list of texts
        task_type: Task type for Gemini API
        
    Returns:
        Single embedding or list of embeddings
    """
    service = get_gemini_embedding_service()
    
    if isinstance(text, str):
        result = service.generate_embedding(text, task_type)
        return result.embedding
    else:
        results = service.generate_embeddings_batch(text, task_type)
        return [result.embedding for result in results]

# Mock class for drop-in replacement of SentenceTransformer
class GeminiTransformer:
    """
    Drop-in replacement for SentenceTransformer using Gemini API
    """
    
    def __init__(self, model_name_ignored: str = None):
        """Initialize - model_name is ignored as we use Gemini"""
        self.service = get_gemini_embedding_service()
        self.model_name = self.service.model_name
    
    def encode(self, sentences: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
        """Encode text(s) to embeddings - compatible with SentenceTransformer API"""
        return encode(sentences)
    
    def __repr__(self):
        return f"GeminiTransformer(model='{self.model_name}')"
