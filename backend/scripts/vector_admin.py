#!/usr/bin/env python3
"""
Vector Database Admin Interface

Simple command-line interface for managing the multi-personality vector database.
Provides easy access to common administrative functions without needing to call
API endpoints directly.

FEATURES:
- View database statistics by personality
- Search and test vector similarity
- Manage content (add, remove, update)
- Health checks and diagnostics
- Database backup and restore
- Performance monitoring

USAGE:
    python scripts/vector_admin.py [command] [options]

COMMANDS:
    stats     - Show database statistics
    search    - Test vector search functionality  
    health    - Run health check diagnostics
    backup    - Create database backup
    migrate   - Run database migration
    add       - Add new content to personality
    remove    - Remove content from personality
    
EXAMPLES:
    python scripts/vector_admin.py stats --personality krishna
    python scripts/vector_admin.py search "dharma and duty" --personality krishna
    python scripts/vector_admin.py health --verbose
    python scripts/vector_admin.py backup --name manual_backup_2024
"""

import asyncio
import logging
import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.vector_database_service import VectorDatabaseService
    from services.rag_integration_service import RAGIntegrationService
    from admin.vector_database_admin import VectorDatabaseAdmin
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the backend directory and all dependencies are installed")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VectorDatabaseCLI:
    """Command-line interface for vector database administration"""
    
    def __init__(self):
        self.vector_service = None
        self.rag_service = None
        self.admin_service = None
        
    async def initialize(self):
        """Initialize all required services"""
        logger.info("🔧 Initializing admin services...")
        
        try:
            self.vector_service = VectorDatabaseService()
            await self.vector_service.initialize()
            logger.info("✅ Vector database service initialized")
            
            self.rag_service = RAGIntegrationService()
            logger.info("✅ RAG integration service initialized")
            
            self.admin_service = VectorDatabaseAdmin(self.vector_service)
            logger.info("✅ Admin service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {e}")
            raise
    
    async def show_stats(self, personality: Optional[str] = None, verbose: bool = False):
        """Show database statistics"""
        logger.info("📊 Retrieving database statistics...")
        
        try:
            if personality:
                # Show stats for specific personality
                stats = await self.vector_service.get_personality_stats(personality)
                
                print(f"\\n{'='*50}")
                print(f"📊 STATISTICS FOR {personality.upper()}")
                print(f"{'='*50}")
                print(f"📄 Total chunks: {stats['total_chunks']}")
                print(f"🧠 Total embeddings: {stats['total_embeddings']}")
                print(f"📚 Total sources: {stats['total_sources']}")
                print(f"💾 Storage size: {stats.get('storage_size_mb', 'N/A')} MB")
                print(f"⏱️ Last updated: {stats.get('last_updated', 'N/A')}")
                
                if verbose and 'sources' in stats:
                    print(f"\\n📚 Sources:")
                    for source in stats['sources']:
                        print(f"  - {source}")
                        
            else:
                # Show overall stats
                overall_stats = await self.admin_service.get_database_statistics()
                
                print(f"\\n{'='*60}")
                print(f"📊 VECTOR DATABASE OVERVIEW")
                print(f"{'='*60}")
                print(f"👥 Total personalities: {overall_stats['total_personalities']}")
                print(f"📄 Total chunks: {overall_stats['total_chunks']}")
                print(f"🧠 Total embeddings: {overall_stats['total_embeddings']}")
                print(f"💾 Total storage: {overall_stats.get('total_storage_mb', 'N/A')} MB")
                print(f"⚡ System health: {overall_stats.get('health_status', 'Unknown')}")
                
                print(f"\\n📈 BY PERSONALITY:")
                for personality_id, stats in overall_stats.get('personality_breakdown', {}).items():
                    print(f"  {personality_id:15} - {stats['chunks']:,} chunks, {stats['embeddings']:,} embeddings")
                    
        except Exception as e:
            logger.error(f"❌ Failed to retrieve statistics: {e}")
            return False
        
        return True
    
    async def test_search(self, query: str, personality: str = "krishna", limit: int = 5):
        """Test vector search functionality"""
        logger.info(f"🔍 Testing search for: '{query}' (personality: {personality})")
        
        try:
            # Test both vector service and RAG service
            print(f"\\n{'='*60}")
            print(f"🔍 SEARCH TEST: '{query}'")
            print(f"👤 Personality: {personality}")
            print(f"{'='*60}")
            
            # Test vector database search
            print(f"\\n🔍 Vector Database Search:")
            vector_results = await self.vector_service.search_content(
                personality_id=personality,
                query=query,
                limit=limit
            )
            
            if vector_results:
                for i, result in enumerate(vector_results, 1):
                    score = result.get('similarity_score', 0.0)
                    content = result.get('content', '')[:100] + "..."
                    source = result.get('source', 'Unknown')
                    
                    print(f"  {i}. Score: {score:.3f} | Source: {source}")
                    print(f"     Content: {content}")
                    print()
            else:
                print("  No results found")
            
            # Test RAG integration
            print(f"\\n🧠 RAG Integration Test:")
            rag_response = await self.rag_service.generate_enhanced_response(
                query=query,
                personality=personality
            )
            
            if rag_response:
                print(f"  ✅ Response generated: {len(rag_response.get('response', ''))} chars")
                print(f"  📚 Context chunks used: {len(rag_response.get('context_chunks', []))}")
                print(f"  🔗 Citations: {len(rag_response.get('citations', []))}")
                print(f"  🎯 Confidence: {rag_response.get('confidence', 0.0):.3f}")
                
                if rag_response.get('response'):
                    print(f"\\n📝 Sample Response:")
                    print(f"  {rag_response['response'][:200]}...")
            else:
                print("  ❌ RAG integration failed")
                
        except Exception as e:
            logger.error(f"❌ Search test failed: {e}")
            return False
            
        return True
    
    async def run_health_check(self, verbose: bool = False):
        """Run comprehensive health check"""
        logger.info("🏥 Running health check diagnostics...")
        
        try:
            health_results = await self.admin_service.perform_health_check()
            
            print(f"\\n{'='*50}")
            print(f"🏥 HEALTH CHECK RESULTS")
            print(f"{'='*50}")
            
            overall_status = health_results.get('status', 'unknown')
            status_emoji = "✅" if overall_status == "healthy" else "❌"
            print(f"{status_emoji} Overall Status: {overall_status.upper()}")
            
            # Show component health
            components = health_results.get('components', {})
            for component, status in components.items():
                component_emoji = "✅" if status == "healthy" else "❌"
                print(f"  {component_emoji} {component}: {status}")
            
            # Show performance metrics
            if 'performance' in health_results:
                perf = health_results['performance']
                print(f"\\n⚡ Performance Metrics:")
                print(f"  🔍 Avg search time: {perf.get('avg_search_time_ms', 'N/A')} ms")
                print(f"  🧠 Avg embedding time: {perf.get('avg_embedding_time_ms', 'N/A')} ms")
                print(f"  💾 Memory usage: {perf.get('memory_usage_mb', 'N/A')} MB")
            
            # Show issues if any
            issues = health_results.get('issues', [])
            if issues:
                print(f"\\n⚠️ Issues Found:")
                for issue in issues:
                    print(f"  - {issue}")
            
            # Verbose details
            if verbose and 'details' in health_results:
                print(f"\\n🔍 Detailed Information:")
                details = health_results['details']
                for key, value in details.items():
                    print(f"  {key}: {value}")
                    
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
            
        return True
    
    async def create_backup(self, name: Optional[str] = None):
        """Create database backup"""
        backup_name = name or f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"📦 Creating backup: {backup_name}")
        
        try:
            result = await self.admin_service.create_backup(backup_name)
            
            if result.get('success'):
                print(f"\\n✅ Backup created successfully:")
                print(f"  📦 Name: {backup_name}")
                print(f"  📄 Documents: {result.get('documents_backed_up', 'N/A')}")
                print(f"  💾 Size: {result.get('backup_size_mb', 'N/A')} MB")
                print(f"  📁 Location: {result.get('backup_path', 'N/A')}")
            else:
                print(f"❌ Backup failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return False
            
        return True
    
    async def add_content(self, personality: str, content: str, source: str = "", title: str = ""):
        """Add new content to personality"""
        logger.info(f"➕ Adding content to {personality}: '{title or content[:50]}...'")
        
        try:
            result = await self.vector_service.add_content(
                personality_id=personality,
                content=content,
                source=source,
                title=title,
                metadata={
                    'added_via': 'admin_cli',
                    'added_at': datetime.now().isoformat()
                }
            )
            
            if result:
                print(f"\\n✅ Content added successfully:")
                print(f"  👤 Personality: {personality}")
                print(f"  📄 Chunks created: {result.get('chunks_created', 'N/A')}")
                print(f"  🧠 Embeddings generated: {result.get('embeddings_generated', 'N/A')}")
                print(f"  🆔 Content ID: {result.get('content_id', 'N/A')}")
            else:
                print(f"❌ Failed to add content")
                return False
                
        except Exception as e:
            logger.error(f"❌ Content addition failed: {e}")
            return False
            
        return True

async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Vector Database Admin Interface")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    stats_parser.add_argument('--personality', type=str, help='Show stats for specific personality')
    stats_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Test vector search')
    search_parser.add_argument('query', type=str, help='Search query')
    search_parser.add_argument('--personality', type=str, default='krishna', help='Personality to search')
    search_parser.add_argument('--limit', type=int, default=5, help='Number of results')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Run health check')
    health_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed health info')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create database backup')
    backup_parser.add_argument('--name', type=str, help='Backup name')
    
    # Add content command
    add_parser = subparsers.add_parser('add', help='Add content to personality')
    add_parser.add_argument('personality', type=str, help='Personality ID')
    add_parser.add_argument('content', type=str, help='Content to add')
    add_parser.add_argument('--source', type=str, default='', help='Content source')
    add_parser.add_argument('--title', type=str, default='', help='Content title')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize CLI
    cli = VectorDatabaseCLI()
    
    try:
        await cli.initialize()
        
        # Execute command
        success = False
        
        if args.command == 'stats':
            success = await cli.show_stats(args.personality, args.verbose)
            
        elif args.command == 'search':
            success = await cli.test_search(args.query, args.personality, args.limit)
            
        elif args.command == 'health':
            success = await cli.run_health_check(args.verbose)
            
        elif args.command == 'backup':
            success = await cli.create_backup(args.name)
            
        elif args.command == 'add':
            success = await cli.add_content(args.personality, args.content, args.source, args.title)
            
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"💥 CLI operation failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
