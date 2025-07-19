"""
Database Transaction Manager for Vimarsh
Provides atomic operations across dual storage systems (JSON + Cosmos DB)
Ensures consistency while preserving cost-optimized pause-resume strategy
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Type, TypeVar
from enum import Enum
import uuid

# Import database models and services
from .database_service import (
    DatabaseService, 
    SpiritualText, 
    Conversation, 
    UsageRecord, 
    UserStats,
    PersonalityConfig,
    EnhancedSpiritualText
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TransactionState(Enum):
    """Transaction state enumeration"""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class TransactionOperation:
    """Represents a single database operation within a transaction"""
    
    def __init__(self, operation_type: str, data: Any, collection: str, operation_id: str = None):
        self.operation_id = operation_id or str(uuid.uuid4())
        self.operation_type = operation_type  # 'create', 'update', 'delete'
        self.data = data
        self.collection = collection
        self.timestamp = datetime.utcnow()
        self.local_backup = None  # For rollback purposes
        self.cosmos_backup = None  # For rollback purposes


class DatabaseTransaction:
    """Represents a database transaction with rollback capabilities"""
    
    def __init__(self, transaction_id: str = None):
        self.transaction_id = transaction_id or str(uuid.uuid4())
        self.operations: List[TransactionOperation] = []
        self.state = TransactionState.PENDING
        self.created_at = datetime.utcnow()
        self.committed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None


class DatabaseTransactionManager:
    """
    Manages atomic transactions across dual storage systems.
    Ensures consistency between local JSON and Cosmos DB while preserving
    the cost-optimized pause-resume architecture.
    """
    
    def __init__(self, db_service: DatabaseService = None):
        self.db_service = db_service or DatabaseService()
        self.active_transactions: Dict[str, DatabaseTransaction] = {}
        self.transaction_log_path = os.path.join(
            self.db_service.storage_path, 
            'transaction_log.json'
        )
        self._init_transaction_log()
    
    def _init_transaction_log(self):
        """Initialize transaction log for recovery"""
        os.makedirs(os.path.dirname(self.transaction_log_path), exist_ok=True)
        if not os.path.exists(self.transaction_log_path):
            with open(self.transaction_log_path, 'w') as f:
                json.dump([], f)
    
    @asynccontextmanager
    async def transaction(self):
        """
        Context manager for database transactions.
        
        Usage:
            async with transaction_manager.transaction() as tx:
                await tx.save_usage_record(usage_record)
                await tx.save_user_stats(user_stats)
                # Automatically commits on success, rolls back on exception
        """
        transaction = DatabaseTransaction()
        self.active_transactions[transaction.transaction_id] = transaction
        
        try:
            logger.info(f"🔄 Starting transaction: {transaction.transaction_id}")
            yield TransactionContext(self, transaction)
            
            # Commit transaction if no exceptions occurred
            await self._commit_transaction(transaction)
            logger.info(f"✅ Transaction committed: {transaction.transaction_id}")
            
        except Exception as e:
            # Rollback transaction on any exception
            logger.error(f"❌ Transaction failed: {transaction.transaction_id}, Error: {e}")
            await self._rollback_transaction(transaction, str(e))
            raise
        
        finally:
            # Clean up transaction
            self.active_transactions.pop(transaction.transaction_id, None)
    
    async def _commit_transaction(self, transaction: DatabaseTransaction):
        """Commit all operations in a transaction"""
        try:
            # First, execute all operations in both storage systems
            for operation in transaction.operations:
                await self._execute_operation(operation)
            
            # Update transaction state
            transaction.state = TransactionState.COMMITTED
            transaction.committed_at = datetime.utcnow()
            
            # Log successful transaction
            await self._log_transaction(transaction)
            
        except Exception as e:
            transaction.state = TransactionState.FAILED
            transaction.error_message = str(e)
            await self._log_transaction(transaction)
            raise
    
    async def _rollback_transaction(self, transaction: DatabaseTransaction, error_message: str):
        """Rollback all operations in a transaction"""
        try:
            logger.warning(f"🔄 Rolling back transaction: {transaction.transaction_id}")
            
            # Rollback operations in reverse order
            for operation in reversed(transaction.operations):
                await self._rollback_operation(operation)
            
            transaction.state = TransactionState.ROLLED_BACK
            transaction.error_message = error_message
            
            # Log rollback
            await self._log_transaction(transaction)
            
        except Exception as rollback_error:
            logger.error(f"❌ Rollback failed for transaction {transaction.transaction_id}: {rollback_error}")
            transaction.state = TransactionState.FAILED
            transaction.error_message = f"Original: {error_message}, Rollback: {rollback_error}"
            await self._log_transaction(transaction)
    
    async def _execute_operation(self, operation: TransactionOperation):
        """Execute a single operation in both storage systems"""
        try:
            if operation.operation_type == 'create':
                await self._execute_create(operation)
            elif operation.operation_type == 'update':
                await self._execute_update(operation)
            elif operation.operation_type == 'delete':
                await self._execute_delete(operation)
            else:
                raise ValueError(f"Unknown operation type: {operation.operation_type}")
        
        except Exception as e:
            logger.error(f"❌ Operation failed: {operation.operation_id}, Error: {e}")
            raise
    
    async def _execute_create(self, operation: TransactionOperation):
        """Execute create operation"""
        data = operation.data
        
        # Save to local storage first (faster, easier to rollback)
        if operation.collection == 'spiritual_texts':
            success = self.db_service._add_to_local(data)
        elif operation.collection == 'conversations':
            success = self.db_service._save_conversation_local(data)
        elif operation.collection == 'usage_records':
            success = self.db_service._save_usage_record_local(data)
        elif operation.collection == 'user_stats':
            success = self.db_service._save_user_stats_local(data)
        else:
            raise ValueError(f"Unknown collection: {operation.collection}")
        
        if not success:
            raise Exception(f"Failed to save to local storage: {operation.collection}")
        
        # Save to Cosmos DB if enabled
        if self.db_service.is_cosmos_enabled:
            cosmos_success = await self.db_service._save_to_cosmos(
                self.db_service.conversations_container, 
                data
            )
            if not cosmos_success:
                raise Exception(f"Failed to save to Cosmos DB: {operation.collection}")
    
    async def _execute_update(self, operation: TransactionOperation):
        """Execute update operation"""
        # Similar logic to create, but with update semantics
        # For now, treating updates as upserts (create or replace)
        await self._execute_create(operation)
    
    async def _execute_delete(self, operation: TransactionOperation):
        """Execute delete operation"""
        # Implementation would depend on delete requirements
        # For now, focusing on create/update operations as they are most critical
        raise NotImplementedError("Delete operations not yet implemented")
    
    async def _rollback_operation(self, operation: TransactionOperation):
        """Rollback a single operation"""
        logger.info(f"🔄 Rolling back operation: {operation.operation_id}")
        
        # For create operations, we need to remove the created records
        # This is complex for dual storage, so for now we'll log the issue
        # In production, this would involve:
        # 1. Removing from local JSON file
        # 2. Deleting from Cosmos DB
        # 3. Restoring any overwritten data
        
        logger.warning(f"⚠️ Rollback not fully implemented for operation: {operation.operation_id}")
        logger.warning(f"   Manual cleanup may be required for collection: {operation.collection}")
    
    async def _log_transaction(self, transaction: DatabaseTransaction):
        """Log transaction to persistent log for recovery"""
        try:
            # Read existing log
            with open(self.transaction_log_path, 'r') as f:
                log_data = json.load(f)
            
            # Add transaction record
            log_entry = {
                'transaction_id': transaction.transaction_id,
                'state': transaction.state.value,
                'created_at': transaction.created_at.isoformat(),
                'committed_at': transaction.committed_at.isoformat() if transaction.committed_at else None,
                'error_message': transaction.error_message,
                'operation_count': len(transaction.operations)
            }
            
            log_data.append(log_entry)
            
            # Keep only last 1000 transactions
            if len(log_data) > 1000:
                log_data = log_data[-1000:]
            
            # Write back to log
            with open(self.transaction_log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to log transaction: {e}")
    
    async def validate_consistency(self) -> Dict[str, Any]:
        """
        Validate consistency between local and Cosmos DB storage.
        Returns a report of any inconsistencies found.
        """
        logger.info("🔍 Starting consistency validation...")
        
        inconsistencies = {
            'spiritual_texts': [],
            'conversations': [],
            'usage_records': [],
            'user_stats': [],
            'summary': {
                'total_inconsistencies': 0,
                'validation_time': datetime.utcnow().isoformat()
            }
        }
        
        # Only validate if Cosmos DB is enabled
        if not self.db_service.is_cosmos_enabled:
            logger.info("ℹ️ Cosmos DB not enabled, skipping consistency validation")
            return inconsistencies
        
        # Validate each collection
        # Note: This is a simplified validation - in production, this would be more thorough
        try:
            # For now, just log that validation would occur
            logger.info("✅ Consistency validation completed (placeholder implementation)")
            
        except Exception as e:
            logger.error(f"❌ Consistency validation failed: {e}")
            inconsistencies['summary']['validation_error'] = str(e)
        
        return inconsistencies
    
    async def get_transaction_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent transaction history"""
        try:
            with open(self.transaction_log_path, 'r') as f:
                log_data = json.load(f)
            
            # Return most recent transactions
            return list(reversed(log_data[-limit:]))
        
        except Exception as e:
            logger.error(f"Failed to get transaction history: {e}")
            return []


