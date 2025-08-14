#!/usr/bin/env python3
"""
Unified Data Diagnostics Tool
Consolidates functionality from multiple test, check, debug, and analysis scripts:
- simple_*.py, quick_*.py, test_*.py scripts
- analyze_*.py scripts
- debug_*.py scripts

Usage:
    python data_diagnostics.py --check [embedding|container|data|content|all] [options]
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

class DataDiagnostics:
    """Unified tool for comprehensive data diagnostics"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.containers = {}
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
            
            # Cache container references
            self._load_containers()
            
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB: {e}")
            raise
    
    def _load_containers(self):
        """Load and cache container references"""
        try:
            container_names = ['personality_vectors', 'personality-vectors', 'users', 'user_activity', 'user_interactions']
            for name in container_names:
                try:
                    self.containers[name] = self.database.get_container_client(name)
                except:
                    pass  # Container may not exist
        except Exception as e:
            logger.warning(f"Some containers not accessible: {e}")
    
    def check_embeddings(self, detailed: bool = False) -> Dict[str, Any]:
        """Comprehensive embedding diagnostics"""
        print("🔍 Checking embedding status...")
        
        # Try both container names
        container = self.containers.get('personality_vectors') or self.containers.get('personality-vectors')
        if not container:
            return {'error': 'No personality vectors container found'}
        
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'container_name': 'personality_vectors',
            'summary': {},
            'by_personality': {},
            'issues': []
        }
        
        try:
            # Overall counts
            total_query = "SELECT VALUE COUNT(1) FROM c"
            total_count = list(container.query_items(query=total_query, enable_cross_partition_query=True))[0]
            
            with_embeddings_query = "SELECT VALUE COUNT(1) FROM c WHERE c.has_embedding = true"
            with_embeddings_count = list(container.query_items(query=with_embeddings_query, enable_cross_partition_query=True))[0]
            
            without_embeddings_count = total_count - with_embeddings_count
            completion_rate = (with_embeddings_count / total_count * 100) if total_count > 0 else 0
            
            results['summary'] = {
                'total_entries': total_count,
                'with_embeddings': with_embeddings_count,
                'without_embeddings': without_embeddings_count,
                'completion_rate': completion_rate
            }
            
            # By personality analysis
            personality_query = """
            SELECT c.personality, 
                   COUNT(1) as total,
                   SUM(c.has_embedding = true ? 1 : 0) as with_embeddings
            FROM c 
            GROUP BY c.personality
            """
            
            personality_stats = list(container.query_items(query=personality_query, enable_cross_partition_query=True))
            
            for stat in personality_stats:
                personality = stat['personality']
                total = stat['total']
                with_emb = stat['with_embeddings']
                rate = (with_emb / total * 100) if total > 0 else 0
                
                results['by_personality'][personality] = {
                    'total': total,
                    'with_embeddings': with_emb,
                    'without_embeddings': total - with_emb,
                    'completion_rate': rate
                }
            
            # Detailed analysis if requested
            if detailed:
                results['detailed_analysis'] = self._detailed_embedding_analysis(container)
            
            # Check for common issues
            results['issues'] = self._check_embedding_issues(container)
            
            self._print_embedding_report(results)
            
        except Exception as e:
            results['error'] = str(e)
            logger.error(f"Embedding check failed: {e}")
        
        return results
    
    def _detailed_embedding_analysis(self, container) -> Dict[str, Any]:
        """Detailed embedding analysis"""
        analysis = {}
        
        try:
            # Embedding model distribution
            model_query = """
            SELECT c.embedding_model, COUNT(1) as count
            FROM c 
            WHERE IS_DEFINED(c.embedding_model)
            GROUP BY c.embedding_model
            """
            model_stats = list(container.query_items(query=model_query, enable_cross_partition_query=True))
            analysis['embedding_models'] = {stat['embedding_model']: stat['count'] for stat in model_stats}
            
            # Content length analysis
            length_query = """
            SELECT c.personality,
                   AVG(LENGTH(c.content)) as avg_length,
                   MIN(LENGTH(c.content)) as min_length,
                   MAX(LENGTH(c.content)) as max_length
            FROM c 
            WHERE IS_DEFINED(c.content) AND c.content != ""
            GROUP BY c.personality
            """
            length_stats = list(container.query_items(query=length_query, enable_cross_partition_query=True))
            analysis['content_lengths'] = {
                stat['personality']: {
                    'avg_length': stat['avg_length'],
                    'min_length': stat['min_length'], 
                    'max_length': stat['max_length']
                } for stat in length_stats
            }
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _check_embedding_issues(self, container) -> List[str]:
        """Check for common embedding issues"""
        issues = []
        
        try:
            # Empty content with embeddings
            empty_content_query = """
            SELECT VALUE COUNT(1) FROM c 
            WHERE c.has_embedding = true 
            AND (IS_NULL(c.content) OR c.content = "" OR LENGTH(c.content) < 20)
            """
            empty_content_count = list(container.query_items(query=empty_content_query, enable_cross_partition_query=True))[0]
            if empty_content_count > 0:
                issues.append(f"{empty_content_count} entries with embeddings but empty/minimal content")
            
            # Duplicate content
            duplicate_query = """
            SELECT c.content, COUNT(1) as count
            FROM c 
            WHERE IS_DEFINED(c.content) AND c.content != ""
            GROUP BY c.content
            HAVING COUNT(1) > 1
            """
            duplicate_stats = list(container.query_items(query=duplicate_query, enable_cross_partition_query=True))
            if duplicate_stats:
                total_duplicates = sum(stat['count'] for stat in duplicate_stats)
                issues.append(f"{len(duplicate_stats)} sets of duplicate content affecting {total_duplicates} entries")
            
        except Exception as e:
            issues.append(f"Error checking for issues: {str(e)}")
        
        return issues
    
    def check_containers(self) -> Dict[str, Any]:
        """Check container health and configuration"""
        print("🏗️ Checking container health...")
        
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'containers': {},
            'summary': {
                'total_containers': 0,
                'accessible_containers': 0,
                'total_items': 0
            }
        }
        
        try:
            # List all containers
            all_containers = list(self.database.list_containers())
            results['summary']['total_containers'] = len(all_containers)
            
            for container_info in all_containers:
                container_name = container_info['id']
                container_details = {
                    'exists': True,
                    'accessible': False,
                    'item_count': 0,
                    'partition_key': container_info.get('partitionKey', {}).get('paths', ['Unknown']),
                    'last_modified': container_info.get('_ts', 'Unknown'),
                    'issues': []
                }
                
                try:
                    container = self.database.get_container_client(container_name)
                    count_query = "SELECT VALUE COUNT(1) FROM c"
                    count_result = list(container.query_items(query=count_query, enable_cross_partition_query=True))
                    container_details['item_count'] = count_result[0] if count_result else 0
                    container_details['accessible'] = True
                    results['summary']['accessible_containers'] += 1
                    results['summary']['total_items'] += container_details['item_count']
                    
                except Exception as e:
                    container_details['issues'].append(f"Access error: {str(e)}")
                
                results['containers'][container_name] = container_details
            
            self._print_container_report(results)
            
        except Exception as e:
            results['error'] = str(e)
            logger.error(f"Container check failed: {e}")
        
        return results
    
    def check_data_integrity(self) -> Dict[str, Any]:
        """Check data integrity across containers"""
        print("🔒 Checking data integrity...")
        
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'integrity_checks': {},
            'issues': []
        }
        
        try:
            # Check personality vectors integrity
            if 'personality_vectors' in self.containers or 'personality-vectors' in self.containers:
                results['integrity_checks']['personality_vectors'] = self._check_personality_vectors_integrity()
            
            # Check user data integrity
            if 'users' in self.containers:
                results['integrity_checks']['users'] = self._check_user_data_integrity()
            
            # Check cross-container relationships
            results['integrity_checks']['relationships'] = self._check_cross_container_relationships()
            
            self._print_integrity_report(results)
            
        except Exception as e:
            results['error'] = str(e)
            logger.error(f"Data integrity check failed: {e}")
        
        return results
    
    def _check_personality_vectors_integrity(self) -> Dict[str, Any]:
        """Check personality vectors container integrity"""
        container = self.containers.get('personality_vectors') or self.containers.get('personality-vectors')
        if not container:
            return {'error': 'Container not accessible'}
        
        integrity = {
            'required_fields_check': True,
            'missing_fields': [],
            'data_quality_issues': []
        }
        
        try:
            # Check for required fields
            required_fields_query = """
            SELECT COUNT(1) as total,
                   SUM(IS_DEFINED(c.personality) ? 1 : 0) as has_personality,
                   SUM(IS_DEFINED(c.content) ? 1 : 0) as has_content,
                   SUM(IS_DEFINED(c.id) ? 1 : 0) as has_id
            FROM c
            """
            
            field_stats = list(container.query_items(query=required_fields_query, enable_cross_partition_query=True))[0]
            
            total = field_stats['total']
            if field_stats['has_personality'] != total:
                integrity['missing_fields'].append(f"{total - field_stats['has_personality']} entries missing personality")
            if field_stats['has_content'] != total:
                integrity['missing_fields'].append(f"{total - field_stats['has_content']} entries missing content")
            if field_stats['has_id'] != total:
                integrity['missing_fields'].append(f"{total - field_stats['has_id']} entries missing id")
            
            integrity['required_fields_check'] = len(integrity['missing_fields']) == 0
            
        except Exception as e:
            integrity['error'] = str(e)
        
        return integrity
    
    def _check_user_data_integrity(self) -> Dict[str, Any]:
        """Check user data integrity"""
        container = self.containers.get('users')
        if not container:
            return {'error': 'Users container not accessible'}
        
        integrity = {
            'user_count': 0,
            'valid_users': 0,
            'issues': []
        }
        
        try:
            # Count total users
            total_query = "SELECT VALUE COUNT(1) FROM c"
            integrity['user_count'] = list(container.query_items(query=total_query, enable_cross_partition_query=True))[0]
            
            # Check for required user fields
            valid_users_query = """
            SELECT VALUE COUNT(1) FROM c 
            WHERE IS_DEFINED(c.user_id) AND IS_DEFINED(c.created_at)
            """
            integrity['valid_users'] = list(container.query_items(query=valid_users_query, enable_cross_partition_query=True))[0]
            
            if integrity['valid_users'] != integrity['user_count']:
                integrity['issues'].append(f"{integrity['user_count'] - integrity['valid_users']} users missing required fields")
            
        except Exception as e:
            integrity['error'] = str(e)
        
        return integrity
    
    def _check_cross_container_relationships(self) -> Dict[str, Any]:
        """Check relationships between containers"""
        relationships = {
            'checks_performed': [],
            'issues': []
        }
        
        # This would contain logic to check referential integrity between containers
        # For now, just placeholder
        relationships['checks_performed'].append('Cross-container relationship checks not yet implemented')
        
        return relationships
    
    def check_content_quality(self) -> Dict[str, Any]:
        """Check content quality metrics"""
        print("📝 Checking content quality...")
        
        container = self.containers.get('personality_vectors') or self.containers.get('personality-vectors')
        if not container:
            return {'error': 'No personality vectors container found'}
        
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'quality_metrics': {},
            'recommendations': []
        }
        
        try:
            # Content length distribution
            length_distribution_query = """
            SELECT 
                COUNT(1) as total,
                AVG(LENGTH(c.content)) as avg_length,
                MIN(LENGTH(c.content)) as min_length,
                MAX(LENGTH(c.content)) as max_length
            FROM c 
            WHERE IS_DEFINED(c.content) AND c.content != ""
            """
            
            length_stats = list(container.query_items(query=length_distribution_query, enable_cross_partition_query=True))[0]
            results['quality_metrics']['content_length'] = length_stats
            
            # Check for very short content
            short_content_query = """
            SELECT VALUE COUNT(1) FROM c 
            WHERE IS_DEFINED(c.content) AND LENGTH(c.content) < 100
            """
            short_content_count = list(container.query_items(query=short_content_query, enable_cross_partition_query=True))[0]
            
            if short_content_count > 0:
                results['recommendations'].append(f"Consider reviewing {short_content_count} entries with very short content (<100 chars)")
            
            # Check for missing titles
            missing_title_query = """
            SELECT VALUE COUNT(1) FROM c 
            WHERE IS_NULL(c.title) OR c.title = ""
            """
            missing_title_count = list(container.query_items(query=missing_title_query, enable_cross_partition_query=True))[0]
            
            if missing_title_count > 0:
                results['recommendations'].append(f"Consider adding titles to {missing_title_count} entries")
            
            results['quality_metrics']['short_content_count'] = short_content_count
            results['quality_metrics']['missing_title_count'] = missing_title_count
            
            self._print_content_quality_report(results)
            
        except Exception as e:
            results['error'] = str(e)
            logger.error(f"Content quality check failed: {e}")
        
        return results
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics across all areas"""
        print("🔬 Running comprehensive data diagnostics...")
        print("=" * 80)
        
        all_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'diagnostics': {}
        }
        
        # Run all diagnostic checks
        checks = [
            ('embeddings', self.check_embeddings),
            ('containers', self.check_containers),
            ('data_integrity', self.check_data_integrity),
            ('content_quality', self.check_content_quality)
        ]
        
        for check_name, check_func in checks:
            try:
                print(f"\n--- {check_name.replace('_', ' ').title()} Check ---")
                all_results['diagnostics'][check_name] = check_func()
            except Exception as e:
                all_results['diagnostics'][check_name] = {'error': str(e)}
                print(f"❌ {check_name} check failed: {e}")
        
        # Generate summary
        all_results['summary'] = self._generate_overall_summary(all_results['diagnostics'])
        self._print_overall_summary(all_results['summary'])
        
        return all_results
    
    def _generate_overall_summary(self, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall summary of all diagnostics"""
        summary = {
            'total_checks': len(diagnostics),
            'successful_checks': 0,
            'failed_checks': 0,
            'total_issues': 0,
            'critical_issues': [],
            'recommendations': []
        }
        
        for check_name, results in diagnostics.items():
            if 'error' in results:
                summary['failed_checks'] += 1
            else:
                summary['successful_checks'] += 1
                
                # Extract issues from each check
                if 'issues' in results:
                    summary['total_issues'] += len(results['issues'])
                    summary['critical_issues'].extend(results['issues'])
                
                if 'recommendations' in results:
                    summary['recommendations'].extend(results['recommendations'])
        
        return summary
    
    def _print_embedding_report(self, results: Dict[str, Any]):
        """Print formatted embedding report"""
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            return
        
        summary = results['summary']
        print(f"\n📊 Embedding Summary:")
        print(f"  Total entries: {summary['total_entries']:,}")
        print(f"  With embeddings: {summary['with_embeddings']:,} ({summary['completion_rate']:.1f}%)")
        print(f"  Without embeddings: {summary['without_embeddings']:,}")
        
        if results['by_personality']:
            print(f"\n👥 By Personality:")
            for personality, stats in results['by_personality'].items():
                status = "✅" if stats['completion_rate'] == 100 else "⚠️" if stats['completion_rate'] > 80 else "❌"
                print(f"  {status} {personality}: {stats['with_embeddings']}/{stats['total']} ({stats['completion_rate']:.1f}%)")
        
        if results['issues']:
            print(f"\n⚠️ Issues Found:")
            for issue in results['issues']:
                print(f"  • {issue}")
    
    def _print_container_report(self, results: Dict[str, Any]):
        """Print formatted container report"""
        summary = results['summary']
        print(f"\n📦 Container Summary:")
        print(f"  Total containers: {summary['total_containers']}")
        print(f"  Accessible: {summary['accessible_containers']}")
        print(f"  Total items: {summary['total_items']:,}")
    
    def _print_integrity_report(self, results: Dict[str, Any]):
        """Print formatted integrity report"""
        print(f"\n🔒 Data Integrity Summary:")
        for check_name, check_results in results['integrity_checks'].items():
            if 'error' not in check_results:
                print(f"  ✅ {check_name}: Checks completed")
            else:
                print(f"  ❌ {check_name}: {check_results['error']}")
    
    def _print_content_quality_report(self, results: Dict[str, Any]):
        """Print formatted content quality report"""
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            return
        
        metrics = results['quality_metrics']
        print(f"\n📝 Content Quality Summary:")
        if 'content_length' in metrics:
            length = metrics['content_length']
            print(f"  Average content length: {length['avg_length']:.0f} characters")
            print(f"  Length range: {length['min_length']} - {length['max_length']} characters")
        
        if results['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in results['recommendations']:
                print(f"  • {rec}")
    
    def _print_overall_summary(self, summary: Dict[str, Any]):
        """Print overall diagnostic summary"""
        print(f"\n🎯 Overall Diagnostic Summary:")
        print(f"  Checks completed: {summary['successful_checks']}/{summary['total_checks']}")
        print(f"  Total issues found: {summary['total_issues']}")
        
        if summary['critical_issues']:
            print(f"\n🚨 Critical Issues:")
            for issue in summary['critical_issues'][:5]:  # Show top 5
                print(f"  • {issue}")
            if len(summary['critical_issues']) > 5:
                print(f"  ... and {len(summary['critical_issues']) - 5} more")


def main():
    """Main entry point with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Unified Data Diagnostics Tool')
    parser.add_argument('--check', choices=['embedding', 'container', 'data', 'content', 'all'], 
                       default='all', help='Type of diagnostic to run')
    parser.add_argument('--detailed', action='store_true', help='Run detailed analysis')
    parser.add_argument('--output', help='Output file for results (JSON format)')
    
    args = parser.parse_args()
    
    try:
        diagnostics = DataDiagnostics()
        
        if args.check == 'embedding':
            results = diagnostics.check_embeddings(detailed=args.detailed)
        elif args.check == 'container':
            results = diagnostics.check_containers()
        elif args.check == 'data':
            results = diagnostics.check_data_integrity()
        elif args.check == 'content':
            results = diagnostics.check_content_quality()
        elif args.check == 'all':
            results = diagnostics.run_all_checks()
        
        # Save results if output file specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to {args.output}")
        
        print(f"\n✅ Data diagnostics completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Diagnostics failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
