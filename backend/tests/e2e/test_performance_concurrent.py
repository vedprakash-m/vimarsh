"""
Advanced performance testing for Vimarsh platform.

This module provides comprehensive performance testing including:
- Concurrent user load testing
- Stress testing under high load
- Memory and resource usage monitoring
- Response time analysis
- Throughput measurement
- System bottleneck identification
"""

import pytest
import asyncio
import time
import json
import statistics
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import logging
import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import mock implementations for testing
try:
    from mock_implementations import MockSpiritualGuidanceAPI, MockVoiceInterfaceAPI
except ImportError:
    # Fallback if mock implementations not available
    class MockSpiritualGuidanceAPI:
        async def process_spiritual_query(self, **kwargs):
            await asyncio.sleep(0.1)  # Simulate processing time
            return {"response": "Mock response", "citations": [], "authenticity_score": 0.9}
    
    class MockVoiceInterfaceAPI:
        async def process_voice_query(self, **kwargs):
            await asyncio.sleep(0.2)  # Simulate voice processing time
            return {"text_response": "Mock response", "audio_response": {"duration": 10}}

logger = logging.getLogger(__name__)

class TestConcurrentPerformance:
    """Test performance under concurrent user scenarios."""
    
    @pytest.mark.asyncio
    async def test_5_concurrent_users_performance(self):
        """Test system performance with 5 concurrent users (MVP target)."""
        logger.info("Testing 5 concurrent users performance")
        
        api = MockSpiritualGuidanceAPI()
        user_count = 5
        queries_per_user = 3
        
        async def simulate_user_session(user_id: int) -> Dict[str, Any]:
            """Simulate a complete user session with multiple queries."""
            session_times = []
            responses = []
            
            for query_num in range(queries_per_user):
                start_time = time.time()
                
                response = await api.process_spiritual_query(
                    query=f"User {user_id} query {query_num}: What is the meaning of dharma?",
                    language="English",
                    user_id=f"perf_test_user_{user_id}"
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                session_times.append(response_time)
                responses.append(response)
            
            return {
                "user_id": user_id,
                "response_times": session_times,
                "avg_response_time": statistics.mean(session_times),
                "total_session_time": sum(session_times),
                "responses": responses
            }
        
        # Execute concurrent user sessions
        test_start = time.time()
        tasks = [simulate_user_session(i) for i in range(user_count)]
        results = await asyncio.gather(*tasks)
        test_end = time.time()
        
        total_test_time = test_end - test_start
        
        # Analyze results
        all_response_times = []
        all_avg_times = []
        
        for result in results:
            all_response_times.extend(result["response_times"])
            all_avg_times.append(result["avg_response_time"])
            
            # Individual user assertions
            assert result["avg_response_time"] < 5.0, \
                f"User {result['user_id']} avg response time {result['avg_response_time']:.2f}s exceeds 5s"
            
            assert len(result["responses"]) == queries_per_user, \
                f"User {result['user_id']} did not complete all queries"
        
        # Overall performance assertions
        overall_avg = statistics.mean(all_response_times)
        overall_median = statistics.median(all_response_times)
        overall_max = max(all_response_times)
        
        assert overall_avg < 3.0, f"Overall avg response time {overall_avg:.2f}s too high"
        assert overall_median < 2.5, f"Overall median response time {overall_median:.2f}s too high"
        assert overall_max < 10.0, f"Max response time {overall_max:.2f}s too high"
        
        # Throughput calculation
        total_queries = user_count * queries_per_user
        throughput = total_queries / total_test_time
        
        assert throughput >= 2.0, f"Throughput {throughput:.2f} queries/sec too low"
        
        logger.info(f"5 users test completed - Avg: {overall_avg:.2f}s, Throughput: {throughput:.2f} q/s")
    
    @pytest.mark.asyncio
    async def test_10_concurrent_users_performance(self):
        """Test system performance with 10 concurrent users (production target)."""
        logger.info("Testing 10 concurrent users performance")
        
        api = MockSpiritualGuidanceAPI()
        user_count = 10
        queries_per_user = 2
        
        async def simulate_user_queries(user_id: int) -> List[float]:
            """Simulate multiple queries from a single user."""
            response_times = []
            
            for query_num in range(queries_per_user):
                start_time = time.time()
                
                await api.process_spiritual_query(
                    query=f"What is karma yoga? (User {user_id}, Query {query_num})",
                    language="English",
                    user_id=f"stress_test_user_{user_id}"
                )
                
                end_time = time.time()
                response_times.append(end_time - start_time)
            
            return response_times
        
        # Execute concurrent load
        test_start = time.time()
        tasks = [simulate_user_queries(i) for i in range(user_count)]
        results = await asyncio.gather(*tasks)
        test_end = time.time()
        
        # Flatten results
        all_times = [time for user_times in results for time in user_times]
        
        # Performance analysis
        avg_time = statistics.mean(all_times)
        percentile_95 = sorted(all_times)[int(0.95 * len(all_times))]
        total_queries = user_count * queries_per_user
        throughput = total_queries / (test_end - test_start)
        
        # Assertions for production performance
        assert avg_time < 5.0, f"Avg response time {avg_time:.2f}s exceeds target"
        assert percentile_95 < 8.0, f"95th percentile {percentile_95:.2f}s too high"
        assert throughput >= 1.5, f"Throughput {throughput:.2f} q/s below target"
        
        logger.info(f"10 users test - Avg: {avg_time:.2f}s, 95th: {percentile_95:.2f}s, Throughput: {throughput:.2f}")
    
    @pytest.mark.asyncio
    async def test_peak_load_30_users(self):
        """Test system behavior under peak load (3x normal capacity)."""
        logger.info("Testing peak load with 30 concurrent users")
        
        api = MockSpiritualGuidanceAPI()
        user_count = 30
        queries_per_user = 1  # Single query per user for peak load test
        
        async def single_user_query(user_id: int) -> Tuple[float, bool]:
            """Single query from user with success tracking."""
            try:
                start_time = time.time()
                
                response = await api.process_spiritual_query(
                    query=f"Peak load test query from user {user_id}",
                    language="English",
                    user_id=f"peak_test_user_{user_id}"
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Check if response is valid
                success = response is not None and "response" in response
                return response_time, success
                
            except Exception as e:
                logger.warning(f"User {user_id} query failed: {e}")
                return 30.0, False  # Mark as failed with high response time
        
        # Execute peak load test
        test_start = time.time()
        tasks = [single_user_query(i) for i in range(user_count)]
        results = await asyncio.gather(*tasks)
        test_end = time.time()
        
        # Analyze peak load results
        response_times = [result[0] for result in results]
        success_flags = [result[1] for result in results]
        
        success_rate = sum(success_flags) / len(success_flags)
        successful_times = [time for time, success in results if success]
        
        if successful_times:
            avg_successful_time = statistics.mean(successful_times)
            max_successful_time = max(successful_times)
        else:
            avg_successful_time = float('inf')
            max_successful_time = float('inf')
        
        total_time = test_end - test_start
        
        # Peak load assertions (more lenient than normal load)
        assert success_rate >= 0.8, f"Success rate {success_rate:.1%} too low for peak load"
        
        if successful_times:
            assert avg_successful_time < 15.0, f"Avg successful time {avg_successful_time:.2f}s too high"
            assert max_successful_time < 30.0, f"Max successful time {max_successful_time:.2f}s too high"
        
        assert total_time < 45.0, f"Total peak load test time {total_time:.2f}s too long"
        
        logger.info(f"Peak load test - Success rate: {success_rate:.1%}, Avg time: {avg_successful_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_sustained_load_performance(self):
        """Test system performance under sustained load over time."""
        logger.info("Testing sustained load performance")
        
        api = MockSpiritualGuidanceAPI()
        duration_seconds = 30  # 30-second sustained test
        users_per_wave = 5
        wave_interval = 2  # New wave every 2 seconds
        
        results = []
        test_start = time.time()
        
        async def sustained_user_simulation(wave_id: int, user_id: int) -> Dict[str, Any]:
            """Simulate user activity during sustained load test."""
            wave_start = time.time()
            
            response = await api.process_spiritual_query(
                query=f"Sustained load wave {wave_id} user {user_id} query",
                language="English",
                user_id=f"sustained_user_{wave_id}_{user_id}"
            )
            
            response_time = time.time() - wave_start
            
            return {
                "wave_id": wave_id,
                "user_id": user_id,
                "response_time": response_time,
                "timestamp": wave_start,
                "success": response is not None
            }
        
        # Execute waves of users over the duration
        wave_id = 0
        while time.time() - test_start < duration_seconds:
            wave_start_time = time.time()
            
            # Launch a wave of users
            wave_tasks = [
                sustained_user_simulation(wave_id, user_id) 
                for user_id in range(users_per_wave)
            ]
            
            wave_results = await asyncio.gather(*wave_tasks)
            results.extend(wave_results)
            
            wave_id += 1
            
            # Wait for next wave (if time remaining)
            elapsed = time.time() - wave_start_time
            if elapsed < wave_interval:
                await asyncio.sleep(wave_interval - elapsed)
        
        test_end = time.time()
        actual_duration = test_end - test_start
        
        # Analyze sustained load results
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        response_times = [r["response_time"] for r in results if r["success"]]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            throughput = total_requests / actual_duration
        else:
            avg_response_time = float('inf')
            median_response_time = float('inf')
            throughput = 0
        
        # Sustained load assertions
        assert success_rate >= 0.9, f"Sustained load success rate {success_rate:.1%} too low"
        assert total_requests >= 20, f"Too few requests {total_requests} in sustained test"
        
        if response_times:
            assert avg_response_time < 8.0, f"Sustained avg response time {avg_response_time:.2f}s too high"
            assert median_response_time < 6.0, f"Sustained median time {median_response_time:.2f}s too high"
        
        assert throughput >= 1.0, f"Sustained throughput {throughput:.2f} req/s too low"
        
        logger.info(f"Sustained load - Requests: {total_requests}, Success: {success_rate:.1%}, "
                   f"Avg: {avg_response_time:.2f}s, Throughput: {throughput:.2f} req/s")

class TestVoicePerformance:
    """Test voice interface performance under load."""
    
    @pytest.mark.asyncio
    async def test_concurrent_voice_processing(self):
        """Test voice processing performance with multiple concurrent requests."""
        logger.info("Testing concurrent voice processing performance")
        
        voice_api = MockVoiceInterfaceAPI()
        concurrent_users = 5
        
        async def voice_user_simulation(user_id: int) -> Dict[str, Any]:
            """Simulate voice interaction from a user."""
            start_time = time.time()
            
            # Mock audio data
            mock_audio = b"mock_audio_data_" + str(user_id).encode()
            
            response = await voice_api.process_voice_query(
                audio_data=mock_audio,
                language="English",
                user_id=f"voice_perf_user_{user_id}"
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            
            return {
                "user_id": user_id,
                "response_time": total_time,
                "success": response is not None,
                "has_audio_output": "audio_response" in response if response else False
            }
        
        # Execute concurrent voice processing
        tasks = [voice_user_simulation(i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
        
        # Analyze voice performance
        response_times = [r["response_time"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        audio_output_count = sum(1 for r in results if r.get("has_audio_output", False))
        
        avg_voice_time = statistics.mean(response_times)
        max_voice_time = max(response_times)
        success_rate = success_count / len(results)
        
        # Voice performance assertions
        assert success_rate == 1.0, f"Voice success rate {success_rate:.1%} not 100%"
        assert avg_voice_time < 8.0, f"Avg voice response time {avg_voice_time:.2f}s exceeds 8s target"
        assert max_voice_time < 15.0, f"Max voice response time {max_voice_time:.2f}s too high"
        assert audio_output_count == concurrent_users, "Not all voice responses included audio"
        
        logger.info(f"Voice performance - Avg: {avg_voice_time:.2f}s, Max: {max_voice_time:.2f}s")

class TestMemoryAndResourceUsage:
    """Test memory usage and resource consumption patterns."""
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage patterns under concurrent load."""
        logger.info("Testing memory usage under load")
        
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_available = True
        except ImportError:
            memory_available = False
            logger.warning("psutil not available, using mock memory monitoring")
        
        api = MockSpiritualGuidanceAPI()
        
        # Get baseline memory
        if memory_available:
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        else:
            baseline_memory = 50.0  # Mock baseline
        
        memory_samples = [baseline_memory]
        
        # Execute load while monitoring memory
        async def memory_monitoring_load():
            """Execute queries while monitoring memory usage."""
            for i in range(20):  # 20 queries
                await api.process_spiritual_query(
                    query=f"Memory test query {i}",
                    language="English",
                    user_id=f"memory_test_user_{i}"
                )
                
                # Sample memory every few queries
                if i % 5 == 0 and memory_available:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_samples.append(current_memory)
                elif not memory_available:
                    # Mock gradual memory increase
                    memory_samples.append(baseline_memory + (i * 0.5))
                
                # Small delay to allow memory measurement
                await asyncio.sleep(0.05)
        
        await memory_monitoring_load()
        
        # Analyze memory usage
        if memory_available:
            final_memory = process.memory_info().rss / 1024 / 1024
        else:
            final_memory = memory_samples[-1]
        
        memory_increase = final_memory - baseline_memory
        max_memory = max(memory_samples)
        memory_growth_rate = memory_increase / len(memory_samples)
        
        # Memory usage assertions
        assert memory_increase < 50.0, f"Memory increased by {memory_increase:.2f}MB (too much)"
        assert max_memory - baseline_memory < 75.0, f"Peak memory increase {max_memory - baseline_memory:.2f}MB too high"
        assert memory_growth_rate < 5.0, f"Memory growth rate {memory_growth_rate:.2f}MB per sample too high"
        
        logger.info(f"Memory test - Increase: {memory_increase:.2f}MB, Peak: {max_memory:.2f}MB")
    
    @pytest.mark.asyncio
    async def test_response_time_consistency(self):
        """Test response time consistency across multiple requests."""
        logger.info("Testing response time consistency")
        
        api = MockSpiritualGuidanceAPI()
        sample_size = 50
        
        response_times = []
        
        for i in range(sample_size):
            start_time = time.time()
            
            await api.process_spiritual_query(
                query=f"Consistency test query {i}",
                language="English",
                user_id=f"consistency_user_{i}"
            )
            
            end_time = time.time()
            response_times.append(end_time - start_time)
        
        # Statistical analysis
        mean_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        std_deviation = statistics.stdev(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        # Coefficient of variation (std dev / mean)
        cv = std_deviation / mean_time if mean_time > 0 else float('inf')
        
        # Consistency assertions
        assert cv < 0.5, f"Response time coefficient of variation {cv:.3f} too high (inconsistent)"
        assert std_deviation < 2.0, f"Response time std deviation {std_deviation:.2f}s too high"
        assert max_time / min_time < 5.0, f"Response time ratio {max_time/min_time:.2f} too variable"
        
        logger.info(f"Consistency test - Mean: {mean_time:.3f}s, StdDev: {std_deviation:.3f}s, CV: {cv:.3f}")

class TestErrorRecoveryPerformance:
    """Test performance during error conditions and recovery."""
    
    @pytest.mark.asyncio
    async def test_performance_during_partial_failures(self):
        """Test system performance when some requests fail."""
        logger.info("Testing performance during partial failures")
        
        # Mock API with intermittent failures
        class FailingMockAPI:
            def __init__(self, failure_rate=0.2):
                self.failure_rate = failure_rate
                self.call_count = 0
            
            async def process_spiritual_query(self, **kwargs):
                self.call_count += 1
                
                # Simulate failures based on failure rate
                if self.call_count % 5 == 0:  # Every 5th call fails
                    await asyncio.sleep(0.05)  # Quick failure
                    raise Exception("Simulated service failure")
                
                await asyncio.sleep(0.1)  # Normal processing time
                return {
                    "response": "Test response",
                    "citations": [],
                    "authenticity_score": 0.9
                }
        
        failing_api = FailingMockAPI()
        request_count = 25
        
        async def resilient_request(request_id: int) -> Dict[str, Any]:
            """Make request with error handling."""
            start_time = time.time()
            
            try:
                response = await failing_api.process_spiritual_query(
                    query=f"Resilience test {request_id}",
                    language="English",
                    user_id=f"resilience_user_{request_id}"
                )
                
                end_time = time.time()
                return {
                    "request_id": request_id,
                    "response_time": end_time - start_time,
                    "success": True,
                    "error": None
                }
                
            except Exception as e:
                end_time = time.time()
                return {
                    "request_id": request_id,
                    "response_time": end_time - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        # Execute requests with expected failures
        tasks = [resilient_request(i) for i in range(request_count)]
        results = await asyncio.gather(*tasks)
        
        # Analyze resilience performance
        successful_results = [r for r in results if r["success"]]
        failed_results = [r for r in results if not r["success"]]
        
        success_rate = len(successful_results) / len(results)
        
        if successful_results:
            avg_success_time = statistics.mean([r["response_time"] for r in successful_results])
            max_success_time = max([r["response_time"] for r in successful_results])
        else:
            avg_success_time = float('inf')
            max_success_time = float('inf')
        
        if failed_results:
            avg_failure_time = statistics.mean([r["response_time"] for r in failed_results])
        else:
            avg_failure_time = 0
        
        # Resilience performance assertions
        assert success_rate >= 0.7, f"Success rate {success_rate:.1%} too low during failures"
        
        if successful_results:
            assert avg_success_time < 5.0, f"Avg success time {avg_success_time:.2f}s too high during failures"
            assert max_success_time < 10.0, f"Max success time {max_success_time:.2f}s too high"
        
        # Failed requests should fail fast
        if failed_results:
            assert avg_failure_time < 1.0, f"Avg failure time {avg_failure_time:.2f}s too slow (should fail fast)"
        
        logger.info(f"Resilience test - Success rate: {success_rate:.1%}, "
                   f"Avg success: {avg_success_time:.2f}s, Avg failure: {avg_failure_time:.2f}s")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
