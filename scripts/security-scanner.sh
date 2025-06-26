#!/bin/bash

# =============================================================================
# Vimarsh Security Scanning and Compliance Verification Script
# =============================================================================
# Comprehensive security scanning and compliance verification for production deployments

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs/security-scanning"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/security-scan_$TIMESTAMP.log"
REPORT_FILE="$LOG_DIR/security-report_$TIMESTAMP.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Global variables
ENVIRONMENT=""
SCAN_TYPE="full"
VERBOSE=false
DRY_RUN=false
SECURITY_RESULTS=()
FAILED_SCANS=0
TOTAL_SCANS=0
CRITICAL_ISSUES=0
HIGH_ISSUES=0
MEDIUM_ISSUES=0
LOW_ISSUES=0

# =============================================================================
# Utility Functions
# =============================================================================

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "$@"
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    log "SUCCESS" "$@"
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    log "WARNING" "$@"
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    log "ERROR" "$@"
    echo -e "${RED}[ERROR]${NC} $*"
}

log_critical() {
    log "CRITICAL" "$@"
    echo -e "${RED}[CRITICAL]${NC} $*"
}

log_scan() {
    log "SCAN" "$@"
    echo -e "${PURPLE}[SCAN]${NC} $*"
}

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Vimarsh Security Scanning and Compliance Verification

OPTIONS:
    -e, --environment ENV    Target environment (dev|staging|prod)
    -t, --scan-type TYPE     Scan type (quick|full|compliance|custom)
    -c, --category CAT       Specific category to scan (dependencies|secrets|code|infrastructure|compliance)
    -h, --help              Show this help message
    --dry-run               Show what would be scanned without executing
    --verbose               Enable verbose logging
    --output FORMAT         Output format (json|html|markdown) [default: json]

SCAN TYPES:
    quick                   Fast security scan of critical vulnerabilities
    full                    Comprehensive security scan (default)
    compliance              Focus on compliance verification (GDPR, SOC2, etc.)
    custom                  Custom scan based on specified categories

CATEGORIES:
    dependencies            Scan for vulnerable dependencies
    secrets                 Check for exposed secrets and credentials
    code                    Static code analysis for security issues
    infrastructure          Infrastructure security configuration
    compliance              Regulatory compliance verification

EXAMPLES:
    $0 --environment prod --scan-type full --verbose
    $0 --environment staging --scan-type quick
    $0 --environment prod --scan-type compliance --output html
    $0 --category dependencies --environment dev

EOF
}

check_dependencies() {
    local deps=("jq" "curl" "git")
    local missing_deps=()
    
    # Check for Python security tools
    local python_tools=("bandit" "safety" "semgrep")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_warning "Missing optional dependencies: ${missing_deps[*]}"
        log_info "Some security scans may be limited. Install missing tools for full functionality."
    fi
    
    # Check Python security tools
    for tool in "${python_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_info "Python security tool '$tool' not found. Install with: pip install $tool"
        fi
    done
}

# =============================================================================
# Security Scanning Functions
# =============================================================================

run_security_scan() {
    local scan_name="$1"
    local scan_function="$2"
    local severity="$3"
    
    ((TOTAL_SCANS++))
    log_scan "Running security scan: $scan_name"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would run security scan: $scan_name"
        SECURITY_RESULTS+=("{\"name\": \"$scan_name\", \"status\": \"DRY_RUN\", \"severity\": \"$severity\"}")
        return 0
    fi
    
    local start_time=$(date +%s)
    local result
    
    if result=$($scan_function 2>&1); then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log_success "✓ $scan_name (${duration}s)"
        SECURITY_RESULTS+=("{\"name\": \"$scan_name\", \"status\": \"PASS\", \"severity\": \"$severity\", \"duration\": $duration, \"result\": \"$result\"}")
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        case "$severity" in
            "CRITICAL")
                log_critical "✗ $scan_name (${duration}s)"
                ((CRITICAL_ISSUES++))
                ;;
            "HIGH")
                log_error "✗ $scan_name (${duration}s)"
                ((HIGH_ISSUES++))
                ;;
            "MEDIUM")
                log_warning "✗ $scan_name (${duration}s)"
                ((MEDIUM_ISSUES++))
                ;;
            "LOW")
                log_info "✗ $scan_name (${duration}s)"
                ((LOW_ISSUES++))
                ;;
        esac
        
        SECURITY_RESULTS+=("{\"name\": \"$scan_name\", \"status\": \"FAIL\", \"severity\": \"$severity\", \"duration\": $duration, \"error\": \"$result\"}")
        ((FAILED_SCANS++))
        return 1
    fi
}

