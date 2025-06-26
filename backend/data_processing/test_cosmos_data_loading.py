"""
Comprehensive Tests for Cosmos DB Data Loading Pipeline
Task 8.8: Load and chunk source texts into production Cosmos DB

Tests all components of the data loading system including source management,
text processing, chunking, embedding generation, and Cosmos DB integration.
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Import components to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.data_processing.spiritual_text_manager import SpiritualTextDataManager, SpiritualTextSource
from backend.data_processing.cosmos_data_loader import CosmosDataLoader, LoadingProgress
from backend.data_processing.data_loading_monitor import DataLoadingMonitor, DataQualityReport
from backend.rag.text_processor import AdvancedSpiritualTextProcessor, TextType


class TestSpiritualTextDataManager:
    """Test suite for SpiritualTextDataManager."""
    
    @pytest.fixture
    def temp_sources_dir(self):
        """Create a temporary sources directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sources_dir = Path(temp_dir) / "sources"
            sources_dir.mkdir()
            
            # Create sample source file
            sample_file = sources_dir / "bhagavad_gita_sample.txt"
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write("""Chapter 2: The Yoga of Knowledge

2.47 You have a right to perform your prescribed duty, but do not claim entitlement to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.

2.48 Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure. Such equanimity is called yoga.

2.49 Far inferior indeed is mere action to the yoga of wisdom, O Arjuna. Seek refuge in wisdom. Pitiable are those who are motivated by the fruits of action.
""")
            
            yield sources_dir
    
    @pytest.fixture
    def data_manager(self, temp_sources_dir):
        """Create a SpiritualTextDataManager instance."""
        return SpiritualTextDataManager(str(temp_sources_dir))
    
    def test_initialization(self, data_manager):
        """Test data manager initialization."""
        assert data_manager.sources_directory.exists()
        assert isinstance(data_manager.sources, dict)
        assert len(data_manager.sources) == 0  # Initially empty
    
    def test_register_source(self, data_manager):
        """Test source registration."""
        source = SpiritualTextSource(
            source_id="test_source",
            title="Test Spiritual Text",
            author="Test Author",
            translator="Test Translator",
            source_type="bhagavad_gita",
            language="English",
            file_path="bhagavad_gita_sample.txt",
            copyright_status="public_domain"
        )
        
        success = data_manager.register_source(source)
        assert success
        assert "test_source" in data_manager.sources
        
        # Verify metadata was added
        registered_source = data_manager.sources["test_source"]
        assert registered_source.content_hash is not None
        assert registered_source.word_count > 0
        assert registered_source.character_count > 0
    
    def test_register_source_missing_file(self, data_manager):
        """Test source registration with missing file."""
        source = SpiritualTextSource(
            source_id="missing_source",
            title="Missing Text",
            author="Test Author",
            translator="Test Translator",
            source_type="bhagavad_gita",
            language="English",
            file_path="missing_file.txt",
            copyright_status="public_domain"
        )
        
        success = data_manager.register_source(source)
        assert not success
        assert "missing_source" not in data_manager.sources
    
    def test_validate_source(self, data_manager):
        """Test source validation."""
        # Register a valid source first
        source = SpiritualTextSource(
            source_id="validation_test",
            title="Validation Test",
            author="Test Author",
            translator="Test Translator",
            source_type="bhagavad_gita",
            language="English",
            file_path="bhagavad_gita_sample.txt",
            copyright_status="public_domain"
        )
        
        data_manager.register_source(source)
        
        # Validate the source
        result = data_manager.validate_source("validation_test")
        
        assert result["valid"]
        assert "checks" in result
        assert result["checks"]["file_accessible"]
        assert result["checks"]["copyright_clear"]
    
    def test_load_source_content(self, data_manager):
        """Test loading source content."""
        # Register a source first
        source = SpiritualTextSource(
            source_id="content_test",
            title="Content Test",
            author="Test Author",
            translator="Test Translator",
            source_type="bhagavad_gita",
            language="English",
            file_path="bhagavad_gita_sample.txt",
            copyright_status="public_domain"
        )
        
        data_manager.register_source(source)
        
        # Load content
        content = data_manager.load_source_content("content_test")
        
        assert content is not None
        assert "Chapter 2" in content
        assert "2.47" in content
        assert "dharma" in content.lower() or "duty" in content


