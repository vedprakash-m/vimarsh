#!/usr/bin/env python3
"""
Storage size analyzer for Cosmos DB containers.
Investigates storage size inconsistencies between source and destination containers.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import statistics

from azure.cosmos.aio import CosmosClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StorageSizeAnalyzer:
    """Analyze storage size differences between containers."""
    
    def __init__(self):
        self.cosmos_client = None
        self.db = None
        
    async def initialize_cosmos_connection(self):
        """Initialize Cosmos DB connection"""
        try:
            # Load environment variables from parent directory
            from dotenv import load_dotenv
            env_path = Path(__file__).parent.parent.parent / '.env'
            load_dotenv(env_path)
            
            # Try connection string first
            cosmos_connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING') or os.getenv('COSMOSDB_CONNECTION_STRING')
            
            if cosmos_connection_string:
                # Parse connection string to get endpoint and key
                import re
                endpoint_match = re.search(r'AccountEndpoint=([^;]+)', cosmos_connection_string)
                key_match = re.search(r'AccountKey=([^;]+)', cosmos_connection_string)
                
                if endpoint_match and key_match:
                    cosmos_endpoint = endpoint_match.group(1)
                    cosmos_key = key_match.group(1)
                else:
                    raise ValueError("Invalid connection string format")
            else:
                # Fallback to separate endpoint and key
                cosmos_endpoint = os.getenv('COSMOS_ENDPOINT')
                cosmos_key = os.getenv('COSMOS_KEY')
                
                if not cosmos_endpoint or not cosmos_key:
                    raise ValueError("COSMOS connection string or COSMOS_ENDPOINT and COSMOS_KEY environment variables are required")
            
            self.cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
            self.db = self.cosmos_client.get_database_client('vimarsh-multi-personality')
            logger.info("✅ Connected to Cosmos DB")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
            raise
            
    async def analyze_document_sizes(self, container_name: str, sample_size: int = 100) -> Dict[str, Any]:
        """Analyze document sizes in a container"""
        try:
            container = self.db.get_container_client(container_name)
            
            # Query all documents
            query = "SELECT * FROM c"
            items = container.query_items(query=query, enable_cross_partition_query=True)
            
            document_sizes = []
            total_documents = 0
            sample_documents = []
            
            async for item in items:
                total_documents += 1
                
                # Calculate document size in bytes (rough estimation)
                doc_json = json.dumps(item, ensure_ascii=False)
                doc_size = len(doc_json.encode('utf-8'))
                document_sizes.append(doc_size)
                
                # Collect sample documents for detailed analysis
                if len(sample_documents) < sample_size:
                    sample_documents.append({
                        'id': item.get('id', 'unknown'),
                        'size_bytes': doc_size,
                        'size_kb': doc_size / 1024,
                        'personality': item.get('personality', 'N/A'),
                        'type': item.get('type', 'N/A'),
                        'has_vector': 'vector' in item,
                        'vector_length': len(item.get('vector', [])) if 'vector' in item else 0,
                        'field_count': len(item.keys())
                    })
            
            # Calculate statistics
            if document_sizes:
                total_size_bytes = sum(document_sizes)
                avg_size_bytes = statistics.mean(document_sizes)
                median_size_bytes = statistics.median(document_sizes)
                min_size_bytes = min(document_sizes)
                max_size_bytes = max(document_sizes)
                std_dev_bytes = statistics.stdev(document_sizes) if len(document_sizes) > 1 else 0
            else:
                total_size_bytes = avg_size_bytes = median_size_bytes = min_size_bytes = max_size_bytes = std_dev_bytes = 0
            
            analysis = {
                'container_name': container_name,
                'total_documents': total_documents,
                'total_size_bytes': total_size_bytes,
                'total_size_mb': total_size_bytes / (1024 * 1024),
                'avg_size_bytes': avg_size_bytes,
                'avg_size_kb': avg_size_bytes / 1024,
                'median_size_bytes': median_size_bytes,
                'median_size_kb': median_size_bytes / 1024,
                'min_size_bytes': min_size_bytes,
                'min_size_kb': min_size_bytes / 1024,
                'max_size_bytes': max_size_bytes,
                'max_size_kb': max_size_bytes / 1024,
                'std_dev_bytes': std_dev_bytes,
                'std_dev_kb': std_dev_bytes / 1024,
                'sample_documents': sample_documents
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze container {container_name}: {e}")
            raise
            
    async def compare_containers(self) -> Dict[str, Any]:
        """Compare storage between spiritual-vectors and personality-vectors"""
        try:
            logger.info("🔍 Starting detailed storage analysis...")
            
            # Analyze both containers
            spiritual_analysis = await self.analyze_document_sizes('spiritual-vectors')
            personality_analysis = await self.analyze_document_sizes('personality-vectors')
            
            # Calculate differences
            size_difference_mb = spiritual_analysis['total_size_mb'] - personality_analysis['total_size_mb']
            avg_size_difference_kb = spiritual_analysis['avg_size_kb'] - personality_analysis['avg_size_kb']
            
            comparison = {
                'spiritual_vectors': spiritual_analysis,
                'personality_vectors': personality_analysis,
                'differences': {
                    'total_size_mb': size_difference_mb,
                    'avg_size_difference_kb': avg_size_difference_kb,
                    'document_count_difference': spiritual_analysis['total_documents'] - personality_analysis['total_documents']
                }
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Failed to compare containers: {e}")
            raise
            
    async def analyze_document_structure_differences(self) -> Dict[str, Any]:
        """Analyze structural differences between documents in both containers"""
        try:
            logger.info("🔍 Analyzing document structure differences...")
            
            # Get sample documents from both containers
            spiritual_container = self.db.get_container_client('spiritual-vectors')
            personality_container = self.db.get_container_client('personality-vectors')
            
            # Query first few documents from each container
            spiritual_query = "SELECT TOP 5 * FROM c"
            personality_query = "SELECT TOP 5 * FROM c"
            
            spiritual_docs = []
            personality_docs = []
            
            # Get spiritual-vectors documents
            async for item in spiritual_container.query_items(query=spiritual_query, enable_cross_partition_query=True):
                spiritual_docs.append(item)
            
            # Get personality-vectors documents
            async for item in personality_container.query_items(query=personality_query, enable_cross_partition_query=True):
                personality_docs.append(item)
            
            # Analyze structure differences
            structure_analysis = {
                'spiritual_vectors_sample': [],
                'personality_vectors_sample': [],
                'field_differences': {}
            }
            
            # Analyze spiritual-vectors structure
            for doc in spiritual_docs[:3]:  # Analyze first 3 documents
                doc_analysis = {
                    'id': doc.get('id', 'unknown'),
                    'fields': list(doc.keys()),
                    'field_count': len(doc.keys()),
                    'has_vector': 'vector' in doc,
                    'vector_length': len(doc.get('vector', [])) if 'vector' in doc else 0,
                    'estimated_size_kb': len(json.dumps(doc, ensure_ascii=False).encode('utf-8')) / 1024
                }
                structure_analysis['spiritual_vectors_sample'].append(doc_analysis)
            
            # Analyze personality-vectors structure
            for doc in personality_docs[:3]:  # Analyze first 3 documents
                doc_analysis = {
                    'id': doc.get('id', 'unknown'),
                    'fields': list(doc.keys()),
                    'field_count': len(doc.keys()),
                    'has_vector': 'vector' in doc,
                    'vector_length': len(doc.get('vector', [])) if 'vector' in doc else 0,
                    'estimated_size_kb': len(json.dumps(doc, ensure_ascii=False).encode('utf-8')) / 1024
                }
                structure_analysis['personality_vectors_sample'].append(doc_analysis)
            
            return structure_analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze document structure: {e}")
            raise
            
    def print_analysis_report(self, comparison: Dict[str, Any], structure_analysis: Dict[str, Any]):
        """Print detailed analysis report"""
        print("\n" + "="*80)
        print("📊 COSMOS DB STORAGE SIZE ANALYSIS REPORT")
        print("="*80)
        
        # Container comparison
        spiritual = comparison['spiritual_vectors']
        personality = comparison['personality_vectors']
        differences = comparison['differences']
        
        print(f"\n📦 CONTAINER COMPARISON:")
        print(f"spiritual-vectors:")
        print(f"  📄 Documents: {spiritual['total_documents']:,}")
        print(f"  💾 Total Size: {spiritual['total_size_mb']:.2f} MB")
        print(f"  📏 Avg Doc Size: {spiritual['avg_size_kb']:.2f} KB")
        print(f"  📐 Median Doc Size: {spiritual['median_size_kb']:.2f} KB")
        print(f"  📊 Size Range: {spiritual['min_size_kb']:.2f} - {spiritual['max_size_kb']:.2f} KB")
        
        print(f"\npersonality-vectors:")
        print(f"  📄 Documents: {personality['total_documents']:,}")
        print(f"  💾 Total Size: {personality['total_size_mb']:.2f} MB")
        print(f"  📏 Avg Doc Size: {personality['avg_size_kb']:.2f} KB")
        print(f"  📐 Median Doc Size: {personality['median_size_kb']:.2f} KB")
        print(f"  📊 Size Range: {personality['min_size_kb']:.2f} - {personality['max_size_kb']:.2f} KB")
        
        print(f"\n🔍 DIFFERENCES:")
        print(f"  📄 Document Count Diff: {differences['document_count_difference']}")
        print(f"  💾 Total Size Diff: {differences['total_size_mb']:.2f} MB")
        print(f"  📏 Avg Size Diff: {differences['avg_size_difference_kb']:.2f} KB")
        
        # Structure analysis
        print(f"\n🏗️ DOCUMENT STRUCTURE ANALYSIS:")
        print(f"spiritual-vectors samples:")
        for i, doc in enumerate(structure_analysis['spiritual_vectors_sample']):
            print(f"  Sample {i+1}: {doc['id']}")
            print(f"    Fields: {doc['field_count']} | Vector: {doc['has_vector']} | Length: {doc['vector_length']} | Size: {doc['estimated_size_kb']:.2f} KB")
        
        print(f"\npersonality-vectors samples:")
        for i, doc in enumerate(structure_analysis['personality_vectors_sample']):
            print(f"  Sample {i+1}: {doc['id']}")
            print(f"    Fields: {doc['field_count']} | Vector: {doc['has_vector']} | Length: {doc['vector_length']} | Size: {doc['estimated_size_kb']:.2f} KB")
        
        # Analysis conclusions
        print(f"\n💡 ANALYSIS CONCLUSIONS:")
        if abs(differences['total_size_mb']) > 5:  # Significant difference
            print(f"  ⚠️  SIGNIFICANT SIZE DIFFERENCE DETECTED: {differences['total_size_mb']:.2f} MB")
            if differences['total_size_mb'] > 0:
                print(f"  📈 spiritual-vectors is {differences['total_size_mb']:.2f} MB larger")
                print(f"  🔍 This suggests potential data loss or compression during migration")
            else:
                print(f"  📉 personality-vectors is {abs(differences['total_size_mb']):.2f} MB larger")
                print(f"  🔍 This suggests additional data was added during migration")
        else:
            print(f"  ✅ Size difference is minimal: {differences['total_size_mb']:.2f} MB")
        
        if differences['document_count_difference'] != 0:
            print(f"  ⚠️  DOCUMENT COUNT MISMATCH: {differences['document_count_difference']} documents")
        else:
            print(f"  ✅ Document counts match: {spiritual['total_documents']:,} documents each")
        
        print("="*80)
        
    async def cleanup(self):
        """Clean up resources"""
        if self.cosmos_client:
            await self.cosmos_client.close()

async def main():
    """Main function"""
    analyzer = StorageSizeAnalyzer()
    
    try:
        await analyzer.initialize_cosmos_connection()
        
        # Run comprehensive analysis
        comparison = await analyzer.compare_containers()
        structure_analysis = await analyzer.analyze_document_structure_differences()
        
        # Print detailed report
        analyzer.print_analysis_report(comparison, structure_analysis)
        
        # Save analysis to file
        analysis_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'container_comparison': comparison,
            'structure_analysis': structure_analysis
        }
        
        output_file = Path(__file__).parent / f"storage_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        logger.info(f"📁 Analysis saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"❌ Storage analysis failed: {e}")
        raise
    finally:
        await analyzer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
