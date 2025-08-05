#!/bin/bash

# Smart test execution script for Vimarsh CI/CD optimization
# This script reduces test execution time by running only relevant tests

set -e

BACKEND_CHANGED="${1:-false}"
FRONTEND_CHANGED="${2:-false}"
TEST_TYPE="${3:-unit}"

echo "🧪 Smart Test Execution"
echo "Backend changed: $BACKEND_CHANGED"
echo "Frontend changed: $FRONTEND_CHANGED"
echo "Test type: $TEST_TYPE"

# Backend optimizations
if [[ "$BACKEND_CHANGED" == "true" ]]; then
    echo "📦 Running backend tests..."
    cd backend
    
    case "$TEST_TYPE" in
        "unit")
            # Run only unit tests, skip slow integration tests
            python -m pytest tests/ -v \
                -k "not integration and not e2e and not comprehensive" \
                --tb=short \
                --disable-warnings \
                --maxfail=5 \
                --durations=10 \
                --no-header \
                --no-summary \
                -q
            ;;
        "integration")
            # Run only critical integration tests
            python -m pytest tests/ -v \
                -k "integration and not comprehensive" \
                --tb=short \
                --disable-warnings \
                --maxfail=3 \
                --durations=5 \
                --no-header \
                -q
            ;;
        "critical")
            # Run only critical path tests for main branch
            python -m pytest tests/ -v \
                -k "test_spiritual_guidance or test_auth or test_security" \
                --tb=short \
                --disable-warnings \
                --maxfail=1 \
                -q
            ;;
    esac
else
    echo "⏭️ Skipping backend tests (no changes detected)"
fi

# Frontend optimizations
if [[ "$FRONTEND_CHANGED" == "true" ]]; then
    echo "🎨 Running frontend tests..."
    cd frontend
    
    # Use Jest with optimizations
    npm run test:ci -- \
        --runInBand \
        --forceExit \
        --detectOpenHandles=false \
        --maxWorkers=2 \
        --silent \
        --passWithNoTests
else
    echo "⏭️ Skipping frontend tests (no changes detected)"
fi

echo "✅ Smart test execution completed"
