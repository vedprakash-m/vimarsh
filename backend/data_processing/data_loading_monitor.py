"""
Data Loading Monitor and Validator
Task 8.8: Load and chunk source texts into production Cosmos DB

Provides real-time monitoring, validation, and quality assurance
for the data loading process.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json
from pathlib import Path
from dataclasses import dataclass, asdict

# Import our modules
from cosmos_data_loader import CosmosDataLoader, LoadingProgress
from ..rag.storage_factory import get_vector_storage
from ..monitoring.app_insights_client import AppInsightsClient

logger = logging.getLogger(__name__)


@dataclass
class DataQualityReport:
    """Report on data quality metrics."""
    
    total_chunks: int
    high_quality_chunks: int
    medium_quality_chunks: int
    low_quality_chunks: int
    
    avg_chunk_size: float
    avg_quality_score: float
    
    sanskrit_terms_coverage: float
    verse_reference_coverage: float
    
    issues: List[str]
    recommendations: List[str]
    
    @property
    def quality_distribution(self) -> Dict[str, float]:
        """Get quality distribution percentages."""
        if self.total_chunks == 0:
            return {"high": 0.0, "medium": 0.0, "low": 0.0}
        
        return {
            "high": (self.high_quality_chunks / self.total_chunks) * 100,
            "medium": (self.medium_quality_chunks / self.total_chunks) * 100,
            "low": (self.low_quality_chunks / self.total_chunks) * 100
        }


class DataLoadingMonitor:
    """
    Monitors data loading operations and provides real-time feedback.
    
    Tracks progress, validates quality, and provides recommendations
    for optimization.
    """
    
    def __init__(self, 
                 loader: CosmosDataLoader,
                 app_insights: Optional[AppInsightsClient] = None):
        """
        Initialize the data loading monitor.
        
        Args:
            loader: CosmosDataLoader instance to monitor
            app_insights: Application Insights client for telemetry
        """
        self.loader = loader
        self.app_insights = app_insights
        
        # Monitoring state
        self.monitoring_active = False
        self.last_progress_update = None
        self.progress_history = []
        
        logger.info("DataLoadingMonitor initialized")
    
    async def start_monitoring(self, update_interval: int = 10) -> None:
        """
        Start real-time monitoring of the data loading process.
        
        Args:
            update_interval: Seconds between progress updates
        """
        self.monitoring_active = True
        logger.info(f"Starting data loading monitoring (update interval: {update_interval}s)")
        
        while self.monitoring_active:
            try:
                # Get current progress
                progress = self.loader.get_loading_progress()
                
                # Log progress update
                self._log_progress_update(progress)
                
                # Send telemetry if available
                if self.app_insights:
                    await self._send_progress_telemetry(progress)
                
                # Store progress history
                progress["timestamp"] = datetime.now(timezone.utc).isoformat()
                self.progress_history.append(progress)
                
                # Keep only last 100 updates
                if len(self.progress_history) > 100:
                    self.progress_history = self.progress_history[-100:]
                
                self.last_progress_update = progress
                
                # Check if loading is complete
                if progress.get("is_complete", False):
                    logger.info("Data loading completed, stopping monitoring")
                    break
                
                # Wait for next update
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(update_interval)
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring process."""
        self.monitoring_active = False
        logger.info("Data loading monitoring stopped")
    
    def _log_progress_update(self, progress: Dict[str, Any]) -> None:
        """Log a progress update."""
        if progress["total_chunks"] > 0:
            percentage = progress["progress_percentage"]
            loaded = progress["loaded_chunks"]
            total = progress["total_chunks"]
            failed = progress["failed_chunks"]
            success_rate = progress["success_rate"]
            
            current_source = progress.get("current_source", "")
            source_info = f" (Current: {current_source})" if current_source else ""
            
            logger.info(
                f"Loading Progress: {percentage:.1f}% "
                f"({loaded}/{total} chunks, {failed} failed, "
                f"{success_rate:.1f}% success rate){source_info}"
            )
    
    async def _send_progress_telemetry(self, progress: Dict[str, Any]) -> None:
        """Send progress telemetry to Application Insights."""
        try:
            # Track loading metrics
            metrics = {
                "data_loading_progress": progress["progress_percentage"],
                "chunks_loaded": progress["loaded_chunks"],
                "chunks_failed": progress["failed_chunks"],
                "success_rate": progress["success_rate"]
            }
            
            properties = {
                "current_source": progress.get("current_source", ""),
                "total_sources": str(progress["total_sources"]),
                "processed_sources": str(progress["processed_sources"])
            }
            
            await self.app_insights.track_metrics("DataLoadingProgress", metrics, properties)
            
        except Exception as e:
            logger.error(f"Failed to send progress telemetry: {str(e)}")
    
    async def validate_data_quality(self) -> DataQualityReport:
        """
        Validate the quality of loaded data.
        
        Returns:
            DataQualityReport with quality metrics and recommendations
        """
        logger.info("Starting data quality validation...")
        
        try:
            # Initialize storage to query loaded data
            storage = await get_vector_storage()
            
            # Get sample of loaded chunks for analysis
            sample_queries = [
                "dharma",
                "Krishna",
                "yoga",
                "Arjuna",
                "meditation",
                "devotion",
                "wisdom",
                "soul"
            ]
            
            all_chunks = []
            for query in sample_queries:
                try:
                    results = await storage.search(query, top_k=20)
                    all_chunks.extend(results)
                except Exception as e:
                    logger.warning(f"Failed to query '{query}': {str(e)}")
            
            # Remove duplicates based on chunk ID
            unique_chunks = {chunk.id: chunk for chunk in all_chunks}.values()
            chunks = list(unique_chunks)
            
            logger.info(f"Analyzing {len(chunks)} unique chunks for quality...")
            
            # Analyze quality metrics
            total_chunks = len(chunks)
            if total_chunks == 0:
                return DataQualityReport(
                    total_chunks=0,
                    high_quality_chunks=0,
                    medium_quality_chunks=0,
                    low_quality_chunks=0,
                    avg_chunk_size=0.0,
                    avg_quality_score=0.0,
                    sanskrit_terms_coverage=0.0,
                    verse_reference_coverage=0.0,
                    issues=["No chunks found for analysis"],
                    recommendations=["Check data loading process"]
                )
            
            # Calculate quality distribution
            high_quality = sum(1 for chunk in chunks if chunk.quality_score >= 1.5)
            medium_quality = sum(1 for chunk in chunks if 1.0 <= chunk.quality_score < 1.5)
            low_quality = sum(1 for chunk in chunks if chunk.quality_score < 1.0)
            
            # Calculate averages
            avg_chunk_size = sum(len(chunk.content) for chunk in chunks) / total_chunks
            avg_quality_score = sum(chunk.quality_score for chunk in chunks) / total_chunks
            
            # Calculate coverage metrics
            chunks_with_sanskrit = sum(1 for chunk in chunks if chunk.sanskrit_terms)
            sanskrit_coverage = (chunks_with_sanskrit / total_chunks) * 100
            
            chunks_with_verses = sum(1 for chunk in chunks if chunk.chapter and chunk.verse)
            verse_coverage = (chunks_with_verses / total_chunks) * 100
            
            # Identify issues and recommendations
            issues = []
            recommendations = []
            
            if avg_quality_score < 1.2:
                issues.append(f"Low average quality score: {avg_quality_score:.2f}")
                recommendations.append("Review text processing parameters and source quality")
            
            if sanskrit_coverage < 50:
                issues.append(f"Low Sanskrit terms coverage: {sanskrit_coverage:.1f}%")
                recommendations.append("Verify Sanskrit term extraction is working correctly")
            
            if verse_coverage < 30:
                issues.append(f"Low verse reference coverage: {verse_coverage:.1f}%")
                recommendations.append("Check verse boundary detection in text processing")
            
            if avg_chunk_size < 200:
                issues.append(f"Small average chunk size: {avg_chunk_size:.0f} characters")
                recommendations.append("Consider increasing chunk size for better context")
            elif avg_chunk_size > 1000:
                issues.append(f"Large average chunk size: {avg_chunk_size:.0f} characters")
                recommendations.append("Consider reducing chunk size for better retrieval")
            
            # Create quality report
            report = DataQualityReport(
                total_chunks=total_chunks,
                high_quality_chunks=high_quality,
                medium_quality_chunks=medium_quality,
                low_quality_chunks=low_quality,
                avg_chunk_size=avg_chunk_size,
                avg_quality_score=avg_quality_score,
                sanskrit_terms_coverage=sanskrit_coverage,
                verse_reference_coverage=verse_coverage,
                issues=issues,
                recommendations=recommendations
            )
            
            logger.info(f"Data quality validation complete: {report}")
            return report
            
        except Exception as e:
            logger.error(f"Data quality validation failed: {str(e)}")
            return DataQualityReport(
                total_chunks=0,
                high_quality_chunks=0,
                medium_quality_chunks=0,
                low_quality_chunks=0,
                avg_chunk_size=0.0,
                avg_quality_score=0.0,
                sanskrit_terms_coverage=0.0,
                verse_reference_coverage=0.0,
                issues=[f"Validation failed: {str(e)}"],
                recommendations=["Check system configuration and connectivity"]
            )
    
    def generate_progress_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive progress report.
        
        Returns:
            Detailed progress report
        """
        if not self.last_progress_update:
            return {"error": "No progress data available"}
        
        progress = self.last_progress_update
        
        # Calculate performance metrics
        duration = progress.get("duration_seconds", 0)
        loaded_chunks = progress["loaded_chunks"]
        
        chunks_per_second = loaded_chunks / duration if duration > 0 else 0
        
        # Estimate completion time
        remaining_chunks = progress["total_chunks"] - progress["loaded_chunks"]
        estimated_completion = remaining_chunks / chunks_per_second if chunks_per_second > 0 else None
        
        report = {
            "current_status": {
                "progress_percentage": progress["progress_percentage"],
                "loaded_chunks": loaded_chunks,
                "total_chunks": progress["total_chunks"],
                "failed_chunks": progress["failed_chunks"],
                "success_rate": progress["success_rate"],
                "is_complete": progress["is_complete"]
            },
            "performance_metrics": {
                "duration_seconds": duration,
                "chunks_per_second": chunks_per_second,
                "estimated_completion_seconds": estimated_completion
            },
            "source_progress": {
                "processed_sources": progress["processed_sources"],
                "total_sources": progress["total_sources"],
                "current_source": progress.get("current_source")
            },
            "history_summary": {
                "updates_recorded": len(self.progress_history),
                "monitoring_duration": duration,
                "average_progress_rate": self._calculate_average_progress_rate()
            }
        }
        
        return report
    
    def _calculate_average_progress_rate(self) -> float:
        """Calculate average progress rate from history."""
        if len(self.progress_history) < 2:
            return 0.0
        
        # Get progress deltas
        deltas = []
        for i in range(1, len(self.progress_history)):
            prev = self.progress_history[i-1]
            curr = self.progress_history[i]
            
            prev_chunks = prev["loaded_chunks"]
            curr_chunks = curr["loaded_chunks"]
            
            if curr_chunks > prev_chunks:
                deltas.append(curr_chunks - prev_chunks)
        
        return sum(deltas) / len(deltas) if deltas else 0.0
    
    def save_progress_history(self, file_path: str) -> None:
        """
        Save progress history to file.
        
        Args:
            file_path: Path to save the progress history
        """
        try:
            history_data = {
                "monitoring_session": {
                    "start_time": self.progress_history[0]["timestamp"] if self.progress_history else None,
                    "end_time": self.progress_history[-1]["timestamp"] if self.progress_history else None,
                    "total_updates": len(self.progress_history)
                },
                "progress_history": self.progress_history,
                "final_report": self.generate_progress_report()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Progress history saved to: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save progress history: {str(e)}")


async def monitor_data_loading(loader: CosmosDataLoader, 
                             update_interval: int = 10,
                             save_history: bool = True) -> Dict[str, Any]:
    """
    Monitor a data loading operation with real-time feedback.
    
    Args:
        loader: CosmosDataLoader instance to monitor
        update_interval: Seconds between progress updates
        save_history: Whether to save progress history to file
        
    Returns:
        Final monitoring report
    """
    logger.info("Starting data loading monitoring session...")
    
    # Initialize monitor
    monitor = DataLoadingMonitor(loader)
    
    # Start monitoring in background
    monitoring_task = asyncio.create_task(
        monitor.start_monitoring(update_interval)
    )
    
    try:
        # Wait for monitoring to complete
        await monitoring_task
        
        # Generate final report
        final_report = monitor.generate_progress_report()
        
        # Validate data quality
        quality_report = await monitor.validate_data_quality()
        final_report["data_quality"] = asdict(quality_report)
        
        # Save history if requested
        if save_history:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = f"data_loading_history_{timestamp}.json"
            monitor.save_progress_history(history_file)
            final_report["history_file"] = history_file
        
        logger.info("Data loading monitoring session completed")
        return final_report
        
    except Exception as e:
        logger.error(f"Monitoring session failed: {str(e)}")
        monitor.stop_monitoring()
        return {"error": str(e)}


if __name__ == "__main__":
    # Example usage
    async def main():
        from cosmos_data_loader import CosmosDataLoader
        
        loader = CosmosDataLoader()
        
        # Start loading operation
        loading_task = asyncio.create_task(
            loader.load_all_sources(validate_first=True)
        )
        
        # Start monitoring
        monitoring_task = asyncio.create_task(
            monitor_data_loading(loader, update_interval=5)
        )
        
        # Wait for both to complete
        loading_results, monitoring_report = await asyncio.gather(
            loading_task, monitoring_task
        )
        
        print("\n" + "="*60)
        print("DATA LOADING MONITORING REPORT")
        print("="*60)
        print(json.dumps(monitoring_report, indent=2))
    
    asyncio.run(main())
