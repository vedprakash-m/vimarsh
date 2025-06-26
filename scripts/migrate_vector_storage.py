"""
Vector Storage Migration Script
Task 8.7: Migrate local vector storage to Cosmos DB vector search

Script to migrate existing local vector storage data to Cosmos DB,
with validation and rollback capabilities.
"""

import asyncio
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from backend.rag import (
    VectorStorageMigration,
    LocalVectorStorage,
    CosmosVectorSearch,
    TextChunk,
    SpiritualTextChunk
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationController:
    """Controls the migration process with validation and reporting."""
    
    def __init__(self, 
                 local_storage_path: str = "data/vector_storage",
                 cosmos_endpoint: str = None,
                 cosmos_key: str = None,
                 backup_path: str = "data/migration_backup",
                 dry_run: bool = False):
        """
        Initialize migration controller.
        
        Args:
            local_storage_path: Path to local Faiss storage
            cosmos_endpoint: Cosmos DB endpoint URL
            cosmos_key: Cosmos DB access key
            backup_path: Path for migration backup files
            dry_run: If True, simulate migration without actual data transfer
        """
        self.local_storage_path = Path(local_storage_path)
        self.cosmos_endpoint = cosmos_endpoint
        self.cosmos_key = cosmos_key
        self.backup_path = Path(backup_path)
        self.dry_run = dry_run
        
        # Initialize migration utility
        self.migration = VectorStorageMigration(
            local_storage_path=str(self.local_storage_path),
            cosmos_endpoint=cosmos_endpoint,
            cosmos_key=cosmos_key,
            backup_path=str(self.backup_path)
        )
        
        logger.info(f"Migration controller initialized (dry_run: {dry_run})")
    
    async def run_full_migration(self, validation_sample_size: int = 10) -> Dict[str, Any]:
        """
        Run complete migration process with validation.
        
        Args:
            validation_sample_size: Number of chunks to validate after migration
            
        Returns:
            Migration report with statistics and validation results
        """
        start_time = datetime.now(timezone.utc)
        report = {
            "migration_id": f"migration_{int(start_time.timestamp())}",
            "start_time": start_time.isoformat(),
            "dry_run": self.dry_run,
            "status": "in_progress",
            "phases": {}
        }
        
        try:
            # Phase 1: Pre-migration validation
            logger.info("Phase 1: Pre-migration validation")
            validation_result = await self.migration.validate_migration_readiness()
            report["phases"]["pre_validation"] = validation_result
            
            if not validation_result["ready_for_migration"]:
                report["status"] = "failed"
                report["error"] = "Pre-migration validation failed"
                return report
            
            # Phase 2: Create backup
            logger.info("Phase 2: Creating backup")
            if not self.dry_run:
                backup_result = await self.migration.create_backup()
                report["phases"]["backup"] = backup_result
            else:
                report["phases"]["backup"] = {"status": "skipped", "reason": "dry_run"}
            
            # Phase 3: Data migration
            logger.info("Phase 3: Data migration")
            if not self.dry_run:
                migration_result = await self.migration.migrate_all_data()
                report["phases"]["migration"] = migration_result
                
                if not migration_result["success"]:
                    report["status"] = "failed"
                    report["error"] = migration_result.get("error", "Migration failed")
                    return report
            else:
                # Simulate migration statistics
                local_stats = await self._get_local_storage_stats()
                report["phases"]["migration"] = {
                    "status": "simulated",
                    "chunks_to_migrate": local_stats.get("total_chunks", 0),
                    "estimated_time_minutes": max(1, local_stats.get("total_chunks", 0) // 60)
                }
            
            # Phase 4: Post-migration validation
            logger.info("Phase 4: Post-migration validation")
            if not self.dry_run:
                post_validation = await self.migration.validate_migration_integrity(
                    sample_size=validation_sample_size
                )
                report["phases"]["post_validation"] = post_validation
            else:
                report["phases"]["post_validation"] = {"status": "skipped", "reason": "dry_run"}
            
            # Phase 5: Performance comparison
            logger.info("Phase 5: Performance comparison")
            if not self.dry_run:
                performance_result = await self._compare_storage_performance()
                report["phases"]["performance"] = performance_result
            else:
                report["phases"]["performance"] = {"status": "skipped", "reason": "dry_run"}
            
            report["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            report["status"] = "failed"
            report["error"] = str(e)
        
        finally:
            end_time = datetime.now(timezone.utc)
            report["end_time"] = end_time.isoformat()
            report["duration_minutes"] = (end_time - start_time).total_seconds() / 60
        
        return report
    
    async def validate_migration_only(self) -> Dict[str, Any]:
        """Run migration validation without actual data transfer."""
        logger.info("Running migration validation only")
        
        return await self.migration.validate_migration_readiness()
    
    async def create_backup_only(self) -> Dict[str, Any]:
        """Create backup of local storage without migration."""
        logger.info("Creating backup only")
        
        return await self.migration.create_backup()
    
    async def rollback_migration(self, backup_id: str = None) -> Dict[str, Any]:
        """
        Rollback migration using backup data.
        
        Args:
            backup_id: Specific backup to restore (if None, uses latest)
            
        Returns:
            Rollback result
        """
        logger.info(f"Rolling back migration (backup_id: {backup_id})")
        
        try:
            result = await self.migration.rollback_migration(backup_id=backup_id)
            return result
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_local_storage_stats(self) -> Dict[str, Any]:
        """Get statistics about local storage."""
        try:
            local_storage = LocalVectorStorage(storage_path=str(self.local_storage_path))
            local_storage.load_index()
            
            stats = {
                "total_chunks": len(local_storage.chunks),
                "storage_size_mb": self._get_directory_size(self.local_storage_path) / (1024 * 1024),
                "sources": list(set(chunk.source for chunk in local_storage.chunks.values())),
                "has_embeddings": any(chunk.embedding is not None for chunk in local_storage.chunks.values())
            }
            
            return stats
            
        except Exception as e:
            logger.warning(f"Could not get local storage stats: {str(e)}")
            return {"error": str(e)}
    
    async def _compare_storage_performance(self) -> Dict[str, Any]:
        """Compare performance between local and Cosmos DB storage."""
        try:
            # Create test query
            import numpy as np
            test_query = np.random.rand(768).astype(np.float32)
            
            # Test local storage performance
            local_storage = LocalVectorStorage(storage_path=str(self.local_storage_path))
            local_storage.load_index()
            
            start_time = datetime.now()
            local_results = local_storage.search(test_query, top_k=5)
            local_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Test Cosmos DB performance
            cosmos_storage = CosmosVectorSearch(
                endpoint=self.cosmos_endpoint,
                key=self.cosmos_key
            )
            
            start_time = datetime.now()
            cosmos_results = await cosmos_storage.vector_search(
                query_vector=test_query.tolist(),
                top_k=5
            )
            cosmos_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "local_search_time_ms": round(local_time, 2),
                "cosmos_search_time_ms": round(cosmos_time, 2),
                "local_results_count": len(local_results),
                "cosmos_results_count": len(cosmos_results),
                "performance_ratio": round(cosmos_time / local_time if local_time > 0 else 0, 2)
            }
            
        except Exception as e:
            logger.warning(f"Could not compare performance: {str(e)}")
            return {"error": str(e)}
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        return total_size
    
    async def generate_migration_report(self, report_data: Dict[str, Any]) -> str:
        """Generate human-readable migration report."""
        report_lines = [
            "=" * 60,
            "VIMARSH VECTOR STORAGE MIGRATION REPORT",
            "=" * 60,
            f"Migration ID: {report_data.get('migration_id', 'N/A')}",
            f"Status: {report_data.get('status', 'Unknown').upper()}",
            f"Start Time: {report_data.get('start_time', 'N/A')}",
            f"End Time: {report_data.get('end_time', 'N/A')}",
            f"Duration: {report_data.get('duration_minutes', 0):.2f} minutes",
            f"Dry Run: {'Yes' if report_data.get('dry_run') else 'No'}",
            ""
        ]
        
        # Add error information if failed
        if report_data.get('status') == 'failed':
            report_lines.extend([
                "ERROR DETAILS:",
                f"  {report_data.get('error', 'Unknown error')}",
                ""
            ])
        
        # Add phase details
        phases = report_data.get('phases', {})
        for phase_name, phase_data in phases.items():
            report_lines.extend([
                f"{phase_name.upper()} PHASE:",
                f"  Status: {phase_data.get('status', 'Unknown')}"
            ])
            
            # Add phase-specific details
            if phase_name == 'migration' and not report_data.get('dry_run'):
                chunks_migrated = phase_data.get('chunks_migrated', 0)
                migration_time = phase_data.get('migration_time_seconds', 0)
                report_lines.extend([
                    f"  Chunks Migrated: {chunks_migrated}",
                    f"  Migration Time: {migration_time:.2f} seconds",
                    f"  Throughput: {chunks_migrated / max(migration_time, 1):.2f} chunks/second"
                ])
            
            elif phase_name == 'post_validation':
                validation_score = phase_data.get('validation_score', 0)
                sample_size = phase_data.get('sample_size', 0)
                report_lines.extend([
                    f"  Validation Score: {validation_score:.2%}",
                    f"  Sample Size: {sample_size} chunks"
                ])
            
            elif phase_name == 'performance':
                local_time = phase_data.get('local_search_time_ms', 0)
                cosmos_time = phase_data.get('cosmos_search_time_ms', 0)
                ratio = phase_data.get('performance_ratio', 0)
                report_lines.extend([
                    f"  Local Search Time: {local_time:.2f} ms",
                    f"  Cosmos Search Time: {cosmos_time:.2f} ms",
                    f"  Performance Ratio: {ratio:.2f}x"
                ])
            
            report_lines.append("")
        
        # Add recommendations
        report_lines.extend([
            "RECOMMENDATIONS:",
        ])
        
        if report_data.get('status') == 'completed':
            report_lines.extend([
                "  ✅ Migration completed successfully",
                "  ✅ Update application configuration to use Cosmos DB storage",
                "  ✅ Monitor application performance after deployment",
                "  ✅ Consider removing local storage after validation period"
            ])
        elif report_data.get('status') == 'failed':
            report_lines.extend([
                "  ❌ Review error details and fix issues",
                "  ❌ Ensure Cosmos DB credentials and configuration are correct",
                "  ❌ Validate local storage data integrity",
                "  ❌ Consider running dry-run migration first"
            ])
        
        report_lines.extend([
            "",
            "=" * 60
        ])
        
        return "\\n".join(report_lines)


async def main():
    """Main CLI entry point for migration script."""
    parser = argparse.ArgumentParser(description="Vimarsh Vector Storage Migration Tool")
    
    parser.add_argument(
        '--cosmos-endpoint',
        help='Cosmos DB endpoint URL',
        default=None
    )
    
    parser.add_argument(
        '--cosmos-key',
        help='Cosmos DB access key',
        default=None
    )
    
    parser.add_argument(
        '--local-storage-path',
        help='Path to local vector storage',
        default='data/vector_storage'
    )
    
    parser.add_argument(
        '--backup-path',
        help='Path for migration backup files',
        default='data/migration_backup'
    )
    
    parser.add_argument(
        '--action',
        choices=['validate', 'backup', 'migrate', 'rollback'],
        default='migrate',
        help='Action to perform'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate migration without actual data transfer'
    )
    
    parser.add_argument(
        '--backup-id',
        help='Backup ID for rollback (use latest if not specified)',
        default=None
    )
    
    parser.add_argument(
        '--validation-sample-size',
        type=int,
        default=10,
        help='Number of chunks to validate after migration'
    )
    
    parser.add_argument(
        '--output-report',
        help='Path to save migration report',
        default=None
    )
    
    args = parser.parse_args()
    
    # Create migration controller
    controller = MigrationController(
        local_storage_path=args.local_storage_path,
        cosmos_endpoint=args.cosmos_endpoint,
        cosmos_key=args.cosmos_key,
        backup_path=args.backup_path,
        dry_run=args.dry_run
    )
    
    # Execute requested action
    try:
        if args.action == 'validate':
            result = await controller.validate_migration_only()
            print(json.dumps(result, indent=2))
            
        elif args.action == 'backup':
            result = await controller.create_backup_only()
            print(json.dumps(result, indent=2))
            
        elif args.action == 'migrate':
            result = await controller.run_full_migration(
                validation_sample_size=args.validation_sample_size
            )
            
            # Generate and display report
            report_text = await controller.generate_migration_report(result)
            print(report_text)
            
            # Save report if requested
            if args.output_report:
                with open(args.output_report, 'w') as f:
                    f.write(report_text)
                print(f"\\nReport saved to: {args.output_report}")
            
        elif args.action == 'rollback':
            result = await controller.rollback_migration(backup_id=args.backup_id)
            print(json.dumps(result, indent=2))
        
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
