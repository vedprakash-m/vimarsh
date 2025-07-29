#!/usr/bin/env python3
"""
Repair and enhance old entries in Cosmos DB by adding missing metadata.
This script fixes entries that lack proper integration_date and other metadata
while preserving all valuable content.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('repair_entries.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('../../.env')

def analyze_entries_needing_repair(dry_run: bool = True) -> Dict[str, Any]:
    """
    Analyze entries that need metadata repair without deleting anything.
    
    Args:
        dry_run: If True, only analyze what would be repaired without actually updating
    
    Returns:
        Dictionary with analysis statistics and repair plan
    """
    try:
        from azure.cosmos import CosmosClient
        
        # Get connection string with proper error handling
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("AZURE_COSMOS_CONNECTION_STRING not found in environment variables")
        
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client('vimarsh-multi-personality')
        container = database.get_container_client('personality-vectors')
        
        logger.info("🔍 Starting repair analysis...")
        
        # Query for entries that need repair (missing or invalid integration_date)
        entries_needing_repair_query = """
        SELECT c.id, c.personality, c.integration_date, c.source, c.content, c.keywords, c.has_embedding
        FROM c 
        WHERE IS_NULL(c.integration_date) OR NOT IS_DEFINED(c.integration_date)
        """
        
        repair_stats = {
            'total_analyzed': 0,
            'by_personality': {},
            'repair_actions_needed': {
                'missing_integration_date': 0,
                'missing_personality': 0,
                'missing_keywords': 0,
                'missing_has_embedding': 0
            },
            'sample_entries': [],
            'dry_run': dry_run
        }
        
        logger.info("📊 Analyzing entries needing repair...")
        
        for item in container.query_items(query=entries_needing_repair_query, enable_cross_partition_query=True):
            repair_stats['total_analyzed'] += 1
            
            personality = item.get('personality', 'Unknown')
            
            # Count by personality
            if personality not in repair_stats['by_personality']:
                repair_stats['by_personality'][personality] = 0
            repair_stats['by_personality'][personality] += 1
            
            # Analyze what repairs are needed
            repairs_needed = []
            
            if not item.get('integration_date') or item.get('integration_date') == 'Unknown' or item.get('integration_date') is None:
                repair_stats['repair_actions_needed']['missing_integration_date'] += 1
                repairs_needed.append('integration_date')
            
            if not item.get('personality') or item.get('personality') == 'Unknown':
                repair_stats['repair_actions_needed']['missing_personality'] += 1
                repairs_needed.append('personality')
            
            if not item.get('keywords'):
                repair_stats['repair_actions_needed']['missing_keywords'] += 1
                repairs_needed.append('keywords')
            
            if not item.get('has_embedding'):
                repair_stats['repair_actions_needed']['missing_has_embedding'] += 1
                repairs_needed.append('has_embedding')
            
            # Store sample entries for reporting
            if len(repair_stats['sample_entries']) < 10:
                repair_stats['sample_entries'].append({
                    'id': item.get('id'),
                    'personality': personality,
                    'integration_date': item.get('integration_date'),
                    'content_preview': item.get('content', '')[:100] if item.get('content') else 'N/A',
                    'repairs_needed': repairs_needed
                })
        
        logger.info("📈 Analysis complete:")
        logger.info(f"  Total entries needing repair: {repair_stats['total_analyzed']}")
        logger.info(f"  Missing integration_date: {repair_stats['repair_actions_needed']['missing_integration_date']}")
        logger.info(f"  Missing has_embedding flag: {repair_stats['repair_actions_needed']['missing_has_embedding']}")
        
        return repair_stats
        
    except Exception as e:
        error_msg = f"❌ Analysis failed: {str(e)}"
        logger.error(error_msg)
        return {'error': error_msg}

def repair_entry_metadata(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Repair metadata for a single entry while preserving all content.
    
    Args:
        entry: The database entry to repair
        
    Returns:
        Updated entry with repaired metadata
    """
    repaired_entry = entry.copy()
    repairs_made = []
    
    # Fix missing integration_date
    if not entry.get('integration_date') or entry.get('integration_date') == 'Unknown' or entry.get('integration_date') is None:
        # Set to yesterday's date since these are the old entries
        repaired_entry['integration_date'] = '2025-07-27'
        repaired_entry['integration_date_repaired'] = True
        repaired_entry['integration_date_repaired_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        repairs_made.append('integration_date')
    
    # Fix missing has_embedding flag
    if 'has_embedding' not in entry or entry.get('has_embedding') is None:
        repaired_entry['has_embedding'] = False  # They likely don't have embeddings yet
        repairs_made.append('has_embedding')
    
    # Ensure personality is properly assigned
    if not entry.get('personality') or entry.get('personality') == 'Unknown':
        # Try to derive personality from keywords if available
        if entry.get('keywords') and len(entry['keywords']) > 0:
            derived_personality = entry['keywords'][0].title()
            repaired_entry['personality'] = derived_personality
            repaired_entry['personality_derived_from_keywords'] = True
            repairs_made.append('personality')
        else:
            # Default to Krishna if we can't determine otherwise
            repaired_entry['personality'] = 'Krishna'
            repaired_entry['personality_defaulted'] = True
            repairs_made.append('personality')
    
    # Add repair metadata
    if repairs_made:
        repaired_entry['metadata_repaired'] = True
        repaired_entry['repairs_made'] = repairs_made
        repaired_entry['repaired_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return repaired_entry

def repair_entries_batch(container, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Repair a batch of entries with proper error handling.
    
    Returns:
        Dictionary with repair statistics
    """
    batch_stats = {
        'processed': 0,
        'successful': 0,
        'failed': 0,
        'errors': []
    }
    
    for entry in entries:
        try:
            # Repair the entry metadata
            repaired_entry = repair_entry_metadata(entry)
            
            # Update in Cosmos DB
            container.upsert_item(repaired_entry)
            batch_stats['successful'] += 1
            
            if batch_stats['successful'] % 50 == 0:
                logger.info(f"  Repaired {batch_stats['successful']} entries...")
                
        except Exception as e:
            error_msg = f"Failed to repair entry {entry.get('id', 'unknown')}: {str(e)}"
            batch_stats['errors'].append(error_msg)
            batch_stats['failed'] += 1
            logger.error(f"  {error_msg}")
        
        batch_stats['processed'] += 1
    
    return batch_stats

def repair_old_entries(dry_run: bool = True) -> Dict[str, Any]:
    """
    Repair old entries by fixing missing metadata while preserving content.
    
    Args:
        dry_run: If True, only analyze what would be repaired without actually updating
    
    Returns:
        Dictionary with repair statistics and results
    """
    try:
        from azure.cosmos import CosmosClient
        
        # Get connection string
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("AZURE_COSMOS_CONNECTION_STRING not found in environment variables")
        
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client('vimarsh-multi-personality')
        container = database.get_container_client('personality-vectors')
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - Analyzing repairs needed")
            return analyze_entries_needing_repair(dry_run=True)
        
        logger.info("🔧 Starting entry repair operation...")
        
        # Query for entries that need repair
        entries_to_repair_query = """
        SELECT * FROM c 
        WHERE IS_NULL(c.integration_date) OR NOT IS_DEFINED(c.integration_date)
        """
        
        entries_to_repair = list(container.query_items(query=entries_to_repair_query, enable_cross_partition_query=True))
        
        repair_stats = {
            'total_entries': len(entries_to_repair),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': [],
            'dry_run': False
        }
        
        logger.info(f"Found {len(entries_to_repair)} entries to repair")
        
        if not entries_to_repair:
            logger.info("✨ No entries need repair!")
            return repair_stats
        
        # Process entries in batches for better performance
        batch_size = 100
        
        for i in range(0, len(entries_to_repair), batch_size):
            batch = entries_to_repair[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(entries_to_repair) + batch_size - 1) // batch_size
            
            logger.info(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} entries)")
            
            batch_results = repair_entries_batch(container, batch)
            
            # Update overall statistics
            repair_stats['processed'] += batch_results['processed']
            repair_stats['successful'] += batch_results['successful']
            repair_stats['failed'] += batch_results['failed']
            repair_stats['errors'].extend(batch_results['errors'])
            
            logger.info(f"✅ Batch {batch_num} complete: {batch_results['successful']}/{len(batch)} successful")
        
        logger.info("🎉 Entry repair complete!")
        logger.info(f"  Total processed: {repair_stats['processed']}")
        logger.info(f"  Successfully repaired: {repair_stats['successful']}")
        logger.info(f"  Failed: {repair_stats['failed']}")
        logger.info(f"  Success rate: {(repair_stats['successful'] / repair_stats['processed'] * 100):.1f}%")
        
        return repair_stats
        
    except Exception as e:
        error_msg = f"❌ Repair operation failed: {str(e)}"
        logger.error(error_msg)
        return {
            'error': error_msg,
            'dry_run': dry_run
        }

def main():
    """Main execution function with interactive confirmation."""
    print("🔧 Vimarsh Database Entry Repair Tool")
    print("=" * 50)
    print("This tool repairs missing metadata while preserving all content")
    
    # First, run in dry-run mode to show what would be repaired
    print("\n🔍 Step 1: Analyzing entries needing repair (dry run)")
    analysis_results = repair_old_entries(dry_run=True)
    
    if 'error' in analysis_results:
        print(f"❌ Analysis failed: {analysis_results['error']}")
        return
    
    print("\n📊 Analysis Results:")
    print(f"  Total entries needing repair: {analysis_results['total_analyzed']}")
    print(f"  Missing integration_date: {analysis_results['repair_actions_needed']['missing_integration_date']}")
    print(f"  Missing has_embedding flag: {analysis_results['repair_actions_needed']['missing_has_embedding']}")
    
    print("\n👥 Entries by personality:")
    for personality, count in analysis_results['by_personality'].items():
        print(f"  {personality}: {count} entries")
    
    if analysis_results['total_analyzed'] == 0:
        print("✨ No entries need repair. Database metadata is complete!")
        return
    
    # Show sample entries that would be repaired
    print("\n📋 Sample entries to be repaired:")
    for i, entry in enumerate(analysis_results['sample_entries'][:5], 1):
        repairs_str = ', '.join(entry['repairs_needed'])
        print(f"  {i}. ID: {entry['id'][:20]}... | Personality: {entry['personality']}")
        print(f"     Repairs needed: {repairs_str}")
        print(f"     Content: {entry['content_preview']}...")
        print()
    
    # Ask for confirmation
    print(f"🔧 REPAIR PLAN:")
    print(f"  • Add integration_date = '2025-07-27' to {analysis_results['repair_actions_needed']['missing_integration_date']} entries")
    print(f"  • Add has_embedding = false to {analysis_results['repair_actions_needed']['missing_has_embedding']} entries")
    print(f"  • All original content will be preserved")
    print(f"  • Add repair metadata for tracking")
    
    response = input(f"\nDo you want to repair {analysis_results['total_analyzed']} entries? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print("\n🔧 Step 2: Performing repairs...")
        repair_results = repair_old_entries(dry_run=False)
        
        if 'error' in repair_results:
            print(f"❌ Repair failed: {repair_results['error']}")
        else:
            print("✅ Repair completed successfully!")
            print(f"  Entries repaired: {repair_results.get('successful', 0)}")
            print(f"  All content preserved with enhanced metadata")
            if repair_results.get('failed', 0) > 0:
                print(f"  ⚠️  Some repairs failed: {repair_results['failed']}")
                print("  Check repair_entries.log for details")
    else:
        print("❌ Repair cancelled by user")

if __name__ == "__main__":
    main()
