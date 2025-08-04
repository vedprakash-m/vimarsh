#!/bin/bash

# Vimarsh Data Sources Setup Script
# This script sets up the required data sources for the Vimarsh platform

set -e

echo "🕉️ Setting up Vimarsh data sources..."

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/sources/raw-bg/chapters
mkdir -p data/cache
mkdir -p data/cost_tracking
mkdir -p data/demo_analytics
mkdir -p data/real_time_monitoring
mkdir -p data/real_time_demo
mkdir -p data/validation_test
mkdir -p data/spiritual_validation_test
mkdir -p data/test_vector_storage
mkdir -p data/rag_llm_test_storage
mkdir -p data/vector_storage
mkdir -p data/vectors

echo "📚 Setting up spiritual text sources..."

# Note: Large spiritual text files should be downloaded separately
# or generated from authoritative sources
echo "⚠️  Note: Large spiritual text files (Bhagavad Gita, etc.) should be:"
echo "   1. Downloaded from authoritative sources"
echo "   2. Generated using data processing scripts"
echo "   3. Or loaded from production database backup"

echo "🔧 Creating default configuration files..."

# Create default cost monitoring config if it doesn't exist
if [ ! -f "data/cost_monitoring_config.json" ]; then
    cat > data/cost_monitoring_config.json << 'EOF'
{
  "monitoring_enabled": true,
  "cost_alerts": {
    "daily_limit": 50.0,
    "monthly_limit": 1000.0
  },
  "tracking_granularity": "hourly",
  "currency": "USD"
}
EOF
    echo "✅ Created cost_monitoring_config.json"
fi

# Create default demo config
cat > data/real_time_demo/demo_config.json << 'EOF'
{
  "demo_mode": false,
  "sample_queries": [
    "What is dharma?",
    "How can I find inner peace?",
    "What is the purpose of life?"
  ],
  "demo_personality": "krishna"
}
EOF

# Create default validation config
cat > data/validation_test/test_config.json << 'EOF'
{
  "test_mode": true,
  "validation_queries": [
    "Test spiritual guidance",
    "Validate personality responses"
  ],
  "expected_response_time_ms": 5000
}
EOF

echo "✅ Data source setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Run data processing scripts to generate spiritual texts"
echo "   2. Configure production data sources"
echo "   3. Test the setup with: npm test or python -m pytest"
echo ""
echo "🔗 For production data loading, see:"
echo "   - scripts/production_validator.py"
echo "   - backend/scripts/download_personality_data.py"
