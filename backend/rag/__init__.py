"""
RAG (Retrieval-Augmented Generation) Module

Enhanced text processing and vector search capabilities for spiritual texts
with advanced chunking strategies and verse boundary preservation.
Supports both local Faiss storage (development) and Cosmos DB vector search (production).
"""

from .text_processor import (
    AdvancedSpiritualTextProcessor,
    EnhancedTextChunk,
    VerseReference,
    TextType
)

from .storage_factory import (
    VectorStorageFactory,
    VectorStorageInterface,
    LocalStorageAdapter,
    CosmosStorageAdapter,
    get_vector_storage
)

from .vector_storage import LocalVectorStorage, TextChunk
from .cosmos_vector_search import CosmosVectorSearch, SpiritualTextChunk
from .migration_utils import VectorStorageMigration

__all__ = [
    'AdvancedSpiritualTextProcessor',
    'EnhancedTextChunk', 
    'VerseReference',
    'TextType',
    'VectorStorageFactory',
    'VectorStorageInterface',
    'LocalStorageAdapter',
    'CosmosStorageAdapter',
    'get_vector_storage',
    'LocalVectorStorage',
    'TextChunk',
    'CosmosVectorSearch',
    'SpiritualTextChunk',
    'VectorStorageMigration'
]
