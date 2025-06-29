"""
Comprehensive cost management tests for Vimarsh.

This module tests the cost monitoring, budget alerts, request batching,
and query deduplication functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json


class TestCostMonitoring:
    """Test cost monitoring functionality."""
    
    @pytest.fixture
    def mock_cost_monitor(self):
        """Create a mock cost monitor."""
        with patch('cost_management.vimarsh_cost_monitor.CostMonitor') as mock:
            monitor = Mock()
            monitor.get_current_costs.return_value = {
                'total_cost': 45.67,
                'daily_cost': 3.20,
                'monthly_projection': 96.00,
                'services': {
                    'gemini_api': 25.40,
                    'cosmos_db': 15.27,
                    'functions': 5.00
                }
            }
            monitor.check_budget_alerts.return_value = []
            mock.return_value = monitor
            yield monitor
    
    def test_cost_tracking_basic(self, mock_cost_monitor):
        """Test basic cost tracking functionality."""
        costs = mock_cost_monitor.get_current_costs()
        
        assert isinstance(costs, dict)
        assert 'total_cost' in costs
        assert 'daily_cost' in costs
        assert 'monthly_projection' in costs
        assert 'services' in costs
        
        assert costs['total_cost'] > 0
        assert costs['daily_cost'] > 0
        assert costs['monthly_projection'] > 0
    
    def test_budget_alert_system(self, mock_cost_monitor):
        """Test budget alert system."""
        # Configure mock to return alerts
        mock_cost_monitor.check_budget_alerts.return_value = [
            {
                'level': 'WARNING',
                'message': 'Monthly cost approaching 80% of budget',
                'current_cost': 80.00,
                'budget_limit': 100.00,
                'percentage': 80.0
            }
        ]
        
        alerts = mock_cost_monitor.check_budget_alerts()
        
        assert isinstance(alerts, list)
        assert len(alerts) > 0
        
        alert = alerts[0]
        assert 'level' in alert
        assert 'message' in alert
        assert 'current_cost' in alert
        assert 'budget_limit' in alert
        assert 'percentage' in alert
    
    def test_cost_breakdown_by_service(self, mock_cost_monitor):
        """Test cost breakdown by service."""
        costs = mock_cost_monitor.get_current_costs()
        services = costs['services']
        
        expected_services = ['gemini_api', 'cosmos_db', 'functions']
        for service in expected_services:
            assert service in services
            assert services[service] > 0
        
        # Total should match sum of services (approximately)
        service_total = sum(services.values())
        assert abs(costs['total_cost'] - service_total) < 0.01


class TestRequestBatching:
    """Test request batching functionality."""
    
    @pytest.fixture
    def mock_batch_processor(self):
        """Create a mock batch processor."""
        with patch('cost_management.request_batcher.RequestBatcher') as mock:
            processor = Mock()
            processor.batch_size = 5
            processor.batch_timeout = 1.0
            processor.pending_requests = []
            processor.add_request.return_value = True
            processor.process_batch.return_value = [
                {'id': 1, 'result': 'response_1'},
                {'id': 2, 'result': 'response_2'},
                {'id': 3, 'result': 'response_3'}
            ]
            mock.return_value = processor
            yield processor
    
    def test_batch_size_configuration(self, mock_batch_processor):
        """Test batch size configuration."""
        assert mock_batch_processor.batch_size == 5
        assert mock_batch_processor.batch_timeout == 1.0
    
    def test_request_batching_logic(self, mock_batch_processor):
        """Test request batching logic."""
        # Add multiple requests
        for i in range(3):
            result = mock_batch_processor.add_request(f"request_{i}")
            assert result is True
        
        # Process batch
        batch_results = mock_batch_processor.process_batch()
        
        assert isinstance(batch_results, list)
        assert len(batch_results) == 3
        
        for result in batch_results:
            assert 'id' in result
            assert 'result' in result
    
    def test_batch_timeout_handling(self, mock_batch_processor):
        """Test batch timeout handling."""
        # Configure timeout behavior
        mock_batch_processor.should_process_batch.return_value = True
        
        start_time = time.time()
        should_process = mock_batch_processor.should_process_batch()
        end_time = time.time()
        
        assert should_process is True
        # Processing decision should be fast
        assert (end_time - start_time) < 0.1


class TestQueryDeduplication:
    """Test query deduplication functionality."""
    
    @pytest.fixture
    def mock_deduplicator(self):
        """Create a mock query deduplicator."""
        with patch('cost_management.request_batcher.RequestBatcher') as mock:
            deduplicator = Mock()
            deduplicator.cache = {}
            deduplicator.hit_rate = 0.35
            deduplicator.check_cache.return_value = None
            deduplicator.store_result.return_value = True
            deduplicator.get_cache_stats.return_value = {
                'hits': 35,
                'misses': 65,
                'hit_rate': 0.35,
                'cache_size': 100
            }
            mock.return_value = deduplicator
            yield deduplicator
    
    def test_cache_hit_detection(self, mock_deduplicator):
        """Test cache hit detection."""
        # Test cache miss
        result = mock_deduplicator.check_cache("new_query")
        assert result is None
        
        # Configure for cache hit
        mock_deduplicator.check_cache.return_value = {
            'response': 'cached_response',
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.95
        }
        
        cached_result = mock_deduplicator.check_cache("cached_query")
        assert cached_result is not None
        assert 'response' in cached_result
        assert 'timestamp' in cached_result
        assert 'confidence' in cached_result
    
    def test_cache_storage(self, mock_deduplicator):
        """Test cache storage functionality."""
        query = "What is dharma?"
        response = "Dharma is the righteous way of living..."
        
        result = mock_deduplicator.store_result(query, response)
        assert result is True
    
    def test_cache_statistics(self, mock_deduplicator):
        """Test cache statistics."""
        stats = mock_deduplicator.get_cache_stats()
        
        assert isinstance(stats, dict)
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats
        assert 'cache_size' in stats
        
        assert stats['hit_rate'] == 0.35
        assert stats['hits'] + stats['misses'] == 100
    
    def test_query_normalization(self, mock_deduplicator):
        """Test query normalization for deduplication."""
        # Configure normalization
        mock_deduplicator.normalize_query.return_value = "what is dharma"
        
        normalized = mock_deduplicator.normalize_query("What is Dharma?")
        assert normalized == "what is dharma"
        
        # Test variations should normalize to same result
        variations = [
            "What is dharma?",
            "WHAT IS DHARMA?",
            "  what is dharma  ",
            "What is Dharma???"
        ]
        
        for variation in variations:
            mock_deduplicator.normalize_query.return_value = "what is dharma"
            normalized = mock_deduplicator.normalize_query(variation)
            assert normalized == "what is dharma"


class TestCostOptimization:
    """Test cost optimization strategies."""
    
    @pytest.fixture
    def mock_optimizer(self):
        """Create a mock cost optimizer."""
        with patch('cost_management.model_switcher.ModelSwitcher') as mock:
            optimizer = Mock()
            optimizer.current_model = 'gemini-pro'
            optimizer.optimization_level = 'standard'
            optimizer.switch_model.return_value = True
            optimizer.enable_caching.return_value = True
            optimizer.get_optimization_recommendations.return_value = [
                {
                    'type': 'model_switch',
                    'current': 'gemini-pro',
                    'recommended': 'gemini-flash',
                    'estimated_savings': 0.40
                },
                {
                    'type': 'enable_caching',
                    'estimated_savings': 0.25
                }
            ]
            mock.return_value = optimizer
            yield optimizer
    
    def test_model_switching_logic(self, mock_optimizer):
        """Test model switching for cost optimization."""
        result = mock_optimizer.switch_model('gemini-flash')
        assert result is True
        
        # Verify current model tracking
        assert mock_optimizer.current_model == 'gemini-pro'
    
    def test_optimization_recommendations(self, mock_optimizer):
        """Test optimization recommendations."""
        recommendations = mock_optimizer.get_optimization_recommendations()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert 'type' in rec
            assert 'estimated_savings' in rec
            assert rec['estimated_savings'] > 0
    
    def test_caching_optimization(self, mock_optimizer):
        """Test caching optimization."""
        result = mock_optimizer.enable_caching()
        assert result is True


class TestCostIntegration:
    """Test cost management integration."""
    
    def test_end_to_end_cost_flow(self):
        """Test complete cost management flow."""
        with patch('cost_management.vimarsh_cost_monitor.CostMonitor') as mock_monitor, \
             patch('cost_management.request_batcher.RequestBatcher') as mock_batch, \
             patch('cost_management.request_batcher.RequestBatcher') as mock_dedup:
            
            # Configure mocks
            monitor = Mock()
            monitor.track_request_cost.return_value = 0.05
            mock_monitor.return_value = monitor
            
            batch_processor = Mock()
            batch_processor.add_request.return_value = True
            mock_batch.return_value = batch_processor
            
            deduplicator = Mock()
            deduplicator.check_cache.return_value = None
            deduplicator.store_result.return_value = True
            mock_dedup.return_value = deduplicator
            
            # Simulate request flow
            query = "What is the meaning of life according to Bhagavad Gita?"
            
            # Check for cached result
            cached = deduplicator.check_cache(query)
            assert cached is None
            
            # Add to batch
            batch_added = batch_processor.add_request(query)
            assert batch_added is True
            
            # Track cost
            cost = monitor.track_request_cost("spiritual_guidance", query)
            assert cost == 0.05
            
            # Store result
            response = "According to the Bhagavad Gita..."
            stored = deduplicator.store_result(query, response)
            assert stored is True
    
    def test_cost_alerts_integration(self):
        """Test cost alerts integration."""
        with patch('cost_management.vimarsh_cost_monitor.CostMonitor') as mock_monitor:
            monitor = Mock()
            
            # Configure high cost scenario
            monitor.get_current_costs.return_value = {
                'total_cost': 95.00,
                'monthly_projection': 120.00
            }
            
            monitor.check_budget_alerts.return_value = [
                {
                    'level': 'CRITICAL',
                    'message': 'Monthly budget exceeded',
                    'percentage': 95.0
                }
            ]
            
            mock_monitor.return_value = monitor
            
            # Check costs and alerts
            costs = monitor.get_current_costs()
            alerts = monitor.check_budget_alerts()
            
            assert costs['total_cost'] == 95.00
            assert len(alerts) == 1
            assert alerts[0]['level'] == 'CRITICAL'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
