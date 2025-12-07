#!/usr/bin/env python3
"""
Embedding Validation Script

Validates that all embeddings in Cosmos DB have been properly migrated
to text-embedding-3-large (Azure OpenAI) with correct dimensionality and normalization.

Usage:
    python validate_embeddings.py              # Full validation
    python validate_embeddings.py --quick      # Quick count check
    python validate_embeddings.py --sample 10  # Validate sample documents

Author: Vimarsh Team
Date: December 2025
"""

import os
import sys
import json
import math
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

# Azure Cosmos DB
try:
    from azure.cosmos import CosmosClient
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    print("⚠️ Azure Cosmos DB SDK not available")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Expected configuration
EXPECTED_MODEL = "text-embedding-3-large"
EXPECTED_DIMENSION = 768


def is_normalized(embedding: List[float], tolerance: float = 0.01) -> bool:
    """Check if embedding is L2-normalized (magnitude ≈ 1.0)"""
    if not embedding:
        return False
    
    magnitude = math.sqrt(sum(x * x for x in embedding))
    return abs(magnitude - 1.0) < tolerance


def calculate_embedding_stats(embedding: List[float]) -> Dict[str, float]:
    """Calculate statistics for an embedding vector"""
    if not embedding:
        return {}
    
    magnitude = math.sqrt(sum(x * x for x in embedding))
    mean = sum(embedding) / len(embedding)
    variance = sum((x - mean) ** 2 for x in embedding) / len(embedding)
    
    return {
        'dimension': len(embedding),
        'magnitude': magnitude,
        'mean': mean,
        'variance': variance,
        'min': min(embedding),
        'max': max(embedding)
    }


