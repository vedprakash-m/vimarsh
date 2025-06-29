#!/bin/bash

# =============================================================================
# Vimarsh Security and Compliance Automation Script
# =============================================================================
# Combined security scanning and compliance verification automation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs/security-compliance"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/security-compliance_$TIMESTAMP.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Global variables
ENVIRONMENT="dev"
RUN_SECURITY=true
RUN_COMPLIANCE=true
VERBOSE=false
DRY_RUN=false
OUTPUT_FORMAT="json"

# Results tracking
SECURITY_EXIT_CODE=0
COMPLIANCE_EXIT_CODE=0
OVERALL_ISSUES=0

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

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Vimarsh Security and Compliance Automation

OPTIONS:
    -e, --environment ENV    Target environment (production only)
    --security-only         Run only security scanning
    --compliance-only       Run only compliance verification
    --output FORMAT         Output format (json|html|markdown) [default: json]
    --verbose               Enable verbose logging
    --dry-run               Show what would be executed without running
    -h, --help              Show this help message

FEATURES:
    - Comprehensive security scanning (dependencies, secrets, code, infrastructure)
    - Detailed compliance verification (GDPR, data protection, spiritual standards)
    - Combined reporting and analysis
    - CI/CD integration ready
    - Automated remediation suggestions

EXAMPLES:
    $0 --environment production --verbose
    $0 --security-only --environment production
    $0 --compliance-only --output html
    $0 --dry-run --verbose

EOF
}

# =============================================================================
# Main Functions
# =============================================================================

run_security_scanning() {
    log_info "=== Starting Security Scanning ==="
    
    local security_cmd="$SCRIPT_DIR/security-scanner.sh --environment $ENVIRONMENT --scan-type full"
    
    if [[ "$VERBOSE" == "true" ]]; then
        security_cmd="$security_cmd --verbose"
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        security_cmd="$security_cmd --dry-run"
    fi
    
    security_cmd="$security_cmd --output $OUTPUT_FORMAT"
    
    log_info "Running: $security_cmd"
    
    if $security_cmd; then
        log_success "Security scanning completed successfully"
        SECURITY_EXIT_CODE=0
    else
        local exit_code=$?
        case $exit_code in
            1)
                log_warning "Security scanning found some issues"
                SECURITY_EXIT_CODE=1
                ;;
            2)
                log_error "Security scanning found high priority issues"
                SECURITY_EXIT_CODE=2
                ((OVERALL_ISSUES++))
                ;;
            3)
                log_critical "Security scanning found critical issues"
                SECURITY_EXIT_CODE=3
                ((OVERALL_ISSUES += 2))
                ;;
            *)
                log_error "Security scanning failed with exit code $exit_code"
                SECURITY_EXIT_CODE=$exit_code
                ((OVERALL_ISSUES++))
                ;;
        esac
    fi
}

run_compliance_verification() {
    log_info "=== Starting Compliance Verification ==="
    
    local compliance_file="$LOG_DIR/compliance-report_$TIMESTAMP.json"
    local compliance_cmd="python3 $SCRIPT_DIR/compliance-checker.py --project-root $PROJECT_ROOT --output $compliance_file"
    
    if [[ "$OUTPUT_FORMAT" == "yaml" ]]; then
        compliance_file="$LOG_DIR/compliance-report_$TIMESTAMP.yaml"
        compliance_cmd="$compliance_cmd --format yaml"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        compliance_cmd="$compliance_cmd --verbose"
    fi
    
    log_info "Running: $compliance_cmd"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would run compliance verification"
        COMPLIANCE_EXIT_CODE=0
    else
        if $compliance_cmd; then
            log_success "Compliance verification completed successfully"
            COMPLIANCE_EXIT_CODE=0
        else
            local exit_code=$?
            case $exit_code in
                1)
                    log_warning "Compliance verification found some issues"
                    COMPLIANCE_EXIT_CODE=1
                    ;;
                2)
                    log_error "Compliance verification found high priority issues"
                    COMPLIANCE_EXIT_CODE=2
                    ((OVERALL_ISSUES++))
                    ;;
                3)
                    log_critical "Compliance verification found critical issues"
                    COMPLIANCE_EXIT_CODE=3
                    ((OVERALL_ISSUES += 2))
                    ;;
                *)
                    log_error "Compliance verification failed with exit code $exit_code"
                    COMPLIANCE_EXIT_CODE=$exit_code
                    ((OVERALL_ISSUES++))
                    ;;
            esac
        fi
    fi
}

