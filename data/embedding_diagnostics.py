#!/usr/bin/env python3
"""
Unified Embedding Diagnostics Tool
Consolidates functionality from:
- check_embeddings.py
- check_empty_content_embeddings.py  
- simple_embedding_check.py
- quick_embedding_check.py

Usage:
    python embedding_diagnostics.py --mode [status|empty|quick|full]
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

# Load environment variables
load_dotenv('../.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingDiagnostics:
    """Unified tool for embedding diagnostics and validation"""
    
    def __init__(self):
        self.client = None
        self.container = None
        self._initialize_cosmos()
    
    def _initialize_cosmos(self):
        """Initialize Cosmos DB connection"""
        try:
            # Try connection string first (more reliable)
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if connection_string:
                from azure.cosmos import CosmosClient
                self.client = CosmosClient.from_connection_string(connection_string)
                database = self.client.get_database_client('vimarsh-multi-personality')
                self.container = database.get_container_client('personality_vectors')
            else:
                # Fallback to endpoint/key
                endpoint = os.getenv('COSMOS_ENDPOINT')
                key = os.getenv('COSMOS_KEY')
                if endpoint and key:
                    from azure.cosmos import CosmosClient
                    self.client = CosmosClient(endpoint, key)
                    database = self.client.get_database_client('vimarsh-multi-personality')
                    self.container = database.get_container_client('personality-vectors')
                else:
                    # Try using CosmosManager from backend
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    from backend.core.cosmos_client import CosmosManager
                    cosmos_manager = CosmosManager()
                    self.container = cosmos_manager.get_container('personality-vectors')
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB: {e}")
            raise

    def check_embedding_status(self) -> Dict[str, Any]:
        """Check overall embedding status across personalities"""
        print("🔍 Analyzing embedding status:")
        print("=" * 80)
        
        # Query entries without embeddings
        query_no_embeddings = """
        SELECT c.personality, COUNT(1) as count
        FROM c 
        WHERE c.has_embedding = false OR IS_NULL(c.has_embedding) OR NOT IS_DEFINED(c.has_embedding)
        GROUP BY c.personality
        """
        
        no_embeddings = list(self.container.query_items(
            query=query_no_embeddings,
            enable_cross_partition_query=True
        ))
        
        # Query entries with embeddings
        query_with_embeddings = """
        SELECT c.personality, COUNT(1) as count
        FROM c 
        WHERE c.has_embedding = true
        GROUP BY c.personality
        """
        
        with_embeddings = list(self.container.query_items(
            query=query_with_embeddings,
            enable_cross_partition_query=True
        ))
        
        # Query total entries
        query_total = """
        SELECT c.personality, COUNT(1) as count
        FROM c 
        GROUP BY c.personality
        """
        
        total_entries = list(self.container.query_items(
            query=query_total,
            enable_cross_partition_query=True
        ))
        
        # Compile results
        results = {
            'total_entries': sum(item['count'] for item in total_entries),
            'with_embeddings': sum(item['count'] for item in with_embeddings),
            'without_embeddings': sum(item['count'] for item in no_embeddings),
            'by_personality': {
                'with_embeddings': {item['personality']: item['count'] for item in with_embeddings},
                'without_embeddings': {item['personality']: item['count'] for item in no_embeddings},
                'total': {item['personality']: item['count'] for item in total_entries}
            }
        }
        
        self._print_status_report(results)
        return results
    
    def check_empty_content_embeddings(self) -> Dict[str, Any]:
        """Check for entries with embeddings but empty/minimal content"""
        print("🔍 Checking for entries with embeddings but empty/minimal content...")
        print("=" * 70)
        
        # Query for entries with embeddings but problematic content
        problematic_query = """
        SELECT c.id, c.personality, c.content, c.has_embedding, c.title, c.source, c.keywords
        FROM c 
        WHERE c.has_embedding = true 
        AND (IS_NULL(c.content) OR c.content = "" OR LENGTH(c.content) < 20)
        """
        
        problematic_entries = list(self.container.query_items(
            query=problematic_query,
            enable_cross_partition_query=True
        ))
        
        print(f"📊 Found {len(problematic_entries)} entries with embeddings but problematic content")
        
        if len(problematic_entries) == 0:
            print("✅ All entries with embeddings have substantial content!")
        else:
            print("\n⚠️ Problematic entries:")
            for entry in problematic_entries[:10]:  # Show first 10
                content_preview = entry.get('content', 'None')[:50] + '...' if entry.get('content') else 'None'
                print(f"  • {entry['personality']}: {entry.get('title', 'No title')} - Content: '{content_preview}'")
            
            if len(problematic_entries) > 10:
                print(f"  ... and {len(problematic_entries) - 10} more")
        
        return {'problematic_entries': len(problematic_entries), 'entries': problematic_entries}
    
    def quick_check(self) -> Dict[str, Any]:
        """Quick embedding count check"""
        print("🚀 Quick embedding status check...")
        
        # Count queries
        queries = {
            'no_embeddings': """
                SELECT COUNT(1) as count FROM c 
                WHERE c.has_embedding = false OR IS_NULL(c.has_embedding) OR NOT IS_DEFINED(c.has_embedding)
            """,
            'with_embeddings': """
                SELECT COUNT(1) as count FROM c WHERE c.has_embedding = true
            """,
            'total': "SELECT COUNT(1) as count FROM c"
        }
        
        results = {}
        for key, query in queries.items():
            result = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            results[key] = result[0]['count'] if result else 0
        
        completion_rate = (results['with_embeddings'] / results['total'] * 100) if results['total'] > 0 else 0
        
        print(f"📊 Quick Status:")
        print(f"  Total entries: {results['total']}")
        print(f"  With embeddings: {results['with_embeddings']}")
        print(f"  Without embeddings: {results['no_embeddings']}")
        print(f"  Completion rate: {completion_rate:.1f}%")
        
        return results
    
    def full_analysis(self) -> Dict[str, Any]:
        """Comprehensive embedding analysis"""
        print("🔬 Running comprehensive embedding analysis...")
        print("=" * 80)
        
        # Combine all checks
        status_results = self.check_embedding_status()
        empty_results = self.check_empty_content_embeddings()
        
        # Additional analysis - embedding model distribution
        model_query = """
        SELECT c.embedding_model, COUNT(1) as count
        FROM c 
        WHERE c.has_embedding = true AND IS_DEFINED(c.embedding_model)
        GROUP BY c.embedding_model
        """
        
        model_distribution = list(self.container.query_items(
            query=model_query,
            enable_cross_partition_query=True
        ))
        
        # Content length analysis
        content_analysis_query = """
        SELECT c.personality, 
               AVG(LENGTH(c.content)) as avg_content_length,
               MIN(LENGTH(c.content)) as min_content_length,
               MAX(LENGTH(c.content)) as max_content_length,
               COUNT(1) as count
        FROM c 
        WHERE c.has_embedding = true AND IS_DEFINED(c.content)
        GROUP BY c.personality
        """
        
        content_analysis = list(self.container.query_items(
            query=content_analysis_query,
            enable_cross_partition_query=True
        ))
        
        full_results = {
            'embedding_status': status_results,
            'empty_content_analysis': empty_results,
            'embedding_models': {item['embedding_model']: item['count'] for item in model_distribution},
            'content_analysis': {item['personality']: {
                'avg_length': item['avg_content_length'],
                'min_length': item['min_content_length'],
                'max_length': item['max_content_length'],
                'count': item['count']
            } for item in content_analysis}
        }
        
        self._print_full_analysis(full_results)
        return full_results
    
    def _print_status_report(self, results: Dict[str, Any]):
        """Print formatted status report"""
        total = results['total_entries']
        with_emb = results['with_embeddings']
        without_emb = results['without_embeddings']
        completion_rate = (with_emb / total * 100) if total > 0 else 0
        
        print(f"\n📊 Overall Statistics:")
        print(f"  Total entries: {total:,}")
        print(f"  With embeddings: {with_emb:,} ({completion_rate:.1f}%)")
        print(f"  Without embeddings: {without_emb:,}")
        
        print(f"\n👥 By Personality:")
        for personality in results['by_personality']['total']:
            total_p = results['by_personality']['total'].get(personality, 0)
            with_p = results['by_personality']['with_embeddings'].get(personality, 0)
            without_p = results['by_personality']['without_embeddings'].get(personality, 0)
            rate_p = (with_p / total_p * 100) if total_p > 0 else 0
            
            status_icon = "✅" if rate_p == 100 else "⚠️" if rate_p > 80 else "❌"
            print(f"  {status_icon} {personality}: {with_p}/{total_p} ({rate_p:.1f}%)")
    
    def _print_full_analysis(self, results: Dict[str, Any]):
        """Print comprehensive analysis results"""
        print(f"\n🔬 Embedding Model Distribution:")
        for model, count in results['embedding_models'].items():
            print(f"  • {model}: {count:,} entries")
        
        print(f"\n📏 Content Length Analysis:")
        for personality, stats in results['content_analysis'].items():
            print(f"  • {personality}: avg={stats['avg_length']:.0f}, min={stats['min_length']}, max={stats['max_length']} chars")


def main():
    """Main entry point with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Unified Embedding Diagnostics Tool')
    parser.add_argument('--mode', choices=['status', 'empty', 'quick', 'full'], 
                       default='status', help='Diagnostic mode to run')
    parser.add_argument('--output', help='Output file for results (JSON format)')
    
    args = parser.parse_args()
    
    try:
        diagnostics = EmbeddingDiagnostics()
        
        if args.mode == 'status':
            results = diagnostics.check_embedding_status()
        elif args.mode == 'empty':
            results = diagnostics.check_empty_content_embeddings()
        elif args.mode == 'quick':
            results = diagnostics.quick_check()
        elif args.mode == 'full':
            results = diagnostics.full_analysis()
        
        # Save results if output file specified
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to {args.output}")
        
        print(f"\n✅ Embedding diagnostics completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Diagnostic failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
