"""
Gemini API-based Embedding Service

Provides vector embeddings using Google Gemini API with gemini-embedding-001 model.
Supports Matryoshka Representation Learning (MRL) for flexible dimensionality.

Migration Note (December 2025):
- Migrated from deprecated text-embedding-004 to gemini-embedding-001
- Added MRL support with output_dimensionality parameter
- Added L2 normalization for dimensions < 3072
"""

import os
import logging
import math
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
    normalized: bool = False

class GeminiEmbeddingService:
    """
    Gemini API-based embedding service using gemini-embedding-001
    
    Features:
    - Matryoshka Representation Learning (MRL) for flexible dimensions
    - L2 normalization for optimal cosine similarity
    - Task-type optimization (RETRIEVAL_QUERY, RETRIEVAL_DOCUMENT, SEMANTIC_SIMILARITY)
    - Higher rate limits and improved quality over text-embedding-004
    """
    
    def __init__(
        self, 
        model_name: str = "models/gemini-embedding-001",
        output_dimensionality: int = 768,
        api_key: Optional[str] = None, 
        test_mode: bool = False
    ):
        """
        Initialize Gemini Embedding Service
        
        Args:
            model_name: Gemini embedding model (default: gemini-embedding-001)
            output_dimensionality: MRL dimension (128-3072, default: 768 for Cosmos DB compatibility)
            api_key: API key for Gemini (optional, will try to get from environment)
            test_mode: If True, allows initialization without API key for testing
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.test_mode = test_mode
        self.output_dimensionality = output_dimensionality
        
        # Try to get API key from various sources if not provided
        if not self.api_key:
            # Check environment variable
            self.api_key = os.getenv('GEMINI_API_KEY')
            
            # Try to get from config if available
            try:
                from core.config import config
                if hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY:
                    self.api_key = config.GEMINI_API_KEY
                    
                # Also check unified config
                try:
                    from config.unified_config import UnifiedConfig
                    unified_config = UnifiedConfig()
                    if hasattr(unified_config, 'llm') and hasattr(unified_config.llm, 'api_key'):
                        if unified_config.llm.api_key:
                            self.api_key = unified_config.llm.api_key
                except Exception:
                    pass
                        
            except Exception:
                pass
        
        # Try to get output dimensionality from environment
        env_dimensionality = os.getenv('EMBEDDING_OUTPUT_DIMENSIONALITY')
        if env_dimensionality:
            try:
                self.output_dimensionality = int(env_dimensionality)
            except ValueError:
                pass
        
        if not self.api_key and not self.test_mode:
            logger.error("❌ GEMINI_API_KEY not found - embedding service will not work")
            logger.info("💡 Set GEMINI_API_KEY environment variable or provide api_key parameter")
            raise ValueError("GEMINI_API_KEY is required for embedding service")
        
        self.model_name = model_name
        self.client = None
        self.dimension = self.output_dimensionality  # MRL allows flexible dimensions
        
        # Validate dimensionality range for MRL
        if self.output_dimensionality < 128 or self.output_dimensionality > 3072:
            logger.warning(f"⚠️ output_dimensionality {self.output_dimensionality} outside recommended range (128-3072)")
        
        if not GEMINI_AVAILABLE and not self.test_mode:
            logger.error("❌ google-generativeai package not available")
            raise ImportError("google-generativeai package is required")
        
        if not self.test_mode:
            self._initialize_client()
        else:
            logger.info("✅ Gemini embedding service initialized in test mode")
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai
            logger.info(f"✅ Gemini embedding service initialized with {self.model_name} (dim={self.output_dimensionality})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            raise
    
    def _normalize_embedding(self, embedding: List[float]) -> List[float]:
        """
        L2-normalize embedding vector for accurate cosine similarity.
        Required when using MRL with dimensions < 3072.
        
        Args:
            embedding: Raw embedding vector
            
        Returns:
            L2-normalized embedding vector
        """
        if not embedding:
            return embedding
        
        # Calculate L2 norm
        norm = math.sqrt(sum(x * x for x in embedding))
        
        if norm == 0:
            return embedding
        
        # Normalize
        return [x / norm for x in embedding]
    
    def generate_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> EmbeddingResult:
        """
        Generate embedding for a single text using gemini-embedding-001
        
        Args:
            text: Text to embed
            task_type: Gemini task type (RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, SEMANTIC_SIMILARITY)
            
        Returns:
            EmbeddingResult with normalized embedding vector and metadata
        """
        if self.test_mode:
            # Return mock embedding for test mode
            logger.info("🧪 Generating mock embedding in test mode")
            mock_embedding = [0.1] * self.dimension
            return EmbeddingResult(
                embedding=self._normalize_embedding(mock_embedding),
                model=self.model_name,
                dimension=self.dimension,
                text_length=len(text),
                normalized=True
            )
            
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Build embed_content parameters
            embed_params = {
                "model": self.model_name,
                "content": cleaned_text,
                "task_type": task_type
            }
            
            # Add output_dimensionality for MRL if not using native 3072
            if self.output_dimensionality != 3072:
                embed_params["output_dimensionality"] = self.output_dimensionality
            
            # Generate embedding using Gemini API
            result = self.client.embed_content(**embed_params)
            
            embedding = result['embedding']
            
            # L2-normalize for dimensions < 3072 (required for MRL)
            needs_normalization = self.output_dimensionality < 3072
            if needs_normalization:
                embedding = self._normalize_embedding(embedding)
            
            return EmbeddingResult(
                embedding=embedding,
                model=self.model_name,
                dimension=len(embedding),
                text_length=len(cleaned_text),
                normalized=needs_normalization
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
        if not self.client and not self.test_mode:
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
                # Return zero vector as fallback (normalized)
                fallback_embedding = self._normalize_embedding([0.0] * self.dimension)
                fallback_result = EmbeddingResult(
                    embedding=fallback_embedding,
                    model=self.model_name,
                    dimension=self.dimension,
                    text_length=len(text),
                    normalized=True
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
    
    def generate_document_embedding(self, document: str) -> EmbeddingResult:
        """
        Generate embedding optimized for document indexing
        
        Args:
            document: Document text to embed
            
        Returns:
            EmbeddingResult optimized for document retrieval
        """
        return self.generate_embedding(document, task_type="RETRIEVAL_DOCUMENT")
    
    def generate_similarity_embedding(self, text: str) -> EmbeddingResult:
        """
        Generate embedding optimized for semantic similarity comparison
        
        Args:
            text: Text to embed for similarity comparison
            
        Returns:
            EmbeddingResult optimized for semantic similarity
        """
        return self.generate_embedding(text, task_type="SEMANTIC_SIMILARITY")
    
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
        
        # Truncate to Gemini's max length (2048 tokens ~ 8000 chars)
        max_length = 7000  # Conservative limit
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
            logger.warning(f"⚠️ Text truncated from {len(text)} to {len(cleaned)} characters")
        
        return cleaned
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        Optimized for pre-normalized embeddings (dot product = cosine similarity).
        
        Args:
            embedding1: First embedding vector (should be normalized)
            embedding2: Second embedding vector (should be normalized)
            
        Returns:
            Cosine similarity score (-1 to 1, typically 0 to 1 for text)
        """
        try:
            if not embedding1 or not embedding2:
                return 0.0
            
            if len(embedding1) != len(embedding2):
                logger.warning(f"⚠️ Embedding dimension mismatch: {len(embedding1)} vs {len(embedding2)}")
                return 0.0
            
            # For normalized vectors, dot product = cosine similarity
            similarity = sum(a * b for a, b in zip(embedding1, embedding2))
            return max(-1.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate similarity: {e}")
            return 0.0
    
    def get_model_info(self) -> dict:
        """Get information about the current embedding model"""
        return {
            "model_name": self.model_name,
            "native_dimension": 3072,
            "output_dimension": self.output_dimensionality,
            "mrl_enabled": self.output_dimensionality != 3072,
            "normalized": self.output_dimensionality < 3072,
            "provider": "Google Gemini",
            "api_based": True,
            "mteb_score": 68.17,
            "supported_task_types": ["RETRIEVAL_QUERY", "RETRIEVAL_DOCUMENT", "SEMANTIC_SIMILARITY"],
            "advantages": [
                "Matryoshka Representation Learning (MRL)",
                "Higher MTEB score (68.17)",
                "Higher rate limits",
                "Flexible dimensionality",
                "Consistent with Gemini LLM"
            ]
        }

# Singleton instance
_gemini_embedding_service = None

def get_gemini_embedding_service(
    model_name: str = "models/gemini-embedding-001",
    output_dimensionality: int = 768
) -> GeminiEmbeddingService:
    """Get singleton instance of Gemini embedding service"""
    global _gemini_embedding_service
    
    if _gemini_embedding_service is None:
        try:
            _gemini_embedding_service = GeminiEmbeddingService(
                model_name=model_name,
                output_dimensionality=output_dimensionality
            )
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
        Single embedding or list of embeddings (normalized)
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