generate_combined_report() {
    local combined_report="$LOG_DIR/combined-security-compliance-report_$TIMESTAMP.json"
    
    log_info "Generating combined security and compliance report"
    
    # Find the latest security and compliance reports
    local security_report=$(find "$PROJECT_ROOT/logs/security-scanning" -name "security-report_*.json" -type f 2>/dev/null | sort | tail -1 || echo "")
    local compliance_report=$(find "$LOG_DIR" -name "compliance-report_*.json" -type f 2>/dev/null | sort | tail -1 || echo "")
    
    cat > "$combined_report" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "environment": "$ENVIRONMENT",
    "execution_summary": {
        "security_scanning": {
            "executed": $RUN_SECURITY,
            "exit_code": $SECURITY_EXIT_CODE,
            "report_file": "$(basename "$security_report" 2>/dev/null || echo "null")"
        },
        "compliance_verification": {
            "executed": $RUN_COMPLIANCE,
            "exit_code": $COMPLIANCE_EXIT_CODE,
            "report_file": "$(basename "$compliance_report" 2>/dev/null || echo "null")"
        },
        "overall_issues": $OVERALL_ISSUES,
        "overall_status": "$([ $OVERALL_ISSUES -eq 0 ] && echo "PASS" || echo "FAIL")"
    },
    "reports": {
        "security_report_path": "$security_report",
        "compliance_report_path": "$compliance_report",
        "combined_report_path": "$combined_report"
    },
    "recommendations": [
EOF
    
    # Add recommendations based on exit codes
    local recommendations=()
    
    if [[ $SECURITY_EXIT_CODE -eq 3 ]]; then
        recommendations+=("\"URGENT: Address critical security vulnerabilities immediately\"")
    fi
    
    if [[ $COMPLIANCE_EXIT_CODE -eq 3 ]]; then
        recommendations+=("\"URGENT: Resolve critical compliance violations immediately\"")
    fi
    
    if [[ $SECURITY_EXIT_CODE -eq 2 ]]; then
        recommendations+=("\"HIGH: Fix high-priority security issues before production deployment\"")
    fi
    
    if [[ $COMPLIANCE_EXIT_CODE -eq 2 ]]; then
        recommendations+=("\"HIGH: Address high-priority compliance issues\"")
    fi
    
    if [[ $SECURITY_EXIT_CODE -eq 1 ]]; then
        recommendations+=("\"MEDIUM: Review and address security scan findings\"")
    fi
    
    if [[ $COMPLIANCE_EXIT_CODE -eq 1 ]]; then
        recommendations+=("\"MEDIUM: Review and improve compliance coverage\"")
    fi
    
    if [[ ${#recommendations[@]} -eq 0 ]]; then
        recommendations+=("\"No critical issues found - continue monitoring and regular scans\"")
    fi
    
    # Add recommendations to JSON
    printf '%s\n' "${recommendations[@]}" | sed '$!s/$/,/' >> "$combined_report"
    
    cat >> "$combined_report" << EOF
    ]
}
EOF
    
    log_info "Combined report saved to: $combined_report"
}

print_summary() {
    echo ""
    log_info "=== Security and Compliance Summary ==="
    log_info "Environment: $ENVIRONMENT"
    log_info "Timestamp: $(date)"
    
    echo ""
    if [[ "$RUN_SECURITY" == "true" ]]; then
        case $SECURITY_EXIT_CODE in
            0)
                log_success "🔒 Security Scanning: PASSED"
                ;;
            1)
                log_warning "🔍 Security Scanning: PASSED with warnings"
                ;;
            2)
                log_error "⚠️  Security Scanning: HIGH priority issues found"
                ;;
            3)
                log_critical "🚨 Security Scanning: CRITICAL issues found"
                ;;
            *)
                log_error "❌ Security Scanning: FAILED (exit code: $SECURITY_EXIT_CODE)"
                ;;
        esac
    else
        log_info "🔒 Security Scanning: SKIPPED"
    fi
    
    if [[ "$RUN_COMPLIANCE" == "true" ]]; then
        case $COMPLIANCE_EXIT_CODE in
            0)
                log_success "📋 Compliance Verification: PASSED"
                ;;
            1)
                log_warning "📝 Compliance Verification: PASSED with warnings"
                ;;
            2)
                log_error "⚠️  Compliance Verification: HIGH priority issues found"
                ;;
            3)
                log_critical "🚨 Compliance Verification: CRITICAL issues found"
                ;;
            *)
                log_error "❌ Compliance Verification: FAILED (exit code: $COMPLIANCE_EXIT_CODE)"
                ;;
        esac
    else
        log_info "📋 Compliance Verification: SKIPPED"
    fi
    
    echo ""
    if [[ $OVERALL_ISSUES -eq 0 ]]; then
        log_success "🎉 Overall Assessment: READY FOR DEPLOYMENT"
        log_success "No critical security or compliance issues found"
    elif [[ $OVERALL_ISSUES -eq 1 ]]; then
        log_warning "🔍 Overall Assessment: REVIEW REQUIRED"
        log_warning "Some issues found - review before deployment"
    else
        log_critical "🛑 Overall Assessment: DEPLOYMENT BLOCKED"
        log_critical "Critical issues must be resolved before deployment"
    fi
    
    echo ""
    log_info "📊 Reports Location: $LOG_DIR/"
    log_info "📝 Combined Report: combined-security-compliance-report_$TIMESTAMP.json"
}

