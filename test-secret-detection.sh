#!/bin/bash
# Test script for the pre-push hook
# This script creates test files with secrets to verify the hook works

echo "🧪 Testing pre-push hook secret detection..."

# Create test directory
mkdir -p test-secrets

# Test 1: Create a file with Google API key
echo "GOOGLE_API_KEY=AIzaSyDummyKeyForTestingPurposes123456" > test-secrets/test-google-api.env
echo "✓ Created test file with Google API key pattern"

# Test 2: Create a file with GitHub token
echo "GITHUB_TOKEN=gho_1234567890abcdefghijklmnopqrstuvwxyz" > test-secrets/test-github.env
echo "✓ Created test file with GitHub token pattern"

# Test 3: Create a file with Azure connection string
echo "AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=abcdefghijklmnopqrstuvwxyz123456789012345678901234567890123456789012345678901234567890==" > test-secrets/test-azure.env
echo "✓ Created test file with Azure connection string"

# Test 4: Create a file with password
echo "DATABASE_PASSWORD=\"super_secret_password_123\"" > test-secrets/test-password.env
echo "✓ Created test file with password pattern"

# Add files to git
git add test-secrets/

echo ""
echo "🔍 Now testing the pre-push hook..."
echo "The hook should detect these secrets and prevent the push."
echo ""

# Try to commit and push (this should fail)
git commit -m "Test commit with secrets (should be blocked)"

echo ""
echo "📝 To test the hook, run:"
echo "   git push origin main"
echo ""
echo "The push should be blocked with secret detection messages."
echo ""
echo "🧹 To clean up test files:"
echo "   git reset --soft HEAD~1"
echo "   git reset HEAD test-secrets/"
echo "   rm -rf test-secrets/"
echo "   git clean -fd"
