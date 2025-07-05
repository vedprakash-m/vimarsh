#!/usr/bin/env python3
"""
Simple Cosmos DB Data Migration Script (Synchronous)
Loads processed spiritual texts directly into Azure Cosmos DB without vector embeddings
"""

import json
from azure.cosmos import CosmosClient, exceptions
import os
import sys
from typing import Dict, Any, List
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
COSMOS_CONNECTION_STRING = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
DATABASE_NAME = "vimarsh-db"
CONTAINER_NAME = "spiritual-texts"

if not COSMOS_CONNECTION_STRING:
    raise ValueError("AZURE_COSMOS_CONNECTION_STRING environment variable is required")

class CosmosDBMigrator:
    def __init__(self):
        self.client = None
        self.database = None
        self.container = None
        
    def initialize(self):
        """Initialize Cosmos DB connection"""
        try:
            self.client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
            
            # Create database if it doesn't exist (serverless mode)
            try:
                self.database = self.client.create_database_if_not_exists(id=DATABASE_NAME)
                logger.info(f"✅ Database '{DATABASE_NAME}' ready")
            except exceptions.CosmosResourceExistsError:
                self.database = self.client.get_database_client(DATABASE_NAME)
                logger.info(f"✅ Using existing database '{DATABASE_NAME}'")
            
            # Create container if it doesn't exist (serverless mode)
            try:
                self.container = self.database.create_container_if_not_exists(
                    id=CONTAINER_NAME,
                    partition_key={'paths': ['/scripture'], 'kind': 'Hash'}
                )
                logger.info(f"✅ Container '{CONTAINER_NAME}' ready")
            except exceptions.CosmosResourceExistsError:
                self.container = self.database.get_container_client(CONTAINER_NAME)
                logger.info(f"✅ Using existing container '{CONTAINER_NAME}'")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB: {e}")
            raise
    
    def load_jsonl_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load records from JSONL file"""
        records = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        if line.strip():
                            record = json.loads(line)
                            records.append(record)
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ Skipping invalid JSON on line {line_num} in {file_path}: {e}")
            
            logger.info(f"📄 Loaded {len(records)} records from {file_path}")
            return records
            
        except Exception as e:
            logger.error(f"❌ Failed to load {file_path}: {e}")
            return []
    
    def insert_record(self, record: Dict[str, Any]) -> bool:
        """Insert a single record into Cosmos DB"""
        try:
            # Ensure the record has required fields
            if 'id' not in record:
                logger.warning("⚠️ Record missing 'id' field, skipping")
                return False
            
            if 'scripture' not in record:
                logger.warning(f"⚠️ Record {record.get('id', 'unknown')} missing 'scripture' field, skipping")
                return False
            
            # Add timestamp if not present
            if 'created_at' not in record:
                record['created_at'] = datetime.utcnow().isoformat()
            
            self.container.create_item(body=record)
            return True
            
        except exceptions.CosmosResourceExistsError:
            logger.debug(f"📝 Record {record.get('id', 'unknown')} already exists, skipping")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to insert record {record.get('id', 'unknown')}: {e}")
            return False
    
    def migrate_data(self, file_paths: List[str]):
        """Migrate data from multiple JSONL files"""
        total_loaded = 0
        total_success = 0
        total_failed = 0
        
        self.initialize()
        
        for file_path in file_paths:
            logger.info(f"🔄 Processing {file_path}...")
            records = self.load_jsonl_file(file_path)
            
            if not records:
                logger.warning(f"⚠️ No records loaded from {file_path}")
                continue
            
            total_loaded += len(records)
            
            # Insert records one by one with progress updates
            for i, record in enumerate(records):
                success = self.insert_record(record)
                
                if success:
                    total_success += 1
                else:
                    total_failed += 1
                
                # Progress update every 50 records
                if (i + 1) % 50 == 0 or (i + 1) == len(records):
                    logger.info(f"📊 Progress: {i + 1}/{len(records)} records processed from {os.path.basename(file_path)}")
        
        # Final report
        logger.info("🎉 MIGRATION COMPLETE!")
        logger.info(f"📊 Total records loaded: {total_loaded}")
        logger.info(f"✅ Successfully inserted: {total_success}")
        logger.info(f"❌ Failed insertions: {total_failed}")
        logger.info(f"📈 Success rate: {(total_success / total_loaded * 100):.1f}%" if total_loaded > 0 else "No data processed")

def main():
    """Main migration function"""
    if len(sys.argv) < 2:
        print("Usage: python migrate_cosmos_data.py <jsonl_file1> [jsonl_file2] ...")
        print("\nExample:")
        print("  python migrate_cosmos_data.py data/sources/bhagavad_gita_clean.jsonl data/sources/sri_isopanisad_clean.jsonl")
        sys.exit(1)
    
    file_paths = sys.argv[1:]
    
    # Verify files exist
    missing_files = [path for path in file_paths if not os.path.exists(path)]
    if missing_files:
        logger.error(f"❌ Files not found: {missing_files}")
        sys.exit(1)
    
    logger.info("🚀 Starting Cosmos DB migration...")
    logger.info(f"📂 Files to process: {file_paths}")
    
    migrator = CosmosDBMigrator()
    migrator.migrate_data(file_paths)

if __name__ == "__main__":
    main()