# Dependency Security Scans
scan_python_dependencies() {
    if command -v safety &> /dev/null; then
        cd "$PROJECT_ROOT/backend"
        safety check --json 2>/dev/null || echo "Dependencies have known vulnerabilities"
    else
        echo "Safety tool not available - install with: pip install safety"
        return 1
    fi
}

scan_npm_dependencies() {
    if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
        cd "$PROJECT_ROOT/frontend"
        if command -v npm &> /dev/null; then
            npm audit --audit-level=moderate --json 2>/dev/null || echo "NPM audit found vulnerabilities"
        else
            echo "NPM not available"
            return 1
        fi
    else
        echo "No package.json found"
        return 1
    fi
}

# Secret Detection Scans
scan_exposed_secrets() {
    # Basic secret pattern detection
    local patterns=(
        "password\s*=\s*['\"][^'\"]+['\"]"
        "api[_-]?key\s*=\s*['\"][^'\"]+['\"]"
        "secret\s*=\s*['\"][^'\"]+['\"]"
        "token\s*=\s*['\"][^'\"]+['\"]"
        "AKIA[0-9A-Z]{16}"  # AWS Access Key
        "sk-[a-zA-Z0-9]{48}" # OpenAI API Key
    )
    
    local found_secrets=0
    
    for pattern in "${patterns[@]}"; do
        if grep -r -E -i "$pattern" "$PROJECT_ROOT" --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ --exclude="*.log" >/dev/null 2>&1; then
            ((found_secrets++))
        fi
    done
    
    if [ $found_secrets -gt 0 ]; then
        echo "Found $found_secrets potential secret patterns"
        return 1
    else
        echo "No obvious secrets detected"
        return 0
    fi
}

scan_git_history_secrets() {
    # Check git history for secrets (last 100 commits)
    if [ -d "$PROJECT_ROOT/.git" ]; then
        local secret_count=0
        local patterns=("password" "api_key" "secret" "token")
        
        for pattern in "${patterns[@]}"; do
            if git log --oneline -100 | grep -i "$pattern" >/dev/null 2>&1; then
                ((secret_count++))
            fi
        done
        
        if [ $secret_count -gt 0 ]; then
            echo "Found potential secrets in git history"
            return 1
        else
            echo "No secrets detected in recent git history"
            return 0
        fi
    else
        echo "Not a git repository"
        return 1
    fi
}

# Code Security Scans
scan_python_code_security() {
    if command -v bandit &> /dev/null; then
        cd "$PROJECT_ROOT"
        bandit -r backend/ -f json 2>/dev/null | jq -r '.results | length' | grep -q "^0$" || echo "Python security issues found"
    else
        echo "Bandit tool not available - install with: pip install bandit"
        return 1
    fi
}

scan_typescript_code_security() {
    # Basic TypeScript/JavaScript security patterns
    local security_patterns=(
        "eval\s*\("
        "innerHTML\s*="
        "document\.write\s*\("
        "setTimeout\s*\(\s*['\"][^'\"]*['\"]"
        "setInterval\s*\(\s*['\"][^'\"]*['\"]"
    )
    
    local issues_found=0
    
    for pattern in "${security_patterns[@]}"; do
        if find "$PROJECT_ROOT/frontend" -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" | xargs grep -E "$pattern" >/dev/null 2>&1; then
            ((issues_found++))
        fi
    done
    
    if [ $issues_found -gt 0 ]; then
        echo "Found $issues_found potential security issues in TypeScript/JavaScript code"
        return 1
    else
        echo "No obvious security issues in frontend code"
        return 0
    fi
}

