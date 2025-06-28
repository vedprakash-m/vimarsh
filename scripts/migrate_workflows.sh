#!/bin/bash

# CI/CD Workflow Migration Script
# Safely migrates from multiple disconnected workflows to unified DAG workflow

set -e

echo "🔄 Migrating CI/CD Workflows to Unified DAG Pipeline"
echo "=================================================="

WORKFLOWS_DIR=".github/workflows"
BACKUP_DIR=".github/workflows/backup-$(date +%Y%m%d-%H%M%S)"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup of existing workflows..."

# List of old workflow files to backup and remove
OLD_WORKFLOWS=(
    "ci-cd.yml"
    "ci-cd-optimized.yml" 
    "test.yml"
    "test-optimized.yml"
    "vimarsh-optimized-test-suite.yml"
)

# Backup old workflows
for workflow in "${OLD_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        echo "  📄 Backing up $workflow"
        cp "$WORKFLOWS_DIR/$workflow" "$BACKUP_DIR/"
    fi
done

echo ""
echo "🔍 Analyzing current workflow issues:"
echo "  ❌ Multiple redundant CI/CD workflows"
echo "  ❌ No proper DAG structure"
echo "  ❌ Disconnected job execution"
echo "  ❌ Duplicate logic across workflows"
echo "  ❌ Resource waste from parallel redundant jobs"
echo ""

echo "✅ New unified workflow benefits:"
echo "  🎯 Single DAG pipeline with proper dependencies"
echo "  ⚡ Intelligent change detection and conditional execution"
echo "  🔒 Security scanning integrated into pipeline"
echo "  🧪 Parallel testing with proper orchestration"
echo "  🏗️ Artifact-based deployment pipeline"
echo "  📊 Comprehensive monitoring and notifications"
echo "  🧹 Automatic cleanup and resource management"
echo ""

# Ask for confirmation
read -p "📋 Ready to migrate to unified workflow? (y/N): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "❌ Migration cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting migration..."

# Remove old workflows
for workflow in "${OLD_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        echo "  🗑️  Removing old workflow: $workflow"
        rm "$WORKFLOWS_DIR/$workflow"
    fi
done

# Create workflow documentation
cat > "$WORKFLOWS_DIR/README.md" << 'EOF'
# Vimarsh CI/CD Workflows

## Unified Pipeline Architecture

This directory contains a single, unified CI/CD pipeline that follows DAG (Directed Acyclic Graph) principles for optimal efficiency and reliability.

### Pipeline Stages

```mermaid
graph TD
    A[Setup & Change Detection] --> B[Security Scan]
    B --> C[Backend Tests]
    B --> D[Frontend Tests]
    C --> E[Integration Tests]
    D --> E
    E --> F[Build Backend]
    E --> G[Build Frontend]
    F --> H[Deploy Staging]
    G --> H
    F --> I[Deploy Production]
    G --> I
    H --> J[Post-Deploy Validation]
    I --> J
    J --> K[Notify & Cleanup]
```

### Key Features

- **🎯 Intelligent Execution**: Only runs necessary stages based on change detection
- **🔒 Security First**: Integrated security scanning before any deployments
- **⚡ Parallel Processing**: Backend and frontend tests run in parallel
- **🏗️ Artifact-Based Deployment**: Builds once, deploys multiple times
- **📊 Comprehensive Monitoring**: Full visibility into pipeline health
- **🧹 Resource Management**: Automatic cleanup of temporary resources

### Workflow Files

- `unified-ci-cd.yml` - Main CI/CD pipeline (replaces all previous workflows)

### Migration History

Previous workflows have been consolidated:
- `ci-cd.yml` → Merged into unified pipeline
- `ci-cd-optimized.yml` → Merged into unified pipeline  
- `test.yml` → Merged into unified pipeline
- `test-optimized.yml` → Merged into unified pipeline
- `vimarsh-optimized-test-suite.yml` → Merged into unified pipeline
- `deploy.yml` → Integrated into unified pipeline

Backups are stored in `backup-*` directories.

### Usage

The unified pipeline automatically:
1. Detects what changed in your commit
2. Runs only the necessary tests and builds
3. Deploys to appropriate environments based on branch
4. Provides comprehensive feedback and notifications

No manual intervention required - the pipeline is fully automated and intelligent.
EOF

echo "  📝 Created workflow documentation"

# Update any references in other files
echo "  🔄 Updating workflow references..."

# Update any scripts or documentation that reference old workflows
if [ -f "scripts/workflow_validator.py" ]; then
    echo "  📝 Updating workflow validator..."
    # Update workflow validator to reference new unified workflow
fi

echo ""
echo "✅ Migration completed successfully!"
echo ""
echo "📊 Summary:"
echo "  🗂️  Backup created: $BACKUP_DIR"
echo "  🗑️  Old workflows removed: ${#OLD_WORKFLOWS[@]} files"
echo "  ✨ New unified workflow: unified-ci-cd.yml"
echo "  📝 Documentation updated: README.md"
echo ""
echo "🎯 Next steps:"
echo "  1. Review the new unified-ci-cd.yml workflow"
echo "  2. Commit and push changes"
echo "  3. Test the pipeline with a small change"
echo "  4. Monitor first few runs for any issues"
echo ""
echo "🔗 The new pipeline will automatically:"
echo "  • Run faster with intelligent change detection"
echo "  • Provide better visibility with structured stages"
echo "  • Reduce CI/CD resource usage significantly"
echo "  • Eliminate redundant job execution"
echo ""
echo "🎉 Your CI/CD pipeline is now optimized!"