class EmbeddingValidator:
    """Validates embeddings in Cosmos DB"""
    
    def __init__(self):
        self.cosmos_client = None
        self.container = None
        self._init_cosmos()
    
    def _init_cosmos(self) -> None:
        """Initialize Cosmos DB connection"""
        if not COSMOS_AVAILABLE:
            raise RuntimeError("Azure Cosmos DB SDK not available")
        
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("AZURE_COSMOS_CONNECTION_STRING not set")
        
        self.cosmos_client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE', 'vimarsh-multi-personality')
        container_name = os.getenv('AZURE_COSMOS_CONTAINER', 'personality_vectors')
        
        database = self.cosmos_client.get_database_client(database_name)
        self.container = database.get_container_client(container_name)
        
        logger.info(f"✅ Connected to {database_name}/{container_name}")
    
    def get_document_count(self) -> int:
        """Get total document count"""
        query = "SELECT VALUE COUNT(1) FROM c"
        result = list(self.container.query_items(query, enable_cross_partition_query=True))
        return result[0] if result else 0
    
    def get_embedding_model_counts(self) -> Dict[str, int]:
        """Get count of documents by embedding model - iterates through all docs"""
        # Cosmos DB GROUP BY not well supported, so we iterate
        query = "SELECT c.embedding_model FROM c"
        results = list(self.container.query_items(query, enable_cross_partition_query=True))
        
        counts: Dict[str, int] = {}
        for r in results:
            model = r.get('embedding_model', 'unknown') or 'unknown'
            counts[model] = counts.get(model, 0) + 1
        return counts
    
    def get_personality_counts(self) -> Dict[str, int]:
        """Get document count by personality - iterates through all docs"""
        query = "SELECT c.personality FROM c"
        results = list(self.container.query_items(query, enable_cross_partition_query=True))
        
        counts: Dict[str, int] = {}
        for r in results:
            personality = r.get('personality', 'unknown') or 'unknown'
            counts[personality] = counts.get(personality, 0) + 1
        return counts
    
    def validate_sample(self, sample_size: int = 10) -> List[Dict[str, Any]]:
        """Validate a random sample of documents"""
        query = f"SELECT TOP {sample_size} * FROM c"
        documents = list(self.container.query_items(query, enable_cross_partition_query=True))
        
        validations = []
        for doc in documents:
            validation = self._validate_document(doc)
            validations.append(validation)
        
        return validations
    
    def _validate_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single document's embedding"""
        doc_id = doc.get('id', 'unknown')
        personality = doc.get('personality', 'unknown')
        
        result = {
            'id': doc_id,
            'personality': personality,
            'valid': True,
            'issues': []
        }
        
        # Check embedding exists
        embedding = doc.get('embedding')
        if not embedding:
            result['valid'] = False
            result['issues'].append('Missing embedding')
            return result
        
        # Check model
        model = doc.get('embedding_model', 'unknown')
        if model != EXPECTED_MODEL:
            result['valid'] = False
            result['issues'].append(f'Wrong model: {model} (expected {EXPECTED_MODEL})')
        
        # Check dimension
        if len(embedding) != EXPECTED_DIMENSION:
            result['valid'] = False
            result['issues'].append(f'Wrong dimension: {len(embedding)} (expected {EXPECTED_DIMENSION})')
        
        # Check normalization
        if not is_normalized(embedding):
            result['valid'] = False
            magnitude = math.sqrt(sum(x * x for x in embedding))
            result['issues'].append(f'Not normalized: magnitude = {magnitude:.4f}')
        
        # Add stats
        result['stats'] = calculate_embedding_stats(embedding)
        
        return result
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run full validation of all embeddings"""
        logger.info("\n" + "=" * 60)
        logger.info("🔍 EMBEDDING VALIDATION REPORT")
        logger.info("=" * 60)
        
        # Get counts
        total = self.get_document_count()
        model_counts = self.get_embedding_model_counts()
        personality_counts = self.get_personality_counts()
        
        logger.info(f"\n📊 Document Statistics:")
        logger.info(f"   Total documents: {total:,}")
        
        logger.info(f"\n🤖 Embedding Models:")
        for model, count in sorted(model_counts.items(), key=lambda x: -x[1]):
            pct = (count / total * 100) if total > 0 else 0
            status = "✅" if model == EXPECTED_MODEL else "⚠️"
            logger.info(f"   {status} {model}: {count:,} ({pct:.1f}%)")
        
        logger.info(f"\n👥 Personalities ({len(personality_counts)}):")
        for personality, count in sorted(personality_counts.items(), key=lambda x: -x[1])[:10]:
            logger.info(f"   - {personality}: {count:,}")
        if len(personality_counts) > 10:
            logger.info(f"   ... and {len(personality_counts) - 10} more")
        
        # Validate sample
        logger.info(f"\n🧪 Sample Validation (10 documents):")
        sample_validations = self.validate_sample(10)
        valid_count = sum(1 for v in sample_validations if v['valid'])
        logger.info(f"   Valid: {valid_count}/10")
        
        for v in sample_validations:
            if not v['valid']:
                logger.info(f"   ❌ {v['id']}: {', '.join(v['issues'])}")
        
        # Migration status
        new_model_count = model_counts.get(EXPECTED_MODEL, 0)
        migration_complete = new_model_count == total
        
        logger.info(f"\n📈 Migration Status:")
        logger.info(f"   {'✅' if migration_complete else '⏳'} {new_model_count:,}/{total:,} documents migrated ({new_model_count/total*100:.1f}%)")
        
        if not migration_complete:
            old_count = total - new_model_count
            logger.info(f"   ⚠️ {old_count:,} documents still need migration")
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_documents': total,
            'model_counts': model_counts,
            'personality_counts': personality_counts,
            'sample_validations': sample_validations,
            'migration_complete': migration_complete,
            'migration_percentage': (new_model_count / total * 100) if total > 0 else 0
        }
        
        # Save report
        report_path = Path(__file__).parent / 'validation_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"\n📝 Report saved to {report_path}")
        
        return result
    
    def run_quick_check(self) -> Dict[str, int]:
        """Quick count check without detailed validation"""
        logger.info("⚡ Quick validation check...")
        
        total = self.get_document_count()
        model_counts = self.get_embedding_model_counts()
        
        new_model_count = model_counts.get(EXPECTED_MODEL, 0)
        
        logger.info(f"   Total: {total:,}")
        logger.info(f"   Migrated: {new_model_count:,} ({new_model_count/total*100:.1f}%)")
        logger.info(f"   Remaining: {total - new_model_count:,}")
        
        return model_counts


def main():
    parser = argparse.ArgumentParser(description='Validate Cosmos DB embeddings')
    parser.add_argument('--quick', action='store_true', help='Quick count check only')
    parser.add_argument('--sample', type=int, default=0, help='Validate N sample documents')
    
    args = parser.parse_args()
    
    # Load environment
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
    
    try:
        validator = EmbeddingValidator()
        
        if args.quick:
            validator.run_quick_check()
        elif args.sample > 0:
            validations = validator.validate_sample(args.sample)
            valid = sum(1 for v in validations if v['valid'])
            logger.info(f"Validated {valid}/{len(validations)} documents successfully")
        else:
            validator.run_full_validation()
            
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        raise


if __name__ == "__main__":
    main()
