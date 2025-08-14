# Database Migration Guide

## Overview

This directory contains scripts and documentation for migrating the Vimarsh database from the current 3-container structure to the new 11-container architecture defined in `docs/db_design.md`.

## ⚠️ Critical Information

- **Current Database**: 6,514 personality vectors with embeddings (no backup exists)
- **Migration Risk**: High - embeddings are expensive to regenerate
- **Safety First**: Complete backup is created before any changes

## 📁 Migration Scripts

### Core Migration Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `execute_migration.py` | **Main orchestrator** - runs entire migration process | Start here |
| `backup_all_data.py` | Creates complete backup of current data | Phase 1 |
| `create_new_containers.py` | Creates 11 new containers with proper configuration | Phase 2 |
| `validate_migration.py` | Validates migration was successful | Phase 4 |
| `rollback_migration.py` | **Emergency rollback** - restores original structure | If problems occur |

### Data Migration Scripts (Run Manually)

| Script | Purpose | Data Migrated |
|--------|---------|---------------|
| `migrate_users.py` | Migrate user data with enhanced schema | 18 user documents |
| `migrate_personality_vectors.py` | **CRITICAL** - Migrate 6,514 vectors with embeddings | All personality vectors |
| `create_personality_configs.py` | Create personality configuration documents | 13 personality configs |

## 🚀 Quick Start

### Prerequisites

1. **Environment Setup**:
   ```bash
   # Ensure .env file exists in project root with:
   AZURE_COSMOS_CONNECTION_STRING="your_connection_string"
   AZURE_COSMOS_DATABASE_NAME="vimarsh-multi-personality"
   ```

2. **Dependencies**:
   ```bash
   pip install azure-cosmos python-dotenv
   ```

### Execute Migration

```bash
# Navigate to data processing directory
cd backend/data_processing

# Run the main migration orchestrator
python execute_migration.py
```

The script will guide you through each phase with confirmations.

## 📋 Migration Phases

### Phase 1: Data Backup ✅
- **Script**: `backup_all_data.py`
- **Purpose**: Create complete backup before any changes
- **Output**: `data/migration_backups/backup_YYYYMMDD_HHMMSS/`
- **Critical**: Contains all 6,514 personality vectors with embeddings

### Phase 2: Container Creation ✅
- **Script**: `create_new_containers.py`
- **Purpose**: Create 11 new containers with proper configuration
- **Containers Created**:
  - `users` (enhanced schema)
  - `user_sessions` (new)
  - `user_interactions` (new)
  - `personalities` (new)
  - `personality_vectors` (enhanced with hierarchical partitioning)
  - Analytics containers: `user_analytics`, `content_analytics`, etc.

### Phase 3: Data Migration (Manual) ⚠️
- **Scripts**: `migrate_users.py`, `migrate_personality_vectors.py`, `create_personality_configs.py`
- **Purpose**: Move data from old to new containers
- **Critical**: Preserve embeddings and enhance data models

### Phase 4: Validation ✅
- **Script**: `validate_migration.py`
- **Purpose**: Verify all data migrated correctly
- **Checks**:
  - Document counts match expected values
  - Embeddings preserved in personality_vectors
  - Partition keys configured correctly
  - All containers exist and accessible

## 🔧 Individual Script Usage

### Backup Data
```bash
python backup_all_data.py
```
Creates timestamped backup in `data/migration_backups/`

### Create New Containers
```bash
python create_new_containers.py
```
Creates 11 containers with proper configuration

### Validate Migration
```bash
python validate_migration.py
```
Comprehensive validation of migration success

### Emergency Rollback
```bash
python rollback_migration.py
```
⚠️ **Use only if migration fails** - restores original 3-container structure

## 📊 Expected Data Counts

| Container | Original | After Migration | Notes |
|-----------|----------|----------------|-------|
| personality-vectors → personality_vectors | 6,514 | 6,514 | **CRITICAL** - Must match exactly |
| users | 18 | 18+ | May increase with enhanced schema |
| user_activity → user_interactions | 121 | 121+ | Enhanced with sessions |
| personalities | 0 | 13 | New configuration container |

## 🛡️ Safety Measures

### Before Migration
- ✅ Complete backup created automatically
- ✅ Validation of current data structure
- ✅ User confirmation required at each phase

### During Migration
- ✅ Atomic operations where possible
- ✅ Progress tracking and logging
- ✅ Error handling with detailed messages

### After Migration
- ✅ Comprehensive validation
- ✅ Rollback capability if issues found
- ✅ Original data preserved until validation passes

## 🚨 Troubleshooting

### Common Issues

1. **Connection Error**:
   ```
   ❌ AZURE_COSMOS_CONNECTION_STRING not found
   ```
   **Solution**: Check `.env` file in project root

2. **Permission Error**:
   ```
   ❌ Error creating container: Forbidden
   ```
   **Solution**: Ensure connection string has sufficient permissions

3. **Data Count Mismatch**:
   ```
   ❌ personality_vectors: Expected 6514, got 6500
   ```
   **Solution**: Run rollback and investigate missing data

4. **Validation Failures**:
   ```
   ❌ MIGRATION VALIDATION FAILED
   ```
   **Solution**: Review specific validation errors and fix or rollback

### Emergency Procedures

#### If Migration Fails Midway
1. **DO NOT PANIC** - original data is backed up
2. Review error messages carefully
3. Run `python rollback_migration.py` to restore original state
4. Investigate issues before retrying

#### If Data Loss Suspected
1. **STOP IMMEDIATELY**
2. Run `python rollback_migration.py`
3. Verify rollback with `python validate_migration.py`
4. Contact technical team if needed

## 📚 Related Documentation

- **[Migration Plan](../../docs/db_migration_plan.md)**: Comprehensive 60+ page migration plan
- **[Database Design](../../docs/db_design.md)**: Target architecture specification
- **[Backend Updates](../../docs/db_migration_plan.md#phase-6-backend-code-updates)**: Code changes needed
- **[Frontend Updates](../../docs/db_migration_plan.md#phase-7-frontend-updates)**: UI changes needed

## 🎯 Success Criteria

### Migration is successful when:
- ✅ All 6,514 personality vectors migrated with embeddings intact
- ✅ User and activity data enhanced and migrated
- ✅ 11 containers created with proper configuration
- ✅ All validation checks pass
- ✅ No data loss detected

### Post-Migration Tasks:
1. Update backend code to use new container structure
2. Update frontend to work with enhanced data models
3. Run comprehensive application testing
4. Deploy updated application
5. Monitor for any issues

## 📞 Support

If you encounter issues during migration:

1. **Check logs** for specific error messages
2. **Review troubleshooting** section above
3. **Use rollback** if data integrity is at risk
4. **Document issues** for future improvements

---

**Remember**: The personality vectors are irreplaceable. When in doubt, prioritize data safety over migration speed.