install_dependencies() {
    log_info "Checking and installing security dependencies..."
    
    # Python dependencies
    local python_deps=("bandit" "safety" "pyyaml")
    
    for dep in "${python_deps[@]}"; do
        if ! python3 -c "import $dep" &>/dev/null; then
            log_info "Installing Python package: $dep"
            if [[ "$DRY_RUN" == "true" ]]; then
                log_info "DRY RUN: Would install $dep"
            else
                pip3 install "$dep" || log_warning "Failed to install $dep"
            fi
        fi
    done
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
            --security-only)
                RUN_COMPLIANCE=false
                shift
                ;;
            --compliance-only)
                RUN_SECURITY=false
                shift
                ;;
            --output)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --install-deps)
                install_dependencies
                exit 0
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
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    log_info "Starting Vimarsh Security and Compliance Automation"
    log_info "Environment: $ENVIRONMENT"
    log_info "Security Scanning: $RUN_SECURITY"
    log_info "Compliance Verification: $RUN_COMPLIANCE"
    log_info "Log file: $LOG_FILE"
    
    # Run security scanning if enabled
    if [[ "$RUN_SECURITY" == "true" ]]; then
        run_security_scanning
    fi
    
    # Run compliance verification if enabled
    if [[ "$RUN_COMPLIANCE" == "true" ]]; then
        run_compliance_verification
    fi
    
    # Generate combined report
    generate_combined_report
    
    # Print summary
    print_summary
    
    # Determine final exit code
    local max_exit_code=$([[ $SECURITY_EXIT_CODE -gt $COMPLIANCE_EXIT_CODE ]] && echo $SECURITY_EXIT_CODE || echo $COMPLIANCE_EXIT_CODE)
    
    exit $max_exit_code
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
