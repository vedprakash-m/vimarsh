#!/usr/bin/env python3
"""
Update Container References Script
Updates all application code to use the new personality-vectors container exclusively.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContainerReferenceUpdater:
    """Update container references across the codebase"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        
        # Define the replacements needed
        self.container_replacements = [
            # Database container references
            ('spiritual-texts', 'personality-vectors'),
            ('spiritual_texts', 'personality_vectors'),
            
            # Database name updates (from old structure to new)
            ('vimarsh-db', 'vimarsh-multi-personality'),
            ('vimarsh"', 'vimarsh-multi-personality'),
        ]
        
        # Files to update (patterns)
        self.file_patterns = [
            'backend/services/*.py',
            'backend/config/*.py', 
            'backend/scripts/*.py',
            'scripts/*.py',
            '.env*',
            '**/*.md'  # Documentation files
        ]
        
        # Files to exclude from updates
        self.exclude_patterns = [
            '**/cleanup_old_containers.py',  # Our cleanup script - keep as-is
            '**/container_migration_*.py',   # Migration scripts - keep as-is  
            '**/storage_size_analyzer.py',   # Analysis scripts - keep as-is
            '**/simple_storage_comparison.py', # Analysis scripts - keep as-is
            '**/*test*.py',                  # Test files - update carefully
            '**/data/**/*.json',             # Data files
            '**/archive/**/*',               # Archived files
            '**/backup/**/*',                # Backup files
        ]
        
    def should_update_file(self, file_path: Path) -> bool:
        """Check if a file should be updated"""
        file_str = str(file_path)
        
        # Check exclusions first
        for exclude_pattern in self.exclude_patterns:
            if file_path.match(exclude_pattern):
                return False
        
        # Check if it matches patterns to update
        for pattern in self.file_patterns:
            if file_path.match(pattern):
                return True
                
        return False
        
    def find_files_to_update(self) -> List[Path]:
        """Find all files that need container reference updates"""
        files_to_update = []
        
        # Search for Python files
        python_files = list(self.workspace_root.rglob("*.py"))
        env_files = list(self.workspace_root.rglob(".env*"))
        md_files = list(self.workspace_root.rglob("*.md"))
        
        all_files = python_files + env_files + md_files
        
        for file_path in all_files:
            if self.should_update_file(file_path):
                # Check if file contains references that need updating
                if self.file_contains_old_references(file_path):
                    files_to_update.append(file_path)
                    
        return files_to_update
        
    def file_contains_old_references(self, file_path: Path) -> bool:
        """Check if file contains old container references"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for old references
            old_patterns = [
                r'spiritual[-_]texts(?!\.json)',  # spiritual-texts/spiritual_texts but not spiritual-texts.json
                r'vimarsh-db(?!")',              # vimarsh-db but not in quotes
                r'vimarsh"(?!\s*:)',             # vimarsh" but not "vimarsh": 
            ]
            
            for pattern in old_patterns:
                if re.search(pattern, content):
                    return True
                    
            return False
            
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return False
            
    def update_file_content(self, file_path: Path) -> Tuple[bool, str]:
        """Update container references in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            updated_content = original_content
            changes_made = []
            
            # Apply container name replacements
            if file_path.suffix == '.py':
                # Python files - be more careful with replacements
                replacements = [
                    # Container name updates
                    (r'"spiritual-texts"', '"personality-vectors"'),
                    (r"'spiritual-texts'", "'personality-vectors'"),
                    (r'spiritual_texts_container\s*=\s*["\']spiritual-texts["\']', 
                     'spiritual_texts_container = "personality-vectors"'),
                    
                    # Database name updates for Cosmos DB
                    (r'"vimarsh-db"', '"vimarsh-multi-personality"'),
                    (r"'vimarsh-db'", "'vimarsh-multi-personality'"),
                    (r'cosmos_db_name\s*=\s*["\']vimarsh-db["\']', 
                     'cosmos_db_name = "vimarsh-multi-personality"'),
                ]
                
            elif file_path.suffix == '.env' or file_path.name.startswith('.env'):
                # Environment files
                replacements = [
                    (r'AZURE_COSMOS_CONTAINER_NAME=spiritual-texts', 
                     'AZURE_COSMOS_CONTAINER_NAME=personality-vectors'),
                    (r'AZURE_COSMOS_DATABASE_NAME=vimarsh-db', 
                     'AZURE_COSMOS_DATABASE_NAME=vimarsh-multi-personality'),
                ]
                
            elif file_path.suffix == '.md':
                # Markdown files - update documentation
                replacements = [
                    (r'`spiritual-texts`', '`personality-vectors`'),
                    (r'spiritual-texts container', 'personality-vectors container'),
                    (r'vimarsh-db database', 'vimarsh-multi-personality database'),
                ]
                
            else:
                # Other files - generic replacements
                replacements = [
                    ('spiritual-texts', 'personality-vectors'),
                    ('vimarsh-db', 'vimarsh-multi-personality'),
                ]
            
            # Apply replacements
            for old_pattern, new_pattern in replacements:
                if re.search(old_pattern, updated_content):
                    updated_content = re.sub(old_pattern, new_pattern, updated_content)
                    changes_made.append(f"{old_pattern} → {new_pattern}")
            
            # Check if any changes were made
            if updated_content != original_content:
                return True, updated_content
            else:
                return False, original_content
                
        except Exception as e:
            logger.error(f"Error updating {file_path}: {e}")
            return False, ""
            
    def update_files(self, files_to_update: List[Path], dry_run: bool = True) -> Dict[str, List[str]]:
        """Update all files with new container references"""
        results = {
            'updated': [],
            'failed': [],
            'skipped': []
        }
        
        logger.info(f"{'DRY RUN: ' if dry_run else ''}Processing {len(files_to_update)} files...")
        
        for file_path in files_to_update:
            try:
                logger.info(f"Processing: {file_path.relative_to(self.workspace_root)}")
                
                success, updated_content = self.update_file_content(file_path)
                
                if success:
                    if not dry_run:
                        # Create backup
                        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                        file_path.rename(backup_path)
                        
                        # Write updated content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        
                        logger.info(f"✅ Updated: {file_path.relative_to(self.workspace_root)}")
                        results['updated'].append(str(file_path))
                    else:
                        logger.info(f"🔍 Would update: {file_path.relative_to(self.workspace_root)}")
                        results['updated'].append(str(file_path))
                else:
                    results['skipped'].append(str(file_path))
                    
            except Exception as e:
                logger.error(f"❌ Failed to update {file_path}: {e}")
                results['failed'].append(str(file_path))
        
        return results
        
    def verify_critical_services(self) -> Dict[str, bool]:
        """Verify that critical services are using the correct container"""
        critical_files = {
            'vector_database_service.py': self.workspace_root / 'backend' / 'services' / 'vector_database_service.py',
            'database_service.py': self.workspace_root / 'backend' / 'services' / 'database_service.py',
        }
        
        verification_results = {}
        
        for service_name, file_path in critical_files.items():
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for new container references
                    has_personality_vectors = 'personality-vectors' in content or 'personality_vectors' in content
                    has_old_spiritual_texts = re.search(r'spiritual[-_]texts(?!\.json)', content)
                    
                    verification_results[service_name] = {
                        'has_new_container': has_personality_vectors,
                        'has_old_container': bool(has_old_spiritual_texts),
                        'status': 'good' if has_personality_vectors and not has_old_spiritual_texts else 'needs_update'
                    }
                    
                except Exception as e:
                    verification_results[service_name] = {
                        'error': str(e),
                        'status': 'error'
                    }
            else:
                verification_results[service_name] = {
                    'status': 'missing'
                }
        
        return verification_results

