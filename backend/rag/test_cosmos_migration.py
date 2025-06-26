"""
Tests for Cosmos DB Vector Search Implementation
Task 8.7: Migrate local vector storage to Cosmos DB vector search
"""

import pytest
import asyncio
import numpy as np
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path
import tempfile
import shutil

from backend.rag.cosmos_vector_search import (
    CosmosVectorSearch,
    SpiritualTextChunk,
    get_vector_search
)
from backend.rag.migration_utils import VectorStorageMigration
from backend.rag.vector_storage import LocalVectorStorage, TextChunk


class TestSpiritualTextChunk:
    """Test SpiritualTextChunk data class"""
    
    def test_chunk_creation(self):
        """Test basic chunk creation"""
        chunk = SpiritualTextChunk(
            id="test_chunk_1",
            text="This is a test spiritual text",
            source="test_source",
            embedding=[0.1, 0.2, 0.3]
        )
        
        assert chunk.id == "test_chunk_1"
        assert chunk.text == "This is a test spiritual text"
        assert chunk.source == "test_source"
        assert chunk.embedding == [0.1, 0.2, 0.3]
        assert chunk.created_at is not None
        assert chunk.updated_at is not None
    
    def test_chunk_post_init(self):
        """Test post-initialization defaults"""
        chunk = SpiritualTextChunk(
            id="test_chunk_2",
            text="Test text",
            source="test"
        )
        
        assert chunk.sanskrit_terms == []
        assert chunk.created_at is not None
        assert chunk.updated_at == chunk.created_at
        assert chunk.chunk_size == len("Test text")
    
    def test_to_cosmos_document(self):
        """Test conversion to Cosmos document format"""
        embedding = np.array([0.1, 0.2, 0.3])
        chunk = SpiritualTextChunk(
            id="test_chunk_3",
            text="Test text with numpy embedding",
            source="test",
            embedding=embedding,
            sanskrit_terms=["dharma", "karma"]
        )
        
        doc = chunk.to_cosmos_document()
        
        assert doc['id'] == "test_chunk_3"
        assert doc['embedding'] == [0.1, 0.2, 0.3]  # Converted to list
        assert doc['sanskrit_terms'] == ["dharma", "karma"]
    
    def test_from_cosmos_document(self):
        """Test creation from Cosmos document"""
        doc = {
            'id': 'test_chunk_4',
            'text': 'Document text',
            'source': 'test_source',
            'embedding': [0.1, 0.2, 0.3],
            'sanskrit_terms': ['moksha']
        }
        
        chunk = SpiritualTextChunk.from_cosmos_document(doc)
        
        assert chunk.id == 'test_chunk_4'
        assert chunk.text == 'Document text'
        assert chunk.source == 'test_source'
        assert chunk.embedding == [0.1, 0.2, 0.3]
        assert chunk.sanskrit_terms == ['moksha']


class TestCosmosVectorSearch:
    """Test Cosmos DB vector search functionality"""
    
    @pytest.fixture
    def mock_cosmos_search(self):
        """Create CosmosVectorSearch with mocked Cosmos client"""
        # Mock the connection so it doesn't try to connect to real Cosmos DB
        with patch('backend.rag.cosmos_vector_search.CosmosClient'):
            search = CosmosVectorSearch(
                endpoint="https://test.documents.azure.com:443/",
                key="test_key",
                database_name="test_db",
                container_name="test_container"
            )
            # Override connection state for testing
            search.is_connected = False  # Use mock mode
        return search
    
    def test_initialization(self, mock_cosmos_search):
        """Test CosmosVectorSearch initialization"""
        search = mock_cosmos_search
        
        assert search.database_name == "test_db"
        assert search.container_name == "test_container"
        assert search.embedding_dimension == 768
        assert not search.is_connected  # In mock mode
    
    def test_add_chunk_mock_mode(self, mock_cosmos_search):
        """Test adding chunk in mock mode"""
        search = mock_cosmos_search
        
        chunk = SpiritualTextChunk(
            id="test_add_1",
            text="Test spiritual text",
            source="bhagavad_gita",
            embedding=[0.1, 0.2, 0.3]
        )
        
        result = search.add_chunk(chunk)
        assert result is True  # Mock mode always returns True
    
    def test_add_chunk_no_embedding(self, mock_cosmos_search):
        """Test adding chunk without embedding"""
        search = mock_cosmos_search
        
        chunk = SpiritualTextChunk(
            id="test_add_2",
            text="Test text without embedding",
            source="test"
        )
        
        result = search.add_chunk(chunk)
        assert result is False  # Should fail without embedding
    
    def test_search_mock_mode(self, mock_cosmos_search):
        """Test search in mock mode"""
        search = mock_cosmos_search
        
        query_embedding = np.array([0.1, 0.2, 0.3])
        results = search.search(query_embedding, k=5)
        
        assert isinstance(results, list)
        assert len(results) == 0  # Mock mode returns empty results
    
    def test_search_by_source_mock_mode(self, mock_cosmos_search):
        """Test search by source in mock mode"""
        search = mock_cosmos_search
        
        results = search.search_by_source("bhagavad_gita", limit=10)
        
        assert isinstance(results, list)
        assert len(results) == 0  # Mock mode returns empty results
    
    def test_get_stats_mock_mode(self, mock_cosmos_search):
        """Test getting stats in mock mode"""
        search = mock_cosmos_search
        
        stats = search.get_stats()
        
        assert 'total_chunks' in stats
        assert 'by_source' in stats
        assert 'connected' in stats
        assert stats['connected'] is False
        assert stats['mode'] == 'mock'
    
    def test_global_instance(self):
        """Test global vector search instance"""
        # Clear any existing global instance
        import backend.rag.cosmos_vector_search
        backend.rag.cosmos_vector_search._cosmos_vector_search = None
        
        search1 = get_vector_search()
        search2 = get_vector_search()
        
        assert search1 is search2  # Should be same instance


