#!/bin/bash

# Full Quality Validation - Run before important releases
# This runs the comprehensive validation that was previously in pre-push

set -euo pipefail

echo "🔍 FULL QUALITY VALIDATION"
echo "=========================="
echo "Running comprehensive validation (may take several minutes)"
echo ""

# Check if user really wants to run full validation
read -p "This will download dependencies and run full tests. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Full validation cancelled"
    exit 1
fi

echo "🚀 Starting comprehensive validation..."

# Run the original comprehensive validation
exec "./scripts/local-e2e-validation.sh"
