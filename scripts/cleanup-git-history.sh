#!/bin/bash
# Script to remove sensitive files from Git history
# ⚠️  WARNING: This rewrites history - coordinate with team first!

echo "🧹 Cleaning up sensitive files from Git history..."

# Files to remove from history
FILES_TO_REMOVE=(
    "frontend-static/"
    "test-secret-detection.sh" 
    "e2e_validation_results_basic_20250726_100819.json"
    "docs/bkp/bkp_metadata.md"
    "frontend/build.zip"
)

# Method 1: Remove files from last few commits (if recent)
echo "Method 1: Soft cleanup (if files were in recent commits)"
for file in "${FILES_TO_REMOVE[@]}"; do
    echo "Checking if $file exists in recent history..."
    if git log --oneline -10 --name-only | grep -q "$file"; then
        echo "Found $file in recent history"
        git rm -r --cached "$file" 2>/dev/null || true
    fi
done

# Add files to .gitignore to prevent re-adding
echo "Adding patterns to .gitignore..."
cat >> .gitignore << EOF

# Security: Prevent accidental commit of sensitive files
frontend-static/
*validation_results*.json
test-secret-detection.sh
docs/bkp/
frontend/build.zip
*.zip
EOF

echo "✅ Soft cleanup complete. Commit and push these changes."
echo ""
echo "If files are still in GitHub after push, run the HARD cleanup method below:"
echo ""
echo "⚠️  HARD CLEANUP (REWRITES HISTORY - DANGEROUS!):"
echo "git filter-branch --force --index-filter 'git rm -r --cached --ignore-unmatch frontend-static/' --prune-empty --tag-name-filter cat -- --all"
echo "git push origin --force --all"
echo ""
echo "🔒 Remember: Always coordinate with team before rewriting history!"
