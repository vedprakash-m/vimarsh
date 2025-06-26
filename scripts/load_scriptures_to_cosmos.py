#!/usr/bin/env python3
"""
Task 8.8: Load and chunk source texts into production Cosmos DB
Generates embeddings for clean scripture data and uploads to Azure Cosmos DB
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScriptureDataLoader:
    """Loads clean scripture data into production Cosmos DB with vector embeddings."""
    
    def __init__(self, base_dir: str):
        """Initialize the scripture data loader."""
        self.base_dir = Path(base_dir)
        self.sources_dir = self.base_dir / "data" / "sources"
        self.registry_file = self.sources_dir / "scriptures_registry.json"
        
        # Environment variables for production deployment
        self.cosmos_connection_string = os.getenv("COSMOS_DB_CONNECTION_STRING")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.cosmos_connection_string:
            logger.warning("COSMOS_DB_CONNECTION_STRING not found, will use local storage for testing")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found, will run in dry-run mode")
    
    def load_scripture_registry(self) -> Dict[str, Any]:
        """Load the scriptures registry."""
        if not self.registry_file.exists():
            raise FileNotFoundError(f"Scripture registry not found: {self.registry_file}")
        
        with open(self.registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        logger.info(f"✅ Loaded scripture registry with {len(registry['scriptures'])} scriptures")
        return registry
    
    def validate_clean_data(self, registry: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Validate that all scriptures have clean data files available."""
        validated_scriptures = {}
        
        for scripture_id, scripture_info in registry["scriptures"].items():
            if scripture_info.get("status") != "success":
                logger.warning(f"⚠️ Skipping {scripture_id}: status is {scripture_info.get('status')}")
                continue
            
            output_file = scripture_info.get("output_file")
            if not output_file or not Path(output_file).exists():
                logger.warning(f"⚠️ Skipping {scripture_id}: output file not found")
                continue
            
            validated_scriptures[scripture_id] = scripture_info
            logger.info(f"✅ Validated {scripture_id}: {scripture_info['chunks_created']} chunks ready")
        
        return validated_scriptures
    
    def count_total_chunks(self, scriptures: Dict[str, Dict[str, Any]]) -> int:
        """Count total chunks across all scriptures."""
        total = sum(scripture['chunks_created'] for scripture in scriptures.values())
        logger.info(f"📊 Total chunks to process: {total}")
        return total
    
    def load_scripture_chunks(self, scripture_id: str, scripture_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Load chunks from a scripture's JSONL file."""
        output_file = Path(scripture_info["output_file"])
        chunks = []
        
        with open(output_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        chunk = json.loads(line)
                        chunks.append(chunk)
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ Skipping invalid JSON on line {line_num} in {output_file}: {e}")
        
        logger.info(f"✅ Loaded {len(chunks)} chunks from {scripture_id}")
        return chunks
    
    def create_embeddings_integration(self):
        """Create the Cosmos DB integration instance."""
        # Import here to avoid issues if dependencies aren't available
        try:
            from scripts.cosmos_db_integration import VectorEmbeddingsManager
            
            if self.cosmos_connection_string and self.openai_api_key:
                manager = VectorEmbeddingsManager(
                    base_dir=str(self.base_dir),
                    openai_api_key=self.openai_api_key,
                    cosmos_connection_string=self.cosmos_connection_string
                )
                logger.info("✅ Created Cosmos DB embeddings manager")
            else:
                logger.info("🔄 Using dry-run mode (missing API keys or connection string)")
                manager = None
            
            return manager
            
        except ImportError as e:
            logger.error(f"❌ Failed to import embeddings manager: {e}")
            logger.info("🔄 Continuing in dry-run mode")
            return None
    
    def process_scripture_embeddings(self, manager, scripture_id: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process embeddings for a single scripture."""
        if not manager:
            logger.info(f"🔄 Dry run mode - would process {len(chunks)} chunks for {scripture_id}")
            return {
                "status": "dry_run",
                "processed": len(chunks),
                "uploaded": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            logger.info(f"🔄 Processing embeddings for {scripture_id} ({len(chunks)} chunks)")
            processed, uploaded = manager.process_scripture_embeddings(scripture_id)
            
            result = {
                "status": "success",
                "processed": processed,
                "uploaded": uploaded,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ {scripture_id}: {processed} processed, {uploaded} uploaded")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to process {scripture_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processed": 0,
                "uploaded": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def update_registry_with_results(self, registry: Dict[str, Any], results: Dict[str, Dict[str, Any]]):
        """Update the scripture registry with embedding results."""
        for scripture_id, result in results.items():
            if scripture_id in registry["scriptures"]:
                registry["scriptures"][scripture_id].update({
                    "embeddings_uploaded": result.get("uploaded", 0) > 0,
                    "embedding_upload_date": result.get("timestamp"),
                    "embedding_status": result.get("status")
                })
        
        registry["last_updated"] = datetime.now().isoformat()
        
        # Save updated registry
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Updated scripture registry with embedding results")
    
    def generate_summary_report(self, results: Dict[str, Dict[str, Any]], total_chunks: int) -> Dict[str, Any]:
        """Generate a comprehensive summary report."""
        successful = [r for r in results.values() if r.get("status") == "success"]
        failed = [r for r in results.values() if r.get("status") == "error"]
        
        total_processed = sum(r.get("processed", 0) for r in successful)
        total_uploaded = sum(r.get("uploaded", 0) for r in successful)
        
        report = {
            "task": "8.8 Load and chunk source texts into production Cosmos DB",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_scriptures": len(results),
                "successful_scriptures": len(successful),
                "failed_scriptures": len(failed),
                "total_chunks_available": total_chunks,
                "total_chunks_processed": total_processed,
                "total_chunks_uploaded": total_uploaded,
                "success_rate": f"{(len(successful) / len(results) * 100):.1f}%" if results else "0%",
                "upload_rate": f"{(total_uploaded / total_processed * 100):.1f}%" if total_processed > 0 else "0%"
            },
            "scripture_results": results,
            "next_steps": [
                "Validate vector search functionality in production",
                "Test scripture-level management capabilities",
                "Proceed to Task 8.9 (Microsoft Entra External ID authentication)"
            ]
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any]):
        """Save the task completion report."""
        report_file = self.base_dir / "task_8_8_completion_report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Task 8.8 completion report saved to: {report_file}")
        return report_file
    
    async def execute_task_8_8(self) -> Dict[str, Any]:
        """Execute the complete Task 8.8: Load and chunk source texts into production Cosmos DB."""
        logger.info("🚀 Starting Task 8.8: Load and chunk source texts into production Cosmos DB")
        
        try:
            # Step 1: Load and validate data
            registry = self.load_scripture_registry()
            validated_scriptures = self.validate_clean_data(registry)
            total_chunks = self.count_total_chunks(validated_scriptures)
            
            if not validated_scriptures:
                raise ValueError("No valid scriptures found for processing")
            
            # Step 2: Initialize embeddings manager
            manager = self.create_embeddings_integration()
            
            # Step 3: Process each scripture
            results = {}
            for scripture_id, scripture_info in validated_scriptures.items():
                chunks = self.load_scripture_chunks(scripture_id, scripture_info)
                result = self.process_scripture_embeddings(manager, scripture_id, chunks)
                results[scripture_id] = result
            
            # Step 4: Update registry and generate report
            self.update_registry_with_results(registry, results)
            report = self.generate_summary_report(results, total_chunks)
            report_file = self.save_report(report)
            
            # Step 5: Display results
            self.display_completion_summary(report)
            
            logger.info("✅ Task 8.8 completed successfully!")
            return report
            
        except Exception as e:
            logger.error(f"❌ Task 8.8 failed: {e}")
            raise
    
    def display_completion_summary(self, report: Dict[str, Any]):
        """Display a user-friendly completion summary."""
        summary = report["summary"]
        
        print("\n" + "="*70)
        print("📋 TASK 8.8 COMPLETION SUMMARY")
        print("="*70)
        print(f"Task: {report['task']}")
        print(f"Completed: {report['timestamp']}")
        print(f"\n📊 RESULTS:")
        print(f"  • Total Scriptures: {summary['total_scriptures']}")
        print(f"  • Successful: {summary['successful_scriptures']}")
        print(f"  • Failed: {summary['failed_scriptures']}")
        print(f"  • Success Rate: {summary['success_rate']}")
        print(f"\n📈 DATA PROCESSING:")
        print(f"  • Total Chunks Available: {summary['total_chunks_available']:,}")
        print(f"  • Chunks Processed: {summary['total_chunks_processed']:,}")
        print(f"  • Chunks Uploaded: {summary['total_chunks_uploaded']:,}")
        print(f"  • Upload Rate: {summary['upload_rate']}")
        
        print(f"\n📋 SCRIPTURE DETAILS:")
        for scripture_id, result in report["scripture_results"].items():
            status_icon = "✅" if result.get("status") == "success" else "❌" if result.get("status") == "error" else "🔄"
            print(f"  {status_icon} {scripture_id}: {result.get('processed', 0)} processed, {result.get('uploaded', 0)} uploaded")
        
        print(f"\n🎯 NEXT STEPS:")
        for i, step in enumerate(report["next_steps"], 1):
            print(f"  {i}. {step}")
        
        print("="*70)


def main():
    """Main execution function."""
    # Get base directory (project root)
    base_dir = Path(__file__).parent.parent
    
    # Create loader and execute task
    loader = ScriptureDataLoader(str(base_dir))
    
    # Run the async task
    try:
        report = asyncio.run(loader.execute_task_8_8())
        print(f"\n✅ Task 8.8 completed successfully!")
        print(f"📊 Report saved to: task_8_8_completion_report.json")
        return 0
    except Exception as e:
        print(f"\n❌ Task 8.8 failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