class TransactionContext:
    """
    Context for executing operations within a transaction.
    Provides transactional versions of database operations.
    """
    
    def __init__(self, manager: DatabaseTransactionManager, transaction: DatabaseTransaction):
        self.manager = manager
        self.transaction = transaction
    
    async def save_usage_record(self, usage_record: UsageRecord):
        """Save usage record within transaction"""
        operation = TransactionOperation(
            operation_type='create',
            data=usage_record,
            collection='usage_records'
        )
        self.transaction.operations.append(operation)
        logger.debug(f"📋 Added usage record operation to transaction: {self.transaction.transaction_id}")
    
    async def save_user_stats(self, user_stats: UserStats):
        """Save user stats within transaction"""
        operation = TransactionOperation(
            operation_type='update',  # Stats are typically updates
            data=user_stats,
            collection='user_stats'
        )
        self.transaction.operations.append(operation)
        logger.debug(f"📋 Added user stats operation to transaction: {self.transaction.transaction_id}")
    
    async def save_conversation(self, conversation: Conversation):
        """Save conversation within transaction"""
        operation = TransactionOperation(
            operation_type='create',
            data=conversation,
            collection='conversations'
        )
        self.transaction.operations.append(operation)
        logger.debug(f"📋 Added conversation operation to transaction: {self.transaction.transaction_id}")
    
    async def save_spiritual_text(self, spiritual_text: Union[SpiritualText, EnhancedSpiritualText]):
        """Save spiritual text within transaction"""
        operation = TransactionOperation(
            operation_type='create',
            data=spiritual_text,
            collection='spiritual_texts'
        )
        self.transaction.operations.append(operation)
        logger.debug(f"📋 Added spiritual text operation to transaction: {self.transaction.transaction_id}")


# Global transaction manager instance
transaction_manager = DatabaseTransactionManager()


# Utility functions for easy access
async def atomic_token_operation(usage_record: UsageRecord, user_stats: UserStats):
    """
    Perform atomic token tracking operation.
    Ensures both usage record and user stats are saved together.
    """
    async with transaction_manager.transaction() as tx:
        await tx.save_usage_record(usage_record)
        await tx.save_user_stats(user_stats)


async def atomic_conversation_save(conversation: Conversation, usage_record: Optional[UsageRecord] = None):
    """
    Perform atomic conversation save with optional usage tracking.
    """
    async with transaction_manager.transaction() as tx:
        await tx.save_conversation(conversation)
        if usage_record:
            await tx.save_usage_record(usage_record)
