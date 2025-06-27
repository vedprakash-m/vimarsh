"""
Comprehensive Monitoring and Observability Tests for Vimarsh AI Agent

This module provides comprehensive testing for monitoring, metrics, logging,
and Application Insights integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any
import json
import time

from monitoring.app_insights import AppInsightsClient
from monitoring.metrics import MetricsCollector, SpiritualMetrics
from monitoring.health_check import HealthChecker
from tests.fixtures import SAMPLE_USER_QUERIES


class TestAppInsightsIntegration:
    """Test Application Insights integration."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.client = AppInsightsClient(connection_string="test_connection")
        self.metrics = SpiritualMetrics()
        
    def test_client_initialization(self):
        """Test App Insights client initialization."""
        assert self.client.connection_string == "test_connection"
        assert self.client.is_enabled is True
        
    def test_track_spiritual_guidance_request(self):
        """Test tracking spiritual guidance requests."""
        with patch.object(self.client, 'track_event') as mock_track:
            self.client.track_spiritual_guidance_request(
                query="What is dharma?",
                response_time=1.5,
                language="English",
                success=True
            )
            
            mock_track.assert_called_once()
            args = mock_track.call_args[1]
            assert args['event_name'] == 'SpiritualGuidanceRequest'
            assert args['properties']['language'] == 'English'
            assert args['measurements']['response_time'] == 1.5
            
    def test_track_error_with_context(self):
        """Test error tracking with spiritual context."""
        with patch.object(self.client, 'track_exception') as mock_track:
            try:
                raise ValueError("Test error")
            except Exception as e:
                self.client.track_error(
                    error=e,
                    context={
                        'query': 'Test query',
                        'component': 'rag_pipeline'
                    }
                )
                
            mock_track.assert_called_once()
            args = mock_track.call_args[1]
            assert 'query' in args['properties']
            assert args['properties']['component'] == 'rag_pipeline'
            
    def test_track_user_session(self):
        """Test user session tracking."""
        with patch.object(self.client, 'track_event') as mock_track:
            session_data = {
                'session_id': 'test_session_123',
                'duration': 300,
                'queries_count': 5,
                'languages_used': ['English', 'Hindi']
            }
            
            self.client.track_user_session(session_data)
            
            mock_track.assert_called_once()
            args = mock_track.call_args[1]
            assert args['event_name'] == 'UserSession'
            assert args['measurements']['duration'] == 300
            
    def test_track_performance_metrics(self):
        """Test performance metrics tracking."""
        with patch.object(self.client, 'track_metric') as mock_track:
            metrics = {
                'vector_search_time': 0.5,
                'llm_response_time': 2.3,
                'total_response_time': 3.1,
                'memory_usage': 512.5
            }
            
            for metric_name, value in metrics.items():
                self.client.track_performance_metric(metric_name, value)
                
            assert mock_track.call_count == len(metrics)