def main():
    """Main function"""
    # Get workspace root (go up from backend/data_processing to root)
    current_file = Path(__file__)
    workspace_root = current_file.parent.parent.parent
    
    updater = ContainerReferenceUpdater(str(workspace_root))
    
    print("🔍 Container Reference Update Tool")
    print("=" * 50)
    
    # Find files to update
    logger.info("Scanning for files with old container references...")
    files_to_update = updater.find_files_to_update()
    
    if not files_to_update:
        print("✅ No files found with old container references!")
        return
    
    print(f"\n📋 Found {len(files_to_update)} files to update:")
    for file_path in files_to_update:
        print(f"  📄 {file_path.relative_to(workspace_root)}")
    
    # Verify critical services first
    print(f"\n🔧 Verifying critical services...")
    verification = updater.verify_critical_services()
    
    for service, status in verification.items():
        if status['status'] == 'good':
            print(f"  ✅ {service}: Using new container correctly")
        elif status['status'] == 'needs_update':
            print(f"  ⚠️  {service}: Needs update")
        elif status['status'] == 'error':
            print(f"  ❌ {service}: Error - {status.get('error')}")
        else:
            print(f"  ❓ {service}: {status['status']}")
    
    # Run dry-run first
    print(f"\n🔍 DRY RUN: Showing what would be updated...")
    dry_results = updater.update_files(files_to_update, dry_run=True)
    
    print(f"\nDRY RUN RESULTS:")
    print(f"  📝 Would update: {len(dry_results['updated'])} files")
    print(f"  ⏭️  Would skip: {len(dry_results['skipped'])} files")
    print(f"  ❌ Would fail: {len(dry_results['failed'])} files")
    
    # Ask for confirmation
    print(f"\n" + "=" * 50)
    proceed = input("Proceed with actual updates? (y/N): ")
    
    if proceed.lower() in ['y', 'yes']:
        print(f"\n🚀 Updating files...")
        actual_results = updater.update_files(files_to_update, dry_run=False)
        
        print(f"\n🎉 UPDATE COMPLETE!")
        print(f"  ✅ Updated: {len(actual_results['updated'])} files")
        print(f"  ⏭️  Skipped: {len(actual_results['skipped'])} files") 
        print(f"  ❌ Failed: {len(actual_results['failed'])} files")
        
        if actual_results['failed']:
            print(f"\n❌ Failed files:")
            for failed_file in actual_results['failed']:
                print(f"  - {failed_file}")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"  1. Review the updated files")
        print(f"  2. Test the application with new container references")
        print(f"  3. Remove .bak files after verification")
        print(f"  4. Update any environment variables in deployment")
        
    else:
        print("❌ Update cancelled")

if __name__ == "__main__":
    main()