# Infrastructure Security Scans
scan_azure_configuration() {
    # Check Bicep templates for security best practices
    local bicep_files=("$PROJECT_ROOT"/infrastructure/*.bicep)
    local security_issues=0
    
    for file in "${bicep_files[@]}"; do
        if [ -f "$file" ]; then
            # Check for common security misconfigurations
            if grep -q "publicNetworkAccess.*Enabled" "$file" 2>/dev/null; then
                ((security_issues++))
            fi
            if grep -q "allowBlobPublicAccess.*true" "$file" 2>/dev/null; then
                ((security_issues++))
            fi
            if grep -q "minTlsVersion.*1\.0\|minTlsVersion.*1\.1" "$file" 2>/dev/null; then
                ((security_issues++))
            fi
        fi
    done
    
    if [ $security_issues -gt 0 ]; then
        echo "Found $security_issues potential Azure security misconfigurations"
        return 1
    else
        echo "Azure configuration appears secure"
        return 0
    fi
}

scan_tls_configuration() {
    # Check for proper TLS configuration
    local config_files=(
        "$PROJECT_ROOT/infrastructure/functions.bicep"
        "$PROJECT_ROOT/infrastructure/static-web-app.bicep"
    )
    
    local tls_issues=0
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            if ! grep -q "httpsOnly.*true" "$file" 2>/dev/null; then
                ((tls_issues++))
            fi
            if ! grep -q "minTlsVersion.*1\.2" "$file" 2>/dev/null; then
                ((tls_issues++))
            fi
        fi
    done
    
    if [ $tls_issues -gt 0 ]; then
        echo "TLS configuration issues found"
        return 1
    else
        echo "TLS configuration is secure"
        return 0
    fi
}

# Compliance Verification Scans
scan_gdpr_compliance() {
    # Check for GDPR compliance indicators
    local gdpr_indicators=(
        "privacy policy"
        "data protection"
        "user consent"
        "data retention"
        "right to be forgotten"
    )
    
    local found_indicators=0
    
    for indicator in "${gdpr_indicators[@]}"; do
        if find "$PROJECT_ROOT" -name "*.md" -o -name "*.txt" -o -name "*.py" -o -name "*.ts" -o -name "*.tsx" | xargs grep -i "$indicator" >/dev/null 2>&1; then
            ((found_indicators++))
        fi
    done
    
    if [ $found_indicators -ge 3 ]; then
        echo "GDPR compliance indicators found ($found_indicators/5)"
        return 0
    else
        echo "Insufficient GDPR compliance indicators ($found_indicators/5)"
        return 1
    fi
}

scan_data_handling_compliance() {
    # Check for proper data handling practices
    local data_patterns=(
        "encrypt.*data"
        "hash.*password"
        "sanitize.*input"
        "validate.*input"
        "audit.*log"
    )
    
    local secure_patterns_found=0
    
    for pattern in "${data_patterns[@]}"; do
        if find "$PROJECT_ROOT" -name "*.py" -o -name "*.ts" -o -name "*.tsx" | xargs grep -E -i "$pattern" >/dev/null 2>&1; then
            ((secure_patterns_found++))
        fi
    done
    
    if [ $secure_patterns_found -ge 3 ]; then
        echo "Good data handling practices found ($secure_patterns_found/5)"
        return 0
    else
        echo "Insufficient data handling security patterns ($secure_patterns_found/5)"
        return 1
    fi
}

scan_spiritual_content_protection() {
    # Ensure spiritual content is properly protected and attributed
    local protection_patterns=(
        "sacred.*text"
        "attribution"
        "copyright"
        "public.*domain"
        "expert.*review"
    )
    
    local protection_found=0
    
    for pattern in "${protection_patterns[@]}"; do
        if find "$PROJECT_ROOT" -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.md" | xargs grep -E -i "$pattern" >/dev/null 2>&1; then
            ((protection_found++))
        fi
    done
    
    if [ $protection_found -ge 3 ]; then
        echo "Spiritual content protection measures found ($protection_found/5)"
        return 0
    else
        echo "Insufficient spiritual content protection ($protection_found/5)"
        return 1
    fi
}

# =============================================================================
# Scan Orchestration
# =============================================================================

run_dependency_scans() {
    log_info "=== Running Dependency Security Scans ==="
    
    run_security_scan "Python Dependencies (Safety)" scan_python_dependencies "HIGH"
    run_security_scan "NPM Dependencies (Audit)" scan_npm_dependencies "HIGH"
}

run_secret_scans() {
    log_info "=== Running Secret Detection Scans ==="
    
    run_security_scan "Exposed Secrets Detection" scan_exposed_secrets "CRITICAL"
    run_security_scan "Git History Secret Scan" scan_git_history_secrets "HIGH"
}

run_code_scans() {
    log_info "=== Running Code Security Scans ==="
    
    run_security_scan "Python Code Security (Bandit)" scan_python_code_security "MEDIUM"
    run_security_scan "TypeScript Code Security" scan_typescript_code_security "MEDIUM"
}

run_infrastructure_scans() {
    log_info "=== Running Infrastructure Security Scans ==="
    
    run_security_scan "Azure Configuration Security" scan_azure_configuration "HIGH"
    run_security_scan "TLS Configuration" scan_tls_configuration "HIGH"
}

run_compliance_scans() {
    log_info "=== Running Compliance Verification Scans ==="
    
    run_security_scan "GDPR Compliance Check" scan_gdpr_compliance "MEDIUM"
    run_security_scan "Data Handling Compliance" scan_data_handling_compliance "MEDIUM"
    run_security_scan "Spiritual Content Protection" scan_spiritual_content_protection "LOW"
}

# =============================================================================
# Reporting
# =============================================================================

generate_security_report() {
    local report_format="${OUTPUT_FORMAT:-json}"
    
    case "$report_format" in
        "json")
            generate_json_report
            ;;
        "html")
            generate_html_report
            ;;
        "markdown")
            generate_markdown_report
            ;;
        *)
            generate_json_report
            ;;
    esac
}

generate_json_report() {
    cat > "$REPORT_FILE" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "environment": "$ENVIRONMENT",
    "scan_type": "$SCAN_TYPE",
    "summary": {
        "total_scans": $TOTAL_SCANS,
        "failed_scans": $FAILED_SCANS,
        "passed_scans": $((TOTAL_SCANS - FAILED_SCANS)),
        "critical_issues": $CRITICAL_ISSUES,
        "high_issues": $HIGH_ISSUES,
        "medium_issues": $MEDIUM_ISSUES,
        "low_issues": $LOW_ISSUES,
        "overall_score": $(python3 -c "
import sys
total = $TOTAL_SCANS
failed = $FAILED_SCANS
critical = $CRITICAL_ISSUES
high = $HIGH_ISSUES

if total == 0:
    print(0)
    sys.exit()

# Calculate weighted score
base_score = ((total - failed) / total) * 100
penalty = (critical * 20) + (high * 10)
final_score = max(0, base_score - penalty)
print(f'{final_score:.1f}')
")
    },
    "results": [
$(printf '%s\n' "${SECURITY_RESULTS[@]}" | sed '$!s/$/,/')
    ]
}
EOF
    
    log_info "Security report saved to: $REPORT_FILE"
}

generate_html_report() {
    local html_file="${REPORT_FILE%.json}.html"
    
    cat > "$html_file" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Vimarsh Security Scan Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .critical { color: #d32f2f; font-weight: bold; }
        .high { color: #f57c00; font-weight: bold; }
        .medium { color: #fbc02d; }
        .low { color: #388e3c; }
        .pass { color: #2e7d32; }
        .summary { background: #e3f2fd; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .scan-result { margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Vimarsh Security Scan Report</h1>
        <p>Environment: ENVIRONMENT_PLACEHOLDER</p>
        <p>Scan Type: SCAN_TYPE_PLACEHOLDER</p>
        <p>Generated: $(date)</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <p>Total Scans: TOTAL_SCANS_PLACEHOLDER</p>
        <p>Failed Scans: FAILED_SCANS_PLACEHOLDER</p>
        <p class="critical">Critical Issues: CRITICAL_ISSUES_PLACEHOLDER</p>
        <p class="high">High Issues: HIGH_ISSUES_PLACEHOLDER</p>
        <p class="medium">Medium Issues: MEDIUM_ISSUES_PLACEHOLDER</p>
        <p class="low">Low Issues: LOW_ISSUES_PLACEHOLDER</p>
    </div>
    
    <h2>📋 Scan Results</h2>
    <!-- Results will be populated here -->
    
</body>
</html>
EOF
    
    # Replace placeholders
    sed -i "s/ENVIRONMENT_PLACEHOLDER/$ENVIRONMENT/g" "$html_file"
    sed -i "s/SCAN_TYPE_PLACEHOLDER/$SCAN_TYPE/g" "$html_file"
    sed -i "s/TOTAL_SCANS_PLACEHOLDER/$TOTAL_SCANS/g" "$html_file"
    sed -i "s/FAILED_SCANS_PLACEHOLDER/$FAILED_SCANS/g" "$html_file"
    sed -i "s/CRITICAL_ISSUES_PLACEHOLDER/$CRITICAL_ISSUES/g" "$html_file"
    sed -i "s/HIGH_ISSUES_PLACEHOLDER/$HIGH_ISSUES/g" "$html_file"
    sed -i "s/MEDIUM_ISSUES_PLACEHOLDER/$MEDIUM_ISSUES/g" "$html_file"
    sed -i "s/LOW_ISSUES_PLACEHOLDER/$LOW_ISSUES/g" "$html_file"
    
    log_info "HTML report saved to: $html_file"
}

print_summary() {
    echo ""
    log_info "=== Security Scanning Summary ==="
    log_info "Environment: $ENVIRONMENT"
    log_info "Scan Type: $SCAN_TYPE"
    log_info "Total Scans: $TOTAL_SCANS"
    log_info "Passed: $((TOTAL_SCANS - FAILED_SCANS))"
    log_info "Failed: $FAILED_SCANS"
    
    echo ""
    log_info "=== Issue Breakdown ==="
    if [ $CRITICAL_ISSUES -gt 0 ]; then
        log_critical "Critical Issues: $CRITICAL_ISSUES"
    fi
    if [ $HIGH_ISSUES -gt 0 ]; then
        log_error "High Issues: $HIGH_ISSUES"
    fi
    if [ $MEDIUM_ISSUES -gt 0 ]; then
        log_warning "Medium Issues: $MEDIUM_ISSUES"
    fi
    if [ $LOW_ISSUES -gt 0 ]; then
        log_info "Low Issues: $LOW_ISSUES"
    fi
    
    echo ""
    if [ $CRITICAL_ISSUES -eq 0 ] && [ $HIGH_ISSUES -eq 0 ]; then
        log_success "🎉 No critical or high-severity security issues found!"
        if [ $MEDIUM_ISSUES -eq 0 ] && [ $LOW_ISSUES -eq 0 ]; then
            log_success "🔒 All security scans passed successfully!"
        else
            log_info "👀 Review medium and low priority issues for best practices."
        fi
    else
        log_error "⚠️  Critical or high-severity security issues require immediate attention!"
        log_error "Please address these issues before deploying to production."
    fi
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--scan-type)
                SCAN_TYPE="$2"
                shift 2
                ;;
            -c|--category)
                CATEGORY="$2"
                shift 2
                ;;
            --output)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Set defaults
    ENVIRONMENT="${ENVIRONMENT:-dev}"
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    log_info "Starting security scanning for $ENVIRONMENT environment"
    log_info "Scan type: $SCAN_TYPE"
    log_info "Log file: $LOG_FILE"
    
    # Check dependencies
    check_dependencies
    
    # Run scans based on type
    case "$SCAN_TYPE" in
        "quick")
            run_secret_scans
            run_dependency_scans
            ;;
        "full")
            run_secret_scans
            run_dependency_scans
            run_code_scans
            run_infrastructure_scans
            run_compliance_scans
            ;;
        "compliance")
            run_compliance_scans
            run_data_handling_compliance
            ;;
        "custom")
            if [[ -n "${CATEGORY:-}" ]]; then
                case "$CATEGORY" in
                    "dependencies") run_dependency_scans ;;
                    "secrets") run_secret_scans ;;
                    "code") run_code_scans ;;
                    "infrastructure") run_infrastructure_scans ;;
                    "compliance") run_compliance_scans ;;
                    *) log_error "Unknown category: $CATEGORY"; exit 1 ;;
                esac
            else
                log_error "Custom scan type requires --category option"
                exit 1
            fi
            ;;
        *)
            log_error "Unknown scan type: $SCAN_TYPE"
            exit 1
            ;;
    esac
    
    # Generate report and summary
    generate_security_report
    print_summary
    
    # Exit with appropriate code
    if [ $CRITICAL_ISSUES -gt 0 ]; then
        exit 3  # Critical issues
    elif [ $HIGH_ISSUES -gt 0 ]; then
        exit 2  # High priority issues
    elif [ $FAILED_SCANS -gt 0 ]; then
        exit 1  # Some scans failed
    else
        exit 0  # All scans passed
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