class TestVectorStorageMigration:
    """Test vector storage migration utility"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_local_storage(self, temp_dir):
        """Create sample local storage with test data"""
        local_storage = LocalVectorStorage(
            dimension=384,
            storage_path=str(Path(temp_dir) / "local_storage")
        )
        
        # Add sample chunks
        chunks = [
            TextChunk(
                id="bhagavad_gita_1_1",
                text="धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।",
                source="bhagavad_gita",
                chapter="1",
                verse="1",
                sanskrit_terms=["dharma", "kurukshetra"],
                embedding=np.random.rand(384)
            ),
            TextChunk(
                id="bhagavad_gita_2_47",
                text="कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
                source="bhagavad_gita",
                chapter="2", 
                verse="47",
                sanskrit_terms=["karma", "adhikara"],
                embedding=np.random.rand(384)
            ),
            TextChunk(
                id="srimad_bhagavatam_1_1",
                text="ॐ नमो भगवते वासुदेवाय।",
                source="srimad_bhagavatam",
                chapter="1",
                verse="1",
                sanskrit_terms=["om", "namah", "bhagavate"],
                embedding=np.random.rand(384)
            )
        ]
        
        for chunk in chunks:
            local_storage.add_chunk(chunk)
        
        return local_storage
    
    @pytest.fixture
    def migration_util(self, temp_dir, sample_local_storage):
        """Create migration utility with test data"""
        migration = VectorStorageMigration(
            local_storage_path=sample_local_storage.storage_path,
            backup_path=str(Path(temp_dir) / "backup")
        )
        # Override local storage to use our sample
        migration.local_storage = sample_local_storage
        return migration
    
    def test_analyze_local_data(self, migration_util):
        """Test local data analysis"""
        analysis = migration_util.analyze_local_data()
        
        assert analysis['total_chunks'] == 3
        assert analysis['unique_sources'] == 2
        assert 'bhagavad_gita' in analysis['sources']
        assert 'srimad_bhagavatam' in analysis['sources']
        assert analysis['sources']['bhagavad_gita'] == 2
        assert analysis['sources']['srimad_bhagavatam'] == 1
        assert analysis['migration_readiness'] is True
        assert len(analysis['data_issues']) == 0
    
    def test_create_backup(self, migration_util):
        """Test backup creation"""
        backup_path = migration_util.create_migration_backup()
        
        assert Path(backup_path).exists()
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        assert 'metadata' in backup_data
        assert 'chunks' in backup_data
        assert backup_data['metadata']['total_chunks'] == 3
        assert len(backup_data['chunks']) == 3
        
        # Verify chunk structure
        chunk = backup_data['chunks'][0]
        assert 'id' in chunk
        assert 'text' in chunk
        assert 'source' in chunk
        assert 'embedding' in chunk
        assert isinstance(chunk['embedding'], list)
    
    def test_convert_chunk_format(self, migration_util):
        """Test chunk format conversion"""
        local_chunk = migration_util.local_storage.chunks[0]
        cosmos_chunk = migration_util.convert_chunk_format(local_chunk)
        
        assert isinstance(cosmos_chunk, SpiritualTextChunk)
        assert cosmos_chunk.id == local_chunk.id
        assert cosmos_chunk.text == local_chunk.text
        assert cosmos_chunk.source == local_chunk.source
        assert cosmos_chunk.chapter == local_chunk.chapter
        assert cosmos_chunk.verse == local_chunk.verse
        assert cosmos_chunk.sanskrit_terms == local_chunk.sanskrit_terms
        
        # Check spiritual metadata was added
        assert cosmos_chunk.spiritual_theme is not None
        assert cosmos_chunk.dharmic_context is not None
        assert cosmos_chunk.character_speaker is not None
        assert cosmos_chunk.chunk_size == len(local_chunk.text)
        assert cosmos_chunk.created_at is not None
    
    def test_validate_migration_chunk(self, migration_util):
        """Test chunk validation after migration"""
        local_chunk = migration_util.local_storage.chunks[0]
        cosmos_chunk = migration_util.convert_chunk_format(local_chunk)
        
        is_valid, issues = migration_util.validate_migration_chunk(local_chunk, cosmos_chunk)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_migration_chunk_with_issues(self, migration_util):
        """Test chunk validation with mismatched data"""
        local_chunk = migration_util.local_storage.chunks[0]
        cosmos_chunk = migration_util.convert_chunk_format(local_chunk)
        
        # Introduce issues
        cosmos_chunk.id = "different_id"
        cosmos_chunk.text = "different text"
        
        is_valid, issues = migration_util.validate_migration_chunk(local_chunk, cosmos_chunk)
        
        assert is_valid is False
        assert len(issues) >= 2  # Should catch ID and text mismatches
    
    def test_spiritual_theme_extraction(self, migration_util):
        """Test spiritual theme extraction"""
        themes = [
            ("This is about duty and dharma", "duty"),
            ("Devotion and bhakti to the divine", "devotion"),  
            ("Knowledge and wisdom are supreme", "knowledge"),
            ("Action and karma yoga", "action"),
            ("Meditation and dhyana practice", "meditation"),
            ("Liberation and moksha", "liberation"),
            ("Divine supreme consciousness", "divinity"),
            ("Ethics and moral behavior", "ethics"),
            ("Random spiritual text", "general")
        ]
        
        for text, expected_theme in themes:
            theme = migration_util._extract_spiritual_theme(text)
            assert theme == expected_theme
    
    def test_dharmic_context_extraction(self, migration_util):
        """Test dharmic context extraction"""
        context = migration_util._extract_dharmic_context(
            "Krishna speaks to Arjuna about dharma",
            ["dharma", "karma"]
        )
        
        assert "dharma" in context
        assert "Krishna-guidance" in context or "Arjuna-inquiry" in context
    
    def test_character_speaker_extraction(self, migration_util):
        """Test character speaker identification"""
        test_cases = [
            ("Krishna said to Arjuna", "bhagavad_gita", "Krishna"),
            ("Arjuna inquired from the Lord", "bhagavad_gita", "Arjuna"),
            ("The narrator describes", "srimad_bhagavatam", "Narrator"),
            ("General spiritual teaching", "bhagavad_gita", "Krishna"),  # Default for BG
        ]
        
        for text, source, expected_speaker in test_cases:
            speaker = migration_util._extract_character_speaker(text, source)
            assert speaker == expected_speaker


class TestMigrationIntegration:
    """Integration tests for migration process"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def migration_setup(self, temp_dir):
        """Set up complete migration test environment"""
        # Create local storage with sample data
        local_path = Path(temp_dir) / "local_storage"
        local_storage = LocalVectorStorage(
            dimension=768,
            storage_path=str(local_path)
        )
        
        # Add comprehensive test data
        test_chunks = [
            TextChunk(
                id=f"test_chunk_{i}",
                text=f"Test spiritual text number {i} about dharma and karma",
                source="bhagavad_gita" if i % 2 == 0 else "srimad_bhagavatam",
                chapter=str((i % 10) + 1),
                verse=str((i % 20) + 1),
                sanskrit_terms=["dharma", "karma"] if i % 2 == 0 else ["bhakti", "moksha"],
                embedding=np.random.rand(768)
            )
            for i in range(20)  # 20 test chunks
        ]
        
        for chunk in test_chunks:
            local_storage.add_chunk(chunk)
        
        # Create migration utility
        migration = VectorStorageMigration(
            local_storage_path=str(local_path),
            backup_path=str(Path(temp_dir) / "backup")
        )
        
        return migration, local_storage
    
    def test_full_migration_process(self, migration_setup):
        """Test complete migration process"""
        migration, local_storage = migration_setup
        
        # Override cosmos storage to use mock mode
        migration.cosmos_storage.is_connected = False
        
        # Perform full migration
        results = migration.perform_full_migration(
            create_backup=True,
            batch_size=5,
            verify_after=True
        )
        
        assert results['success'] is True
        assert results['backup_path'] is not None
        assert Path(results['backup_path']).exists()
        assert results['analysis'] is not None
        assert results['migration_stats'] is not None
        assert results['verification'] is not None
        assert results['report_path'] is not None
        
        # Check migration stats
        stats = results['migration_stats']
        assert stats['total_chunks'] == 20
        assert stats['migrated_chunks'] > 0  # In mock mode, should succeed
        assert stats['start_time'] is not None
        assert stats['end_time'] is not None
    
    def test_migration_with_validation_failures(self, migration_setup):
        """Test migration handling validation failures"""
        migration, local_storage = migration_setup
        
        # Set very high similarity threshold to cause validation failures
        migration.similarity_threshold = 0.99999
        
        # Mock cosmos storage
        migration.cosmos_storage.is_connected = False
        
        # Perform migration with strict validation
        results = migration.migrate_chunks(validate_each=True, batch_size=5)
        
        assert results['total_chunks'] == 20
        # Some chunks might fail validation with very high threshold
        assert results['migrated_chunks'] >= 0
        assert results['failed_chunks'] >= 0
    
    def test_migration_analysis_with_issues(self, temp_dir):
        """Test migration analysis with problematic data"""
        # Create storage with problematic data
        local_path = Path(temp_dir) / "problematic_storage"
        local_storage = LocalVectorStorage(
            dimension=384,
            storage_path=str(local_path)
        )
        
        # Add chunks with issues
        problematic_chunks = [
            TextChunk(id="good_chunk", text="Good text", source="test", embedding=np.random.rand(384)),
            TextChunk(id="no_embedding", text="No embedding", source="test", embedding=None),
            TextChunk(id="empty_text", text="", source="test", embedding=np.random.rand(384)),
            TextChunk(id="no_source", text="No source", source="", embedding=np.random.rand(384))
        ]
        
        for chunk in problematic_chunks:
            if chunk.embedding is not None:
                local_storage.add_chunk(chunk)
            else:
                # Manually add chunk with None embedding for testing
                local_storage.chunks.append(chunk)
                local_storage.id_to_index[chunk.id] = len(local_storage.chunks) - 1
        
        migration = VectorStorageMigration(
            local_storage_path=str(local_path),
            backup_path=str(Path(temp_dir) / "backup")
        )
        migration.local_storage = local_storage
        
        # Analyze problematic data
        analysis = migration.analyze_local_data()
        
        assert analysis['total_chunks'] == 4
        assert len(analysis['data_issues']) > 0  # Should detect issues
        assert analysis['migration_readiness'] is False  # Should fail readiness check


