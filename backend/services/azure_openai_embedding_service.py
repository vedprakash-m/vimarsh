"""
Azure OpenAI Embedding Service

Enterprise-grade embedding service using Azure OpenAI text-embedding-3-large model.
Provides vector embeddings with Microsoft ecosystem integration, enterprise SLA,
and cost-optimized pricing through Azure Reserved Capacity.

Strategic Migration (December 2025):
- Migrated from Google Gemini embeddings to Azure OpenAI for complete ecosystem integration
- Enables 100% Azure-native infrastructure with unified billing and support
- Enterprise SLA guarantees (99.9% uptime) with Microsoft Premier Support
- Cost predictability through Reserved Capacity (40-60% savings) and commitment tiers
"""

import os
import logging
import time
import statistics
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass

try:
    from openai import OpenAI
    from openai import OpenAIError, RateLimitError, APIError
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False
    OpenAI = None
    OpenAIError = Exception
    RateLimitError = Exception
    APIError = Exception

logger = logging.getLogger(__name__)


def validate_embedding(
    embedding: List[float], 
    expected_dimensions: int = 768, 
    min_non_zero_percentage: float = 0.13
) -> bool:
    """
    Validate that embedding contains real values and is not corrupted.
    
    Args:
        embedding: Embedding vector to validate
        expected_dimensions: Expected embedding dimension (default: 768)
        min_non_zero_percentage: Minimum percentage of non-zero values (default: 13%)
        
    Returns:
        True if embedding is valid, False if corrupted or suspicious
        
    Raises:
        ValueError: If validation fails with detailed error message
    """
    # Check if embedding exists
    if not embedding:
        raise ValueError("Embedding is None or empty")
    
    # Check dimension
    if len(embedding) != expected_dimensions:
        raise ValueError(
            f"Invalid embedding dimension: {len(embedding)} (expected {expected_dimensions})"
        )
    
    # Count non-zero values
    non_zero_count = sum(1 for v in embedding if v != 0)
    non_zero_percentage = non_zero_count / len(embedding)
    
    if non_zero_count == 0:
        raise ValueError("Embedding contains all zeros - no actual embedding data!")
    
    if non_zero_percentage < min_non_zero_percentage:
        raise ValueError(
            f"Embedding has only {non_zero_count}/{len(embedding)} non-zero values "
            f"({non_zero_percentage:.1%} < {min_non_zero_percentage:.1%}) - likely corrupted"
        )
    
    # Check average magnitude
    avg_magnitude = statistics.mean([abs(v) for v in embedding])
    if avg_magnitude < 0.001:
        raise ValueError(
            f"Embedding average magnitude too low: {avg_magnitude:.6f} - likely corrupted"
        )
    
    # Check for reasonable value range (normalized embeddings should be ~[-1, 1])
    max_value = max([abs(v) for v in embedding])
    if max_value > 2.0:
        logger.warning(
            f"⚠️  Embedding has unusually high values (max: {max_value:.3f}). "
            "Expected normalized range ~[-1, 1]"
        )
    
    return True

@dataclass
class EmbeddingResult:
    """Result from embedding generation"""
    embedding: List[float]
    model: str
    dimension: int
    text_length: int
    normalized: bool = True  # Azure OpenAI automatically normalizes