class TestMetricsCollector:
    """Test the metrics collection system."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.collector = MetricsCollector()
        
    def test_collect_spiritual_guidance_metrics(self):
        """Test spiritual guidance metrics collection."""
        metrics = self.collector.collect_spiritual_guidance_metrics(
            query="What is the meaning of life?",
            response_time=2.5,
            token_count=150,
            retrieval_count=5,
            success=True
        )
        
        assert metrics.response_time == 2.5
        assert metrics.token_count == 150
        assert metrics.retrieval_count == 5
        assert metrics.success is True
        assert metrics.timestamp is not None
        
    def test_aggregate_session_metrics(self):
        """Test session metrics aggregation."""
        # Simulate multiple requests in a session
        session_metrics = []
        for i in range(5):
            metrics = SpiritualMetrics(
                query_id=f"query_{i}",
                response_time=1.0 + i * 0.5,
                token_count=100 + i * 20,
                success=True
            )
            session_metrics.append(metrics)
            
        aggregated = self.collector.aggregate_session_metrics(session_metrics)
        
        assert aggregated['total_queries'] == 5
        assert aggregated['avg_response_time'] == 2.0  # (1.0 + 1.5 + 2.0 + 2.5 + 3.0) / 5
        assert aggregated['total_tokens'] == 600  # 100 + 120 + 140 + 160 + 180
        assert aggregated['success_rate'] == 1.0
        
    def test_performance_threshold_monitoring(self):
        """Test performance threshold monitoring."""
        thresholds = {
            'response_time': 5.0,
            'token_count': 1000,
            'memory_usage': 1024
        }
        
        # Test normal metrics
        normal_metrics = {
            'response_time': 2.0,
            'token_count': 500,
            'memory_usage': 512
        }
        
        alerts = self.collector.check_performance_thresholds(normal_metrics, thresholds)
        assert len(alerts) == 0
        
        # Test metrics exceeding thresholds
        high_metrics = {
            'response_time': 6.0,
            'token_count': 1200,
            'memory_usage': 2048
        }
        
        alerts = self.collector.check_performance_thresholds(high_metrics, thresholds)
        assert len(alerts) == 3
        assert any('response_time' in alert for alert in alerts)
        
    def test_spiritual_quality_metrics(self):
        """Test spiritual quality metrics tracking."""
        quality_scores = {
            'authenticity': 0.95,
            'reverence': 0.92,
            'scriptural_accuracy': 0.88,
            'cultural_sensitivity': 0.96
        }
        
        metrics = self.collector.collect_quality_metrics(
            query_id="test_query",
            quality_scores=quality_scores
        )
        
        assert metrics.authenticity_score == 0.95
        assert metrics.overall_quality == sum(quality_scores.values()) / len(quality_scores)
        assert metrics.passes_quality_threshold(0.90) is True
        assert metrics.passes_quality_threshold(0.95) is False


class TestHealthChecker:
    """Test system health checking."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.health_checker = HealthChecker()
        
    @pytest.mark.asyncio
    async def test_check_database_health(self):
        """Test database health checking."""
        with patch('monitoring.health_check.CosmosClient') as mock_client:
            mock_client.return_value.get_database_client.return_value.read.return_value = {}
            
            health_status = await self.health_checker.check_database_health()
            
            assert health_status['status'] == 'healthy'
            assert health_status['component'] == 'cosmos_db'
            assert 'response_time' in health_status
            
    @pytest.mark.asyncio
    async def test_check_llm_health(self):
        """Test LLM service health checking."""
        with patch('llm.gemini_client.GeminiProClient.generate_spiritual_guidance') as mock_llm:
            mock_response = Mock()
            mock_response.success = True
            mock_response.response = "Test response"
            mock_llm.return_value = mock_response
            
            health_status = await self.health_checker.check_llm_health()
            
            assert health_status['status'] == 'healthy'
            assert health_status['component'] == 'gemini_pro'
            
    @pytest.mark.asyncio
    async def test_check_vector_search_health(self):
        """Test vector search health checking."""
        with patch('rag_pipeline.vector_storage.CosmosVectorSearch.search') as mock_search:
            mock_search.return_value = [{'text': 'test', 'similarity': 0.8}]
            
            health_status = await self.health_checker.check_vector_search_health()
            
            assert health_status['status'] == 'healthy'
            assert health_status['component'] == 'vector_search'
            
    @pytest.mark.asyncio
    async def test_comprehensive_health_check(self):
        """Test comprehensive system health check."""
        with patch.object(self.health_checker, 'check_database_health') as mock_db:
            with patch.object(self.health_checker, 'check_llm_health') as mock_llm:
                with patch.object(self.health_checker, 'check_vector_search_health') as mock_vector:
                    mock_db.return_value = {'status': 'healthy', 'component': 'cosmos_db'}
                    mock_llm.return_value = {'status': 'healthy', 'component': 'gemini_pro'}
                    mock_vector.return_value = {'status': 'healthy', 'component': 'vector_search'}
                    
                    overall_health = await self.health_checker.comprehensive_health_check()
                    
                    assert overall_health['overall_status'] == 'healthy'
                    assert len(overall_health['components']) == 3
                    assert all(c['status'] == 'healthy' for c in overall_health['components'])
                    
    @pytest.mark.asyncio
    async def test_health_check_with_failures(self):
        """Test health check with component failures."""
        with patch.object(self.health_checker, 'check_database_health') as mock_db:
            with patch.object(self.health_checker, 'check_llm_health') as mock_llm:
                mock_db.return_value = {'status': 'unhealthy', 'component': 'cosmos_db', 'error': 'Connection failed'}
                mock_llm.return_value = {'status': 'healthy', 'component': 'gemini_pro'}
                
                overall_health = await self.health_checker.comprehensive_health_check()
                
                assert overall_health['overall_status'] == 'degraded'
                assert any(c['status'] == 'unhealthy' for c in overall_health['components'])