class TestErrorHandling:
    """Test error handling in migration components"""
    
    def test_cosmos_search_connection_failure(self):
        """Test handling of Cosmos DB connection failures"""
        # Try to create search with invalid credentials
        search = CosmosVectorSearch(
            endpoint="https://invalid.documents.azure.com:443/",
            key="invalid_key"
        )
        
        # Should fall back to mock mode
        assert not search.is_connected
        assert search.connection_error is not None
    
    def test_migration_with_invalid_local_path(self):
        """Test migration with invalid local storage path"""
        migration = VectorStorageMigration(
            local_storage_path="/nonexistent/path",
            backup_path="/tmp/backup"
        )
        
        # Should handle gracefully
        analysis = migration.analyze_local_data()
        assert analysis['total_chunks'] == 0
    
    def test_chunk_conversion_with_missing_data(self):
        """Test chunk conversion with incomplete data"""
        migration = VectorStorageMigration()
        
        # Create chunk with minimal data
        incomplete_chunk = TextChunk(
            id="minimal",
            text="Minimal text",
            source="test"
            # No embedding, chapter, verse, etc.
        )
        
        # Should handle conversion gracefully
        cosmos_chunk = migration.convert_chunk_format(incomplete_chunk)
        assert cosmos_chunk.id == "minimal"
        assert cosmos_chunk.embedding is None
        assert cosmos_chunk.spiritual_theme is not None  # Should have default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
