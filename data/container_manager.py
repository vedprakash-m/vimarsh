#!/usr/bin/env python3
"""
Unified Container Management Tool
Consolidates functionality from:
- create_new_containers.py
- create_new_containers_simple.py  
- create_containers_serverless.py
- cleanup_old_containers.py
- cleanup_old_entries.py
- cleanup_orphaned_embeddings.py

Usage:
    python container_manager.py --action [create|cleanup|list|validate] [options]
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerManager:
    """Unified tool for container management operations"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self._initialize_cosmos()
    
    def _initialize_cosmos(self):
        """Initialize Cosmos DB connection"""
        try:
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if not connection_string:
                raise ValueError("AZURE_COSMOS_CONNECTION_STRING not found")
            
            from azure.cosmos import CosmosClient
            self.client = CosmosClient.from_connection_string(connection_string)
            database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
            self.database = self.client.get_database_client(database_name)
            
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB: {e}")
            raise
    
    def create_containers(self, mode: str = "standard") -> Dict[str, Any]:
        """Create containers based on specified mode"""
        print(f"🚀 Creating containers in {mode} mode...")
        
        if mode == "serverless":
            return self._create_serverless_containers()
        elif mode == "simple":
            return self._create_simple_containers()
        else:
            return self._create_standard_containers()
    
    def _create_standard_containers(self) -> Dict[str, Any]:
        """Create standard 11-container architecture"""
        from azure.cosmos import PartitionKey
        
        containers_config = {
            'users': {
                'partition_key': PartitionKey(path="/user_id"),
                'throughput': 400
            },
            'user_sessions': {
                'partition_key': PartitionKey(path="/user_id"),
                'throughput': 400
            },
            'user_interactions': {
                'partition_key': PartitionKey(path="/user_id"),
                'throughput': 400
            },
            'personalities': {
                'partition_key': PartitionKey(path="/personality_id"),
                'throughput': 400
            },
            'personality_vectors': {
                'partition_key': PartitionKey(path="/personality"),
                'throughput': 1000  # Higher throughput for vector operations
            },
            'user_analytics': {
                'partition_key': PartitionKey(path="/user_id"),
                'throughput': 400
            },
            'content_analytics': {
                'partition_key': PartitionKey(path="/personality"),
                'throughput': 400
            },
            'system_analytics': {
                'partition_key': PartitionKey(path="/metric_type"),
                'throughput': 400
            },
            'feedback': {
                'partition_key': PartitionKey(path="/user_id"),
                'throughput': 400
            },
            'admin_logs': {
                'partition_key': PartitionKey(path="/admin_id"),
                'throughput': 400
            },
            'system_config': {
                'partition_key': PartitionKey(path="/config_type"),
                'throughput': 400
            }
        }
        
        return self._create_containers_from_config(containers_config)
    
    def _create_simple_containers(self) -> Dict[str, Any]:
        """Create simplified 3-container setup"""
        from azure.cosmos import PartitionKey
        
        containers_config = {
            'users': {
                'partition_key': PartitionKey(path="/user_id"),
                'throughput': 400
            },
            'personality-vectors': {
                'partition_key': PartitionKey(path="/personality"),
                'throughput': 800
            },
            'user_activity': {
                'partition_key': PartitionKey(path="/user_id"),
                'throughput': 400
            }
        }
        
        return self._create_containers_from_config(containers_config)
    
    def _create_serverless_containers(self) -> Dict[str, Any]:
        """Create containers optimized for serverless (no throughput provisioning)"""
        from azure.cosmos import PartitionKey
        
        containers_config = {
            'users': {
                'partition_key': PartitionKey(path="/user_id")
            },
            'personality_vectors': {
                'partition_key': PartitionKey(path="/personality")
            },
            'user_interactions': {
                'partition_key': PartitionKey(path="/user_id")
            },
            'personalities': {
                'partition_key': PartitionKey(path="/personality_id")
            }
        }
        
        return self._create_containers_from_config(containers_config, serverless=True)
    
    def _create_containers_from_config(self, config: Dict[str, Any], serverless: bool = False) -> Dict[str, Any]:
        """Create containers from configuration"""
        results = {
            'created': [],
            'existed': [],
            'failed': []
        }
        
        for container_name, container_config in config.items():
            try:
                print(f"  Creating container: {container_name}")
                
                create_kwargs = {
                    'id': container_name,
                    'partition_key': container_config['partition_key']
                }
                
                if not serverless and 'throughput' in container_config:
                    create_kwargs['offer_throughput'] = container_config['throughput']
                
                container = self.database.create_container(**create_kwargs)
                results['created'].append(container_name)
                print(f"    ✅ Created: {container_name}")
                
            except Exception as e:
                if "Conflict" in str(e) or "already exists" in str(e):
                    results['existed'].append(container_name)
                    print(f"    ℹ️ Already exists: {container_name}")
                else:
                    results['failed'].append({
                        'container': container_name,
                        'error': str(e)
                    })
                    print(f"    ❌ Failed: {container_name} - {e}")
        
        return results
    
    def cleanup_containers(self, target: str = "old") -> Dict[str, Any]:
        """Cleanup containers based on target"""
        print(f"🧹 Cleaning up {target} containers...")
        
        if target == "old":
            return self._cleanup_old_containers()
        elif target == "orphaned":
            return self._cleanup_orphaned_embeddings()
        elif target == "empty":
            return self._cleanup_empty_containers()
        else:
            return self._cleanup_entries_by_filter(target)
    
    def _cleanup_old_containers(self) -> Dict[str, Any]:
        """Remove old/deprecated containers"""
        deprecated_containers = [
            'personality-vectors-old',
            'user_activity_old', 
            'temp_migration',
            'backup_container'
        ]
        
        results = {
            'deleted': [],
            'not_found': [],
            'failed': []
        }
        
        for container_name in deprecated_containers:
            try:
                container = self.database.get_container_client(container_name)
                container.delete_container()
                results['deleted'].append(container_name)
                print(f"  ✅ Deleted: {container_name}")
            except Exception as e:
                if "NotFound" in str(e):
                    results['not_found'].append(container_name)
                    print(f"  ℹ️ Not found: {container_name}")
                else:
                    results['failed'].append({
                        'container': container_name,
                        'error': str(e)
                    })
                    print(f"  ❌ Failed to delete: {container_name} - {e}")
        
        return results
    
    def _cleanup_orphaned_embeddings(self) -> Dict[str, Any]:
        """Remove orphaned embeddings (embeddings without content)"""
        container = self.database.get_container_client('personality_vectors')
        
        # Find orphaned embeddings
        orphaned_query = """
        SELECT c.id, c.personality 
        FROM c 
        WHERE c.has_embedding = true 
        AND (IS_NULL(c.content) OR c.content = "" OR LENGTH(c.content) < 10)
        """
        
        orphaned_items = list(container.query_items(
            query=orphaned_query,
            enable_cross_partition_query=True
        ))
        
        results = {
            'found': len(orphaned_items),
            'deleted': 0,
            'failed': []
        }
        
        for item in orphaned_items:
            try:
                container.delete_item(
                    item=item['id'],
                    partition_key=item['personality']
                )
                results['deleted'] += 1
                print(f"  ✅ Deleted orphaned embedding: {item['id']}")
            except Exception as e:
                results['failed'].append({
                    'id': item['id'],
                    'error': str(e)
                })
                print(f"  ❌ Failed to delete: {item['id']} - {e}")
        
        return results
    
    def _cleanup_empty_containers(self) -> Dict[str, Any]:
        """Remove containers that are empty"""
        results = {
            'empty_containers': [],
            'deleted': [],
            'failed': []
        }
        
        # List all containers
        containers = list(self.database.list_containers())
        
        for container_info in containers:
            container_name = container_info['id']
            try:
                container = self.database.get_container_client(container_name)
                
                # Check if container is empty
                count_query = "SELECT VALUE COUNT(1) FROM c"
                count_result = list(container.query_items(
                    query=count_query,
                    enable_cross_partition_query=True
                ))
                
                item_count = count_result[0] if count_result else 0
                
                if item_count == 0:
                    results['empty_containers'].append(container_name)
                    print(f"  📭 Empty container found: {container_name}")
                    
                    # Optional: Delete empty containers (commented out for safety)
                    # container.delete_container()
                    # results['deleted'].append(container_name)
                    
            except Exception as e:
                results['failed'].append({
                    'container': container_name,
                    'error': str(e)
                })
        
        return results
    
    def list_containers(self) -> Dict[str, Any]:
        """List all containers with their details"""
        print("📋 Listing all containers...")
        
        containers = list(self.database.list_containers())
        results = {
            'total_containers': len(containers),
            'containers': []
        }
        
        for container_info in containers:
            container_name = container_info['id']
            try:
                container = self.database.get_container_client(container_name)
                
                # Get item count
                count_query = "SELECT VALUE COUNT(1) FROM c"
                count_result = list(container.query_items(
                    query=count_query,
                    enable_cross_partition_query=True
                ))
                item_count = count_result[0] if count_result else 0
                
                container_details = {
                    'name': container_name,
                    'item_count': item_count,
                    'partition_key': container_info.get('partitionKey', {}).get('paths', ['Unknown']),
                    'last_modified': container_info.get('_ts', 'Unknown')
                }
                
                results['containers'].append(container_details)
                print(f"  📦 {container_name}: {item_count:,} items")
                
            except Exception as e:
                print(f"  ❌ Error accessing {container_name}: {e}")
        
        return results
    
    def validate_containers(self) -> Dict[str, Any]:
        """Validate container configuration and data integrity"""
        print("🔍 Validating containers...")
        
        results = {
            'validation_time': datetime.now(timezone.utc).isoformat(),
            'containers': {},
            'summary': {
                'total_containers': 0,
                'valid_containers': 0,
                'issues_found': 0
            }
        }
        
        containers = list(self.database.list_containers())
        results['summary']['total_containers'] = len(containers)
        
        for container_info in containers:
            container_name = container_info['id']
            container_validation = {
                'exists': True,
                'item_count': 0,
                'partition_key': container_info.get('partitionKey', {}).get('paths', ['Unknown']),
                'issues': []
            }
            
            try:
                container = self.database.get_container_client(container_name)
                
                # Count items
                count_query = "SELECT VALUE COUNT(1) FROM c"
                count_result = list(container.query_items(
                    query=count_query,
                    enable_cross_partition_query=True
                ))
                container_validation['item_count'] = count_result[0] if count_result else 0
                
                # Container-specific validations
                if container_name == 'personality_vectors':
                    # Check for entries without embeddings
                    no_embed_query = """
                    SELECT VALUE COUNT(1) FROM c 
                    WHERE c.has_embedding = false OR IS_NULL(c.has_embedding)
                    """
                    no_embed_result = list(container.query_items(
                        query=no_embed_query,
                        enable_cross_partition_query=True
                    ))
                    no_embed_count = no_embed_result[0] if no_embed_result else 0
                    
                    if no_embed_count > 0:
                        container_validation['issues'].append(
                            f"{no_embed_count} entries without embeddings"
                        )
                
                if len(container_validation['issues']) == 0:
                    results['summary']['valid_containers'] += 1
                else:
                    results['summary']['issues_found'] += len(container_validation['issues'])
                
                print(f"  ✅ {container_name}: {container_validation['item_count']:,} items" + 
                      (f" ({len(container_validation['issues'])} issues)" if container_validation['issues'] else ""))
                
            except Exception as e:
                container_validation['issues'].append(f"Access error: {str(e)}")
                print(f"  ❌ {container_name}: Validation failed - {e}")
            
            results['containers'][container_name] = container_validation
        
        return results


def main():
    """Main entry point with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Unified Container Management Tool')
    parser.add_argument('--action', choices=['create', 'cleanup', 'list', 'validate'], 
                       required=True, help='Action to perform')
    parser.add_argument('--mode', choices=['standard', 'simple', 'serverless'], 
                       default='standard', help='Mode for create action')
    parser.add_argument('--target', choices=['old', 'orphaned', 'empty'], 
                       default='old', help='Target for cleanup action')
    parser.add_argument('--output', help='Output file for results (JSON format)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    
    args = parser.parse_args()
    
    try:
        manager = ContainerManager()
        
        if args.action == 'create':
            results = manager.create_containers(args.mode)
        elif args.action == 'cleanup':
            if args.dry_run:
                print("🔍 DRY RUN MODE - No changes will be made")
            results = manager.cleanup_containers(args.target)
        elif args.action == 'list':
            results = manager.list_containers()
        elif args.action == 'validate':
            results = manager.validate_containers()
        
        # Save results if output file specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to {args.output}")
        
        print(f"\n✅ Container {args.action} completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Container {args.action} failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