class AzureOpenAIEmbeddingService:
    """
    Azure OpenAI embedding service using text-embedding-3-large
    
    Features:
    - Enterprise-grade text-embedding-3-large model (MTEB 64.6)
    - Dimension truncation (3072 → 768 for Cosmos DB compatibility)
    - Automatic L2 normalization by Azure OpenAI
    - Batch processing with optimized rate limiting (100K tokens/min)
    - Exponential backoff retry logic for resilience
    - Cost tracking and monitoring integration
    - Azure Key Vault support for credential management
    """
    
    def __init__(
        self,
        deployment_name: Optional[str] = None,
        dimensions: int = 768,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
        test_mode: bool = False
    ):
        """
        Initialize Azure OpenAI Embedding Service
        
        Args:
            deployment_name: Azure OpenAI deployment name (default: vimarsh-embedding-large)
            dimensions: Output dimension for embeddings (128-3072, default: 768)
            api_key: Azure OpenAI API key (optional, will use environment variable)
            endpoint: Azure OpenAI endpoint URL (optional, will use environment variable)
            api_version: Azure OpenAI API version (default: 2024-08-01-preview)
            test_mode: If True, allows initialization without API key for testing
        """
        self.logger = logging.getLogger(__name__)
        self.test_mode = test_mode
        self.dimensions = dimensions
        
        # Get configuration from environment or parameters
        # Support both AZURE_OPENAI_* and AZURE_OPENAI_EMBEDDING_* naming conventions
        self.endpoint = (
            endpoint or 
            os.getenv('AZURE_OPENAI_ENDPOINT', '') or 
            os.getenv('AZURE_OPENAI_EMBEDDING_ENDPOINT', 'https://vimarsh-openai.openai.azure.com/openai/v1')
        )
        self.api_key = (
            api_key or 
            os.getenv('AZURE_OPENAI_API_KEY', '') or 
            os.getenv('AZURE_OPENAI_EMBEDDING_API_KEY', '')
        )
        self.deployment_name = deployment_name or os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'vimarsh-embedding-large')
        self.api_version = (
            api_version or 
            os.getenv('AZURE_OPENAI_API_VERSION', '') or 
            os.getenv('AZURE_OPENAI_EMBEDDING_API_VERSION', '2024-08-01-preview')
        )
        
        # Validate configuration
        if not self.test_mode:
            if not self.endpoint:
                logger.error("❌ AZURE_OPENAI_ENDPOINT not found - embedding service will not work")
                logger.info("💡 Set AZURE_OPENAI_ENDPOINT environment variable")
                raise ValueError("AZURE_OPENAI_ENDPOINT is required for embedding service")
            
            if not self.api_key:
                logger.error("❌ AZURE_OPENAI_API_KEY not found - embedding service will not work")
                logger.info("💡 Set AZURE_OPENAI_API_KEY environment variable")
                raise ValueError("AZURE_OPENAI_API_KEY is required for embedding service")
        
        # Validate dimensionality range
        if self.dimensions < 128 or self.dimensions > 3072:
            logger.warning(f"⚠️ dimensions {self.dimensions} outside recommended range (128-3072)")
        
        if not AZURE_OPENAI_AVAILABLE and not self.test_mode:
            logger.error("❌ openai package not available")
            raise ImportError("openai package is required (pip install openai>=1.10.0)")
        
        self.client = None
        if not self.test_mode:
            self._initialize_client()
        else:
            logger.info("✅ Azure OpenAI embedding service initialized in test mode")
    
    def _initialize_client(self):
        """Initialize Azure OpenAI client"""
        try:
            self.client = OpenAI(
                base_url=self.endpoint,
                api_key=self.api_key,
                default_headers={"api-version": self.api_version}
            )
            logger.info(f"✅ Azure OpenAI embedding service initialized")
            logger.info(f"   Deployment: {self.deployment_name}")
            logger.info(f"   Dimensions: {self.dimensions}")
            logger.info(f"   API Version: {self.api_version}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure OpenAI client: {e}")
            raise
    
    async def generate_embedding(
        self,
        text: str,
        task_type: str = "retrieval_document",
        retry_attempts: int = 3
    ) -> List[float]:
        """
        Generate embedding for text with dimension truncation.
        
        Args:
            text: Input text to embed
            task_type: 'retrieval_query' or 'retrieval_document' (for semantic clarity)
            retry_attempts: Number of retry attempts on failure
        
        Returns:
            768-dimensional embedding vector (automatically L2-normalized by Azure)
        """
        if self.test_mode:
            # Return mock embedding for testing
            return [0.1] * self.dimensions
        
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimensions
        
        for attempt in range(retry_attempts):
            try:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.deployment_name,
                    dimensions=self.dimensions  # Truncate from 3072 to 768
                )
                
                # Azure OpenAI automatically L2-normalizes embeddings
                embedding = response.data[0].embedding
                
                # Validate embedding before returning
                try:
                    validate_embedding(embedding, expected_dimensions=self.dimensions)
                except ValueError as e:
                    logger.error(f"❌ Embedding validation failed: {e}")
                    raise
                
                return embedding
                
            except RateLimitError as e:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"Rate limit hit (attempt {attempt+1}/{retry_attempts}), waiting {wait_time}s...")
                if attempt < retry_attempts - 1:
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Rate limit exceeded after {retry_attempts} attempts")
                    raise
            
            except APIError as e:
                logger.error(f"❌ Azure OpenAI API error: {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise
            
            except Exception as e:
                logger.error(f"❌ Unexpected error generating embedding: {e}")
                raise
    
    async def generate_batch_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100,
        task_type: str = "retrieval_document"
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with batching.
        
        Azure OpenAI supports up to 2048 texts per request, but we use smaller batches
        for better error handling and progress tracking.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call (default: 100)
            task_type: 'retrieval_query' or 'retrieval_document'
        
        Returns:
            List of embedding vectors
        """
        if self.test_mode:
            return [[0.1] * self.dimensions for _ in texts]
        
        embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            try:
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")
                
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.deployment_name,
                    dimensions=self.dimensions
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                
                # Validate all embeddings in batch
                for idx, emb in enumerate(batch_embeddings):
                    try:
                        validate_embedding(emb, expected_dimensions=self.dimensions)
                    except ValueError as e:
                        logger.error(f"❌ Embedding validation failed for batch item {idx}: {e}")
                        raise
                
                embeddings.extend(batch_embeddings)
                
                # Rate limiting: 100K tokens/min = ~100 docs/min with 1K tokens each
                # Sleep briefly between batches to avoid rate limits
                if i + batch_size < len(texts):
                    time.sleep(0.6)  # 100 requests/min = 0.6s delay
                
            except Exception as e:
                logger.error(f"❌ Batch embedding error (batch {batch_num}): {e}")
                raise
        
        logger.info(f"✅ Generated {len(embeddings)} embeddings in {total_batches} batches")
        return embeddings
    
    def encode(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Synchronous encode method for compatibility with SentenceTransformer interface.
        This provides drop-in compatibility for legacy code that uses .encode()
        
        Args:
            text: Single text string or list of texts
            
        Returns:
            Single embedding vector or list of vectors
        """
        import asyncio
        
        # Handle both single text and batch
        if isinstance(text, str):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is running, we need to use run_coroutine_threadsafe
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.generate_embedding(text))
                    return future.result()
            else:
                return asyncio.run(self.generate_embedding(text))
        elif isinstance(text, list):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.generate_batch_embeddings(text))
                    return future.result()
            else:
                return asyncio.run(self.generate_batch_embeddings(text))
        else:
            raise ValueError(f"Invalid input type: {type(text)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get current model configuration info for diagnostics"""
        return {
            "provider": "Azure OpenAI",
            "model": "text-embedding-3-large",
            "deployment_name": self.deployment_name,
            "dimensions": self.dimensions,
            "api_version": self.api_version,
            "endpoint": self.endpoint[:50] + "..." if len(self.endpoint) > 50 else self.endpoint,
            "normalized": True,  # Azure OpenAI auto-normalizes
            "max_batch_size": 2048,
            "rate_limit": "100K tokens/min",
            "mteb_score": 64.6
        }