class TestCosmosDataLoader:
    """Test suite for CosmosDataLoader."""
    
    @pytest.fixture
    def temp_directories(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sources_dir = temp_path / "sources"
            temp_processing = temp_path / "temp"
            
            sources_dir.mkdir()
            temp_processing.mkdir()
            
            # Create sample source file
            sample_file = sources_dir / "bhagavad_gita_sample.txt"
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write("""Chapter 2: The Yoga of Knowledge

2.47 You have a right to perform your prescribed duty, but do not claim entitlement to the fruits of action.

2.48 Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure.
""")
            
            yield str(sources_dir), str(temp_processing)
    
    @pytest.fixture
    def mock_embedding_model(self):
        """Create a mock embedding model."""
        mock_model = Mock()
        mock_model.encode.return_value = [0.1] * 384  # Mock 384-dim embedding
        return mock_model
    
    @pytest.fixture
    def data_loader(self, temp_directories, mock_embedding_model):
        """Create a CosmosDataLoader instance."""
        sources_dir, temp_dir = temp_directories
        
        with patch('backend.data_processing.cosmos_data_loader.SentenceTransformer') as mock_transformer:
            mock_transformer.return_value = mock_embedding_model
            loader = CosmosDataLoader(
                sources_directory=sources_dir,
                temp_directory=temp_dir,
                embedding_model_name="mock-model"
            )
            yield loader
    
    def test_initialization(self, data_loader):
        """Test data loader initialization."""
        assert data_loader.sources_directory.exists()
        assert data_loader.temp_directory.exists()
        assert data_loader.data_manager is not None
        assert data_loader.text_processor is not None
        assert data_loader.embedding_model is not None
    
    def test_register_sample_sources(self, data_loader):
        """Test sample source registration."""
        success = data_loader.register_sample_sources()
        assert success
        
        sources = data_loader.data_manager.list_sources()
        assert len(sources) >= 2  # At least Bhagavad Gita and Mahabharata samples
        
        source_ids = [source.source_id for source in sources]
        assert "bhagavad_gita_sample" in source_ids
        assert "mahabharata_sample" in source_ids
    
    def test_validate_sources(self, data_loader):
        """Test source validation."""
        # Register sources first
        data_loader.register_sample_sources()
        
        # Validate sources
        results = data_loader.validate_sources()
        
        assert "total_sources" in results
        assert "valid_sources" in results
        assert "source_details" in results
        assert results["total_sources"] > 0
    
    @pytest.mark.asyncio
    async def test_process_source_to_chunks(self, data_loader):
        """Test processing a source into chunks."""
        # Register sources first
        data_loader.register_sample_sources()
        
        # Process a source
        chunks = await data_loader.process_source_to_chunks("bhagavad_gita_sample")
        
        assert len(chunks) > 0
        
        # Verify chunk properties
        for chunk in chunks:
            assert chunk.id is not None
            assert chunk.content is not None
            assert len(chunk.content) > 0
            assert chunk.source_id == "bhagavad_gita_sample"
            assert chunk.vector is not None  # Should have embedding
            assert isinstance(chunk.vector, list)
    
    @pytest.mark.asyncio
    async def test_initialize_storage_mock(self, data_loader):
        """Test storage initialization with mocking."""
        # Mock the storage interface
        with patch('backend.data_processing.cosmos_data_loader.get_vector_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.test_connection.return_value = True
            mock_get_storage.return_value = mock_storage
            
            success = await data_loader.initialize_storage()
            assert success
            assert data_loader.storage is not None


class TestLoadingProgress:
    """Test suite for LoadingProgress."""
    
    def test_initialization(self):
        """Test LoadingProgress initialization."""
        progress = LoadingProgress()
        
        assert progress.total_sources == 0
        assert progress.processed_sources == 0
        assert progress.total_chunks == 0
        assert progress.loaded_chunks == 0
        assert progress.failed_chunks == 0
        assert progress.errors == []
        assert progress.warnings == []
        assert progress.start_time is not None
    
    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        progress = LoadingProgress()
        
        # Test with zero chunks
        assert progress.progress_percentage == 0.0
        
        # Test with some progress
        progress.total_chunks = 100
        progress.loaded_chunks = 25
        assert progress.progress_percentage == 25.0
        
        progress.loaded_chunks = 100
        assert progress.progress_percentage == 100.0
    
    def test_success_rate(self):
        """Test success rate calculation."""
        progress = LoadingProgress()
        
        # Test with no processing
        assert progress.success_rate == 100.0
        
        # Test with some failures
        progress.loaded_chunks = 80
        progress.failed_chunks = 20
        assert progress.success_rate == 80.0
        
        # Test with all failures
        progress.loaded_chunks = 0
        progress.failed_chunks = 100
        assert progress.success_rate == 0.0


class TestDataLoadingMonitor:
    """Test suite for DataLoadingMonitor."""
    
    @pytest.fixture
    def mock_loader(self):
        """Create a mock CosmosDataLoader."""
        loader = Mock(spec=CosmosDataLoader)
        loader.get_loading_progress.return_value = {
            "total_sources": 2,
            "processed_sources": 1,
            "total_chunks": 100,
            "loaded_chunks": 50,
            "failed_chunks": 5,
            "current_source": "test_source",
            "progress_percentage": 50.0,
            "success_rate": 90.9,
            "duration_seconds": 30.0,
            "is_complete": False
        }
        return loader
    
    @pytest.fixture
    def monitor(self, mock_loader):
        """Create a DataLoadingMonitor instance."""
        return DataLoadingMonitor(mock_loader)
    
    def test_initialization(self, monitor, mock_loader):
        """Test monitor initialization."""
        assert monitor.loader == mock_loader
        assert not monitor.monitoring_active
        assert monitor.last_progress_update is None
        assert monitor.progress_history == []
    
    def test_generate_progress_report(self, monitor):
        """Test progress report generation."""
        # Set up some progress data
        monitor.last_progress_update = {
            "total_sources": 2,
            "processed_sources": 1,
            "total_chunks": 100,
            "loaded_chunks": 50,
            "failed_chunks": 5,
            "current_source": "test_source",
            "progress_percentage": 50.0,
            "success_rate": 90.9,
            "duration_seconds": 30.0,
            "is_complete": False
        }
        
        report = monitor.generate_progress_report()
        
        assert "current_status" in report
        assert "performance_metrics" in report
        assert "source_progress" in report
        assert report["current_status"]["progress_percentage"] == 50.0
        assert report["performance_metrics"]["chunks_per_second"] > 0


class TestDataQualityReport:
    """Test suite for DataQualityReport."""
    
    def test_initialization(self):
        """Test DataQualityReport initialization."""
        report = DataQualityReport(
            total_chunks=100,
            high_quality_chunks=60,
            medium_quality_chunks=30,
            low_quality_chunks=10,
            avg_chunk_size=500.0,
            avg_quality_score=1.5,
            sanskrit_terms_coverage=75.0,
            verse_reference_coverage=85.0,
            issues=[],
            recommendations=[]
        )
        
        assert report.total_chunks == 100
        assert report.high_quality_chunks == 60
        assert report.avg_quality_score == 1.5
    
    def test_quality_distribution(self):
        """Test quality distribution calculation."""
        report = DataQualityReport(
            total_chunks=100,
            high_quality_chunks=60,
            medium_quality_chunks=30,
            low_quality_chunks=10,
            avg_chunk_size=500.0,
            avg_quality_score=1.5,
            sanskrit_terms_coverage=75.0,
            verse_reference_coverage=85.0,
            issues=[],
            recommendations=[]
        )
        
        distribution = report.quality_distribution
        
        assert distribution["high"] == 60.0
        assert distribution["medium"] == 30.0
        assert distribution["low"] == 10.0
        
        # Test with zero chunks
        empty_report = DataQualityReport(
            total_chunks=0,
            high_quality_chunks=0,
            medium_quality_chunks=0,
            low_quality_chunks=0,
            avg_chunk_size=0.0,
            avg_quality_score=0.0,
            sanskrit_terms_coverage=0.0,
            verse_reference_coverage=0.0,
            issues=[],
            recommendations=[]
        )
        
        empty_distribution = empty_report.quality_distribution
        assert all(value == 0.0 for value in empty_distribution.values())


class TestTextProcessingIntegration:
    """Integration tests for text processing components."""
    
    def test_end_to_end_text_processing(self):
        """Test complete text processing pipeline."""
        # Sample spiritual text
        sample_text = """Chapter 2: The Yoga of Knowledge

2.47 You have a right to perform your prescribed duty, but do not claim entitlement to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.

2.48 Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure. Such equanimity is called yoga.

2.49 Far inferior indeed is mere action to the yoga of wisdom, O Arjuna. Seek refuge in wisdom. Pitiable are those who are motivated by the fruits of action."""
        
        # Process text
        processor = AdvancedSpiritualTextProcessor()
        chunks = processor.process_text_advanced(sample_text, "test_file.txt")
        
        assert len(chunks) > 0
        
        # Verify chunk properties
        for chunk in chunks:
            assert chunk.content is not None
            assert len(chunk.content) > 0
            assert chunk.text_type == TextType.BHAGAVAD_GITA
            assert chunk.quality_score > 0
            
            # Should have Sanskrit terms or spiritual content
            has_spiritual_content = (
                chunk.sanskrit_terms or 
                'dharma' in chunk.content.lower() or 
                'yoga' in chunk.content.lower() or
                'arjuna' in chunk.content.lower()
            )
            assert has_spiritual_content
    
    def test_chunk_quality_scoring(self):
        """Test chunk quality scoring."""
        processor = AdvancedSpiritualTextProcessor()
        
        # High quality chunk (has verses, Sanskrit terms, good length)
        high_quality_text = """2.47 You have a right to perform your prescribed duty (dharma), but do not claim entitlement to the fruits of action. This is the essence of karma yoga as taught by Krishna to Arjuna on the battlefield of Kurukshetra."""
        
        high_chunks = processor.process_text_advanced(high_quality_text, "test.txt")
        assert len(high_chunks) > 0
        assert high_chunks[0].quality_score >= 1.0
        
        # Low quality chunk (very short, no spiritual content)
        low_quality_text = "Hello world."
        
        low_chunks = processor.process_text_advanced(low_quality_text, "test.txt")
        assert len(low_chunks) > 0
        assert low_chunks[0].quality_score < 1.0


@pytest.mark.integration
class TestFullPipelineIntegration:
    """Integration tests for the complete data loading pipeline."""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_mock(self):
        """Test the complete pipeline with mocked dependencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sources_dir = temp_path / "sources"
            temp_processing = temp_path / "temp"
            
            sources_dir.mkdir()
            temp_processing.mkdir()
            
            # Create sample source file
            sample_file = sources_dir / "bhagavad_gita_sample.txt"
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write("""Chapter 2: The Yoga of Knowledge

2.47 You have a right to perform your prescribed duty, but do not claim entitlement to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.

2.48 Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure. Such equanimity is called yoga.""")
            
            # Mock embedding model
            with patch('backend.data_processing.cosmos_data_loader.SentenceTransformer') as mock_transformer:
                mock_model = Mock()
                mock_model.encode.return_value = [0.1] * 384
                mock_transformer.return_value = mock_model
                
                # Mock storage
                with patch('backend.data_processing.cosmos_data_loader.get_vector_storage') as mock_get_storage:
                    mock_storage = AsyncMock()
                    mock_storage.test_connection.return_value = True
                    mock_storage.add_chunk = AsyncMock()
                    mock_storage.search.return_value = []
                    mock_get_storage.return_value = mock_storage
                    
                    # Create loader
                    loader = CosmosDataLoader(
                        sources_directory=str(sources_dir),
                        temp_directory=str(temp_processing)
                    )
                    
                    # Register sources
                    success = loader.register_sample_sources()
                    assert success
                    
                    # Validate sources
                    validation = loader.validate_sources()
                    assert validation["valid_sources"] > 0
                    
                    # Load all sources
                    results = await loader.load_all_sources(validate_first=True)
                    
                    # Verify results
                    assert results["success"]
                    assert results["processed_sources"] > 0
                    assert results["successful_chunks"] > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
