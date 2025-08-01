#!/bin/bash

# Vimarsh Pre-Push Hook
# Comprehensive validation before pushing to prevent CI/CD failures

set -e

echo "🕉️  Vimarsh Pre-Push Validation"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track validation results
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0

# Helper functions
error() {
    echo -e "${RED}❌ $1${NC}"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "📍 Project root: $PROJECT_ROOT"
echo ""

# 1. Validate project structure
echo "📁 Validating Project Structure..."

# Check critical directories
REQUIRED_DIRS=(
    "backend"
    "frontend" 
    "infrastructure"
    "tests"
    "docs"
    ".github/workflows"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        success "Directory exists: $dir"
    else
        error "Missing required directory: $dir"
    fi
done

# Check critical files
CRITICAL_FILES=(
    "README.md"
    "backend/requirements.txt"
    "backend/function_app.py"
    "frontend/package.json"
    "frontend/src/App.tsx"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        success "File exists: $file"
    else
        error "Missing critical file: $file"
    fi
done

echo ""

# 2. Validate backend dependencies and structure
echo "🐍 Validating Backend..."

cd "$PROJECT_ROOT/backend"

# Check Python syntax for key files
KEY_PYTHON_FILES=(
    "function_app.py"
    "services/llm_service.py"
    "core/config.py"
    "monitoring/app_insights.py"
)

for py_file in "${KEY_PYTHON_FILES[@]}"; do
    if [[ -f "$py_file" ]]; then
        if python3 -m py_compile "$py_file" 2>/dev/null; then
            success "Python syntax valid: $py_file"
        else
            error "Python syntax error in: $py_file"
        fi
    else
        warning "Python file not found: $py_file"
    fi
done

# Check for test files that CI/CD expects
EXPECTED_TEST_FILES=(
    "tests/test_cost_management.py"
    "tests/test_monitoring_comprehensive.py"
    "tests/test_voice_interface_comprehensive.py"
    "tests/performance/__init__.py"
)

for test_file in "${EXPECTED_TEST_FILES[@]}"; do
    if [[ -f "$test_file" ]]; then
        success "Test file exists: $test_file"
    else
        error "Missing test file expected by CI/CD: $test_file"
    fi
done

# Check for missing modules that caused import errors
REQUIRED_MODULES=(
    "monitoring/alerts.py"
    "monitoring/real_time.py"
)

for module in "${REQUIRED_MODULES[@]}"; do
    if [[ -f "$module" ]]; then
        success "Module exists: $module"
    else
        error "Missing module: $module"
    fi
done

echo ""

# 3. Validate frontend configuration
echo "⚛️ Validating Frontend..."

cd "$PROJECT_ROOT/frontend"

# Check package.json for required scripts
if [[ -f "package.json" ]]; then
    success "package.json exists"
    
    # Check for required npm scripts
    REQUIRED_SCRIPTS=("start" "build" "test" "test:coverage")
    
    for script in "${REQUIRED_SCRIPTS[@]}"; do
        if grep -q "\"$script\":" package.json; then
            success "NPM script exists: $script"
        else
            error "Missing NPM script: $script"
        fi
    done
    
    # Check for package-lock.json
    if [[ -f "package-lock.json" ]]; then
        success "package-lock.json exists"
    else
        warning "package-lock.json not found - npm ci may fail in CI/CD"
    fi
else
    error "package.json not found"
fi

echo ""

# 4. Validate CI/CD workflows
echo "🔄 Validating CI/CD Workflows..."

cd "$PROJECT_ROOT"

WORKFLOW_FILES=(
    ".github/workflows/unified-ci-cd.yml"
)

for workflow in "${WORKFLOW_FILES[@]}"; do
    if [[ -f "$workflow" ]]; then
        success "Workflow exists: $(basename $workflow)"
        
        # Check for shell injection patterns (basic check)
        if grep -q '\${{.*github\..*}}.*|' "$workflow"; then
            warning "Potential shell injection pattern in $workflow"
        fi
        
        # Check YAML syntax if yamllint is available
        if command -v yamllint &> /dev/null; then
            if yamllint "$workflow" &> /dev/null; then
                success "YAML syntax valid: $(basename $workflow)"
            else
                error "YAML syntax error in: $(basename $workflow)"
            fi
        fi
    else
        error "Missing workflow file: $workflow"
    fi
done

echo ""

# 5. Run quick tests
echo "🧪 Running Quick Tests..."

cd "$PROJECT_ROOT/backend"

# Run basic import tests
if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import services.llm_service
    import core.config
    import monitoring.app_insights
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" 2>/dev/null; then
    success "Core Python imports working"
else
    error "Core Python imports failing"
fi

# Run basic pytest if available
if command -v pytest &> /dev/null; then
    if pytest tests/test_basic_integration.py -v --tb=short &> /dev/null; then
        success "Basic integration tests passing"
    else
        warning "Basic integration tests failing - check before push"
    fi
else
    warning "pytest not available - install for better validation"
fi

echo ""

# 6. Security validation
echo "🔒 Security Validation..."

cd "$PROJECT_ROOT"

# Check for hardcoded secrets (focused patterns, excluding venv and common false positives)
SECRET_PATTERNS=(
    "AIza[0-9A-Za-z_-]{35}"  # Google API key pattern
    "sk-[a-zA-Z0-9]{20,}"  # OpenAI API key pattern
    "private_key\s*[=:]\s*[\"'][^\"']{50,}[\"']"
    "client_secret\s*[=:]\s*[\"'][a-zA-Z0-9_-]{20,}[\"']"
)

SECURITY_ISSUES=0
for pattern in "${SECRET_PATTERNS[@]}"; do
    # Exclude venv, test files, and common non-sensitive patterns
    if grep -r -E "$pattern" backend/ frontend/ config/ --include="*.py" --include="*.js" --include="*.ts" --include="*.tsx" --include="*.json" --exclude-dir=.venv --exclude-dir=venv --exclude-dir=.python_packages --exclude-dir=node_modules --exclude-dir=tests --exclude-dir=test --exclude="*test*" --exclude="*mock*" | grep -v "example\|sample\|placeholder\|dummy\|template\|TODO\|XXX\|pydantic\|fsspec" &> /dev/null; then
        warning "Potential hardcoded secret found (pattern: $pattern)"
        grep -r -E "$pattern" backend/ frontend/ config/ --include="*.py" --include="*.js" --include="*.ts" --include="*.tsx" --include="*.json" --exclude-dir=.venv --exclude-dir=venv --exclude-dir=.python_packages --exclude-dir=node_modules --exclude-dir=tests --exclude-dir=test --exclude="*test*" --exclude="*mock*" | grep -v "example\|sample\|placeholder\|dummy\|template\|TODO\|XXX\|pydantic\|fsspec" | head -3
        SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
    fi
done

# Additional check for .env files that shouldn't be committed (excluding already deleted ones)
ENV_FILES_FOUND=$(find . -name ".env" -o -name ".env.local" -o -name ".env.production" 2>/dev/null | grep -v ".env.example" || true)
if [[ -n "$ENV_FILES_FOUND" ]]; then
    warning "Environment files found - ensure no secrets are committed:"
    echo "$ENV_FILES_FOUND"
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
fi

if [[ $SECURITY_ISSUES -eq 0 ]]; then
    success "No obvious hardcoded secrets found"
fi

echo ""

# 7. Final validation
echo "📊 Validation Summary"
echo "===================="

echo -e "✅ Passed checks: $((${#REQUIRED_DIRS[@]} + ${#CRITICAL_FILES[@]} + ${#EXPECTED_TEST_FILES[@]} + ${#REQUIRED_MODULES[@]} + ${#WORKFLOW_FILES[@]} - VALIDATION_ERRORS))"
echo -e "⚠️  Warnings: $VALIDATION_WARNINGS"
echo -e "❌ Errors: $VALIDATION_ERRORS"

echo ""

if [[ $VALIDATION_ERRORS -gt 0 ]]; then
    echo -e "${RED}🚫 Pre-push validation FAILED${NC}"
    echo -e "${RED}Fix $VALIDATION_ERRORS errors before pushing to prevent CI/CD failures${NC}"
    echo ""
    echo "💡 Common fixes:"
    echo "  - Run: python scripts/local_e2e_validation.py"
    echo "  - Create missing test files in backend/tests/"
    echo "  - Add missing NPM scripts to frontend/package.json"
    echo "  - Check Python imports and module structure"
    echo ""
    exit 1
elif [[ $VALIDATION_WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  Pre-push validation PASSED with warnings${NC}"
    echo -e "${YELLOW}Consider addressing $VALIDATION_WARNINGS warnings${NC}"
    echo ""
    
    # Check if running in git hook (non-interactive)
    if [[ -n "$GIT_DIR" ]] || [[ ! -t 0 ]]; then
        echo -e "${YELLOW}Running in git hook - proceeding with warnings${NC}"
    else
        read -p "Continue with push? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${GREEN}🎉 Pre-push validation PASSED${NC}"
    echo -e "${GREEN}Ready for CI/CD pipeline!${NC}"
fi

echo -e "${BLUE}🙏 May your code bring wisdom and peace to all seekers${NC}"