class TestAlertingSystem:
    """Test alerting and notification system."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        from monitoring.alerts import AlertManager
        self.alert_manager = AlertManager()
        
    def test_performance_alert_creation(self):
        """Test performance alert creation."""
        alert = self.alert_manager.create_performance_alert(
            metric_name='response_time',
            current_value=10.0,
            threshold=5.0,
            severity='critical'
        )
        
        assert alert.metric_name == 'response_time'
        assert alert.severity == 'critical'
        assert alert.threshold_exceeded is True
        assert 'response_time' in alert.message
        
    def test_error_rate_alert(self):
        """Test error rate alerting."""
        # Simulate high error rate
        error_metrics = {
            'total_requests': 100,
            'failed_requests': 15,
            'error_rate': 0.15
        }
        
        alert = self.alert_manager.check_error_rate_threshold(
            error_metrics, 
            threshold=0.10
        )
        
        assert alert is not None
        assert alert.severity in ['warning', 'critical']
        assert 'error rate' in alert.message.lower()
        
    def test_spiritual_quality_alert(self):
        """Test spiritual quality degradation alerting."""
        quality_metrics = {
            'authenticity_score': 0.75,  # Below typical threshold
            'reverence_score': 0.80,
            'accuracy_score': 0.70
        }
        
        alert = self.alert_manager.check_quality_degradation(
            quality_metrics,
            min_threshold=0.85
        )
        
        assert alert is not None
        assert 'quality' in alert.message.lower()
        assert alert.requires_expert_review is True


class TestRealTimeMonitoring:
    """Test real-time monitoring capabilities."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        from monitoring.real_time import RealTimeMonitor
        self.monitor = RealTimeMonitor()
        
    @pytest.mark.asyncio
    async def test_real_time_metrics_streaming(self):
        """Test real-time metrics streaming."""
        metrics_buffer = []
        
        def metrics_callback(metric):
            metrics_buffer.append(metric)
            
        # Start monitoring (mock)
        with patch.object(self.monitor, 'start_monitoring') as mock_start:
            mock_start.return_value = asyncio.create_task(asyncio.sleep(0.1))
            
            # Simulate metrics
            for i in range(5):
                metric = {
                    'timestamp': time.time(),
                    'metric_name': 'response_time',
                    'value': 1.0 + i * 0.1,
                    'component': 'spiritual_guidance'
                }
                self.monitor.emit_metric(metric)
                
            await asyncio.sleep(0.2)
            
            # Verify metrics were processed
            assert len(self.monitor.metrics_buffer) >= 5
            
    def test_anomaly_detection(self):
        """Test anomaly detection in metrics."""
        # Create baseline metrics
        baseline_metrics = [1.0, 1.1, 0.9, 1.2, 1.0, 0.8, 1.1] * 10  # 70 samples
        
        # Test normal value
        is_anomaly = self.monitor.detect_anomaly('response_time', 1.0, baseline_metrics)
        assert is_anomaly is False
        
        # Test anomalous value
        is_anomaly = self.monitor.detect_anomaly('response_time', 5.0, baseline_metrics)
        assert is_anomaly is True
        
    def test_dashboard_data_aggregation(self):
        """Test dashboard data aggregation."""
        # Simulate various metrics over time
        raw_metrics = []
        for i in range(60):  # 60 seconds of data
            raw_metrics.append({
                'timestamp': time.time() - (60 - i),
                'response_time': 1.0 + (i % 10) * 0.1,
                'token_count': 100 + (i % 20) * 5,
                'success': i % 10 != 0  # 10% failure rate
            })
            
        dashboard_data = self.monitor.aggregate_for_dashboard(
            raw_metrics, 
            time_window=60
        )
        
        assert 'avg_response_time' in dashboard_data
        assert 'success_rate' in dashboard_data
        assert 'total_requests' in dashboard_data
        assert dashboard_data['total_requests'] == 60
        assert 0.85 <= dashboard_data['success_rate'] <= 0.95  # Approximately 90%
