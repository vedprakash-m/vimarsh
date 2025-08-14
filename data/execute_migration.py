#!/usr/bin/env python3
"""
Migration execution script
Orchestrates the complete migration process with safety checks
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_script(script_path, description):
    """Run a Python script and return success status"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, cwd=os.path.dirname(script_path))
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def confirm_step(message):
    """Get user confirmation before proceeding"""
    response = input(f"\n⚠️ {message} (yes/no): ")
    return response.lower() == 'yes'

def main():
    """Main migration execution function"""
    print("🕉️ VIMARSH DATABASE MIGRATION")
    print("=" * 60)
    print("This script will migrate from 3-container to 11-container architecture")
    print("Critical data (6,514 personality vectors with embeddings) will be preserved")
    print()
    
    # Pre-flight checks
    print("🔍 PRE-FLIGHT CHECKS")
    print("-" * 30)
    
    # Check if .env exists
    env_path = "../../.env"
    if not os.path.exists(env_path):
        print("❌ .env file not found in root directory")
        print("Please create .env with AZURE_COSMOS_CONNECTION_STRING")
        return False
    
    print("✅ .env file found")
    
    # Check if data processing directory exists
    data_processing_dir = os.path.dirname(os.path.abspath(__file__))
    required_scripts = [
        'backup_all_data.py',
        'create_new_containers.py',
        'validate_migration.py',
        'rollback_migration.py'
    ]
    
    for script in required_scripts:
        script_path = os.path.join(data_processing_dir, script)
        if not os.path.exists(script_path):
            print(f"❌ Required script not found: {script}")
            return False
    
    print("✅ All required scripts found")
    
    # Get user confirmation
    if not confirm_step("Ready to start migration? This will modify your Cosmos DB"):
        print("❌ Migration cancelled by user")
        return False
    
    # Store script paths
    backup_script = os.path.join(data_processing_dir, 'backup_all_data.py')
    create_containers_script = os.path.join(data_processing_dir, 'create_new_containers.py')
    validate_script = os.path.join(data_processing_dir, 'validate_migration.py')
    
    migration_start_time = datetime.now()
    
    # PHASE 1: Backup current data
    print(f"\n📋 PHASE 1: DATA BACKUP")
    print("This will create a complete backup of all current data")
    
    backup_success = run_script(backup_script, "PHASE 1: Backup Current Data")
    if not backup_success:
        print("❌ MIGRATION FAILED: Backup phase failed")
        print("Your original data is still intact. Please check errors above.")
        return False
    
    print("✅ PHASE 1 COMPLETED: All data backed up safely")
    
    # PHASE 2: Create new containers
    print(f"\n📦 PHASE 2: CONTAINER CREATION")
    print("This will create 11 new containers with proper configuration")
    
    if not confirm_step("Proceed with creating new containers?"):
        print("❌ Migration cancelled at Phase 2")
        print("Your original data is still intact.")
        return False
    
    containers_success = run_script(create_containers_script, "PHASE 2: Create New Containers")
    if not containers_success:
        print("❌ MIGRATION FAILED: Container creation failed")
        print("Your original data is still intact.")
        print("You may need to clean up any partially created containers.")
        return False
    
    print("✅ PHASE 2 COMPLETED: New containers created")
    
    # PHASE 3: Data migration (manual step)
    print(f"\n🔄 PHASE 3: DATA MIGRATION")
    print("Now you need to run the data migration scripts:")
    print()
    print("1. Run migrate_users.py to migrate user data")
    print("2. Run migrate_personality_vectors.py to migrate vector data")
    print("3. Run create_personality_configs.py to create personality configurations")
    print()
    print("These scripts are detailed in docs/db_migration_plan.md")
    
    if not confirm_step("Have you completed the data migration scripts?"):
        print("⚠️ Please complete data migration before validation")
        print("See docs/db_migration_plan.md for detailed instructions")
        return False
    
    # PHASE 4: Validation
    print(f"\n🔍 PHASE 4: MIGRATION VALIDATION")
    print("This will validate that all data was migrated correctly")
    
    validation_success = run_script(validate_script, "PHASE 4: Validate Migration")
    if not validation_success:
        print("❌ MIGRATION VALIDATION FAILED")
        print("This means data may not have been migrated correctly.")
        print()
        print("Options:")
        print("1. Check and fix migration issues manually")
        print("2. Run rollback_migration.py to restore original state")
        print("3. Review logs and try migration again")
        return False
    
    print("✅ PHASE 4 COMPLETED: Migration validated successfully")
    
    # Final summary
    migration_end_time = datetime.now()
    duration = migration_end_time - migration_start_time
    
    print(f"\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Migration duration: {duration}")
    print(f"Started: {migration_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Completed: {migration_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("✅ All 6,514 personality vectors with embeddings preserved")
    print("✅ Users and activity data migrated")
    print("✅ New 11-container architecture ready")
    print("✅ All validations passed")
    print()
    print("📋 NEXT STEPS:")
    print("1. Update backend code to use new container structure")
    print("2. Update frontend to work with new data models")
    print("3. Run comprehensive testing")
    print("4. Deploy updated application")
    print()
    print("📚 See docs/db_migration_plan.md for backend/frontend update details")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 TROUBLESHOOTING:")
        print("- Check logs above for specific errors")
        print("- Ensure .env file has correct Cosmos DB connection string")
        print("- Verify azure-cosmos package is installed: pip install azure-cosmos")
        print("- If data is corrupted, run rollback_migration.py")
        sys.exit(1)
